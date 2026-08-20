# Setup

Gets you from a fresh install to Claude reading and modifying Google Ads and Meta Ads data. About 20 minutes, most of it waiting on OAuth.

The `creative` plugin needs none of this — it runs on the built-in web tools. Skip straight to Step 5 if that's all you want.

---

## Prerequisites

- [ ] **Claude Code** installed and signed in
- [ ] **A Google Ads account** you have access to, plus a developer token (see below)
- [ ] **A Meta ad account** and a Business Manager system user, if you want the Meta plugin
- [ ] **Terminal** and admin access on your machine (to install `uv` and `ffmpeg`)

The Google Ads developer token is the one piece with a lead time — Google has to approve it. Apply early.

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

---

## Step 3 — Install `uv`

`keyword-planner` and `meta-ads` both use `uv` under the hood.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

### Also install `ffmpeg` (for video ad analysis)

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

All three MCP plugins read from a single `~/.env` in your home directory.

```bash
nano ~/.env
```

```bash
# Google Ads — used by keyword-planner AND google-ads
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_oauth_client_id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your_oauth_client_secret
GOOGLE_ADS_REFRESH_TOKEN=generated_by_the_oauth_flow_below
GOOGLE_ADS_CUSTOMER_ID=1234567890
# Only if the account sits under a manager account (MCC):
# GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890

# Meta Ads — used by meta-ads
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

**`GOOGLE_ADS_CLIENT_ID` / `GOOGLE_ADS_CLIENT_SECRET`** — Google Cloud Console → APIs & Services → Credentials → Create OAuth client ID → Desktop app. Enable the Google Ads API on the project first.

**`GOOGLE_ADS_REFRESH_TOKEN`** — generate it yourself:

```bash
uvx mcp-google-ads auth
```

Opens a browser, walks Google's OAuth flow, prints a refresh token. Paste it into `~/.env`.

**`GOOGLE_ADS_CUSTOMER_ID`** — the account you work in, digits only, no dashes. Find it top-right in the Google Ads UI.

**`GOOGLE_ADS_LOGIN_CUSTOMER_ID`** — only needed if the account sits under a manager account. Set it to the manager's ID; it's sent as the `login-customer-id` header on every call. Leave it unset for a standalone account — a manager header on an account that isn't under that manager causes `USER_PERMISSION_DENIED`.

**`ACCESS_TOKEN`** (Meta) — Business Manager → Business Settings → System Users → your system user → Generate New Token. Scopes: `ads_management`, `ads_read`, `business_management` at minimum. Meta shows the token once, so save it immediately.

**`AD_ACCOUNT_ID`** (Meta) — the default account used when no `ad_account_id` is passed. Format `act_XXXXXXXXXX`. Overridable per call, so pick the one you use most.

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

**"Authentication failed" on Google Ads**
- Refresh token expired or wrong → re-run `uvx mcp-google-ads auth`
- Developer token still at Test access → it can't query production accounts; apply for Basic
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID` set on a standalone account → unset it and retry

**`CUSTOMER_NOT_FOUND` or `USER_PERMISSION_DENIED` on a specific account**
Retry the same call *without* the manager header before assuming an access problem. Calls do fail when sent with a manager header the account isn't actually under.

**"ERROR: ACCESS_TOKEN is not set" on Meta startup**
- `~/.env` missing or missing the line — recheck Step 4
- Token expired — generate a new one

**"meta: command not found"**
```bash
uv tool install meta-ads
meta --version
```

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
