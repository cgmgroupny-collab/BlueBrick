"""
Blue Brick Auto-Responder
--------------------------
Reads reply_log.csv for new replies from leads, drafts and sends
personalized responses based on intent detection.

Intent categories:
  - HOT: wants quote/walkthrough/schedule → send booking response
  - WARM: general interest/question → send info + CTA
  - UNSUB: unsubscribe request → mark and skip
  - COLD: auto-reply/OOO/bounce → log and skip

Usage:
    python3 tools/outreach/responder.py --dry-run        # Preview responses
    python3 tools/outreach/responder.py --send            # Send responses
    python3 tools/outreach/responder.py --status          # Show reply summary
"""
import csv
import sys
import os
import re
import time
import random
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    GMAIL_USER, DATA_DIR, BRAND,
    EMAIL_DELAY_MIN, EMAIL_DELAY_MAX,
)

REPLY_LOG = DATA_DIR / "reply_log.csv"
RESPONSE_LOG = DATA_DIR / "response_log.csv"
RESPONSE_FIELDS = [
    "timestamp", "to_email", "business_name", "category",
    "intent", "subject", "status",
]

# ── Intent Detection ─────────────────────────────────────────────────────────

UNSUB_KEYWORDS = ["unsubscribe", "remove me", "stop emailing", "opt out", "take me off"]
HOT_KEYWORDS = [
    "schedule", "walkthrough", "quote", "estimate", "interested",
    "available", "when can", "time", "meet", "appointment", "book",
    "pricing", "rate", "cost", "free estimate", "come by", "stop by",
    "set up", "let's talk", "call me", "sounds good", "love to",
    "send me", "more info", "tell me more", "how much",
]
COLD_KEYWORDS = [
    "out of office", "auto-reply", "automatic reply", "on vacation",
    "no longer with", "delivery failure", "undeliverable", "mailer-daemon",
]


def detect_intent(subject: str, snippet: str) -> str:
    """Classify reply intent: HOT, WARM, UNSUB, or COLD."""
    combined = (subject + " " + snippet).lower()

    if any(kw in combined for kw in UNSUB_KEYWORDS):
        return "UNSUB"
    if any(kw in combined for kw in COLD_KEYWORDS):
        return "COLD"
    if any(kw in combined for kw in HOT_KEYWORDS):
        return "HOT"
    return "WARM"


# ── Response Templates ────────────────────────────────────────────────────────

def get_first_name(business_name: str) -> str:
    """Extract greeting name from business name."""
    name = (business_name or "").split()[0] if business_name else "there"
    if name.lower() in {"the", "a", "an", ""} or len(name) <= 1:
        name = "there"
    return name


PRICE_GUIDES = {
    "realtors": {
        "url": "https://bluebrickmass.com/brand/Blue-Brick-Realtor-Price-Guide.pdf",
        "label": "Realtor Cleaning Price Guide",
        "pitch": "I put together a quick price guide specifically for realtors — covers listing prep, move-out cleans, and staging cleanup with transparent pricing",
    },
    "daycares": {
        "url": "https://bluebrickmass.com/brand/Blue-Brick-Daycare-Price-Guide.pdf",
        "label": "Daycare Facility Price Guide",
        "pitch": "I put together a price guide specifically for childcare facilities — covers daily sanitization, deep cleans, and compliance-ready programs",
    },
    "restaurants": {
        "url": "https://bluebrickmass.com/brand/Blue-Brick-Restaurant-Price-Guide.pdf",
        "label": "Restaurant Cleaning Price Guide",
        "pitch": "I put together a price guide specifically for restaurants — covers kitchen deep cleans, hood cleaning, floor care, and health inspection prep",
    },
}

RESPONSES = {
    "HOT": {
        "subject": "Re: {original_subject}",
        "body": """\
Hi {name},

Thanks for getting back to me — glad to hear you're interested.

{price_guide_line}

I'd love to set up a quick walkthrough at your convenience. It takes about 15 minutes, and I'll have a quote for you the same day.

Easiest way to get started:
- Text me at 781-330-5604 with your availability
- Or reply here and I'll call you

Looking forward to it.

Best,
Gerardo
Blue Brick Luxury & Commercial Cleaning
781-330-5604 (call or text)
bluebrickmass@gmail.com""",
    },

    "WARM": {
        "subject": "Re: {original_subject}",
        "body": """\
Hi {name},

Thanks for the reply — appreciate you taking the time.

{price_guide_line}

We're based in Waltham and cover 15 cities across Greater Boston. Fully insured, reliable team, and we usually turn quotes around the same day.

If you'd like, I can swing by for a free walkthrough — no commitment, just a chance to see the space and give you an accurate number.

Easiest next step:
- Text me at 781-330-5604 and we'll find a time
- Or just reply here with a couple times that work

Best,
Gerardo
Blue Brick Luxury & Commercial Cleaning
781-330-5604 (call or text)
bluebrickmass@gmail.com""",
    },
}


def get_price_guide_line(category: str) -> str:
    """Get the price guide offer text for this industry, or a generic walkthrough offer."""
    guide = PRICE_GUIDES.get(category)
    if guide:
        return f"{guide['pitch']}:\n{guide['url']}"
    return "Happy to put together a custom quote for your space — just takes a quick walkthrough."


def build_response(intent: str, lead: dict, original_subject: str) -> dict | None:
    """Build a response email based on intent. Returns None for UNSUB/COLD."""
    if intent in ("UNSUB", "COLD"):
        return None

    template = RESPONSES.get(intent, RESPONSES["WARM"])
    name = get_first_name(lead.get("business_name", ""))
    category = lead.get("category", "")

    subject = template["subject"].replace("{original_subject}", original_subject)
    body = template["body"].replace("{name}", name)
    body = body.replace("{price_guide_line}", get_price_guide_line(category))

    return {"subject": subject, "body": body}


# ── HTML Wrapper ──────────────────────────────────────────────────────────────

def wrap_response_html(body_text: str) -> str:
    """Wrap plain text response in branded HTML."""
    lines = body_text.strip().split("\n")
    html_parts = []
    for line in lines:
        line = line.strip()
        if not line:
            html_parts.append("<br>")
        elif line.startswith("- "):
            html_parts.append(
                f'<p style="margin:4px 0 4px 16px;font-size:14px;color:#333;">'
                f'<span style="color:#ECA400;font-weight:700;">&#9654;</span> {line[2:]}</p>'
            )
        else:
            html_parts.append(
                f'<p style="margin:0 0 10px;font-size:14px;line-height:1.6;color:#333;">{line}</p>'
            )

    body_html = "\n".join(html_parts)

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;">
<tr><td align="center" style="padding:20px 10px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:4px;overflow:hidden;">

  <tr><td style="height:4px;background:linear-gradient(90deg,#001D4A,#006992,#ECA400);font-size:0;">&nbsp;</td></tr>

  <tr>
    <td style="padding:24px 36px 16px;text-align:center;">
      <h1 style="margin:0;font-family:Georgia,serif;font-size:24px;color:#001D4A;letter-spacing:2px;">
        BLUE <span style="color:#ECA400;">BRICK</span>
      </h1>
      <p style="margin:4px 0 0;font-size:10px;letter-spacing:2px;color:#8aa8c7;text-transform:uppercase;">
        Luxury &amp; Commercial Cleaning
      </p>
    </td>
  </tr>

  <tr>
    <td style="padding:20px 36px 24px;font-family:Arial,Helvetica,sans-serif;">
      {body_html}
    </td>
  </tr>

  <tr>
    <td align="center" style="padding:8px 36px 24px;">
      <table role="presentation" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background:#ECA400;border-radius:4px;">
            <a href="https://bluebrickmass.com/#estimate"
               style="display:inline-block;padding:12px 28px;font-family:Arial,sans-serif;font-size:14px;font-weight:700;color:#001D4A;text-decoration:none;">
              SCHEDULE A WALKTHROUGH
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <tr>
    <td style="background:#001D4A;padding:16px 32px;text-align:center;">
      <p style="margin:0;font-family:Arial,sans-serif;font-size:12px;color:#5a7a9a;">
        Blue Brick &middot; 781-330-5604 &middot; bluebrickmass@gmail.com<br>
        Waltham, MA &middot; 15 Cities Across Greater Boston
      </p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""


# ── Sending ───────────────────────────────────────────────────────────────────

def send_via_mail_app(to_email: str, subject: str, html_body: str,
                      dry_run: bool = False) -> bool:
    """Send response via Mac Mail.app."""
    if dry_run:
        print(f"    [DRY RUN] Would send to {to_email}")
        return True

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".html", prefix="bb_resp_")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(html_body)

        safe_subject = subject.replace("\\", "\\\\").replace('"', '\\"')
        safe_to = to_email.replace("\\", "\\\\").replace('"', '\\"')
        safe_sender = GMAIL_USER.replace("\\", "\\\\").replace('"', '\\"')

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


def log_response(entry: dict):
    """Log a response to response_log.csv."""
    file_exists = RESPONSE_LOG.exists() and RESPONSE_LOG.stat().st_size > 0
    with open(RESPONSE_LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESPONSE_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)


# ── Main ──────────────────────────────────────────────────────────────────────

def load_already_responded() -> set:
    """Load emails we've already responded to."""
    responded = set()
    if RESPONSE_LOG.exists():
        with open(RESPONSE_LOG, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                responded.add(row.get("to_email", "").lower())
    return responded


def show_status():
    """Show summary of replies and responses."""
    print(f"\n🧱 Blue Brick Responder — Status")
    print(f"{'='*50}")

    if not REPLY_LOG.exists():
        print("  No replies logged yet.")
        return

    with open(REPLY_LOG, "r") as f:
        reader = csv.DictReader(f)
        replies = list(reader)

    responded = load_already_responded()

    hot = [r for r in replies if r.get("hot_lead") == "YES"]
    warm = [r for r in replies if r.get("hot_lead") != "YES"]
    pending = [r for r in replies if r.get("from_email", "").lower() not in responded]

    print(f"  Total replies: {len(replies)}")
    print(f"  Hot leads:     {len(hot)}")
    print(f"  Warm leads:    {len(warm)}")
    print(f"  Responded:     {len(responded)}")
    print(f"  Pending:       {len(pending)}")
    print(f"{'='*50}\n")

    if hot:
        print("  🔥 Hot Leads:")
        for r in hot:
            status = "✓ responded" if r.get("from_email", "").lower() in responded else "⏳ pending"
            print(f"    {r['business_name']} <{r['from_email']}> — {status}")
        print()

    if pending:
        print("  ⏳ Pending Responses:")
        for r in pending:
            intent = detect_intent(r.get("subject", ""), r.get("snippet", ""))
            print(f"    {r['business_name']} ({intent}) — {r.get('snippet', '')[:60]}...")
        print()


def process_replies(dry_run: bool = False):
    """Process all unresponded replies."""
    print(f"\n🧱 Blue Brick Auto-Responder")
    print(f"   Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"   Sender: {GMAIL_USER}")
    print()

    if not REPLY_LOG.exists():
        print("  No replies to process. Run monitor_replies.py first.")
        return

    with open(REPLY_LOG, "r") as f:
        reader = csv.DictReader(f)
        replies = list(reader)

    responded = load_already_responded()
    pending = [r for r in replies if r.get("from_email", "").lower() not in responded]

    if not pending:
        print("  All replies have been responded to.")
        return

    print(f"  Pending responses: {len(pending)}\n")

    sent_count = 0
    for i, reply in enumerate(pending):
        email_addr = reply.get("from_email", "")
        business = reply.get("business_name", "")
        subject = reply.get("subject", "")
        snippet = reply.get("snippet", "")
        category = reply.get("category", "")

        intent = detect_intent(subject, snippet)

        print(f"  [{i+1}/{len(pending)}] {business} <{email_addr}>")
        print(f"       Intent: {intent}")
        print(f"       Subject: {subject}")

        if intent == "UNSUB":
            print(f"       → Skipping (unsubscribe request)")
            log_response({
                "timestamp": datetime.now().isoformat(),
                "to_email": email_addr,
                "business_name": business,
                "category": category,
                "intent": intent,
                "subject": "",
                "status": "skipped_unsub",
            })
            continue

        if intent == "COLD":
            print(f"       → Skipping (auto-reply/OOO)")
            log_response({
                "timestamp": datetime.now().isoformat(),
                "to_email": email_addr,
                "business_name": business,
                "category": category,
                "intent": intent,
                "subject": "",
                "status": "skipped_cold",
            })
            continue

        response = build_response(intent, reply, subject)
        if not response:
            continue

        html = wrap_response_html(response["body"])
        success = send_via_mail_app(email_addr, response["subject"], html, dry_run=dry_run)

        if success:
            sent_count += 1
            status = "dry_run" if dry_run else "sent"
            print(f"       → {'Would send' if dry_run else 'Sent ✓'}")
        else:
            status = "failed"
            print(f"       → Failed ✗")

        log_response({
            "timestamp": datetime.now().isoformat(),
            "to_email": email_addr,
            "business_name": business,
            "category": category,
            "intent": intent,
            "subject": response["subject"],
            "status": status,
        })

        # Rate limit
        if not dry_run and i < len(pending) - 1:
            delay = random.uniform(EMAIL_DELAY_MIN, EMAIL_DELAY_MAX)
            print(f"       ⏳ Waiting {delay:.0f}s...")
            time.sleep(delay)

    print(f"\n{'='*50}")
    print(f"  Done — {sent_count}/{len(pending)} responses {'previewed' if dry_run else 'sent'}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blue Brick Auto-Responder")
    parser.add_argument("--send", action="store_true", help="Send responses to pending replies")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Preview without sending")
    parser.add_argument("--status", "-s", action="store_true", help="Show reply/response status")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.send or args.dry_run:
        process_replies(dry_run=args.dry_run)
    else:
        print("Use --status to check replies, --dry-run to preview, or --send to respond.")
