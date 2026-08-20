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

## How it works

On first run, the start script auto-detects your OS and architecture, downloads the correct binary from GitHub, and launches it. Subsequent runs use the cached binary.

The binary is [google-keyword-planner-mcp](https://github.com/ncosentino/google-keyword-planner-mcp) by Nick Cosentino (MIT licensed). Source code reviewed and approved.
