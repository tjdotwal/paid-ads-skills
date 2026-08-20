# Naming Edge Cases

Some ad accounts in the manager account may not follow the standard pipe-delimited taxonomy exactly. Handle these situations as follows.

## Incomplete Naming (Fewer Than 5 Segments)

If a campaign name has fewer than 5 pipe-delimited segments, extract what you can and note the gaps.

- If funnel stage is missing, ask the user to clarify before applying strict relevance thresholds.
- If geo is missing, do not assume targeting scope — ask if geo-based negation is relevant.

## Non-Standard Separators

Some older campaigns may use ` - ` (dash with spaces) or `_` (underscore) as segment separators instead of ` | `. Parse these the same way.

Example: `Acme Scheduling - Demo - BOFU - Cold - USA` → treat identically to the pipe-delimited version.

## Legacy Campaigns Without Taxonomy

If a campaign name does not follow any recognizable taxonomy (e.g., `Campaign #1` or `Search - Generic`), do not attempt to infer funnel stage or audience. Instead:
1. Flag the campaign name as non-standard.
2. Rely on ad group names and keyword text as the primary context for relevance evaluation.
3. Note in your output that campaign-level context was unavailable.

## Brand Campaigns

Brand campaigns (containing the brand's brand name in the campaign name) have a different evaluation standard:
- Search terms should contain the brand name or a close variant.
- Generic non-brand terms are almost always negation candidates in brand campaigns.
- Competitor brand terms may or may not be intentional — flag as "Review" rather than auto-negating.

## Duplicate Campaign Names

If you encounter multiple campaigns with identical names, always confirm with the user which campaign ID to operate on before running any mutations.
