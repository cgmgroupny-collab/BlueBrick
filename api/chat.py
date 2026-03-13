"""
Vercel Serverless Function: Chat Widget Webhook
Receives chat messages and forwards via Email + Telegram.

Environment variables (set in Vercel dashboard):
  GMAIL_USER        — bluebrickmass@gmail.com
  GMAIL_APP_PASSWORD — Gmail app password
  TELEGRAM_BOT_TOKEN — from @BotFather
  TELEGRAM_CHAT_ID   — your personal chat ID
  NOTIFY_EMAIL       — where to send notifications (defaults to GMAIL_USER)
"""

import json
import os
import smtplib
import urllib.request
import urllib.error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import BaseHTTPRequestHandler
from datetime import datetime


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}

            message = body.get('message', '').strip()
            page = body.get('page', 'Unknown page')
            timestamp = body.get('timestamp', datetime.utcnow().isoformat())
            step = body.get('step', '')
            data = body.get('data', {})

            if not message:
                self._respond(400, {'error': 'No message provided'})
                return

            # Sanitize inputs (prevent injection)
            message = message[:1000]
            page = page[:200]
            step = str(step)[:50]

            results = {}

            # Send email notification
            try:
                self._send_email(message, page, timestamp, step, data)
                results['email'] = 'sent'
            except Exception as e:
                results['email'] = f'failed: {str(e)}'

            # Send Telegram notification
            try:
                self._send_telegram(message, page, timestamp, step, data)
                results['telegram'] = 'sent'
            except Exception as e:
                results['telegram'] = f'failed: {str(e)}'

            self._respond(200, {'ok': True, 'results': results})

        except json.JSONDecodeError:
            self._respond(400, {'error': 'Invalid JSON'})
        except Exception as e:
            self._respond(500, {'error': str(e)})

    def do_OPTIONS(self):
        """Handle CORS preflight."""
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
            'https://blue-brick.vercel.app',
            'https://bluebrickcleaning.com',
            'https://www.bluebrickcleaning.com',
            'http://localhost',
        ]
        if any(origin.startswith(a) for a in allowed):
            self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send_email(self, message, page, timestamp, step='', data=None):
        gmail_user = os.environ.get('GMAIL_USER', 'bluebrickmass@gmail.com')
        gmail_pass = os.environ.get('GMAIL_APP_PASSWORD', '')
        notify_email = os.environ.get('NOTIFY_EMAIL', gmail_user)
        data = data or {}

        if not gmail_pass:
            raise Exception('GMAIL_APP_PASSWORD not set')

        # Determine notification type and priority
        is_lead = step in ('collect_phone', 'collect_email', 'quote_done')
        service = data.get('service', '')
        size = data.get('size', '')
        contact = data.get('contact', '')
        contact_method = data.get('contactMethod', '')

        if is_lead:
            subject = f'🔥 NEW LEAD: {service} — {message}'
            priority = 'HIGH'
        elif step in ('quote_type', 'quote_size', 'book'):
            subject = f'👀 Active Quote: {service or message}'
            priority = 'MEDIUM'
        else:
            subject = f'💬 Chat: {message[:50]}'
            priority = 'LOW'

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f'Blue Brick Chat <{gmail_user}>'
        msg['To'] = notify_email

        # Build context section
        details_rows = f'<tr><td style="padding:3px 10px 3px 0;font-weight:600;color:#64748b;">Message:</td><td style="color:#1a202c;">{message}</td></tr>'
        if service:
            details_rows += f'<tr><td style="padding:3px 10px 3px 0;font-weight:600;color:#64748b;">Service:</td><td style="color:#1a202c;">{service}</td></tr>'
        if size:
            details_rows += f'<tr><td style="padding:3px 10px 3px 0;font-weight:600;color:#64748b;">Size:</td><td style="color:#1a202c;">{size}</td></tr>'
        if contact_method:
            details_rows += f'<tr><td style="padding:3px 10px 3px 0;font-weight:600;color:#64748b;">Wants:</td><td style="color:#1a202c;">{contact_method}</td></tr>'
        details_rows += f'<tr><td style="padding:3px 10px 3px 0;font-weight:600;color:#64748b;">Page:</td><td>{page}</td></tr>'
        details_rows += f'<tr><td style="padding:3px 10px 3px 0;font-weight:600;color:#64748b;">Time:</td><td>{timestamp}</td></tr>'

        banner_color = '#dc2626' if is_lead else '#001D4A'
        banner_label = '🔥 NEW LEAD' if is_lead else '💬 Chat Message'

        html = f"""
<div style="font-family:-apple-system,sans-serif;max-width:500px;margin:0 auto;">
    <div style="background:{banner_color};padding:16px 20px;border-radius:12px 12px 0 0;">
        <h2 style="color:#fff;margin:0;font-size:16px;">{banner_label}</h2>
    </div>
    <div style="background:#f8f9fa;padding:20px;border:1px solid #e2e8f0;">
        <table style="font-size:14px;width:100%;">{details_rows}</table>
    </div>
    <div style="background:{banner_color};padding:12px 20px;border-radius:0 0 12px 12px;text-align:center;">
        <a href="sms:+17813305604" style="color:#ECA400;text-decoration:none;font-size:13px;font-weight:600;">Reply via Text →</a>
    </div>
</div>"""

        plain = f"{banner_label}\n\nMessage: {message}\nService: {service}\nSize: {size}\nPage: {page}\nTime: {timestamp}"

        msg.attach(MIMEText(plain, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_pass)
            smtp.send_message(msg)

    def _send_telegram(self, message, page, timestamp, step='', data=None):
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        data = data or {}

        if not token or not chat_id:
            raise Exception('TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set')

        is_lead = step in ('collect_phone', 'collect_email', 'quote_done')
        service = data.get('service', '')
        size = data.get('size', '')
        contact_method = data.get('contactMethod', '')

        if is_lead:
            text = (
                f"🔥🔥 *NEW LEAD* 🔥🔥\n\n"
                f"📝 *{message}*\n"
            )
            if service:
                text += f"🧹 Service: {service}\n"
            if size:
                text += f"📐 Size: {size}\n"
            if contact_method:
                text += f"📱 Wants: {contact_method}\n"
            text += f"\n📄 `{page}`\n🕐 {timestamp}"
        elif step in ('quote_type', 'quote_size', 'book', 'book_contact'):
            text = (
                f"👀 *Active Quote*\n\n"
                f"Selected: *{message}*\n"
            )
            if service:
                text += f"Service: {service}\n"
            if size:
                text += f"Size: {size}\n"
            text += f"\n📄 `{page}` | 🕐 {timestamp}"
        else:
            text = (
                f"💬 `{message}`\n"
                f"📄 {page} | 🕐 {timestamp}"
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
