# Campaign brief — column reference

The same three tabs whether you fill `campaign.xlsx` or a Google Sheet. Semicolons separate list items; `||` separates copy variants / per-card values.

## Campaign (key / value)

| key | notes |
|---|---|
| `client` | Brand name (used in file names only). |
| `ad_account_id` | act_XXXXXXXXX. Required. |
| `page_id` | Facebook Page ID the ads run as. Required. Use page_list to find it. |
| `instagram_user_id` | Instagram account ID for IG placements (the IG user id). Optional; omit to use the Page-backed IG identity. |
| `campaign_name` | Required. Follow your naming convention. |
| `objective` | OUTCOME_LEADS \| OUTCOME_SALES \| OUTCOME_TRAFFIC \| OUTCOME_AWARENESS \| OUTCOME_ENGAGEMENT |
| `buying_type` | AUCTION (default) \| RESERVED |
| `special_ad_categories` | Blank for none, or HOUSING \| EMPLOYMENT \| CREDIT \| ISSUES_ELECTIONS_POLITICS (semicolon-separate multiple). |
| `campaign_daily_budget` | Dollars (e.g. 150.00). Fill this OR ad-set budgets, not both. Filling it = CBO (Advantage+ campaign budget). |
| `campaign_lifetime_budget` | Dollars. Requires end_time on every ad set. Mutually exclusive with campaign_daily_budget. |
| `bid_strategy` | LOWEST_COST_WITHOUT_CAP (default) \| LOWEST_COST_WITH_BID_CAP \| COST_CAP \| LOWEST_COST_WITH_MIN_ROAS |
| `pixel_id` | Dataset / Pixel ID. Required when any ad set optimizes for OFFSITE_CONVERSIONS. |
| `conversion_event` | LEAD \| PURCHASE \| CONTACT \| SCHEDULE \| COMPLETE_REGISTRATION \| SUBMIT_APPLICATION \| ... (default LEAD) |
| `default_country` | ISO code used to resolve cities and zips (default US). |
| `url_tags` | Appended to every destination URL. e.g. utm_source=facebook&utm_medium=ppc&utm_campaign={{campaign.name}}&utm_content={{ad.name}} |

## AdSets (one row per ad set)

| column | notes |
|---|---|
| `adset_name` | Required, unique within the campaign. |
| `daily_budget` | Dollars. Leave blank when the campaign uses CBO. |
| `lifetime_budget` | Dollars. Requires end_time. Blank when CBO. |
| `optimization_goal` | OFFSITE_CONVERSIONS \| LANDING_PAGE_VIEWS \| LINK_CLICKS \| REACH \| IMPRESSIONS \| THRUPLAY \| LEAD_GENERATION |
| `billing_event` | IMPRESSIONS (default) \| LINK_CLICKS \| THRUPLAY |
| `bid_amount` | Dollars. Only for bid cap / cost cap strategies. |
| `geo_type` | countries \| radius \| cities \| zips \| regions |
| `geo_value` | countries: US;CA   radius: 123 Main St, Nashville TN 37203 \| 25mi ; ...   cities: Nashville, TN \| 15mi ; Franklin, TN   zips: 37203; 37204   regions: Tennessee; Kentucky |
| `excluded_geo_type` | Optional. Same options as geo_type. |
| `excluded_geo_value` | Optional. Same formats as geo_value. |
| `age_min` | 18-65 (default 18). |
| `age_max` | 18-65 (default 65). |
| `genders` | all (default) \| male \| female |
| `interests` | Semicolon-separated interest names. Resolved via Meta search; the plan shows what matched. |
| `custom_audiences` | Semicolon-separated audience names or IDs to INCLUDE. |
| `excluded_audiences` | Semicolon-separated audience names or IDs to EXCLUDE. |
| `advantage_audience` | Y (default when no interests/audiences) \| N. Advantage+ audience lets Meta expand beyond your inputs. |
| `placements` | auto (default) or e.g. facebook:feed,story,reels; instagram:stream,story,reels |
| `start_time` | Optional ISO 8601 with offset, e.g. 2026-10-01T06:00:00-0500 |
| `end_time` | Optional ISO 8601. Required with lifetime budgets. |

## Ads (one row per ad)

| column | notes |
|---|---|
| `ad_name` | Required, unique within the campaign. |
| `adset_name` | Must match an adset_name on the AdSets sheet. |
| `format` | image \| video \| carousel \| dco |
| `asset_files` | File name(s) in this folder. image/video: one file. carousel: 2-10 files, semicolon-separated, in card order. dco: up to 10 images or videos. |
| `primary_text` | Body copy. For dco: up to 5 variants separated by \|\| |
| `headline` | For carousel: one per card separated by \|\| (or one to reuse). For dco: up to 5 variants separated by \|\| |
| `description` | Optional link description. Carousel: per card with \|\| |
| `destination_url` | Landing page. Carousel: one per card with \|\| (or one to reuse). |
| `display_link` | Optional caption domain shown under the headline (e.g. example.com). |
| `cta` | LEARN_MORE \| GET_QUOTE \| SIGN_UP \| SHOP_NOW \| CONTACT_US \| GET_OFFER \| BOOK_NOW \| DOWNLOAD \| APPLY_NOW \| SUBSCRIBE \| WATCH_MORE. dco: multiple with \|\| |
| `url_tags` | Optional override of the campaign-level url_tags for this ad. |

## Google Sheets

Import `assets/campaign.xlsx` into a Google Sheet once (File → Import → Upload, keep all three tabs) and copy it per client. To hand a filled sheet to Claude either:

- **File → Download → Microsoft Excel (.xlsx)** — one file, all tabs. Drop it in the assets folder. Preferred.
- **Per tab: File → Download → CSV** — Google names them `<Sheet> - Campaign.csv`, `<Sheet> - AdSets.csv`, `<Sheet> - Ads.csv`. Drop all three in the assets folder. The builder matches on the tab name at the end of the filename.

Row 2 of AdSets and Ads is the help row (starts with `#`). Leave it or delete it; the builder skips it either way.
