# Full JSON Template Library — Canonical Source

Per-format JSON templates are not duplicated in this file. The canonical taxonomy lives in the
`creative-format-library` skill so there is only one place to maintain:

- **`creative-format-library/SKILL.md`** — all 53 templates by section, with a one-line
  descriptor and classification tips for each.
- **`creative-format-library/references/format-detail.md`** — full specs for the formats that
  carry real methodology (43–53): structure, rules, substantiation gates, video script beats,
  and remix logic.
- **`creative-format-library/references/json-prompt-spec.md`** — the JSON prompt key
  architecture, the two-stage brand-DNA workflow, and a complete worked example.

Load `creative-format-library` when you need the taxonomy. Use the summary table in this
skill's `SKILL.md` as the offline fallback when it isn't loaded.

## When to go fetch the JSON

Only fetch when the user explicitly asks for a JSON / Nano Banana 2 / HigsField prompt. Default brief output is the design-team-ready brief format described in `SKILL.md`, not JSON.

## How to use it

1. Load the `creative-format-library` skill.
2. Find the template by number in `SKILL.md`. For 43–53, read its entry in `references/format-detail.md` — those carry structure, rules, and substantiation gates the one-liner can't.
3. For image generation, take the key structure and worked example from `references/json-prompt-spec.md` and fill the bracketed values from the brand's research brief.
4. Never improvise a JSON template from memory. The structural details that matter for output quality — lighting, camera, `ColorRestriction` patterns — are specific, and a half-remembered version produces worse images than a plain-English brief.

## If the taxonomy isn't loaded

Use the format names and one-line descriptors from the Format Library section of this skill's `SKILL.md` to brief in plain English. That's a real fallback, not a degraded one — a clear written brief beats an improvised JSON template. Note to the user that the inline list may not cover every current format.
