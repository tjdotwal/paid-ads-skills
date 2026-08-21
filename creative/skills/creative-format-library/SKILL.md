---
name: creative-format-library
description: A 52-template creative format taxonomy — the working vocabulary for classifying, generating, and gap-analyzing ad creative across Meta, paid social, and any visual placement. Load this skill whenever evaluating an existing ad's format ("what format is this", "classify this creative", "which template does this match"), brainstorming concepts that need to map to a known format ("give me ideas from the format library", "which template should we test next"), mining creative patterns across an account, or recommending untested formats. Companion to the meta-ads plugin's ad_image_get and ad_video_get tools (used to actually see the creative — video ads go through ad_video_get for transcript and keyframes) and to meta-creative-analysis, which uses this taxonomy as its clustering vocabulary. Triggers any time creative analysis needs a standardized taxonomy rather than ad-hoc description.
version: 1.0.0
---

# Creative Format Library

A taxonomy for classifying, generating, and analyzing ad creative. **52 templates across 7 sections.**

Template numbers are the shared vocabulary — they are stable and never reused. Numbers are assigned in the order formats were added, so sections are not numerically contiguous (section E holds 26–30 and 43, 46–49, 52). Sort by section, not by number.

Formats carrying more than a line of methodology have full specs in `references/format-detail.md` — that covers 43–52, the video script frameworks, and the substantiation rules on the claim-heavy formats. `references/json-prompt-spec.md` holds the JSON prompt architecture for image generation. `references/notion-source.example.md` explains the optional live-Notion enrichment.

## Live source check (do this first)

If `references/notion-source.md` exists, the taxonomy has a live upstream in Notion that carries two things this repo doesn't: **a JSON prompt template per format**, and any format added since the repo was last updated. Read that file for the `data_source_id`, then:

1. Query the data source for `Name`, `Section`, `Aspect Ratio`, `Template Type`, `url`. That's the authoritative list of which formats exist right now.
2. Reconcile against the table below. Rows not in it are new — use them, reason from the name and section, and tell the user they aren't documented locally yet.
3. **Before writing a brief or a JSON prompt for a specific format, fetch that format's page** and use its JSON prompt template verbatim rather than reconstructing one.

If the file is absent or the Notion connector isn't available, work from this file and `references/format-detail.md` — they're complete enough to work from. **But say so in the output** (see Source stamp below). The user needs to know when they're getting the local snapshot rather than the live library.

Note the shape of the upstream: formats **1–42 carry only a JSON prompt** on their Notion page, no prose. Formats **43–52 carry full prose specs**, already mirrored into `format-detail.md`. So for the older formats, Notion adds the JSON template; for the newer ones, it adds the template and reference screenshots.

## Source stamp (required on every output)

Every set of format recommendations, every design brief, and every JSON prompt ends with a one-line stamp saying where the format content came from. No exceptions, and never omit it because it seems obvious.

```
Source: Notion live — 52 formats listed, pages fetched for 5, 21, 45
Source: local files only — Notion not configured
Source: local files only — Notion configured but fetch failed (<reason>)
```

If the stamp says `local files only`, you must also add one line telling the user what they're missing: the per-format JSON prompt templates, reference screenshots, and any format added to Notion since this repo was updated. Say it plainly so they can decide whether to open Notion themselves.

Never imply Notion was consulted when it wasn't. If a fetch was attempted and failed, name the failure — a silent fallback is the one outcome that makes the output untrustworthy.

## How to use this library

**For classification:**

1. View the creative. **Check the creative type first, then pick the right tool:**
   - **Static / carousel** → `ad_image_get` (Meta), or the channel's image fetch.
   - **Video** → `ad_video_get`, which returns the spoken script as a timestamped transcript. Never classify a video ad from its thumbnail: the thumbnail is a single platform-chosen frame and routinely misrepresents the format. Usually the script alone tells you the format — a testimonial arc, a listicle, a PAS structure all read clearly in the transcript. When the format hinges on the *visual* (typography-driven, AI animation, talking-head vs b-roll), add `include_keyframes=True` for 5 frames. Keyframes are off by default because they cost real context; turn them on deliberately, not reflexively. If a creative has a `video_id`, it's a video ad.
   - **Always pass `ad_account_id` explicitly** to either tool. Asset lookups are account-scoped; without it they degrade silently to a 64px thumbnail with no error.
   - If the video can't be fetched (Meta gates `source` behind a Page token for some page-owned videos), classify from the thumbnail + copy and mark it **`(creative unverified — copy-layer diagnosis only)`**. Never let a thumbnail-only guess enter a roll-up unflagged.
2. Match against the templates below. Pick the closest fit as the **primary template**. If the creative blends two formats, add a **secondary** (e.g. "Primary: 5 (PAS), Secondary: 21 (LTO) — problem framing with a price anchor").
3. Roll up across the account: group by primary template, attribute performance (CTR, CPA, CVR), report which templates are over- and under-represented and where the winners cluster.

**For generation:**

1. Identify the goal — test untested formats, or double down on what's working.
2. Pull a template number from the relevant section.
3. Hand the template name + brand context to whoever is designing. For image generation, `references/json-prompt-spec.md` has the JSON prompt architecture.

**For gap analysis:**

1. List all 52 templates.
2. Cross-reference against what is currently running in the account.
3. Report untested templates, weighting sections where the brand already has performance signal in adjacent templates.

## The Library

### A. Headline & Text-Driven Ads (6)

| # | Name | What to look for |
|---|------|-------------------|
| 1 | Bold Headline Ad | Large attention-grabbing headline as the primary visual; minimal supporting imagery |
| 2 | Benefit Stack Ad | Vertical list of 3–5 key benefits, often with check-marks or bullets |
| 3 | Stat / Data Callout Ad | One dominant statistic as the hook ("87% of users…") |
| 4 | Quote / Pull-Quote Ad | Editorial-style customer or expert quote with attribution |
| 5 | Problem-Agitate-Solve (PAS) Ad | Problem statement → emotional amplification → product as resolution |
| 6 | Listicle / "3 Reasons" Ad | Numbered reasons or steps, listicle structure |

### B. Comparison & Social Proof Ads (10)

| # | Name | What to look for |
|---|------|-------------------|
| 7 | Us vs. Them (Comparison) Ad | Side-by-side vs. competitor or category default |
| 8 | Ingredient / "What's Inside" Comparison | Visual breakdown of ingredients vs. typical alternative |
| 9 | Testimonial / Customer Quote Ad | Real customer quote with name and/or photo |
| 10 | Star Rating / Review Count Ad | 5-star visual + review count as the headline |
| 11 | Before / After Ad | Split visual showing transformation |
| 12 | "As Seen In" / Press Logos Ad | Wall of media logos as the credibility anchor |
| 13 | Social Media Comment Screenshot Ad | Real social comment used as the creative |
| 14 | UGC-Style / Selfie Review Ad | Customer-shot vertical video/photo, authentic feel |
| 15 | Influencer Endorsement Ad | Named creator or expert paired with the product |
| 45 | Research Receipt / Journal Screenshot Ad | Recreated journal-article panel as the hero, a reframe line, then a real customer comment. Authority → reframe → proof |

### C. Lifestyle & Context Ads (5)

| # | Name | What to look for |
|---|------|-------------------|
| 16 | Lifestyle Context Shot | Product in a real-life use scene |
| 17 | Flat Lay / Top-Down Product Arrangement | Curated overhead arrangement, often with related items |
| 18 | Seasonal / Holiday Ad | Timely seasonal hook (holiday, weather, event) |
| 19 | Unboxing / Packaging Hero Ad | Packaging as the visual subject |
| 20 | Scale / Size Context Ad | Size reference (next to coin, hand, person, etc.) |

### D. Urgency & Offer Ads (5)

| # | Name | What to look for |
|---|------|-------------------|
| 21 | Limited-Time Offer / Sale Ad | Discount + countdown or deadline framing |
| 22 | Countdown / Scarcity Ad | Explicit countdown timer or "only X left" |
| 23 | Bundle / Multi-Product Ad | Multiple products grouped as a deal |
| 24 | Free Shipping / Low-Friction Offer Ad | Frictionless offer as the hook |
| 25 | Money-Back Guarantee / Risk-Reversal Ad | Guarantee or warranty as the lead |

### E. Educational & Informational Ads (11)

| # | Name | What to look for |
|---|------|-------------------|
| 26 | "Did You Know?" / Myth-Buster Ad | Surprising fact or counter-intuitive claim |
| 27 | How-To / Step-by-Step Ad | Numbered steps showing usage or process |
| 28 | Ingredient Spotlight / "What's In It" Ad | Single ingredient or component as hero |
| 29 | Nutritional / Spec Breakdown Ad | Detailed spec or nutrition-label callout |
| 30 | "The Science Behind" / Unique Mechanism Ad | Scientific framing (study, mechanism, expert) |
| 43 | Problem Mechanism / Ugly Ad | Raw, unpolished "ugly" creative explaining the problem mechanism in detail |
| 46 | Mechanism Proof / Before-After Body Render Ad | Product paired with a before/after render of the mechanism inside the body or material. **Gated on substantiation** — see detail |
| 47 | AI Animation Style Ads | AI animation in a non-default aesthetic — felt stop-motion, plush, puppet, vinyl toy, diorama — rather than the Pixar/claymation defaults |
| 48 | Problem Deep Dive Yapper Ad | Faceless, prop-driven demo video. ~80% teaching the root cause, ~20% pitch |
| 49 | Destroy The Common Belief Explainer | Opens by destroying a belief the viewer holds, then teaches the real mechanism. Product enters only as the "new mechanism" |
| 52 | Science / Mechanism Explainer Ad | Teaches the causal *process* behind a claim so the reader concludes it themselves. Problem → mechanism → proof → outcome |

### F. Emotional & Story-Driven Ads (8)

| # | Name | What to look for |
|---|------|-------------------|
| 31 | Founder Story / "Why I Made This" Ad | Founder's personal origin story; candid founder portrait on-image |
| 32 | Aspirational / "Imagine" Ad | Future-state aspiration (your life with the product) |
| 33 | "Day In The Life" / Routine Ad | Time-of-day or routine integration |
| 34 | Emotional Trigger / FOMO Ad | FOMO, urgency, social proof of others having it |
| 35 | Community / "Join Us" Ad | Belonging to a movement, tribe, or community |
| 42 | Outcome-First Yapper Ad | Talking-head video leading with the outcome/result |
| 44 | Personal Letter / Confessional Ad | Long-form first-person body copy as direct address — apology, confession, gratitude, scarcity. Designed, not raw |
| 50 | Long-Form Full-Funnel VSL (Common Enemy) | ~2:30–3:30 UGC selfie testimonial that walks cold traffic through the whole awareness ladder on a stacked two-enemy structure |

### G. Format & Platform-Specific Ads (7)

| # | Name | What to look for |
|---|------|-------------------|
| 36 | Instagram Story / 9:16 Vertical Ad | Vertical story-format designed for IG/FB stories |
| 37 | Carousel First Slide / Hook Slide | Designed as the hook of a multi-slide carousel |
| 38 | Meme-Style Ad | Native meme format/template |
| 39 | Infographic / Value-Dense Ad | Dense visual information design |
| 40 | Text-Only / Typography Ad | Pure typography, no imagery |
| 41 | Slideshow Story Ad | Multi-frame story progression as slideshow |
| 51 | Native Ad (Organic-Mimic) | Built to pass as an organic post. No brand marks, no overlay, withholds context on purpose. Four variants (51a–d) |

## Aspect ratio quick-reference

Most templates default to **1:1** (feed). Some are built for **4:5** (vertical feed) or **9:16** (stories/reels). When choosing a template for a placement, prefer one whose default ratio matches the placement to avoid cropping surprises.

The video script formats (48, 49, 50) and 42 are 9:16 by default. 51 varies by variant — see detail.

## Classification tips

- **Hybrids are common.** A PAS ad with a price anchor is "Primary: 5, Secondary: 21." Don't force a single label.
- **The visual format usually wins over the copy.** A testimonial quote rendered as a meme is Meme-Style (38) first, Testimonial (9) second.
- **Section G is structural, not topical.** A vertical IG Story ad about a discount is "Primary: 36 (IG Story), Secondary: 21 (LTO)" — the platform constraint dominates.
- **The mimicry formats are defined by what they imitate.** 13 imitates social UI, 45 imitates a journal page, 51 imitates an organic post. When a creative mimics a real interface or document, that mimicry is the primary classification and the persuasion structure is secondary.
- **Distinguish 43 / 44 / 51 by production value.** All three are first-person and low-gloss, but: 43 is deliberately ugly and still visibly an ad (headline + solution block); 44 is *designed* — branded fonts, color block, hero product; 51 is undesigned by rule and often names no product at all.
- **The mechanism formats split by medium and structure.** 30 is a static science framing; 46 is a before/after render pair; 52 is a four-beat causal explainer; 43 is a raw single-panel problem visual; 48 and 49 are the video versions. If it teaches a causal process, check all five before labeling.

## Substantiation gate

Formats 45, 46, 30, and 52 borrow credibility from research, anatomy, or engineering. That borrowed credibility is the whole mechanic, which means a fabricated version is not a creative shortcut — it is a false claim.

- A cited study must be real. Title, authors, journal, year, **and** the stat must actually appear in the paper.
- Represent findings honestly. Don't stretch a narrow-population result into a universal claim.
- A before/after render may only depict an outcome the product can substantiate it causes. A "concept illustration" disclaimer does not rescue an unsubstantiable render — the image *is* the claim.
- No disease claims from non-drug products.

`references/format-detail.md` carries the full rules per format. When a format can't clear its gate, pick a different format.

## Extending the library

The library grows as new formats show up in the wild. When that happens:

1. Assign the next unused number. Never renumber or reuse — the numbers are the shared vocabulary and old analyses reference them.
2. Add a row to the correct section table with a one-line "What to look for."
3. Update the section count in the heading and the total at the top.
4. If the format carries real methodology (a script framework, a substantiation rule, variants), add a section to `references/format-detail.md`.
5. If it fits no existing section, add a new one (H, I, …) named for the unifying theme.
6. Bump the plugin version in `.claude-plugin/plugin.json` — patch for additions, minor for a new section.

To capture a format from a screenshot, paste the image into a fresh conversation and ask for a standardized JSON template using the key structure in `references/json-prompt-spec.md`, with brand-specific content replaced by bracketed placeholders.

## Handoff to other skills

This skill is the **taxonomy** — load it when you need to *name* a format. It is not the workflow for producing concepts, briefs, or copy.

- **Concept ideation, design briefs, reverse-engineering a screenshot, slideshow/yapper frame architecture** → `ad-creative-strategist`. It imports this vocabulary and adds the workflow: two operating modes, the design brief format, the frame libraries, the reverse-engineering checklist, A/B variation rules.
- **Copy production** — image copy, headlines, body copy, VSL scripts, landing pages, emails → `direct-response-copywriter`. It runs the upstream diagnostic (offer / customer / market sophistication / resistance type / mechanism / big idea) and writes against it. This skill does not write copy.
- **Account-level pattern mining** — which formats cluster with top performance, gap analysis against untested formats → `meta-ads:meta-creative-analysis`. It uses this taxonomy as its clustering vocabulary.

## When NOT to use this skill

- The question is about ad platform tooling, account setup, or campaign mechanics rather than creative format.
- You're mid-ideation or mid-reverse-engineering — `ad-creative-strategist` is the workflow; this is the vocabulary it depends on.
- You're writing direct-response copy with no visual format component — `direct-response-copywriter`.
