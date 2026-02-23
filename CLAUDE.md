# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution.

## Project: Blue Brick — Luxury & Commercial Cleaning

**Brand:** Blue Brick Luxury and Commercial Cleaning
**Location:** Greater Boston Area (Boston, East Boston, South Boston, Newton, Waltham, Brighton, Allston)
**Contact:** 7813305604 | bluebrickmass@gmail.com
**Focus:** Lead generation for luxury residential and commercial cleaning services

### Brand Voice
- Professional, trustworthy, premium
- Speak to affluent homeowners and property managers
- Emphasize quality, reliability, attention to detail
- Use clean, sophisticated language — no fluff

### Tech Stack
- Static HTML/CSS/JS (single-page landing + blog)
- No frameworks — fast, lightweight, SEO-first
- Hosted via GitHub Pages or Netlify

### SEO Strategy
- Target local keywords: "luxury cleaning Boston", "commercial cleaning Newton", "house cleaning South Boston", etc.
- Blog content targeting long-tail local queries
- Schema markup for LocalBusiness
- Mobile-first, Core Web Vitals optimized

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases

**Layer 2: Agents (The Decision-Maker)**
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- Credentials and API keys are stored in `.env`

## File Structure

```
.tmp/           # Temporary files. Regenerated as needed.
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs defining what to do and how
blog/           # Blog post HTML files for SEO
assets/         # Images, icons, fonts
.env            # API keys and environment variables
```

## Bottom Line

Stay pragmatic. Stay reliable. Keep learning.
