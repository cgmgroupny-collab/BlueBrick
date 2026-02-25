#!/usr/bin/env python3
"""
Blue Brick iMessage Auto-Responder
Monitors incoming iMessages and auto-replies to business-related messages
using Claude API for classification and response generation.
"""

import sqlite3
import subprocess
import time
import json
import logging
import os
import re
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# ── Paths ──
MESSAGES_DB = os.path.expanduser("~/Library/Messages/chat.db")
PROJECT_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_DIR / "tools"
STATE_FILE = TOOLS_DIR / "responder_state.json"
LOG_FILE = TOOLS_DIR / "responder.log"
ENV_FILE = PROJECT_DIR / ".env"

# ── Config ──
POLL_INTERVAL = 45
MAX_REPLIES_PER_MINUTE = 5
MAX_REPLY_LENGTH = 500
CONFIDENCE_THRESHOLD = 0.8
SHORT_CODE_MAX_LEN = 6

# ── Claude System Prompt ──
SYSTEM_PROMPT = """You are an AI assistant for Everlast GC, a general contractor and home services company in Las Vegas. You are helping triage and respond to incoming text messages on behalf of the Everlast GC team.

ABOUT EVERLAST GC:
- Business: Everlast GC
- Location: Las Vegas, NV
- Focus: General contracting and home services

SERVICES OFFERED:
- Post-Construction Cleanup: dust removal, debris cleanup, surface polishing after new builds and renovations
- Renovation & Remodeling: kitchen remodels, bathroom remodels, gut rehabs, home additions
- General Contracting: new builds, commercial buildouts, tenant improvements
- Home Repairs & Maintenance: drywall, painting, flooring, plumbing, electrical
- Residential Cleaning: deep cleaning, move-in/move-out cleaning, regular maintenance cleaning
- Commercial Cleaning: offices, retail spaces, warehouses
- Exterior Services: landscaping, pressure washing, snow removal, fencing
- Handyman Services: general repairs, fixture installation, minor renovations

PROPERTY TYPES SERVED:
- Single Family Homes
- Apartments / Condos
- Townhouses
- Commercial Offices
- Retail Spaces
- Multi-Unit Buildings
- New Construction Sites

PRICING GUIDANCE (do NOT quote exact prices -- always say you'll need to assess the property/job):
- Pricing depends on scope of work, square footage, materials, and condition
- Free estimates available
- Always invite them to describe the job or schedule a walkthrough

YOUR TASK:
Analyze the incoming message and respond with a JSON object (no markdown, no code fences):

{
    "classification": "business" | "personal" | "spam" | "unclear",
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation of why you classified it this way",
    "reply": "the reply text to send, or null if not business-related"
}

CLASSIFICATION RULES:
- "business": Message is asking about home services, cleaning, remodeling, contracting, repairs, quotes, scheduling, availability, or any home/commercial service inquiry. Also includes existing customer coordination (crew arrival times, job updates, payment discussions for services rendered).
- "personal": Clearly personal conversation not related to business (friends, family, casual chat)
- "spam": Automated messages, marketing, bank notifications, carrier messages, scam attempts
- "unclear": Cannot determine intent; could go either way

REPLY GUIDELINES (when classification is "business"):
- Write on behalf of Everlast GC, professional but warm and friendly
- Keep replies under 300 characters when possible -- this is iMessage, not email
- Be helpful and specific to what they asked
- For quote requests: ask about property type, size, and location if not provided
- For scheduling: express availability and ask for their preferred time
- For general inquiries: briefly describe the relevant service and offer a free estimate
- NEVER make up specific prices
- NEVER claim availability for a specific date/time without being asked
- Include a call-to-action (schedule walkthrough, call for details, etc.)
- Sign off with "- Everlast GC, Las Vegas"

WHEN NOT TO REPLY (set reply to null):
- classification is "personal", "spam", or "unclear"
- confidence below 0.8 for business classification
- Message is just "ok", "thanks", "👍" or similar brief acknowledgments (classify as "unclear")
"""


# ── Logging ──
def setup_logging():
    logger = logging.getLogger("bluebrick_responder")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(asctime)s | %(message)s", datefmt="%H:%M:%S"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


# ── State Persistence ──
def get_current_max_rowid():
    conn = sqlite3.connect(MESSAGES_DB)
    row = conn.execute("SELECT MAX(ROWID) FROM message").fetchone()
    conn.close()
    return row[0] if row and row[0] else 0


def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {
        "last_rowid": get_current_max_rowid(),
        "replied_rowids": [],
        "send_timestamps": []
    }


def save_state(state):
    tmp = STATE_FILE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    tmp.rename(STATE_FILE)


# ── Text Extraction ──
def extract_text_from_attributed_body(blob):
    """Extract plain text from NSAttributedString binary blob."""
    if not blob:
        return None
    try:
        import re
        parts = re.findall(rb'[\x20-\x7e\xc0-\xff]{4,}', blob)
        decoded = [p.decode('utf-8', errors='ignore') for p in parts]
        # The actual message text is usually the longest readable string
        # that isn't an Objective-C class name
        ns_prefixes = ('NSMutable', 'NSString', 'NSObject', 'NSAttributed',
                       'NSDictionary', 'NSNumber', 'NSValue', 'streamtyped',
                       '__kIM')
        candidates = [s for s in decoded if not any(s.startswith(p) for p in ns_prefixes)]
        if candidates:
            # Get the longest candidate, strip leading non-alpha chars
            best = max(candidates, key=len)
            # Strip leading binary artifacts like "+(" etc
            best = re.sub(r'^[^a-zA-Z\u00c0-\u024f]+', '', best)
            return best.strip() if best.strip() else None
    except Exception:
        pass
    return None


# ── Database Queries ──
def fetch_new_messages(last_rowid):
    conn = sqlite3.connect(MESSAGES_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT
            m.ROWID as rowid,
            m.text as text,
            m.attributedBody as attr_body,
            h.id as phone,
            m.cache_roomnames as room_name,
            m.associated_message_type as assoc_type,
            m.is_from_me as is_from_me,
            datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date_str
        FROM message m
        LEFT JOIN handle h ON m.handle_id = h.ROWID
        WHERE m.ROWID > ?
        ORDER BY m.ROWID ASC
    """, (last_rowid,))
    messages = []
    for row in cursor:
        msg = dict(row)
        # Fall back to attributedBody if text is empty
        if not msg["text"] and msg.get("attr_body"):
            msg["text"] = extract_text_from_attributed_body(msg["attr_body"])
        # Remove the blob from the dict (not needed after extraction)
        msg.pop("attr_body", None)
        messages.append(msg)
    conn.close()
    return messages


def get_conversation_context(phone, limit=5):
    conn = sqlite3.connect(MESSAGES_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT m.text, m.is_from_me,
               datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date_str
        FROM message m
        JOIN handle h ON m.handle_id = h.ROWID
        WHERE h.id = ?
          AND m.text IS NOT NULL
          AND m.text != ''
          AND m.cache_roomnames IS NULL
          AND m.associated_message_type = 0
        ORDER BY m.date DESC
        LIMIT ?
    """, (phone, limit)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


# ── Message Filtering ──
def should_process(msg, replied_rowids, logger):
    rowid = msg["rowid"]
    text = msg["text"]
    phone = msg["phone"]

    if msg["is_from_me"]:
        logger.debug(f"[{rowid}] SKIP: is_from_me")
        return False

    if msg["room_name"] is not None:
        logger.debug(f"[{rowid}] SKIP: group chat")
        return False

    if msg["assoc_type"] and msg["assoc_type"] != 0:
        logger.debug(f"[{rowid}] SKIP: tapback/reaction")
        return False

    if not text or not text.strip():
        logger.debug(f"[{rowid}] SKIP: empty text")
        return False

    if phone and len(phone.replace("+", "").replace("-", "").replace(" ", "")) <= SHORT_CODE_MAX_LEN:
        logger.debug(f"[{rowid}] SKIP: short code ({phone})")
        return False

    if rowid in replied_rowids:
        logger.debug(f"[{rowid}] SKIP: already handled")
        return False

    return True


# ── Rate Limiting ──
def check_rate_limit(state):
    now = datetime.now()
    one_minute_ago = now - timedelta(minutes=1)
    state["send_timestamps"] = [
        ts for ts in state["send_timestamps"]
        if datetime.fromisoformat(ts) > one_minute_ago
    ]
    return len(state["send_timestamps"]) < MAX_REPLIES_PER_MINUTE


def record_send(state):
    state["send_timestamps"].append(datetime.now().isoformat())


# ── Claude API ──
def classify_and_reply(client, message_text, phone):
    context = get_conversation_context(phone)
    if context:
        context_str = "\n".join([
            f"{'Gerardo' if m['is_from_me'] else 'Customer'} ({m['date_str']}): {m['text']}"
            for m in context
        ])
        user_prompt = f"Recent conversation with {phone}:\n{context_str}\n\nNew incoming message:\n{message_text}"
    else:
        user_prompt = f"Incoming iMessage from {phone}:\n\n{message_text}"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    return json.loads(raw)


# ── Send Message ──
def send_message(phone, message, logger):
    """Send via iMessage first, fall back to SMS if iMessage fails."""
    safe_message = message.replace("\\", "\\\\").replace('"', '\\"')

    # Try SMS first (works for both Android and iPhone), then iMessage as fallback
    services = ["SMS", "iMessage"]
    for service in services:
        applescript = f'''
        tell application "Messages"
            set targetBuddy to "{phone}"
            set targetService to id of 1st account whose service type = {service}
            set theBuddy to participant targetBuddy of account id targetService
            send "{safe_message}" to theBuddy
        end tell
        '''

        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info(f"SENT via {service} to {phone}: {message[:100]}...")
                return True
            else:
                logger.warning(f"{service} failed for {phone}: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            logger.error(f"AppleScript timeout ({service}) sending to {phone}")
        except Exception as e:
            logger.error(f"Send failed ({service}) for {phone}: {e}")

    logger.error(f"All send methods failed for {phone}")
    return False


# ── Main Loop ──
def main():
    load_dotenv(ENV_FILE)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(f"ERROR: ANTHROPIC_API_KEY not found in {ENV_FILE}")
        sys.exit(1)

    logger = setup_logging()
    client = Anthropic(api_key=api_key)
    state = load_state()
    replied_rowids = set(state.get("replied_rowids", []))

    logger.info(f"Blue Brick Auto-Responder starting. Cursor at ROWID {state['last_rowid']}")
    logger.info(f"Polling every {POLL_INTERVAL}s | Confidence threshold: {CONFIDENCE_THRESHOLD}")

    running = True

    def handle_signal(signum, frame):
        nonlocal running
        logger.info(f"Received signal {signum}, shutting down...")
        running = False

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    while running:
        try:
            new_messages = fetch_new_messages(state["last_rowid"])

            if new_messages:
                logger.info(f"Found {len(new_messages)} new message(s) since ROWID {state['last_rowid']}")

            for msg in new_messages:
                state["last_rowid"] = max(state["last_rowid"], msg["rowid"])

                if not should_process(msg, replied_rowids, logger):
                    continue

                logger.info(
                    f"[{msg['rowid']}] Processing from {msg['phone']}: "
                    f"{msg['text'][:80]}{'...' if len(msg['text'] or '') > 80 else ''}"
                )

                if not check_rate_limit(state):
                    logger.warning(f"[{msg['rowid']}] Rate limit reached, deferring")
                    state["last_rowid"] = msg["rowid"] - 1
                    break

                try:
                    result = classify_and_reply(client, msg["text"], msg["phone"])
                except json.JSONDecodeError as e:
                    logger.error(f"[{msg['rowid']}] Claude returned invalid JSON: {e}")
                    replied_rowids.add(msg["rowid"])
                    continue
                except Exception as e:
                    logger.error(f"[{msg['rowid']}] Claude API error: {e}")
                    continue

                logger.info(
                    f"[{msg['rowid']}] Classification: {result['classification']} "
                    f"(confidence={result['confidence']}) -- {result['reasoning']}"
                )

                if (result["classification"] == "business"
                        and result["confidence"] >= CONFIDENCE_THRESHOLD
                        and result.get("reply")):

                    reply_text = result["reply"][:MAX_REPLY_LENGTH]

                    if send_message(msg["phone"], reply_text, logger):
                        record_send(state)
                        replied_rowids.add(msg["rowid"])
                        logger.info(f"[{msg['rowid']}] Reply sent successfully")
                    else:
                        logger.error(f"[{msg['rowid']}] Failed to send reply")
                else:
                    replied_rowids.add(msg["rowid"])
                    logger.info(f"[{msg['rowid']}] No reply sent (not business or low confidence)")

            # Persist state
            state["replied_rowids"] = list(replied_rowids)[-500:]
            save_state(state)

        except Exception as e:
            logger.exception(f"Unexpected error in main loop: {e}")

        # Sleep in 1s chunks for responsive shutdown
        for _ in range(POLL_INTERVAL):
            if not running:
                break
            time.sleep(1)

    # Final save
    state["replied_rowids"] = list(replied_rowids)[-500:]
    save_state(state)
    logger.info("Auto-responder stopped cleanly.")


if __name__ == "__main__":
    main()
