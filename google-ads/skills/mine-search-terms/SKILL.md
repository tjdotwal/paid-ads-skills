---
name: mine-search-terms
description: >
  This skill should be used when asked to "mine search terms", "find negative
  keywords", "build a negative keyword list", "review the search term report",
  "find wasted spend in search terms", "what search terms should we negate",
  or "run the search term report for [brand]". Also triggers when the user
  says "audit my search terms", "clean up search terms", or "add negative keywords".
  Load the naming-conventions and search-term-methodology skills before starting.
version: 1.0.0
---

# Mine Search Terms

Load `search-term-methodology` and `naming-conventions` before starting. Both are required. Do not begin evaluation until both are loaded.

This review produces **two outputs simultaneously**: a negation list and a keyword opportunity list. Never treat it as cleanup only.

## Steps

### 1. Select the Client Account

Confirm the target account. `list_accounts` returns numeric IDs only, so resolve from `GOOGLE_ADS_CUSTOMER_ID` or ask. If the account sits under a manager account, pass `login_customer_id` (see naming-conventions "## Account Targeting"). Present the resolved account to the user and confirm before proceeding. Note the `customer_id` for all subsequent queries.

### 2. Scope the Work

Ask the user:
- Full account, or a specific campaign?
- Any preference on date range? (default: last 30 days; suggest last 7 days if they mention it's a high-volume account)

If no preference is given, default to full account, last 30 days.

### 3. Pull Search Terms

Execute the **two-pass chunked pulls** from `search-term-methodology/references/gaql-queries.md` (Pass 1: clicks > 0 by cost; Pass 2: clicks = 0 by impressions), selecting only triage columns. Do NOT run a single `LIMIT 1000` pull — it overflows context. For high-volume accounts, scope a pass to one campaign at a time or raise the Pass 2 impression threshold. If a result still spills to a temp file, parse it via a subagent and key every row to its campaign/account ID before using it.

Report back: "Pulled X search terms across Y campaigns. Beginning evaluation..."

**PMax note:** Google does not expose PMax search terms via the `search_term_view` API. If the user requests PMax specifically, let them know this is a Google API limitation — PMax terms are not accessible this way.

### 4. Evaluate Terms — Two-Pass Approach

Work through terms in prioritized passes as defined in `search-term-methodology`. Both outputs (negates and keyword opportunities) are built simultaneously throughout both passes.

**Pass 1 — Clicks descending:**
Start with every term that has at least one click. These have already moved spend. Evaluate all of them — do not skip any.

**Pass 2 — Impressions descending:**
Once clicks are cleared, work through the impression list. This is the preventative layer — catching bad terms before they spend.

**Stop when you hit 1-impression terms.** Before evaluating them, check campaign maturity:

- **Mature campaign (3+ months):** Skip 1-impression terms. They are noise.
- **New/dialling-in campaign (under 3 months):** Do not evaluate individually. Cluster them — identify the dominant off-theme pattern and surface it as a keyword health observation (see output format below).

For each term, parse the campaign and ad group names using `naming-conventions` to confirm theme and funnel stage before making a decision.

Apply the three-bucket framework from `search-term-methodology` to every term:
- **Clear Negate** — confidently off-theme; include in negation list
- **Clear Keep** — on-theme; no action required
- **Test Candidate** — ambiguous intent; surface the question to the analyst before negating

Never negate ambiguous terms unilaterally. Always surface the test candidate option.

When you identify a term to negate, immediately check whether a signal word (phrase match) is the right approach or whether the full term (exact match) should be negated. Flag any phrase match conflict with an active or incoming keyword.

**Before finalizing any negate candidate, check existing negatives in BOTH places** using `search-term-methodology/references/gaql-queries.md` → "Check Existing Negatives": pull (1) campaign_criterion negatives, (2) the shared NEGATIVE_KEYWORDS lists attached to the campaign, and (3) the MEMBERS of those shared lists. Exclude any candidate already blocked. Account for match-type/tokenization (a one-word negative won't block a two-word query).

### 5. Determine Negative Level

For each negate candidate, determine the scope. Note: the push tool only writes to CAMPAIGN or AD_GROUP — there is no true account-level negative via the API.

- **Campaign level (default):** When the term is off-theme for that specific campaign but may be valid elsewhere.
- **Applies across all campaigns:** When the brand confirms the use case is out of scope everywhere, or the same bad term recurs across campaigns — implement it by EITHER (a) adding the negative to each campaign individually via the tool, OR (b) instructing the user to add it to the shared "General negative keywords" list in the Google Ads UI.

When in doubt, default to campaign level and flag it.

### 6. Build the Negation Output

**The CSV carries the rows. Chat carries the decisions.** See `search-term-methodology` → "Output Format" and the plugin `CLAUDE.md` → "Output Discipline".

Group negate candidates by campaign, sorted by spend descending. In chat, each campaign is one line: name and count. Full term-by-term detail goes to the CSV — hand it over in chat only if asked.

For phrase match negates, name the **signal word**, not the full term.

Test candidates get one line each — the term, the two readings, the question:

> `sports admin software` — league admin or IT admin? Brand confirmed IT is out of scope? Recommend running 30 more days if not.

### 7. Build the Keyword Opportunity Output

One line per opportunity, alongside the negation summary:

> `youth registration platform` — 2 conv / 14 clicks → `registration-software` exact. Stage 1.

Include opportunities where the term converted and is on-theme, or has 5+ impressions and is on-theme, or represents a distinct intent variant worth capturing. Skip close variants of existing keywords.

Mark Stage 2 (own ad group) only when intent is distinct enough to need dedicated copy, or impression share is starved in the current ad group. One clause of why, no more.

### 8. Present the Summary and CSV

```
Search Terms — [Account] — [Date Range]
X negates across Y campaigns · $Z/30d recovered · N held for you

Ready to push
  [campaign] — X terms
  [campaign] — X terms

Held — your call
  • [term/signal] — [the fact that would make you overrule] ([the stake])

Test candidates (N)
  • [term] — [reading A] or [reading B]? [question]

Opportunities (N)
  • [term] — [metric] → [ad group] [match type]. Stage [1|2].
```

Save a bulk-upload-ready CSV as `search-term-negatives-YYYY-MM-DD.csv` to the outputs folder. Include only rows where Decision = `Negate` — test candidates need analyst sign-off first.

**Required CSV columns (in this order):**

| Campaign | Ad Group | Keyword | Search Term | Match Type | Cost | Clicks | Impressions | CPC | CTR | Conversions | Decision | Reasoning |

Format cost/CPC as dollar amounts, CTR as a percentage, CPC to 2 decimals.

Then one line: the file link, and "Push these? I'll go campaign by campaign."

### 9. Push Negatives (Optional — Requires Explicit Approval Per Campaign)

If the user says yes:

1. Group negatives by campaign
2. For each campaign batch, present: campaign name, count of terms, the exact negative keywords being added with match type
3. Say: "Ready to add X negatives to [Campaign Name]. Confirm?"
4. Wait for explicit confirmation before executing
5. Execute using the MCP tool
6. Confirm in one line: "Added X to [Campaign Name]."
7. Repeat for each campaign

**Never add negatives across multiple campaigns in a single step.** Always batch by campaign and confirm each one individually.

For negatives meant to apply across all campaigns, either add them to each campaign individually (confirm each campaign batch) or hand the user a clean list to paste into the shared "General negative keywords" list in the UI. Do not describe a tool push as "account-level" — the tool cannot do that.

### Error Handling

- **GAQL returns 0 results:** Confirm date range and account scope, then retry with `LAST_60_DAYS`
- **Campaign name doesn't match standard taxonomy:** Note it in the summary and use ad group name as primary context for decision-making
- **MCP mutation fails:** Report the error, do not retry automatically — show the user the failed terms and ask how to proceed
- **Ambiguous client context:** Do not guess. Surface the question and wait for the analyst to confirm before making the call.
