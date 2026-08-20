---
description: Log a winning (or losing) ad into the copywriter's swipe brain, auto-formatted and diagnosed.
argument-hint: paste the ad copy + its result (ROAS/CPA/scale), or say "loser" + why it was killed
---

You are logging an ad result into the direct-response copywriter's memory so future copy compounds on it.

The user's input (ad copy + result, or a kill + reason) is:

$ARGUMENTS

## What to do

1. **Decide winner or loser.**
   - A **winner** has a real result (ROAS, CPA, scale, beat-control). → it goes in `winning-ads.md`.
   - A **loser / killed line** → it goes in the "Kills log" section of `anti-patterns.md`, and if the reason is a repeatable rule, also add it as a structural anti-pattern or banned word.

2. **If a winner**, diagnose it before writing the entry. Fill every field in the schema by reading the copy through the skill's lens (`skills/direct-response-copywriter/references/principles.md`):
   - **Angle** (one of the 8), **Awareness stage**, **Resistance type** + how the copy answered it, **Mechanism used**, and the one-to-three-sentence **Why it won** — the *transferable* lesson.
   - If the result the user gave is vague ("it did well"), ask once for the actual metric. A winner without a result does not get logged — that is the file's core rule.
   - Paste the copy **verbatim**. Never paraphrase it.

3. **Write it.** Append the formatted entry using the schema block at the top of
   `skills/direct-response-copywriter/references/winning-ads.md` (winner) or the Kills log
   in `skills/direct-response-copywriter/references/anti-patterns.md` (loser). Do not disturb existing entries.

4. **Client voice.** If a lesson is client-specific (a banned word, a register note, a proven angle for *this* client only), also write it to
   `skills/direct-response-copywriter/references/client-voice/[brand].md` (create the file if needed), not to the general files.

5. **Confirm** back to the user: which file you wrote to, the diagnosis you assigned (angle / awareness / resistance), and the one-line lesson — so they can correct the diagnosis if you read it wrong.

Keep it fast. This should feel like a 10-second capture, not an interview. Ask at most one clarifying question, and only when a required field (the result, or which client) is genuinely missing.

6. **Size tripwire.** After appending, count live entries in `winning-ads.md`. If it now exceeds ~25, tell the user the file is overdue for distillation and suggest running `/distill-swipe`. Log the entry either way — the tripwire is a nudge, not a block.
