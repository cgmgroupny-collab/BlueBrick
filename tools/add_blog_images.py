#!/usr/bin/env python3
"""
Batch-add images to all Blue Brick blog posts.
Inserts 2 images per post: one after the first content section, one before the CTA.
Images are matched by category and city.
"""

import os
import re

BLOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'blog')

# Image paths relative to blog/ directory
CITY_IMAGES = {
    'allston': '../assets/images/city images/alston finished apartment.png',
    'boston': '../assets/images/city images/boston condo.png',
    'brighton': '../assets/images/city images/brighton apartment.png',
    'east-boston': '../assets/images/city images/east boston rental propety.png',
    'newton': '../assets/images/city images/newton home.png',
    'south-boston': '../assets/images/city images/south boston kichen.png',
    'waltham': '../assets/images/city images/waltham office.png',
}

CITY_ALT_TEXT = {
    'allston': 'Professional cleaning results in an Allston apartment',
    'boston': 'Spotless Boston condo after professional cleaning',
    'brighton': 'Clean Brighton apartment by Blue Brick',
    'east-boston': 'East Boston rental property cleaned by Blue Brick',
    'newton': 'Newton home deep cleaned by Blue Brick',
    'south-boston': 'South Boston kitchen after professional deep cleaning',
    'waltham': 'Waltham office cleaned by Blue Brick',
}

SERVICE_IMAGES = {
    'deep-cleaning': '../assets/images/services images/luxury residential .jpg',
    'move-in-move-out': '../assets/images/services images/move in move out clean.jpg',
    'post-construction': '../assets/images/services images/New Build Final Clean.jpg',
    'office': '../assets/images/services images/commercial properties.jpg',
    'restaurant': '../assets/images/services images/luxury residential .jpg',
    'renovation': '../assets/images/services images/renovation restoration clean.jpg',
}

SERVICE_ALT_TEXT = {
    'deep-cleaning': 'Luxury residential deep cleaning by Blue Brick',
    'move-in-move-out': 'Move-in move-out cleaning service by Blue Brick',
    'post-construction': 'Post-construction final clean by Blue Brick',
    'office': 'Commercial office cleaning by Blue Brick',
    'restaurant': 'Professional restaurant deep cleaning by Blue Brick',
    'renovation': 'Renovation and restoration cleaning by Blue Brick',
}

# Luxury apt stock photos — rotate across posts that lack a city image
LUXURY_PHOTOS = [
    '../assets/images/Luxury apt images/pexels-artbovich-6077368.jpg',
    '../assets/images/Luxury apt images/pexels-artbovich-6492384.jpg',
    '../assets/images/Luxury apt images/pexels-artbovich-6636314.jpg',
    '../assets/images/Luxury apt images/pexels-artbovich-6758521.jpg',
    '../assets/images/Luxury apt images/pexels-artbovich-7031214.jpg',
    '../assets/images/Luxury apt images/pexels-artbovich-8082229.jpg',
    '../assets/images/Luxury apt images/pexels-kseniachernaya-5691495.jpg',
]

# CSS to inject for blog images
IMAGE_CSS = """
        /* ============================================
           BLOG CONTENT IMAGES
           ============================================ */
        .article-container .blog-image {
            width: 100%;
            margin: 2rem 0;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 29, 74, 0.1);
        }

        .article-container figure {
            margin: 2.5rem 0;
        }

        .article-container figcaption {
            font-size: 0.8rem;
            color: var(--mid-gray);
            text-align: center;
            margin-top: 0.5rem;
            font-style: italic;
        }
"""


def get_category(filename):
    """Determine blog post category from filename."""
    if filename.startswith('deep-cleaning-'):
        return 'deep-cleaning'
    elif filename.startswith('move-in-move-out-') or filename.startswith('move-out-cleaning'):
        return 'move-in-move-out'
    elif filename.startswith('post-construction-'):
        return 'post-construction'
    elif filename.startswith('office-cleaning-'):
        return 'office'
    elif filename.startswith('restaurant-'):
        return 'restaurant'
    elif filename.startswith('spring-cleaning'):
        return 'deep-cleaning'
    elif filename.startswith('property-manager'):
        return 'move-in-move-out'
    elif filename.startswith('daycare-'):
        return 'deep-cleaning'
    elif filename.startswith('airbnb-'):
        return 'deep-cleaning'
    return 'deep-cleaning'


def get_city(filename):
    """Extract city slug from filename."""
    # Remove category prefix and .html
    name = filename.replace('.html', '')
    for prefix in ['deep-cleaning-', 'move-in-move-out-cleaning-',
                    'post-construction-cleaning-', 'office-cleaning-']:
        if name.startswith(prefix):
            return name[len(prefix):]
    return None


def get_city_display(city_slug):
    """Convert slug to display name."""
    if not city_slug:
        return 'Greater Boston'
    return city_slug.replace('-', ' ').title()


def build_image_html(src, alt, caption=None):
    """Build an image or figure HTML block."""
    if caption:
        return f'''
                <figure class="reveal">
                    <img src="{src}" alt="{alt}" class="blog-image" loading="lazy">
                    <figcaption>{caption}</figcaption>
                </figure>
'''
    return f'''
                <div class="reveal">
                    <img src="{src}" alt="{alt}" class="blog-image" loading="lazy">
                </div>
'''


def process_blog(filepath, filename, luxury_idx):
    """Add images to a single blog post."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has blog images
    if 'blog-image' in content:
        print(f'  SKIP (already has images): {filename}')
        return luxury_idx

    # Skip index
    if filename == 'index.html':
        return luxury_idx

    category = get_category(filename)
    city = get_city(filename)
    city_display = get_city_display(city)

    # Pick image 1: service category image (after first content section)
    service_img = SERVICE_IMAGES.get(category, SERVICE_IMAGES['deep-cleaning'])
    service_alt = SERVICE_ALT_TEXT.get(category, SERVICE_ALT_TEXT['deep-cleaning'])

    # Pick image 2: city image if available, otherwise luxury stock photo
    if city and city in CITY_IMAGES:
        secondary_img = CITY_IMAGES[city]
        secondary_alt = CITY_ALT_TEXT[city]
        secondary_caption = f'Blue Brick cleaning results in {city_display}'
    else:
        secondary_img = LUXURY_PHOTOS[luxury_idx % len(LUXURY_PHOTOS)]
        secondary_alt = f'Professional cleaning service in {city_display} by Blue Brick'
        secondary_caption = f'Premium cleaning results by Blue Brick'
        luxury_idx += 1

    # For post-construction, use renovation image as secondary
    if category == 'post-construction' and city not in (CITY_IMAGES if city else {}):
        secondary_img = SERVICE_IMAGES['renovation']
        secondary_alt = SERVICE_ALT_TEXT['renovation']
        secondary_caption = 'Renovation cleanup by Blue Brick professionals'

    # Build image HTML blocks
    img1_html = build_image_html(
        service_img,
        f'{service_alt} in {city_display}',
        f'Professional {category.replace("-", " ")} service in {city_display}'
    )
    img2_html = build_image_html(
        secondary_img,
        secondary_alt,
        secondary_caption
    )

    # --- Inject CSS ---
    if 'BLOG CONTENT IMAGES' not in content:
        # Insert before the HEADER comment or before closing </style>
        css_insert_point = content.find('/* ============================================\n           HEADER')
        if css_insert_point == -1:
            css_insert_point = content.find('</style>')
        if css_insert_point != -1:
            content = content[:css_insert_point] + IMAGE_CSS + '\n' + content[css_insert_point:]

    # --- Insert Image 1: after the SECOND </div> inside article ---
    # (after the first content section)
    # Match any article class variant
    article_start = -1
    for cls in ['article-container', 'article-wrapper', 'article-section',
                'article-content', 'post-content']:
        # Use a flexible search that handles role= and other attributes
        idx = content.find(f'<article class="{cls}"')
        if idx != -1:
            article_start = idx
            break
    if article_start == -1:
        print(f'  SKIP (no article tag found): {filename}')
        return luxury_idx

    # Find the end of the second reveal div
    pos = article_start
    div_count = 0
    search_pos = pos
    insert_pos_1 = None
    while div_count < 2:
        # Find next closing </div> that ends a reveal block
        next_close = content.find('</div>', search_pos)
        if next_close == -1:
            break
        # Check if this is a reveal div (look backward for class="reveal")
        chunk = content[max(0, next_close - 2000):next_close]
        if 'class="reveal"' in chunk or "class='reveal'" in chunk:
            div_count += 1
            if div_count == 1:
                insert_pos_1 = next_close + len('</div>')
        search_pos = next_close + 1

    # --- Insert Image 2: before the CTA section ---
    cta_pos = content.find('<section class="cta-section')
    insert_pos_2 = None
    if cta_pos != -1:
        # Find the closing </article> or </section> before cta
        # Insert just before the CTA section
        # Look for the closing </section> of article-section before CTA
        pre_cta = content[:cta_pos].rfind('</section>')
        if pre_cta != -1:
            insert_pos_2 = pre_cta

    # Do insertions (from end to start to preserve positions)
    if insert_pos_2 and insert_pos_2 > (insert_pos_1 or 0):
        content = content[:insert_pos_2] + '\n' + img2_html + '\n' + content[insert_pos_2:]

    if insert_pos_1:
        content = content[:insert_pos_1] + '\n' + img1_html + content[insert_pos_1:]

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    img_count = (1 if insert_pos_1 else 0) + (1 if insert_pos_2 else 0)
    print(f'  OK ({img_count} images): {filename}')
    return luxury_idx


def main():
    blog_dir = os.path.abspath(BLOG_DIR)
    files = sorted(f for f in os.listdir(blog_dir) if f.endswith('.html') and f != 'index.html')

    print(f'Adding images to {len(files)} blog posts...\n')

    luxury_idx = 0
    for filename in files:
        filepath = os.path.join(blog_dir, filename)
        luxury_idx = process_blog(filepath, filename, luxury_idx)

    print(f'\nDone! Processed {len(files)} posts.')


if __name__ == '__main__':
    main()
