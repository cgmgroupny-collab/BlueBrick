"""
Blue Brick — Rich Email Template Sender
----------------------------------------
Extracts designed HTML templates from email-template-preview.html,
compresses images, embeds via CID attachments, and sends properly
formatted MIME emails.

Usage:
    python3 tools/outreach/send_templates.py --test          # Send all 7 to yourself
    python3 tools/outreach/send_templates.py --test --only property_managers
    python3 tools/outreach/send_templates.py --test --only contractors,realtors
    python3 tools/outreach/send_templates.py --dry-run       # Preview without sending
"""

import re
import sys
import ssl
import time
import os
import base64
import argparse
import smtplib
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from datetime import datetime
from PIL import Image
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))
from config import GMAIL_USER, GMAIL_APP_PASSWORD, BRAND

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
TRACKING_BASE = "https://bluebrickmass.com/api/track"
PREVIEW_HTML = PROJECT_ROOT / "tools" / "email-template-preview.html"
ASSETS_DIR = PROJECT_ROOT / "assets" / "images" / "email-templates"

# Template order and metadata
TEMPLATES = [
    {
        "key": "property_managers",
        "label": "Property Managers",
        "subject": "Quick question about your April turnovers",
    },
    {
        "key": "contractors",
        "label": "Contractors",
        "subject": "Who handles cleanup after your builds?",
    },
    {
        "key": "realtors",
        "label": "Realtors",
        "subject": "Thought of you — listing prep idea",
    },
    {
        "key": "restaurants",
        "label": "Restaurants",
        "subject": "Before your next health inspection",
    },
    {
        "key": "daycares",
        "label": "Daycares",
        "subject": "How are you handling facility sanitization?",
    },
    {
        "key": "airbnb_hosts",
        "label": "Airbnb Hosts",
        "subject": "Tired of doing turnovers yourself?",
    },
    {
        "key": "interior_designers",
        "label": "Interior Designers",
        "subject": "Your reveals deserve a spotless finish",
    },
]

# Image compression settings
MAX_WIDTH = 600
JPEG_QUALITY = 75


def compress_image(path: Path, is_logo: bool = False) -> bytes:
    """Compress image for email. Logo stays PNG (transparency), photos become JPEG."""
    img = Image.open(path)

    if is_logo:
        # Logo: keep PNG for transparency, just resize
        if img.width > 320:
            ratio = 320 / img.width
            img = img.resize((320, int(img.height * ratio)), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    # Photos: convert to JPEG
    if img.mode in ("RGBA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            bg.paste(img, mask=img.split()[3])
        else:
            bg.paste(img)
        img = bg

    # Resize if wider than MAX_WIDTH
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_size = (MAX_WIDTH, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return buf.getvalue()


def extract_templates(html_path: Path) -> list[str]:
    """Extract email HTML from each template section in the preview file."""
    content = html_path.read_text()

    # Split by template section comments
    # Each template is inside <div class="email-frame">...</div>
    soup = BeautifulSoup(content, "html.parser")
    frames = soup.find_all("div", class_="email-frame")

    templates = []
    for frame in frames:
        # Get the inner HTML (the actual email table structure)
        inner = frame.decode_contents().strip()
        templates.append(inner)

    return templates


def resolve_image_paths(html: str) -> dict[str, Path]:
    """Find all image src paths in the HTML and map to local files."""
    images = {}
    pattern = r'src="(\.\./assets/images/email-templates/[^"]+)"'
    for match in re.finditer(pattern, html):
        rel_path = match.group(1)
        # ../assets/images/email-templates/X/Y.png -> ASSETS_DIR/X/Y.png
        parts = rel_path.replace("../assets/images/email-templates/", "")
        abs_path = ASSETS_DIR / parts
        if abs_path.exists():
            # CID name: just the filename without extension
            cid_name = abs_path.stem  # e.g., "pm-hero"
            images[rel_path] = (abs_path, cid_name)
    return images


def make_tracking_url(email_addr: str, category: str, business: str = "") -> str:
    """Generate a tracking pixel URL for this recipient."""
    e = base64.b64encode(email_addr.encode()).decode()
    b = base64.b64encode(business.encode()).decode() if business else ""
    url = f"{TRACKING_BASE}?e={e}&c={category}"
    if b:
        url += f"&b={b}"
    return url


def make_cid_html(template_html: str, images: dict) -> str:
    """Replace relative image paths with cid: references and wrap in DOCTYPE."""
    html = template_html

    # Replace image src with CID references
    for rel_path, (_, cid_name) in images.items():
        html = html.replace(f'src="{rel_path}"', f'src="cid:{cid_name}"')

    # Replace placeholder href="#" with actual website link
    html = html.replace('href="#"', 'href="https://bluebrickmass.com/#estimate"')

    # Replace {first_name} with a test name for test sends
    html = html.replace("{first_name}", "there")

    # Wrap in proper email DOCTYPE
    return f"""\
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>Blue Brick</title>
</head>
<body style="margin:0;padding:0;">
{html}
</body>
</html>"""


def make_base64_html(template_html: str, images: dict) -> str:
    """Replace image paths with base64 data URIs for Mail.app sending.
    This makes the HTML fully self-contained — no CID, no external files."""
    html = template_html

    for rel_path, (abs_path, _) in images.items():
        is_logo = "logo" in abs_path.stem.lower()
        img_data = compress_image(abs_path, is_logo=is_logo)
        mime = "image/png" if is_logo else "image/jpeg"
        b64 = base64.b64encode(img_data).decode("ascii")
        data_uri = f"data:{mime};base64,{b64}"
        html = html.replace(f'src="{rel_path}"', f'src="{data_uri}"')

    html = html.replace('href="#"', 'href="https://bluebrickmass.com/#estimate"')
    html = html.replace("{first_name}", "there")

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;">
{html}
</body>
</html>"""


def send_via_mail_app(to_email: str, subject: str, html_body: str,
                      sender: str = GMAIL_USER, dry_run: bool = False) -> bool:
    """Send email via Mac Mail.app using AppleScript + temp file."""
    if dry_run:
        print(f"    [DRY RUN] Would send to {to_email} via Mail.app")
        return True

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".html", prefix="bb_email_")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(html_body)

        safe_subject = subject.replace("\\", "\\\\").replace('"', '\\"')
        safe_to = to_email.replace("\\", "\\\\").replace('"', '\\"')
        safe_sender = sender.replace("\\", "\\\\").replace('"', '\\"')

        applescript = f'''
        set htmlFile to POSIX file "{tmp_path}"
        set htmlContent to read htmlFile as «class utf8»

        tell application "Mail"
            set newMessage to make new outgoing message with properties {{subject:"{safe_subject}", visible:false}}
            tell newMessage
                set html content to htmlContent
                set sender to "{safe_sender}"
                make new to recipient at end of to recipients with properties {{address:"{safe_to}"}}
                send
            end tell
        end tell
        '''

        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True, text=True, timeout=30,
        )

        if result.returncode != 0:
            print(f"    ✗ AppleScript error: {result.stderr.strip()}")
            return False
        return True

    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def make_plain_text(key: str) -> str:
    """Generate plain text fallback for a template category."""
    t = next((t for t in TEMPLATES if t["key"] == key), TEMPLATES[0])

    return f"""\
Hi there,

I'm Gerardo with Blue Brick Luxury & Commercial Cleaning, based in Waltham, MA.

We specialize in professional cleaning services for businesses across Greater Boston — from move-in/out turnovers to post-construction cleanup to commercial deep cleaning.

If you'd like a free estimate or walkthrough, reach out anytime:

Phone: 781-330-5604 (text preferred)
Email: bluebrickmass@gmail.com
Web: {BRAND['website']}

Best,
Gerardo Cazares
Blue Brick Luxury & Commercial Cleaning
Waltham, MA · Serving 15 cities across Greater Boston

---
To stop receiving emails, reply with "unsubscribe".
"""


def build_email(
    to_email: str,
    subject: str,
    template_html: str,
    plain_text: str,
    images: dict[str, tuple[Path, str]],
) -> MIMEMultipart:
    """Build a properly structured MIME email with CID-embedded images.

    Structure:
      multipart/related
        multipart/alternative
          text/plain
          text/html
        image/jpeg (CID: pm-hero)
        image/jpeg (CID: pm-before)
        ...
    """
    # Outer: multipart/related (ties HTML to its CID images)
    msg = MIMEMultipart("related")
    msg["From"] = f"Gerardo Cazares <{GMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Reply-To"] = GMAIL_USER

    # Inner: multipart/alternative (plain text + HTML)
    alt = MIMEMultipart("alternative")

    # Plain text fallback
    alt.attach(MIMEText(plain_text, "plain", "utf-8"))

    # HTML version
    alt.attach(MIMEText(template_html, "html", "utf-8"))

    msg.attach(alt)

    # Attach images with CID headers
    seen_cids = set()
    for rel_path, (abs_path, cid_name) in images.items():
        if cid_name in seen_cids:
            continue
        seen_cids.add(cid_name)

        is_logo = "logo" in cid_name.lower()
        img_data = compress_image(abs_path, is_logo=is_logo)
        subtype = "png" if is_logo else "jpeg"
        ext = "png" if is_logo else "jpg"
        img_part = MIMEImage(img_data, _subtype=subtype)
        img_part.add_header("Content-ID", f"<{cid_name}>")
        img_part.add_header("Content-Disposition", "inline", filename=f"{cid_name}.{ext}")
        msg.attach(img_part)

    return msg


def send_email(msg: MIMEMultipart, to_email: str, dry_run: bool = False) -> bool:
    """Send a MIME message via Gmail SMTP."""
    if dry_run:
        size_kb = len(msg.as_bytes()) / 1024
        print(f"    [DRY RUN] Would send to {to_email} ({size_kb:.0f} KB)")
        return True

    if not GMAIL_APP_PASSWORD:
        print("  ✗ GMAIL_APP_PASSWORD not set in .env.local")
        return False

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_bytes())
        return True
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Blue Brick Rich Email Sender")
    parser.add_argument("--test", action="store_true", help="Send test emails to yourself")
    parser.add_argument("--send", action="store_true", help="Send to leads from leads.csv")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Preview without sending")
    parser.add_argument("--via", choices=["smtp", "mailapp"], default="mailapp",
                        help="Send method: smtp (needs app password) or mailapp (Mac Mail.app, default)")
    parser.add_argument("--only", type=str, help="Comma-separated list of template keys to send")
    parser.add_argument("--to", type=str, default=GMAIL_USER, help="Recipient email for test mode")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max emails to send (default 20)")
    args = parser.parse_args()

    if not args.test and not args.dry_run and not args.send:
        print("Use --test to send to yourself, --send to send to leads, or --dry-run to preview.")
        return

    # If --send mode, load leads and send rich templates
    if args.send:
        import csv
        import random
        from config import LEADS_CSV, SENT_LOG, DATA_DIR, EMAIL_DELAY_MIN, EMAIL_DELAY_MAX

        category = args.only or "realtors"
        if "," in category:
            category = category.split(",")[0].strip()

        use_mailapp = args.via == "mailapp"

        print(f"\n🧱 Blue Brick Rich Email Sender (LEAD MODE)")
        print(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
        print(f"   Via: {'Mac Mail.app' if use_mailapp else 'Gmail SMTP'}")
        print(f"   Category: {category}")
        print(f"   Limit: {args.limit}")
        print()

        # Extract the correct template
        print("  Extracting templates from preview HTML...")
        template_htmls = extract_templates(PREVIEW_HTML)
        print(f"  Found {len(template_htmls)} templates")

        # Find the template index for the category
        tmpl_idx = next((i for i, t in enumerate(TEMPLATES) if t["key"] == category), 0)
        tmpl = TEMPLATES[tmpl_idx]
        raw_html = template_htmls[tmpl_idx] if tmpl_idx < len(template_htmls) else template_htmls[0]

        # Resolve images
        images = resolve_image_paths(raw_html)
        print(f"  Template: {tmpl['label']} ({len(images)} images)")

        # Load unsent leads
        leads = []
        if LEADS_CSV.exists():
            with open(LEADS_CSV, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("status") == "sent":
                        continue
                    if not row.get("email"):
                        continue
                    if row.get("category") != category:
                        continue
                    leads.append(row)

        if not leads:
            print("  No unsent leads found for this category.")
            return

        leads = leads[:args.limit]
        print(f"  Leads to contact: {len(leads)}\n")

        sent_count = 0
        for i, lead in enumerate(leads):
            email = lead["email"]
            biz_name = lead.get("business_name", "")
            name = biz_name.split()[0] if biz_name else "there"
            if name.lower() in {"the", "a", "an", ""} or len(name) <= 1:
                name = "there"

            # Inject tracking pixel for this specific lead
            lead_html = raw_html.replace(
                "{tracking_pixel}",
                make_tracking_url(email, category, biz_name),
            )

            if use_mailapp:
                # Mail.app: use base64 data URIs (self-contained HTML)
                personalized_html = make_base64_html(lead_html, images)
                personalized_html = personalized_html.replace("{first_name}", name)
                print(f"  [{i+1}/{len(leads)}] {email}")
                success = send_via_mail_app(email, tmpl["subject"], personalized_html, dry_run=args.dry_run)
            else:
                # SMTP: use CID-embedded images
                personalized_html = make_cid_html(lead_html, images)
                personalized_html = personalized_html.replace("{first_name}", name)
                plain_text = make_plain_text(category)
                plain_text = plain_text.replace("Hi there,", f"Hi {name},")
                msg = build_email(email, tmpl["subject"], personalized_html, plain_text, images)
                size_kb = len(msg.as_bytes()) / 1024
                print(f"  [{i+1}/{len(leads)}] {email} ({size_kb:.0f} KB)")
                success = send_email(msg, email, dry_run=args.dry_run)
            if success:
                sent_count += 1
                if not args.dry_run:
                    # Mark as sent in CSV
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

                    # Log
                    file_exists = SENT_LOG.exists()
                    with open(SENT_LOG, "a", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=[
                            "email", "business_name", "category", "subject", "sent_at"
                        ])
                        if not file_exists:
                            writer.writeheader()
                        writer.writerow({
                            "email": email,
                            "business_name": lead.get("business_name", ""),
                            "category": category,
                            "subject": tmpl["subject"],
                            "sent_at": datetime.now().isoformat(),
                        })

                    print(f"       Sent ✓")
                else:
                    print(f"       Would send")

                if i < len(leads) - 1:
                    delay = random.uniform(EMAIL_DELAY_MIN, EMAIL_DELAY_MAX)
                    if not args.dry_run:
                        print(f"       ⏳ Waiting {delay:.0f}s...")
                        time.sleep(delay)

        print(f"\n{'='*50}")
        print(f"  Done — {sent_count}/{len(leads)} rich emails {'previewed' if args.dry_run else 'sent'}")
        print(f"{'='*50}\n")
        return

    # Parse --only filter
    only_keys = None
    if args.only:
        only_keys = [k.strip() for k in args.only.split(",")]

    use_mailapp = args.via == "mailapp"

    print(f"\n🧱 Blue Brick Rich Email Sender")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE TEST'}")
    print(f"   Via: {'Mac Mail.app' if use_mailapp else 'Gmail SMTP'}")
    print(f"   Recipient: {args.to}")
    print(f"   Source: {PREVIEW_HTML.name}")
    print()

    # Extract all template HTML from preview
    print("  Extracting templates from preview HTML...")
    template_htmls = extract_templates(PREVIEW_HTML)
    print(f"  Found {len(template_htmls)} templates")

    if len(template_htmls) < len(TEMPLATES):
        print(f"  ⚠ Expected {len(TEMPLATES)} templates, got {len(template_htmls)}")

    sent = 0
    for i, tmpl in enumerate(TEMPLATES):
        if i >= len(template_htmls):
            break

        if only_keys and tmpl["key"] not in only_keys:
            continue

        print(f"\n  [{i+1}/{len(TEMPLATES)}] {tmpl['label']}")
        print(f"       Subject: {tmpl['subject']}")

        raw_html = template_htmls[i]

        # Inject tracking pixel for this recipient
        tracking_url = make_tracking_url(args.to, tmpl["key"], "Test")
        raw_html = raw_html.replace("{tracking_pixel}", tracking_url)

        # Find and resolve image paths
        images = resolve_image_paths(raw_html)
        print(f"       Images: {len(images)} found")

        if use_mailapp:
            # Mail.app: base64 data URIs (self-contained)
            final_html = make_base64_html(raw_html, images)
            success = send_via_mail_app(args.to, tmpl["subject"], final_html, dry_run=args.dry_run)
        else:
            # SMTP: CID-embedded images
            final_html = make_cid_html(raw_html, images)
            plain_text = make_plain_text(tmpl["key"])
            msg = build_email(args.to, tmpl["subject"], final_html, plain_text, images)
            size_kb = len(msg.as_bytes()) / 1024
            print(f"       Size: {size_kb:.0f} KB")
            success = send_email(msg, args.to, dry_run=args.dry_run)

        if success:
            sent += 1
            action = "Would send" if args.dry_run else "Sent ✓"
            print(f"       {action}")
        else:
            print(f"       ✗ Failed")

        # Brief delay between sends
        if not args.dry_run and i < len(TEMPLATES) - 1:
            time.sleep(2)

    print(f"\n{'='*50}")
    print(f"  Done — {sent}/{len(TEMPLATES)} emails {'previewed' if args.dry_run else 'sent'}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
