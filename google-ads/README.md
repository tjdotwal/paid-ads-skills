# Google Ads Toolkit

A Claude Code plugin for managing Google Ads across a brand's account. Connects to the Google Ads API via MCP, encodes paid search workflows as skills, and supports both analysis delivery (CSV output) and direct account mutations with explicit approval.

## Components

### MCP Connector — Google Ads
Connects to the Google Ads API via `mcp-google-ads`. Pointed at your account, or at a manager account for access to everything under it. Exposes GAQL query execution, campaign performance data, and account mutations (adding negative keywords, adjusting budgets, etc.).

### Skills

| Skill | Purpose |
|-------|---------|
| `naming-conventions` | Teaches Claude how to parse the campaign naming taxonomy so it understands what each campaign is selling, to whom, and at what funnel stage |
| `search-term-methodology` | The relevance evaluation framework for deciding whether a search term should be negated, kept, or flagged for review |
| `mine-search-terms` | Execution skill — pulls search term data via GAQL, evaluates every term using the two skills above, produces a bulk-upload CSV, and optionally pushes negatives directly |

### Commands

| Command | Description |
|---------|-------------|
| `/mine-search-terms [brand]` | Launch search term mining for a ad account |

## Setup

### Required Environment Variables

Set these in your system environment or Claude's MCP configuration before using the plugin:

| Variable | Description |
|----------|-------------|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads developer token. Needs Basic access to query production accounts |
| `GOOGLE_ADS_CLIENT_ID` | OAuth 2.0 client ID from Google Cloud Console (Desktop app type) |
| `GOOGLE_ADS_CLIENT_SECRET` | OAuth 2.0 client secret |
| `GOOGLE_ADS_CREDENTIALS_PATH` | Path where the server reads and writes its OAuth token file. Required even before the file exists |
| `GOOGLE_ADS_AUTH_TYPE` | `oauth` (default) or `service_account`. Optional |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Manager account ID, digits only. Only set this if the target account sits under a manager |

This server does **not** read a refresh token from the environment — that's the `keyword-planner` plugin's auth model. This one runs the OAuth installed-app flow itself on first launch and caches the result at `GOOGLE_ADS_CREDENTIALS_PATH`. Run it once from a terminal so the browser consent can complete before Claude Code launches it; see Step 4 in [SETUP.md](../SETUP.md).

### Installing the MCP Server

The plugin uses `mcp-google-ads` via `uvx`. Install `uv` if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then verify:

```bash
uvx mcp-google-ads --help
```

### Generating a Refresh Token

If you don't have a refresh token yet, run the OAuth flow:

```bash
uvx mcp-google-ads auth
```

Follow the prompts to authorize access to your Google Ads MCC account.

## Usage

### Mine Search Terms

**Via command:** Type `/mine-search-terms` in any Claude Code session (optionally followed by a brand name hint, e.g. `/mine-search-terms Acme Scheduling`).

**Via chat:** Say "mine search terms for [brand]" or "find negative keywords for [campaign]".

The workflow will:
1. List all ad accounts in your MCC — you select which one
2. Pull last 30 days of unactioned search terms, sorted by spend
3. Evaluate every term against the campaign theme and funnel stage
4. Produce a CSV file (`search-term-negatives-YYYY-MM-DD.csv`) with a reasoning column on every row
5. Offer to push approved negatives to campaign-level negative keyword lists, campaign by campaign, with explicit confirmation at each step

## Roadmap

Skills planned for future versions:
- `budget-optimize` — impression share analysis + budget recommendations
- `audit-ad-copy` — RSA performance audit and copy recommendations
- `weekly-review` — automated weekly performance summary across all clients
- `performance-analysis` — deep-dive campaign and ad group analysis
