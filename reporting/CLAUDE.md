# Reporting agent

Two skills, both read-mostly, both cross-channel. Neither has an MCP server of its own — they orchestrate the `google-ads` and `meta-ads` plugins.

| Skill | Question it answers |
|---|---|
| `budget-pacing-manager` | Did the money go out on schedule, and is it in the right places? |
| `advertising-performance-manager` | Did that money buy anything, versus recent months? |

Run pacing first. Reallocating budget toward a campaign that's quietly broken is worse than leaving it alone, so knowing what's working comes before deciding where money goes.

## Default posture

- **Live API data, never a spreadsheet.** A sheet is a stale snapshot of what the APIs already hold. The only thing that comes from a file is monthly budget *intent* (`config/budget.md`), because no API knows what you meant to spend.
- **Cross-channel first, then per channel.** Report the total, then break it down. A healthy total can hide one starving channel and one overspending one.
- **Numbers in the open.** Never a percentage without the absolute figure behind it. "−45%" is unactionable; "−$4,577 by month end" isn't.
- **Say what you counted.** Meta conversion counting is a judgment call with several defensible answers. State which events were summed, every time.
- **A failed pull is not a zero.** If a channel doesn't respond, say so. Reporting a failed pull as zero spend or zero conversions invites a badly wrong correction.
- **Terse output.** These get read on a phone between other things. Headline, then the lines that support one decision. No preamble, no restating the date as prose.

## Guardrails

- **Never mutate without explicit confirmation.** Both skills propose; the user approves. Read back every change and verify.
- **Units.** Google Ads budgets are in micros ($135 = 135000000), Meta in minor units ($45 = 4500). This is the highest-cost mistake available in this plugin.
- **Budget conservation.** Reallocation nets to zero by default. Raising or cutting a monthly total needs explicit authorization and gets said out loud.
- **Don't act on noise.** Inside ±10% on a small sample is nothing. Under 10 conversions in the window is too volatile to scale on.
- **Rule out tracking before diagnosing performance.** A broken pixel is indistinguishable from a collapse, and optimizing against phantom data makes things worse.

## Setup

Copy `config/budget.example.md` to `config/budget.md` and fill in the monthly intent and account IDs. That filename is gitignored. Without it, the skills ask for the numbers and note that the answer isn't saved.

## Scope

One brand at a time, by design. These were adapted from a multi-account agency workflow; the per-account triage loop is deliberately gone. For several brands, keep a config per brand or edit between runs.
