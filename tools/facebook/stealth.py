"""
Blue Brick Facebook Automation — Stealth & Human-Like Behavior
"""
import random
import asyncio


STEALTH_INIT_SCRIPT = """
    // Remove webdriver flag
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

    // Fix chrome object
    window.chrome = { runtime: {}, loadTimes: function(){}, csi: function(){}, app: {} };

    // Fix permissions query
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) =>
        parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters);

    // Fix plugins (headless has 0)
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });

    // Fix languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
    });
"""


async def apply_stealth(context):
    """Apply stealth patches to browser context."""
    await context.add_init_script(STEALTH_INIT_SCRIPT)


async def human_delay(min_s=0.5, max_s=2.0):
    """Random delay with gaussian distribution (more natural than uniform)."""
    mean = (min_s + max_s) / 2
    std = (max_s - min_s) / 4
    delay = max(min_s, min(max_s, random.gauss(mean, std)))
    await asyncio.sleep(delay)
    return delay


async def human_type(page, element, text, min_delay_ms=30, max_delay_ms=120):
    """Type text character by character with variable speed."""
    await element.click()
    await human_delay(0.2, 0.5)

    for char in text:
        await page.keyboard.type(char, delay=random.randint(min_delay_ms, max_delay_ms))
        # 5% chance of micro-pause (thinking)
        if random.random() < 0.05:
            await human_delay(0.3, 1.2)


async def human_scroll(page, scrolls=1):
    """Scroll like a human — variable distance."""
    for _ in range(scrolls):
        distance = random.randint(200, 600)
        await page.mouse.wheel(0, distance)
        await human_delay(0.8, 2.0)


async def click_with_fallbacks(page, selectors, timeout=10000):
    """Try multiple selectors — Facebook changes DOM frequently."""
    per_selector_timeout = max(2000, timeout // len(selectors))
    for selector in selectors:
        try:
            element = await page.wait_for_selector(selector, timeout=per_selector_timeout)
            if element:
                await human_delay(0.2, 0.6)
                await element.click()
                return element
        except Exception:
            continue
    raise Exception(f"None of the selectors matched: {selectors}")


async def check_for_checkpoint(page):
    """Check if Facebook has thrown a challenge."""
    url = page.url
    if "checkpoint" in url:
        return "checkpoint"
    captcha = await page.query_selector('[data-testid="captcha"]')
    if captcha:
        return "captcha"
    blocked = await page.query_selector('text="You\'re Temporarily Blocked"')
    if blocked:
        return "blocked"
    return None
