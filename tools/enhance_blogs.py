#!/usr/bin/env python3
"""
Batch enhance all Blue Brick blog posts:
1. Add emojis/icons to h2 and h3 headings
2. Add inline CTA banners (text/call) throughout articles
3. Convert FAQ sections to accordion dropdowns
4. Add quote calculator embed before CTA section
5. Update blog index cards to use real images instead of text placeholders
"""

import os
import re
import html

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blog')

# ─── Emoji mappings for headings ───
HEADING_EMOJIS = {
    # Keywords → emoji prefix
    'kitchen': '🍳 ',
    'bathroom': '🚿 ',
    'bedroom': '🛏️ ',
    'living': '🛋️ ',
    'detail': '🔍 ',
    'neighborhood': '📍 ',
    'serve': '📍 ',
    'why': '💡 ',
    'what': '📋 ',
    'how': '🤔 ',
    'cost': '💰 ',
    'price': '💰 ',
    'spring': '🌸 ',
    'winter': '❄️ ',
    'climate': '🌡️ ',
    'season': '📅 ',
    'apartment': '🏢 ',
    'renter': '🏢 ',
    'landlord': '🏠 ',
    'property manager': '🏘️ ',
    'move-in': '📦 ',
    'move-out': '📦 ',
    'move out': '📦 ',
    'move in': '📦 ',
    'checklist': '✅ ',
    'construction': '🏗️ ',
    'renovation': '🔨 ',
    'post-construction': '🏗️ ',
    'restaurant': '🍽️ ',
    'commercial': '🏢 ',
    'office': '💼 ',
    'health': '🏥 ',
    'inspection': '📋 ',
    'fire': '🔥 ',
    'safety': '🛡️ ',
    'schedule': '📅 ',
    'book': '📞 ',
    'contact': '📞 ',
    'frequently': '❓ ',
    'faq': '❓ ',
    'cleaning include': '✨ ',
    'deep cleaning': '✨ ',
    'professional': '⭐ ',
    'maintain': '🔄 ',
    'benefit': '🌟 ',
    'choose': '🏆 ',
    'approach': '🎯 ',
    'process': '⚙️ ',
    'daycare': '👶 ',
    'child': '👶 ',
    'airbnb': '🏡 ',
    'turnover': '🔄 ',
    'dust': '💨 ',
    'mold': '🦠 ',
    'allergen': '🤧 ',
    'floor': '🪣 ',
    'window': '🪟 ',
    'carpet': '🧹 ',
    'grout': '🧽 ',
    'appliance': '🔌 ',
    'equipment': '⚙️ ',
    'hood': '🔥 ',
    'exhaust': '💨 ',
    'cold storage': '🧊 ',
    'restroom': '🚻 ',
    'front of house': '🪑 ',
    'greater boston': '🗺️ ',
    'boston': '🏙️ ',
    'flexible': '⏰ ',
    'get': '🚀 ',
    'ready': '🚀 ',
    'start': '🚀 ',
    'trust': '🤝 ',
    'guarantee': '✅ ',
}

# H3-specific emojis (more specific, smaller scope)
H3_EMOJIS = {
    'kitchen': '🍳 ',
    'bathroom': '🚿 ',
    'bedroom': '🛏️ ',
    'living': '🛋️ ',
    'detail': '🔍 ',
    'floor': '🪣 ',
    'wall': '🧱 ',
    'ceiling': '💡 ',
    'window': '🪟 ',
    'carpet': '🧹 ',
    'tile': '🧽 ',
    'hood': '🔥 ',
    'exhaust': '💨 ',
    'cold storage': '🧊 ',
    'cooking': '🍳 ',
    'restroom': '🚻 ',
    'front of house': '🪑 ',
    'technology': '💻 ',
    'medical': '🏥 ',
    'law': '⚖️ ',
    'financial': '💰 ',
    'startup': '🚀 ',
    'coworking': '👥 ',
}


def get_emoji_for_heading(text, is_h3=False):
    """Find the best emoji for a heading based on keywords."""
    text_lower = text.lower()
    mapping = H3_EMOJIS if is_h3 else HEADING_EMOJIS

    # Already has emoji? skip
    if any(ord(c) > 0x1F000 for c in text[:3]):
        return text

    for keyword, emoji in mapping.items():
        if keyword in text_lower:
            return emoji + text

    # Fallback: no emoji if no match
    if not is_h3:
        return '✨ ' + text  # All h2s get at least a sparkle
    return text


def add_emojis_to_headings(content):
    """Add emojis to h2 and h3 headings in article content."""
    # Only process headings inside article body (after article tag)
    article_match = re.search(r'<article\b[^>]*>', content)
    if not article_match:
        return content

    article_start = article_match.start()
    article_end_match = re.search(r'</article>', content[article_start:])
    if not article_end_match:
        return content
    article_end = article_start + article_end_match.end()

    before = content[:article_start]
    article = content[article_start:article_end]
    after = content[article_end:]

    # Process h2 tags (not in CTA section)
    def replace_h2(match):
        full = match.group(0)
        attrs = match.group(1) or ''
        inner = match.group(2)
        # Skip if it contains <em> tags (CTA headings)
        if '<em>' in inner and ('Get' in inner or 'Ready' in inner or 'Book' in inner):
            return full
        # Strip any existing em tags for matching, then re-add
        clean = re.sub(r'</?em>', '', inner)
        emoji_text = get_emoji_for_heading(clean, is_h3=False)
        if emoji_text != clean:
            # Put emoji before content, preserving em tags
            emoji = emoji_text[:len(emoji_text) - len(clean)]
            return f'<h2{attrs}>{emoji}{inner}</h2>'
        return full

    article = re.sub(r'<h2([^>]*)>(.*?)</h2>', replace_h2, article, flags=re.DOTALL)

    # Process h3 tags
    def replace_h3(match):
        attrs = match.group(1) or ''
        inner = match.group(2)
        clean = re.sub(r'</?em>', '', inner)
        emoji_text = get_emoji_for_heading(clean, is_h3=True)
        if emoji_text != clean:
            emoji = emoji_text[:len(emoji_text) - len(clean)]
            return f'<h3{attrs}>{emoji}{inner}</h3>'
        return match.group(0)

    article = re.sub(r'<h3([^>]*)>(.*?)</h3>', replace_h3, article, flags=re.DOTALL)

    return before + article + after


# ─── Inline CTA banner ───
INLINE_CTA_HTML = '''
                <div class="inline-cta reveal">
                    <p>📞 <strong>Get your free estimate today!</strong> Text or call <a href="tel:+17813305604">781-330-5604</a> · <a href="mailto:bluebrickmass@gmail.com">bluebrickmass@gmail.com</a></p>
                </div>
'''

INLINE_CTA_CSS = """
        /* ============================================
           INLINE CTA BANNERS
           ============================================ */
        .inline-cta {
            background: linear-gradient(135deg, rgba(0, 29, 74, 0.04), rgba(0, 105, 146, 0.06));
            border-left: 4px solid var(--amber);
            border-radius: 0 12px 12px 0;
            padding: 1.2rem 1.5rem;
            margin: 2rem 0;
        }

        .inline-cta p {
            margin: 0;
            font-size: 1rem;
            font-weight: 500;
            color: var(--prussian);
        }

        .inline-cta a {
            color: var(--cerulean);
            font-weight: 700;
            text-decoration: underline;
            text-decoration-color: var(--amber);
            text-underline-offset: 3px;
        }

        .inline-cta a:hover {
            color: var(--amber);
        }
"""

# ─── Quote Calculator Embed ───
QUOTE_CALC_HTML = '''
                <div class="quote-calc-embed reveal">
                    <div class="quote-calc-header">
                        <span>💰</span>
                        <div>
                            <strong>Get an Instant Estimate</strong>
                            <p>See pricing for your home or office in seconds</p>
                        </div>
                    </div>
                    <a href="/tools/quote-calculator.html" class="quote-calc-btn" target="_blank">Open Quote Calculator →</a>
                </div>
'''

QUOTE_CALC_CSS = """
        /* ============================================
           QUOTE CALCULATOR EMBED
           ============================================ */
        .quote-calc-embed {
            background: linear-gradient(135deg, #001D4A, #0a2a5c);
            border-radius: 16px;
            padding: 2rem;
            margin: 2.5rem 0;
            color: #ffffff !important;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.5rem;
            flex-wrap: wrap;
        }

        .quote-calc-header {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .quote-calc-header span {
            font-size: 2.5rem;
            line-height: 1;
        }

        .quote-calc-header strong {
            display: block;
            font-size: 1.15rem;
            color: #ffffff !important;
            font-weight: 700;
        }

        .quote-calc-header p {
            margin: 0.2rem 0 0 !important;
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.7) !important;
            line-height: 1.4;
        }

        .quote-calc-btn {
            background: #ECA400;
            color: #001D4A !important;
            font-weight: 700;
            padding: 0.8rem 1.8rem;
            border-radius: 10px;
            font-size: 0.95rem;
            text-decoration: none !important;
            white-space: nowrap;
            transition: background 0.3s, transform 0.2s;
        }

        .quote-calc-btn:hover {
            background: #f4be3a;
            transform: translateY(-2px);
            color: #001D4A !important;
        }

        @media (max-width: 600px) {
            .quote-calc-embed {
                flex-direction: column;
                text-align: center;
            }
            .quote-calc-header {
                flex-direction: column;
            }
            .quote-calc-btn {
                width: 100%;
                text-align: center;
            }
        }
"""

# ─── FAQ Accordion CSS + JS ───
FAQ_ACCORDION_CSS = """
        /* ============================================
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
            border-color: var(--amber);
        }

        .faq-question {
            font-family: var(--font-body);
            font-size: 1rem;
            font-weight: 600;
            color: var(--prussian);
            padding: 1.2rem 3rem 1.2rem 1.2rem;
            margin: 0;
            cursor: pointer;
            position: relative;
            user-select: none;
            background: var(--off-white, #f9fafb);
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
            color: var(--amber);
            transition: transform 0.3s;
        }

        .faq-item.open .faq-question::after {
            content: '−';
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
            max-height: 500px;
            padding: 0 1.2rem 1.2rem;
        }
"""

FAQ_ACCORDION_JS = """
    <script>
    document.querySelectorAll('.faq-question').forEach(function(q) {
        q.addEventListener('click', function() {
            var item = this.closest('.faq-item');
            var wasOpen = item.classList.contains('open');
            // Close all
            document.querySelectorAll('.faq-item.open').forEach(function(el) {
                el.classList.remove('open');
            });
            // Toggle current
            if (!wasOpen) item.classList.add('open');
        });
    });
    </script>
"""


def inject_css(content, css_block, marker):
    """Inject a CSS block before the HEADER comment or </style> if not already present."""
    if marker in content:
        return content

    insert_point = content.find('/* ============================================\n           HEADER')
    if insert_point == -1:
        insert_point = content.find('/* ============================================\r\n           HEADER')
    if insert_point == -1:
        # Try before </style>
        insert_point = content.rfind('</style>')
    if insert_point == -1:
        return content

    return content[:insert_point] + css_block + '\n' + content[insert_point:]


def replace_faq_css(content):
    """Replace old FAQ CSS with accordion version."""
    # Find and replace the old FAQ section CSS
    old_faq_pattern = re.compile(
        r'/\*\s*={10,}\s*\n\s*FAQ SECTION\s*\n\s*={10,}\s*\*/.*?(?=/\*\s*={10,})',
        re.DOTALL
    )
    match = old_faq_pattern.search(content)
    if match:
        content = content[:match.start()] + content[match.end():]

    # Also remove individual old faq rules that might remain
    for old_rule in [
        r'\.faq-section\s*\{[^}]*\}',
        r'\.faq-item\s*\{[^}]*\}',
        r'\.faq-item:first-child\s*\{[^}]*\}',
        r'\.faq-question\s*\{[^}]*\}',
        r'\.faq-answer\s*\{[^}]*\}',
    ]:
        content = re.sub(old_rule, '', content)

    return content


def convert_faq_to_accordion(content):
    """Convert static FAQ items to accordion pattern and change p→div for question."""
    # Change faq-question from p to div (for semantic click targets)
    content = content.replace('<p class="faq-question">', '<div class="faq-question">')
    content = re.sub(
        r'</p>\s*\n(\s*)<p class="faq-answer">',
        r'</div>\n\1<div class="faq-answer"><p>',
        content
    )
    # Close the answer div properly
    content = re.sub(
        r'(class="faq-answer"><p>.*?)</p>\s*\n(\s*)</div>',
        r'\1</p></div>\n\2</div>',
        content,
        flags=re.DOTALL
    )

    return content


def add_inline_ctas(content):
    """Add 1-2 inline CTA banners throughout the article body."""
    if 'Get your free estimate today' in content:
        return content

    # Find all h2 positions in the article body (these mark sections)
    article_match = re.search(r'<article\b[^>]*>', content)
    if not article_match:
        return content

    article_start = article_match.end()
    article_end = content.find('</article>', article_start)
    if article_end == -1:
        return content

    # Find h2 tags as section markers
    h2_positions = [m.start() + article_start for m in re.finditer(r'<h2', content[article_start:article_end])]

    if len(h2_positions) < 3:
        return content

    # Insert CTA before the h2 at ~1/3 and ~2/3 of the way through
    idx_1 = h2_positions[len(h2_positions) // 3]
    idx_2 = h2_positions[2 * len(h2_positions) // 3]

    # Find the nearest preceding </div> to insert after
    def find_prev_div_close(pos):
        search_area = content[:pos]
        last = search_area.rfind('</div>')
        if last != -1:
            return last + len('</div>')
        return pos

    insert_1 = find_prev_div_close(idx_1)
    insert_2 = find_prev_div_close(idx_2)

    if insert_2 - insert_1 < 500:
        insert_2 = None

    # Insert from back to front
    if insert_2:
        content = content[:insert_2] + INLINE_CTA_HTML + content[insert_2:]
    content = content[:insert_1] + INLINE_CTA_HTML + content[insert_1:]

    return content


def add_quote_calculator(content):
    """Add quote calculator embed before the CTA section."""
    if 'Open Quote Calculator' in content:
        return content

    # Find CTA section by looking for the section tag
    cta_pos = content.find('<section class="cta-section')
    if cta_pos == -1:
        return content

    # Go back to find the HTML comment before it
    comment_pos = content.rfind('<!--', max(0, cta_pos - 300), cta_pos)
    insert_pos = comment_pos if comment_pos != -1 else cta_pos

    calc_block = f'''
        <div style="max-width:780px;margin:0 auto;padding:0 clamp(1.5rem, 4vw, 3rem);">
{QUOTE_CALC_HTML}
        </div>

'''

    return content[:insert_pos] + calc_block + content[insert_pos:]


def add_faq_accordion_js(content):
    """Add FAQ accordion JS before </body>."""
    if "faq-question" not in content:
        return content
    if "closest('.faq-item')" in content:
        return content

    body_end = content.rfind('</body>')
    if body_end == -1:
        return content

    return content[:body_end] + FAQ_ACCORDION_JS + '\n' + content[body_end:]


def process_blog(filepath, filename):
    """Apply all enhancements to a single blog post."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if filename == 'index.html':
        return False

    original = content

    # 1. Add emoji to headings
    content = add_emojis_to_headings(content)

    # 2. Inject inline CTA CSS + add inline CTAs
    content = inject_css(content, INLINE_CTA_CSS, 'INLINE CTA BANNERS')
    content = add_inline_ctas(content)

    # 3. Replace FAQ CSS with accordion + convert HTML + add JS
    content = replace_faq_css(content)
    content = inject_css(content, FAQ_ACCORDION_CSS, 'FAQ ACCORDION')
    content = convert_faq_to_accordion(content)
    content = add_faq_accordion_js(content)

    # 4. Add quote calculator CSS + embed
    content = inject_css(content, QUOTE_CALC_CSS, 'QUOTE CALCULATOR EMBED')
    content = add_quote_calculator(content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


# ─── Blog Index: Add images to cards ───

CARD_IMAGE_MAP = {
    'WALTHAM': '../assets/images/city images/waltham office.png',
    'NEWTON': '../assets/images/city images/newton home.png',
    'CAMBRIDGE': '../assets/images/Luxury apt images/pexels-artbovich-6077368.jpg',
    'BROOKLINE': '../assets/images/Luxury apt images/pexels-artbovich-6492384.jpg',
    'SOMERVILLE': '../assets/images/Luxury apt images/pexels-artbovich-6636314.jpg',
    'BRIGHTON': '../assets/images/city images/brighton apartment.png',
    'WATERTOWN': '../assets/images/Luxury apt images/pexels-artbovich-6758521.jpg',
    'BOSTON': '../assets/images/city images/boston condo.png',
    'EASTIE': '../assets/images/city images/east boston rental propety.png',
    'SOUTHIE': '../assets/images/city images/south boston kichen.png',
    'ALLSTON': '../assets/images/city images/alston finished apartment.png',
    'LEXINGTON': '../assets/images/Luxury apt images/pexels-artbovich-7031214.jpg',
    'NEEDHAM': '../assets/images/Luxury apt images/pexels-artbovich-8082229.jpg',
    'WELLESLEY': '../assets/images/Luxury apt images/pexels-kseniachernaya-5691495.jpg',
    'WESTON': '../assets/images/services images/luxury residential .jpg',
    'OFFICE': '../assets/images/services images/commercial properties.jpg',
    'RESTAURANT': '../assets/images/Luxury apt images/pexels-artbovich-6077368.jpg',
    'LANDLORD': '../assets/images/services images/move in move out clean.jpg',
    'SPRING': '../assets/images/Luxury apt images/pexels-artbovich-6636314.jpg',
    'AIRBNB': '../assets/images/Luxury apt images/pexels-artbovich-6492384.jpg',
    'DAYCARE': '../assets/images/Luxury apt images/pexels-artbovich-8082229.jpg',
    'CONTRACTOR': '../assets/images/services images/New Build Final Clean.jpg',
    'CHECKLIST': '../assets/images/services images/move in move out clean.jpg',
}


def update_blog_index():
    """Replace text-only card-image divs with actual background images."""
    index_path = os.path.join(BLOG_DIR, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Replace .card-image CSS to support background images
    old_card_css = re.search(
        r'\.card-image\s*\{[^}]*\}',
        content
    )
    if old_card_css:
        new_card_css = """.card-image {
            width: 100%;
            height: 200px;
            background: linear-gradient(135deg, var(--navy-mid), var(--navy-light));
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: var(--font-display);
            font-size: 2.2rem;
            letter-spacing: 0.1em;
            color: rgba(255, 255, 255, 0.9);
            border-bottom: 1px solid rgba(201, 169, 110, 0.06);
            background-size: cover;
            background-position: center;
            position: relative;
            overflow: hidden;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
        }

        .card-image::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(to bottom, rgba(10, 22, 40, 0.25), rgba(10, 22, 40, 0.6));
            z-index: 1;
        }

        .card-image span {
            position: relative;
            z-index: 2;
        }"""
        content = content[:old_card_css.start()] + new_card_css + content[old_card_css.end():]

    # Replace each card-image div with background image version
    def replace_card_image(match):
        city_name = match.group(1).strip()
        img_path = CARD_IMAGE_MAP.get(city_name)
        if img_path:
            return f'<div class="card-image" style="background-image: url(\'{img_path}\')"><span>{city_name}</span></div>'
        return match.group(0)

    content = re.sub(
        r'<div class="card-image">(\w+)</div>',
        replace_card_image,
        content
    )

    if content != original:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  OK: blog/index.html (card images + overlays)')
        return True
    else:
        print(f'  SKIP: blog/index.html (no changes)')
        return False


def main():
    blog_dir = os.path.abspath(BLOG_DIR)
    files = sorted(f for f in os.listdir(blog_dir) if f.endswith('.html') and f != 'index.html')

    print(f'Enhancing {len(files)} blog posts...\n')

    updated = 0
    for filename in files:
        filepath = os.path.join(blog_dir, filename)
        if process_blog(filepath, filename):
            print(f'  OK: {filename}')
            updated += 1
        else:
            print(f'  SKIP: {filename}')

    print(f'\nUpdated {updated}/{len(files)} blog posts.')
    print(f'\nUpdating blog index cards...')
    update_blog_index()
    print('\nDone!')


if __name__ == '__main__':
    main()
