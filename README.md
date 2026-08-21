# paid-ads-skills

A Claude Code plugin marketplace for running paid advertising: Google Ads and Meta Ads MCP servers, plus the skills that encode how to use them — search-term mining, keyword research, campaign builds, creative analysis, market research, and direct-response copywriting.

Built for a single operator running paid media for one brand at a time.

## Install

Add the marketplace, then install the plugins you need:

```
/plugin marketplace add tjdotwal/paid-ads-skills
/plugin install google-ads@paid-ads
/plugin install meta-ads@paid-ads
/plugin install keyword-planner@paid-ads
/plugin install creative@paid-ads
/plugin install reporting@paid-ads
```

`google-ads`, `meta-ads`, and `keyword-planner` need API credentials. `creative` needs none. `reporting` needs no credentials of its own but calls the two ad plugins, plus a local `config/budget.md`. See **[SETUP.md](./SETUP.md)** for credentials, `uv`, and the OAuth flow.

## Plugins

### `google-ads`

MCP server over the Google Ads API, in-repo under `google-ads/mcp_google_ads/` — GAQL queries, campaign and keyword performance, and mutations (negatives, keywords, budgets, campaign status). 22 tools.

| Skill | What it does |
|---|---|
| `naming-conventions` | How to read campaign and ad group names so campaign intent is interpreted consistently. Load before any analysis |
| `search-term-methodology` | How to evaluate search terms for relevance, negation candidacy, and keyword opportunity. Also covers performance pulse-check diagnosis |
| `mine-search-terms` | The mining run itself — pull the report, evaluate, produce a negation list and an opportunity list |
| `google-ads-campaign-build` | Build or restructure search campaigns: architecture, ad groups, keywords, RSAs, budgets, and a go-live QA pass |

Command: `/mine-search-terms`

### `meta-ads`

MCP server wrapping Meta's official `meta ads` CLI. Local tokens, no third-party auth proxy. Reads campaigns, ad sets, ads, creatives, and insights; writes campaign, ad set, and ad changes.

The creative fetch tools are the useful part: `ad_image_get` returns full-resolution images, and `ad_video_get` returns a timestamped transcript of the spoken script (plus optional keyframes) so video ads can be analyzed on what they actually say rather than on a thumbnail.

| Skill | What it does |
|---|---|
| `meta-account-audit` | Five-step structural audit of an account, run in a fixed sequence before changing settings |
| `meta-creative-analysis` | Cohort-level performance attribution — why some creatives outperform, ending in next-test theses |

### `keyword-planner`

MCP server over the Google Ads Keyword Planner API: keyword ideas, historical search volume, and forecasts. Shares the developer token and OAuth client with `google-ads`, but authenticates with a refresh token rather than a token file — the two are separate implementations. Requires an account with billing configured.

| Skill | What it does |
|---|---|
| `keyword-research` | Keyword discovery and volume validation, mapped to funnel stages and ad group themes |

### `creative`

Skills only, no MCP server. The research and creative layer that runs before copy gets written.

| Skill | What it does |
|---|---|
| `competitor-research` | Market and competitor research → a structured brief: landscape, ranked pain points with verbatim customer quotes, competitor vulnerabilities, switching objections, campaign angles |
| `scholarly-mechanism-research` | Source-verified research from Scholar/PubMed so claims cite real peer-reviewed evidence |
| `creative-format-library` | 52-template format taxonomy across 7 sections, with full specs for the 10 formats that carry real methodology, plus the JSON prompt architecture for image generation |
| `ad-creative-strategist` | Ad concepts and design briefs against the format library; also reverse-engineers an existing ad from a screenshot |
| `direct-response-copywriter` | DR copy — ads, headlines, image and body copy, VSL scripts, landing pages, emails. Pulls its diagnostic from the research brief when one exists |
| `no-ai-slop` | Edits drafts against four principles (simplicity, brevity, clarity, humanity) and a pattern list, or audits a draft without rewriting |

Commands: `/log-win`, `/pull-winners`, `/distill-swipe` — maintain an annotated swipe file of winning ads. `/pull-winners` reads both ad platforms over a date window and drafts diagnosed entries for approval.

### `reporting`

Skills only. Cross-channel pacing and performance review, orchestrating the two ad plugins. Needs `config/budget.md` for monthly intent — the one number no API can supply. Everything else is pulled live.

| Skill | What it does |
|---|---|
| `budget-pacing-manager` | Is spend on schedule, and should budget move? Day-aware tolerance band, trailing-14-day reallocation logic, Google impression-share and Meta frequency supply diagnostics, budget-conserving recommendations |
| `advertising-performance-manager` | Is that spend producing leads at the right cost? 3-month day-matched baselines, 🔴/🟢/🟡/🆕 buckets, and a symptom-to-cause table separating auction pressure from creative fatigue from broken tracking |

## How it fits together

The skills are designed to chain. Research produces evidence, strategy picks formats, copy executes:

```
competitor-research ─┐
                     ├─→ ad-creative-strategist ─→ direct-response-copywriter ─→ no-ai-slop
scholarly-research ──┘         ↑
                     creative-format-library
```

On the account side, analysis feeds the build:

```
keyword-research ─→ google-ads-campaign-build ─→ mine-search-terms ─→ (negatives + new keywords)
                            ↑
                    naming-conventions
```

`meta-creative-analysis` closes the loop back to `ad-creative-strategist` — the analysis ends with next-test theses the strategist picks up.

The reporting pair runs on its own cadence over both channels:

```
budget-pacing-manager ──→ is spend on schedule, and where should it go?
advertising-performance-manager ──→ did that spend produce leads at the right cost?
```

Run pacing first — moving budget toward a campaign that's quietly broken is worse than leaving it alone.

## Repo layout

```
paid-ads-skills/
├── .claude-plugin/
│   └── marketplace.json      Marketplace manifest
├── SETUP.md                  Credentials, uv, OAuth, smoke tests
├── google-ads/               MCP server (Python) + 4 skills
├── meta-ads/                 MCP server (Python) + 2 skills
├── keyword-planner/          MCP server (Go binary) + 1 skill
├── creative/                 6 skills, no MCP server
└── reporting/                2 skills, no MCP server
```

Each plugin has a `CLAUDE.md` defining its operating posture and guardrails, and a `README.md` covering its own setup.

## Editing a skill

Skills are markdown. Open the `SKILL.md`, edit, and restart Claude Code (or start a new session) to reload. The frontmatter `description` is what determines when the skill triggers, so changes there matter more than changes to the body.

Bump the version in the plugin's `.claude-plugin/plugin.json` when a change is worth tracking.

## License

MIT — see [LICENSE](./LICENSE).

Three components are third-party and carry their own MIT licenses:

- **`creative/skills/no-ai-slop`** — by [Peter Yang](https://github.com/petergyang), vendored with its license at `creative/skills/no-ai-slop/LICENSE`.
- **`google-ads/mcp_google_ads/server.py`** — vendored from [mcp-google-ads](https://github.com/cohnen/mcp-google-ads) by Ernesto Cohnen / ixigo, with the write tools added. Attribution, license, and local changes in `google-ads/NOTICE`.
- **The Keyword Planner MCP binary** — [google-keyword-planner-mcp](https://github.com/ncosentino/google-keyword-planner-mcp) by Nick Cosentino. Not vendored; `keyword-planner/scripts/start-keyword-planner.sh` downloads the release binary for your platform on first run.
