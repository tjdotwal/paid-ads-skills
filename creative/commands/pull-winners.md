---
description: Auto-draft winning-ad entries by pulling real performance from the Meta + Google Ads MCPs. Proposes diagnosed entries; writes only after approval.
argument-hint: client name (required) + optional window ("last 30 days" default) and channel ("meta" | "google" | both)
---

You are closing the data-in loop: instead of waiting for a human to log wins by hand, you read the actual ad accounts, find what won, diagnose it, and draft entries for the swipe brain. This is the accelerator that makes the brain fill as real data comes in.

Input: $ARGUMENTS  (expect a brand; default window = last 30 days; default channel = every ad MCP connected)

## Phase 1 — Scope

- Confirm the brand and resolve where its winners live: `brands/[brand]/brand-brain/winners.md` if that brain exists, otherwise fall back to the plugin's `skills/direct-response-copywriter/references/winning-ads.md`.
- Set the date window and which channels to pull (Meta, Google, or both).

## Phase 1.5 — Learn what "good" means for THIS client (required)

Read `brands/[brand]/brand-brain/kpis.md` before pulling anything. Structure it as **default + per-campaign overrides**:

- **Default KPI** — the single bottom-funnel custom conversion that judges a winner for most of the account, plus its benchmark (target/acceptable CPA, or min ROAS for the few value-goal clients).
- **Campaign overrides** — campaigns whose goal differs get their own KPI (e.g. a webinar-signup campaign judged on webinar signups + its own CPA, not the main purchase goal). Match by campaign name/pattern.
- **Exclusions** — conversion actions that never count toward "winner."

**Do not guess a universal metric, and do not judge every campaign by the brand default.** Ranking a webinar-signup campaign's ads against the main purchase KPI makes real winners look like losers. If `kpis.md` is missing, ask the user to define it once for this client and offer to save it — then proceed. Never rank without it.

## Phase 2 — Pull performance

- **Group ads by campaign first, then resolve each campaign's KPI** from `kpis.md` (override if the campaign has one, else the default). Judge every ad against *its own campaign's* KPI + benchmark — never cross-compare a webinar-signup ad against a purchase goal.
- **Meta:** use `mcp__plugin_meta-ads_meta-ads__insights_get` (ad level) over the window, requesting each campaign's KPI conversion action. A winner is: strong on that campaign's real KPI *and* it earned spend (the algo kept feeding it = signal) — not high spend on the wrong action.
- **Google:** discover the google-ads reporting tool via ToolSearch (`+google-ads report`), pull ad-level performance for the relevant KPI conversion action(s), rank the same way.
- Take the **top ~5–10 per campaign-KPI group** so smaller campaigns (e.g. webinar signups) surface their own winners instead of being buried under the main goal. The per-campaign benchmark decides who clears the bar; the human confirms in Phase 4.

## Phase 3 — Enrich (get the actual creative)

For each candidate, fetch the real copy/creative so you can diagnose it, not guess:
- Meta: `ad_get` + `creative_get` to get the copy fields, then see the creative itself:
  - **Static / carousel** → `ad_image_get` to read the on-image copy, primary text, headline.
  - **Video** (the creative has a `video_id`) → **`ad_video_get`**. Video ads must be diagnosed from the transcript + keyframes, not from the thumbnail and body copy. The hook lives in the first 3 seconds of spoken script and opening frame; neither appears anywhere in the creative's text fields, so a copy-only read of a video winner tells you nothing about *why* it won — which is the entire point of the swipe entry.
  - **Always pass the brand's `ad_account_id` explicitly** to `ad_image_get` and `ad_video_get`. Asset lookups are account-scoped, and without it they degrade silently to a 64px thumbnail — no error, just an unreadable creative you might not notice.
  - Paste the transcript's script into the entry verbatim, the same as you would on-image copy for a static. The script *is* the reusable asset for a video winner — an entry that only records "it was a video" teaches nothing later.
- Google: pull the RSA headlines/descriptions from the ad resource.

**Unverified-creative flag.** If you cannot see the creative — `ad_video_get` fails (Meta gates video `source` behind a Page access token for some page-owned videos), the image won't resolve, or the asset is otherwise unavailable — you may still draft the entry from the copy layer, but it **must** carry:

> `(creative unverified — copy-layer diagnosis only)`

Put it on the entry's diagnosis fields (Angle / Why it won / Mechanism), because those are the ones a copy-only read can't actually support. This is not optional and it is not a low-confidence marker: `(low confidence — confirm)` means "I read the creative and I'm unsure," while this flag means "I never saw the creative." A reader mining the swipe file later needs to know which entries were diagnosed from the real thing.

## Phase 4 — Diagnose + draft (do NOT write yet)

For each candidate, fill the `winning-ads.md` schema by reading the creative through `skills/direct-response-copywriter/references/principles.md`:
- **Result** — auto-filled from the insights pull (spend, CPA/ROAS, window). This is the proof field `/log-win` normally has to nag for; here it's free.
- **Angle / Awareness stage / Resistance type / Mechanism / Why it won** — your read of the creative. Mark any field you're unsure of as `(low confidence — confirm)` so the human corrects it.
- Paste the copy **verbatim**.
- **De-dupe:** skip anything already logged in the target file.

Present all drafts as a reviewable list.

## Phase 5 — Approval gate

Wait for a yes. The human confirms which candidates are genuinely winners (not just high-spend noise) and fixes any diagnosis you flagged. Write nothing unapproved — high spend alone is a candidate, not a confirmed winner.

## Phase 6 — Write

Append approved entries to the target `winners.md` / `winning-ads.md`, preserving the schema. Confirm what was added and the new entry count (trigger the distill nudge if it passes ~25).

## Making it a routine

This command is the core; to run it weekly, wrap it in a scheduled task (see the `schedule` skill) that runs `/pull-winners [brand]` every Monday and posts the drafts for approval. Keep the approval gate even when scheduled — auto-pull drafts, human confirms.
