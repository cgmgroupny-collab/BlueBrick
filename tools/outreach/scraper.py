"""
Blue Brick Lead Scraper
-----------------------
Uses Playwright + BeautifulSoup to find businesses near Waltham 02453
and extract contact info from their websites.

Usage:
    python3 tools/outreach/scraper.py
    python3 tools/outreach/scraper.py --category realtors
    python3 tools/outreach/scraper.py --category contractors --max-results 30
"""
import asyncio
import csv
import re
import random
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))
from config import CATEGORIES, DATA_DIR, LEADS_CSV, SCRAPE_DELAY_MIN, SCRAPE_DELAY_MAX

# Email regex
EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
)

# Filter junk emails
JUNK_DOMAINS = {
    "example.com", "sentry.io", "wixpress.com", "googleapis.com",
    "w3.org", "schema.org", "facebook.com", "twitter.com",
    "instagram.com", "google.com", "yelp.com", "yahoo.com",
    "wordpress.org", "gravatar.com", "squarespace.com",
    "sentry-next.wixpress.com", "wix.com",
    "hearst.com", "omeda.com", "futurenet.com", "peerspace.com",
    "redfin.com", "realtor.com", "remax.com", "realty.com",
    "realestateagents.com", "interiordesign.net", "decorilla.com",
    "housebeautiful.com", "homesandgardens.com", "doordash.com",
    "resy.com", "restaurantguru.com", "opentable.com", "grubhub.com",
    "ubereats.com", "postmates.com", "seamless.com",
    "ohio.gov", "ny.gov", "state.ma.us", "mass.gov",
    "cremedelacreme.com", "cremeschool.com", "winnie.com",
    "childcare.gov", "care.com", "brightwheel.com", "kindercare.com",
    "goddardschool.com", "cadenceacademy.com", "learningcaregroup.com",
}

JUNK_PREFIXES = {"noreply", "no-reply", "support", "admin", "webmaster", "postmaster", "user"}
JUNK_EMAILS = {"user@domain.com", "name@domain.com", "email@domain.com", "your@email.com"}


def is_valid_email(email: str) -> bool:
    email = email.lower().strip()
    if email.startswith("%20") or email.startswith(" "):
        email = email.lstrip("%20").lstrip()
    domain = email.split("@")[-1]
    prefix = email.split("@")[0]
    if email in JUNK_EMAILS:
        return False
    if domain in JUNK_DOMAINS:
        return False
    if prefix in JUNK_PREFIXES:
        return False
    if len(email) > 60:
        return False
    if any(ext in email for ext in [".png", ".jpg", ".svg", ".gif", ".css", ".js"]):
        return False
    return True


def extract_emails(text: str) -> List[str]:
    raw = EMAIL_RE.findall(text)
    return list(set(e.lower() for e in raw if is_valid_email(e)))


def extract_phones(text: str) -> List[str]:
    phone_re = re.compile(
        r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    )
    raw = phone_re.findall(text)
    phones = []
    for p in raw:
        digits = re.sub(r"\D", "", p)
        if len(digits) == 10:
            phones.append("({}) {}-{}".format(digits[:3], digits[3:6], digits[6:]))
        elif len(digits) == 11 and digits[0] == "1":
            digits = digits[1:]
            phones.append("({}) {}-{}".format(digits[:3], digits[3:6], digits[6:]))
    return list(set(phones))


async def search_bing(page, query: str, max_pages: int = 2) -> List[str]:
    """Search Bing and return business website URLs via cite text extraction."""
    urls = []
    skip_domains = {
        "google.", "youtube.", "facebook.", "instagram.", "twitter.",
        "yelp.", "yellowpages.", "bbb.", "mapquest.", "angi.",
        "thumbtack.", "houzz.", "nextdoor.", "linkedin.", "pinterest.",
        "homeadvisor.", "angieslist.", "tripadvisor.", "indeed.",
        "glassdoor.", "reddit.", "wikipedia.", "tiktok.", "bing.",
        "microsoft.", "msn.", "live.", "amazon.", "zillow.",
        "allpropertymanagement.", "propertymanagement.com",
        "realtor.com", "redfin.", "remax.", "realty.com",
        "realestateagents.", "apartments.com", "trulia.",
        "housebeautiful.", "homesandgardens.", "interiordesign.net",
        "decorilla.", "peerspace.", "arsight.",
        "doordash.", "resy.", "restaurantguru.", "opentable.",
        "grubhub.", "ubereats.", "postmates.", "seamless.",
        "thefork.", "restaurant.com", "nycinteriordesign.",
        ".gov", "state.ma.us", "childcare.gov", "winnie.com",
        "cremedelacreme.com", "kindercare.", "goddardschool.",
        "cadenceacademy.", "learningcaregroup.", "care.com",
        "brightwheel.", "brightorizons.",
    }

    for page_num in range(max_pages):
        first = page_num * 10 + 1
        search_url = "https://www.bing.com/search?q={}&first={}".format(
            query.replace(" ", "+"), first
        )

        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(random.uniform(1.5, 3))

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            # Extract real URLs from <cite> text inside each search result
            # Bing wraps hrefs in redirect URLs, but <cite> shows the real domain
            for result in soup.select("li.b_algo"):
                cite = result.select_one("cite")
                if not cite:
                    continue
                cite_text = cite.get_text(strip=True)
                if not cite_text or "." not in cite_text:
                    continue
                # Clean up cite text: remove breadcrumb arrows, take base URL
                clean = cite_text.split("›")[0].strip().rstrip("/")
                if not clean.startswith("http"):
                    clean = "https://" + clean
                domain = urlparse(clean).netloc.lower()
                if not any(skip in domain for skip in skip_domains):
                    urls.append(clean)

        except Exception as e:
            print("    Warning: Search page error: {}".format(e))

        await asyncio.sleep(random.uniform(SCRAPE_DELAY_MIN, SCRAPE_DELAY_MAX))

    # Dedupe, preserve order
    seen = set()
    deduped = []
    for u in urls:
        base = urlparse(u).netloc.lower()
        if base not in seen:
            seen.add(base)
            deduped.append(u)
    return deduped


async def scrape_website(page, url: str) -> Optional[Dict]:
    """Visit a business website and extract contact info."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=12000)
        await asyncio.sleep(random.uniform(1, 2))

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Get page text + raw html for email/phone extraction
        text = soup.get_text(separator=" ", strip=True)
        combined = text + " " + html

        emails = extract_emails(combined)
        phones = extract_phones(text)

        # Get title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            for sep in [" | ", " - ", " — ", " :: ", " – "]:
                if sep in title:
                    title = title.split(sep)[0].strip()

        # Also check contact/about pages for emails if none found
        if not emails:
            contact_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].lower()
                if any(word in href for word in ["contact", "about", "team"]):
                    if href.startswith("/"):
                        base = urlparse(url)
                        href = "{}://{}{}".format(base.scheme, base.netloc, href)
                    if href.startswith("http"):
                        contact_links.append(href)

            for link in contact_links[:2]:  # Only try first 2
                try:
                    await page.goto(link, wait_until="domcontentloaded", timeout=10000)
                    await asyncio.sleep(1)
                    sub_html = await page.content()
                    sub_text = BeautifulSoup(sub_html, "html.parser").get_text(separator=" ")
                    emails = extract_emails(sub_text + " " + sub_html)
                    if emails:
                        break
                except Exception:
                    pass

        if not emails and not phones:
            return None

        return {
            "business_name": title[:100] if title else "",
            "website": url,
            "emails": emails,
            "phones": phones,
        }

    except Exception as e:
        print("  ✗ Error scraping {}: {}".format(url[:50], e))
        return None


def load_existing_leads() -> Set[str]:
    existing = set()
    if LEADS_CSV.exists():
        with open(LEADS_CSV, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row.get("website", "").lower())
                if row.get("email"):
                    existing.add(row["email"].lower())
    return existing


def save_lead(lead: Dict, category: str):
    file_exists = LEADS_CSV.exists()
    fieldnames = [
        "business_name", "category", "email", "phone",
        "website", "scraped_at", "status"
    ]

    with open(LEADS_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        emails = lead.get("emails", [])
        phones = lead.get("phones", [])

        if emails:
            for email in emails:
                writer.writerow({
                    "business_name": lead["business_name"],
                    "category": category,
                    "email": email,
                    "phone": phones[0] if phones else "",
                    "website": lead["website"],
                    "scraped_at": datetime.now().isoformat(),
                    "status": "new",
                })
        elif phones:
            writer.writerow({
                "business_name": lead["business_name"],
                "category": category,
                "email": "",
                "phone": phones[0],
                "website": lead["website"],
                "scraped_at": datetime.now().isoformat(),
                "status": "new",
            })


USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]


async def run_scraper(categories: List[str] = None, max_results: int = 20):
    if categories is None:
        categories = list(CATEGORIES.keys())

    existing = load_existing_leads()
    total_found = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for category in categories:
            queries = CATEGORIES.get(category, [])
            if not queries:
                print("⚠ Unknown category: {}".format(category))
                continue

            print("\n{}".format("=" * 60))
            print("  Searching: {}".format(category.upper().replace("_", " ")))
            print("=" * 60)

            category_urls = []
            for qi, query in enumerate(queries):
                # Fresh browser context per query to avoid Bing rate limiting
                ua = USER_AGENTS[qi % len(USER_AGENTS)]
                context = await browser.new_context(
                    viewport={"width": 1366, "height": 768},
                    user_agent=ua,
                    locale="en-US",
                    timezone_id="America/New_York",
                )
                page = await context.new_page()

                print("\n  → Bing: \"{}\"".format(query))
                urls = await search_bing(page, query, max_pages=1)
                print("    Found {} website links".format(len(urls)))
                category_urls.extend(urls)

                await context.close()
                # Longer delay between search queries
                await asyncio.sleep(random.uniform(8, 15))

            # Dedupe across queries
            seen = set()
            deduped = []
            for u in category_urls:
                base = urlparse(u).netloc.lower()
                if base not in seen:
                    seen.add(base)
                    deduped.append(u)
            category_urls = deduped[:max_results]

            print("\n  Scraping {} unique websites for contact info...".format(len(category_urls)))

            # Use a single context for scraping actual websites
            scrape_context = await browser.new_context(
                viewport={"width": 1366, "height": 768},
                user_agent=USER_AGENTS[0],
                locale="en-US",
                timezone_id="America/New_York",
            )
            scrape_page = await scrape_context.new_page()

            for i, url in enumerate(category_urls):
                if url.lower() in existing:
                    print("  [{}/{}] Skip (already have): {}".format(
                        i + 1, len(category_urls), url[:60]
                    ))
                    continue

                print("  [{}/{}] Scraping: {}...".format(
                    i + 1, len(category_urls), url[:60]
                ))
                lead = await scrape_website(scrape_page, url)

                if lead:
                    save_lead(lead, category)
                    existing.add(url.lower())
                    for e in lead.get("emails", []):
                        existing.add(e.lower())
                    total_found += 1
                    emails_str = ", ".join(lead["emails"][:2])
                    phones_str = ", ".join(lead["phones"][:1])
                    print("    ✓ {} | {} {}".format(
                        lead["business_name"][:40],
                        emails_str,
                        phones_str,
                    ))
                else:
                    print("    ✗ No contact info found")

                await asyncio.sleep(random.uniform(SCRAPE_DELAY_MIN, SCRAPE_DELAY_MAX))

            await scrape_context.close()

        await browser.close()

    print("\n{}".format("=" * 60))
    print("  DONE — {} new leads saved to {}".format(total_found, LEADS_CSV))
    print("=" * 60)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blue Brick Lead Scraper")
    parser.add_argument(
        "--category", "-c",
        choices=list(CATEGORIES.keys()) + ["all"],
        default="all",
        help="Category to scrape (default: all)",
    )
    parser.add_argument(
        "--max-results", "-m",
        type=int,
        default=20,
        help="Max websites to scrape per category (default: 20)",
    )

    args = parser.parse_args()

    cats = list(CATEGORIES.keys()) if args.category == "all" else [args.category]

    print("\n🧱 Blue Brick Lead Scraper")
    print("   Target: Businesses within 5mi of Waltham, MA 02453")
    print("   Categories: {}".format(", ".join(cats)))
    print("   Max results per category: {}".format(args.max_results))

    asyncio.run(run_scraper(categories=cats, max_results=args.max_results))
