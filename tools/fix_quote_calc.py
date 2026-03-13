#!/usr/bin/env python3
"""
Replace quote calculator embed CSS across all blog posts with premium redesign.
"""

import os
import re
import glob

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')

# Premium redesigned CSS
NEW_CSS = """/* ============================================
           QUOTE CALCULATOR EMBED
           ============================================ */
        .quote-calc-embed {
            background: linear-gradient(135deg, #001D4A 0%, #002a5c 50%, #001840 100%);
            border: 1px solid rgba(236, 164, 0, 0.2);
            border-radius: 14px;
            padding: 1.1rem 1.5rem;
            margin: 2.5rem 0;
            color: #ffffff !important;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.25rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(0, 29, 74, 0.25), 0 0 0 1px rgba(236, 164, 0, 0.08);
        }

        .quote-calc-embed::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #ECA400, #f4be3a, #ECA400);
        }

        .quote-calc-embed::after {
            content: '';
            position: absolute;
            top: -40%;
            right: -5%;
            width: 180px;
            height: 180px;
            background: radial-gradient(circle, rgba(236, 164, 0, 0.06) 0%, transparent 70%);
            pointer-events: none;
        }

        .quote-calc-header {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            flex: 1;
            min-width: 0;
        }

        .quote-calc-header span {
            font-size: 1.75rem;
            line-height: 1;
            flex-shrink: 0;
            filter: drop-shadow(0 2px 4px rgba(236, 164, 0, 0.3));
        }

        .quote-calc-header strong {
            display: block;
            font-size: 1.05rem;
            color: #ffffff !important;
            font-weight: 700;
            letter-spacing: -0.01em;
            line-height: 1.3;
        }

        .quote-calc-header p {
            margin: 0.15rem 0 0 !important;
            font-size: 0.82rem;
            color: rgba(255, 255, 255, 0.75) !important;
            line-height: 1.35;
            letter-spacing: 0.01em;
        }

        .quote-calc-btn {
            background: linear-gradient(135deg, #ECA400, #d4940a);
            color: #001D4A !important;
            font-weight: 700;
            padding: 0.6rem 1.3rem;
            border-radius: 8px;
            font-size: 0.85rem;
            text-decoration: none !important;
            white-space: nowrap;
            flex-shrink: 0;
            letter-spacing: 0.01em;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 8px rgba(236, 164, 0, 0.3);
            position: relative;
            z-index: 1;
        }

        .quote-calc-btn:hover {
            background: linear-gradient(135deg, #f4be3a, #ECA400);
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(236, 164, 0, 0.4);
            color: #001D4A !important;
        }

        @media (max-width: 520px) {
            .quote-calc-embed {
                flex-direction: column;
                text-align: center;
                padding: 1.2rem;
                gap: 1rem;
            }
            .quote-calc-header {
                flex-direction: column;
                gap: 0.5rem;
            }
            .quote-calc-btn {
                width: 100%;
                text-align: center;
                padding: 0.7rem 1.2rem;
            }
        }

"""


def replace_quote_calc_css(content):
    """Replace the entire quote calculator CSS block."""
    # Match from the QUOTE CALCULATOR EMBED comment through the mobile media query
    # until the next section comment or closing style tag
    pattern = (
        r'/\*\s*={10,}\s*\n\s*QUOTE CALCULATOR EMBED\s*\n\s*={10,}\s*\*/'
        r'.*?'
        r'@media\s*\(max-width:\s*\d+px\)\s*\{'
        r'[^}]*\.quote-calc-embed\s*\{[^}]*\}'
        r'[^}]*\.quote-calc-header\s*\{[^}]*\}'
        r'[^}]*\.quote-calc-btn\s*\{[^}]*\}'
        r'\s*\}'
        r'\s*'
    )

    new_content = re.sub(pattern, NEW_CSS, content, flags=re.DOTALL)

    if new_content == content:
        # Fallback: try simpler pattern
        pattern2 = (
            r'/\*\s*={10,}\s*\n\s*QUOTE CALCULATOR EMBED\s*\n\s*={10,}\s*\*/'
            r'.*?'
            r'(?=/\*\s*={10,}\s*\n\s*(?:HEADER|INLINE|VISUAL|FAQ))'
        )
        new_content = re.sub(pattern2, NEW_CSS, content, flags=re.DOTALL)

    return new_content


def main():
    blog_dir = os.path.abspath(BLOG_DIR)
    files = sorted(glob.glob(os.path.join(blog_dir, '*.html')))

    updated = 0
    skipped = 0
    for f in files:
        basename = os.path.basename(f)
        if basename == 'index.html':
            continue

        with open(f, 'r') as fh:
            content = fh.read()

        if 'QUOTE CALCULATOR EMBED' not in content:
            print(f'  NO CALC: {basename}')
            skipped += 1
            continue

        original = content
        content = replace_quote_calc_css(content)

        if content != original:
            with open(f, 'w') as fh:
                fh.write(content)
            print(f'  OK: {basename}')
            updated += 1
        else:
            print(f'  SKIP (no change): {basename}')
            skipped += 1

    print(f'\nUpdated {updated} files, skipped {skipped}')


if __name__ == '__main__':
    main()
