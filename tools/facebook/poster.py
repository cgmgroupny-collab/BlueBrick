"""
Blue Brick Facebook Group Poster

Posts ads to Facebook groups with human-like behavior.
Default: 10 groups in ~15 minutes (~90s between posts).

Usage:
    python poster.py                          # Post to all saved groups
    python poster.py --groups 5               # Post to first 5 groups
    python poster.py --ad "ads/my_ad.png"     # Use specific ad image
    python poster.py --text "Custom post"     # Override post text
    python poster.py --dry-run                # Preview without posting
"""
import asyncio
import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

from config import (
    FB_EMAIL, FB_PASSWORD, SESSION_FILE, DATA_DIR, ADS_DIR,
    POST_DELAY_MIN, POST_DELAY_MAX, VIEWPORT, USER_AGENT,
    TIMEZONE, GEOLOCATION, POST_GREETINGS, POST_CLOSINGS, BRAND,
    load_groups,
)
from stealth import (
    apply_stealth, human_delay, human_type, human_scroll,
    click_with_fallbacks, check_for_checkpoint,
)


def generate_post_text(custom_text=None):
    """Generate varied post text to avoid duplicate detection."""
    if custom_text:
        return custom_text

    greeting = random.choice(POST_GREETINGS)
    closing = random.choice(POST_CLOSINGS)

    bodies = [
        (
            f"Looking for a reliable cleaning service in the Greater Boston area? "
            f"{BRAND['name']} offers premium residential and commercial cleaning — "
            f"deep cleans, move-in/move-out, post-construction, and recurring service."
        ),
        (
            f"Tired of coming home to a messy house? {BRAND['name']} provides luxury "
            f"cleaning services across Boston, Newton, Waltham, and surrounding areas. "
            f"We handle everything from regular upkeep to deep cleans."
        ),
        (
            f"Just moved in? Renovating? Selling your home? {BRAND['name']} specializes "
            f"in post-construction cleaning, pre-sale deep cleans, and move-out cleaning "
            f"throughout Greater Boston."
        ),
        (
            f"If you need your home or office spotless, {BRAND['name']} has you covered. "
            f"We serve Boston, South Boston, East Boston, Newton, Waltham, Brighton & more. "
            f"Licensed, insured, and trusted by homeowners across the area."
        ),
        (
            f"Need a cleaning crew you can actually trust? {BRAND['name']} delivers "
            f"top-tier cleaning for homes, offices, and commercial spaces in Greater Boston. "
            f"First-time clients get a free estimate!"
        ),
    ]

    body = random.choice(bodies)
    contact = f"\n\n📞 {BRAND['phone']}\n📧 {BRAND['email']}"

    return f"{greeting} {body}{contact}\n\n{closing}"


async def login(browser):
    """Login to Facebook, restoring session if available."""
    context_args = {
        "viewport": VIEWPORT,
        "user_agent": USER_AGENT,
        "locale": "en-US",
        "timezone_id": TIMEZONE,
        "geolocation": GEOLOCATION,
        "permissions": ["geolocation"],
    }

    # Try restoring saved session
    if SESSION_FILE.exists():
        try:
            context = await browser.new_context(
                storage_state=str(SESSION_FILE),
                **context_args,
            )
            await apply_stealth(context)
            page = await context.new_page()
            await page.goto("https://www.facebook.com/")
            await page.wait_for_selector(
                '[aria-label="Search Facebook"]', timeout=15000
            )
            print("[OK] Session restored")
            return context, page
        except Exception as e:
            print(f"[!] Session expired ({e}), logging in fresh...")

    # Fresh login
    context = await browser.new_context(**context_args)
    await apply_stealth(context)
    page = await context.new_page()
    await page.goto("https://www.facebook.com/")
    await human_delay(1, 2)

    # Enter credentials
    await page.fill("#email", FB_EMAIL)
    await human_delay(0.5, 1.5)
    await page.fill("#pass", FB_PASSWORD)
    await human_delay(0.3, 0.8)
    await page.click('[name="login"]')

    # Wait for login to complete
    try:
        await page.wait_for_selector(
            '[aria-label="Search Facebook"]', timeout=30000
        )
    except Exception:
        # Check for 2FA/checkpoint
        status = await check_for_checkpoint(page)
        if status:
            print(f"\n[!] Facebook {status} detected.")
            print("    Complete the verification in the browser window.")
            print("    Waiting up to 2 minutes...")
            await page.wait_for_selector(
                '[aria-label="Search Facebook"]', timeout=120000
            )
        else:
            print("[ERROR] Login failed — check credentials in .env")
            sys.exit(1)

    # Save session
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    await context.storage_state(path=str(SESSION_FILE))
    print("[OK] Logged in and session saved")
    return context, page


async def warmup(page):
    """Browse feed briefly before posting — looks more natural."""
    print("[...] Warming up — browsing feed...")
    await page.goto("https://www.facebook.com/")
    await human_delay(2, 4)

    for i in range(random.randint(2, 4)):
        await human_scroll(page)
        await human_delay(1.5, 3)

    # Maybe like something
    if random.random() < 0.3:
        try:
            likes = await page.query_selector_all('[aria-label="Like"]')
            if likes:
                target = random.choice(likes[:5])
                await target.click()
                await human_delay(1, 2)
                print("  Liked a post (natural behavior)")
        except Exception:
            pass

    print("[OK] Warmup done")


async def post_to_group(page, group_url, text, image_path=None):
    """Post content to a single Facebook group."""
    await page.goto(group_url)
    await page.wait_for_load_state("networkidle")
    await human_delay(2, 4)

    # Check for issues
    status = await check_for_checkpoint(page)
    if status:
        return {"success": False, "error": f"Checkpoint: {status}", "url": group_url}

    # Click the composer box
    composer_selectors = [
        'div[role="button"] span:has-text("Write something")',
        'div[role="button"] span:has-text("What\'s on your mind")',
        '[aria-label="Create a public post…"]',
        '[aria-label="Write something..."]',
    ]
    try:
        await click_with_fallbacks(page, composer_selectors, timeout=12000)
    except Exception:
        return {"success": False, "error": "Could not find composer", "url": group_url}

    await human_delay(1.5, 3)

    # Wait for dialog
    try:
        await page.wait_for_selector('div[role="dialog"]', timeout=10000)
    except Exception:
        return {"success": False, "error": "Composer dialog didn't open", "url": group_url}

    await human_delay(0.5, 1)

    # Upload image first if provided
    if image_path:
        try:
            photo_selectors = [
                'div[role="dialog"] [aria-label="Photo/video"]',
                'div[role="dialog"] [aria-label="Photo/Video"]',
                'div[role="dialog"] [aria-label="Photo/video"][role="button"]',
            ]
            await click_with_fallbacks(page, photo_selectors, timeout=8000)
            await human_delay(1, 2)

            file_input = await page.wait_for_selector(
                'div[role="dialog"] input[type="file"]', timeout=5000
            )
            await file_input.set_input_files(str(image_path))
            await human_delay(3, 6)  # Wait for upload
        except Exception as e:
            print(f"  [!] Image upload failed ({e}), posting text only")

    # Find the text editor and type
    editor_selectors = [
        'div[role="dialog"] div[contenteditable="true"][role="textbox"]',
        'div[role="dialog"] div[contenteditable="true"]',
        'div[role="dialog"] [aria-label="Write something..."]',
        'div[role="dialog"] [aria-label="Create a public post…"]',
    ]
    try:
        editor = await click_with_fallbacks(page, editor_selectors, timeout=8000)
    except Exception:
        return {"success": False, "error": "Could not find text editor", "url": group_url}

    # Type post text with human-like speed
    await human_delay(0.3, 0.8)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        for char in line:
            await page.keyboard.type(char, delay=random.randint(30, 100))
            if random.random() < 0.03:
                await human_delay(0.3, 1.0)
        if i < len(lines) - 1:
            await page.keyboard.press("Shift+Enter")
            await human_delay(0.1, 0.3)

    await human_delay(1, 3)

    # Click Post
    post_selectors = [
        'div[role="dialog"] div[aria-label="Post"][role="button"]',
        'div[role="dialog"] [aria-label="Post"]',
        'div[role="dialog"] span:has-text("Post")',
    ]
    try:
        await click_with_fallbacks(page, post_selectors, timeout=8000)
    except Exception:
        return {"success": False, "error": "Could not click Post button", "url": group_url}

    # Wait for dialog to close (post submitted)
    try:
        await page.wait_for_selector('div[role="dialog"]', state="hidden", timeout=20000)
    except Exception:
        # Post might be pending admin approval
        pass

    await human_delay(2, 5)
    return {"success": True, "url": group_url}


async def run(args):
    """Main posting loop."""
    if not FB_EMAIL or not FB_PASSWORD:
        print("[ERROR] Set FB_EMAIL and FB_PASSWORD in your .env file")
        print("  Example:")
        print('    FB_EMAIL=you@email.com')
        print('    FB_PASSWORD=yourpassword')
        sys.exit(1)

    groups = load_groups()
    if not groups:
        print("[ERROR] No groups saved. Run group_finder.py first.")
        sys.exit(1)

    # Filter to active/joined groups
    target_groups = [g for g in groups if g.get("joined")]
    if not target_groups:
        print("[!] No joined groups found. Using all saved groups.")
        target_groups = groups

    # Limit number of groups
    max_groups = args.groups or 10
    target_groups = target_groups[:max_groups]

    # Resolve ad image
    image_path = None
    if args.ad:
        image_path = Path(args.ad)
        if not image_path.is_absolute():
            image_path = ADS_DIR / args.ad
        if not image_path.exists():
            print(f"[ERROR] Ad image not found: {image_path}")
            sys.exit(1)
    else:
        # Use default test ad if it exists
        default_ad = ADS_DIR / "test_ad.png"
        if default_ad.exists():
            image_path = default_ad

    print(f"\n{'='*50}")
    print(f"  Blue Brick Facebook Group Poster")
    print(f"  Groups: {len(target_groups)} | Image: {'Yes' if image_path else 'No'}")
    print(f"  Delay: {POST_DELAY_MIN}-{POST_DELAY_MAX}s between posts")
    print(f"{'='*50}\n")

    if args.dry_run:
        print("[DRY RUN] Preview mode — no posts will be made\n")
        for i, group in enumerate(target_groups, 1):
            text = generate_post_text(args.text)
            print(f"  {i}. {group.get('name', group['url'])}")
            print(f"     Text: {text[:80]}...")
            print()
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-first-run",
            ],
        )

        context, page = await login(browser)
        await warmup(page)

        results = []
        for i, group in enumerate(target_groups, 1):
            group_url = group.get("url", group.get("slug", ""))
            group_name = group.get("name", group_url)

            print(f"\n[{i}/{len(target_groups)}] Posting to: {group_name}")

            text = generate_post_text(args.text)
            result = await post_to_group(page, group_url, text, image_path)
            results.append({**result, "group_name": group_name, "time": datetime.now().isoformat()})

            if result["success"]:
                print(f"  [OK] Posted successfully")
            else:
                print(f"  [FAIL] {result['error']}")
                # If checkpoint, stop immediately
                if "Checkpoint" in result.get("error", ""):
                    print("\n[STOP] Facebook checkpoint detected. Stopping to protect account.")
                    break

            # Delay between posts (except after last one)
            if i < len(target_groups):
                delay = random.uniform(POST_DELAY_MIN, POST_DELAY_MAX)
                print(f"  Waiting {delay:.0f}s before next post...")
                await asyncio.sleep(delay)

        # Save session for next run
        await context.storage_state(path=str(SESSION_FILE))

        # Save results log
        log_file = DATA_DIR / f"post_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, "w") as f:
            json.dump(results, f, indent=2)

        # Summary
        success = sum(1 for r in results if r["success"])
        print(f"\n{'='*50}")
        print(f"  Done! {success}/{len(results)} posts successful")
        print(f"  Log saved: {log_file}")
        print(f"{'='*50}")

        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post ads to Facebook groups")
    parser.add_argument("--groups", type=int, help="Number of groups to post to (default: 10)")
    parser.add_argument("--ad", type=str, help="Path to ad image (relative to ads/ or absolute)")
    parser.add_argument("--text", type=str, help="Custom post text (overrides generated text)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    args = parser.parse_args()
    asyncio.run(run(args))
