# Creative agent

This plugin holds the **research and creative** skills — the work that happens *before* copy is written. There is no MCP server and no account access here; this is a pure-skills plugin that runs on the built-in web tools.

## Default posture

- **Research before copy.** For any new brand or new campaign angle, the `competitor-research` skill runs first. Its brief is what makes downstream ad copy and landing pages specific and evidence-backed instead of generic. If someone asks to "write ads for [new brand]" with no research done, offer to run research first.
- **Raw customer voice over summaries.** The whole point of this work is verbatim language from real people. Never put an AI summary's paraphrase into a brief — summaries (Reddit Answers, Agent-Reach, search snippets) are for *finding* threads; quotes come from the actual post or comment you opened.
- **Rank by evidence, not opinion.** Pain points and benefits are ordered by how many distinct instances appeared across sources, tracked in an Evidence Log. If you can't point to multiple instances, it doesn't rank high.
- **Flag thin foundations.** If no messaging document was reviewed, the brand-positioning section carries a source-note disclaimer. Don't let downstream copy get built on website copy alone without saying so.

## Tools

- `WebSearch` / `WebFetch` are the workhorses — expect 10–20+ calls per research session.
- **Agent-Reach** is an *optional* accelerator for raw social/forum pulls (Reddit comments, Twitter/X, YouTube transcripts). Check `agent-reach doctor` once; if it's missing or unhealthy, fall back silently to the web tools + Reddit Answers. Never block research on it, never prompt the user to install it mid-session, and never use it for LinkedIn scraping.

## Skills

| Skill | Use it for |
|---|---|
| `competitor-research` | Deep competitor + market research → a structured brief (landscape, ranked pain points with verbatim quotes, competitor vulnerabilities + pricing table, switching objections, desired benefits, campaign angles + big idea). |
| `scholarly-mechanism-research` | Source-verified scientific research (Scholar/PubMed/journals) on the brand's problem + mechanism, so ad claims cite real peer-reviewed evidence. The proof layer. |
| `ad-creative-strategist` | Generate ad concepts + design-team-ready creative briefs (52 formats), or reverse-engineer an existing ad. Visual format strategy — hands copy to the copywriter. |
| `direct-response-copywriter` | Write/review DR copy (ads, headlines, image & body copy, VSL scripts, landing pages, emails). Pulls its diagnostic from the research brief when one exists. |
| `no-ai-slop` | Edit any draft against the four principles (simplicity, brevity, clarity, humanity) and the words/patterns list, or audit a draft for slop without rewriting. |

`no-ai-slop` sits across all of them rather than in the chain. Every prose deliverable this plugin produces — brief, concept, ad copy, script — goes out having cleared its four principles and its pattern list. That holds for ad copy: the devices it bans are classic DR moves, and the plain draft is what you want so you can punch it up yourself.

These run as a pipeline: **research → brief → `ad-creative-strategist` → `direct-response-copywriter`.** `competitor-research` (customer voice) and `scholarly-mechanism-research` (scientific proof) produce the evidence; the strategist picks formats and concepts; the copywriter writes the words. Each downstream skill starts from the prior output rather than re-deriving it. If copy/creative is requested for a new brand with no brief, offer research first; if the user says just go, go.

## When in doubt

Read `skills/competitor-research/SKILL.md` — it carries the full intake gate, phase-by-phase process, output structure, and quality bar. Follow it exactly; the Quality Standards checklist at the end is the bar the brief must clear before delivery.
