---
name: meta-account-audit
description: Foundational 5-step audit of a Meta ad account — run it before touching a single setting. Use whenever you are taking over an unfamiliar Meta account ("audit this account", "takeover audit", "what am I inheriting"), OR doing a deep dive on an existing account that's been running a couple of quarters without major changes ("deep dive into [brand]", "foundational review", "what's structurally wrong with this account", "why can't [brand] scale", "full account audit"). Also trigger on "audit [brand]'s Meta account", "health check the whole account", or any request to diagnose account-level problems before proposing strategy. This is the diagnostic layer that runs BEFORE strategy — it reads existing data in a fixed sequence and finds the cause, not the symptom. Not for weekly pulse checks not for creative pattern mining (use meta-creative-analysis) — this is the one-time structural read of the whole account.
version: 1.0.0
---

# Meta Account Audit

A ~45-minute foundational audit of a Meta ad account. No new ads launched, no budgets changed, no campaigns restructured — just reading the data that's already there, in an order where each finding explains the next.

The core insight this skill encodes: most media buyers see "ROAS is down" and jump to "launch new ads." That treats the symptom. This sequence finds the cause — and 90% of the time the account doesn't need a new strategy, it needs the foundational problems fixed first.

**Two modes, same sequence:**

- **Takeover audit** — new brand, before we touch anything. Emphasis on what we're inheriting and what's silently broken.
- **Deep dive** — an account we've run for 2+ quarters without major changes. Emphasis on slow-building structural problems (audience exhaustion, retargeting mirages, creative staleness) that weekly pulse checks don't surface.

Ask which mode applies if it isn't obvious from the request. It changes the framing of the brief, not the checks.

## Dependencies

Load alongside this skill:

- **`google-ads:naming-conventions`** — to read intent from campaign/ad-set names (prospecting vs. retargeting, funnel stage)
- **`meta-ads:creative-format-library`** — for classifying creative in Step 5

If either isn't available, run anyway and flag the gap in the output.

## Why the order matters

The five steps are a causal chain, not a checklist. Each layer explains the one before it:

1. The **metric cascade** tells you *what* moved.
2. **Frequency and rolling reach** tell you whether the traffic problem is audience exhaustion.
3. **Conversion source** tells you whether the "good" numbers are real acquisition or credit-taking.
4. **Infrastructure checks** tell you whether any of the data you just read can be trusted.
5. **Creative mix** tells you whether the account is even capable of reaching new people.

Don't reorder, and don't skip ahead to recommendations mid-audit. A finding in Step 4 (e.g., double-firing pixel) can invalidate a conclusion you drew in Step 1 — that's why all five run before any verdict.

## Step 0 — Scope confirmation

Confirm before pulling data:

1. Which client / ad account? (`ad_account_list` if unsure)
2. Mode — takeover or deep dive?
3. Windows — default: last 90 days vs. the prior 90 days. Override only if the account is too young (see Edge cases).
4. Any client-specific benchmark overrides? (Defaults below.)

Then state the **audit universe** before analyzing anything: active campaigns, ad sets, and ads (counts from `campaign_list`/`adset_list`/`ad_list`). Teams routinely believe they have 40 active ads and actually have 200 — the count itself is sometimes the first finding, and it defines what the rest of the audit covers.

## Benchmarks (defaults — overridable per brand)

| Signal | Healthy | Warning | Red |
|---|---|---|---|
| Frequency (90d, account-level) | < 3 | 3–6 | > 6 |
| Rolling reach (net-new share of monthly reach) | > 20% | 10–20% | < 10% |
| Layer-metric shift (90d vs. prior 90d) | < ±10% | ±10–20% | > ±20% |

These come from the audit methodology this skill is built on (Marin Istvanic). State them as defaults in the brief; adjust per vertical/budget when the operator says so, and note the override in the output.

## Step 1 — Metric cascade (90d vs. prior 90d)

Don't start with the ads. Start with the numbers.

Pull account-level insights for both windows using `mcp__plugin_meta-ads_meta-ads__insights_get` with `since`/`until` (two calls — the presets can't express "prior 90 days"):

```
fields: spend, impressions, clicks, ctr, cpc, cpm, reach, frequency,
        actions, cost_per_action_type, action_values
```

Compute and walk the deltas in **this exact order**:

```
spend growth → CPM → CTR → CPC → cost per add-to-cart → CPA → AOV → conversion rate
```

(Cost per ATC and CPA come from `cost_per_action_type`; AOV = purchase value ÷ purchases from `action_values`/`actions`; conversion rate = purchases ÷ link clicks. If the brand's conversion event isn't purchases — leads, bookings — substitute the equivalent event and skip AOV.)

The sequence matters because each layer explains the next. If CPA is up 30%, the cascade tells you whether that's because:

- **CPM spiked** → traffic got expensive (auction/audience problem)
- **CTR dropped** → creative is fatiguing
- **Conversion rate fell** → funnel/landing-page problem
- **AOV shifted** → customers buying cheaper options (offer/merchandising problem)

Name the *first* layer in the chain that broke. That's the cause. Everything downstream of it is a symptom.

**Bottleneck triage** — before anyone blames the creative, use the cascade to rule out non-creative causes:

- High CTR but low conversion rate → landing page or offer problem, not creative
- Low CTR but the landing page converts fine → creative is the bottleneck
- Low reach + high CPM → audience saturation or targeting problem (Step 2 confirms)

This takes minutes and prevents the most expensive audit failure: prescribing new creative when the funnel is what's broken.

## Step 2 — Frequency and rolling reach

This is where the biggest hidden problems live.

**Frequency:** account-level `frequency` over the 90d window (already pulled in Step 1). Score against the benchmark table.

**Rolling reach (net-new share):** the API has no direct "net-new reach" metric, so approximate it:

1. Pull cumulative `reach` for days 0–90 and days 0–60 (two `insights_get` calls with custom ranges).
2. Net-new people in the latest 30 days ≈ `reach(0–90) − reach(0–60)`.
3. Pull `reach` for the latest 30-day slice alone. Net-new share = net-new ÷ 30d reach.

State clearly in the brief that this is an approximation.

**The pattern to catch:** frequency at 3–6, rolling reach declining for months, and nobody noticed because campaign-level ROAS still looked acceptable. That acceptable ROAS is a mirage — it's propped up by retargeting the same people over and over. The top of funnel is starving, and the day those retargeting audiences are exhausted, the whole account collapses. (Real accounts have been found with *lifetime frequency of 37* — every person in the addressable market had seen the ads 37 times. No media-buying trick fixes that.)

**CPMr — the mirage, quantified.** CPMr (cost per 1,000 unique people reached) = CPM × frequency, computable from the Step 1 pull. Compare it across the two 90d windows alongside CPA:

- CPMr rising AND CPA rising → creative and audience are both exhausted.
- CPMr rising while CPA holds → the audience is saturating but conversions are coming from the warm pool. The account is measuring repeat exposure as performance. Feed this straight into Step 3's NC-ROAS check — it's the same mirage from two angles.

If frequency is red, also pull lifetime-ish frequency (widest available custom range) to size the exhaustion.

## Step 3 — Where conversions actually come from

The question: what percentage of spend goes to existing customers vs. genuinely new people?

**What the API can tell you (proxy):**

1. `adset_list` + `adset_get` for active ad sets — classify each as **prospecting** (broad / interest / lookalike targeting) or **retargeting** (website custom audiences, customer lists, engagement audiences). Use naming conventions from `naming-conventions` as a cross-check, but trust the actual targeting over the name.
2. Per-adset `insights_get` → spend and conversions split by that classification.
3. Report spend share and conversion share for retargeting vs. prospecting.

**What needs a MANUAL CHECK (flag in the brief, don't guess):**

- **NC-ROAS from third-party attribution** (Triple Whale, Northbeam, or platform new-vs-returning data). This is the decisive number. The canonical failure: a "best performing" catalog campaign showing 4.0 ROAS in Ads Manager while third-party attribution shows **0.7 new-customer ROAS** — almost every conversion an existing customer who would've bought through email anyway. The campaign wasn't acquiring customers; it was taking credit for sales that were already going to happen, while eating the prospecting budget.

If retargeting-classified spend is a large share of total AND Step 2 flagged frequency, treat platform ROAS as unreliable until NC-ROAS is checked. Say so plainly.

## Step 4 — What's silently broken

These aren't performance problems — they're infrastructure problems, and they make every other optimization decision unreliable because the data feeding it is wrong. A red finding here retroactively caveats Steps 1–3; say which conclusions it touches.

**API-checkable:**

- **Exclusions attached?** For every retargeting/prospecting ad set (`adset_get`), check whether purchaser/customer exclusion audiences are attached at all, and note audience sizes where visible. A suspiciously small exclusion audience is the tell — the canonical case: a Klaviyo buyer-exclusion list under 1,000 people on a brand with tens of thousands of customers. The exclusion was doing nothing; they'd retargeted existing buyers for three years thinking they were excluded.
- **Destination URLs:** `ad_get`/`creative_get` for active ads — pull link URLs. Flag anything pointing to the wrong page, a dead page, or inconsistent UTM tagging. If reachable, spot-check that top-spend URLs resolve.

**MANUAL CHECKS (list explicitly in the brief):**

- Exclusion-list sync: does the CRM/Klaviyo customer count roughly match the synced audience size in Meta?
- Audience miscategorization: are newsletter subscribers being counted as "existing customers" (or vice versa), making segment data unreadable?
- **Pixel double-firing:** checkout events firing twice make the funnel look 2× healthier than reality. Verify in Events Manager (test events). Heuristic red flag from the API side: conversion rate wildly above vertical norms, or purchases ≈ 2× add-to-carts pattern anomalies.

## Step 5 — Creative mix

1. `ad_list` + `creative_list` for active ads; join with per-ad spend from insights. Compute **% of spend on video vs. image**.
2. For products that need explanation — supplements, subscriptions, health, anything considered-purchase — image ads mostly *retarget*: they remind people who already know the brand, they don't educate new people. Videos that explain, demonstrate, or tell a story are what genuinely reach new people. An account running 90% image ads that "can't scale" is usually just recycling the same warm audience (which Step 2's frequency finding will corroborate — connect the two in the brief).
3. **Same-thumbnail check:** pull thumbnails via `ad_image_get`/`creative_image_get` for the video ads. Five different videos with identical thumbnails get treated by Meta as one ad — the creative "diversity" is an illusion. Eyeball the images; report duplicates.
4. Classify the active creative spread against the format library if loaded (one line per format cluster, not a full creative analysis — that's `meta-creative-analysis`'s job).

## Output — the audit brief

An audit is a hand-off deliverable, so it earns its length — case 4 under "What earns extra words" in the plugin `CLAUDE.md`. But every section still obeys one-line-per-finding.

Structured chat brief, internal voice, this exact structure:

```
# Meta Account Audit — [Client] ([mode], [date])

## Scorecard
| Step | Check | Status | One-line finding |
(🟢 healthy / 🟡 warning / 🔴 red / ⚪ needs manual check — one row per check)

## The causal chain
[3–6 sentences MAX: what moved, and the FIRST layer that broke. This is the
"cause not symptom" verdict. If infrastructure findings undermine the data,
lead with that. This is the only prose block in the brief.]

## Findings by step
[Steps 1–5. One line per finding: the number, the verdict, what it means.
Cite the metric that proves each claim. No paragraphs.]

## Manual checks required
[Numbered: what to check, where (Events Manager, Klaviyo, Triple Whale...),
and what answer confirms or clears the flag. One line each.]

## Fix list (ordered by severity, not effort)
[Infrastructure fixes first — they unblock trust in everything else.
One line each: what to fix, which finding it came from. Directional only.]
```

The Scorecard is the whole audit for a reader in a hurry. If someone can read only that table and know what to do first, the brief works.

**What this brief is not:** a strategy document. No new creative concepts, no budget reallocations, no restructure plans. End with handoffs:

> *Creative gaps → ad-creative-strategist. Creative pattern mining → meta-creative-analysis. Ongoing monitoring → advertising-performance-manager.*

If the user asks for a stakeholder-facing version, rebuild it as a a branded docx (with a docx styling skill) — but the chat brief comes first.

## Hard rules

1. **Complete all five steps before any verdict.** A Step 4 finding can invalidate a Step 1 conclusion. No recommendations mid-audit.
2. **Cause, not symptom.** Every "X is broken" claim names the metric and the layer of the cascade that proves it.
3. **Never guess at manual-check items.** NC-ROAS, exclusion sync, and pixel firing cannot be read from the API. Flag them ⚪, specify where to look, move on.
4. **Approximations are labeled.** The rolling-reach math is a proxy; say so.
5. **The audit changes nothing.** Read-only. If the operator asks you to fix something mid-audit, finish the audit first — the fix list is ordered by severity for a reason.
6. **Benchmarks are defaults, not laws.** Note any client-specific override the operator gives, and apply it consistently.

## Edge cases

| Situation | How to handle |
|---|---|
| Account younger than 180 days | Shrink to the longest symmetric split available (e.g., 45d vs. 45d). Flag reduced confidence; skip trend claims under 30d per window. |
| Lead-gen / non-ecom client | Swap purchases → primary conversion event throughout the cascade; drop AOV. Note the substitution. |
| No third-party attribution in the stack | NC-ROAS stays ⚪ with a recommendation to pull Shopify (or equivalent) new-vs-returning as a stopgap. |
| Ad-level insight calls rate-limit on big accounts | Classify ad sets first; only pull ad-level data for the top ~80% of spend. Note the cutoff. |
| Operator wants "just the frequency check" | Run the step they asked for, but say what the full sequence would add — partial audits miss cross-step causes (e.g., creative mix explaining frequency). |
| Account structure is CBO-heavy / Advantage+ | Targeting reads are limited; classify what's visible, flag ASC campaigns as partially opaque, lean harder on the manual NC-ROAS check. |

## Voice

Operator-direct, numbers in the open, short sentences, no hedging padding. If data is thin, say so in five words. Push back when the data contradicts what you (or a stakeholder) believe — that's the entire value of an audit. Don't manufacture certainty, and don't soften a red flag because the account is a new engagement.

Length is governed by "Output Discipline" in the plugin `CLAUDE.md`. The audit is long because it has an audience beyond the operator — that is not licence for paragraphs under each finding.
