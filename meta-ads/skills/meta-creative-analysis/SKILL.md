---
name: meta-creative-analysis
description: Performance attribution and creative pattern mining for a Meta ad account. Use whenever the user asks to "analyze creative performance for [brand]", "mine the creative for [brand]", "what's working in [brand]'s Meta ads", "creative analysis for [brand]", "which creative is winning", "what messaging theme is winning", "which ad is converting best", or any account-level question about why some Meta creatives outperform others. Trigger when the user wants to understand *why* certain ads work — not just see numbers — across an account or campaign, and wants a structured brief. This is the skill for cohort-level performance attribution on a brand's own Meta ad account. Not for single-ad reverse-engineering (use creative-format-library) or competitor recon from the Meta Ads Library. Pairs with ad-creative-strategist — the analysis ends with directional next-test theses the strategist picks up.
version: 1.0.0
---

# Meta Creative Analysis

Mine a Meta ad account or campaign to identify winning creative patterns. Produce a structured analysis brief that diagnoses performance across four dimensions — format, copy, performance, visual — and ends with directional next-test recommendations.

This is **performance attribution**: every claim about why a creative is working must be grounded in metrics, not opinion. If the data is too thin to support a claim, say so explicitly. The brief is for the internal team, so be operator-direct — no client-deck polish, no hedging.

## Dependencies

Load these alongside this skill at the start of the analysis. They carry vocabulary and conventions the analysis depends on:

- **`meta-ads:creative-format-library`** — the 52-format taxonomy used for format classification
- **`google-ads:naming-conventions`** — the campaign/ad-set naming convention (used to read intent from names like `BOFU-SQL`, `TEACHER-EDITION`, etc. The conventions apply across platforms.)
- **`direct-response-copywriter`** — the copy-framework diagnostic vocabulary (hook types, mechanism presence, resistance type, PAS/AIDA, etc.)

If any of these aren't available, the skill still runs but flag the gap in the output (e.g., "Format library not loaded — formats are described, not classified").

## Workflow

```
1. Confirm scope interactively (client, campaign, window, focus dimensions)
2. Pull insights at 4 time windows (30d, 14d, 7d, 3d) for trend analysis
3. For each active ad:
   a. Pull creative image
   b. Classify primary format
   c. Diagnose copy framework
   d. Visual read
   e. Hook/hold read (video ads)
   f. Compute trend deltas
4. Rank ads on 4 metrics independently (CPA, Conv Rate, CTR, Spend Share)
5. Compute composite rank (average of individual ranks) + assign kill/scale/iterate verdicts
6. Synthesize winning theme across top performers
7. Generate 2-3 directional next-test theses
8. Output the brief
```

## Step 1 — Interactive scope confirmation

Always confirm scope before pulling data. Silent assumptions break the analysis. Use this opening:

> "Before I pull data, I need to confirm:
> 1. Which client / ad account?
> 2. Which campaign or ad set? (I can list active ones if you want.)
> 3. Time window — default 30 days with trend slices at 14d/7d/3d. Override?
> 4. Focus dimensions — default all four (format / copy / performance / visual). Drop any?"

If the user invokes with some of these already specified, only ask for what's missing. Don't re-ask things already provided.

If the user says "just pick" or skips a question, use these defaults: 30-day window with trend slices, all four dimensions, highest-spend active campaign in the account.

## Step 2 — Pull performance data

Use `mcp__plugin_meta-ads_meta-ads__insights_get` (or `meta_raw`) with the campaign or ad set ID. Pull these fields:

```
ad_name, impressions, clicks, ctr, cpc, cpm, spend, reach,
frequency, actions, cost_per_action_type, purchase_roas
```

For cohorts containing video ads, also pull the video engagement fields: `video_play_actions`, `video_thruplay_watched_actions` (3-second views come through `actions` as `video_view`). These feed the hook/hold read in Step 3.

Pull at the **ad level** by iterating per-ad if the wrapped tool doesn't return ad-level rows in one call. (This is a known limitation of the current Meta plugin.) For each of the 4 time windows (30d, 14d, 7d, 3d), pull insights per active ad. Build a metrics table in memory.

If the campaign has paused ads that delivered in the 30-day window, include them in the table — flag as PAUSED in the status column. They still teach you something about what got turned off and when.

## Step 3 — Per-ad analysis loop

For each active ad with enough delivery to be analyzable (>500 impressions OR >$50 spend in the window — default impressions floor). Each ad gets two analysis blocks: **Creative format** (what's on the image) and **Ad copy framework** (Meta API headline / body / description fields).

1. **See the creative — pick the tool by creative type.** You need to see it, not just read metadata.
   - **Static / carousel** → `mcp__plugin_meta-ads_meta-ads__ad_image_get`
   - **Video** (the creative has a `video_id`) → `mcp__plugin_meta-ads_meta-ads__ad_video_get`. Returns the spoken script as a timestamped transcript. Use it for every video ad — the thumbnail is one Meta-chosen frame and tells you almost nothing about the hook. **Keyframes are off by default and should stay off for cohort work** (a 10-ad cohort with frames on is 50 images, which crowds out the analysis). Add `include_keyframes=True` for the one or two ads where the visual is the open question.
   - **Pass the brand's `ad_account_id` explicitly on both tools.** Asset lookups are account-scoped: without it they silently degrade to a 64px thumbnail, and a 64px thumbnail is unreadable for on-image copy.
2. **Pull ad copy fields** via `creative_get` if `ad_get` only returns the creative ID. Capture headline, body, and description verbatim. These are different from the on-image copy.

3. **Build the CREATIVE FORMAT block** (what's on the image):
   - **Format:** Single label from the 43-format library (e.g., `#5 PAS`, `#26 Did-You-Know`). If hybrid, name the primary and add one line of rationale.
   - **Creative copy:** Transcribe the on-image copy verbatim, laid out as it appears top to bottom. If the thumbnail resolution is too low to read body-level on-image copy, say so explicitly — do not guess.
   - **Visual style:** One sentence covering imagery type (live photo / graphic / UGC / typography-only / spec diagram), layout (split / centered / band / etc.), and mood.

   **For video ads, this block covers the script instead:**
   - **Hook (first 3 seconds):** the transcript's opening line verbatim. This is the single highest-value read in the whole analysis — pair it with the hook rate in item 5. A weak hook rate plus a slow verbal open is a diagnosis. A weak hook rate with a strong spoken open points at the visual instead, and *that's* when to re-pull with `include_keyframes=True`.
   - **Script structure:** how the transcript moves (problem → agitate → mechanism → offer, testimonial arc, listicle, etc.). Map it to the 43-format library the same way.
   - **Messaging + theme:** the claims, proof, and offer as actually spoken — this is what clusters across the cohort in Step 5.
   - **Visual style:** only if you pulled keyframes — talking-head / UGC selfie / b-roll over voiceover / typography-driven / AI animation, plus whether on-screen text carries the message independently of the audio (most Meta video is watched muted).
   - If `ad_video_get` couldn't read the video (Meta gates `source` behind a Page token for some page-owned videos), say so in this block and mark the ad **`(creative unverified — copy-layer diagnosis only)`**. The performance read in item 5 still stands on its own.

4. **Build the AD COPY FRAMEWORK block** (Meta API fields). Each gets the verbatim text plus a ≤8-word clause on what it's doing:
   - **Headline:** "[verbatim]" — [what it's doing]
   - **Body:** "[verbatim — summarize only if >3 paragraphs]" — [what it's doing]
   - **Description:** "[verbatim]" — [what it's doing]

5. **For video ads, compute the hook/hold read.** This is where video performance actually gets diagnosed — the thumbnail tells you almost nothing:
   - **Thumbstop ratio** = 3-sec views ÷ impressions — does the opening frame stop the scroll?
   - **Hook rate** = 3-sec views ÷ video plays. Below 25% = the opening isn't earning attention (no downstream optimization fixes that); ~30% = strong; 40%+ = elite.
   - **Hold rate** = thruplays ÷ 3-sec views — does the middle keep people after the hook?

   The diagnostic value is in the *combination*: strong hook + weak hold = the opening works but the middle loses people (fix the middle, keep the hook). Weak hook = nothing downstream matters yet.

6. **Compute trend deltas.** For CPA, CTR, and Conv Rate compare 30d vs. 14d vs. 7d vs. 3d. If the last-7d metric is >20% worse than 30d → flag as **decaying**. If last-7d is >20% better → flag as **momentum**. Otherwise → **stable**.

7. **One-line synthesis** of why the ad is winning or losing, tied to specific metrics. Two sentences max. No abstractions — name the metric that proves the claim.

## Step 4 — Composite ranking math

This is the most important methodological piece. Get it right or the analysis points at the wrong winner.

1. Rank each active ad on each of these 4 metrics independently. Rank 1 = best, ascending.
   - **CPA** (lower = better)
   - **Conversion rate** (link clicks → conversions; higher = better)
   - **CTR** (higher = better)
   - **Spend share** (higher = better — Meta's auto-optimization vote)
2. **Composite rank = average of the 4 individual ranks.** Lowest average = composite winner.
3. Show ALL four individual ranks in the output, not just the composite. The reader needs to see WHO wins on each dimension to make sense of the composite.

**Edge cases:**
- If no conversions occurred in the window, drop CPA and Conv Rate from the composite. Fall back to CTR + Spend Share only and flag the gap loudly. Don't fabricate.
- If only one ad is active, skip ranking entirely. Just deep-dive that one ad.
- If an ad falls below the minimum-data floor (<500 impressions or <$50 spend), include it in the metrics table but **exclude from ranking**. Mark as "insufficient data."

**From ranks to verdicts.** After ranking, give every ranked ad one of three labels. The verdict answers the question the reader actually has ("what do I do with this ad?") — ranks alone don't:

- **KILL** — below the cohort on CPA, CTR, *and* trend after sufficient spend. No single strong signal to build on. No iteration saves it; every dollar it keeps spending is a dollar off a winner.
- **SCALE** — above-benchmark composite with stable or momentum trend. Room to add budget.
- **ITERATE** — mixed signal with one identifiable weak link: strong hook + weak hold, strong CTR + weak conv rate, or a concept that works in a format that doesn't. Name the one variable to change.

Ads that are "too new for trend read" or below the data floor get no verdict — killing an ad on thin data is how winners die early. The verdict says what to do with *existing* ads; the Step 6 theses say what to build *next*. Don't blur them.

## Step 5 — Theme synthesis

After ranking, look at the top 1-3 composite-ranked ads. What do they share?

Possible shared dimensions:
- Same on-image hook / messaging frame (loss aversion, outcome promise, identity targeting)
- Same format pattern (e.g., live photo + bold headline vs. spec-sheet graphic)
- Same body-copy opener type
- Same visual register (real photography vs. typographic vs. graphic)

State the dominant theme as **one sentence**. Be specific. "Loss aversion + dollar quantification + live-action proof scenes" beats "emotional appeal that resonates."

Tie the theme to evidence: which ads carry it, and which of the 4 metrics confirm it.

## Step 6 — Recommendation generation

Generate **2–3 directional next-test theses**. Each one has two parts:

1. **What to build** — name the source ad(s) by shorthand and specify what to keep or swap. Reference the ads' actual words, not abstractions. A junior copywriter reading this should be able to start a creative brief with zero follow-up questions.
2. **Why** — one sentence with the metric proof from THIS analysis. Name the number.

**Forbidden phrases.** These don't tell a junior reader anything actionable. Use the ad's actual words instead:
- "emotional register" / "functional register"
- "info-dense framing" / "info-dense body"
- "per-impression efficiency"
- "hybrid creative" without specifying what to combine
- "lean into" anything
- Any phrase that requires the reader to interpret what you mean

**Bad example** (fails the junior-reader test):

> Test angle: Hybrid creative — emotional hook + info-dense body.

**Good example** (passes):

> **Test angle 1: Swap Peace-of-Mind-10's headline for ad2a's headline.** Take Peace-of-Mind-10 as-is and replace the "Are You 50+ with Frustrating Dental Problems" headline with ad2a's "Did you know dental anxiety comes from the clinic, not the procedure." Keep everything else in Peace-of-Mind-10 the same (treatment list, $375 offer, body copy).
>
> Why: ad2a's headline drives the highest CTR in the cohort (2.52%). Peace-of-Mind-10's body drives 60% of spend share. Combining them tests whether you can stack both wins.

Do **not** write full image copy, body copy, headlines, or design briefs inside this skill's output. That's the `ad-creative-strategist` skill's job. End the recommendation block with:

> *Hand off to ad-creative-strategist for concept build.*

This separation matters. If the analysis skill duplicates the strategist's work, the outputs diverge and the team stops trusting both. Stay in lane.

## Step 7 — Output the brief

See `references/output-template.md` for the full markdown template. The required sections in order are:

1. **Account summary** — window, spend, conversions, CPA, active/paused counts, key flags
2. **Ad-level comparison table** — all active ads with metrics + format + composite rank + verdict (KILL / SCALE / ITERATE)
3. **Deep-dive on each ad** (or top 3 + bottom 1 if N > 10) — Creative format block (format / creative copy / visual style) + Ad copy framework block (headline / body / description, each verbatim) + Trend table + 2-sentence why-it-works synthesis
4. **Winning messaging theme** — one-sentence + evidence
5. **Recommendations** — 2–3 directional theses + handoff line

## Hard rules

These don't bend.

1. **Minimum data floor.** Ads with <500 impressions OR <$50 spend in the window appear in the metrics table but are excluded from composite ranking. Flag as "insufficient data."
2. **Trend decay rule.** Last-7d metric >20% worse than 30d → flag as "decaying." This catches winners-turning-into-losers before they drain budget.
3. **Composite math is independent ranks averaged.** Not a weighted blend, not an opinion-based pick. Show all 4 individual ranks in the output so the reader can audit.
4. **Recommendations stay directional.** Never write full image copy, headlines, or design specs. Point to the strategist instead.
5. **Always confirm scope interactively.** No silent assumptions about client, campaign, or window. The 30-second confirmation up front saves 10 minutes of wrong-direction analysis.
6. **Performance attribution requires evidence.** Every "this ad won because X" claim must be backed by which metric(s) prove it. If you're inferring without metrics, say so: "Likely because [reason] — couldn't confirm with available data."
7. **Junior-reader test.** Recommendations must reference specific ads by shorthand and say concretely what to keep / swap. No abstract framing terms — see Step 6's forbidden phrases list. If a sentence requires the reader to interpret what you mean, rewrite it.
8. **Verbatim creative copy.** The Creative format block transcribes on-image copy as it appears — top to bottom, exact wording. If the thumbnail is too low-resolution to read body-level on-image copy, say so explicitly. Never guess.

## Edge cases

| Situation | How to handle |
|---|---|
| Only 1 active ad in window | Skip composite ranking. Deep-dive the one ad. State explicitly that the analysis is a single-ad read, not a cohort comparison. |
| Paused ads delivered in window | Include in metrics table, mark as PAUSED. Treat their data as historical context — useful for understanding what got turned off. |
| Brand-new ads (<3 days old) | Exclude from trend analysis. Note as "too new for trend read." Still rank them but flag the small-sample risk. |
| Carousel / multi-image ads | Analyze the primary image (the one `ad_image_get` returns). Note that carousel-level analysis is partial in v1. |
| Video ads | Use `ad_video_get` for the spoken script. Diagnose the hook from the opening line, then read it against the hook/hold metrics in Step 3, item 5. Keyframes stay off unless the visual is the open question. Never fall back to the thumbnail when the script is readable. |
| Video ad where `ad_video_get` fails | Two causes: Meta gates the video `source` behind a Page access token for some page-owned videos, or the machine can't transcribe locally (Intel Mac). Either way the performance read is unaffected — hook rate, hold rate, and thumbstop ratio (Step 3, item 5) still diagnose the video without reading it. Do the visual read from keyframes or the thumbnail, and mark the ad **`(creative unverified — copy-layer diagnosis only)`** so a copy-only read never gets mistaken for a full creative diagnosis. |
| No conversions in window | Drop CPA + Conv Rate from composite. Use CTR + Spend Share only. Flag the gap explicitly — readers need to know the analysis lost two of its four signals. |
| Account has multiple active campaigns | At scope confirmation, ask which campaign. If user says "the whole account," loop the analysis per campaign and show results grouped by campaign. Don't blend campaigns into one ranking — different campaigns serve different objectives. |
| Large cohort (N > 10 active ads) | Compress the comparison table to key metrics only (drop CPM, frequency, reach). Auto-limit deep-dive to top 3 + bottom 1 for contrast. Note that full per-ad breakdowns are available on request. |

## Voice

This brief is for a junior team member to grab and act on. Write so they don't need to interpret you.

- Short sentences. No filler.
- Reference specific ads by shorthand when you're recommending something (e.g., "test a variant of Peace-of-Mind-10 that swaps in ad2a's headline").
- Numbers in the open.
- If data is thin, say so in five words, not a paragraph.
- Plain English, not buzzwords. No "register," no "framing," no "lean into."
- Push back when the data contradicts intuition.
- Don't write to win awards. Write to be acted on.

**The reader test:** A junior copywriter should read the recommendations section and know exactly what to build next, with no follow-up questions. If a sentence in your draft would make them ask "what do you mean?" — rewrite it.

The brief is a working document, not a polished deliverable. Don't manufacture certainty.
