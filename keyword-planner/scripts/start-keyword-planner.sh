#!/bin/bash
# Start the Google Keyword Planner MCP server.
# Downloads the correct binary on first run, then launches it.
# Credentials are loaded from ~/.env (same source as the main Google Ads plugin).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${SCRIPT_DIR}/../bin"
VERSION="v0.1.0"
BINARY_NAME="kwp-mcp-go"

# Load credentials from ~/.env (matches the existing Google Ads plugin pattern)
if [ -f "$HOME/.env" ]; then
  export $(cat "$HOME/.env" | grep -v '^#' | grep '=' | xargs)
fi

# Detect OS and architecture
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$OS" in
  darwin) PLATFORM="darwin" ;;
  linux)  PLATFORM="linux" ;;
  mingw*|msys*|cygwin*) PLATFORM="windows" ;;
  *) echo "Unsupported OS: $OS" >&2; exit 1 ;;
esac

case "$ARCH" in
  x86_64|amd64)  GOARCH="amd64" ;;
  arm64|aarch64) GOARCH="arm64" ;;
  *) echo "Unsupported architecture: $ARCH" >&2; exit 1 ;;
esac

FILENAME="${BINARY_NAME}-${PLATFORM}-${GOARCH}"
if [ "$PLATFORM" = "windows" ]; then
  FILENAME="${FILENAME}.exe"
fi

BINARY_PATH="${BIN_DIR}/${FILENAME}"

# Download binary on first run
if [ ! -f "$BINARY_PATH" ]; then
  echo "Downloading Keyword Planner MCP server (${FILENAME})..." >&2
  mkdir -p "$BIN_DIR"
  DOWNLOAD_URL="https://github.com/ncosentino/google-keyword-planner-mcp/releases/download/${VERSION}/${FILENAME}"
  if command -v curl &>/dev/null; then
    curl -fsSL -o "$BINARY_PATH" "$DOWNLOAD_URL"
  elif command -v wget &>/dev/null; then
    wget -q -O "$BINARY_PATH" "$DOWNLOAD_URL"
  else
    echo "Error: curl or wget required to download binary" >&2
    exit 1
  fi
  chmod +x "$BINARY_PATH"
  echo "Downloaded to ${BINARY_PATH}" >&2
fi

exec "$BINARY_PATH"
