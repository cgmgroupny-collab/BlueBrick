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

We're based in Waltham and cover 15 cities across Greater Boston — Newton, Cambridge, Brookline, Somerville, Watertown, Lexington, Wellesley, and more. Our team is insured, reliable, and understands that presentation sells homes.

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

We cover 15 cities across Greater Boston — Waltham, Newton, Cambridge, Brookline, Wellesley, Lexington, and more. Fully insured and detail-oriented.

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

We're based in Waltham and serve 15 cities across Greater Boston — Newton, Cambridge, Brookline, Somerville, Watertown, Needham, Lexington, and more. Fully insured, background-checked team, and we use child-safe cleaning products.

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

We've cleaned after new builds, gut renovations, and everything in between. Based in Waltham, covering 15 cities across Greater Boston — Newton, Cambridge, Brookline, Somerville, Lexington, and more.

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

We're local, insured, and built for the kind of turnaround speed that April demands. We've worked with managers across Waltham, Newton, Watertown, Cambridge, Brookline, Somerville, and 9 more Greater Boston cities.

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

We're based in Waltham and serve 15 cities across Greater Boston — Watertown, Newton, Cambridge, Brookline, Somerville, Brighton, and more. Flexible scheduling — we work around your hours so there's zero disruption to service.

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

We're based in Waltham and cover 15 cities across Greater Boston — Newton, Cambridge, Brookline, Watertown, Somerville, Brighton, and more. Local means fast response when you get a last-minute booking.

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


# HTML email wrapper with branded banner and CTA
def wrap_html(body_text: str) -> str:
    """Wrap plain text email body in a branded HTML email with banner and CTA."""
    # Convert plain text body to HTML paragraphs
    lines = body_text.strip().split("\n")
    html_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            html_lines.append("")
            continue
        if line.startswith("•"):
            html_lines.append(
                f'<tr><td style="padding:2px 0 2px 8px;font-size:15px;color:#333333;">'
                f'{line}</td></tr>'
            )
            continue
        html_lines.append(
            f'<p style="margin:0 0 10px;font-size:15px;line-height:1.6;color:#333333;">'
            f'{line}</p>'
        )

    # Separate bullet items into a table
    body_html_parts = []
    in_bullets = False
    for h in html_lines:
        if "<tr>" in h:
            if not in_bullets:
                body_html_parts.append(
                    '<table role="presentation" cellpadding="0" cellspacing="0" '
                    'style="margin:8px 0 12px 12px;">'
                )
                in_bullets = True
            body_html_parts.append(h)
        else:
            if in_bullets:
                body_html_parts.append("</table>")
                in_bullets = False
            body_html_parts.append(h)
    if in_bullets:
        body_html_parts.append("</table>")

    body_html = "\n".join(body_html_parts)

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;">
<tr><td align="center" style="padding:20px 10px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:4px;overflow:hidden;">

  <!-- Banner Header -->
  <tr>
    <td style="background:#001D4A;padding:28px 32px 24px;text-align:center;">
      <h1 style="margin:0;font-family:Georgia,'Times New Roman',serif;font-size:32px;font-weight:700;letter-spacing:3px;color:#ffffff;">
        BLUE <span style="color:#ECA400;">BRICK</span>
      </h1>
      <p style="margin:6px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#8aa8c7;">
        Luxury &amp; Commercial Cleaning
      </p>
    </td>
  </tr>

  <!-- Gold accent bar -->
  <tr>
    <td style="height:4px;background:linear-gradient(90deg,#ECA400,#f4be3a,#ECA400);font-size:0;line-height:0;">&nbsp;</td>
  </tr>

  <!-- Email Body -->
  <tr>
    <td style="padding:32px 36px 24px;font-family:Arial,Helvetica,sans-serif;">
      {body_html}
    </td>
  </tr>

  <!-- CTA Button -->
  <tr>
    <td align="center" style="padding:8px 36px 32px;">
      <table role="presentation" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background:#ECA400;border-radius:4px;">
            <a href="https://bluebrickmass.com/#estimate"
               style="display:inline-block;padding:14px 36px;font-family:Arial,Helvetica,sans-serif;font-size:15px;font-weight:700;color:#001D4A;text-decoration:none;letter-spacing:1px;">
              REQUEST A FREE ESTIMATE
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="background:#001D4A;padding:20px 32px;text-align:center;">
      <p style="margin:0 0 4px;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#ffffff;">
        <a href="tel:7813305604" style="color:#ECA400;text-decoration:none;font-weight:600;">781-330-5604</a>
        &nbsp;&middot;&nbsp;
        <a href="mailto:bluebrickmass@gmail.com" style="color:#ECA400;text-decoration:none;font-weight:600;">bluebrickmass@gmail.com</a>
      </p>
      <p style="margin:8px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#5a7a9a;">
        Waltham, MA &middot; Insured &middot; 15 Cities Across Greater Boston
      </p>
      <p style="margin:10px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:10px;color:#3d5a7a;">
        To stop receiving emails, reply with "unsubscribe".
      </p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""


def personalize(template: dict, lead: dict) -> dict:
    """Fill in placeholders from lead data."""
    first_name = lead.get("business_name", "").split()[0] if lead.get("business_name") else "there"

    # If the first word looks like a business name (not a person), use generic
    if first_name.lower() in {"the", "a", "an", ""} or len(first_name) <= 1:
        first_name = "there"

    body = template["body"].format(first_name=first_name)

    return {
        "subject": template["subject"].format(first_name=first_name),
        "body": body,
        "html": wrap_html(body),
    }
