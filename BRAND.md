# Blue Brick — Brand & Project Reference

## About
**Blue Brick Luxury & Commercial Cleaning** is a premium cleaning service operating in the Greater Boston Area. The business targets affluent homeowners and commercial property managers who need reliable, high-quality cleaning — especially post-construction, renovation, and luxury residential work.

**Contact:** 781-330-5604 | bluebrickmass@gmail.com

---

## Service Areas
Boston · East Boston · South Boston · Newton · Waltham · Brighton · Allston

## Services
1. Post-Construction Cleanup
2. Renovation Cleanup
3. New Build Final Clean
4. Luxury Residential
5. Commercial Property
6. Move-In / Move-Out

---

## Brand Voice
- **Tone:** Professional, trustworthy, premium
- **Audience:** Affluent homeowners & property managers
- **Style:** Clean, sophisticated language — no fluff or filler
- **Emphasis:** Quality, reliability, attention to detail

## Visual Identity

### Logo System
The brand uses a 3D isometric brick icon with "BLUE BRICK" text and "LUXURY & COMMERCIAL CLEANING" tagline. Available in:

| File | Variant | Use On |
|------|---------|--------|
| `logo-horizontal-white.png` | Blue/dark text, horizontal | Light/white backgrounds |
| `logo-horizontal-dark.png` | White text, horizontal | Dark backgrounds |
| `logo-stacked-white.png` | Blue/dark text, stacked | Light/white backgrounds |
| `logo-stacked-dark.png` | White text, stacked | Dark backgrounds |
| `logo-profile.png` | BB brick icon only | Social media, avatars |
| `favicon-16.png`, `favicon-32.png`, `favicon-180.png` | Favicon variants | Browser tab, bookmarks |
| `email-templates/blue-brick-logo.png` | Blue/dark text, horizontal | Email headers (white bg) |

**Rule:** White font logo on dark backgrounds. Dark/blue font logo on light backgrounds.

### Colors
| Name          | Hex     | Usage                  |
|---------------|---------|------------------------|
| Prussian Blue | #0C1F35 | Primary / backgrounds  |
| Yale Blue     | #1A3A5C | Secondary              |
| Cerulean      | #3D7A9E | Accent blue            |
| Steel Light   | #5A9BBD | Logo accent            |
| Amber         | #ECA400 | CTA / highlight        |
| Cream         | #EAF8BF | Light backgrounds      |

### Typography
- **Display:** Bebas Neue — bold, uppercase headlines
- **Body:** Manrope — clean, professional readability
- **Blog:** Outfit — lighter editorial feel

---

## Tech Stack
| Layer        | Technology             | Notes                        |
|--------------|------------------------|------------------------------|
| Frontend     | HTML5, CSS3, Vanilla JS| No frameworks — fast & light |
| Forms        | Web3Forms API          | 3-step lead capture form     |
| Hosting      | GitHub Pages / Netlify | Static deployment            |
| SEO          | Schema.org markup      | LocalBusiness + Article      |
| Architecture | WAT Framework          | Workflows, Agents, Tools     |

---

## Site Structure

### Pages
| Page              | File                    | Purpose                          |
|-------------------|-------------------------|----------------------------------|
| Landing Page      | `index.html`            | Main lead-gen page with form     |
| Service Areas     | `cities.html`           | City showcase with local copy    |
| Blog Hub          | `blog/index.html`       | Blog post listing                |
| Blog Posts (x7)   | `blog/post-*.html`      | SEO articles per service city    |

### Key Features
- Multi-step lead capture form (Contact > Property > Details)
- 11+ scroll-triggered CSS animations
- IntersectionObserver for reveal effects
- Animated trust counters (100+ projects, 500+ customers)
- Phone number auto-formatting
- Mobile-first responsive design with fluid typography

---

## Tools & Automation

| Tool                     | Type        | Purpose                              | Status  |
|--------------------------|-------------|--------------------------------------|---------|
| SMS Auto-Responder       | Python/AI   | AI-classifies texts, auto-replies    | Active  |
| lookup_contacts.scpt     | AppleScript | Look up contacts by name             | Ready   |
| send_snow_blast.scpt     | AppleScript | iMessage promo blast (19 recipients) | Ready   |
| send_snow_image.scpt     | AppleScript | Send images via Messages             | Ready   |
| Web3Forms Integration    | JS/API      | Form submission handling             | Active  |
| Multi-Step Lead Form     | HTML/JS     | 3-step lead capture                  | Active  |

---

## SEO Strategy
- **Target:** Local long-tail keywords (e.g., "luxury cleaning Boston", "post-construction cleaning Newton")
- **Content:** 7 city-specific blog posts targeting local search intent
- **Markup:** LocalBusiness + Article Schema on every page
- **Performance:** Mobile-first, Core Web Vitals optimized, no frameworks

---

## Marketing Goals
1. **Generate leads** through the website form and phone calls
2. **Rank locally** for cleaning keywords in all 7 service cities
3. **Build trust** through professional design and social proof
4. **Automate outreach** via SMS auto-responder and iMessage campaigns
5. **Scale content** with SEO blog posts targeting long-tail queries

---

## Project Status

### Complete
- Landing page with multi-step form
- 7 SEO blog posts (one per city)
- Service area showcase page
- Brand identity & design system
- Mobile responsiveness + animations
- SMS auto-responder (AI-powered)
- iMessage marketing blasts

### Needs Work
- `workflows/` — No SOPs written yet
- `tools/` — No Python scripts beyond responder logs
- Analytics — Not configured
- Google Business Profile integration
- Review collection system

---

## File Structure
```
BlueBrick/
├── index.html              # Main landing page
├── cities.html             # Service areas page
├── blog/                   # SEO blog posts
│   ├── index.html          # Blog hub
│   └── post-*.html         # 7 city articles
├── assets/images/          # All imagery
│   ├── city images/        # 7 property photos
│   ├── services images/    # 5 service photos
│   └── Luxury apt images/  # 7 stock photos
├── tools/                  # Automation logs & state
├── workflows/              # SOPs (empty)
├── .tmp/                   # AppleScripts & temp files
├── .env                    # API keys
├── CLAUDE.md               # Agent instructions
├── CLAUDE_REFERENCE.md     # WAT architecture guide
├── SKILL.md                # Frontend design guide
└── BRAND.md                # This file
```
