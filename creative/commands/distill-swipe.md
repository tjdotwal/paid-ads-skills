---
description: Monthly reflective pass over the copywriter's swipe brain — collapse, reconcile, prune, promote. Proposes changes, applies only after approval.
argument-hint: optionally name a brand (e.g. "riverbend") to also distill that brand's brain; omit to distill the plugin-level swipe files only
---

You are running the distillation pass that keeps the direct-response copywriter's memory sharp instead of bloated. Capture grows these files; this is the brake that shrinks them. Modeled on the `consolidate-memory` skill's reflective-pass structure, pointed at the swipe brain.

The user may have named a brand: $ARGUMENTS

## Scope

Always distill the agency-wide plugin files:
- `skills/direct-response-copywriter/references/winning-ads.md`
- `skills/direct-response-copywriter/references/principles.md`
- `skills/direct-response-copywriter/references/anti-patterns.md`

If a brand was named AND you're in (or can find) that brand's brain (`brands/[brand]/brand-brain/`), also distill its `winners.md`, `voice.md`, and `anti-patterns` notes.

## Phase 1 — Take stock (read only)

Read every in-scope file. Report a short inventory before proposing anything:
- Live entry count per file (flag if `winning-ads.md` is past ~25 — that's the overdue tripwire).
- Any leftover scaffold that should go: the labeled DEMO entry and unfilled TODO stubs in `winning-ads.md`, placeholder banned words in `anti-patterns.md`.

## Phase 2 — Propose a plan (do NOT write yet)

Draft the changes as a reviewable plan, grouped by the four operations. Never apply in this phase.

1. **Collapse** — entries that won the same way. Show: "These 3 winners all prove [pattern] → one principle in `principles.md`, compress the raw entries." Quote the entries.
2. **Reconcile** — contradictions. Show the two conflicting rules/winners and recommend which wins (newer result usually beats older) and whether to delete or mark the loser `superseded`.
3. **Prune** — stale entries (angle stopped working, client churned, DEMO/TODO leftovers). List each with a one-line reason.
4. **Promote** — a pattern proven across 2–3+ clients that should graduate UP from a brand brain into the plugin's shared `principles.md`.

## Phase 3 — Approval gate

Present the plan and wait for a yes. Let the user accept all, cherry-pick, or reject. Apply nothing unapproved.

**Hard boundary — the tool/data line:** writing into the plugin files (`principles.md` etc.) changes the shared agency brain that every client and teammate inherits. When a promotion or edit touches a plugin file, say so explicitly and treat it as **PR-worthy** — state that this should be committed as a reviewed change, not a silent local edit. Client-brain edits are free; plugin edits are governed.

## Phase 4 — Apply

Apply only the approved items. Preserve the entry schema at the top of each file. Then confirm: what changed, new entry counts, and any plugin-file edits that now need a PR.

Keep the whole thing a review-and-approve, not a rewrite-from-scratch. The human judgment in Phase 3 is the quality gate — never bypass it.
