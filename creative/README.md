# creative

Claude plugin housing the **research and creative** skills — the layer that runs *before* copy gets written. Channel-agnostic: the briefs it produces feed Meta Ads, Google Ads, landing pages, and copywriting work alike.

Unlike `google-ads` and `meta-ads`, this plugin has **no MCP server** — it's skills-only. It relies on the built-in `WebSearch` / `WebFetch` tools, with an optional accelerator (see below).

## How it's wired

```
creative/
├── .claude-plugin/plugin.json          Plugin metadata (loaded by Claude)
├── skills/
│   ├── competitor-research/SKILL.md         Deep competitor + market research → structured brief
│   ├── scholarly-mechanism-research/SKILL.md  Source-verified scientific proof for ad claims
│   ├── ad-creative-strategist/SKILL.md      Creative concepts + design briefs (52 formats)
│   └── direct-response-copywriter/SKILL.md  Turns the brief into high-converting DR copy
├── CLAUDE.md                           Agent-facing guidance loaded when the plugin is active
└── README.md                           (you are here)
```

## Skills

- **competitor-research** — Turns a brand URL + target audience + named competitors into a structured, evidence-backed research brief (market landscape, ranked pain points with verbatim quotes, competitor vulnerabilities + pricing table, switching objections, desired benefits, campaign angles + big idea). This is the FIRST step before writing any copy for a new brand or campaign angle.
- **scholarly-mechanism-research** — Runs deep, source-verified scientific research (Google Scholar, PubMed, journals) on a brand's problem and mechanism so ad claims can cite real peer-reviewed evidence. The *proof* layer that pairs with `competitor-research` (customer voice) and `ad-creative-strategist` (formats) — e.g. for medical-paper / research-screenshot creatives.
- **ad-creative-strategist** — Generates static/slideshow/short-form video ad concepts and design-team-ready creative briefs across 52 formats; also reverse-engineers existing ads. Handles *visual format strategy*; hands copy decisions to `direct-response-copywriter` and can pull the canonical taxonomy from `meta-ads:creative-format-library`.
- **direct-response-copywriter** — Writes high-converting DR copy (ads, headlines, image/body copy, VSL scripts, landing pages, emails). Runs AFTER `competitor-research` and pulls its diagnostic — customer pains, mechanism, big idea, verbatim quote ammunition — straight from that brief when one exists.

The skills compose as a pipeline: **research → creative strategy → copy.** `competitor-research` (customer voice) and `scholarly-mechanism-research` (scientific proof) produce the evidence; `ad-creative-strategist` chooses the formats and concepts; `direct-response-copywriter` writes the words. Verbatim customer quotes and cited evidence flow through all of them.

## Optional accelerator: Agent-Reach

The `competitor-research` skill works fully with the built-in web tools. If [Agent-Reach](https://github.com/Panniantong/Agent-Reach) happens to be installed, the skill will use it for raw social/forum pulls (Reddit comments, Twitter/X, YouTube transcripts) because it returns raw lived-experience text instead of search snippets.

It is **not required and not a team dependency.** The skill checks `agent-reach doctor` once and silently falls back to `WebSearch` / `WebFetch` + Reddit Answers if it's missing or unhealthy. To try it:

```bash
# Optional — only if you want richer raw-source pulls
# See https://github.com/Panniantong/Agent-Reach for install
agent-reach doctor   # shows which platforms are working
```

Read-only research use only — not for LinkedIn scraping, and kept entirely separate from the authenticated ad-account plugins.

## Editing a skill

1. Open `skills/competitor-research/SKILL.md`
2. Make changes, save
3. Restart Claude Code (or start a new session)
4. Bump `version` in the SKILL.md frontmatter and `plugin.json` if you want a new release
5. Commit and push — the marketplace auto-syncs from `main`
