---
name: search-term-methodology
description: >
  This skill defines how to evaluate Google Ads search terms for
  relevance, negation candidacy, keyword opportunity, AND performance
  pulse-check diagnosis. Load this skill when asked to "mine search terms",
  "find negative keywords", "evaluate search terms", "review the search term
  report", "identify wasted spend", "find irrelevant queries", "build a
  negative keyword list", "pulse check", "how is the campaign doing",
  "diagnose a performance drop", "is this campaign healthy", or any question
  about whether a Google Ads campaign is underperforming. ALSO load this skill
  for any scaling or headroom question — "can this campaign scale", "is this
  campaign capped", "is this campaign starved", "should we increase budget on
  X", "where should we move budget", "is there headroom here", "why is volume
  so low" — because those claims require impression share evidence (see
  "Scaling Claims Require Impression Share"). Must be loaded alongside
  naming-conventions before any search term evaluation, performance
  diagnosis, or scaling recommendation begins.
version: 1.0.0
---

# Search Term Methodology

Load `naming-conventions` before applying this skill.

Search term reviews are a routine weekly or semi-weekly activity across every active ad account. The review has **two outputs running simultaneously** — a negation list and a keyword opportunity list. Never treat it as cleanup only.

This skill also governs **performance pulse-check diagnosis**. See "Performance Pulse Checks" below.

## Review Scope

Default date range: **last 30 days**. Use last 7 days for high-volume accounts where 30 days would surface too many already-actioned terms.

Target depth: **100–200 terms per campaign** (one to two pages). The agent should work in prioritized passes rather than dumping a flat list. Stop when the natural cutoff is reached (see Prioritization below).

## Prioritization Order

Work through search terms in two passes:

**Pass 1 — Sort by clicks descending.**
Review all terms with clicks first. These are the highest priority because spend has already moved. Confirm on-theme or negate. Do not skip any term with at least one click.

**Pass 2 — Sort by impressions descending.**
Once clicks are cleared, work down the impression list. This is the preventative layer — catching bad terms before they get clicks and spend.

**Stop when you hit 1-impression terms.** Apply the campaign maturity rule below before deciding how to handle them.

## Campaign Maturity Rule

Before evaluating 1-impression terms, check how long the campaign has been running:

**Mature campaign (3+ months of data):**
Single-impression terms are noise. Skip them entirely. The keyword themes are established and these terms won't move the needle.

**New or dialling-in campaign (under 3 months):**
Do not evaluate 1-impression terms individually. Instead, read them as a **cluster**. Identify the dominant off-theme pattern across all of them and surface it as a keyword health observation — not a negation recommendation.

Example output for a new campaign:
> "There are 18 single-impression terms in this campaign. The dominant theme is camp and event registration queries. This may indicate your registration software keywords are matching too broadly. Recommend reviewing keyword match types before adding negatives."

This is a structural diagnosis, not a cleanup task. Flag it and let the analyst decide whether to rework the keyword strategy.

## Three-Bucket Decision Framework

For every term, assign one of three decisions:

### 1. Clear Negate
The term is confidently off-theme, wrong vertical, wrong intent, or wrong audience. Recommend negation with a one-sentence reasoning. Wait for explicit approval before adding.

Confidence for a clear negate comes from one of two sources:
- **Data pattern**: The signal word or theme appears across multiple bad queries in this review
- **Account knowledge**: The client has confirmed this use case is out of scope

Never make a unilateral negate decision on a term you've only seen once without one of these two confidence sources.

### 2. Clear Keep
On-theme, matches campaign intent and funnel stage as defined by naming-conventions. No action required. Note it and move on.

### 3. Test Candidate
Intent is ambiguous — the term could signal the right buyer or the wrong one. Do not negate. Instead, surface the question:

> "This term could indicate [use case A] or [use case B]. Has the brand confirmed whether [use case] is in scope? If not, recommend running it and reviewing in 30 days."

Always offer the test option on borderline terms. A low-cost lead from an ambiguous query might still have value — land-and-expand, adjacent buyer, different classification of the same need. The analyst and client context decides, not the agent.

## Impression Threshold

- **1 impression**: Apply maturity rule above — skip (mature) or cluster-diagnose (new)
- **2+ impressions**: Evaluate individually using the three-bucket framework
- The lower the impression count, the less urgency — but 2–5 impressions on a clearly bad term in a high-spend campaign is still worth flagging

## Phrase Match Negative Logic

When a term warrants negation, do not always negate the full term. Identify whether a **signal word** is responsible for the wrong intent and negate that word as phrase match instead.

**When to negate the signal word (phrase match):**
- The word appears across multiple bad queries in the same review session
- OR the brand has confirmed the intent category is out of scope

Example: If "event", "camp", "free", and "jobs" each appear across multiple bad terms, negate those words as phrase match — not each individual full term.

**When to negate the full term (exact match):**
- The signal word also appears in a keyword you are adding or monitoring — negating it as phrase match would create a conflict
- The term is highly specific and the signal word alone would over-negate

**Always check for conflicts before adding any negative:**
If a word you're considering as a phrase match negative also appears in a keyword being added or already active in the ad group, do not phrase match negate it. Go surgical — negate specific bad exact match phrases instead.

Example: If you're adding "sports registration app" as a keyword, do not phrase match negate "app" even if some app-related terms look bad. Negate the specific bad phrases ("free mobile app", "app download") as exact match instead.

## Keyword Opportunity Logic

Run this in parallel with negation throughout the entire review.

**Add as exact match keyword when:**
- The term has a conversion and is clearly relevant to the campaign theme
- The term has meaningful impressions (5+) and is relevant, even without clicks yet — it warrants monitoring
- The term represents a distinct intent variant worth capturing (e.g., "sports registration app" vs "sports registration software" — different framing, potentially different buyer mindset)

**Skip when:**
- The term is a close variant of an existing keyword — modern Google match types handle it
- The term has only 1–2 impressions and no clicks in a mature campaign

**Two-stage keyword development:**

Stage 1 — **Add and monitor**: New keyword goes into the existing ad group as exact match. Watch for clicks, conversions, and search impression share.

Stage 2 — **Promote to own ad group**: Trigger promotion when:
- Search impression share is low and the keyword isn't getting enough dedicated spend to get a fair test
- Early conversions signal strong standalone potential
- The intent framing is distinct enough to warrant dedicated ad copy (e.g., "app" terminology deserves different copy than "software" terminology)

## Output Format (for negation/keyword work)

Governed by **Output Discipline** in the plugin's `CLAUDE.md`. Read it before writing the summary.

**Row-level data goes to the CSV, not to chat.** Every evaluated term gets a row — search term, clicks, impressions, spend, CPC, decision, reasoning. That file is the record. Chat gets counts and the decisions that need the analyst.

Chat summary, in this order:

1. **Headline** — counts and recovered spend. "47 negates across 4 campaigns, $412/30d. 3 held for you."
2. **Pushed / ready to push** — one line per campaign: campaign name and count. No term lists unless asked.
3. **Held or skipped** — one line each, with the fact that would make the analyst overrule you and the stake. This is the only section that earns two clauses per item.
4. **Test candidates** — one line each: the term, the two readings, the question. Never negate unilaterally.
5. **Keyword opportunities** — one line each: term, destination ad group, match type, and the number that justifies it (conversion, impressions, or distinct intent).
6. **Keyword health note** — only if 1-impression cluster analysis was triggered, and only if it changes an action.

For phrase match negates, name the **signal word** being negated, not the full term.

A table earns its place when the analyst is comparing magnitude across four or more rows. For three items, use lines.

---

# Performance Pulse Checks: Diagnose Before Sounding Alarms

Search-term analysis isn't only for finding negatives — it's also the most reliable way to interpret a performance dip. **Before flagging any campaign as underperforming based on conversion data alone, run this diagnostic.**

the brand often have cyclical buyers. A youth hockey association admin enters and exits the buying cycle based on when their season starts; the same pattern holds for soccer, baseball, swim clubs, summer camps, and most sports verticals. Conversion data over a 7/14/30-day window can show a drop simply because the buyer isn't in market right now — not because anything is broken with the campaign.

The right question is not "are we converting?" but **"is the campaign still attracting the right buyer's queries?"** If yes, the campaign is doing its job and you wait out the cycle. If no, you have a real problem to flag.

## The Variable Elimination Ladder

Cross off the controllable variables one at a time. What remains is the cause.

**Step 1 — Did we change the ads?**
If no, CTR should be stable. Pull CTR for the strong-conversion baseline period and compare to the recent period. If CTR held or improved → ads are still performing.

**Step 2 — Did we change the landing page?**
If no, conversion rate should be stable for any given audience quality. Pull CVR for the strong baseline and compare. If CVR held within a normal band → the funnel is still converting.

**Step 3 — Are search terms still on-theme?**
Run the strong-month vs current-period theme comparison (below). If the term mix is consistent → targeting is still healthy.

**If all three hold and conversions are still down → the problem is market timing, not campaign quality.** Hold steady. Don't pause, don't slash budgets, don't recommend rework. Note it and wait for the cycle to turn.

**If any of the three breaks → that's where the real problem is.** Investigate that variable specifically before making changes elsewhere.

## Picking the Strong-Conversion Baseline

For B2B clients with cyclical buyers, you usually don't have clean year-over-year data — campaigns get rebuilt and structures change over 12+ months. So default to:

1. **Most recent strong-conversion month within the trailing 12 months.** Pull daily performance, identify the month with the highest absolute conversion volume that wasn't an obvious anomaly (single-day spike, ad change, conversion tracking glitch, etc.).
2. **Same period last year as a sanity check** — but only if the same campaign was running at the time. Otherwise this comparison is worse than useless.

Don't pick "best ever" if it's older than 6 months — too much can have changed in the account, the market, and the bidding algorithm.

**Watch for outlier months.** If one month's CVR is dramatically higher than every other month's, that month may be the outlier — and the recent period may actually be the true baseline. Sanity-check by asking whether the recent CVR is consistent with the trailing 4–6 month average.

## Search-Term Theme Comparison

The comparison is qualitative, not quantitative. You're looking for **theme and intent stability**, not exact term-by-term match.

Pull the top 30–50 search terms by clicks (with impressions and conversions) from:
- The strong-conversion month
- The recent low period

Then ask: *Does the recent period show the same buyer queries as the strong period?* The answer is almost always yes/no obvious. If the top terms in both periods are dominated by the same intent themes — for example "sports registration software", "youth registration platform", "team management software" — the targeting is healthy. If the recent period has shifted into educational/drill/competitor/tangential terms, you have real targeting drift.

Don't over-analyze the distribution. If five of the top ten terms in both periods share the same intent theme, that's a pass. The buyer is still showing up; they're just not converting today.

## When to Apply This Diagnostic

**Always run this before:**
- Reporting that a campaign is "underperforming"
- Recommending a budget cut on a campaign with weak recent conversions
- Recommending a campaign pause
- Flagging a CPA spike to the brand
- Saying "this campaign is a CPA disaster" or similar language

**Skip it for:**
- Campaigns that have been live <30 days (no real baseline yet)
- Campaigns with structural changes in the period being evaluated (different keywords, different LP, different bidding strategy) — the comparison is invalid
- Search-term mining work, where the focus is finding negatives rather than diagnosing performance

## Output Format for Pulse Check

Four lines, then stop. The analyst wants the verdict, not the ladder.

```
[Campaign] — market timing, not a problem.
CTR 3.1% → 3.2% · CVR 4.4% → 4.1% · terms still on-theme (7 of top 10 match)
Conversions 22 → 6 tracks the season, not the campaign.
Hold. Revisit when registration opens in August.
```

- **Lead with the verdict**, never with conversion data.
- Cross-off metrics go on one line, not in a table — the analyst only needs to see that they held.
- The theme comparison collapses to a count ("7 of top 10 share intent"). Do not print both term lists unless a variable broke.
- If a variable *did* break, that's case 3 under "What earns extra words" — name which one, show both periods, and say what to investigate.

---

# Scaling Claims Require Impression Share

The Variable Elimination Ladder above stops you from calling a campaign broken without evidence. This section is the mirror image: it stops you from calling a campaign **fixable with money** without evidence.

**Never describe a campaign as starved, capped, constrained, limited, throttled, scalable, or as "having headroom" — and never recommend moving budget into it — without first pulling impression share.** Required metrics:

- `metrics.search_impression_share`
- `metrics.search_budget_lost_impression_share`
- `metrics.search_rank_lost_impression_share`

See `references/gaql-queries.md` → "Impression Share".

## Raw impression volume proves nothing

Low impressions can mean either "we are losing available auctions" or "there are no auctions to win." Those lead to opposite recommendations and volume alone cannot distinguish them. Read it this way:

| Pattern | Diagnosis | Action |
|---|---|---|
| High IS (>80%), low volume | Demand ceiling. Niche or hyper-local query set. | Do NOT add budget. Money cannot buy impressions that do not exist. Report the ceiling. |
| Low IS, high budget-lost | Genuinely budget-constrained. | Budget increase is a valid lever — size it against the campaign's CPA first. |
| Low IS, high rank-lost | Ad Rank problem: bids, Quality Score, or ad relevance. | Bid and quality work. More budget will NOT fix this. |
| Low IS, both elevated | Two separate problems. | Name both. Do not collapse them into one recommendation. |

**Always name which lever you are recommending against.** "Lost to budget" is buyable with money; "lost to rank" is buyable with bids and quality. Saying only "there's headroom" hides which one and is not an actionable recommendation.

## Do not recommend scaling into an unverified CPA

Budget-constrained headroom in the account's *worst-CPA* campaign is a trap. Before recommending a budget increase, confirm the CPA is trustworthy — check `conversion_action.counting_type`. A `MANY_PER_CLICK` lead action inflates conversion volume and understates CPA, so the campaign that looks cheapest to scale may be the most expensive. Fix measurement first, then size the budget.

---

## The Agent's Role

- Never decide alone on ambiguous terms — always surface the question
- Always offer the test option when intent is unclear
- Flag when a signal word is a phrase match negative candidate vs when it conflicts with a keyword being added
- Prompt the analyst on client context before making account-knowledge-based decisions
- Default to asking, not assuming
- **For pulse checks: never call a campaign underperforming based on conversion data alone.** Run the variable elimination ladder first. If the problem is market timing, say so directly and recommend holding steady.
- **For scaling claims: never call a campaign starved, capped, or scalable based on impression volume alone.** Pull impression share first and name whether the loss is budget or rank. If impression share is already high, say the demand ceiling is the constraint and recommend against adding budget.

See `references/gaql-queries.md` for the exact queries to use when pulling search term data.
