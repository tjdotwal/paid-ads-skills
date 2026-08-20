#!/bin/bash
# Load credentials from ~/.env and start the Google Ads MCP server
# from the patched fork at github.com/tjdotwal/mcp-google-ads, pinned
# to v2.1.0 (adds multi-MCC-aware WRITE tools — negatives, keywords,
# status, budgets, campaigns — each accepting a per-call login_customer_id).
if [ -f "$HOME/.env" ]; then
  export $(cat "$HOME/.env" | grep -v '^#' | grep '=' | xargs)
fi

# The fork declares `mcp[cli]>=1.3.0` with no upper bound, so uvx resolves to
# mcp 2.0.0, which dropped the vendored `mcp.server.fastmcp` module the server
# imports. Hold mcp on the 1.x line until the fork migrates off it.
exec uvx --from "git+https://github.com/tjdotwal/mcp-google-ads@v2.1.0" \
  --with "mcp[cli]<2" \
  mcp-google-ads
