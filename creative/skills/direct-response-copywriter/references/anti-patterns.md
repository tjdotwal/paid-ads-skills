# Anti-patterns — what gets killed and why

The negative half of the loop. Every time copy gets rejected, rewritten, or a test loses,
the *reason* gets distilled into a rule here. The skill reads this file before writing and
treats each rule as a do-not-cross line. Pairs with the `no-ai-slop` skill.

Feedback flows in two steps:
1. **In the moment**, a correction is captured to session memory so it isn't lost.
2. **On the monthly review**, recurring corrections graduate into a durable rule here.

## Rules for this file

- Write the rule as a **command**, not a story. "Never open a Riverbend Dental ad with a stat" beats "there was this one time the stat didn't work."
- Include the **why** in one clause so the rule survives context changes.
- If a rule only applies to one client, move it to `client-voice/[brand].md`.

---

## Banned words / phrases (agency-wide)

<!-- Add words you consistently kill. Example format: -->
- `unlock` — [reason, if given]
- `elevate` — [reason]
- `game-changer` — [reason]
<!-- ^ these are placeholders; keep only the ones that are actually true for the team -->

## Structural anti-patterns

- **Word-swap variants.** Two "variations" that differ only in synonyms are not a real test and waste testing budget. Variants must test different strategic frames OR different rhythm/density of the same frame. (SKILL.md hard rule 5.)
- **Orphan components.** Copy written without awareness of what comes before/after in the chain. Image copy must hand off to the LP hero. (Hard rule 3.)
- **Offer-first to a problem-aware reader.** Leading with the offer before the reader knows they need it. (See `principles.md` awareness stages.)
- *[Add corrections here as they recur.]*

## Kills log (raw — distill upward monthly)

<!-- Fast capture. When /log-win logs a loser or you kill a line, drop it here verbatim. -->
<!-- ## YYYY-MM-DD — [brand] — killed: "the line" — why: [reason] -->
