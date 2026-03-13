#!/usr/bin/env python3
"""Reorganize footer: add Quick Links, email subscriber form, expand layout."""

import os
import glob
import re

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# ── NEW FOOTER HTML (blog posts — paths with ../) ──
BLOG_FOOTER = '''    <footer role="contentinfo">
        <div class="footer-bg"></div>

        <!-- Email Subscriber CTA -->
        <div class="footer-cta">
            <div class="footer-cta-inner">
                <h3>Win a Free Cleaning Every Month</h3>
                <p>Subscribe and get entered to win a complimentary home cleaning — one lucky winner each month.</p>
                <form class="subscribe-form" id="subscribeForm" onsubmit="return handleSubscribe(event)">
                    <div class="subscribe-input-wrap">
                        <input type="email" id="subEmail" placeholder="Enter your email" required autocomplete="email">
                        <button type="submit" class="subscribe-btn">Subscribe</button>
                    </div>
                    <p class="subscribe-note">No spam, ever. Unsubscribe anytime.</p>
                </form>
                <p class="subscribe-success" id="subscribeSuccess" style="display:none;">You\'re in! Check your inbox for confirmation.</p>
            </div>
        </div>

        <div class="footer-top">
            <div class="footer-brand">
                <div class="footer-logo">
                    <img src="../assets/images/IMG_9670.png" alt="Blue Brick — Luxury & Commercial Cleaning">
                </div>
                <p>Boston\'s trusted deep cleaning and luxury property care.</p>
                <a href="sms:+17813305604" class="contact-line" aria-label="Text us">
                    <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                    (781) 330-5604
                </a>
                <a href="mailto:bluebrickmass@gmail.com" class="contact-line" aria-label="Email us">
                    <svg viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                    bluebrickmass@gmail.com
                </a>
            </div>

            <div class="footer-col">
                <h4>Quick Links</h4>
                <nav class="footer-links-list" aria-label="Quick links">
                    <a href="/">Home</a>
                    <a href="/cities.html">Service Areas</a>
                    <a href="/blog/">Blog</a>
                    <a href="/tools/quote-calculator.html">Quote Calculator</a>
                    <a href="/#quote">Free Estimate</a>
                    <a href="sms:+17813305604">Text Us</a>
                </nav>
            </div>

            <div class="footer-col">
                <h4>Services</h4>
                <nav class="footer-links-list" aria-label="Cleaning services">
                    <a href="/blog/deep-cleaning-boston.html">Deep Cleaning</a>
                    <a href="/blog/post-construction-cleaning-boston.html">Post-Construction</a>
                    <a href="/blog/move-in-move-out-cleaning-boston.html">Move-In / Move-Out</a>
                    <a href="/#quote">Luxury Residential</a>
                    <a href="/#quote">Commercial Cleaning</a>
                    <a href="/blog/spring-cleaning-boston.html">Spring Cleaning</a>
                </nav>
            </div>

            <div class="footer-col">
                <h4>Top Areas</h4>
                <nav class="footer-links-list" aria-label="Service areas">
                    <a href="/blog/deep-cleaning-boston.html">Boston</a>
                    <a href="/blog/deep-cleaning-cambridge.html">Cambridge</a>
                    <a href="/blog/deep-cleaning-newton.html">Newton</a>
                    <a href="/blog/deep-cleaning-waltham.html">Waltham</a>
                    <a href="/blog/deep-cleaning-brookline.html">Brookline</a>
                    <a href="/blog/deep-cleaning-somerville.html">Somerville</a>
                    <a href="/cities.html">All 15 Cities →</a>
                </nav>
            </div>
        </div>

        <div class="footer-bottom">
            <p>&copy; 2026 Blue Brick Luxury and Commercial Cleaning. All rights reserved.</p>
        </div>
    </footer>'''

# ── NEW FOOTER HTML (root pages — no ../ prefix) ──
ROOT_FOOTER = BLOG_FOOTER.replace(
    'src="../assets/images/IMG_9670.png"',
    'src="assets/images/IMG_9670.png"'
)

# ── SUBSCRIBE FORM CSS ──
SUBSCRIBE_CSS = """
        /* ============================================
           EMAIL SUBSCRIBER
           ============================================ */
        .subscribe-form {
            max-width: 420px;
            margin: 0 auto;
        }

        .subscribe-input-wrap {
            display: flex;
            gap: 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        }

        .subscribe-input-wrap input[type="email"] {
            flex: 1;
            padding: 0.7rem 1rem;
            border: none;
            font-size: 0.88rem;
            font-family: inherit;
            background: rgba(255, 255, 255, 0.95);
            color: #001D4A;
            outline: none;
            min-width: 0;
        }

        .subscribe-input-wrap input[type="email"]::placeholder {
            color: #94a3b8;
        }

        .subscribe-btn {
            background: linear-gradient(135deg, #ECA400, #d4940a);
            color: #001D4A;
            font-weight: 700;
            font-size: 0.85rem;
            padding: 0.7rem 1.3rem;
            border: none;
            cursor: pointer;
            white-space: nowrap;
            letter-spacing: 0.02em;
            transition: background 0.2s;
            font-family: inherit;
        }

        .subscribe-btn:hover {
            background: linear-gradient(135deg, #f4be3a, #ECA400);
        }

        .subscribe-note {
            font-size: 0.7rem;
            color: rgba(255, 255, 255, 0.4) !important;
            margin: 0.5rem 0 0 !important;
            text-align: center;
        }

        .subscribe-success {
            color: #ECA400 !important;
            font-weight: 600;
            font-size: 0.9rem;
            margin-top: 0.8rem !important;
        }

"""

# ── SUBSCRIBE FORM JS ──
SUBSCRIBE_JS = """
        // -- Email subscriber form --
        function handleSubscribe(e) {
            e.preventDefault();
            var email = document.getElementById('subEmail').value.trim();
            if (!email) return false;
            // Send to API
            fetch('/api/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, page: window.location.pathname })
            }).catch(function() {});
            // Show success
            document.getElementById('subscribeForm').style.display = 'none';
            document.getElementById('subscribeSuccess').style.display = 'block';
            return false;
        }
"""

# ── FOOTER-TOP CSS update: 4 columns instead of 3 ──
OLD_GRID = 'grid-template-columns: 1.2fr 1fr 1fr;'
NEW_GRID = 'grid-template-columns: 1.4fr 1fr 1fr 1fr;'


def process_file(filepath, is_root=False):
    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    basename = os.path.basename(filepath)
    changes = []

    # 1. Replace entire footer block
    new_footer = ROOT_FOOTER if is_root else BLOG_FOOTER
    footer_match = re.search(
        r'    <footer[^>]*>.*?</footer>',
        content,
        re.DOTALL
    )
    if footer_match:
        content = content[:footer_match.start()] + new_footer + content[footer_match.end():]
        changes.append('footer-html')

    # 2. Update grid to 4 columns
    if OLD_GRID in content:
        content = content.replace(OLD_GRID, NEW_GRID)
        changes.append('4-col-grid')

    # 3. Add subscribe CSS before BACK TO TOP or before TUBELIGHT NAVBAR section
    if '.subscribe-form' not in content:
        markers = [
            '        /* ============================================\n           BACK TO TOP',
            '        /* ============================================\n           TUBELIGHT NAVBAR',
        ]
        inserted = False
        for marker in markers:
            if marker in content:
                idx = content.find(marker)
                content = content[:idx] + SUBSCRIBE_CSS + content[idx:]
                changes.append('subscribe-css')
                inserted = True
                break
        if not inserted:
            # Fallback: before </style>
            style_close = content.rfind('</style>')
            if style_close != -1:
                content = content[:style_close] + SUBSCRIBE_CSS + '    </style>' + content[style_close + len('</style>'):]
                changes.append('subscribe-css-fallback')

    # 4. Add subscribe JS before </script> of last script block
    if 'handleSubscribe' not in content:
        body_close = content.rfind('</body>')
        if body_close != -1:
            last_script = content.rfind('</script>', 0, body_close)
            if last_script != -1:
                content = content[:last_script] + SUBSCRIBE_JS + '    </script>' + content[last_script + len('</script>'):]
                changes.append('subscribe-js')

    # 5. Update mobile grid for 4 columns
    old_mobile_grid = ".footer-top { grid-template-columns: 1fr 1fr;"
    new_mobile_grid = ".footer-top { grid-template-columns: 1fr 1fr;"
    # Add 4-col collapse: at tablet show 2x2, at mobile show 1 col
    old_tablet_footer = ".footer-top { grid-template-columns: 1fr 1fr; }"
    if old_tablet_footer in content and '.footer-brand { grid-column: span 2; }' in content:
        # Update to handle 4 columns properly
        content = content.replace(
            ".footer-brand { grid-column: span 2; }",
            ".footer-brand { grid-column: span 2; }\n            .footer-col:last-child { grid-column: span 2; }"
        )
        changes.append('mobile-grid')

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'  OK [{", ".join(changes)}]: {basename}')
        return True
    else:
        print(f'  SKIP: {basename}')
        return False


def main():
    files = sorted(glob.glob(os.path.join(BASE_DIR, 'blog', '*.html')))
    updated = 0

    for f in files:
        if not os.path.exists(f):
            continue
        if process_file(f, is_root=False):
            updated += 1

    # Root pages
    for name in ['index.html', 'cities.html']:
        path = os.path.join(BASE_DIR, name)
        if os.path.exists(path):
            if process_file(path, is_root=True):
                updated += 1

    # tools/quote-calculator.html
    qc = os.path.join(BASE_DIR, 'tools', 'quote-calculator.html')
    if os.path.exists(qc):
        if process_file(qc, is_root=False):
            updated += 1

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
