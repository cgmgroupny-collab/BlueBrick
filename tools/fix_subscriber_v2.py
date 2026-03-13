#!/usr/bin/env python3
"""
1. Fix footer subscriber CTA — bigger, centered, eye-catching
2. Add inline subscriber CTA between blog post sections
3. Fix footer grid alignment
"""

import os
import glob
import re

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# ── REPLACE subscribe CSS with improved version ──
OLD_SUBSCRIBE_CSS_START = """
        /* ============================================
           EMAIL SUBSCRIBER
           ============================================ */
        .subscribe-form {"""

NEW_SUBSCRIBE_CSS = """
        /* ============================================
           EMAIL SUBSCRIBER
           ============================================ */
        .footer-cta {
            background: linear-gradient(135deg, #ECA400 0%, #d4940a 100%);
            padding: 3rem 2rem;
            text-align: center;
            position: relative;
            z-index: 1;
        }

        .footer-cta h3 {
            font-family: var(--font-display, 'Playfair Display', serif);
            font-size: 1.8rem;
            color: #001D4A;
            margin: 0 0 0.5rem;
            font-weight: 800;
        }

        .footer-cta > .footer-cta-inner > p {
            font-size: 0.95rem;
            color: rgba(0, 29, 74, 0.75);
            margin: 0 0 1.5rem;
            line-height: 1.5;
        }

        .subscribe-form {"""

# ── REPLACE the old subscribe CSS block entirely ──
OLD_SUB_BLOCK = """
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

NEW_SUB_BLOCK = """
        /* ============================================
           EMAIL SUBSCRIBER
           ============================================ */
        .footer-cta {
            background: linear-gradient(135deg, #ECA400 0%, #d4940a 100%);
            padding: 3rem 2rem;
            text-align: center;
            position: relative;
            z-index: 1;
        }

        .footer-cta-inner {
            max-width: 560px;
            margin: 0 auto;
        }

        .footer-cta h3 {
            font-family: var(--font-display, 'Playfair Display', serif);
            font-size: 1.8rem;
            color: #001D4A;
            margin: 0 0 0.5rem;
            font-weight: 800;
        }

        .footer-cta-inner > p {
            font-size: 0.95rem;
            color: rgba(0, 29, 74, 0.7);
            margin: 0 0 1.5rem;
            line-height: 1.5;
        }

        .subscribe-form {
            max-width: 480px;
            margin: 0 auto;
        }

        .subscribe-input-wrap {
            display: flex;
            gap: 0;
            border-radius: 50px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 29, 74, 0.2);
            border: 2px solid #001D4A;
        }

        .subscribe-input-wrap input[type="email"] {
            flex: 1;
            padding: 0.9rem 1.4rem;
            border: none;
            font-size: 0.95rem;
            font-family: inherit;
            background: #fff;
            color: #001D4A;
            outline: none;
            min-width: 0;
        }

        .subscribe-input-wrap input[type="email"]::placeholder {
            color: #94a3b8;
        }

        .subscribe-btn {
            background: #001D4A;
            color: #fff;
            font-weight: 700;
            font-size: 0.9rem;
            padding: 0.9rem 1.8rem;
            border: none;
            cursor: pointer;
            white-space: nowrap;
            letter-spacing: 0.02em;
            transition: background 0.2s;
            font-family: inherit;
        }

        .subscribe-btn:hover {
            background: #002a6b;
        }

        .subscribe-note {
            font-size: 0.72rem;
            color: rgba(0, 29, 74, 0.45) !important;
            margin: 0.6rem 0 0 !important;
            text-align: center;
        }

        .subscribe-success {
            color: #001D4A !important;
            font-weight: 600;
            font-size: 0.95rem;
            margin-top: 0.8rem !important;
        }

        /* Inline blog subscriber CTA */
        .inline-subscribe {
            background: linear-gradient(135deg, #ECA400 0%, #f4be3a 100%);
            border-radius: 16px;
            padding: 2rem 1.5rem;
            margin: 2.5rem 0;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .inline-subscribe::before {
            content: '';
            position: absolute;
            top: -30%;
            left: -10%;
            width: 160px;
            height: 160px;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
            pointer-events: none;
        }

        .inline-subscribe h3 {
            font-family: var(--font-display, 'Playfair Display', serif);
            font-size: 1.3rem;
            color: #001D4A;
            margin: 0 0 0.35rem;
            font-weight: 800;
        }

        .inline-subscribe > p {
            font-size: 0.85rem;
            color: rgba(0, 29, 74, 0.7);
            margin: 0 0 1rem;
            line-height: 1.4;
        }

        .inline-subscribe .subscribe-form {
            max-width: 400px;
        }

        .inline-subscribe .subscribe-input-wrap {
            border-width: 1.5px;
        }

        .inline-subscribe .subscribe-input-wrap input[type="email"] {
            padding: 0.75rem 1.2rem;
            font-size: 0.88rem;
        }

        .inline-subscribe .subscribe-btn {
            padding: 0.75rem 1.4rem;
            font-size: 0.85rem;
        }

        .inline-subscribe .subscribe-note {
            color: rgba(0, 29, 74, 0.4) !important;
            font-size: 0.68rem;
        }

        @media (max-width: 480px) {
            .inline-subscribe { padding: 1.5rem 1.25rem; }
            .inline-subscribe h3 { font-size: 1.15rem; }
            .footer-cta h3 { font-size: 1.4rem; }
        }

"""

# ── OLD footer-cta CSS to remove (it's now in the subscribe block) ──
OLD_FOOTER_CTA_CSS = """        .footer-cta {
            background: linear-gradient(135deg, rgba(0, 29, 74, 0.95), rgba(10, 42, 92, 0.92));
            padding: 2.5rem 2rem;
            text-align: center;
            position: relative;
            z-index: 1;
        }

        .footer-cta-inner {
            max-width: 640px;
            margin: 0 auto;
        }

        .footer-cta h3 {
            font-family: var(--font-display, 'Playfair Display', serif);
            font-size: 1.5rem;
            color: #ffffff;
            margin: 0 0 0.4rem;
            font-weight: 700;
        }

        .footer-cta p {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.7);
            margin: 0 0 1.2rem;
            line-height: 1.5;
        }

        .footer-cta-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, #ECA400, #d4940a);
            color: #001D4A !important;
            font-weight: 700;
            font-size: 0.9rem;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            text-decoration: none !important;
            letter-spacing: 0.02em;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 16px rgba(236, 164, 0, 0.3);
        }

        .footer-cta-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(236, 164, 0, 0.45);
            background: linear-gradient(135deg, #f4be3a, #ECA400);
        }

"""

# ── Inline subscriber HTML (inserted into blog articles) ──
INLINE_SUB_HTML = '''
                    <div class="inline-subscribe">
                        <h3>Win a Free Cleaning</h3>
                        <p>Enter your email for a chance to win a complimentary home cleaning every month.</p>
                        <form class="subscribe-form" onsubmit="return handleSubscribe(event)">
                            <div class="subscribe-input-wrap">
                                <input type="email" id="inlineSub" placeholder="Your email address" required autocomplete="email">
                                <button type="submit" class="subscribe-btn">Enter</button>
                            </div>
                            <p class="subscribe-note">No spam. Unsubscribe anytime.</p>
                        </form>
                    </div>
'''

# ── Fix inline subscribe JS to handle multiple forms ──
OLD_SUB_JS = """
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

NEW_SUB_JS = """
        // -- Email subscriber form (handles multiple forms) --
        function handleSubscribe(e) {
            e.preventDefault();
            var form = e.target;
            var input = form.querySelector('input[type="email"]');
            var email = input ? input.value.trim() : '';
            if (!email) return false;
            fetch('/api/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, page: window.location.pathname })
            }).catch(function() {});
            // Replace form with success message
            form.innerHTML = '<p style="color:#001D4A;font-weight:700;font-size:0.95rem;margin:0.5rem 0;">You\\'re in! Good luck this month.</p>';
            return false;
        }
"""


def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    basename = os.path.basename(filepath)
    changes = []

    # 1. Replace subscribe CSS block
    if OLD_SUB_BLOCK in content:
        content = content.replace(OLD_SUB_BLOCK, NEW_SUB_BLOCK)
        changes.append('css')

    # 2. Remove old footer-cta CSS (now in subscribe block)
    if OLD_FOOTER_CTA_CSS in content:
        content = content.replace(OLD_FOOTER_CTA_CSS, '')
        changes.append('rm-old-cta-css')

    # 3. Fix mobile media query refs
    content = content.replace(
        ".footer-cta { padding: 2rem 1.5rem; }\n            .footer-cta h3 { font-size: 1.2rem; }",
        ".footer-cta { padding: 2rem 1.5rem; }\n            .footer-cta h3 { font-size: 1.3rem; }"
    )

    # 4. Replace subscribe JS
    if OLD_SUB_JS in content:
        content = content.replace(OLD_SUB_JS, NEW_SUB_JS)
        changes.append('js')

    # 5. Insert inline subscriber CTA into blog article (after 3rd <h2>)
    if 'inline-subscribe' not in content and '<section class="article-section">' in content:
        h2_positions = [m.start() for m in re.finditer(r'<h2>', content)]
        if len(h2_positions) >= 4:
            # Insert before the 4th h2 (after 3rd section)
            # Find the parent <div> closing before the 4th h2
            target_h2 = h2_positions[3]
            # Walk back to find the preceding paragraph end
            insert_pos = content.rfind('</p>', 0, target_h2)
            if insert_pos != -1:
                insert_pos = insert_pos + len('</p>')
                content = content[:insert_pos] + INLINE_SUB_HTML + content[insert_pos:]
                changes.append('inline-cta')

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
    # Add root pages
    for name in ['index.html', 'cities.html']:
        files.append(os.path.join(BASE_DIR, name))
    files.append(os.path.join(BASE_DIR, 'tools', 'quote-calculator.html'))
    
    updated = 0
    for f in files:
        if not os.path.exists(f):
            continue
        if os.path.basename(f) == 'index.html' and 'blog' in f:
            pass  # blog/index.html included via glob
        if process_file(f):
            updated += 1

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
