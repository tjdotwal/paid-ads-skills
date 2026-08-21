#!/bin/bash
# Load credentials from ~/.env and start the Google Ads MCP server.
#
# Required env vars (set in ~/.env):
#   GOOGLE_ADS_DEVELOPER_TOKEN   Developer token; needs Basic access for production accounts
#   GOOGLE_ADS_CLIENT_ID         OAuth 2.0 client ID (Desktop app type)
#   GOOGLE_ADS_CLIENT_SECRET     OAuth 2.0 client secret
#   GOOGLE_ADS_CREDENTIALS_PATH  Where the OAuth token file is read/written
# Optional:
#   GOOGLE_ADS_AUTH_TYPE         "oauth" (default) or "service_account"
#   GOOGLE_ADS_LOGIN_CUSTOMER_ID Manager account ID, only if the target sits under one

if [ -f "$HOME/.env" ]; then
  export $(cat "$HOME/.env" | grep -v '^#' | grep '=' | xargs)
fi

# Claude Code sets CLAUDE_PLUGIN_ROOT when it launches the plugin. Fall back to
# this script's plugin directory so the one-time manual OAuth launch below
# works when a person runs the script straight from a terminal.
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# Hard fail early on missing creds — better than a cryptic MCP error later.
for var in GOOGLE_ADS_DEVELOPER_TOKEN GOOGLE_ADS_CREDENTIALS_PATH; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set. Add it to ~/.env." >&2
    exit 3
  fi
done

# On first run with no cached token, the server opens a browser for OAuth
# consent. That needs a terminal, so complete it once by running this script
# directly before letting Claude Code launch the plugin. See SETUP.md Step 4.

# `uv run` installs deps into an isolated env on first launch, then reuses it.
exec uv run --directory "${PLUGIN_ROOT}" python -m mcp_google_ads
