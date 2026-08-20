# Google Ads New Campaign Build QA Checklist

This is the full QA checklist for new campaign builds. Walk through every item before considering a build complete.

## Ad Copy & Creative
- [ ] Ad copy headlines in Title Case (capitalize major words, lowercase: in, for, of, a, the, and, to, with)
- [ ] Display path URLs set using ad group keyword theme (e.g., `Managed-IT / Services`)
- [ ] Descriptions under 90 characters each
- [ ] Headlines under 30 characters each
- [ ] At least 12 headlines per RSA (Google recommends 8-10 minimum, 12-15 is ideal)
- [ ] At least 4 descriptions per RSA
- [ ] RSAs are ENABLED (not accidentally left PAUSED)
- [ ] Ad copy reflects the brand's brand voice (pulled from existing ads, not invented)

## Keywords
- [ ] Keywords set up with intentional match types (exact vs phrase vs broad documented)
- [ ] Ad groups tightly themed (one clear intent per ad group)
- [ ] No keyword dumping — each ad group should have 3-10 keywords, not 50+
- [ ] CPC bids set (ideally informed by historical data or Keyword Planner)
- [ ] Duplicate keyword check across ad groups within the same campaign
- [ ] All new keywords at correct status (ENABLED)

## Negative Keywords
- [ ] Basic negative keyword research completed and added
- [ ] Negatives added at campaign level across all active campaigns
- [ ] Conflict check: no negatives blocking active keywords or desired search terms
- [ ] Special attention to "free" negative if client offers free assessments/consultations

## URLs & Landing Pages
- [ ] Final URLs are accurate and resolving
- [ ] Landing pages optimized for desktop AND mobile
- [ ] Landing page matches ad group intent (don't send managed IT traffic to cybersecurity page)
- [ ] UTM parameters included for tracking

## Extensions
- [ ] Sitelink extensions added (keyword-optimized, driving to relevant pages)
- [ ] Callout extensions added (keyword-optimized per campaign/ad group)
- [ ] Call extensions added (if applicable)
- [ ] Location extensions added (if applicable)
- [ ] Any other relevant extensions considered

## Campaign Settings
- [ ] Campaign settings accurate to spec
- [ ] Location targeting correct (radius, specific locations, presence vs interest)
- [ ] Location options set to "Search Interest & Presence" (not just "Presence")
- [ ] Search network ONLY — display network turned OFF
- [ ] Auto-recommendation settings turned OFF
- [ ] Bid strategy compatible with budget type (no MAXIMIZE_CONVERSIONS with shared budgets)
- [ ] No unintended end date set (or if set, calendar reminder exists)

## Budget
- [ ] Daily budget × 30.4 = approved monthly budget
- [ ] Budget allocation across campaigns reflects priority and opportunity
- [ ] Consolidated campaigns have combined budgets (didn't lose spend when merging)

## Tracking & Analytics
- [ ] Page analytics setup and tags firing
- [ ] Conversion tracking setup and firing
- [ ] Cross-domain tracking setup in Google Tag Manager (if applicable)

## Geo Targeting
- [ ] Geo targeting matches the brand's service area
- [ ] "Near me" keywords paired with appropriate radius targeting (not overly narrow city targeting)
- [ ] Expanded geo (e.g., 25-mile radius) when using location-intent keywords

## Legacy Cleanup
- [ ] Old/legacy keywords paused to prevent cannibalization
- [ ] Old ad groups paused
- [ ] Deprecated campaigns paused (after contents recreated in surviving campaign)
- [ ] No duplicate ad groups left enabled across campaigns

## Final Verification
- [ ] Full GAQL scan confirms all elements at correct status
- [ ] Manual steps flagged with exact campaign/ad group names (not just IDs)
- [ ] User has reviewed and confirmed the build
