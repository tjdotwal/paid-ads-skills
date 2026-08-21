---
name: advertising-performance-manager
description: |
  Performance review across Google Ads and Meta for a single brand, against a 3-month day-matched baseline. Use this skill when the user says "performance check", "how are we performing", "how did last week go", "is performance up or down", "why is CPA up", "why are conversions down", or asks about CPA, conversion volume, or CVR trends versus recent months. Also trigger on "weekly review", "month-over-month", or any question about whether results are getting better or worse. It knows the baseline math, the bucket thresholds, and the Meta multi-event conversion counting that default metrics get wrong. Load `google-ads:naming-conventions` alongside it when drilling. For whether spend is on schedule, use `budget-pacing-manager` instead — this skill is about whether that spend is producing leads at the right cost.
version: 1.0.0
---

# Advertising Performance Manager

Pacing asks whether the money went out on schedule. This asks whether it bought anything.

Two phases: **triage** (are CPA and conversion volume better or worse than recent months) and **drill** (why, and what to do).

## Inputs

Metrics come **live from the APIs**. Account IDs come from `config/budget.md` if present, otherwise from `GOOGLE_ADS_CUSTOMER_ID` and `AD_ACCOUNT_ID`, otherwise ask.

Run `date +%Y-%m-%d` first, every time. Every window in this skill is relative to today.

`target_cpa` in config, if set, is a secondary reference only. **Baselines drive the buckets, not the target.** A CPA under target but 40% worse than last quarter is still a problem worth naming.

## Counting conversions — Meta's defaults are wrong for this

A single Meta campaign often fires several conversion events: a custom pixel event per thank-you page, plus a native lead-form event. Default `conversions`-style fields hide this, so you have to aggregate manually or the numbers come out low.

When calling `insights_get`, return the `actions` array. Per campaign or ad set:

- **Sum** `value` across every `action_type` starting with `offsite_conversion.custom.` — these are the deliberately configured pixel events.
- **Plus** `action_type == "lead"` for native lead forms.
- **Skip** Meta's auto-added duplicate counters: `offsite_complete_registration_add_meta_leads`, `offsite_search_add_meta_leads`, `offsite_content_view_add_meta_leads`, `onsite_conversion.lead_grouped`. These re-categorize the same fill — counting them inflates results.
- **Skip** engagement entirely: `post_engagement`, `link_click`, `landing_page_view`, `video_view`, reactions, comments. Not conversions.

If both `lead` and a custom event appear for the same campaign and look like the same fill counted twice, prefer the custom event — that's what was deliberately set up.

**Google Ads** — `metrics.conversions` already aggregates across configured conversion actions, so the headline number needs no special handling. For a drill breakdown, segment by `segments.conversion_action_name`.

State which events you counted in the output. A conversion number whose definition is invisible can't be checked.

## Comparison Math

**Baseline = the three full calendar months before the current one.** On June 9, that's the average of March, April, and May.

**Conversion volume — day-matched:**

```
current_volume  = MTD conversions, all active channels
baseline_volume = average of (conversions through the same day-of-month) for each baseline month
volume_delta    = (current − baseline) / baseline
```

On June 9, compare against the average of May 1–9, April 1–9, March 1–9. Full-month comparison would make every early-month check look catastrophic.

**CPA — full-month rate, no day-matching:**

```
current_cpa  = MTD cost / MTD conversions
baseline_cpa = average of each baseline month's full-month CPA
cpa_delta    = (current − baseline) / baseline
```

Rates are directly comparable regardless of window length — dollars-per-conversion either way.

**CVR — same treatment as CPA:**

```
current_cvr  = MTD conversions / MTD clicks
baseline_cvr = average of baseline months' full-month CVR
```

CVR gives context but **does not drive the bucket**. It explains the why: CPA up with CVR flat is an auction problem (CPC/CPM rising). CPA up because CVR fell is a creative or landing page problem. The drill separates them.

## Bucket Logic

| Bucket | Trigger | Action |
|---|---|---|
| 🔴 BAD | CPA > 120% of baseline **OR** volume < 80% of day-matched baseline | Drill |
| 🟢 GOOD | CPA < 90% of baseline **OR** volume > 110% of day-matched baseline | Scale or hold |
| 🟡 FINE | Within ±10% on both | No action |
| 🆕 NEW | Under one full month of history | No baseline — report raw and say so |

If both 🔴 and 🟢 trigger (CPA down 30% *and* conversions down 25%), **🔴 wins.** A volume collapse is the more actionable signal — cheap conversions you're not getting enough of is still a problem.

Under 5 MTD conversions, tag `⚠️ small sample` and don't bucket hard. Early-month low counts produce noisy CPA.

## Phase 1 — Triage

1. Pull MTD cost, clicks, conversions per channel.
2. Pull the same day-matched window for each of the three baseline months.
3. Compute deltas, assign a bucket at total level, then per channel.
4. Report.

### Output

Same register as pacing — a message, not a report. Headline first, numbers in the open, no preamble.

```
Performance — 🔴 CPA up 34% (day 12, vs Mar–May baseline)

CPA $114 vs $85 · 24 conv vs 31 day-matched (−23%) · $2,736 spent
  Google  $92 vs $78 (+18%)    14 conv vs 19 (−26%)
  Meta    $148 vs $94 (+57%)   10 conv vs 12 (−17%)

CVR 2.1% vs 2.4% — down, but not enough to explain a 57% Meta CPA jump.
Meta CPMs are the likelier cause. Drill Meta?
```

Healthy:

```
Performance — 🟢 CPA down 12% (day 12, vs Mar–May baseline)

CPA $75 vs $85 · 38 conv vs 31 day-matched (+23%) · $2,850 spent
  Google  $71 vs $78 (−9%)    22 conv vs 19 (+16%)
  Meta    $80 vs $94 (−15%)   16 conv vs 12 (+33%)

Conversions counted: Google all actions; Meta custom pixel events + lead forms.
```

Always name which conversion events were counted on Meta.

## Phase 2 — Drill

1. Break the flagged channel down by campaign for MTD and the baseline window.
2. Identify whether the change is concentrated in one campaign or spread across all. **Concentrated and spread mean different causes** — one campaign breaking is a campaign problem; everything moving together is an auction, tracking, or seasonality problem.
3. Separate the mechanism:

| Symptom | Likely cause | Where to look |
|---|---|---|
| CPA up, CVR flat, CPC/CPM up | Auction pressure | Competitor entry, seasonality, bid strategy change |
| CPA up, CVR down, CPC flat | Creative fatigue or landing page | Frequency (Meta), ad-level CTR, LP changes |
| Volume down, CPA flat | Reduced delivery | Impression share lost to budget, paused campaigns, audience saturation |
| Volume down, CPA down | Tracking break | Conversion action status, pixel firing, recent site deploy |
| Everything down at once | Tracking break before anything else | Verify conversions are recording before diagnosing performance |

**Check tracking first when the drop is sharp and broad.** A pixel that stopped firing looks exactly like a performance collapse, and every hour spent optimizing against phantom data is wasted.

4. Load `google-ads:naming-conventions` before reading campaign names so funnel stage and intent parse consistently.

### Drill output

State the finding, then the evidence, then one recommendation per finding:

```
Meta drill — CPA up 57%, concentrated in one campaign

  retargeting-warm-bofu    $198 CPA vs $91 baseline    6 conv, $1,188
      Frequency 4.7 (was 2.1). Audience saturated — same people, more impressions.
      CTR 0.8% vs 1.6%. Creative is burnt.

  prospecting-cold-tofu    $104 CPA vs $97 baseline    4 conv, $416
      Within noise. Leave it.

Recommend:
  1. Refresh retargeting creative — it's a frequency problem, not a bidding one.
     Raising bids on a saturated audience buys more of the same fatigue.
  2. Expand the retargeting window (30d → 60d) to enlarge the pool while
     new creative is produced.

Execute #2 now? #1 needs creative — hand to ad-creative-strategist.
```

### Recommendation rules

- **One recommendation per diagnosed cause.** No lists of everything possible.
- **Name the mechanism, not the metric.** "Refresh creative, frequency is 4.7" beats "improve CPA."
- **Say when the fix isn't a settings change.** Creative fatigue needs creative. Hand off to `creative:ad-creative-strategist` rather than proposing a bid tweak that won't help.
- **Say when the answer is do nothing.** Inside ±10% on a small sample is noise. Acting on noise makes results worse and destroys the baseline you'd measure against.
- **Never recommend scaling on fewer than 10 conversions** in the window. Too volatile.

## Common pitfalls

- **Comparing MTD against full baseline months.** Guarantees a false alarm every time. Day-match volume.
- **Using Meta's default conversion field.** Undercounts multi-event campaigns and makes CPA look worse than it is.
- **Summing every Meta action type.** Overcounts via the duplicate counters. Both errors are common; both are avoidable.
- **Diagnosing performance before verifying tracking.** Always rule out a broken pixel or a disabled conversion action first.
- **Averaging CPA across channels by taking the mean of two CPAs.** Compute total cost ÷ total conversions. Channel CPAs weight differently.
- **Bucketing on a 3-conversion sample.** Tag small samples and hold.

## What this skill does NOT do

- Check whether spend is on schedule. That's `budget-pacing-manager`.
- Multiple brands in one run. One account at a time.
- Attribution modelling or incrementality. Platform-reported conversions only, and it says so.
- Creative analysis. `meta-ads:meta-creative-analysis` does cohort-level creative attribution.
