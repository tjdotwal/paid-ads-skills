---
name: beat-planner
description: Map a direct-response ad script onto a scene-by-scene beat plan for an animated explainer ad — assigns beat types, scene durations, per-scene narration within word budget, and a visual concept per scene. Use when planning scenes for an animated video ad, breaking a script into scenes or beats, or when the explainer-ad-director pipeline reaches its beat-plan phase. Not for writing the ad copy itself.
---

# Beat planner

Turns a script into a scene list. Output is a table the user approves and a
`scenes` array in `run.json`.

Read `../explainer-ad-director/references/beat-grammar.md` first. It holds the
duration arcs, the word budgets, and the beat type library.

## Procedure

1. **Pick the arc** from the target duration. Do not invent an arc or derive the
   scene count from how many sentences the script happens to have.

2. **Map the script onto the beats.** Most DR scripts already run hook → problem →
   solution → CTA, so the mapping is usually direct. Where the script is missing a
   beat the arc calls for, write that beat from the material already in the script —
   never from invented facts about the product.

3. **Fit each line to its word budget.** 2.5 words per second. A line over budget
   gets cut, not accelerated. This is the step people skip, and it is why narration
   ends up running past the visual.

4. **Write one visual concept per scene.** Concrete and singular. "A dental invoice
   with three lines snapping into highlight" works. "Trust and professionalism" does
   not.

5. **Note on-screen text per scene**, where any is wanted — the PROOF number, the
   price, the CTA. Record it as `onscreen_text` for the burn-in step. It is never
   generated.

6. **Build the asset roster.** Anything recurring across scenes gets one fixed
   description string. See `../explainer-ad-director/references/run-state.md`.

7. **Write `run.json`** with status `planned`, then show the table.

## Output table

| # | Beat | Sec | Narration | Visual | On-screen text |
| ---: | --- | ---: | --- | --- | --- |
| 1 | HOOK | 3 | Most implant quotes hide three fees. | A dental invoice, three lines snapping into highlight. | — |

Show the total duration and total word count under the table, and flag any line
over its budget.

## Checks before handing over

- Scene count and durations match the arc table exactly, and the durations sum to
  the target.
- HOOK is 3s, is scene 1, and works with the sound off.
- CTA is the last scene and names one action.
- No scene over 10s.
- Every line is inside its word budget.
- Every claim traces to the approved-claims allowlist.
- Something set up in PROBLEM gets resolved in SOLUTION.
