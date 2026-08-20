# Winning Ads — annotated swipe brain

This is the highest-value file in the copywriter's memory. It is **not** a screenshot folder.
Every entry is a *diagnosis* of why a real ad won, structured so the lesson transfers to the
next client. On any copy job, the skill reads this file, finds the entries whose **resistance
type + awareness stage + angle** match the current job, and models their structure.

## Rules for this file

- **Only real winners go here.** An entry earns its place with a result (ROAS, CPA, scale, win-rate vs control). No result → it is not a winner, it is a guess. Keep guesses out.
- **The `Why it won` line is the whole point.** Write the *transferable* reason, not "it performed well." If the lesson only applies to this one client, it belongs in `client-voice/`, not here.
- **Verbatim copy only.** Paste the exact words that ran. Never paraphrase a winner into marketing-speak — the specific language IS the asset.
- **Promote patterns upward.** When three entries win the same way, that pattern graduates into `principles.md` during the monthly distillation pass, and the raw entries can be compressed.

---

## Entry schema (copy this block for each new winner)

```markdown
## [Client / Format] — "first line of the hook"
- **Result:** [the proof it won — ROAS / CPA / spend scaled to / beat control by]
- **Angle:** [Pain point | Outcome | Social proof | Curiosity | Comparison | Urgency | Identity | Contrarian]
- **Awareness stage:** [Unaware | Problem-aware | Solution-aware | Product-aware | Most-aware]
- **Resistance type:** [Functional | Emotional]  → [how the copy answered it]
- **Mechanism used:** [the specific, credible reason the offer delivers]
- **Why it won:** [1–3 sentences. The transferable lesson.]
- **Full copy:**
  > [verbatim — hook, body, CTA]
```

---

## ⚠️ FORMAT DEMO — replace, do not cite as real data

> The entry below exists only to show the shape. The numbers and copy are illustrative, not a
> real result. Delete it once you have two real winners logged.

## [DEMO Client] / Meta single image — "You don't have a lead problem. You have a follow-up problem."
- **Result:** [ILLUSTRATIVE] beat control by ~40% on CPL, scaled to $X/day over N weeks
- **Angle:** Contrarian
- **Awareness stage:** Problem-aware
- **Resistance type:** Functional → reframes the reader's assumed problem, then proves the real one with a mechanism
- **Mechanism used:** [the specific system that fixes follow-up]
- **Why it won:** Contrarian reframe stops the scroll by contradicting what the problem-aware reader already believes, then the mechanism makes the reframe credible instead of just clever. Transfers to any market where the buyer has misdiagnosed their own problem.
- **Full copy:**
  > [verbatim hook / body / CTA would go here]

---

## Backfilling this file

The fastest way to fill this file is `/pull-winners`, which reads the Meta and Google Ads
MCPs over a date window, finds ads that beat their campaign's real KPI *and* earned spend,
and drafts diagnosed entries for approval. `/log-win` adds a single entry by hand.

Two rules while backfilling:

- **A result or it doesn't go in.** ROAS, CPA, spend scaled to, or win-rate vs control.
- **Write the transferable reason, not the outcome.** "Contrarian reframe works when the
  buyer has misdiagnosed their own problem" transfers. "This ad did well" doesn't.
