#!/usr/bin/env python3
"""
Fix blog posts:
1. Replace broken FAQ CSS with complete working accordion styles
2. Fix triple-emoji on FAQ headings
3. Bigger article h2 titles
4. Visual polish: section dividers, better spacing
"""

import os
import re
import glob

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')

# Complete FAQ accordion CSS
FAQ_CSS = """        /* ============================================
           FAQ ACCORDION
           ============================================ */
        .faq-section {
            margin: 2.5rem 0 1.5rem;
        }

        .faq-item {
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            overflow: hidden;
            transition: border-color 0.3s;
        }

        .faq-item:hover {
            border-color: var(--amber, #ECA400);
        }

        .faq-question {
            font-family: var(--font-body, 'Manrope', sans-serif);
            font-size: 1rem;
            font-weight: 600;
            color: var(--prussian, #001D4A);
            padding: 1.2rem 3rem 1.2rem 1.2rem;
            margin: 0;
            cursor: pointer;
            position: relative;
            user-select: none;
            background: #f9fafb;
            transition: background 0.3s;
        }

        .faq-question:hover {
            background: rgba(236, 164, 0, 0.06);
        }

        .faq-question::after {
            content: '+';
            position: absolute;
            right: 1.2rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.4rem;
            font-weight: 300;
            color: var(--amber, #ECA400);
            transition: transform 0.3s;
        }

        .faq-item.open .faq-question::after {
            content: '\\2212';
        }

        .faq-answer {
            font-size: 1rem;
            color: var(--dark-gray, #374151);
            line-height: 1.8;
            padding: 0 1.2rem;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s ease, padding 0.3s ease;
        }

        .faq-item.open .faq-answer {
            max-height: 600px;
            padding: 0 1.2rem 1.2rem;
        }"""

# Visual polish CSS to add
VISUAL_POLISH_CSS = """
        /* ============================================
           VISUAL POLISH
           ============================================ */
        .article-container h2,
        .article-wrapper h2,
        .article-section h2,
        .article-content h2,
        .post-content h2 {
            font-size: 1.65rem !important;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            line-height: 1.3;
        }

        .article-container h3,
        .article-wrapper h3,
        .article-section h3,
        .article-content h3,
        .post-content h3 {
            font-size: 1.2rem !important;
            margin-top: 1.8rem;
            margin-bottom: 0.8rem;
        }

        .article-container .reveal + .reveal,
        .article-wrapper .reveal + .reveal,
        .article-section .reveal + .reveal {
            border-top: 1px solid rgba(0, 29, 74, 0.06);
            padding-top: 2rem;
        }

        .highlight-box {
            border-left: 4px solid var(--amber, #ECA400) !important;
            background: linear-gradient(135deg, rgba(236, 164, 0, 0.04), rgba(0, 105, 146, 0.03)) !important;
            border-radius: 0 12px 12px 0 !important;
            padding: 1.5rem !important;
        }"""


def fix_faq_css(content):
    """Replace broken FAQ CSS with complete working version."""
    # Remove any existing FAQ ACCORDION section (potentially broken)
    pattern = r'/\*\s*={10,}\s*\n\s*FAQ ACCORDION\s*\n\s*={10,}\s*\*/.*?(?=/\*\s*={10,})'
    content = re.sub(pattern, '', content, flags=re.DOTALL)

    # Also remove any leftover FAQ SECTION block
    pattern2 = r'/\*\s*={10,}\s*\n\s*FAQ SECTION\s*\n\s*={10,}\s*\*/.*?(?=/\*\s*={10,})'
    content = re.sub(pattern2, '', content, flags=re.DOTALL)

    # Remove orphaned faq rules that might be floating
    content = re.sub(r'\n\s*\.faq-item\.open\s*\n\s*\n', '\n', content)
    content = re.sub(r'\n\s*\.faq-item:hover\s*\{[^}]*\}\s*\n', '\n', content)
    content = re.sub(r'\n\s*\.faq-question:hover\s*\{[^}]*\}\s*\n', '\n', content)
    content = re.sub(r'\n\s*\.faq-question::after\s*\{[^}]*\}\s*\n', '\n', content)
    content = re.sub(r'\n\s*\.faq-item\.open\s+\.faq-question::after\s*\{[^}]*\}\s*\n', '\n', content)
    content = re.sub(r'\n\s*\.faq-item\.open\s+\.faq-answer\s*\{[^}]*\}\s*\n', '\n', content)
    content = re.sub(r'\n\s*\.faq-section\s*\{[^}]*\}\s*\n', '\n', content)
    content = re.sub(r'\n\s*\.faq-item\s*\{[^}]*\}\s*\n', '\n', content)
    content = re.sub(r'\n\s*\.faq-item:first-child\s*\{[^}]*\}\s*\n', '\n', content)
    content = re.sub(r'\n\s*\.faq-question\s*\{[^}]*\}\s*\n', '\n', content)
    content = re.sub(r'\n\s*\.faq-answer\s*\{[^}]*\}\s*\n', '\n', content)

    # Only add FAQ CSS if post has FAQ content
    if 'faq-section' in content or 'faq-item' in content:
        # Insert before QUOTE CALCULATOR or HEADER CSS
        for marker in ['QUOTE CALCULATOR EMBED', 'INLINE CTA BANNERS', 'HEADER']:
            idx = content.find(f'/* ============================================\n           {marker}')
            if idx == -1:
                idx = content.find(f'/*\n           {marker}')
            if idx != -1:
                content = content[:idx] + FAQ_CSS + '\n\n' + content[idx:]
                break

    return content


def add_visual_polish(content):
    """Add visual polish CSS."""
    if 'VISUAL POLISH' in content:
        return content

    # Insert before closing </style>
    idx = content.rfind('</style>')
    if idx != -1:
        content = content[:idx] + VISUAL_POLISH_CSS + '\n\n' + content[idx:]

    return content


def fix_triple_emoji(content):
    """Fix triple emoji on FAQ heading (❓ ❓ ❓ → ❓)."""
    content = content.replace('❓ ❓ ❓ Frequently', '❓ Frequently')
    content = content.replace('❓ ❓ Frequently', '❓ Frequently')
    # Fix any other doubled emojis
    content = re.sub(r'([\U0001F000-\U0001FFFF]) \1 \1 ', r'\1 ', content)
    content = re.sub(r'([\U0001F000-\U0001FFFF]) \1 ', r'\1 ', content)
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

        content = fix_faq_css(content)
        content = fix_triple_emoji(content)
        content = add_visual_polish(content)

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
