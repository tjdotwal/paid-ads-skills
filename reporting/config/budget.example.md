# Budget config — example

Copy this to `budget.md` in the same directory and fill it in. That filename is gitignored, so your real numbers stay local.

Pacing math needs one input no API can give you: **what you intended to spend this month.** Everything else — actual spend, conversions, clicks — comes live from the Google Ads and Meta APIs. This file is only the intent.

## Config

```
brand:                 Acme Scheduling
month_total:           10000
google_ads_monthly:    6000
meta_monthly:          4000
currency:              USD

google_customer_id:    1234567890
meta_ad_account_id:    act_1234567890

target_cpa:            85
```

## Fields

| Field | Required | Notes |
|---|---|---|
| `brand` | yes | Label for the output header |
| `month_total` | yes | Total intended spend this calendar month, all channels |
| `google_ads_monthly` | if running Google | Intended Google Ads spend this month |
| `meta_monthly` | if running Meta | Intended Meta spend this month |
| `currency` | yes | Match the ad account's currency. No conversion is performed |
| `google_customer_id` | if running Google | Digits, no dashes. Falls back to `GOOGLE_ADS_CUSTOMER_ID` |
| `meta_ad_account_id` | if running Meta | `act_` prefix. Falls back to `AD_ACCOUNT_ID` |
| `target_cpa` | no | Used as a secondary reference in performance reviews. Baselines drive the buckets, not this |

## Notes

- Channel budgets should sum to `month_total`. If they don't, `month_total` wins for pacing math and the skill flags the mismatch.
- Running one channel only? Omit the other and the skill reports single-channel without complaint.
- Changing budget mid-month? Update this file. Pacing recomputes from whatever is here — it keeps no history.
- Multiple brands? One config directory per brand, or edit between runs. These skills are built for one account at a time by design.
