#!/bin/bash
# Load credentials from ~/.env and start the Meta Ads MCP server.
#
# Required env vars (set in ~/.env or your shell):
#   ACCESS_TOKEN   - System user access token from Meta Business Manager
#   AD_ACCOUNT_ID     - Default ad account id (format: act_XXXXXXXXX)
# Optional:
#   META_API_VERSION    - e.g. v25.0 (passed through to the CLI)
#   BUSINESS_ID    - Default business id for catalog/dataset ops

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

# Hard fail early if creds are missing — better than a cryptic MCP error later.
if [ -z "$ACCESS_TOKEN" ]; then
  echo "ERROR: ACCESS_TOKEN is not set. Add it to ~/.env." >&2
  exit 3
fi

# Run the MCP server from the plugin folder via uv. `uv run` installs deps
# into an isolated env on first launch, then reuses it.
exec uv run --directory "${CLAUDE_PLUGIN_ROOT}" python -m mcp_meta_ads
