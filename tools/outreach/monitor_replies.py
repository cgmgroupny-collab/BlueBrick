"""
Blue Brick Reply Monitor
-------------------------
Monitors Gmail inbox for replies to outreach emails.
Cross-references senders against leads.csv and flags hot leads.

Setup:
    Same as sender.py — needs GMAIL_USER and GMAIL_APP_PASSWORD in .env

Usage:
    python3 tools/outreach/monitor_replies.py             # Check once
    python3 tools/outreach/monitor_replies.py --watch      # Check every 60s
    python3 tools/outreach/monitor_replies.py --watch 120  # Check every 120s
    python3 tools/outreach/monitor_replies.py --all        # Check all mail, not just unread
"""
import csv
import imaplib
import email
import email.message
import argparse
import sys
import time
import re
from pathlib import Path
from datetime import datetime
from email.header import decode_header
from email.utils import parseaddr

sys.path.insert(0, str(Path(__file__).parent))
from config import GMAIL_USER, GMAIL_APP_PASSWORD, LEADS_CSV, DATA_DIR


# ── Constants ─────────────────────────────────────────────────────────────────

REPLY_LOG = DATA_DIR / "reply_log.csv"
REPLY_LOG_FIELDS = [
    "timestamp", "business_name", "category", "from_email",
    "subject", "snippet", "hot_lead",
]

BOUNCE_LOG = DATA_DIR / "bounce_log.csv"
BOUNCE_LOG_FIELDS = [
    "timestamp", "from_email", "original_to", "subject", "snippet", "bounce_type",
]

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993

BOUNCE_SENDERS = [
    "mailer-daemon", "postmaster", "mail-daemon", "noreply",
]
BOUNCE_SUBJECTS = [
    "delivery status notification", "undeliverable", "delivery failure",
    "mail delivery failed", "returned mail", "undelivered mail",
    "message not delivered", "delivery has failed",
]

HOT_KEYWORDS = [
    "schedule", "walkthrough", "quote", "estimate", "interested",
    "available", "when", "time", "meet", "appointment", "book",
    "pricing", "rate", "cost", "free estimate", "come by", "stop by",
    "set up", "let's talk", "call me", "sounds good", "love to",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def decode_mime_header(raw: str) -> str:
    """Decode a MIME-encoded header (subject, from, etc.) into plain text."""
    if not raw:
        return ""
    parts = decode_header(raw)
    decoded = []
    for data, charset in parts:
        if isinstance(data, bytes):
            decoded.append(data.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(data)
    return " ".join(decoded)


def extract_body(msg: email.message.Message) -> str:
    """Extract plain-text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def make_snippet(body: str, max_len: int = 200) -> str:
    """Clean up body text and truncate to a snippet."""
    # Collapse whitespace
    text = re.sub(r"\s+", " ", body).strip()
    if len(text) > max_len:
        text = text[:max_len] + "..."
    return text


def is_hot_lead(subject: str, body: str) -> bool:
    """Check if the reply contains booking-related keywords."""
    combined = (subject + " " + body).lower()
    return any(kw in combined for kw in HOT_KEYWORDS)


def load_leads_index() -> dict:
    """Load leads.csv into a dict keyed by lowercase email address."""
    index = {}
    if not LEADS_CSV.exists():
        return index
    with open(LEADS_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = row.get("email", "").strip().lower()
            if addr:
                index[addr] = row
    return index


def log_reply(entry: dict):
    """Append a reply to reply_log.csv."""
    file_exists = REPLY_LOG.exists() and REPLY_LOG.stat().st_size > 0
    with open(REPLY_LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REPLY_LOG_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)


def load_logged_ids() -> set:
    """Load already-logged (from_email, subject) pairs to avoid duplicates."""
    seen = set()
    if not REPLY_LOG.exists():
        return seen
    with open(REPLY_LOG, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get("from_email", "").lower(), row.get("subject", ""))
            seen.add(key)
    return seen


def load_logged_bounces() -> set:
    """Load already-logged bounce subjects to avoid duplicates."""
    seen = set()
    if not BOUNCE_LOG.exists():
        return seen
    with open(BOUNCE_LOG, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            seen.add(row.get("subject", ""))
    return seen


def is_bounce(from_addr: str, subject: str) -> bool:
    """Check if an email is a bounce/delivery failure notification."""
    from_lower = from_addr.lower()
    subj_lower = subject.lower()
    if any(s in from_lower for s in BOUNCE_SENDERS):
        return True
    if any(s in subj_lower for s in BOUNCE_SUBJECTS):
        return True
    return False


def extract_original_recipient(body: str) -> str:
    """Try to extract the original recipient email from a bounce message body."""
    patterns = [
        r"Original-Recipient:.*?<?([\w.+-]+@[\w.-]+)>?",
        r"Final-Recipient:.*?<?([\w.+-]+@[\w.-]+)>?",
        r"was not delivered to\s+([\w.+-]+@[\w.-]+)",
        r"delivery to\s+([\w.+-]+@[\w.-]+)\s+failed",
        r"could not be delivered to:\s*([\w.+-]+@[\w.-]+)",
        r"<([\w.+-]+@[\w.-]+)>",
    ]
    for pat in patterns:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            addr = m.group(1).lower()
            if addr != GMAIL_USER.lower():
                return addr
    return ""


def log_bounce(entry: dict):
    """Append a bounce to bounce_log.csv."""
    file_exists = BOUNCE_LOG.exists() and BOUNCE_LOG.stat().st_size > 0
    with open(BOUNCE_LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=BOUNCE_LOG_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)


# ── Core ──────────────────────────────────────────────────────────────────────

def connect_imap() -> imaplib.IMAP4_SSL:
    """Connect and authenticate to Gmail IMAP."""
    if not GMAIL_APP_PASSWORD:
        print("Error: GMAIL_APP_PASSWORD not set in .env")
        print("  1. Enable 2FA: https://myaccount.google.com/security")
        print("  2. Create App Password: https://myaccount.google.com/apppasswords")
        print("  3. Add to .env: GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx")
        sys.exit(1)

    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    return mail


def check_inbox(only_unread: bool = True) -> tuple[list[dict], list[dict]]:
    """
    Check Gmail inbox for replies from known leads and bounce notifications.
    Returns (replies, bounces) tuples.
    """
    leads = load_leads_index()
    if not leads:
        print("Warning: No leads found in leads.csv")
        return [], []

    logged = load_logged_ids()
    logged_bounces = load_logged_bounces()
    mail = connect_imap()
    mail.select("INBOX")

    # Search criteria
    criteria = "UNSEEN" if only_unread else "ALL"
    status, data = mail.search(None, criteria)

    if status != "OK" or not data[0]:
        mail.logout()
        return [], []

    msg_ids = data[0].split()
    replies = []
    bounces = []

    for msg_id in msg_ids:
        status, msg_data = mail.fetch(msg_id, "(BODY.PEEK[])")
        if status != "OK":
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Parse sender
        from_raw = decode_mime_header(msg.get("From", ""))
        _, from_addr = parseaddr(from_raw)
        from_addr = from_addr.lower().strip()

        subject = decode_mime_header(msg.get("Subject", ""))
        body = extract_body(msg)

        # Check for bounces first
        if is_bounce(from_addr, subject):
            if subject not in logged_bounces:
                original_to = extract_original_recipient(body)
                bounce_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "from_email": from_addr,
                    "original_to": original_to,
                    "subject": subject,
                    "snippet": make_snippet(body),
                    "bounce_type": "hard" if "does not exist" in body.lower() or "unknown user" in body.lower() else "soft",
                }
                bounces.append(bounce_entry)
                logged_bounces.add(subject)
                mail.store(msg_id, "+FLAGS", "\\Seen")
            continue

        # Skip if not from a known lead
        if from_addr not in leads:
            continue

        snippet = make_snippet(body)

        # Deduplicate
        dedup_key = (from_addr, subject)
        if dedup_key in logged:
            continue

        lead = leads[from_addr]
        hot = is_hot_lead(subject, body)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "business_name": lead.get("business_name", ""),
            "category": lead.get("category", ""),
            "from_email": from_addr,
            "subject": subject,
            "snippet": snippet,
            "hot_lead": "YES" if hot else "",
        }

        replies.append(entry)
        logged.add(dedup_key)

        # Mark as seen now that we've processed it
        mail.store(msg_id, "+FLAGS", "\\Seen")

    mail.logout()
    return replies, bounces


def print_reply(entry: dict):
    """Print a formatted reply notification to the terminal."""
    hot_tag = " *** HOT LEAD ***" if entry["hot_lead"] == "YES" else ""
    print(f"\n{'='*60}")
    print(f"  REPLY RECEIVED{hot_tag}")
    print(f"  From:     {entry['from_email']}")
    print(f"  Business: {entry['business_name']} ({entry['category']})")
    print(f"  Subject:  {entry['subject']}")
    print(f"  Snippet:  {entry['snippet']}")
    print(f"  Time:     {entry['timestamp']}")
    print(f"{'='*60}")


def print_bounce(entry: dict):
    """Print a formatted bounce notification to the terminal."""
    btype = entry.get("bounce_type", "unknown").upper()
    print(f"\n{'='*60}")
    print(f"  BOUNCE DETECTED ({btype})")
    print(f"  Original to: {entry.get('original_to', 'unknown')}")
    print(f"  Subject:     {entry['subject']}")
    print(f"  Snippet:     {entry['snippet'][:100]}")
    print(f"  Time:        {entry['timestamp']}")
    print(f"{'='*60}")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_check(only_unread: bool = True):
    """Run a single inbox check."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now}] Checking inbox for replies and bounces...")

    replies, bounces = check_inbox(only_unread=only_unread)

    if not replies and not bounces:
        print("  No new replies or bounces.")
        return 0

    for entry in replies:
        log_reply(entry)
        print_reply(entry)

    for entry in bounces:
        log_bounce(entry)
        print_bounce(entry)

    hot_count = sum(1 for r in replies if r["hot_lead"] == "YES")
    if replies:
        print(f"\n  New replies: {len(replies)}")
        if hot_count:
            print(f"  Hot leads: {hot_count}")
        print(f"  Logged to: {REPLY_LOG}")
    if bounces:
        print(f"\n  Bounces detected: {len(bounces)}")
        print(f"  Logged to: {BOUNCE_LOG}")

    return len(replies) + len(bounces)


def run_watch(interval: int = 60, only_unread: bool = True):
    """Continuously monitor inbox at the given interval."""
    print(f"\nBlue Brick Reply Monitor")
    print(f"  Watching: {GMAIL_USER}")
    print(f"  Interval: every {interval}s")
    print(f"  Mode: {'unread only' if only_unread else 'all messages'}")
    print(f"  Press Ctrl+C to stop.\n")

    try:
        while True:
            run_check(only_unread=only_unread)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blue Brick Reply Monitor")
    parser.add_argument(
        "--watch", "-w",
        nargs="?",
        const=60,
        type=int,
        metavar="SECONDS",
        help="Keep checking every N seconds (default: 60)",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Check all mail, not just unread",
    )

    args = parser.parse_args()

    if args.watch is not None:
        run_watch(interval=args.watch, only_unread=not args.all)
    else:
        run_check(only_unread=not args.all)
