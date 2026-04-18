"""
Vercel Serverless Function: Email Subscriber
Collects subscriber emails and notifies via Email + Telegram.

Stores subscribers in a simple notification — for a full list,
integrate with Mailchimp, ConvertKit, or a Google Sheet later.
"""

import json
import os
import smtplib
import urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import BaseHTTPRequestHandler
from datetime import datetime


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}

            email = body.get('email', '').strip().lower()
            page = body.get('page', 'Unknown')

            if not email or '@' not in email:
                self._respond(400, {'error': 'Valid email required'})
                return

            email = email[:200]
            page = page[:200]
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

            results = {}

            # Notify owner via email
            try:
                self._send_email(email, page, timestamp)
                results['email'] = 'sent'
            except Exception as e:
                results['email'] = f'failed: {str(e)}'

            # Notify owner via Telegram
            try:
                self._send_telegram(email, page, timestamp)
                results['telegram'] = 'sent'
            except Exception as e:
                results['telegram'] = f'failed: {str(e)}'

            self._respond(200, {'ok': True, 'results': results})

        except json.JSONDecodeError:
            self._respond(400, {'error': 'Invalid JSON'})
        except Exception as e:
            self._respond(500, {'error': str(e)})

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def _respond(self, status, data):
        self.send_response(status)
        self._cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _cors_headers(self):
        origin = self.headers.get('Origin', '')
        allowed = [
            'https://bluebrickmass.com',
            'https://bluebrickmass.com',
            'https://bluebrickmass.com',
            'http://localhost',
        ]
        if any(origin.startswith(a) for a in allowed):
            self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send_email(self, subscriber_email, page, timestamp):
        gmail_user = os.environ.get('GMAIL_USER', 'bluebrickmass@gmail.com')
        gmail_pass = os.environ.get('GMAIL_APP_PASSWORD', '')
        notify_email = os.environ.get('NOTIFY_EMAIL', gmail_user)

        if not gmail_pass:
            raise Exception('GMAIL_APP_PASSWORD not set')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'New Subscriber: {subscriber_email}'
        msg['From'] = f'Blue Brick <{gmail_user}>'
        msg['To'] = notify_email

        plain = f"New email subscriber!\n\nEmail: {subscriber_email}\nPage: {page}\nTime: {timestamp}"

        html = f"""
<div style="font-family: -apple-system, sans-serif; max-width: 500px; margin: 0 auto;">
    <div style="background: #001D4A; padding: 16px 20px; border-radius: 12px 12px 0 0;">
        <h2 style="color: #fff; margin: 0; font-size: 16px;">📧 New Subscriber!</h2>
    </div>
    <div style="background: #f8f9fa; padding: 20px; border: 1px solid #e2e8f0;">
        <div style="background: #fff; padding: 14px 16px; border-radius: 10px; border-left: 3px solid #ECA400; margin-bottom: 12px;">
            <p style="margin: 0; font-size: 16px; color: #1a202c; font-weight: 600;">{subscriber_email}</p>
        </div>
        <table style="font-size: 13px; color: #64748b;">
            <tr><td style="padding: 2px 8px 2px 0; font-weight: 600;">Page:</td><td>{page}</td></tr>
            <tr><td style="padding: 2px 8px 2px 0; font-weight: 600;">Time:</td><td>{timestamp}</td></tr>
        </table>
    </div>
    <div style="background: #001D4A; padding: 12px 20px; border-radius: 0 0 12px 12px; text-align: center;">
        <span style="color: rgba(255,255,255,0.5); font-size: 12px;">Free cleaning giveaway subscriber</span>
    </div>
</div>"""

        msg.attach(MIMEText(plain, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_pass)
            smtp.send_message(msg)

    def _send_telegram(self, subscriber_email, page, timestamp):
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

        if not token or not chat_id:
            raise Exception('TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set')

        text = (
            f"📧 *New Subscriber*\n\n"
            f"Email: `{subscriber_email}`\n"
            f"Page: `{page}`\n"
            f"Time: {timestamp}"
        )

        payload = json.dumps({
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown',
        }).encode()

        req = urllib.request.Request(
            f'https://api.telegram.org/bot{token}/sendMessage',
            data=payload,
            headers={'Content-Type': 'application/json'},
        )
        urllib.request.urlopen(req, timeout=5)
