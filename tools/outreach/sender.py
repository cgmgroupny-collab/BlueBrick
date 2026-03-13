"""
Blue Brick Email Sender
-----------------------
Sends personalized outreach emails via Gmail SMTP.

Setup:
    1. Enable 2FA on your Gmail account
    2. Generate an App Password: https://myaccount.google.com/apppasswords
    3. Add to .env: GMAIL_APP_PASSWORD=your_app_password_here

Usage:
    python3 tools/outreach/sender.py --dry-run          # Preview without sending
    python3 tools/outreach/sender.py --category realtors # Send to realtors only
    python3 tools/outreach/sender.py                     # Send to all unsent leads
    python3 tools/outreach/sender.py --limit 10          # Send max 10 emails
"""
import csv
import smtplib
import ssl
import argparse
import random
import time
import sys
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    GMAIL_USER, GMAIL_APP_PASSWORD, LEADS_CSV, SENT_LOG, DATA_DIR,
    EMAIL_DELAY_MIN, EMAIL_DELAY_MAX, MAX_EMAILS_PER_DAY, BRAND,
)
from templates import get_template, personalize


def load_leads(category: str = None) -> list[dict]:
    """Load leads from CSV, optionally filter by category."""
    if not LEADS_CSV.exists():
        print("✗ No leads.csv found. Run the scraper first.")
        return []

    leads = []
    with open(LEADS_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("status") == "sent":
                continue
            if not row.get("email"):
                continue
            if category and row.get("category") != category:
                continue
            leads.append(row)

    return leads


def mark_sent(email: str):
    """Mark a lead as sent in the CSV."""
    if not LEADS_CSV.exists():
        return

    rows = []
    with open(LEADS_CSV, "r") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row.get("email") == email:
                row["status"] = "sent"
            rows.append(row)

    with open(LEADS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def log_sent(lead: dict, subject: str):
    """Log sent email for tracking."""
    file_exists = SENT_LOG.exists()
    with open(SENT_LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "email", "business_name", "category", "subject", "sent_at"
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "email": lead["email"],
            "business_name": lead.get("business_name", ""),
            "category": lead.get("category", ""),
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
        })


def send_email(to_email: str, subject: str, body: str, html: str = None, dry_run: bool = False) -> bool:
    """Send a single email via Gmail SMTP with plain text + HTML banner."""
    if dry_run:
        print(f"\n  --- DRY RUN ---")
        print(f"  To: {to_email}")
        print(f"  Subject: {subject}")
        print(f"  Body preview: {body[:150]}...")
        print(f"  HTML banner: {'Yes' if html else 'No'}")
        print(f"  --- END DRY RUN ---")
        return True

    if not GMAIL_APP_PASSWORD:
        print("✗ GMAIL_APP_PASSWORD not set in .env")
        print("  1. Enable 2FA: https://myaccount.google.com/security")
        print("  2. Create App Password: https://myaccount.google.com/apppasswords")
        print("  3. Add to .env: GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{BRAND['name']} <{GMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Reply-To"] = GMAIL_USER

    # CAN-SPAM footer for plain text fallback
    footer = (
        f"\n\n---\n"
        f"{BRAND['name']}\n"
        f"{BRAND['address']}\n"
        f"To stop receiving emails, reply with \"unsubscribe\"."
    )
    body_with_footer = body + footer

    # Plain text version (fallback)
    msg.attach(MIMEText(body_with_footer, "plain"))

    # HTML version with branded banner + CTA (preferred by email clients)
    if html:
        msg.attach(MIMEText(html, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"  ✗ Failed to send to {to_email}: {e}")
        return False


def run_sender(category: str = None, dry_run: bool = False, limit: int = None):
    """Main sender pipeline."""
    leads = load_leads(category)

    if not leads:
        print("No unsent leads found.")
        return

    if limit:
        leads = leads[:limit]

    max_send = min(len(leads), MAX_EMAILS_PER_DAY)
    leads = leads[:max_send]

    print(f"\n🧱 Blue Brick Email Sender")
    print(f"   Mode: {'DRY RUN (no emails sent)' if dry_run else 'LIVE'}")
    print(f"   Leads to contact: {len(leads)}")
    if category:
        print(f"   Category: {category}")
    print()

    sent_count = 0
    for i, lead in enumerate(leads):
        cat = lead.get("category", "realtors")
        template = get_template(cat)
        personalized = personalize(template, lead)

        print(f"[{i+1}/{len(leads)}] {lead['email']} ({cat})")

        success = send_email(
            to_email=lead["email"],
            subject=personalized["subject"],
            body=personalized["body"],
            html=personalized.get("html"),
            dry_run=dry_run,
        )

        if success:
            sent_count += 1
            if not dry_run:
                mark_sent(lead["email"])
                log_sent(lead, personalized["subject"])
                print(f"  ✓ Sent")
            else:
                print(f"  ✓ Would send")

            # Rate limit between emails
            if i < len(leads) - 1:
                delay = random.uniform(EMAIL_DELAY_MIN, EMAIL_DELAY_MAX)
                if not dry_run:
                    print(f"  ⏳ Waiting {delay:.0f}s...")
                    time.sleep(delay)

    print(f"\n{'='*50}")
    print(f"  Done — {sent_count}/{len(leads)} emails {'previewed' if dry_run else 'sent'}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blue Brick Email Sender")
    parser.add_argument(
        "--category", "-c",
        choices=["realtors", "interior_designers", "daycares", "contractors",
                 "property_managers", "restaurants", "airbnb_hosts"],
        help="Only send to this category",
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Preview emails without sending",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        help="Max emails to send",
    )

    args = parser.parse_args()
    run_sender(category=args.category, dry_run=args.dry_run, limit=args.limit)
