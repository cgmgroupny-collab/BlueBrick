"""
Blue Brick Outreach — Configuration
Target: Businesses across 15 Greater Boston service cities
"""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Directories
OUTREACH_DIR = Path(__file__).parent
DATA_DIR = OUTREACH_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Output files
LEADS_CSV = DATA_DIR / "leads.csv"
SENT_LOG = DATA_DIR / "sent_log.csv"

# Gmail SMTP
GMAIL_USER = os.getenv("GMAIL_USER", "bluebrickmass@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")  # Google App Password required

# Search targets
ZIP_CODE = "02453"
LOCATION = "Waltham, MA"
RADIUS = "15 miles"

# All 15 service cities
SERVICE_CITIES = [
    "Waltham", "Newton", "Cambridge", "Brookline", "Somerville",
    "Brighton", "Watertown", "Boston", "South Boston", "East Boston",
    "Allston", "Lexington", "Needham", "Wellesley", "Weston",
]

CATEGORIES = {
    "property_managers": [
        # Priority 1 — April turnovers, recurring revenue
        "property management companies Waltham MA",
        "apartment management Waltham MA",
        "rental property managers near 02453",
        "property management Newton MA",
        "property management Cambridge MA",
        "property management Brookline MA",
        "property management Somerville MA",
        "apartment management Somerville MA",
        "property management Watertown MA",
        "property management Boston MA",
        "property management South Boston MA",
        "condo management Brighton Allston MA",
        "landlord services Needham Wellesley MA",
        "rental property managers Lexington Weston MA",
        "property management companies near Boston MA",
    ],
    "contractors": [
        # Priority 2 — Highest ticket, steady pipeline
        "general contractors Waltham MA",
        "home renovation contractors Waltham MA",
        "construction companies Waltham Newton MA",
        "kitchen remodeling contractors Waltham MA",
        "bathroom remodeling Waltham Newton MA",
        "general contractors Watertown MA",
        "general contractors Cambridge MA",
        "general contractors Brookline MA",
        "home renovation contractors Newton MA",
        "construction companies Lexington Weston MA",
        "general contractors Somerville MA",
        "home renovation contractors Boston MA",
        "construction companies South Boston East Boston MA",
        "general contractors Brighton Allston MA",
        "home renovation contractors Needham Wellesley MA",
    ],
    "restaurants": [
        # Priority 3 — Recurring deep cleans, health inspections
        "Moody Street restaurants Waltham",
        "Italian restaurant Waltham MA",
        "Indian restaurant Waltham MA",
        "pizza restaurant Waltham MA",
        "Thai restaurant Waltham MA",
        "restaurant Watertown MA",
        "restaurant Newton MA",
        "restaurant Cambridge MA",
        "restaurant Brookline MA",
        "restaurant Somerville MA",
        "restaurant Brighton MA",
        "restaurant South Boston MA",
        "restaurant East Boston MA",
        "restaurant Allston MA",
        "bakery cafe Waltham Watertown MA",
        "restaurant Needham Wellesley MA",
    ],
    "realtors": [
        # Priority 4 — Listing prep, referral network
        "real estate agents near Waltham MA",
        "realtors in Waltham MA",
        "real estate brokers Newton MA",
        "realtors near 02453",
        "realtors Watertown Brookline MA",
        "real estate agents Cambridge MA",
        "realtors Somerville MA",
        "real estate agents Lexington Weston MA",
        "realtors Needham Wellesley MA",
        "real estate agents Brighton Allston MA",
        "realtors South Boston MA",
        "real estate agents Boston MA",
    ],
    "airbnb_hosts": [
        # Priority 5 — Same-day turnover, recurring
        "Airbnb property manager Waltham MA",
        "short term rental management Waltham MA",
        "vacation rental property manager near 02453",
        "Airbnb cleaning service Waltham Newton MA",
        "short term rental host Cambridge Brookline MA",
        "Airbnb property manager Boston MA",
        "short term rental management Somerville MA",
        "Airbnb host South Boston MA",
        "vacation rental manager Brighton Allston MA",
    ],
    "daycares": [
        # Priority 6 — Safety angle, recurring weekly
        "daycare centers near Waltham MA",
        "childcare centers Waltham MA",
        "preschools near 02453",
        "daycare centers Watertown Newton MA",
        "daycare centers Brookline MA",
        "childcare centers Cambridge Somerville MA",
        "preschools Needham Wellesley MA",
        "daycare centers Brighton Allston MA",
        "childcare centers Lexington MA",
    ],
    "interior_designers": [
        # Priority 7 — Niche, high-margin
        "interior designers near Waltham MA",
        "interior design firms Waltham Newton MA",
        "home staging companies near 02453",
        "interior designers Cambridge Brookline MA",
        "interior design firms Boston MA",
        "home staging companies Wellesley Needham MA",
        "interior designers Lexington Weston MA",
    ],
}

# Brand
BRAND = {
    "name": "Blue Brick Luxury & Commercial Cleaning",
    "phone": "781-330-5604",
    "email": "bluebrickmass@gmail.com",
    "website": "https://bluebrickmass.com",
    "address": "Waltham, MA",
    "areas": "Greater Boston — Waltham, Newton, Watertown, Cambridge, Brookline, Somerville, Lexington, Weston, Brighton, Allston, Boston, South Boston, East Boston, Needham, Wellesley",
}

# Rate limiting
SCRAPE_DELAY_MIN = 5  # seconds between page loads
SCRAPE_DELAY_MAX = 10
EMAIL_DELAY_MIN = 30  # seconds between emails
EMAIL_DELAY_MAX = 90
MAX_EMAILS_PER_DAY = 50  # stay well under Gmail's 500 limit
