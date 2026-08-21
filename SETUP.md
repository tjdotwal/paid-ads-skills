# Setup

Gets you from a fresh install to Claude reading and modifying Google Ads and Meta Ads data. About 20 minutes, most of it waiting on OAuth.

The `creative` plugin needs none of this — it runs on the built-in web tools. Skip straight to Step 5 if that's all you want.

---

## Prerequisites

- [ ] **Claude Code** installed and signed in
- [ ] **A Google Ads account** you have access to, plus a developer token (see below)
- [ ] **A Meta ad account** and a Business Manager system user, if you want the Meta plugin
- [ ] **Terminal** and admin access on your machine (to install `uv` and `ffmpeg`)

The Google Ads developer token is the one piece with a lead time — Google has to approve it, and a fresh token starts at Test access which can't query real accounts. Apply early.

---

## Step 1 — Add the marketplace

```
/plugin marketplace add tjdotwal/paid-ads-skills
```

---

## Step 2 — Install the plugins

```
/plugin install google-ads@paid-ads
/plugin install meta-ads@paid-ads
/plugin install keyword-planner@paid-ads
/plugin install creative@paid-ads
```

Install only what you need; you can add the rest later. The Meta plugin's first launch takes 30–60 seconds because `uv` is building an isolated Python environment. That's normal.

### What the servers actually are

Worth knowing, because it explains the commands further down:

| Plugin | Server | Where it comes from |
|---|---|---|
| `google-ads` | `mcp-google-ads` | Fetched by `uvx` from [`tjdotwal/mcp-google-ads`](https://github.com/tjdotwal/mcp-google-ads), pinned to `v2.1.0`. A public fork of the upstream project that adds the write tools — negatives, keywords, budgets, campaign status — each accepting a per-call `login_customer_id`. `mcp[cli]` is held below 2.0 because the server imports the vendored `mcp.server.fastmcp` module that 2.0 dropped. |
| `meta-ads` | `mcp_meta_ads` | In this repo, under `meta-ads/`. A FastMCP server that wraps Meta's official `meta` CLI. |
| `keyword-planner` | `kwp-mcp-go` | Downloaded on first run from [`ncosentino/google-keyword-planner-mcp`](https://github.com/ncosentino/google-keyword-planner-mcp) releases, matched to your OS and architecture, then cached in `keyword-planner/bin/`. |

Nothing is vendored as a prebuilt binary in the repo — the Go binary is fetched at runtime and gitignored.

---

## Step 3 — Install the command-line dependencies

### `uv` (required by `keyword-planner` and `meta-ads`)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

### The `meta` CLI (required by `meta-ads`)

The Meta plugin doesn't call the Graph API directly for most operations — it shells out to Meta's official `meta` CLI. Without it, **every** Meta tool fails, not just video analysis.

```bash
uv tool install meta-ads
meta --version
```

> **PATH gotcha.** `uv tool install` puts the binary in `~/.local/bin`, and the plugin resolves `meta` with a plain PATH lookup — no fallback to `~/.local/bin` or the Homebrew prefixes. Since the server is launched by Claude Code rather than your shell, `~/.local/bin` has to be on the PATH Claude Code inherits. If `meta --version` works in your terminal but the plugin reports `The meta CLI is not on PATH`, that's this. Add `export PATH="$HOME/.local/bin:$PATH"` to your shell profile, then fully quit and reopen Claude Code.

Authentication is environment-only — there is no `meta auth login`. The CLI reads `ACCESS_TOKEN`, `AD_ACCOUNT_ID`, and `BUSINESS_ID` straight from the environment, which the start script exports from `~/.env`. Once Step 4 is done, verify with:

```bash
meta auth status
```

Expect `Authenticated (token: EAA…)`.

### `ffmpeg` (optional — for video ad analysis)

The Meta plugin can transcribe video ads and pull keyframes so Claude can read and see a video creative rather than guessing from a thumbnail. That one feature needs `ffmpeg`. Everything else works without it, so if this step gives you trouble, keep going and come back.

```bash
brew install ffmpeg
ffmpeg -version
```

No Homebrew? Install it from [brew.sh](https://brew.sh) first.

> **If Claude Code was already running when you installed `ffmpeg`, restart it.** The plugin is launched by Claude Code, not your shell, so it only picks up the new PATH on a fresh start.

The transcription model downloads itself on first use — about 500 MB, one time, so the first video takes roughly a minute. Nothing is written to disk when a video is analyzed; the audio is read over the network and transcribed in memory.

> **Older Intel Mac?** Everything works including keyframe extraction. The one piece that can't run locally is transcribing the spoken script — Claude says so plainly instead of failing. Apple silicon needs macOS 14 or newer for it.

---

## Step 4 — Credentials in `~/.env`

All three MCP plugins read from a single `~/.env` in your home directory, but **they do not read the same variables.** The two Google Ads servers authenticate differently:

- **`keyword-planner`** (Go) uses a **refresh token** in the environment.
- **`google-ads`** (Python) uses a **token file on disk** at `GOOGLE_ADS_CREDENTIALS_PATH`, and runs the OAuth flow itself to create it. It never reads a refresh token from the environment.

Both sets can live in the same file.

```bash
nano ~/.env
```

```bash
# ---- Shared by both Google Ads plugins ----
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_oauth_client_id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your_oauth_client_secret
# Only if the target account sits under a manager account (MCC):
# GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890

# ---- keyword-planner only ----
GOOGLE_ADS_REFRESH_TOKEN=from_the_one_time_flow_below
GOOGLE_ADS_CUSTOMER_ID=1234567890

# ---- google-ads only ----
GOOGLE_ADS_AUTH_TYPE=oauth
GOOGLE_ADS_CREDENTIALS_PATH=/Users/you/.config/google-ads/token.json

# ---- meta-ads ----
ACCESS_TOKEN=your_meta_system_user_token_starts_with_EAA
AD_ACCOUNT_ID=act_1234567890
# Optional:
# META_API_VERSION=v25.0
# BUSINESS_ID=1234567890
```

Save with **Ctrl+O**, Enter, **Ctrl+X**. Then lock it down:

```bash
chmod 600 ~/.env
```

### Where each credential comes from

**`GOOGLE_ADS_DEVELOPER_TOKEN`** — Google Ads UI → Tools → API Center. A new token starts at Test access, which only reads test accounts; apply for Basic access to query real ones. This is the approval step with a lead time.

**`GOOGLE_ADS_CLIENT_ID` / `GOOGLE_ADS_CLIENT_SECRET`** — Google Cloud Console → APIs & Services → Credentials → Create OAuth client ID → **Desktop app**. Enable the Google Ads API on the project first. Complete the OAuth flow as the Google account that actually has access to the ad account.

**`GOOGLE_ADS_LOGIN_CUSTOMER_ID`** — only if the target account sits under a manager account. Set it to the manager's ID; it's sent as the `login-customer-id` header. Leave it unset for a standalone account — a manager header on an account that isn't under that manager causes `USER_PERMISSION_DENIED`.

**`GOOGLE_ADS_CUSTOMER_ID`** (keyword-planner) — the account with billing, from the top-right of the Google Ads UI. Dashes optional. Keyword Planner requires a payment method on file, though you don't have to spend anything.

**`GOOGLE_ADS_REFRESH_TOKEN`** (keyword-planner) — one-time flow. Fill in your client ID and secret, then run the whole block; it opens a browser, catches the redirect on a temporary local listener, and prints the token:

```bash
CLIENT_ID="YOUR_CLIENT_ID"
CLIENT_SECRET="YOUR_CLIENT_SECRET"
REDIRECT_URI="http://localhost:9876"

open "https://accounts.google.com/o/oauth2/v2/auth?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fadwords&access_type=offline&prompt=consent"

CODE=$(python3 -c "
import http.server, urllib.parse, sys
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        print(params['code'][0], end='')
        self.send_response(200); self.end_headers()
        self.wfile.write(b'Auth complete! Close this tab.')
        sys.exit(0)
    def log_message(self, *a): pass
http.server.HTTPServer(('', 9876), H).handle_request()
")

curl -s -X POST https://oauth2.googleapis.com/token \
  -d "client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}&code=${CODE}&grant_type=authorization_code&redirect_uri=${REDIRECT_URI}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['refresh_token'])"
```

Google returns a refresh token only once per consent grant, so save it immediately.

**`GOOGLE_ADS_CREDENTIALS_PATH`** (google-ads) — a path where the server will read and write its OAuth token file. It doesn't have to exist yet; the directory does:

```bash
mkdir -p ~/.config/google-ads
```

On first launch, if there's no valid token at that path, the server builds an OAuth client config from `GOOGLE_ADS_CLIENT_ID` / `GOOGLE_ADS_CLIENT_SECRET`, runs the installed-app flow, and saves the result.

> **Do this once from a terminal, not from Claude Code.** The flow needs to open a browser and bind a local port, which is unreliable from a server subprocess that has no terminal attached. Run it manually first so the token file exists before Claude Code ever launches the plugin:
>
> ```bash
> set -a; source ~/.env; set +a
> uvx --from "git+https://github.com/tjdotwal/mcp-google-ads@v2.1.0" --with "mcp[cli]<2" mcp-google-ads
> ```
>
> Complete the browser consent, confirm the token file was written, then Ctrl+C. After that the plugin starts clean.

`GOOGLE_ADS_AUTH_TYPE` defaults to `oauth`, so setting it is optional. Set it to `service_account` instead if you'd rather point `GOOGLE_ADS_CREDENTIALS_PATH` at a service account key — that path also uses `GOOGLE_ADS_IMPERSONATION_EMAIL`.

**`ACCESS_TOKEN`** (meta-ads) — Business Manager → Business Settings → System Users → your system user → Generate New Token. Scopes: `ads_management`, `ads_read`, `business_management` at minimum. Meta shows the token once, so save it immediately.

**`AD_ACCOUNT_ID`** (meta-ads) — the default account used when no `ad_account_id` is passed. Format `act_XXXXXXXXXX`. Overridable per call, so pick the one you use most.

---

## Step 5 — Smoke test

New session, one at a time:

**keyword-planner** → *"Generate keyword ideas for 'commercial roofing calgary'"*
Expect keywords with monthly volume, competition, and CPC estimates.

**google-ads** → *"List my Google Ads accounts"*
Expect numeric customer IDs. Names aren't returned — that's an API limitation, not a bug.

**meta-ads** → *"List my Meta ad accounts"*
Expect the accounts your token can reach.

**creative** → *"What creative format is a journal-screenshot ad?"*
Expect it to load `creative-format-library` and identify template 45.

**Video analysis** (only if you installed `ffmpeg`) → *"Analyze the video creative for ad <AD_ID> in account act_<ACCOUNT_ID>"*
Expect a timestamped transcript. First run takes about a minute while the model downloads.

---

## Troubleshooting

**"Authentication failed" on Google Ads** — check which plugin first, they fail differently:
- `keyword-planner` → refresh token expired or revoked. Re-run the one-time refresh-token flow in Step 4.
- `google-ads` → the token file at `GOOGLE_ADS_CREDENTIALS_PATH` is missing, stale, or was never created. Delete it and re-run the manual launch from Step 4 to redo consent.
- Either → developer token still at Test access. It can't query production accounts; apply for Basic.
- Either → `GOOGLE_ADS_LOGIN_CUSTOMER_ID` set on a standalone account. Unset it and retry.

**`GOOGLE_ADS_CREDENTIALS_PATH environment variable not set`**
The `google-ads` server requires it even when the token file doesn't exist yet. Add it to `~/.env` and `mkdir -p` its parent directory.

**`google-ads` hangs on startup with no error**
It's almost certainly blocked on the OAuth consent flow, waiting for a browser that never opened. Kill it and run the manual launch from Step 4 in a terminal to complete consent once.

**`CUSTOMER_NOT_FOUND` or `USER_PERMISSION_DENIED` on a specific account**
Retry the same call *without* the manager header before assuming an access problem. Calls do fail when sent with a manager header the account isn't actually under.

**"ERROR: ACCESS_TOKEN is not set" on Meta startup**
- `~/.env` missing or missing the line — recheck Step 4
- Token expired — generate a new one

**Meta tools fail with an auth error even though `ACCESS_TOKEN` is set**
Check what the CLI itself sees: `meta auth status`. If that reports authenticated but the plugin still fails, the token is valid but lacks a scope for the operation — regenerate it with `ads_management`, `ads_read`, and `business_management`.

**`The meta CLI is not on PATH` from a Meta tool**
Two different causes:
- Not installed → `uv tool install meta-ads`
- Installed but invisible to the plugin → `~/.local/bin` isn't on the PATH Claude Code inherits. The plugin resolves `meta` with a plain PATH lookup and has no `~/.local/bin` fallback, so `meta --version` working in your terminal proves nothing. Add `export PATH="$HOME/.local/bin:$PATH"` to your shell profile, then fully quit and reopen Claude Code.

**No `mcp__*` tools available**
Restart Claude Code. If they're still missing, check `/plugin` for an error on the plugin.

**Meta plugin hangs on first launch**
Normal for up to 60 seconds while `uv` installs dependencies. Past two minutes, confirm `uv --version` works and restart.

**"ffmpeg was not found on PATH"**
`brew install ffmpeg`, then restart Claude Code. If `ffmpeg -version` already works in your terminal, it's a PATH inheritance problem and the restart is the fix — the plugin inherits PATH from Claude Code, not your shell.

**Video analysis fails with "Could not get a readable source URL"**
Meta gates video source behind a Page access token for page-owned videos; a system user token isn't always enough. Not blocking — Claude falls back to diagnosing from thumbnail and copy, flagged `(creative unverified — copy-layer diagnosis only)` so you know the video wasn't reviewed.

**Creative images come back as 64×64 thumbnails**
The ad account ID wasn't passed, so the account-scoped asset lookup fell back to a thumbnail. Name the account: *"…for account act_XXXXXXXXXX"*.

**"Permission denied" reading `~/.env`**
```bash
chmod 600 ~/.env
```

---

## Using it

Talk normally; the skills trigger off their descriptions:

- "Mine search terms for the last 30 days"
- "Pull the last 30 days of Meta performance"
- "What keywords should we target for a roofing company in Edmonton?"
- "Audit the negative keywords on the scheduling-software campaign"
- "Analyze the creative performance in this account"
- "Write image copy for a myth-buster ad"

If a skill you expected doesn't load, be more specific — "mine search terms" rather than "look at search terms." Skill descriptions are matched on intent, so naming the job helps.

---

## Not covered here

- **Writing your own skills** — see each plugin's `README.md` and `CLAUDE.md` for the patterns used here.
- **The naming taxonomy** — loaded automatically during account work. To read it: `google-ads/skills/naming-conventions/SKILL.md`.
