# reporting

Cross-channel budget pacing and performance review across Google Ads and Meta. Skills only — no MCP server; it pulls live metrics through the `google-ads` and `meta-ads` plugins.

## Skills

| Skill | What it does |
|---|---|
| `budget-pacing-manager` | Is spend on schedule this month, and should budget move? Day-aware tolerance band, trailing-14-day reallocation logic, Google impression-share and Meta frequency supply diagnostics, budget-conserving recommendations. |
| `advertising-performance-manager` | Is that spend producing leads at the right cost? 3-month day-matched baselines, 🔴/🟢/🟡/🆕 buckets, and a symptom-to-cause table that separates auction pressure from creative fatigue from broken tracking. |

Pacing answers whether the money went out. Performance answers whether it bought anything. Run pacing first.

## Setup

```bash
cp config/budget.example.md config/budget.md
```

Fill in `month_total`, the per-channel split, and your account IDs. `budget.md` is gitignored.

That file exists for one reason: pacing needs to know what you *intended* to spend, and no API can tell you that. Everything else — spend, clicks, conversions — is pulled live.

Requires `google-ads` and/or `meta-ads` installed and authenticated. Runs single-channel without complaint if you only have one.

## Notes

**Units.** Google Ads budgets are micros ($135.00 = `135000000`); Meta is minor units ($45.00 = `4500`).

**Meta conversion counting.** Default conversion fields undercount campaigns firing several events. Both skills sum `offsite_conversion.custom.*` plus `lead`, and skip Meta's auto-added duplicate counters. The output always states which events were counted.

**Pacing formula.** `(mtd_spend − expected_spend) / expected_spend` — variance from expected, not from the monthly total. Dividing by the total makes early-month problems look trivial until they're uncorrectable.

**One brand at a time.** Adapted from a multi-account agency workflow; the per-account triage loop is intentionally removed.
