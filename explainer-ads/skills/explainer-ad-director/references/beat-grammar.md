# Beat grammar for animated explainer ads

One beat = one scene = one clip = one narration line = one visual concept. Never
merge two beats into one clip, and never split one beat across two clips. That
one-to-one rule is what makes a scene cheap to regenerate when it comes back wrong.

## Narration density — planning figure only

The table below **plans** a script. It does not decide the timing. Measured
ElevenLabs delivery came in at **3.08 w/s overall, ranging 2.51 to 3.95** depending on
the line — short punchy lines run fast, lists and unfamiliar words run slow. Planning
at 2.5 built 4.4s of dead air into a 30s ad.

Plan at **3.0 w/s**, then **record the narration and re-time every beat to the
measured audio before generating video.** See the `narration` skill. The estimate
gets you a script of roughly the right size; only the audio decides the cut.

| Scene length | Word budget (at 3.0 w/s) |
| ---: | ---: |
| 3s | 8–9 |
| 4s | 11–12 |
| 5s | 14–15 |
| 6s | 17–18 |
| 8s | 23–24 |
| 10s | 29–30 |

Treat these as a target for drafting, not a gate. A line slightly over budget is
fine — the beat moves to fit it at the narration step. A line 2x over budget is a
line that needs cutting, and that is worth catching before anyone records it.

Every scene should end with **0.2–0.4s of visual after the line lands**, so the cut
does not clip the last word.

## Duration arcs

Pick the arc from the total duration the brand bought. Every arc opens on HOOK and
closes on CTA, both as their own scenes.

### 15s — 4 scenes, ~38 words
| # | Beat | Sec |
| ---: | --- | ---: |
| 1 | HOOK | 3 |
| 2 | PROBLEM | 4 |
| 3 | SOLUTION | 5 |
| 4 | CTA | 3 |

No proof beat fits in 15s. Do not try to add one — cut to one problem and one
promise.

### 20s — 5 scenes, ~50 words
HOOK 3 · PROBLEM 4 · AGITATE 4 · SOLUTION 6 · CTA 3

### 30s — 6 scenes, ~75 words
| # | Beat | Sec |
| ---: | --- | ---: |
| 1 | HOOK | 3 |
| 2 | PROBLEM | 5 |
| 3 | AGITATE | 4 |
| 4 | SOLUTION | 7 |
| 5 | PROOF | 6 |
| 6 | CTA | 5 |

### 45s — 8 scenes, ~112 words
HOOK 3 · PROBLEM 5 · AGITATE 5 · FAILED_ALT 5 · MECHANISM 8 · SOLUTION 8 · PROOF 6 · CTA 5

### 60s — 9 scenes, ~150 words
| # | Beat | Sec |
| ---: | --- | ---: |
| 1 | HOOK | 3 |
| 2 | PROBLEM | 5 |
| 3 | AGITATE | 6 |
| 4 | FAILED_ALT | 6 |
| 5 | MECHANISM | 9 |
| 6 | SOLUTION | 9 |
| 7 | PROOF | 8 |
| 8 | OBJECTION | 6 |
| 9 | CTA | 8 |

### Over 60s
Extend by repeating MECHANISM → PROOF → OBJECTION blocks, one offer element per
block. Two hard caps: no scene over **10s**, and HOOK stays at 3s no matter the
total length.

## Hard scene rules

- **Beats are sized from measured audio.** Planned lengths are provisional until the
  narration exists. This is the rule that prevents the most expensive class of error.
- **HOOK is never longer than 3s** and never merged into another beat. It is the
  only scene that has to work with the sound off.
- **No scene over 10s.** Longer scenes drift in style, cost more to redo, and stall
  the cut rhythm.
- **CTA is always the last scene** and always its own.
- Scene count comes from the arc table, not from sentence count in the source script.

## Beat type library

Each beat has a job. Give the animator one idea per beat — a scene carrying two
ideas reads as neither.

| Beat | Job | Visual grammar |
| --- | --- | --- |
| `HOOK` | Stop the scroll. Pattern interrupt, sharp question, or a number. | One bold subject, centre frame, immediate motion on frame 1. No slow build, no establishing shot. |
| `PROBLEM` | Name the pain in the viewer's own words. | Show the friction concretely — the mess, the queue, the error, the pile. |
| `AGITATE` | Cost of leaving it alone. Stakes, not adjectives. | Escalate the same visual: the pile grows, the meter climbs, the clock runs. |
| `FAILED_ALT` | What they already tried that did not work. | The alternative shown breaking down or being set aside. |
| `MECHANISM` | Why this works. The "how", which is what earns belief. | Diagram, cutaway, or step-through. The one beat where a schematic beats a scene. |
| `SOLUTION` | The offer, plainly. | Product or service in use, doing the thing, resolving the earlier friction shot. |
| `PROOF` | Evidence: a stat, a result, a credential. | The number on screen, large, with the source. Burn it in post — never generate text. |
| `OBJECTION` | Kill the blocker — price, time, risk, effort. | Direct visual answer: the calendar clearing, the guarantee stamp, the short setup. |
| `CTA` | One action, one place to take it. | Clean end card, product plus wordmark, generous margin for the burned text. |

## Continuity across beats

- **Resolve what you set up.** The friction object introduced in PROBLEM should
  reappear resolved in SOLUTION. That callback is most of what makes a cut-together
  set of clips feel like one ad.
- **Carry the asset roster.** Every recurring character, object, and location is
  described with the same words in every scene prompt. See `run-state.md`.
- **One escalation direction.** Pick a visual quantity that moves in one direction
  through the ad — clutter clearing, a bar filling, a colour warming.

## Claim discipline

Only claims the brand supplied and approved go in the script. No invented
statistics, no invented testimonials, no implied endorsement, no before/after
outcome that was not provided in writing. Where no claims were supplied, write to
observable mechanics — what the thing is and what it does. This is the same
allowlist rule the creative copy skills use, and it is a compliance requirement,
not a stylistic preference.
