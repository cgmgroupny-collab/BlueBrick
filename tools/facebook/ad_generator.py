"""
Blue Brick Ad Image Generator

Renders HTML ad templates to PNG images using Playwright.
Creates 1080x1080 square images optimized for Facebook.

Usage:
    python ad_generator.py                          # Generate default test ad
    python ad_generator.py --template my_ad.html    # Custom template
    python ad_generator.py --output my_ad.png       # Custom output name
"""
import asyncio
import argparse
from pathlib import Path

from playwright.async_api import async_playwright

from config import ADS_DIR


async def generate_ad(template_name="test_ad.html", output_name="test_ad.png"):
    """Render an HTML ad template to a PNG image."""
    template_path = ADS_DIR / template_name
    output_path = ADS_DIR / output_name

    if not template_path.exists():
        print(f"[ERROR] Template not found: {template_path}")
        return None

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1080})

        await page.goto(f"file://{template_path.resolve()}")
        await page.wait_for_load_state("networkidle")

        await page.screenshot(path=str(output_path), type="png")
        await browser.close()

    print(f"[OK] Ad generated: {output_path}")
    print(f"     Size: 1080x1080px")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ad images from HTML templates")
    parser.add_argument("--template", default="test_ad.html", help="HTML template file in ads/")
    parser.add_argument("--output", default="test_ad.png", help="Output PNG filename")
    args = parser.parse_args()
    asyncio.run(generate_ad(args.template, args.output))
