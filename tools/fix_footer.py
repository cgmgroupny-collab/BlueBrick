#!/usr/bin/env python3
"""
Enhance blog post footers:
1. Add background image with dark overlay
2. Add CTA banner above footer columns
3. Add back-to-top button
4. Brighter, more appealing text
5. Better spacing and visual hierarchy
"""

import os
import re
import glob

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')

# New footer CSS to replace the existing FOOTER section
NEW_FOOTER_CSS = """/* ============================================
           FOOTER
           ============================================ */
        .back-to-top {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #ECA400, #d4940a);
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 16px rgba(236, 164, 0, 0.35);
            opacity: 0;
            visibility: hidden;
            transform: translateY(10px);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 999;
        }

        .back-to-top.visible {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .back-to-top:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 24px rgba(236, 164, 0, 0.5);
        }

        .back-to-top svg {
            width: 20px;
            height: 20px;
            stroke: #001D4A;
            fill: none;
            stroke-width: 2.5;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .footer-cta {
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

        footer {
            padding: 0;
            position: relative;
            overflow: hidden;
            color: rgba(255, 255, 255, 0.75);
        }

        .footer-bg {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('../assets/images/Luxury apt images/pexels-kseniachernaya-5691495.jpg');
            background-size: cover;
            background-position: center;
            filter: brightness(0.15) saturate(0.6);
        }

        .footer-bg::after {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(180deg, #001D4A 0%, rgba(0, 29, 74, 0.85) 30%, rgba(0, 29, 74, 0.75) 100%);
        }

        .footer-top {
            display: grid;
            grid-template-columns: 1.2fr 1fr 1fr;
            gap: 2.5rem;
            max-width: 1140px;
            margin: 0 auto 1.5rem;
            padding: 3rem clamp(1.5rem, 5vw, 4rem) 1.5rem;
            position: relative;
            z-index: 1;
        }

        .footer-brand .footer-logo {
            display: flex;
            align-items: center;
            margin-bottom: 0.8rem;
        }

        .footer-brand .footer-logo img {
            width: 160px;
            height: auto;
            filter: brightness(0) invert(1);
        }

        .footer-brand p {
            font-size: 0.85rem;
            line-height: 1.7;
            margin-bottom: 1rem;
            color: rgba(255, 255, 255, 0.6);
        }

        .contact-line {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.75);
            transition: color 0.3s;
        }

        .contact-line:hover { color: #ECA400; }

        .contact-line svg {
            width: 15px;
            height: 15px;
            stroke: #ECA400;
            fill: none;
            stroke-width: 1.5;
            flex-shrink: 0;
        }

        .footer-col h4 {
            font-family: var(--font-display, 'Playfair Display', serif);
            font-size: 1rem;
            color: #ffffff;
            margin-bottom: 0.8rem;
            padding-bottom: 0.5rem;
            position: relative;
        }

        .footer-col h4::after {
            content: '';
            position: absolute;
            bottom: 0; left: 0;
            width: 24px;
            height: 2px;
            background: #ECA400;
        }

        .footer-links-list {
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }

        .footer-links-list a {
            font-size: 0.82rem;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.6);
            transition: all 0.3s;
            letter-spacing: 0.02em;
        }

        .footer-links-list a:hover {
            color: #ECA400;
            padding-left: 4px;
        }

        .footer-bottom {
            text-align: center;
            padding: 1rem clamp(1.5rem, 5vw, 4rem);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            max-width: 1140px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }

        .footer-bottom p {
            font-size: 0.72rem;
            color: rgba(255, 255, 255, 0.35);
        }"""


# New footer HTML
NEW_FOOTER_HTML = """    <!-- Back to Top Button -->
    <button class="back-to-top" id="backToTop" aria-label="Back to top">
        <svg viewBox="0 0 24 24"><polyline points="18 15 12 9 6 15"/></svg>
    </button>

    <!-- ==========================================
         FOOTER
         ========================================== -->
    <footer role="contentinfo" aria-label="Blue Brick contact information and service areas">
        <div class="footer-bg"></div>

        <div class="footer-cta">
            <div class="footer-cta-inner">
                <h3>Ready for a Spotless Space?</h3>
                <p>Get a free estimate for your home or office — no commitment, fast response.</p>
                <a href="/tools/quote-calculator.html" class="footer-cta-btn" target="_blank">Get Your Free Estimate <span>&rarr;</span></a>
            </div>
        </div>

        <div class="footer-top">
            <div class="footer-brand">
                <div class="footer-logo">
                    <img src="../assets/images/IMG_9670.png" alt="Blue Brick — Luxury & Commercial Cleaning">
                </div>
                <p>Boston's trusted deep cleaning and luxury property care.</p>
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
                <h4>Service Areas</h4>
                <nav class="footer-links-list" aria-label="Service areas">
                    <a href="/blog/deep-cleaning-boston.html">Boston</a>
                    <a href="/blog/deep-cleaning-cambridge.html">Cambridge</a>
                    <a href="/blog/deep-cleaning-newton.html">Newton</a>
                    <a href="/blog/deep-cleaning-waltham.html">Waltham</a>
                    <a href="/blog/deep-cleaning-brookline.html">Brookline</a>
                    <a href="/blog/deep-cleaning-somerville.html">Somerville</a>
                    <a href="/blog/deep-cleaning-brighton.html">Brighton</a>
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
        </div>

        <div class="footer-bottom">
            <p>&copy; 2026 Blue Brick Luxury and Commercial Cleaning. All rights reserved.</p>
        </div>
    </footer>"""

# Back-to-top JS to inject
BACK_TO_TOP_JS = """
        // -- Back to Top button --
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 600) {
                    backToTop.classList.add('visible');
                } else {
                    backToTop.classList.remove('visible');
                }
            });
            backToTop.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }"""


def replace_footer_css(content):
    """Replace the FOOTER CSS section."""
    # Match from FOOTER comment to the RESPONSIVE comment
    pattern = (
        r'/\*\s*={10,}\s*\n\s*FOOTER\s*\n\s*={10,}\s*\*/'
        r'.*?'
        r'(?=/\*\s*={10,}\s*\n\s*RESPONSIVE)'
    )
    new_content = re.sub(pattern, NEW_FOOTER_CSS + '\n\n        ', content, flags=re.DOTALL)
    return new_content


def replace_footer_html(content):
    """Replace the footer HTML section."""
    # Match from the FOOTER HTML comment or <footer> tag to </footer>
    pattern = (
        r'(?:<!-- ={10,}\s*\n\s*FOOTER\s*\n\s*={10,} -->)?\s*'
        r'<footer[^>]*>.*?</footer>'
    )
    new_content = re.sub(pattern, NEW_FOOTER_HTML, content, flags=re.DOTALL)
    return new_content


def add_back_to_top_js(content):
    """Add back-to-top JS before the closing </script> of the main script block."""
    if 'backToTop' in content:
        return content

    # Insert before the closing </script> of the first script block
    # Find the smooth scroll section and insert after it
    marker = "if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });"
    idx = content.find(marker)
    if idx != -1:
        # Find the next closing of the event listener block after marker
        end_block = content.find('});', idx)
        if end_block != -1:
            end_block = content.find('\n', end_block)
            if end_block != -1:
                content = content[:end_block] + BACK_TO_TOP_JS + content[end_block:]
    return content


def update_responsive_footer(content):
    """Update responsive CSS for footer to work with new structure."""
    # Replace old footer responsive rules
    old_responsive_1 = """.footer-top { grid-template-columns: 1fr 1fr; }
            .footer-brand { grid-column: span 2; }"""
    new_responsive_1 = """.footer-top { grid-template-columns: 1fr 1fr; }
            .footer-brand { grid-column: span 2; }
            .footer-cta h3 { font-size: 1.3rem; }"""
    content = content.replace(old_responsive_1, new_responsive_1)

    old_responsive_2 = """footer { padding: 2rem 1.5rem 1rem; }
            .footer-top { grid-template-columns: 1fr 1fr; gap: 1.5rem 1rem; text-align: center; }
            .footer-brand { grid-column: span 2; text-align: center; }
            .footer-brand p { margin-bottom: 0.5rem; font-size: 0.9rem; }
            .footer-col h4 { margin-bottom: 0.5rem; padding-bottom: 0.3rem; }
            .footer-col h4::after { left: 50%; transform: translateX(-50%); }
            .footer-links-list { align-items: center; gap: 0.25rem; }
            .footer-links-list a { font-size: 0.85rem; }
            .contact-line { justify-content: center; margin-bottom: 0.3rem; font-size: 0.9rem; }"""
    new_responsive_2 = """footer { padding: 0; }
            .footer-top { grid-template-columns: 1fr 1fr; gap: 1.5rem 1rem; text-align: center; padding: 2rem 1.5rem 1rem; }
            .footer-brand { grid-column: span 2; text-align: center; }
            .footer-brand p { margin-bottom: 0.5rem; font-size: 0.9rem; }
            .footer-col h4 { margin-bottom: 0.5rem; padding-bottom: 0.3rem; }
            .footer-col h4::after { left: 50%; transform: translateX(-50%); }
            .footer-links-list { align-items: center; gap: 0.3rem; }
            .footer-links-list a { font-size: 0.85rem; }
            .contact-line { justify-content: center; margin-bottom: 0.3rem; font-size: 0.9rem; }
            .footer-cta { padding: 2rem 1.5rem; }
            .footer-cta h3 { font-size: 1.2rem; }
            .back-to-top { bottom: 1.5rem; right: 1.5rem; width: 40px; height: 40px; }"""
    content = content.replace(old_responsive_2, new_responsive_2)

    return content


def remove_old_footer_animations(content):
    """Remove the old footerGradient and floatDot keyframe animations if they exist."""
    # Remove @keyframes footerGradient
    content = re.sub(
        r'@keyframes\s+footerGradient\s*\{[^}]*\{[^}]*\}[^}]*\{[^}]*\}\s*\}\s*',
        '', content, flags=re.DOTALL
    )
    # simpler pattern
    content = re.sub(
        r'@keyframes\s+footerGradient\s*\{.*?\}\s*\}\s*',
        '', content, flags=re.DOTALL
    )
    content = re.sub(
        r'@keyframes\s+floatDot\s*\{.*?\}\s*\}\s*',
        '', content, flags=re.DOTALL
    )
    return content


def main():
    blog_dir = os.path.abspath(BLOG_DIR)
    files = sorted(glob.glob(os.path.join(blog_dir, '*.html')))

    updated = 0
    for f in files:
        basename = os.path.basename(f)
        if basename == 'index.html':
            continue

        with open(f, 'r') as fh:
            content = fh.read()

        original = content

        content = remove_old_footer_animations(content)
        content = replace_footer_css(content)
        content = replace_footer_html(content)
        content = update_responsive_footer(content)
        content = add_back_to_top_js(content)

        if content != original:
            with open(f, 'w') as fh:
                fh.write(content)
            print(f'  OK: {basename}')
            updated += 1
        else:
            print(f'  SKIP: {basename}')

    print(f'\nUpdated {updated} files')


if __name__ == '__main__':
    main()
