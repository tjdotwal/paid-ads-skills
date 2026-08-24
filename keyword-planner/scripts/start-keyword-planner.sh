#!/bin/bash
# Load credentials from ~/.env and start the Keyword Planner MCP server.
#
# Required env vars (set in ~/.env):
#   GOOGLE_ADS_DEVELOPER_TOKEN   Developer token; needs Basic access for production accounts
#   GOOGLE_ADS_CLIENT_ID         OAuth 2.0 client ID (Desktop app type)
#   GOOGLE_ADS_CLIENT_SECRET     OAuth 2.0 client secret
#   GOOGLE_ADS_REFRESH_TOKEN     Refresh token for the above client
# Optional:
#   GOOGLE_ADS_CUSTOMER_ID       Default account; every tool can override per call
#   GOOGLE_ADS_LOGIN_CUSTOMER_ID Manager account ID, only if the target sits under one
#   GOOGLE_ADS_CREDENTIALS_PATH  Authorized-user token file, used when no refresh token is set
#   GOOGLE_ADS_AUTH_TYPE         "oauth" (default) or "service_account"

set -euo pipefail

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
# this script's plugin directory so the server also runs straight from a shell.
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# Hard fail early on missing creds — better than a cryptic MCP error later.
if [ -z "${GOOGLE_ADS_DEVELOPER_TOKEN:-}" ]; then
  echo "ERROR: GOOGLE_ADS_DEVELOPER_TOKEN is not set. Add it to ~/.env." >&2
  exit 3
fi

if [ -z "${GOOGLE_ADS_REFRESH_TOKEN:-}" ] && [ -z "${GOOGLE_ADS_CREDENTIALS_PATH:-}" ]; then
  echo "ERROR: set GOOGLE_ADS_REFRESH_TOKEN (with GOOGLE_ADS_CLIENT_ID and" >&2
  echo "GOOGLE_ADS_CLIENT_SECRET) or GOOGLE_ADS_CREDENTIALS_PATH in ~/.env." >&2
  exit 3
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is not installed. See SETUP.md, or: brew install uv" >&2
  exit 3
fi

# `uv run` installs deps into an isolated env on first launch, then reuses it.
exec uv run --directory "${PLUGIN_ROOT}" python -m mcp_keyword_planner
