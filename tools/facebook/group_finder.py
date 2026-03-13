"""
Blue Brick Facebook Group Finder

Searches Facebook for active local groups relevant to cleaning leads.
Ranks them by member count and saves results for the poster.

Usage:
    python group_finder.py                         # Search all default keywords
    python group_finder.py --keywords "Boston moms" # Search specific term
    python group_finder.py --limit 50              # Max groups to save
"""
import asyncio
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

from config import (
    FB_EMAIL, FB_PASSWORD, SESSION_FILE, DATA_DIR, GROUPS_FILE,
    SEARCH_KEYWORDS, VIEWPORT, USER_AGENT, TIMEZONE, GEOLOCATION,
    load_groups, save_groups,
)
from stealth import (
    apply_stealth, human_delay, human_scroll,
    click_with_fallbacks, check_for_checkpoint,
)


def parse_member_count(text):
    """Parse member count strings like '10.5K members' into integers."""
    if not text:
        return 0
    text = text.strip().upper().replace(",", "")
    match = re.search(r"([\d.]+)\s*(K|M)?", text)
    if not match:
        return 0
    num = float(match.group(1))
    suffix = match.group(2)
    if suffix == "K":
        return int(num * 1_000)
    elif suffix == "M":
        return int(num * 1_000_000)
    return int(num)


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

    if SESSION_FILE.exists():
        try:
            context = await browser.new_context(
                storage_state=str(SESSION_FILE), **context_args
            )
            await apply_stealth(context)
            page = await context.new_page()
            await page.goto("https://www.facebook.com/")
            await page.wait_for_selector('[aria-label="Search Facebook"]', timeout=15000)
            print("[OK] Session restored")
            return context, page
        except Exception:
            print("[!] Session expired, logging in fresh...")

    context = await browser.new_context(**context_args)
    await apply_stealth(context)
    page = await context.new_page()
    await page.goto("https://www.facebook.com/")
    await human_delay(1, 2)

    await page.fill("#email", FB_EMAIL)
    await human_delay(0.5, 1.5)
    await page.fill("#pass", FB_PASSWORD)
    await human_delay(0.3, 0.8)
    await page.click('[name="login"]')

    try:
        await page.wait_for_selector('[aria-label="Search Facebook"]', timeout=30000)
    except Exception:
        status = await check_for_checkpoint(page)
        if status:
            print(f"\n[!] Facebook {status} detected — complete verification in browser.")
            await page.wait_for_selector('[aria-label="Search Facebook"]', timeout=120000)
        else:
            print("[ERROR] Login failed")
            sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    await context.storage_state(path=str(SESSION_FILE))
    print("[OK] Logged in")
    return context, page


async def search_groups(page, keyword):
    """Search Facebook for groups matching a keyword."""
    print(f"\n  Searching: '{keyword}'")

    # Use Facebook search
    search_url = f"https://www.facebook.com/search/groups/?q={keyword.replace(' ', '%20')}"
    await page.goto(search_url)
    await page.wait_for_load_state("networkidle")
    await human_delay(2, 4)

    # Scroll to load more results
    for _ in range(4):
        await human_scroll(page)
        await human_delay(1, 2.5)

    # Extract group data from the page
    groups = await page.evaluate("""
        () => {
            const results = [];
            const seen = new Set();
            const links = document.querySelectorAll('a[href*="/groups/"]');

            links.forEach(link => {
                const href = link.href;
                const match = href.match(/groups\\/([\\w.-]+)/);
                if (!match || seen.has(match[1])) return;

                // Skip system pages
                const slug = match[1];
                if (['search', 'feed', 'discover', 'create'].includes(slug)) return;
                seen.add(slug);

                // Walk up to find the result container
                let container = link;
                for (let i = 0; i < 10; i++) {
                    if (!container.parentElement) break;
                    container = container.parentElement;
                    if (container.getAttribute('role') === 'article') break;
                }
                const allText = container.textContent || '';

                // Extract name from the link text
                let name = '';
                const spans = link.querySelectorAll('span');
                spans.forEach(s => {
                    const t = s.textContent.trim();
                    if (t.length > name.length && t.length < 200 && !t.includes('member')) {
                        name = t;
                    }
                });
                if (!name) name = link.textContent.trim().substring(0, 200);

                // Extract member count
                const memberMatch = allText.match(/(\\d[\\d.,]*[KkMm]?)\\s*members/i);

                // Detect privacy
                const privacy = allText.includes('Private') ? 'Private' :
                                allText.includes('Public') ? 'Public' : 'Unknown';

                // Detect activity hints
                const postsMatch = allText.match(/(\\d+)\\+?\\s*(?:posts?|new)\\s*(?:a|per|today|this)\\s*(?:day|week|month)/i);

                if (name && name.length > 2) {
                    results.push({
                        name: name,
                        url: 'https://www.facebook.com/groups/' + slug,
                        slug: slug,
                        members_raw: memberMatch ? memberMatch[1] : null,
                        privacy: privacy,
                        activity_hint: postsMatch ? postsMatch[0] : null,
                    });
                }
            });
            return results;
        }
    """)

    # Parse member counts
    for g in groups:
        g["members"] = parse_member_count(g.get("members_raw", ""))

    print(f"  Found {len(groups)} groups")
    return groups


async def run(args):
    """Main group finder flow."""
    if not FB_EMAIL or not FB_PASSWORD:
        print("[ERROR] Set FB_EMAIL and FB_PASSWORD in your .env file")
        sys.exit(1)

    keywords = args.keywords if args.keywords else SEARCH_KEYWORDS
    if isinstance(keywords, str):
        keywords = [keywords]

    print(f"\n{'='*50}")
    print(f"  Blue Brick Group Finder")
    print(f"  Keywords: {len(keywords)}")
    print(f"{'='*50}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ],
        )

        context, page = await login(browser)

        all_groups = {}
        for keyword in keywords:
            status = await check_for_checkpoint(page)
            if status:
                print(f"\n[STOP] Checkpoint detected. Stopping search.")
                break

            groups = await search_groups(page, keyword)

            for g in groups:
                slug = g["slug"]
                if slug in all_groups:
                    # Keep the one with more info
                    if g["members"] > all_groups[slug].get("members", 0):
                        all_groups[slug] = g
                else:
                    g["found_via"] = keyword
                    all_groups[slug] = g

            # Delay between searches
            await human_delay(3, 6)

        # Rank by member count (bigger = more active usually)
        ranked = sorted(all_groups.values(), key=lambda g: g.get("members", 0), reverse=True)

        # Limit results
        limit = args.limit or 100
        ranked = ranked[:limit]

        # Merge with existing groups (preserve "joined" status)
        existing = {g["slug"]: g for g in load_groups()}
        for g in ranked:
            if g["slug"] in existing:
                g["joined"] = existing[g["slug"]].get("joined", False)
            else:
                g["joined"] = False

        # Save
        save_groups(ranked)
        await context.storage_state(path=str(SESSION_FILE))

        # Print results
        print(f"\n{'='*60}")
        print(f"  {'Rank':<5} {'Members':<10} {'Privacy':<9} {'Name'}")
        print(f"  {'-'*55}")
        for i, g in enumerate(ranked[:30], 1):
            members = g.get("members_raw") or "?"
            print(f"  {i:<5} {members:<10} {g['privacy']:<9} {g['name'][:50]}")
        if len(ranked) > 30:
            print(f"  ... and {len(ranked) - 30} more")

        print(f"\n  Total: {len(ranked)} groups saved to {GROUPS_FILE}")
        print(f"  Next: Review the list, mark groups as joined, then run poster.py")
        print(f"{'='*60}")

        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find Facebook groups for Blue Brick outreach")
    parser.add_argument("--keywords", nargs="+", help="Custom search keywords")
    parser.add_argument("--limit", type=int, help="Max groups to save (default: 100)")
    args = parser.parse_args()
    asyncio.run(run(args))
