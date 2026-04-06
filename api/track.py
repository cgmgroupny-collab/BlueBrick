"""
Vercel Serverless Function: Email Open Tracking Pixel
Serves a 1x1 transparent GIF and notifies via Telegram when a lead opens an email.

Query params:
  e  — base64-encoded email address
  b  — base64-encoded business name
  c  — category (plain text)
"""

import json
import os
import base64
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime


# 1x1 transparent GIF (43 bytes)
PIXEL = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Category display names
CATEGORY_LABELS = {
    "property_managers": "Property Manager",
    "contractors": "Contractor",
    "realtors": "Realtor",
    "restaurants": "Restaurant",
    "daycares": "Daycare",
    "airbnb_hosts": "Airbnb Host",
    "interior_designers": "Interior Designer",
}


def send_telegram(text: str):
    """Send a notification via Telegram bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
        }).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)

        # Decode tracking info
        email_addr = ""
        business = ""
        category = ""
        try:
            if "e" in params:
                email_addr = base64.b64decode(params["e"][0]).decode("utf-8")
            if "b" in params:
                business = base64.b64decode(params["b"][0]).decode("utf-8")
            if "c" in params:
                category = params["c"][0]
        except Exception:
            pass

        # Send Telegram notification
        if email_addr:
            cat_label = CATEGORY_LABELS.get(category, category.replace("_", " ").title())
            now = datetime.utcnow().strftime("%I:%M %p UTC, %b %d")
            msg = (
                f"\U0001f4ec Email Opened\n\n"
                f"Business: {business or 'Unknown'}\n"
                f"Email: {email_addr}\n"
                f"Industry: {cat_label}\n"
                f"Time: {now}"
            )
            send_telegram(msg)

        # Return 1x1 transparent GIF with no-cache headers
        self.send_response(200)
        self.send_header("Content-Type", "image/gif")
        self.send_header("Content-Length", str(len(PIXEL)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(PIXEL)

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
