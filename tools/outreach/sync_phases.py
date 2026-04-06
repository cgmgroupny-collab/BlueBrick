"""
Blue Brick — Phase Sync
------------------------
Cross-references leads.csv, sent_log.csv, reply_log.csv, response_log.csv,
and bounce_log.csv to determine the current phase for each lead.

Updates the LEADS array in lead-command-center.html with accurate phases.

Phases:
  no_email   — No email address on file
  ready      — Has email, not sent yet
  sent       — Email sent, awaiting response
  replied    — Lead replied (warm interest)
  hot        — Lead replied with booking intent
  booked     — Walkthrough/call scheduled
  bounced    — Email bounced
  unsubscribed — Lead opted out

Usage:
    python3 tools/outreach/sync_phases.py           # Sync phases
    python3 tools/outreach/sync_phases.py --status   # Show phase breakdown
"""
import csv
import json
import re
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR

PROJECT_ROOT = Path(__file__).parent.parent.parent
DASHBOARD = PROJECT_ROOT / "lead-command-center.html"
LEADS_CSV = DATA_DIR / "leads.csv"
SENT_LOG = DATA_DIR / "sent_log.csv"
REPLY_LOG = DATA_DIR / "reply_log.csv"
RESPONSE_LOG = DATA_DIR / "response_log.csv"
BOUNCE_LOG = DATA_DIR / "bounce_log.csv"


def load_csv_set(path: Path, key_field: str) -> dict:
    """Load a CSV and index by a key field (lowercased)."""
    index = {}
    if not path.exists():
        return index
    with open(path, "r") as f:
        for row in csv.DictReader(f):
            k = row.get(key_field, "").lower().strip()
            if k:
                if k not in index:
                    index[k] = []
                index[k].append(row)
    return index


def compute_phases() -> dict:
    """
    Compute the phase for each lead email.
    Returns dict mapping email -> phase string.
    """
    phases = {}

    # Load all data sources
    sent = load_csv_set(SENT_LOG, "email")
    replies = load_csv_set(REPLY_LOG, "from_email")
    responses = load_csv_set(RESPONSE_LOG, "to_email")
    bounces = load_csv_set(BOUNCE_LOG, "original_to")

    # Check for unsubscribes in response log
    unsubs = set()
    for email, entries in responses.items():
        for entry in entries:
            if entry.get("intent") == "UNSUB":
                unsubs.add(email)

    # Load leads
    if not LEADS_CSV.exists():
        return phases

    with open(LEADS_CSV, "r") as f:
        for row in csv.DictReader(f):
            email = row.get("email", "").lower().strip()
            if not email:
                phases[row.get("business_name", "").lower()] = "no_email"
                continue

            # Determine phase (priority order)
            if email in unsubs:
                phases[email] = "unsubscribed"
            elif email in bounces:
                phases[email] = "bounced"
            elif email in replies:
                # Check if any reply was hot
                is_hot = any(r.get("hot_lead") == "YES" for r in replies[email])
                phases[email] = "hot" if is_hot else "replied"
            elif email in sent:
                phases[email] = "sent"
            else:
                phases[email] = "ready"

    return phases


def show_status():
    """Print phase breakdown."""
    phases = compute_phases()
    counts = {}
    for phase in phases.values():
        counts[phase] = counts.get(phase, 0) + 1

    phase_order = ["ready", "sent", "replied", "hot", "booked", "bounced", "unsubscribed", "no_email"]
    phase_labels = {
        "no_email": "No Email",
        "ready": "Ready to Send",
        "sent": "Sent (Awaiting)",
        "replied": "Replied (Warm)",
        "hot": "Hot Lead",
        "booked": "Booked",
        "bounced": "Bounced",
        "unsubscribed": "Unsubscribed",
    }

    total = sum(counts.values())
    print(f"\n  Blue Brick — Lead Phase Breakdown")
    print(f"  {'='*40}")
    for phase in phase_order:
        count = counts.get(phase, 0)
        if count:
            bar = "#" * min(count // 2, 30)
            pct = count / total * 100 if total else 0
            print(f"  {phase_labels.get(phase, phase):20s} {count:4d}  ({pct:4.1f}%)  {bar}")
    print(f"  {'─'*40}")
    print(f"  {'Total':20s} {total:4d}")
    print()


def sync_dashboard():
    """Update the LEADS array status field in lead-command-center.html."""
    if not DASHBOARD.exists():
        print("Dashboard not found.")
        return

    phases = compute_phases()
    if not phases:
        print("No phase data to sync.")
        return

    content = DASHBOARD.read_text()

    # Find the LEADS array and update status values
    # The LEADS array has objects with "email" and "status" fields
    updated = 0
    for email, phase in phases.items():
        if not email or "@" not in email:
            continue
        # Find this email in the LEADS array and update its status
        escaped_email = re.escape(email)
        pattern = rf'("email"\s*:\s*"{escaped_email}"\s*,\s*"[^"]*"\s*:\s*"[^"]*"\s*,\s*"status"\s*:\s*")[^"]*(")'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            content = content[:match.start(1)] + match.group(1) + phase + match.group(2) + content[match.end(2):]
            updated += 1
        else:
            # Try alternate field order — status might be in different position
            # Just replace "status":"old" near the email
            # Find the email, then find the nearest status field
            email_pos = content.lower().find(f'"email":"{email}"')
            if email_pos == -1:
                email_pos = content.lower().find(f'"email": "{email}"')
            if email_pos >= 0:
                # Look for "status":"..." within 200 chars
                chunk_start = email_pos
                chunk_end = min(email_pos + 300, len(content))
                chunk = content[chunk_start:chunk_end]
                status_match = re.search(r'"status"\s*:\s*"[^"]*"', chunk)
                if status_match:
                    old = chunk[status_match.start():status_match.end()]
                    new = f'"status":"{phase}"'
                    content = content[:chunk_start + status_match.start()] + new + content[chunk_start + status_match.end():]
                    updated += 1

    if updated:
        DASHBOARD.write_text(content)
        print(f"  Updated {updated} lead phases in dashboard.")
    else:
        print("  No leads matched for update.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blue Brick Phase Sync")
    parser.add_argument("--status", "-s", action="store_true", help="Show phase breakdown only")
    args = parser.parse_args()

    if args.status:
        show_status()
    else:
        show_status()
        sync_dashboard()
