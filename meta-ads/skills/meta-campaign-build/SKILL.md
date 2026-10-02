---
name: meta-campaign-build
description: Build and launch a complete Meta (Facebook/Instagram) campaign from a folder of assets plus a campaign.xlsx brief — campaign, ad sets with full targeting (radius / cities / zips / interests / custom & lookalike audiences / placements / Advantage+ audience), and image, video, carousel or DCO creatives, all created PAUSED for review in Ads Manager. Use whenever the operator says "build this campaign", "launch this on Meta", "here are the assets and copy, create the ads", "set up ad sets for [client]", "put this promo live on Facebook", hands over a folder with images/videos and copy, or asks for the campaign sheet template. Also use for one-off pieces of the same job: "create an ad set targeting 25 miles around [address]", "make a carousel from these five images", "upload this video and build a creative". Not for analysis (use meta-creative-analysis), audits (meta-account-audit), or weekly pacing (budget-pacing-manager).
---

# Meta Campaign Build

Turn a folder (assets + `campaign.xlsx`) into a fully built, PAUSED Meta campaign the operator reviews and launches in Ads Manager. The workbook is the single source of truth; the `campaign_build` tool does the API work; this skill is the process around it.

The point of the sheet is that the operator can hand it to a designer or a media buyer, they can fill it without knowing the API, and the plan step catches every mistake before a single object exists on the account.

## Tools this skill drives

| Step | Tool |
|---|---|
| Blank workbook | `campaign_sheet_template(folder)` |
| Find IDs to fill the Campaign sheet | `ad_account_list`, `page_list`, `pixel_list`, `custom_audience_list` |
| Sanity-check a targeting input | `geo_search`, `interest_search`, `targeting_from_sheet_row` |
| Validate + preview | `campaign_build(workbook_path, dry_run=True)` |
| Create everything, PAUSED | `campaign_build(workbook_path, dry_run=False)` |
| One-off pieces | `adset_create_full`, `creative_create_full`, `image_upload`, `video_upload`, `ad_create` |
| Read back / inspect | `campaign_get`, `adset_list`, `ad_list`, `ad_image_get`, `ad_video_get` |

## The flow

### 1. Get the brief into a workbook

The canonical template lives in this skill at `assets/campaign.xlsx`; the column-by-column reference is `references/columns.md`. Read `columns.md` before filling or checking any sheet.

The operator usually works in a Google Sheet built from that template and exports it. Two export shapes arrive, and `campaign_build` reads both without changes:

- **One `.xlsx`** (File → Download → Microsoft Excel): all three tabs in one file. Point `campaign_build` at it.
- **Three CSVs** (per-tab File → Download → CSV): Google names them `<Sheet name> - Campaign.csv`, `... - AdSets.csv`, `... - Ads.csv`. Point `campaign_build` at the folder.

If the operator hands you a folder with no sheet at all, run `campaign_sheet_template(folder)` (writes a copy of the shipped template) and fill it from whatever brief they gave (a doc, a Slack message, a spreadsheet in another shape). Fill what you can, leave what you can't, and hand back a list of blanks.

If a Google Sheet link arrives instead of a file and a Drive connector is available, download it as `.xlsx` into the assets folder yourself; otherwise ask for the export.

Things you will usually have to look up for them:

- `ad_account_id` → `ad_account_list`, match on client name.
- `page_id` → `page_list`. If several, ask.
- `pixel_id` → `pixel_list(ad_account_id)`. Prefer the one with a recent `last_fired_time`.
- Audience names → `custom_audience_list(ad_account_id)`. Use the exact name or the ID in the sheet.

Naming: campaign, ad set and ad names follow the client's existing convention. Pull three current names with `campaign_list` / `adset_list` and mirror the pattern. If the account is empty, use `Client | Offer | Meta | Funnel stage` and say so.

### 2. Dry run, always

```
campaign_build(workbook_path, dry_run=True)
```

This parses every row, resolves every city / zip / interest / audience against Meta, and returns the exact payloads. Nothing is created or uploaded. Two possible outcomes:

- **Error.** The message names the sheet, the row, and the fix. Fix it in the workbook (or tell the operator what to change) and rerun. Do not work around a validation error by hand-building the piece with lower-level tools; the error is there because the build would have failed or done the wrong thing on Meta.
- **Plan.** Show the operator the `summary` field verbatim, then the `resolutions` list. Resolutions are where silent mistakes hide: an interest that resolved to a "nearest match", a city that matched the wrong state, an audience matched by ID you didn't expect. Read every one.

Check these before asking for approval:

- Budget mode is what they meant. `campaign_daily_budget` filled = CBO; blank = each ad set carries its own. Mixing is rejected, but the wrong choice isn't.
- Total daily spend across ad sets (or the CBO amount) matches the client's monthly budget ÷ ~30.4. Flag anything over.
- Every ad set has at least one ad (warning, not error).
- Conversion ad sets point at the right pixel event. `LEAD` for lead gen, `PURCHASE` for ecommerce, `CONTACT` / `SCHEDULE` for local service when that's what the pixel actually fires.
- Destination URLs open and are the landing page for this offer, not the homepage.
- `url_tags` are set. UTMs live on the creative in Meta; if the sheet leaves them blank every ad lands untagged. Default pattern:
  `utm_source=facebook&utm_medium=ppc&utm_campaign={{campaign.name}}&utm_content={{ad.name}}`
  Meta fills the `{{...}}` at delivery time.

### 3. Approval, then build

Only after the operator says the plan is right:

```
campaign_build(workbook_path, dry_run=False)
```

Assets upload first (videos wait for Meta processing, so a build with several videos takes minutes), then campaign → ad sets → creatives → ads. Everything is PAUSED. Return the headline: campaign ID, ad set count, ad count, the Ads Manager link, and the path to `<workbook>-build-results.csv`.

If it fails part-way, say what was created (the `progress` list), what failed and why (Meta's message is passed through verbatim), and that a rerun after the fix will not duplicate anything. The state file next to the workbook holds every ID already created.

### 4. Launch is the operator's

This skill never sets anything ACTIVE. The operator reviews in Ads Manager (previews, placements, pixel) and flips it live themselves. If they ask you to activate from chat, restate the daily spend that will start and the number of ads going live, get an explicit yes, then `campaign_update(status="ACTIVE")` → `adset_update(status="ACTIVE")` for each → `ad_update(status="ACTIVE")` for each, in that order.

## The workbook

Template: `assets/campaign.xlsx`. Full column reference: `references/columns.md`. Three sheets. Row 2 of AdSets and Ads is a help row (starts with `#`, ignored on build). Copy is plain text; no markdown.

**Campaign** (key / value): `ad_account_id`, `page_id`, `campaign_name`, `objective` are required. `campaign_daily_budget` turns on CBO. `pixel_id` + `conversion_event` are required when any ad set optimizes for `OFFSITE_CONVERSIONS`. `url_tags` applies to every ad unless a row overrides it.

**AdSets** (one row each): geo is `geo_type` + `geo_value`:

| geo_type | geo_value example | Notes |
|---|---|---|
| `radius` | `1200 Broadway, Nashville, TN 37203 \| 25mi; 36.16,-86.78 \| 10mi` | Address or lat,lng. 1-50 miles. The local-service default. |
| `cities` | `Nashville, TN \| 15mi; Franklin, TN` | State disambiguates. Optional radius 10-50mi. |
| `zips` | `37203; 37204; 37205` | Resolved in `default_country`. |
| `regions` | `Tennessee; KY` | States / provinces. |
| `countries` | `US; CA` | |

`interests` and audience columns are semicolon-separated names. `advantage_audience` defaults on when no interests/audiences are given and off when they are; set `Y`/`N` to force. `placements` defaults to Advantage+ (all); write `facebook:feed,story,reels; instagram:stream,story,reels` to restrict.

**Ads** (one row each): `format` is `image` / `video` / `carousel` / `dco`. `asset_files` are file names found anywhere under the workbook's folder. Multi-value copy uses `||`: per-card headlines / descriptions / URLs for carousel, up to 5 variants each for dco. A dco ad must be alone in its ad set (the builder flags the ad set `is_dynamic_creative`).

## Common failures and what they mean

| Message | Cause | Fix |
|---|---|---|
| `City 'X' did not resolve` | Name misspelled or state missing | Use `geo_search` to find the right key/name, fix the sheet. |
| `campaign uses CBO — clear the ad-set budget columns` | Both budget levels filled | Pick one. |
| `OFFSITE_CONVERSIONS needs pixel_id` | Conversion goal with no pixel | `pixel_list`, fill `pixel_id`. |
| `asset 'x.png' not found` | Filename mismatch or file outside the folder | Match the name exactly; move the file in. |
| Graph: `Invalid parameter` on adsets with `targeting` | Usually a Special Ad Category account with age/gender/zip targeting | Clear age, gender, zips; use radius ≥15mi. |
| Graph: `(#100) Param instagram_user_id must be a valid Instagram account id` | Wrong IG id, or the Page's IG isn't linked in Business Settings | Clear `instagram_user_id`; Meta uses the Page-backed identity. |
| Graph: `age ... can't be set to lower than 65` (1870189) | Advantage+ audience on with a hard age ceiling | The builder lifts age_max to 65 and notes it; set `advantage_audience=N` to keep the ceiling. |
| Graph: `Could not geocode address` (1487855) | `radius` entry is a bare city name | Use a street address, `lat,lng \| Nmi`, or `geo_type=cities`. The builder now rejects address strings with no street number. |
| Graph: `Performance goal isn't available` (2490408) | optimization_goal not allowed under the objective | The builder validates this before building; e.g. OUTCOME_SALES needs OFFSITE_CONVERSIONS or VALUE. |
| Graph: `Ads creative post was created by an app that is in development mode` (1885183) | The Meta app behind ACCESS_TOKEN is in Development mode | developers.facebook.com → the app → switch App Mode to **Live**. Campaigns and ad sets create fine in dev mode; creatives/ads do not. |
| Graph: `Video ... not ready` | Rare; processing race | Rerun; the upload is recorded and won't repeat. |
| Graph: permissions error on `/adcreatives` | System user lacks `ads_management` or Page access | Business Settings → System Users → assign the Page + ad account. |

## Output discipline

Follow the plugin's CLAUDE.md. For the dry run: the summary, the resolutions, and the checks that need a decision. For the build: the headline numbers, the link, the CSV path. For failures: what exists, what didn't, one-line cause, one-line fix.
