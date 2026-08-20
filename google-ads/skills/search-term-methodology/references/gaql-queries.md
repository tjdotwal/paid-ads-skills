# GAQL Reference Queries

Use these queries with the `execute_gaql_query` tool. Always substitute the correct `customer_id` for the selected ad account.

## Primary Search Term Pull

Pulls all unactioned search terms from the last 30 days, sorted by cost descending. This is the standard starting query for `mine-search-terms`.

```sql
SELECT
  campaign.name,
  ad_group.name,
  search_term_view.search_term,
  metrics.cost_micros,
  metrics.clicks,
  metrics.impressions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND search_term_view.status = 'NONE'
ORDER BY metrics.cost_micros DESC
LIMIT 300
```

(Pull the heavier columns — `average_cpc`, `ctr`, `conversions`, `segments.keyword.*` — only for the specific terms you're actually actioning, not for the whole list.)

**Notes:**
- `cost_micros` is in micros (divide by 1,000,000 to get dollars)
- `average_cpc` is also in micros
- Do NOT pull one large unfiltered list. A `LIMIT 1000` × ~13-column pull overflows the context window and gets written to a temp file you then have to parse out-of-band. Pull in narrow, prioritized slices (see "Two-pass chunked pulls" below) and select only the columns you need.
- Use `LAST_14_DAYS` for accounts with lower traffic, `LAST_60_DAYS` for accounts needing broader coverage

## Two-pass chunked pulls (preferred over one large query)

Pull spend-moving terms and preventative terms separately so each result stays readable inline.

### Pass 1 — terms that already spent (clicks > 0)
```sql
SELECT campaign.name, ad_group.name, search_term_view.search_term,
       metrics.cost_micros, metrics.clicks, metrics.impressions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND search_term_view.status = 'NONE'
  AND metrics.clicks > 0
ORDER BY metrics.cost_micros DESC
LIMIT 300
```

### Pass 2 — preventative (zero clicks, by impressions)
```sql
SELECT campaign.name, ad_group.name, search_term_view.search_term,
       metrics.cost_micros, metrics.clicks, metrics.impressions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND search_term_view.status = 'NONE'
  AND metrics.clicks = 0
  AND metrics.impressions >= 2
ORDER BY metrics.impressions DESC
LIMIT 200
```

Tuning: on high-volume accounts raise the Pass 2 threshold (`impressions >= 3` or `>= 5`) and/or scope to one campaign at a time (`AND campaign.name LIKE '%...%'`) to keep each result inline. The methodology's target depth is 100–200 terms per campaign — don't exceed what you'll actually evaluate.

## Handling oversized results

If a result still overflows and gets written to a temp file:
1. First try to re-run with tighter filters (higher impression threshold, single campaign) or fewer columns — prefer keeping data inline.
2. If you must parse the temp file, hand it to a subagent or use jq/python on the saved path. Do NOT read a 100k+ char file into the main context.
3. **Data-integrity rule for subagent fan-out:** when multiple subagents pull per-account data, require every returned row/metric to be keyed to its `campaign.id` / `customer_id`, and spot-check at least one figure per account against the source before using it. Subagent fan-out has previously returned one account's numbers mislabeled as another's — never trust unkeyed aggregates.

## Campaign-Scoped Pull

To pull search terms for a specific campaign only:

```sql
SELECT
  campaign.name,
  campaign.id,
  ad_group.name,
  ad_group.id,
  search_term_view.search_term,
  search_term_view.status,
  segments.keyword.info.text,
  segments.keyword.info.match_type,
  metrics.cost_micros,
  metrics.clicks,
  metrics.impressions,
  metrics.average_cpc,
  metrics.ctr,
  metrics.conversions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND search_term_view.status = 'NONE'
  AND campaign.name LIKE '%Campaign Name Fragment%'
ORDER BY metrics.cost_micros DESC
LIMIT 500
```

## Check Existing Negatives (BOTH campaign-level AND shared lists)

Before recommending or pushing any negative, you MUST check two places. Campaign-level criteria alone are NOT enough — most accounts attach a shared "General negative keywords" list, and those members are invisible to the campaign_criterion query.

### Step 1 — Campaign-level negatives

```sql
SELECT
  campaign.name,
  campaign.id,
  campaign_criterion.keyword.text,
  campaign_criterion.keyword.match_type,
  campaign_criterion.negative
FROM campaign_criterion
WHERE campaign_criterion.negative = TRUE
  AND campaign_criterion.type = 'KEYWORD'
ORDER BY campaign.name
```

### Step 2 — Which shared negative lists are attached to which campaigns

```sql
SELECT
  campaign.name,
  campaign.id,
  shared_set.name,
  shared_set.id,
  shared_set.type,
  shared_set.member_count
FROM campaign_shared_set
WHERE shared_set.type = 'NEGATIVE_KEYWORDS'
```

### Step 3 — The actual MEMBERS of each shared list (this is the part that was missing)

For each `shared_set.id` returned above, pull its keywords and dedup candidates against them:

```sql
SELECT
  shared_criterion.keyword.text,
  shared_criterion.keyword.match_type
FROM shared_criterion
WHERE shared_set.id = SHARED_SET_ID
ORDER BY shared_criterion.keyword.text
```

When deduping, remember match-type/tokenization matters: a one-word phrase negative (e.g. `hardpressed`) does NOT block a two-word query (`hard pressed`), and a broad-match negative only blocks when ALL its tokens are present. Treat a candidate as "already covered" only if an existing negative would actually block the observed search term.

## Impression Share (REQUIRED before any scaling or budget claim)

Run this before describing a campaign as starved, capped, or scalable, and before recommending any budget move. See SKILL.md → "Scaling Claims Require Impression Share".

```sql
SELECT
  campaign.name,
  metrics.impressions,
  metrics.cost_micros,
  metrics.search_impression_share,
  metrics.search_budget_lost_impression_share,
  metrics.search_rank_lost_impression_share,
  metrics.search_absolute_top_impression_share
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
  AND campaign.advertising_channel_type = 'SEARCH'
  AND metrics.impressions > 0
ORDER BY metrics.cost_micros DESC
```

Pair it with the daily budget so "lost to budget" can be read against actual pacing:

```sql
SELECT campaign.name, campaign_budget.amount_micros, metrics.cost_micros
FROM campaign
WHERE segments.date DURING LAST_30_DAYS AND metrics.impressions > 0
ORDER BY metrics.cost_micros DESC
```

**Notes:**
- Impression share fields are ratios (0.9211 = 92.11%), NOT percentages. Do not report them raw.
- Estimate addressable demand as `impressions / search_impression_share`. If that ceiling is small, the campaign cannot scale regardless of budget.
- These fields are unavailable for Display and PMax campaigns. Filter to `advertising_channel_type = 'SEARCH'` or the rows return empty.
- Google allows up to 2x the daily budget on any single day, so daily cost exceeding the budget is not by itself evidence of a budget change.
- `campaign.start_date` is NOT a valid field on the `campaign` resource in v23 — do not include it when checking campaign maturity.

## Adding Negatives via MCP

The `add_negative_keywords` tool writes ONLY to a campaign or ad group — it CANNOT add to a shared negative keyword list. Editing the shared "General negative keywords" list must be done in the Google Ads UI (no API tool is exposed for it in this plugin).

To push negatives:
1. Set `level` = `CAMPAIGN` (default) or `AD_GROUP`, and `target_resource_name` = the campaign or ad-group resource name (e.g. `customers/<cid>/campaigns/<campaign_id>`). There is no negative-list ID parameter.
2. Pass `login_customer_id` = the account's MCC when required (see naming-conventions ## Account Targeting); retry without it on `USER_PERMISSION_DENIED`.
3. Choose match type: phrase for a signal word/business name that should be blocked in any variant; exact for a specific full query you don't want to over-block.
4. Present the full batch to the user and get an explicit "yes" before executing. Batch by campaign and confirm each campaign separately.
5. If a negative should apply across ALL campaigns, either (a) add it to each campaign individually via the tool, or (b) tell the user to add it to the shared "General negative keywords" list in the UI. Do NOT claim the tool added an "account-level" or "shared-list" negative.
6. After execution, confirm the added count matches what was approved.
