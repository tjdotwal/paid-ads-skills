---
name: google-ads-campaign-build
description: |
  Build, restructure, or audit new Google Ads search campaigns for the brand. Use this skill whenever asked to "build a campaign," "create new ad groups," "restructure an account," "set up a new campaign," "launch a new campaign," "build out campaigns," or any task that involves creating new campaign structures, ad groups, keywords, RSAs, or budgets from scratch. Also trigger when the user provides performance data and asks for a new campaign structure or account restructure. This skill covers the full workflow from campaign architecture through QA — it is NOT for search term mining (use mine-search-terms for that) but IS for everything that comes after the analysis: building the actual campaigns. Load the naming-conventions skill alongside this one to interpret existing account structure.
version: 1.0.0
---

# Google Ads Campaign Build

This skill defines how to build new Google Ads search campaigns. It captures the full workflow from campaign architecture through go-live QA, based on real build patterns and lessons learned from real account work.

The goal is to build campaigns that are tightly themed, budget-conscious, and ready to perform from day one — not bloated structures that need weeks of cleanup.

## Before You Start

1. **Load the naming-conventions skill** to understand the naming taxonomy (pipe-delimited campaign names, ad group naming patterns)
   - Confirm the target account. `list_accounts` returns numeric IDs only, so resolve from `GOOGLE_ADS_CUSTOMER_ID` or ask. If the account sits under a manager account, pass `login_customer_id` (see naming-conventions "## Account Targeting").
2. **Pull existing ad creatives** from the account to extract brand voice, landing page URLs, and value propositions — never write ad copy in a vacuum
3. **Confirm budget** with the user — this drives everything else (how many campaigns, how many ad groups, match type aggression)

## Campaign Architecture Principles

### Tight Theming Over Keyword Volume

The single biggest mistake in Google Ads builds is cramming too many keywords into too few ad groups. Every ad group should have one clear intent theme. If you can't write a single RSA that speaks directly to every keyword in the ad group, the ad group is too broad.

**Good:** An ad group called "managed-it-services" with 4-5 exact match keywords all about managed IT services
**Bad:** An ad group called "Managed IT Services" with 98 keywords spanning managed IT, cybersecurity, local IT support, and small business IT

### Budget Dictates Structure

With limited budgets (~$3k/month or less), consolidate aggressively. It's better to have 1 well-funded campaign with 4 tightly themed ad groups than 3 underfunded campaigns fighting each other. When consolidating:

- Combine campaigns that share geo targeting and audience intent
- Add the budgets together when merging (don't lose the spend allocation)
- Recreate ad groups and their full contents (keywords, RSAs) in the surviving campaign — you can't move ad groups between campaigns in Google Ads

### Budget Math

Daily budget × 30.4 = approximate monthly spend. Always verify the math adds up to the brand's approved monthly budget. Present this to the user for confirmation.

## Build Workflow

### Step 1: Create Campaign Budgets

Create individual daily budgets for each campaign. Avoid shared budgets when using automated bid strategies (MAXIMIZE_CONVERSIONS is incompatible with shared budgets).

### Step 2: Create Ad Groups

Name ad groups using lowercase-kebab-case that reflects the keyword theme: `it-support-near-me`, `managed-it-services`, `cybersecurity-for-business`.

Set a default CPC bid at the ad group level. This serves as the fallback — individual keywords can override with their own bids.

### Step 3: Add Keywords

#### Match Type Strategy

Start tight, expand later. With limited budgets, exact match gives you the most control over spend.

**Exact match** is the default for:
- High-intent BOFU keywords ("managed it services," "cybersecurity services near me")
- Keywords where you want precise query control
- Any keyword where the complete phrase IS the search intent

**Phrase match** is appropriate for:
- Geo-modified keywords ("it services temecula," "cybersecurity temecula") — because you want to catch "best it services temecula," "top rated it services temecula ca," etc.
- Keywords where natural pre/post modifiers add value without changing intent

**Broad match** — avoid on tight budgets unless the user specifically requests it. Broad is a budget burner in competitive spaces.

When the user asks for "just exact" or "start with exact only," respect that and save phrase/broad for a later expansion phase.

#### CPC Bid Tiering

If you don't have historical CPC data from the account, flag this to the user. If you need to set initial bids, tier them by intent value:

- **Top tier** — highest-intent, money keywords (the core service terms)
- **Mid tier** — strong intent but longer tail or less direct
- **Lower tier** — niche terms, adjacent intent

Always tell the user you set bids without auction data and recommend they check Keyword Planner or historical CPCs to calibrate. Don't present your bid tiers as data-driven when they're logic-driven.

### Step 4: Create RSAs

#### Headlines (15 per ad, max 30 characters each)

Always use all 15 headline slots. This gives Google maximum combinations to test and optimize.

**Use Title Case** — capitalize all major words, lowercase minor words (in, for, of, a, the, and, to, with) unless they're the first word.

Good: "Get a Free IT Assessment"
Bad: "Get A Free IT Assessment"

Build headlines in three categories of 5:

**5 × Keyword-Focused Headlines** — Mirror the ad group's core keywords and close variations. These drive relevance and Quality Score.
- "Managed IT Services"
- "Managed IT Service Provider"
- "Managed IT Solutions"
- "Full-Service Managed IT"
- "Managed IT for Business"

**5 × Benefit/Outcome/Pain-Solving Headlines** — What the prospect gets or what problem goes away. Speak to the result, not the feature.
- "24/7 IT Monitoring & Support"
- "Under 5 Min Response Times"
- "No Long Term Contracts"
- "Protect Your Business 24/7"
- "Transparent IT Pricing"

**5 × Brand/CTA Headlines** — Drive action and establish who you are.
- "Get a Free IT Assessment"
- "Book a Free Consultation"
- "27+ Years of IT Expertise"
- "Vertex IT - Temecula CA"
- "Your Trusted IT Partner"

#### Descriptions (4 per ad, max 90 characters each)

Keep under 90 characters — this is a hard limit and the API will reject anything over. Write the description, then count characters before pushing.

Build descriptions in two categories of 2:

**2 × Outcome-Focused Descriptions** — What the user gets after engaging with the service. Paint the after-state.
- "Enterprise-level managed IT without the enterprise cost. No contracts required."
- "Stop firefighting IT issues. Get proactive managed services. Free assessment."

**2 × How-Focused Descriptions** — The unique mechanisms, features, and differentiators for how the brand delivers the outcome.
- "Proactive managed IT services from Vertex IT. 27+ years protecting businesses."
- "Managed IT that keeps your business running smoothly. Transparent pricing."

Pull language from existing ads in the account to maintain brand voice consistency.

#### Display Path URLs

Set display paths using the ad group's keyword theme, split across two paths:

- `managed-it-services` ad group → display path: `Managed-IT / Services`
- `it-support-near-me` ad group → display path: `IT-Support / Near-Me`
- `cybersecurity-for-business` ad group → display path: `Cybersecurity / Business`

Note: The Google Ads API may not support display path creation via all tools. If the API returns a `display_url` error, skip paths and flag for manual addition.

#### Landing Page URLs

Pull landing page URLs from existing ads in the account. Match the landing page to the ad group theme — don't send managed IT traffic to a cybersecurity page. Include UTM parameters for tracking.

### Step 5: Add Negative Keywords

Add campaign-level negatives to all active campaigns. Standard negatives for most B2B/service accounts:

- **Job seekers**: jobs, salary, career, hiring, resume
- **Education seekers**: course, certification, training, degree, "how to become"
- **Informational**: "what is" (phrase match)
- **Freebie seekers**: free (but CHECK for conflicts — if the brand offers "free assessments" and that's part of their funnel, this negative might block qualified traffic. Discuss with the user.)

After adding negatives, always do a **conflict check**: do any negatives block keywords or searches you're actively targeting? Flag any conflicts to the user.

### Step 6: Pause Legacy Elements

When restructuring, pause old elements to prevent cannibalization:
- Pause all keywords in old ad groups (do this via API)
- Pause the old ad groups themselves (may need manual step)
- If consolidating campaigns, pause the deprecated campaign after recreating its contents in the surviving campaign

### Step 7: Verification Scan

Run a full GAQL scan after all changes and verify:
- All campaigns at correct status (ENABLED/PAUSED as intended)
- All new ad groups ENABLED
- All new keywords ENABLED
- All new RSAs ENABLED (common miss — they default to PAUSED)
- Budget amounts correct
- Negative keywords present on all intended campaigns
- Old/legacy elements properly paused

Run this scan at least once. If the user made manual changes, run it again to confirm.

### Step 8: Flag Manual Steps

Some things can't be done via API and need to be flagged for the user to do in the Google Ads UI:

- Geo targeting changes (location radius, presence vs interest settings)
- Display path URLs (if API doesn't support)
- Ad extensions (sitelinks, callouts, call assets, location extensions)
- Search/display network settings
- Auto-recommendation settings
- Enabling/pausing specific ad groups in campaigns you didn't create

Always give the user **exact campaign and ad group names** for manual steps — never just IDs.

## QA Checklist

After the build is complete, walk through this checklist. See `references/qa-checklist.md` for the full version.

Critical items:
1. Ad copy in Title Case with display paths set?
2. Keywords using intentional match types (documented reasoning)?
3. Negative keyword conflict check passed?
4. Final URLs accurate and landing pages live?
5. Budget math checks out (daily × 30.4 = monthly target)?
6. Geo targeting correct?
7. Extensions added (sitelinks, callouts, call assets)?
8. Search network only (display network OFF)?
9. Auto-recommendations turned OFF?
10. Conversion tracking firing?
11. All new elements at correct status (not accidentally paused)?

## Common Pitfalls

These are things that have caused real issues in real builds:

- **MAXIMIZE_CONVERSIONS + shared budgets** — these are incompatible. Use individual budgets.
- **Campaign creation via API may require `contains_eu_political_advertising` field** in v23+. If campaign creation fails, pivot to repurposing existing paused campaigns (Option A).
- **Negative keywords that are actually negatives show up as "keywords" in GAQL** — if you try to pause them via `update_keyword_status`, you'll get a `CANT_UPDATE_NEGATIVE` error. Remove those from your batch and retry.
- **RSAs default to PAUSED** when created via API. Always verify ad status after creation.
- **Display path URLs via API** may throw a `VALUE_MUST_BE_UNSET` error on the `display_url` field. Skip and flag for manual addition.
- **90-character description limit** is strictly enforced. Count characters before pushing. Common offenders are descriptions that run 92-95 characters — trim before submitting.
- **"Near me" keywords with narrow geo targeting** — if the campaign targets only a specific city, "near me" keywords will match based on the user's location + the geo target. Expand geo targeting (e.g., 25-mile radius) when using "near me" keywords.
