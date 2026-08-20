#!/bin/bash
# Load credentials from ~/.env and start the Meta Ads MCP server.
#
# Required env vars (set in ~/.env or your shell):
#   ACCESS_TOKEN   - System user access token from Meta Business Manager
#   AD_ACCOUNT_ID     - Default ad account id (format: act_XXXXXXXXX)
# Optional:
#   META_API_VERSION    - e.g. v25.0 (passed through to the CLI)
#   BUSINESS_ID    - Default business id for catalog/dataset ops

if [ -f "$HOME/.env" ]; then
  export $(cat "$HOME/.env" | grep -v '^#' | grep '=' | xargs)
fi

# Hard fail early if creds are missing — better than a cryptic MCP error later.
if [ -z "$ACCESS_TOKEN" ]; then
  echo "ERROR: ACCESS_TOKEN is not set. Add it to ~/.env." >&2
  exit 3
fi

# Run the MCP server from the plugin folder via uv. `uv run` installs deps
# into an isolated env on first launch, then reuses it.
exec uv run --directory "${CLAUDE_PLUGIN_ROOT}" python -m mcp_meta_ads
