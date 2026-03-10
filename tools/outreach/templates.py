"""
Blue Brick Outreach — Email Templates
--------------------------------------
Personalized cold emails for each industry vertical.
Each template uses {placeholders} for personalization.
"""

TEMPLATES = {
    "realtors": {
        "subject": "Cleaning partner for your listings — Blue Brick",
        "body": """\
Hi {first_name},

I'm Gerardo with Blue Brick Luxury & Commercial Cleaning. We work with realtors across the Greater Boston area to make sure properties are spotless for showings, open houses, and closings.

What we handle for agents like you:
• Move-in / move-out deep cleans
• Pre-listing detail cleaning
• Post-renovation and construction cleanup
• Ongoing maintenance for vacant properties

We're based in Waltham and cover Boston, Newton, Brighton, South Boston, East Boston, and Allston. Our team is insured, reliable, and understands that presentation sells homes.

If you ever need a fast turnaround clean before a showing — or a reliable partner for your listings — I'd love to connect.

Happy to do a complimentary walkthrough on your next property.

Best,
Gerardo
Blue Brick Luxury & Commercial Cleaning
781-330-5604
bluebrickmass@gmail.com
""",
    },

    "interior_designers": {
        "subject": "Post-renovation cleanup for your projects — Blue Brick",
        "body": """\
Hi {first_name},

I'm Gerardo with Blue Brick Luxury & Commercial Cleaning. I'm reaching out because we specialize in the kind of cleanup that happens after the design work is done — post-renovation, post-construction, and final detail cleaning.

We know that dust, debris, and construction residue can undermine weeks of beautiful design work. That's where we come in.

What we do for design firms:
• Post-renovation deep cleaning (dust, grout haze, adhesive removal)
• Final walkthrough cleaning before client reveals
• Window, fixture, and surface detailing
• Ongoing maintenance for completed projects

We cover the Greater Boston area — Waltham, Newton, Brighton, Boston, South Boston, East Boston, and Allston. Fully insured and detail-oriented.

If you'd like a cleaning partner who treats your projects with the same care you put into them — let's talk.

Best,
Gerardo
Blue Brick Luxury & Commercial Cleaning
781-330-5604
bluebrickmass@gmail.com
""",
    },

    "daycares": {
        "subject": "Professional cleaning for your facility — Blue Brick",
        "body": """\
Hi {first_name},

I'm Gerardo with Blue Brick Luxury & Commercial Cleaning. We provide professional commercial cleaning for childcare facilities in the Greater Boston area, and I wanted to see if you're happy with your current cleaning provider.

We understand that cleanliness in a daycare isn't just about appearances — it's about safety. Parents notice, licensing inspectors notice, and kids deserve a healthy environment.

What we offer:
• Daily or weekly deep cleaning programs
• Sanitization of high-touch surfaces, play areas, and restrooms
• Floor care, window cleaning, and kitchen/break room cleaning
• Flexible scheduling — evenings and weekends so we never disrupt your day

We're based in Waltham and serve the surrounding area. Fully insured, background-checked team, and we use child-safe cleaning products.

If you're open to a quick conversation — or want a free walkthrough and quote — I'd love to hear from you.

Best,
Gerardo
Blue Brick Luxury & Commercial Cleaning
781-330-5604
bluebrickmass@gmail.com
""",
    },

    "contractors": {
        "subject": "Post-construction cleanup crew — Blue Brick",
        "body": """\
Hi {first_name},

I'm Gerardo with Blue Brick Luxury & Commercial Cleaning. We do post-construction and renovation cleanup across the Greater Boston area, and I'm looking to connect with contractors who could use a reliable cleanup crew.

Here's the deal — you finish the build, we make it move-in ready. No leftover dust, no smudged windows, no drywall residue. Just a clean handoff to your client.

What we handle:
• Full post-construction deep cleaning
• Dust removal from every surface, vent, and fixture
• Window and glass cleaning (interior + exterior)
• Floor scrubbing, grout cleaning, final detail work
• Debris removal and haul-away coordination

We've cleaned after new builds, gut renovations, and everything in between. Based in Waltham, covering Boston, Newton, Brighton, South Boston, East Boston, and Allston.

If you've got a project wrapping up — or want to set up an ongoing partnership — let's connect. Happy to come see a job site.

Best,
Gerardo
Blue Brick Luxury & Commercial Cleaning
781-330-5604
bluebrickmass@gmail.com
""",
    },

    "property_managers": {
        "subject": "April turnovers coming up? We handle the cleaning — Blue Brick",
        "body": """\
Hi {first_name},

I'm Gerardo with Blue Brick Luxury & Commercial Cleaning, based right here in Waltham.

With April 1 lease turnovers around the corner, I wanted to reach out. We specialize in move-in/move-out cleaning for property managers — fast turnarounds so your units are ready for the next tenant without delays.

What we do for property managers:
• Move-out deep cleaning (appliances, bathrooms, floors, walls)
• Move-in ready detailing
• Multi-unit turnover batches — we can handle volume
• Post-renovation and construction cleanup
• Recurring common area maintenance

We're local, insured, and built for the kind of turnaround speed that April demands. We've worked with managers across Waltham, Newton, Watertown, Cambridge, and Brookline.

If you've got units turning over — or want to set up a standing partnership — text me anytime. Happy to walk a property and give you a same-day quote.

Best,
Gerardo
Blue Brick Luxury & Commercial Cleaning
781-330-5604 (text preferred)
bluebrickmass@gmail.com
""",
    },

    "restaurants": {
        "subject": "Deep cleaning for your restaurant — Blue Brick",
        "body": """\
Hi {first_name},

I'm Gerardo with Blue Brick Luxury & Commercial Cleaning. We provide professional deep cleaning for restaurants and food service businesses in the Greater Boston area.

We know kitchens, dining areas, and restrooms take a beating — and regular staff cleaning only goes so far. That's where we come in.

What we offer restaurants:
• Kitchen deep cleaning (hoods, grease traps, behind equipment)
• Dining room and restroom deep sanitization
• Floor stripping and refinishing
• Pre-inspection and health code prep cleaning
• One-time deep cleans or recurring weekly/monthly programs

We're based in Waltham and serve Moody Street, Watertown, Newton, Cambridge, and beyond. Flexible scheduling — we work around your hours so there's zero disruption to service.

If you're looking for a reliable cleaning crew — or have an inspection coming up — text me and I'll come take a look.

Best,
Gerardo
Blue Brick Luxury & Commercial Cleaning
781-330-5604 (text preferred)
bluebrickmass@gmail.com
""",
    },

    "airbnb_hosts": {
        "subject": "Turnover cleaning for your rental — Blue Brick",
        "body": """\
Hi {first_name},

I'm Gerardo with Blue Brick Luxury & Commercial Cleaning. We do turnover cleaning for short-term rental hosts in the Greater Boston area — Airbnb, Vrbo, and furnished rentals.

I know guest turnovers are time-sensitive. You need someone who shows up on schedule, cleans to hotel standards, and doesn't miss details that lead to bad reviews.

What we handle:
• Same-day turnover cleaning between guests
• Linen change and bed making
• Kitchen and bathroom deep sanitization
• Restocking essentials (if needed)
• Consistent quality every single time

We're based in Waltham and cover a 12-mile radius — Newton, Cambridge, Brookline, Watertown, Somerville, and more. Local means fast response when you get a last-minute booking.

If you're managing rentals and need a reliable cleaning partner — or want to stop doing turnovers yourself — text me. Happy to do a trial clean.

Best,
Gerardo
Blue Brick Luxury & Commercial Cleaning
781-330-5604 (text preferred)
bluebrickmass@gmail.com
""",
    },
}


def get_template(category: str) -> dict:
    """Get email template for a category."""
    return TEMPLATES.get(category, TEMPLATES["realtors"])


def personalize(template: dict, lead: dict) -> dict:
    """Fill in placeholders from lead data."""
    first_name = lead.get("business_name", "").split()[0] if lead.get("business_name") else "there"

    # If the first word looks like a business name (not a person), use generic
    if first_name.lower() in {"the", "a", "an", ""} or len(first_name) <= 1:
        first_name = "there"

    return {
        "subject": template["subject"].format(first_name=first_name),
        "body": template["body"].format(first_name=first_name),
    }
