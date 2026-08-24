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

# Parsed line by line rather than word-split through xargs, so values containing
# spaces, quotes, or '=' survive verbatim. The file is never sourced, so a stray
# line cannot execute shell or abort startup under `set -e`.
if [ -f "$HOME/.env" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%$'\r'}"                       # tolerate CRLF files
    case "$line" in ''|'#'*) continue ;; esac
    case "$line" in *=*) ;; *) continue ;; esac

    key="${line%%=*}"
    value="${line#*=}"

    key="${key#"${key%%[![:space:]]*}"}"        # trim leading whitespace
    key="${key#export }"
    key="${key%"${key##*[![:space:]]}"}"        # trim trailing whitespace
    case "$key" in ''|[0-9]*|*[!A-Za-z0-9_]*) continue ;; esac

    value="${value%"${value##*[![:space:]]}"}"  # trim trailing whitespace
    case "$value" in                            # strip one layer of quotes
      \"*\") value="${value#\"}"; value="${value%\"}" ;;
      \'*\') value="${value#\'}"; value="${value%\'}" ;;
    esac

    export "$key=$value"
  done < "$HOME/.env"
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
