#!/usr/bin/env python3
"""
Add a floating side CTA for the quote calculator that stays visible while scrolling.
Repositions back-to-top button below it.
"""

import os
import re
import glob

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')

# CSS for the floating side CTA
FLOATING_CTA_CSS = """
        /* ============================================
           FLOATING SIDE CTA
           ============================================ */
        .floating-cta {
            position: fixed;
            right: 0;
            top: 50%;
            transform: translateY(-50%) translateX(100%);
            z-index: 998;
            opacity: 0;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .floating-cta.visible {
            transform: translateY(-50%) translateX(0);
            opacity: 1;
        }

        .floating-cta-link {
            display: flex;
            align-items: center;
            gap: 0;
            text-decoration: none !important;
            background: linear-gradient(135deg, #ECA400, #d4940a);
            color: #001D4A !important;
            font-weight: 700;
            font-size: 0.78rem;
            letter-spacing: 0.03em;
            border-radius: 12px 0 0 12px;
            box-shadow: -4px 4px 20px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(236, 164, 0, 0.15);
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .floating-cta-link:hover {
            box-shadow: -6px 6px 30px rgba(0, 0, 0, 0.3), 0 0 20px rgba(236, 164, 0, 0.2);
            transform: translateX(-4px);
        }

        .floating-cta-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 48px;
            height: 48px;
            background: rgba(0, 29, 74, 0.12);
            flex-shrink: 0;
        }

        .floating-cta-icon svg {
            width: 22px;
            height: 22px;
            fill: #001D4A;
        }

        .floating-cta-text {
            padding: 0 1rem 0 0.75rem;
            white-space: nowrap;
            line-height: 1.2;
        }

        .floating-cta-text span {
            display: block;
            font-size: 0.65rem;
            font-weight: 500;
            opacity: 0.7;
            margin-top: 1px;
        }

        @media (max-width: 768px) {
            .floating-cta {
                top: auto;
                bottom: 0;
                left: 0;
                right: 0;
                transform: translateY(100%);
            }

            .floating-cta.visible {
                transform: translateY(0);
            }

            .floating-cta-link {
                border-radius: 0;
                width: 100%;
                justify-content: center;
                padding: 0.15rem 0;
            }

            .floating-cta-icon {
                width: 40px;
                height: 40px;
                background: none;
            }

            .floating-cta-text {
                padding: 0 1rem 0 0;
            }

            .back-to-top {
                bottom: 4.5rem !important;
            }
        }"""

# HTML for the floating CTA
FLOATING_CTA_HTML = """    <!-- Floating Side CTA -->
    <div class="floating-cta" id="floatingCta">
        <a href="/tools/quote-calculator.html" class="floating-cta-link" target="_blank">
            <div class="floating-cta-icon">
                <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-4 8h-2v2c0 .55-.45 1-1 1s-1-.45-1-1v-2H9c-.55 0-1-.45-1-1s.45-1 1-1h2V7c0-.55.45-1 1-1s1 .45 1 1v2h2c.55 0 1 .45 1 1s-.45 1-1 1z"/></svg>
            </div>
            <div class="floating-cta-text">
                Free Estimate
                <span>Instant pricing &rarr;</span>
            </div>
        </a>
    </div>

"""

# JS for the floating CTA visibility
FLOATING_CTA_JS = """
        // -- Floating side CTA --
        const floatingCta = document.getElementById('floatingCta');
        if (floatingCta) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 400) {
                    floatingCta.classList.add('visible');
                } else {
                    floatingCta.classList.remove('visible');
                }
            });
        }"""


def add_floating_css(content):
    """Insert floating CTA CSS before the FOOTER section."""
    if 'FLOATING SIDE CTA' in content:
        return content

    marker = '/* ============================================\n           FOOTER'
    idx = content.find(marker)
    if idx != -1:
        content = content[:idx] + FLOATING_CTA_CSS + '\n\n        ' + content[idx:]
    return content


def add_floating_html(content):
    """Insert floating CTA HTML before the back-to-top button."""
    if 'floatingCta' in content:
        return content

    marker = '    <!-- Back to Top Button -->'
    idx = content.find(marker)
    if idx != -1:
        content = content[:idx] + FLOATING_CTA_HTML + content[idx:]
    return content


def add_floating_js(content):
    """Insert floating CTA JS after back-to-top JS."""
    if 'Floating side CTA' in content:
        return content

    marker = "// -- Back to Top button --"
    idx = content.find(marker)
    if idx != -1:
        # Find the end of the backToTop block (closing }  of the if block)
        # Look for the pattern: });  }  at the end of the backToTop section
        block_end = content.find('});', idx)  # end of addEventListener scroll
        if block_end != -1:
            block_end = content.find('});', block_end + 3)  # end of addEventListener click
            if block_end != -1:
                close_brace = content.find('}', block_end + 3)  # closing if(backToTop)
                if close_brace != -1:
                    insert_pos = close_brace + 1
                    content = content[:insert_pos] + FLOATING_CTA_JS + content[insert_pos:]
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

        content = add_floating_css(content)
        content = add_floating_html(content)
        content = add_floating_js(content)

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
