"""
Blue Brick Facebook Automation — Configuration
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Paths
BASE_DIR = Path(__file__).parent
ADS_DIR = BASE_DIR / "ads"
DATA_DIR = BASE_DIR / "data"
SESSION_FILE = DATA_DIR / "fb_session.json"
GROUPS_FILE = DATA_DIR / "groups.json"

# Facebook credentials
FB_EMAIL = os.getenv("FB_EMAIL", "")
FB_PASSWORD = os.getenv("FB_PASSWORD", "")

# Timing — 10 groups in ~15 minutes
POST_DELAY_MIN = 60       # seconds between group posts (minimum)
POST_DELAY_MAX = 120      # seconds between group posts (maximum)
TYPING_DELAY_MIN = 30     # ms between keystrokes
TYPING_DELAY_MAX = 120    # ms between keystrokes
WARMUP_SCROLLS = 3        # scroll news feed before posting

# Browser
VIEWPORT = {"width": 1366, "height": 768}
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
TIMEZONE = "America/New_York"
GEOLOCATION = {"latitude": 42.3601, "longitude": -71.0589}  # Boston

# Group finder keywords — targeting Blue Brick's audience
SEARCH_KEYWORDS = [
    "Boston homeowners",
    "Boston moms group",
    "Boston real estate",
    "Newton MA community",
    "South Boston neighbors",
    "East Boston community",
    "Waltham MA neighbors",
    "Brighton Allston community",
    "Boston pet owners",
    "Greater Boston families",
    "Boston realtors network",
    "Boston single moms",
    "Boston cleaning recommendations",
    "Boston home services",
    "Massachusetts homeowners",
]

# Post content variations — mix and match to avoid duplicate detection
POST_GREETINGS = [
    "Hi everyone!",
    "Hello neighbors!",
    "Hey folks,",
    "Hi there,",
    "Good day everyone!",
    "Hello!",
]

POST_CLOSINGS = [
    "Feel free to reach out anytime!",
    "Happy to answer any questions.",
    "DM me or call anytime!",
    "Would love to help — just reach out!",
    "Message me for a free quote!",
]

# Brand info for posts
BRAND = {
    "name": "Blue Brick Luxury & Commercial Cleaning",
    "phone": "781-330-5604",
    "email": "bluebrickmass@gmail.com",
    "areas": "Greater Boston (Boston, Newton, Waltham, Brighton, South Boston, East Boston)",
}


def load_groups():
    """Load saved groups list."""
    if GROUPS_FILE.exists():
        with open(GROUPS_FILE) as f:
            return json.load(f)
    return []


def save_groups(groups):
    """Save groups list."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(GROUPS_FILE, "w") as f:
        json.dump(groups, f, indent=2)
