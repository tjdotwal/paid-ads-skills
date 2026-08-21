---
name: budget-pacing-manager
description: |
  Budget pacing review and reallocation across Google Ads and Meta for a single brand. Use this skill when the user says "pacing check", "run a pacing scan", "am I on pace", "budget pacing", "where should I move budget", "reallocate budget", or asks anything about whether spend is ahead of or behind schedule this month. Also trigger on "am I going to overspend", "why is spend behind", or any question about daily budget caps versus monthly intent. It knows the day-aware tolerance band, the pacing formula, and the conversion-volume + CVR reallocation logic. Load `google-ads:naming-conventions` alongside it when drilling so campaign names interpret consistently. For whether that spend is producing leads at the right cost, use `advertising-performance-manager` instead — this skill is about whether spend is on schedule.
version: 1.0.0
---

# Budget Pacing Manager

Three phases: **triage** (is spend on schedule), **drill** (which campaigns are the problem), **execute** (push approved changes).

The goal is to end the month on budget with spend concentrated where it's actually producing leads. Not to make small daily tweaks that add up to noise.

## Why this exists

The failure mode isn't the arithmetic — it's missing the hot hand. When one campaign in one channel is producing leads cheaply, budget doesn't shift toward it fast enough, and the month ends with spend spread evenly across things that performed unevenly.

## Inputs

**Intent comes from `config/budget.md`** in this plugin (see `config/budget.example.md`). That file holds the one number no API can supply: what you meant to spend this month. If it's missing, ask for `month_total` and the per-channel split, and say the answer is unsaved.

**Actuals come live from the ad platforms.** Never from a spreadsheet — a sheet is a stale snapshot of what the APIs already know.

Run `date +%Y-%m-%d` at the start of every run. Never rely on a date already in context.

### Pulling month-to-date spend

**Google Ads** — `mcp__plugin_google-ads_google-ads__execute_gaql_query`:

```sql
SELECT metrics.cost_micros, metrics.clicks, metrics.conversions
FROM customer
WHERE segments.date BETWEEN '<first-of-month>' AND '<today>'
```

Cost is in **micros** — divide by 1,000,000. Pass `login_customer_id` only if the account sits under a manager account.

**Meta** — `mcp__plugin_meta-ads_meta-ads__insights_get` with `since` = first of month, `until` = today, at account level. Read `spend`, `clicks`, and the `actions` array.

If a channel's pull fails, say so and report the other channel alone. Never present one channel as the whole picture, and never silently treat a failed pull as zero spend.

## Pacing Math

```
days_elapsed   = today's day of month
days_in_month  = total days in current calendar month
expected_pct   = days_elapsed / days_in_month
expected_spend = month_total × expected_pct
pacing_pct     = (mtd_spend − expected_spend) / expected_spend
```

- Negative → under-pacing (month ends short)
- Positive → over-pacing (will overspend)

**Divide by `expected_spend`, not by `month_total`.** This is the difference between a useful metric and a misleading one. Variance-from-expected reads as "I'm X% short of where I should be today," and it stays stable as the month progresses — 50% behind on day 3 still reads −50% on day 15 if the daily rate doesn't change. Dividing by `month_total` makes early-month problems look trivial and hides them until it's too late to correct.

Derived:
- `forecasted_eom = mtd_spend / expected_pct`
- `dollar_variance = forecasted_eom − month_total`

### Tolerance band widens early in the month

| Days into month | Tolerance |
|---|---|
| 1–6 | ±15% |
| 7–13 | ±10% |
| 14+ | ±5% |

`tolerance = 0.15 if days_elapsed <= 6 else 0.10 if days_elapsed <= 13 else 0.05`. Flag when `abs(pacing_pct) > tolerance`.

Why: when `expected_spend` is small (day 3 = 10% of total), a small dollar variance reads as a huge percentage. Flagging everything is alarm fatigue. As `expected_spend` grows, absolute dollars become the real signal, so tighten.

### Worked example

June 3, `month_total` = $10,000, `mtd_spend` = $542.27:

- `days_elapsed` 3, `days_in_month` 30, `expected_pct` 10%
- `expected_spend` = $1,000
- `pacing_pct` = (542.27 − 1000) / 1000 = **−45.77%**
- Day 3 → ±15% band → **flagged**
- `forecasted_eom` = 542.27 / 0.10 = $5,423 → **$4,577 under** by month end

At day 5 with `pacing_pct` of −12%, that's inside the ±15% early band — no flag.

## Phase 1 — Triage

1. Read `config/budget.md`.
2. Pull MTD spend per channel.
3. Compute `pacing_pct` at total level, then per channel.
4. Report. If total is inside the band but a channel is badly off, still surface it — offsetting channels can hide a starving one.

### Output

Reads like a message from a colleague, not a report. You're supporting one decision — what to do about pacing — and everything else is noise.

- No preamble. No "I've recomputed pacing…", no restating today's date as a sentence.
- Compact lines, not tables. Tables waste vertical space and read as a report.
- Context goes in parentheses, not sentences.
- Numbers in the open. Never a percentage without the dollars behind it.

On pace:

```
Pacing — on track (day 12 of 30)

$4,180 spent vs $4,000 expected · +4.5% · forecast $10,450 vs $10,000
  Google  $2,510 vs $2,400 (+4.6%)
  Meta    $1,670 vs $1,600 (+4.4%)
```

Off pace:

```
Pacing — 🔴 under by 28% (day 12 of 30)

$2,880 spent vs $4,000 expected · forecast $7,200 vs $10,000 (−$2,800)
  Google  $1,010 vs $2,400 (−58%)  ← the problem
  Meta    $1,870 vs $1,600 (+17%)

Drill Google?
```

Only prompt to drill when something is actually flagged.

## Phase 2 — Drill

1. Pull campaign-level spend and daily budgets for the flagged channel, MTD.
2. Pull **trailing 14 days** of conversions, clicks, and cost per campaign.
3. Identify which campaigns are under- or over-spending against their share.
4. Run supply diagnostics on anything that can't spend its allocation.

### Decision logic

**Primary signal: trailing-14-day conversion volume + conversion rate.**

- High volume + high CVR → hot hand. Boost.
- Low volume + low CVR → dead weight. Trim.
- High CVR + low volume → likely supply-constrained. Run diagnostics before boosting.
- Low CVR + high volume → wasting spend regardless of total conversions. Trim.

CPA is a tiebreaker, not the primary signal. A $20 CPA at 2 conversions/month rarely beats a $40 CPA at 50 conversions/month for lead gen.

**Why 14 days, not MTD?** Early in the month MTD samples are too small for confident decisions. Late in the month MTD includes pre-optimization spend that no longer reflects current performance. Use MTD for pacing math, trailing 14 for decisions.

### Supply diagnostics

**Google Ads — campaign can't spend its budget?** Check in order:

1. `search_impression_share_lost_budget` > 20% → budget is the bottleneck. Raise it.
2. `search_impression_share_lost_rank` > 40% → bidding or quality is the bottleneck, not budget. Flag separately; raising budget won't help.
3. `search_impression_share` < 30% with neither above → keyword set is too narrow. Send to `keyword-planner:keyword-research`.
4. Impression share healthy but spend still capped → search volume is the real constraint. Reallocate to Meta.

Never claim a campaign can scale without checking impression share first. "Increase budget" on a campaign losing share to rank burns money.

**Meta — ad set can't spend its budget?**

1. Frequency > 3 → audience saturated.
2. Small remaining audience → expand targeting or accept the cap.
3. Otherwise the daily cap is the constraint. Raise it before moving budget out of the channel.

### Cross-channel reallocation

**Move A → B when:** A is structurally underspending (Google: no search volume; Meta: saturated) **and** B has capacity **and** B's CVR/volume justifies it.

**Don't when:** A is only underspending because its caps are set conservatively — raise A's caps first. Or B's strong performance rests on fewer than 10 conversions in the trailing 14 days. Too volatile.

### Budget conservation

By default the sum of all daily budget changes is **zero**. This skill reallocates; it does not raise totals.

Exceptions need explicit approval:
- **Catch-up:** more than 10% behind past the halfway mark → propose temporarily raising caps.
- **Total cut:** more than 10% ahead past halfway with nothing able to absorb a trim → propose lowering caps across the board.

Never change the monthly total silently.

### Recommendation output

One line per change, with the reason and the arithmetic proof that it nets to zero:

```
Google — reallocate $47/day
  ↓ brand-awareness-tofu           $60 → $28  (−$32)  3 conv / 0.4% CVR trailing 14
  ↑ demo-request-bofu              $45 → $77  (+$32)  31 conv / 4.1% CVR, losing 34% IS to budget

  Net: $0/day. Monthly total unchanged.

Execute?
```

## Phase 3 — Execute (only on explicit confirmation)

**Google Ads** — `update_campaign_budget` or `update_budget_amount`. Budgets are in **micros**: $135.00 = `135000000`. Convert carefully; a factor-of-1000 error here spends real money.

**Meta** — `adset_update` or `campaign_update` with the new daily budget. Meta takes **minor units**: $45.00 = `4500`.

After executing:

1. Read back every changed entity and confirm the new value.
2. Report what changed, old → new, and re-verify the net is zero.
3. If any single change fails, stop. Report which succeeded and which didn't — a half-applied reallocation is worse than none, because the total no longer reconciles.

## Common pitfalls

- **Micros and minor units.** Google in micros, Meta in cents. Mixing them is the highest-cost mistake available here.
- **Trusting a cached date.** Run `date` every time. Pacing is entirely date-dependent.
- **Reporting a failed pull as zero spend.** That reads as catastrophic under-pacing and invites a wrong correction.
- **Treating a removed or paused campaign's MTD spend as available.** It already spent; it won't spend more. Exclude it from capacity, include it in MTD.
- **Recommending a boost without impression share.** See diagnostics above.
- **Percentages without dollars.** −45% means nothing until it's "−$4,577 by month end."

## What this skill does NOT do

- Judge whether spend is *working*. That's `advertising-performance-manager`.
- Handle multiple brands in one run. One account at a time by design.
- Track budget history. It reads current intent from config and computes fresh.
- Touch bid strategies, targeting, or creative. Budgets only.
