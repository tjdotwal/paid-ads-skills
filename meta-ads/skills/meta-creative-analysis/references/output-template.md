# Output Template — Meta Creative Analysis Brief

The brief is markdown delivered inline in chat. Use this template as the section skeleton — fill with real numbers and findings. Do not add sections beyond these unless the analysis genuinely needs them; do not skip sections unless an edge case in `SKILL.md` says to.

**Reader test:** A junior copywriter should be able to read this and start a creative brief with no follow-up questions. If a line forces them to interpret your meaning, rewrite it.

---

## [Client] Creative Analysis — [Window] ([date range])

### 1. Account summary

- **Account:** [client name + Meta account ID]
- **Campaign / ad set:** [name + ID]
- **Window:** [N days] ([YYYY-MM-DD] → [YYYY-MM-DD])
- **Spend / Impressions / Reach:** [$X] / [N] / [N]
- **Conversions:** [N] @ [$CPA]
- **Active ads in window:** [N] | **Paused ads that delivered:** [N]
- **Flags:** [decay, momentum, low-volume, no-conversions, multi-campaign, etc.]

### 2. Ad-level comparison table

| Ad name | Status | Spend | Impr | CTR | CPA | Conv | Conv rate | Spend share | Format | Composite rank | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|

Composite rank = average of independent ranks across CPA, Conv Rate, CTR, Spend Share. Lowest avg = best. Verdict = KILL / SCALE / ITERATE (— for ads too new or below the data floor).

### 3. Deep-dive on each ad

(Or top 3 + bottom 1 if N > 10.)

For each ad, in composite-rank order, deliver TWO blocks plus a trend table plus a 2-sentence synthesis:

---

**[Ad name] — Composite rank #[X]**
*Individual ranks: CPA #X | Conv Rate #X | CTR #X | Spend Share #X*

**Creative format**
- **Format:** #N [Format name from 43-library] — [1-line note if hybrid]
- **Creative copy** (on-image, verbatim, top to bottom):
  > [Line 1 of on-image copy]
  >
  > [Line 2 of on-image copy]
  >
  > [Line 3 of on-image copy]
  >
  > (If thumbnail too low-res to read body-level on-image text: *"Thumbnail resolution can't resolve body-level on-image copy."*)
- **Visual style:** [One sentence — imagery type + layout + mood]

**Ad copy framework** (Meta API fields)
- **Headline:** "[verbatim]" — [≤8 words on what it's doing]
- **Body:** "[verbatim — summarize only if >3 paragraphs]" — [≤8 words on what it's doing]
- **Description:** "[verbatim]" — [≤8 words on what it's doing]

**Trend (30d → 14d → 7d → 3d):**
- CPA: $X → $X → $X → $X — [decaying / momentum / stable]
- CTR: x% → x% → x% → x% — [decaying / momentum / stable]

**Hook/hold (video ads only):** thumbstop x% | hook rate x% [weak <25% / strong ~30% / elite 40%+] | hold rate x% — [one clause: where the video loses people]

**Why it's [winning / losing]:** [2 sentences max. Tie every claim to a specific metric. No abstractions.]

**Verdict: [KILL / SCALE / ITERATE]** — [one line: for ITERATE, name the single variable to change; for KILL, the metrics that seal it; for SCALE, the headroom signal]

---

### 4. Winning messaging theme

**One sentence:** [The dominant pattern across top performers, stated concretely. Name the ads that carry it. Name the on-image element or copy line that defines it. No abstract framing terms.]

**Evidence:**
- [Ad X] — ranks #1 composite, [specific metric proof: e.g., "won CTR at 2.52%"]
- [Ad Y] — ranks #2 composite, [specific metric proof]
- [Ad Z] — does NOT carry this theme, ranks #N, [specific metric proof of the contrast]

### 5. Recommendations — directional next-test theses

For each test angle (2–3 of them), use this format:

**Test angle 1: [Concrete one-line description naming the source ad(s) and what to keep/swap]**

- **What to build:** [Specifics — which ad, what to change, what to keep. Reference the ads' actual headlines / body copy by their verbatim words. A junior copywriter should be able to start a brief from this line.]
- **Why:** [One sentence. Name the metric proof from this analysis. Name the number.]

---

*Hand off to ad-creative-strategist for concept build.*

---

## Example — RainGuard Golf, May 18–24, 2026

### 3. Deep-dive (excerpt — single ad)

---

**priced_cancelled_golf_lessons_2 — Composite rank #1**
*Individual ranks: CPA #1 | Conv Rate #1 | CTR #1 | Spend Share #1*

**Creative format**
- **Format:** #1 Bold Headline Ad
- **Creative copy** (on-image, top to bottom):
  > TEACH RAIN OR SHINE
  >
  > Don't let the weather decide when you can coach
  >
  > Starting at $14,500 USD. Does not include shipping.
  >
  > Commercial 2-bay canopy built for golf instruction
  >
  > REQUEST A FREE QUOTE
- **Visual style:** Real photo of instructor + student teaching under the canopy in actual rain, bold white serif headline on dark teal band above the photo, mood = grounded and authentic.

**Ad copy framework**
- **Headline:** "Cancelled Lessons Cost You Money" — names the financial loss
- **Body:** "Golf instructors — cancelled lessons mean lost income. One rainy afternoon can wipe out an entire day of teaching. RainGuard Golf Teachers Edition keeps your instruction schedule running, even when the forecast doesn't cooperate..." — identity hook, loss-aversion frame, mechanism-light
- **Description:** "Stop cancellations with a 2-bay teaching canopy" — restates the offer in outcome terms

**Trend (30d → 14d → 7d → 3d):**
- CPA: $40.89 → … → … → …
- CTR: 1.59% → … → … → …

**Why it's winning:** Drove 100% of campaign conversions (6 of 6) at $40.89 CPA against a $46.15 campaign average. The loss-aversion hook + live-action proof scene combo outperformed the feature/spec ad (`priced_professional_canopy_1`) which spent $28.58 with zero conversions on 1,519 impressions.

### 5. Recommendations (excerpt)

**Test angle 1: Take `priced_cancelled_golf_lessons_2` and add dollar math to the headline.**

- **What to build:** Keep the same image (instructor + student in the rain under canopy). Replace the on-image headline "TEACH RAIN OR SHINE" with a dollar-quantified version: e.g., "8 CANCELLED LESSONS = $720 GONE" with the subhead "Don't let the weather decide when you can coach." Keep all body copy and the description unchanged.
- **Why:** The control wins on income-loss framing (drove 100% of conversions) but never puts a dollar figure on the loss. Sharpening the math tests whether quantified pain converts at a lower CPA than the current $40.89.
