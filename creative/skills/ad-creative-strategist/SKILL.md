---
name: ad-creative-strategist
description: >
  Ad creative strategy skill for generating static image, slideshow, and short-form video ad concepts and copy briefs for design
  teams. Use this skill whenever the user is working on an advertising build, wants creative
  concept ideas for a brand or campaign, mentions HigsField or Nano Banana 2, uploads an ad
  screenshot to reverse-engineer, or asks for ad creative suggestions. Also trigger when the user
  says "generate ad concepts", "what formats could work for this client", "give me creative ideas
  for this campaign", "reverse-engineer this ad", "write a creative brief", references any of
  the creative format types in the playbook, or mentions slideshow ads, story ads, video carousels,
  sequenced frame ads, talking-head Reels, yapper ads, or ugly ads. Default output is a
  design-team-ready creative brief (copy on image + image suggestion, or talk track + b-roll for
  video formats). Only output JSON if the user explicitly asks for it.
version: 1.0.0
---

# Ad Creative Strategist

> **Canonical sources of truth**
> - **Format taxonomy** — `creative-format-library`, in this same plugin. The inline Format Library below covers the same 52 templates with strategic notes layered on, so it's enough on its own for formats 1–42. For **43–52, read `../creative-format-library/references/format-detail.md`** — those entries are one-line summaries of specs running 40–90 lines each, and for the video formats (48, 49, 50) the beat sheet is the deliverable.
> - **JSON prompt architecture** — `creative-format-library/references/json-prompt-spec.md`: the key structure, the two-stage brand-DNA workflow, and a complete worked example.
> - **For copy work** (image copy, headlines, body copy, VSL scripts, landing pages) — hand off to the `direct-response-copywriter` skill. This skill is for visual format strategy and design briefs; copy decisions go through the copywriter.

## Two Operating Modes

### Mode 1: Creative Ideation (Primary Use)
Triggered when the user is working on a brand advertising build and wants concept ideas.

**Pick your angle before building the slate.** Every ad is built around one main angle — one reason the reader stops and pays attention. Before recommending formats, look at the list below and make sure the slate of concepts hits at least 3–4 different angles, not five versions of the same one.

| Angle | Example |
|---|---|
| Pain point | "Stop wasting time on X" |
| Outcome | "Achieve Y in Z days" |
| Social proof | "Join 10,000+ teams who…" |
| Curiosity | "The X secret top companies use" |
| Comparison | "Unlike X, we do Y" |
| Urgency | "Limited time: get X free" |
| Identity | "Built for [specific role/type]" |
| Contrarian | "Why [common practice] doesn't work" |

**Workflow:**
1. Review the brand's brand, messaging, product, and campaign goals from the conversation context
2. **Scan the formats** in the inline Format Library below. If any of 43–52 look like candidates, read `../creative-format-library/references/format-detail.md` for those before recommending them.
3. Recommend the 5–10 most strategically relevant formats for this brand and campaign
4. For each recommended format, output a **design brief** in the standard format below
5. Only offer JSON prompts if the user explicitly asks — do not default to it

**Output format — one block per concept:**

Each brief has two sections: **Copy On Image** and **Image Suggestions**. The content inside each section should match the format type — don't force a fixed template. A testimonial ad needs a quote and attribution, not a benefit stack. A stat callout needs one big number and a line of context. A lifestyle ad might have almost no copy on image at all. Write what the format actually calls for.

**Copy On Image** — label each copy element clearly on its own line. Examples of what a line might look like depending on format:
- `Headline: [text]`
- `Quote: "[verbatim customer language]"`
- `Stat: [number + context]`
- `Step 1: [action]`
- `Body: [short body copy]`
- `CTA: [CTA line]`

Use only the copy elements the format needs. Don't pad with filler sections. A pull quote ad might just be a quote and a CTA. A PAS ad might be three labeled bands. Follow the format, not a checklist.

**Image Suggestions** — be specific. Describe layout (grid, single shot, split screen, collage), subjects, mood, and whether to use client-provided photos vs. AI-generated. One to two lines is enough unless the concept needs more direction.

**Structure per concept:**
```
## [FORMAT NAME] — [Strategic Rationale]

Copy On Image:
```[Element label]: [copy]
```[Element label]: [copy]
Image Suggestions:
- [Specific visual direction]
---
```

After delivering briefs, offer to generate Nano Banana 2 JSON prompts only if the user wants them for AI image generation.

### Mode 2: Reverse-Engineering (Secondary Use)
Triggered when the user uploads an ad screenshot, points at an existing live ad, or asks to break down an ad in the account.

**Workflow:**
1. **Get the image.** If the user uploaded a screenshot, use it directly. If the user references an ad by ID or by name in their Meta account, fetch the creative via the `ad_image_get` tool (from the `meta-ads` plugin) — it returns the full-resolution image, not a thumbnail. Do not work from copy metadata alone; the visual format dominates classification.
2. Analyze every visual component in the image systematically (see analysis checklist below).
3. **Classify against the Format Library** below. Pick a primary template, add a secondary if the creative is a hybrid (e.g., "Primary: 5 PAS, Secondary: 21 LTO"). The visual format usually wins over the copy. For the distinctions that are easy to get wrong — 43 vs 44 vs 51 by production value, and the mimicry formats (13, 45, 51) — read the classification tips in `../creative-format-library/SKILL.md`.
4. Output a design brief in the standard format above — describing what's in the ad.
5. After the brief, offer: *"Want a Nano Banana 2 JSON prompt for AI image generation, or 5–10 concept variations?"*

**Important — copy vs. on-image copy.** The Meta ad API exposes a `headline`, `description`, and `body` field as creative metadata. Those are **not** the same as the copy painted onto the image. Always distinguish: "headline (API field)" vs. "on-image copy" in your analysis. The on-image copy is what users actually read; the API metadata is the surrounding ad chrome.

**Exception — output JSON directly** if the user explicitly says they want a JSON prompt, HigsField prompt, or Nano Banana 2 output.

---

## JSON Key Architecture

Only use this section when the user explicitly requests JSON / NB2 / HigsField output.

Every JSON prompt uses exactly these keys. Do not rename, skip, or add keys unless explicitly instructed.

```json
{
  "label": "",
  "tags": [],
  "Style": [],
  "Subject": [],
  "TextOverlay": {},
  "Background": "",
  "ColorRestriction": [],
  "Lighting": "",
  "Camera": {
    "lens": "",
    "aperture": "",
    "angle": ""
  },
  "Arrangement": "",
  "OutputStyle": "",
  "Mood": "",
  "meta": {
    "aspect_ratio": ""
  }
}
```

| Key | What to put here |
|---|---|
| `label` | `[brand]-[format]-[variant]` |
| `tags` | 4–6 keywords anchoring ad type and aesthetic |
| `Style` | Specific rendering style descriptors — "commercial-product-photography", not just "clean" |
| `Subject` | Array of precise descriptions including position, surface, studio treatment |
| `TextOverlay` | All text elements as named sub-keys with explicit style instructions per element |
| `Background` | Scene/surface description including color, texture, mood, depth |
| `ColorRestriction` | **Most important key.** Every color named with its location. Always end with `"no additional colors introduced"` |
| `Lighting` | Source, direction, quality, mood — specific, not vague |
| `Camera` | All three sub-keys: `lens` (mm), `aperture` (f-stop), `angle` |
| `Arrangement` | Where every element sits relative to others in the frame |
| `OutputStyle` | Single sentence rendering instruction |
| `Mood` | 3–5 emotional descriptors |
| `meta.aspect_ratio` | `1:1` / `4:5` / `9:16` / `16:9` |

**ColorRestriction examples:**
- Bad: `["brand colors", "clean palette"]`
- Good: `["#1A1A1A background", "white headline text", "#FF4D00 CTA button", "no additional colors introduced"]`

---

## Format Library

`creative-format-library` is the source of truth for *which formats exist*. The list below covers the same 52 and adds what the taxonomy doesn't carry: which funnel stage each format suits and when to reach for it. Use it as your working list; go to the detail files when a format needs more than a line.

### Read the detail files directly

`creative-format-library` ships in this same plugin, so its files are always on disk next to this one. **Read the paths directly rather than waiting for the skill to be loaded** — a file read is deterministic, invoking a sibling skill is not:

| Path | What's in it |
|---|---|
| `../creative-format-library/SKILL.md` | All 52 templates by section, classification tips, the mimicry and production-value distinctions |
| `../creative-format-library/references/format-detail.md` | Full specs for 43–52 — structure, rules, substantiation gates, complete video script beat sheets, remix logic |
| `../creative-format-library/references/json-prompt-spec.md` | JSON prompt key architecture, two-stage brand-DNA workflow, worked example |
| `../creative-format-library/references/notion-source.md` | **If present**, a live Notion upstream with a per-format JSON prompt template and reference screenshots |

**Check for `notion-source.md` before recommending formats.** When it exists and the Notion connector is available, fetch the page for each format you're about to brief and use its JSON prompt template rather than building one from the key architecture. That template is the difference between a usable image on the first generation and iterating three times. The older formats (1–42) have no prose spec upstream, only that template — so for those the fetch is *purely* about the prompt.

When it's absent or the fetch fails, work from the files above — **and stamp the output** so the user knows. Every brief and every JSON prompt ends with:

```
Source: Notion live — pages fetched for <format numbers>
Source: local files only — Notion not configured
Source: local files only — Notion configured but fetch failed (<reason>)
```

On `local files only`, add one line naming what's missing: the per-format JSON prompt templates, reference screenshots, and any format newer than this repo. Never imply Notion was consulted when it wasn't — a silent fallback is what makes an output untrustworthy.

**When to read which:**

- **Recommending or classifying formats 1–42** — the inline list below is sufficient. It carries strategic notes (funnel stage, when to reach for it) the taxonomy doesn't.
- **Any of 43–52 in play** — read `format-detail.md` for that format before writing the brief. The inline entries for these are summaries of documents that run 40–90 lines each; for 48, 49, and 50 the beat sheet *is* the deliverable and you cannot reconstruct it from one line.
- **Writing a JSON prompt** — if `notion-source.md` exists, fetch that format's page and use its template. Otherwise read `json-prompt-spec.md` for the key architecture and build one. Never improvise the key structure from memory.
- **Substantiation-gated formats (30, 45, 46, 52)** — read the gate in `format-detail.md` before proposing them. These borrow credibility from research or anatomy, so a version that can't clear its gate isn't a creative shortcut, it's a false claim.

The inline list below and the taxonomy cover the same 52 templates. If they ever disagree on which formats exist, `creative-format-library` wins — it's the source of truth and this list is a strategic-notes layer over it.

### The 52 formats, with strategic notes

Bold-marked entries have full specs in `../creative-format-library/references/format-detail.md`. Read those before writing a brief against them.

### A. Headline & Text-Driven
1. **Bold Headline** — Product + big bold headline. Top-of-funnel workhorse. 1:1
2. **Benefit Stack** — Product + 3–5 checkmark benefits. Consideration stage. 1:1
3. **Stat / Data Callout** — Oversized statistic as hero. Authority/credibility. 1:1
4. **Pull Quote** — Short punchy quote, editorial typography feel. 4:5
5. **PAS (Problem-Agitate-Solve)** — 3-band layout: pain → amplify → solution. 4:5
6. **Listicle / "3 Reasons"** — Numbered list, scannable. Great for retargeting. 4:5

### B. Comparison & Social Proof
7. **Us vs. Them** — Split-screen, brand vs generic. Keep competitor unnamed. 1:1
8. **Ingredient Comparison** — Clean ingredient list vs cluttered competitor list. 1:1
9. **Testimonial / Customer Quote** — Real review language as centerpiece. 1:1
10. **Star Rating / Review Count** — Leads with rating. Use only if 4.5+ stars, 500+ reviews. 1:1
11. **Before / After** — Visual transformation. Fitness, skincare, cleaning, organization. 1:1
12. **As Seen In / Press Logos** — Media logos row. Authority builder. 1:1
13. **Social Comment Screenshot** — Mimics organic social UI. Pattern interrupt. 4:5
14. **UGC-Style / Selfie Review** — Intentionally unpolished phone-camera aesthetic. 4:5
15. **Influencer Endorsement** — Creator portrait + product + quote. 1:1
45. **Research Receipt / Journal Screenshot** — Mimics a screenshot of a peer-reviewed study, journal abstract, or research finding as third-party proof. High-authority social proof for claims that need a citation. Pull the underlying evidence with the `scholarly-mechanism-research` skill. 4:5

### C. Lifestyle & Context
16. **Lifestyle Context Shot** — Product in natural use environment. Top-of-funnel vibe sell. 1:1
17. **Flat Lay / Top-Down** — Bird's-eye curated product arrangement. Instagram-native. 1:1
18. **Seasonal / Holiday** — Product adapted to seasonal context. Plan 2–4 weeks ahead. 1:1
19. **Unboxing / Packaging Hero** — Open box, product emerging. DTC/subscription brands. 4:5
20. **Scale / Size Context** — Product held in hand or next to familiar object. 1:1

### D. Urgency & Offer
21. **Limited-Time Offer / Sale** — Discount-led. Urgency elements. Real offers only. 1:1
22. **Countdown / Scarcity** — Visual scarcity element. Premium urgency, not clearance energy. 1:1
23. **Bundle / Multi-Product** — Products arranged as cohesive set + combined value prop. 1:1
24. **Free Shipping / Low-Friction** — Friction-remover as lead offer. Surprisingly high converter. 1:1
25. **Money-Back Guarantee / Risk-Reversal** — Guarantee seal. Higher-priced or low-awareness brands. 1:1

### E. Educational & Informational
26. **Did You Know / Myth-Buster** — Surprising fact or debunked myth as hook. 4:5
27. **How-To / Step-by-Step** — 3-step process using product. Demonstrates simplicity. 4:5
28. **Ingredient Spotlight** — Hero ingredient macro + product shot. One ingredient only. 1:1
29. **Nutritional / Spec Breakdown** — Clean visual breakdown of specs. 1:1
30. **The Science Behind** — Diagram/illustration of mechanism of action. Supplements, skincare, tech. 4:5
43. **Problem Mechanism / Ugly Ad** — Raw, intentionally unpolished creative that explains the *why* of the problem in long-form detail. Looks like a doc, a notepad, a screenshot, or a stripped typographic layout — not a designed ad. Works because it reads like information, not marketing. Use for high-resistance audiences who reject polish. 4:5 or 9:16.
46. **Mechanism Proof / Before-After Body Render** — Illustrated or rendered before-and-after of the mechanism at work (e.g., inside the body, on a surface) to make an invisible process visible. Educational proof for health, skincare, supplement, and tech offers. Pairs with `scholarly-mechanism-research` for the underlying science. **Substantiation-gated** — the render may only show an outcome the product can prove it causes. 1:1
47. **AI Animation Style Ads** — AI animation in a deliberately non-default material style: felt stop-motion, plush, puppet, vinyl toy, cardboard, diorama, glass. The Pixar/claymation look is saturated; a chosen material reads as craft instead. Pick one material and hold it for the whole spot — physical-material styles tolerate AI imperfection far better than photoreal humans do, which is most of why they work. 1:1 & 9:16
48. **Problem Deep Dive Yapper Ad** — Faceless, prop-driven demo video. Roughly 80% teaching the root cause with real objects, 20% pitch, so the viewer feels taught rather than sold and the product lands as the conclusion of the lesson. Cheap to shoot and endlessly remixable across niches. Needs a teachable problem and something physical to demonstrate with. 9:16. **Full beat sheet in `format-detail.md`.**
49. **Destroy The Common Belief Explainer** — Opens by naming and destroying a belief the viewer already holds, teaches the real mechanism, and introduces the product only as the "new mechanism" near the end. Thirteen beats, each removing one reason not to buy. For categories crowded with cheap look-alikes and misinformation, where a false belief is the thing blocking the sale. 9:16. **Full beat sheet in `format-detail.md`.**
50. **Long-Form Full-Funnel VSL (Common Enemy)** — 2:30–3:30 UGC selfie testimonial that walks cold traffic through the entire awareness ladder in one first-person story, on a stacked two-enemy structure: a distrusted institution for emotional alliance, the cheap/fake version of the solution for logical exoneration. Product arrives at the 60–70% mark. Heavy artillery for cold traffic and higher-consideration offers where the buyer has already tried the cheap version and been burned. 9:16. **Full beat sheet in `format-detail.md`.**
51. **Native Ad (Organic-Mimic)** — Built to pass as an actual organic post, not "authentic-looking branded content." Two jobs, both required: no signal that it's an ad (no logo, no brand font, no overlay, no CTA in-frame), and a visual that provokes a question it refuses to answer, so the only way to find out is to tap. Four variants — 51a native reel, 51b raw static, 51c long-caption truncation, 51d advertorial. Buys clicks with curiosity, so judge on CPL/CPA and never CTR alone, and make sure the landing page pays the question off in the first screen. Per-variant ratios and the curiosity-device list in `format-detail.md`.
52. **Science / Mechanism Explainer** — Teaches the causal *process* behind a claim in four beats (problem → mechanism → proof → outcome) so the reader reaches the conclusion themselves instead of being told it. Three beats of physics, one beat of claim; the benefit lands last and feels earned. Only works when there's a genuine explainable mechanism and the audience's default assumption about the problem is wrong or incomplete. Never stack two mechanisms — the format lives on one "aha." 1:1 & 9:16

### F. Emotional & Story-Driven
31. **Founder Story / "Why I Made This"** — Candid founder portrait + authentic quote. 4:5
32. **Aspirational / "Imagine"** — Cinematic scene of the ideal outcome. Sell the transformation. 4:5
33. **Day In The Life / Routine** — 3-4 panel grid, product in daily moments. 1:1
34. **FOMO / Emotional Trigger** — Without vs. with product contrast. Relatable, not condescending. 1:1
35. **Community / "Join Us"** — Group of happy customers. Specific numbers matter. 1:1
42. **Outcome-First Yapper Ad** — Talking-head short-form video (Reels/TikTok-native) that leads with the outcome or result in the first 1–2 seconds, then earns the watch time. Often founder, customer, or creator on-camera, vertical, minimal cuts. Hook is the result; the ad is the explanation. 9:16. See video brief section below.
44. **Personal Letter / Confessional** — Long-form first-person letter or confessional, formatted like a heartfelt note rather than an ad (founder or customer voice). Reads as honest disclosure, not marketing. For high-trust, emotional-resistance audiences. 4:5

### G. Format & Platform-Specific
36. **Instagram Story / 9:16 Vertical** — Full-screen vertical. Safe zone: center 80%. 9:16
37. **Carousel Hook Slide** — Bold text only. Its only job is to make them swipe. 1:1
38. **Meme-Style** — Authentic meme format, product in punchline. If it looks corporate, it's wrong. 1:1
39. **Infographic / Value-Dense** — Max information, organized layout. People screenshot and save. 4:5
40. **Text-Only / Typography** — No product image. Pure typographic poster. Two-color maximum. 1:1
41. **Slideshow Story Ad** — 4–6 sequenced static frames exported as video. Each frame does one persuasion job. Structured like a landing page in motion. Always deliver both 1:1 (feed) and 9:16 (Reels) variants. See frame library below.

---

## Slideshow Story Ad — Frame Library

Use this section when outputting briefs for format #41. Frames are modular — select and sequence based on awareness stage and funnel position. Do not default to all 6. A cold audience needs more frames; a warm retargeting audience can skip early-funnel frames.

### Available Frame Types

| Frame Type | Job | When to Use |
|---|---|---|
| **Pain Hook** | Open on the problem. Make them feel seen before you sell anything. | Cold audiences, problem-unaware prospects |
| **WIIFM Hook** | Lead with the outcome. What's their life like after? | Warm audiences, benefit-aware prospects |
| **Twist the Knife** | Dig into the pain. Make staying stuck feel worse than buying. | After a pain hook when conversion pressure is needed |
| **Solution Explainer** | Introduce the product as the answer. Clear, not clever. | Mid-sequence, after problem is established |
| **Objection Handler** | Name the #1 reason they won't buy. Dismiss it directly. | Pre-close, especially for higher-ticket or skeptical audiences |
| **Social Proof** | One strong testimonial, stat, or review. Borrowed credibility. | Anywhere after the hook — especially before CTA |
| **CTA Card** | One action. One line. No options. | Always last |

### Sequencing by Funnel Stage

**Cold / Problem-Unaware:**
Pain Hook → Twist the Knife → Solution Explainer → Social Proof → CTA

**Warm / Solution-Aware:**
WIIFM Hook → Solution Explainer → Objection Handler → CTA

**Retargeting:**
Objection Handler → Social Proof → CTA

### Output Format for Slideshow Story Ad Briefs

Always label each frame with its type. Copy elements only what the frame needs — don't force a fixed template onto every frame. End every brief with the aspect ratio deliverable note.

```
## SLIDESHOW STORY AD — [Strategic Rationale]

Frame 1 — [Frame Type]
Headline: [text]
Subhead: [text if needed]
Image: [specific visual direction]

Frame 2 — [Frame Type]
Headline: [text]
Image: [specific visual direction]

[Continue for each frame in sequence]

---
Deliverables: 1:1 (feed) + 9:16 (Reels) — both required
```

---

## Talking-Head Video Brief (Yapper Ad — Format #42)

Use this section when outputting briefs for format #42 (Outcome-First Yapper Ad). The brief is a *talk track + b-roll* sheet, not a static layout.

### Hook discipline
The first 1–2 seconds must lead with the outcome or the result. Not the setup. Not the credentials. The result. Examples:
- *"We booked 47 patients in 14 days with one ad."*
- *"This is how I gained back $3,200 a year on our roofing budget."*
- *"My wife dropped 22 pounds without changing a single workout."*

The rest of the video is the explanation — *how* this happened, *why* this works, *what* the offer is. Never the other way around.

### Brief output format

```
## YAPPER AD — [Strategic Rationale]

On-camera talent: [Founder / Customer / Creator / Employee — pick one]
Setting: [Specific location — "in front of the shop", "in the field", "at the kitchen counter"]
Wardrobe: [Brief direction — "branded polo", "work clothes", "casual everyday"]

TALK TRACK (delivered direct-to-camera):

[0:00–0:02] Hook — outcome-first
[Verbatim line]

[0:02–0:08] Setup — *just enough* context for the outcome to make sense
[Verbatim lines]

[0:08–0:20] Mechanism — why this worked
[Verbatim lines]

[0:20–0:28] Proof or specifics — numbers, names, screenshots
[Verbatim lines]

[0:28–0:35] CTA — one action, one line
[Verbatim line]

B-ROLL (cutaways layered over talk track):

[Timestamp] [Description]
[Timestamp] [Description]

ON-SCREEN TEXT (captions + emphasis):

- Auto-captions: on (white sans-serif, bottom third, safe-zone aware)
- Emphasis text: pull 2–3 key phrases from the talk track for big-text highlights — typically the hook, the number, and the CTA

---
Deliverables: 9:16 (primary — Reels/Stories/TikTok), 1:1 (secondary if running on Meta feed)
Aspect: 9:16
Length target: 30–45 seconds
```

### Sequencing principles
- **Outcome → Setup → Mechanism → Proof → CTA.** Never start with the setup.
- **Cuts every 2–4 seconds** to hold attention. Either talk-track cuts (jump cuts on the talent) or b-roll cuts.
- **No "Hey guys" or "What's up everyone" openings.** Dead air kills the hook.
- **The talent must believe the line.** A founder reading a script flatly is worse than a customer ad-libbing.

### When the user hands you a Yapper brief request
Hand off copy production for the talk track to the `direct-response-copywriter` skill. That skill handles the opener / hook / mechanism logic. This skill handles the format, sequencing, and b-roll architecture.

---

## Camera Settings Reference

Only relevant when outputting JSON prompts.

| Intent | Lens | Aperture | Effect |
|---|---|---|---|
| Premium product hero | 85mm | f/2.0–f/2.8 | Shallow DOF, cinematic |
| Informational/spec | 50mm | f/5.6–f/8 | Flat, even, readable |
| Lifestyle/environmental | 35mm | f/2.8 | Wide, contextual |
| Ingredient macro | 100mm macro | f/2.8 | Extreme close-up detail |
| UGC/phone-style | 28mm | f/1.8 | Casual, wide, amateur feel |
| Flat lay top-down | 35mm | f/5.6 | Even, no perspective distortion |

---

## Reverse-Engineering Checklist

Work through this before writing any brief or JSON key:

**Subject:** Hero element? Lit how and from where? What surface/context?
**Text hierarchy:** Headline, subtext, CTA? Font weight/size relationships? Badges, stars, logo?
**Color:** Dominant background color? Text/accent/product colors?
**Composition:** Where does each element sit? Split layout, centered, asymmetric?
**Style/mood:** Editorial, UGC, studio-commercial, meme-style, typographic?

---

## Variation Rules (for A/B Testing)

When generating design brief variations, change one creative dimension at a time:

| Variation type | What to change | What to keep |
|---|---|---|
| Copy only | Headlines, CTAs, benefit copy | Visual direction, layout |
| Visual treatment | Image style, grid vs. single | Copy |
| Tone shift | Aspirational vs. utilitarian mood | Structure |
| Platform reformat | Aspect ratio, layout density | Core message |

Label variations: `[concept-name]-v1`, `[concept-name]-v2`

---

## Aspect Ratio Guide

| Placement | Ratio |
|---|---|
| Feed square | 1:1 |
| Feed portrait (best performer) | 4:5 |
| Stories / Reels | 9:16 |
| YouTube / landscape | 16:9 |

Default to `4:5` if ratio is ambiguous.
