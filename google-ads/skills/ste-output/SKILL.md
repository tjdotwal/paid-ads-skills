---
name: ste-output
description: >
  Sentence-level writing rules for every analytical and ad-ops output from the
  google-ads, meta-ads, reporting and keyword-planner plugins, based on
  ASD-STE100 Simplified Technical English (the aerospace maintenance-manual
  standard Andrej Karpathy recommends for LLM output). Load it before writing any
  pulse check, pacing read, performance review, search term review, account
  audit, creative diagnosis, keyword research summary, or change proposal. Also
  load it when the user says "STE", "Simplified Technical English",
  "ASD-STE100", "write it like a manual", or "tighten the output". Output
  Discipline (in each plugin's CLAUDE.md) decides WHAT goes in the output; this
  skill decides HOW each sentence is built. NOT for ad copy, scripts, landing
  pages, or anything in the creative or explainer-ads plugins.
version: 0.1.0
---

# STE Output

ASD-STE100 is a controlled form of English. Aerospace makers built it in the late 1970s so that maintenance crews read each instruction one way only. It limits sentence length, allows one instruction per sentence, and gives each word one meaning.

Karpathy's point: people now spend more time reading what models produce than writing it themselves. Models know STE100 well, and asking for it makes output easier to read than the default style. The full standard is strict, so he asks for "80% of the way to ASD-STE100." This skill is that 80%, tuned for ad-ops.

## How this fits with Output Discipline

Output Discipline (each plugin's CLAUDE.md) still controls the shape: headline first, one line per decision, under 25 lines, row data in the CSV. This skill controls the sentences inside that shape. Apply both. If they conflict, Output Discipline wins on length and this skill wins on wording.

## The 80% rule: never trade a fact for a shorter sentence

Strict STE drops facts. One informal test found full ASD-STE100 lost 47% of the specific facts in a technical explanation, while loose "simple technical English" lost 8.5%. So:

- Never drop a number, a date window, an account name, a campaign name, or a caveat to meet a word limit. Split the sentence instead.
- Follow the spirit of STE. Do not chase the approved word list.
- If the uncertainty is the point, keep it. Say what is uncertain and which number would settle it.

## Sentence rules

1. **One instruction per sentence.** One action, one line. "Pause ad set 3. Move its $40/day to ad set 1." Never "Pause ad set 3 and consider moving some budget over."
2. **Start actions with the verb.** Write in the imperative. "Negate 'free'." Never "I'd recommend we look at negating 'free'."
3. **Length limits.** Actions: 20 words or fewer. Descriptions: 25 words or fewer. Split anything longer.
4. **One topic per paragraph, six sentences maximum.** In practice, most outputs have no paragraphs at all.
5. **Active voice, with the actor named.** "Meta reset the learning phase on Tuesday." Never "The learning phase was reset."
6. **Simple tenses only.** Past for what happened, present for what is true now, imperative for what to do. Never "has been seeing," "would have been," "is going to be trending."
7. **No noun stacks over three words.** "Brand search budget" is fine. "Q4 brand search campaign budget increase" is not. Rewrite it: "Increase the Q4 brand search budget."
8. **No -ing forms where a plain verb works.** "Spend is rising" becomes "Spend rose 18% (7d)."
9. **No phrasal verbs.** Use the single verb: scale up → increase, roll out → launch, dial back → decrease, look into → check, shut off → pause, figure out → find.
10. **Warnings go command first, reason second.** "Do not push these negatives to Hockey BOFU. That campaign bids on 'youth hockey' as a keyword." The stake goes in the same line.
11. **Steps go in a numbered list.** Use a number only when order matters. Use bullets otherwise.
12. **Full sentences keep their articles.** "Pause the ad set," not "Pause ad set." This does not apply to data lines (below).

## Data lines are exempt from grammar rules

The Output Discipline shorthand stays as it is:

> 🔴 Search – Brand: CPA $212 vs $96 baseline, conv 14 → 6

A data line is a label, not a sentence. Rules 6, 8 and 12 do not apply to it. Rule 13 (below) does.

13. **Every number carries its unit and window.** "$212 CPA (30d) vs $96 (3-mo baseline)." Never "CPA doubled" without both numbers. Use one window across a whole output unless you label the change.

## One word, one meaning

STE gives every word one meaning and uses that word every time. Models do the opposite. They switch synonyms to sound varied, and the reader then wonders whether "leads," "results" and "conversions" are three different numbers.

Use the term in the left column every time. Never use the ones on the right as substitutes.

| Use | Never substitute | Meaning |
|---|---|---|
| conversions (conv) | leads, results, signups, actions | The counted conversion events for that account |
| CPA | CPL, cost per lead, cost per result, CAC | Spend ÷ conversions |
| spend | cost, budget used, burn | Money spent in the window |
| budget | spend, allocation (when you mean spend) | Money planned for the period |
| pace | burn rate, run rate | Spend to date vs where the budget says it should be |
| baseline | average, norm, typical | The 3-month baseline defined in `reporting:advertising-performance-manager` |
| ad group | ad set (on Google) | Google only |
| ad set | ad group (on Meta) | Meta only |
| campaign name | the campaign, that one | Always the exact name from the account |
| negate / negative | exclude, block, filter out | Add a negative keyword |
| pause | kill, turn off, stop, shut off | Set status to PAUSED |
| enable | turn on, restart, relaunch | Set status to ENABLED |
| increase / decrease | bump, scale, ramp, dial, trim | Change a budget or bid; always give the before and after |
| move (budget) | shift, reallocate, rebalance | Move $X/day from A to B. "Reallocation" stays the noun. |
| make sure | ensure, verify that | Check a condition before an action |
| fatigued | tired, burned out, worn out | Frequency high and CTR falling; give both numbers |

Pick the term once per output for anything not in this table, then never vary it. If the account uses a different word for conversions ("bookings," "registrations"), use that word for the whole output.

## Hedge words

Cut "seems," "appears," "potentially," "somewhat," "may want to," and "it's worth noting." STE has no use for them, and they hide whether you know something.

- If you know it, say it plainly.
- If you do not know it, say what is missing. "Conv data for Oct 18–20 is not in yet. CPA is provisional."

## Beyond text

Karpathy ranks text as the slowest way to understand something and puts diagrams, interactive pages and video above it. For ad-ops:

- **Text (this skill):** the default. Pulse checks, pacing, reviews and change proposals.
- **Table:** row data with four or more items. Use the CSV for the full set.
- **Diagram:** account structure, funnel flow, or a restructure plan. Offer a Mermaid flowchart when the user must see how campaigns and ad groups connect.
- **Interactive page:** budget scenarios, such as "what happens to CPA if we move $X." Offer an Artifact with a slider. Do not build one unasked.

## Before and after

**Pacing read**

Before:
> It looks like Meta – Prospecting has been pacing a bit ahead of schedule this month, so we may want to consider dialing back the budget slightly to make sure we don't end up overspending before month-end.

After:
> 🟡 Meta – Prospecting: spend $3,410 vs $2,900 on pace (Oct 1–22).
> Decrease the budget from $140/day to $110/day. Without it, the account overspends by about $900.

**Search term warning**

Before:
> I'd hold off on adding "camp" as a negative across the board since some of the campaigns are actually targeting summer camp registrations and it could end up blocking relevant traffic.

After:
> Do not negate "camp" at the account level. Summer Camps BOFU bids on it: 41 conv (30d).

**Creative diagnosis**

Before:
> The top ad seems to be getting a little tired: frequency has been climbing and results are starting to taper off, so it might be time to look into refreshing the creative.

After:
> Ad "Spring Signup V2" is fatigued: freq 4.1 (7d), CTR 1.9% → 0.8%.
> Launch the next creative test this week.

## Check before you send

- [ ] Each action is its own sentence and starts with a verb.
- [ ] No action is over 20 words. No description is over 25.
- [ ] Every number has a unit and a window.
- [ ] Each concept uses one term for the whole output, from the table where one applies.
- [ ] No passive voice, phrasal verbs, or hedge words.
- [ ] Warnings put the command first.
- [ ] Every number and caveat from the analysis is still there.
