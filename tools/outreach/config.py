"""
Blue Brick Outreach — Configuration
Target: Businesses within 12mi of Waltham, MA 02453
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
RADIUS = "12 miles"

CATEGORIES = {
    "realtors": [
        "real estate agents near Waltham MA",
        "realtors in Waltham MA",
        "real estate brokers Newton Waltham MA",
        "realtors near 02453",
        "realtors Watertown Brookline Cambridge MA",
        "real estate agents Lexington Weston MA",
    ],
    "interior_designers": [
        "interior designers near Waltham MA",
        "interior design firms Waltham Newton MA",
        "home staging companies near 02453",
        "interior designers Cambridge Brookline MA",
    ],
    "daycares": [
        "daycare centers near Waltham MA",
        "childcare centers Waltham MA",
        "preschools near 02453",
        "daycare centers Watertown Newton Brookline MA",
    ],
    "contractors": [
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
    ],
    "property_managers": [
        "property management companies Waltham MA",
        "apartment management Waltham MA",
        "rental property managers near 02453",
        "property management Newton Waltham MA",
        "landlord services Waltham MA",
        "condo management Waltham MA",
        "property management Watertown Cambridge Brookline MA",
        "apartment management Somerville MA",
    ],
    "restaurants": [
        "Moody Street restaurants Waltham",
        "Italian restaurant Waltham MA",
        "Indian restaurant Waltham MA",
        "pizza restaurant Waltham MA",
        "Thai restaurant Waltham MA",
        "restaurant Watertown MA",
        "restaurant Newton MA",
        "restaurant Cambridge MA Mass Ave",
        "restaurant Brookline MA",
        "bakery cafe Waltham MA",
    ],
    "airbnb_hosts": [
        "Airbnb property manager Waltham MA",
        "short term rental management Waltham MA",
        "vacation rental property manager near 02453",
        "Airbnb cleaning service Waltham Newton MA",
        "short term rental host Cambridge Brookline MA",
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
