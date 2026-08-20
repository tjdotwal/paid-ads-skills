---
name: naming-conventions
description: >
  Load this skill before any analysis, mining, auditing, or optimization work on
  a Google Ads account. It defines how to read campaign names, ad group names,
  and account structure so campaign intent is interpreted consistently. Use it
  whenever you need to answer "what is this campaign selling", "who is this ad
  group targeting", or "what funnel stage is this". Load it when asked to "mine
  search terms", "audit ad copy", "review performance", "optimize budgets", or
  any task that depends on understanding campaign intent.
version: 1.0.0
---

# Naming Conventions

This skill defines how to read campaign and ad group naming so that every analysis interprets campaign intent the same way. Load and internalize it before any account analysis or optimization work.

The taxonomy below is a convention, not a platform rule. It is the structure this toolkit assumes and the one it builds new campaigns in — see `google-ads-campaign-build`. Accounts that don't follow it are handled in `references/naming-edge-cases.md`.

## Account Targeting

`list_accounts` returns **numeric customer IDs only — no account names**, so it can't be used on its own to pick an account by name. Resolve the ID once and keep it in your environment as `GOOGLE_ADS_CUSTOMER_ID`.

**If the account sits under a manager account (MCC):**

- Set `GOOGLE_ADS_LOGIN_CUSTOMER_ID` to the manager ID. It is sent as the `login-customer-id` header on every call, reads and mutations alike.
- If a call returns `CUSTOMER_NOT_FOUND` or `USER_PERMISSION_DENIED`, retry it **without** the manager header before assuming an access problem. Calls do fail when sent with a manager header the account doesn't actually sit under.
- Managing accounts under more than one manager means passing `login_customer_id` per call rather than relying on the env default.

Confirm which account you're pointed at before running mutations. Never assume.

## Campaign Naming Taxonomy

Campaigns follow a pipe-delimited naming structure:

```
[Brand/Product] | [Campaign Type] | [Funnel Stage] | [Audience] | [Geo]
```

**Reference example:**
```
Acme Scheduling Software | Demo & Self Signup | BOFU Cold Traffic | Tier 3+ | USA
```

Parse each segment as follows:

### Segment 1 — Brand/Product
The brand and/or specific product or service being advertised. Use this to understand the core offering and infer what a relevant search query would look like.

### Segment 2 — Campaign Type
The conversion action or campaign goal. Examples: `Demo & Self Signup`, `Lead Gen`, `Brand`, `Retargeting`, `Shopping`. This tells you what the campaign is trying to get users to do.

### Segment 3 — Funnel Stage
The audience's position in the buying journey. Interpret as follows:

| Label | Meaning | Relevance bar |
|-------|---------|---------------|
| TOFU | Top of funnel, awareness | Broader intent acceptable |
| MOFU | Mid funnel, consideration | Some product specificity expected |
| BOFU | Bottom of funnel, conversion-ready | High purchase/sign-up intent required |
| Brand | Branded search | Must contain brand terms |
| Retargeting | Past visitor/engaged audience | Intent context varies |

The funnel stage directly affects how strictly you evaluate search term relevance. A BOFU campaign has zero tolerance for generic, research-phase, or off-topic queries. A TOFU campaign may accept broader informational terms.

Cold Traffic = no prior brand awareness. This further raises the bar — a BOFU Cold Traffic campaign needs searchers who are ready to act *and* haven't been warmed up by retargeting.

### Segment 4 — Audience
Tier segmentation (e.g., `Tier 3+`) or audience descriptor. Tier labels typically refer to geographic market quality or audience scoring. Use this as supporting context, not a primary relevance signal.

### Segment 5 — Geo
Geographic targeting. Use this to flag searches that are geographically misaligned if the campaign targets a specific region.

## Ad Group Naming Conventions

Ad group names use kebab-case and describe the targeting theme or keyword intent of that group.

**Example:** `non-free-scheduling-software`

This ad group targets users looking for scheduling software and specifically *not* the free variety — implying willingness to pay. That's critical context when evaluating search terms: "free scheduling app" is off-theme for this ad group even though it's on-topic for the product.

Parse ad group names by splitting on hyphens and reading them as descriptive phrases. Use the full phrase to understand the targeting intent.

## Using Naming Conventions in Evaluation

When evaluating any search term, always construct the full context sentence before making a decision:

> "This search term appeared in the [campaign name] campaign, triggered by the keyword [keyword], in the ad group [ad group name]."

Then ask: **Does this search term fit someone who would respond to this campaign's offer at this funnel stage?**

If no → candidate for negation.
If yes → keep.
If ambiguous → flag as "Review" with your reasoning.

See `references/naming-edge-cases.md` for handling accounts with non-standard naming conventions.
