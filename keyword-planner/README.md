# Keyword Planner Plugin

Google Ads Keyword Planner integration for Claude. Companion to the `google-ads` plugin.

## Tools

| Tool | Description |
|------|-------------|
| `generate_keyword_ideas` | Generate keyword ideas from seed keywords and/or a URL. Returns search volume, competition level, and CPC estimates. |
| `get_historical_metrics` | Get historical search volume, competition, and bid data for a specific list of keywords. |
| `get_keyword_forecast` | Project impressions, clicks, and cost for keywords at a given max CPC bid. |

## Setup

This plugin uses the same Google Ads API credentials as the main `google-ads` plugin, loaded from `~/.env`.

### Required environment variables

```
GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token
GOOGLE_ADS_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your-client-secret
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token
GOOGLE_ADS_CUSTOMER_ID=your-account-id
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your-manager-account-id
```

### Billing requirement

The Keyword Planner API requires an account with billing configured. You don't need to run ads or spend money — just a payment method on file.

### API access level

Requires at least Basic access on your developer token (not test mode). If you're already running the Google Ads plugin, you should already have this.

### Scoping every call

All three tools take optional `customer_id` and `login_customer_id`, so a single call can
target any account under any manager account without touching `~/.env`. Unset, they fall back
to the env defaults above.

They also take `geo_targets` (`["CA"]`, `["2124"]`, or a full resource name) and `language`
(`"en"`, `"1000"`, or a full resource name). **Omitting `geo_targets` returns worldwide
volume**, which for a local advertiser overstates reality by an order of magnitude — the same
term reads 49,500/mo worldwide and 1,600/mo in Canada. Pass the market you actually advertise in.

## How it works

`scripts/start-keyword-planner.sh` loads `~/.env` and launches a Python MCP server through
`uv run`, which builds an isolated environment on first launch and reuses it afterwards. Same
pattern as the `google-ads` and `meta-ads` plugins. Requires [uv](https://docs.astral.sh/uv/).

The server calls the Google Ads API v23 directly. Through 1.0.0 it downloaded and wrapped a
prebuilt Go binary ([google-keyword-planner-mcp](https://github.com/ncosentino/google-keyword-planner-mcp)
by Nick Cosentino, MIT licensed). That was dropped in 2.0.0 because two of its three tools were
broken against v23:

- `get_keyword_forecast` returned HTTP 400. It posted `campaignForecastSpec`, which v23 does
  not define — the request field is `campaign`.
- `get_historical_metrics` silently returned zero results for every input, discarding a
  response the API had actually populated.

Dropping it also means nothing is downloaded at startup and no executable is written into the
plugin directory, which may be read-only depending on install layout.
