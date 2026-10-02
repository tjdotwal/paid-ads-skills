---
name: keyword-research
description: >
  Use this skill when the user asks to "research keywords", "find keyword ideas",
  "discover new keywords", "check search volume", "validate keywords",
  "what keywords should we target", "expand our keyword list", "find new keywords
  for this campaign", "keyword research for [brand]", "what themes should we target",
  or any task involving keyword discovery or search volume analysis using Google Ads
  Keyword Planner data. Also trigger when the user is starting a new campaign build
  and needs keyword themes, or wants to go deeper on an existing campaign's keywords.
version: 1.0.0
---

# Keyword Research Workflow

Three use cases trigger keyword research. Identify which one applies before starting.

## Use Case 1: New Campaign Build (Greenfield)

The most structured path. Triggered when a new brand comes in or an existing client needs a new campaign.

### Step 1: Identify the Core Service AND the Geo Footprint

Get the brand's website, strategy doc, or messaging brief. Identify two things before touching Keyword Planner:

1. **The core service.** The offering the brand most wants leads for.
2. **The geo footprint.** One city, multiple cities, or national. This determines the campaign structure, not just the keyword list. Ask the user explicitly if the brief doesn't make it obvious.

Start from the bottom of the funnel. Find the highest-intent, most commercial way someone would search for that core service. This becomes the anchor keyword theme.

Example: Roofing company in Saskatoon whose main goal is roof replacement leads. The anchor theme is "roof replacement" — not "roofing" (too broad), not "roof replacement insurance claim" (different funnel stage).

### Step 2: Generate Keywords Under the Theme

Call `generate_keyword_ideas` with the anchor term as the seed keyword.

**For multi-geo clients, seed Keyword Planner once per city.** Generic seeds (e.g., "screen printing") return US/national volume, which is useless for Canadian local services. Seed with `[anchor term] [city]` to get real city-level volume from Keyword Planner's Canadian data. Do this for every target city before moving on.

From the results, pull ~10 tight keywords that ALL share the same purchase intent: the searcher has already decided they need this service and is looking to hire someone.

Filter by:
- **Intent first, volume second.** A 50,000-volume keyword with informational intent is worth less than a 500-volume keyword with buying intent. The question for every keyword: "Is this person looking to pay a company like our client to get this service?"
- **Same funnel stage.** Every keyword under the theme must match the same purchase intent. Keywords that signal a different stage get flagged for a separate campaign, not added here.

Intent signals that DO NOT belong in a bottom-of-funnel theme:
- DIY / how-to intent ("roof replacement DIY", "how to replace a roof") — they want to do it themselves
- Insurance/claims intent ("roof replacement insurance claim") — still figuring out how to pay, separate campaign
- Informational ("roof replacement cost", "how long does roof replacement take") — researching, not buying yet
- Job-seeking ("roof replacement jobs", "roofing contractor hiring") — not a customer

Intent signals that DO belong:
- Service + location ("roof replacement Saskatoon")
- Service + company/contractor modifier ("roof replacement company near me", "roof replacement contractors")
- Service + action modifier ("get my roof replaced", "redo my roof")
- Service + qualifier ("best roof replacement", "licensed roof replacement contractor")

The geo modifier (e.g., "Saskatoon") is NOT a constant across all keywords. Some keywords will have it, some won't. The unifying thread is the service theme and purchase intent, not the location. (How to structure geo-modified vs. un-modified keywords across campaigns is covered in "Campaign Structure for Multi-Geo Clients" below — read that BEFORE presenting the final output if the brand targets more than one city.)

### Step 3: Rank by Volume for Ad Copy

Once the keyword list is built, rank by search volume. This ranking directly feeds the RSA headline structure:

- **Headlines 1–5 (Service/keyword headlines):** Derived from the top-volume keywords. Written naturally — not verbatim keyword stuffing. "Roof replacement Saskatoon" becomes "Roof Replacement in Saskatoon" or "Get Your Roof Replaced Today."
- **Headlines 6–10 (Benefits/outcomes):** Customer benefits, unique mechanisms, what makes the brand different from competitors.
- **Headlines 11–15 (Brand + CTA):** Brand name, social proof, calls to action. E.g., "Northside Roofing Denver", "Get a Free Quote", "5-Star Rated Contractor."

Present the keywords with volume data and note which ones map to H1–H5. For multi-geo clients, rank volume **within each city campaign**, not across the whole account — each campaign's H1–5 should be city-specific.

### Step 4: Move to the Next Theme

After completing one theme, identify the next highest-intent theme for that same service. Then the next. If the brand has multiple services, restart the entire process for each service.

Theme prioritization is always bottom-of-funnel first, working upward:
1. Highest-intent BOFU theme for Service A
2. Next-highest-intent BOFU theme for Service A
3. Continue until BOFU is covered
4. Repeat for Service B, C, etc.
5. MOFU and TOFU campaigns come later, separate builds

### Step 5: Deliver Output

One line per theme. See the plugin `CLAUDE.md` → "Output Discipline".

```
N themes, N keywords, all exact.

  [theme] — [volume]/mo [geo], [competition], $[low]–$[high]. [H1–H5 anchor | own ad group]
  [theme] — [volume]/mo, [competition]. [note only if it changes the build]

Skipped: [theme] — [the reason in one clause]
Negatives seeded: N terms → [file or list]
```

Per theme, the reader needs: volume, competition, bid range, whether it anchors H1–H5, and whether it belongs in a different campaign (different funnel stage). Nothing else.

Full keyword lists with per-keyword metrics go to a file, not into chat.

**If the brand targets multiple geos, organize the deliverable as campaign-per-city with themes as ad groups inside (see next section for why). Do NOT deliver a flat theme list that relies on city-modified keywords inside a single campaign — that structure can't be operated properly in Google Ads.** State that as one line, not a lecture — the reasoning below is there if they ask.

If the user wants to proceed to building, hand off to the `google-ads-campaign-build` skill.

---

## Campaign Structure for Multi-Geo Clients

**This is a rule, not a recommendation. Read this before finalizing any multi-geo deliverable.**

Google Ads sets location targeting at the **campaign level**, not the ad group or keyword level. You cannot "target Calgary with keyword A and Kelowna with keyword B" inside a single campaign — the campaign targets whichever geos are set in its location settings, and every ad group and keyword inherits that. The keyword itself can contain a city name ("screen printing calgary"), but the city name in the keyword only affects query matching — it does not control who sees the ad or how budget is spent.

Consequences of putting multiple cities in one campaign:
- **Budget cannot be split by city.** If Calgary eats 80% of demand, it will eat 80% of spend, and a small market like Kelowna will be starved of impressions even if it has better CPAs.
- **Bids cannot be tuned by city.** CPCs vary meaningfully between markets. One campaign forces one bid strategy across all of them.
- **Ad copy cannot be city-specific.** A Calgary-in-the-headline ad will serve to Saskatoon searchers who happen to type "custom t shirts" with no city modifier.
- **Performance data is conflated.** You can't see which city is converting — location reports segment performance, but optimization decisions (pause/scale) happen at the campaign level.
- **Schedules, landing pages, and extensions are single-city-or-nothing.** Hours of operation, location extensions, call extensions, and landing pages all belong to the campaign.

### The rule

**One target geo = one campaign.** For a brand targeting 3 cities, that's 3 campaigns. Themes become ad groups inside each campaign, mirrored across the city campaigns.

```
Campaign 1: [Brand] | Lead Gen | BOFU | ... | Calgary
  ├── Ad Group: screen-printing
  ├── Ad Group: custom-t-shirt-printing
  ├── Ad Group: embroidery
  └── Ad Group: custom-hoodies

Campaign 2: [Brand] | Lead Gen | BOFU | ... | Saskatoon
  ├── Ad Group: screen-printing
  ├── Ad Group: custom-t-shirt-printing
  ├── Ad Group: embroidery
  └── Ad Group: custom-hoodies

Campaign 3: [Brand] | Lead Gen | BOFU | ... | Kelowna
  ├── Ad Group: screen-printing
  ├── Ad Group: custom-t-shirt-printing
  ├── Ad Group: embroidery
  └── Ad Group: custom-hoodies
```

Inside each city campaign, keywords can include the city modifier (e.g., "screen printing calgary" inside the Calgary campaign) — this is still valuable because geo-modified queries have higher commercial intent. But the campaign's location-targeting setting is what actually gates who sees the ad.

### Location targeting settings (call these out in the deliverable)

When handing off, specify:
- **Presence setting = "People in or regularly in your targeted locations."** Not "Interest." "Interest" lets a Toronto searcher see a Kelowna-geo'd campaign just because they typed "custom t shirts kelowna," which defeats the purpose of the split.
- **Exclude the other target cities from each campaign's location settings.** So the Calgary campaign excludes Saskatoon + Kelowna, the Saskatoon campaign excludes Calgary + Kelowna, etc. This prevents cannibalization if a searcher straddles the boundary.

### When a separate national campaign makes sense

Some BOFU themes have zero city-level volume but real national volume (common with B2B workwear and corporate-gifting terms). These get their own national/country-level campaign at a small budget allocation, separate from the city campaigns. Flag this when it happens — it's a structure decision, not a keyword decision.

### Budget allocation heuristic

Pro-rata the monthly budget by the sum of exact-match volume per city. Cap the smallest city at a floor (e.g., $200–$250/mo) so it has a fair shot at learning. Revisit after 30 days on actual CPL, not planned volume.

---

## Use Case 2: Expanding an Existing Campaign

Triggered when a campaign is already running but the user wants to find gaps.

### Step 1: Start with Search Term Data

The first move is always the search term report — use the `mine-search-terms` skill or pull search terms via GAQL. Look for new keyword opportunities in what's already triggering.

Only go to keyword planner if the search term report doesn't surface anything new.

### Step 2: Seed with Top Performers

If keyword planner is needed, take the top 2–3 converting keywords from the campaign. "Top performing" means:
- 5+ conversions (enough to be statistically meaningful)
- Strong conversion rate
- Acceptable cost-per-lead

Do NOT seed with highest-traffic keywords — seed with best-converting keywords.

### Step 3: Evaluate Results

Call `generate_keyword_ideas` with those top performers as seeds.

For expansion, the bar is simple: **does the intent fit the existing theme?** If yes, add it to test. No volume floor, no CPC ceiling. Let performance data decide after it runs.

Flag anything that suggests a new theme rather than a fit for the existing one — that becomes a separate conversation about whether to build a new campaign. If the proposed "new theme" is actually a new geo, that's a new campaign, not a new ad group inside the existing one — see "Campaign Structure for Multi-Geo Clients" above.

---

## Use Case 3: Strategic Theme Exploration

Triggered early in the brand relationship, often during strategy sessions. This is not a different process — it's Use Case 1 applied as planning.

Identify the brand's core services from their website/brief. For each service, identify the most bottom-of-funnel keyword theme. Use keyword planner to validate that there's volume behind the themes worth building campaigns around.

The output here is a theme map, not a full keyword list:
- Service A → Theme 1 (anchor term, estimated volume) → Theme 2 → Theme 3
- Service B → Theme 1 → Theme 2
- Prioritization recommendation based on volume and intent

For multi-geo clients, add a geo layer to the theme map — estimate volume per city per theme so the campaign architecture conversation has real numbers behind it.

This feeds into the campaign architecture conversation before any building starts.

---

## Interpreting Keyword Planner Data

### Competition Levels
- **LOW** — fewer advertisers bidding, often lower CPC. Common in niche local services.
- **MEDIUM** — moderate competition. Standard in most service industries.
- **HIGH** — many advertisers bidding, expect higher CPCs. Requires strong ad relevance and landing pages.

### CPC Estimates
Values are in micros (1,000,000 = $1.00).
- `lowTopOfPageBidMicros` — minimum bid to appear at top of page
- `highTopOfPageBidMicros` — competitive bid for consistent top position
- The spread between low and high indicates bid sensitivity in that market

### Search Volume Caveats
- Accounts without active ad spend see volume ranges (1K–10K), not exact numbers. Note this when presenting data.
- Very niche terms may return zero data — this does not mean zero searches.
- Keyword Planner groups close variants (singular/plural, misspellings) into one metric.
- Seasonal businesses will show volume spikes in certain months — call these out when relevant.
- **Un-modified seeds return national (usually US) volume, which is useless for Canadian local services.** Always seed with `[term] [city]` when researching a Canadian local client — that returns real CAD city-level volume.
