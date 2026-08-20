# meta-ads

Claude plugin that lets an operator manage Meta Ads (Facebook + Instagram) campaigns from inside Claude. Wraps Meta's official `meta ads` CLI in a local MCP server — no third-party auth proxy, no tokens leaving the operator's machine.

Mirrors the structure of `google-ads`.

## How it's wired

```
meta-ads/
├── .claude-plugin/plugin.json    Plugin metadata (loaded by Claude)
├── .mcp.json                     Tells Claude how to launch the MCP server
├── scripts/start-server.sh       Loads ~/.env, then runs the Python MCP server via `uv`
├── pyproject.toml                Python package definition for the wrapper
├── mcp_meta_ads/       The MCP server itself
│   ├── __main__.py               Entrypoint (`python -m mcp_meta_ads`)
│   ├── server.py                 FastMCP server + tool definitions
│   └── cli.py                    Thin subprocess wrapper around the `meta` CLI
├── commands/                     Slash commands (empty in v0.1.0)
├── skills/                       Account audit + creative analysis skills
├── CLAUDE.md                     Agent-facing guidance loaded when the plugin is active
└── README.md                     (you are here)
```

## Prerequisites

1. **Meta Ads CLI installed** on the operator's machine. Python 3.12+ required.
   ```bash
   uv tool install meta-ads
   # or: pip install meta-ads
   ```
   Verify with `meta --version`.

2. **Meta system user access token** with the right business scope. Generate it from Meta Business Manager under Business Settings → System Users.

3. **`~/.env` file** with at minimum:
   ```bash
   ACCESS_TOKEN=EAAB...
   AD_ACCOUNT_ID=act_123456789012345
   # Optional:
   # META_API_VERSION=v25.0
   # BUSINESS_ID=1234567890
   ```

4. **`uv` installed** (Astral). The launcher script uses `uv run` to manage the wrapper's deps in an isolated env.
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

5. **`ffmpeg` on PATH** — required only by `ad_video_get` (video creative analysis). Every other tool works without it.
   ```bash
   brew install ffmpeg        # macOS
   sudo apt install ffmpeg    # Linux
   ```
   Verify with `ffmpeg -version`. If you install it while Claude is running, restart Claude so the MCP server inherits the updated PATH — the server is launched by Claude, not by your shell.

   Transcription itself needs no extra install: `faster-whisper` comes in via `uv sync`, and it downloads its model (~500 MB for the default `small`) to `~/.cache/huggingface` on the first `ad_video_get` call. That first call takes 30-60 seconds; later ones are a few seconds.

   **Platform note — Intel Macs.** `faster-whisper` needs `onnxruntime` (for voice-activity detection), which publishes no macOS x86_64 wheel. As a hard dependency that would fail `uv sync` and take the *entire* MCP server down, so it's excluded on `darwin` + `x86_64` via an environment marker in `pyproject.toml`. Apple silicon, Linux (x86_64/aarch64), and Windows all get local transcription. On an Intel Mac everything else works normally and `ad_video_get` says plainly that transcription isn't available on that machine, suggesting the keyframe path instead. Apple silicon also needs macOS 14+ (the `onnxruntime` wheel floor).

## Install the plugin in Claude

1. Drop this folder anywhere on disk.
2. In Claude (or Claude Code), install the plugin pointing at this folder. The exact UI depends on your Claude surface — same flow your team used for `google-ads`.
3. Claude will run `scripts/start-server.sh`. First launch pulls deps via `uv` and may take 30-60 seconds. Subsequent launches are instant.

## What the agent can do today

Typed MCP tools cover:

- **Ad accounts** — `list`, `get`, `current`
- **Campaigns** — `list`, `get`, `create`, `update`, `delete`
- **Ad sets** — `list`, `get`, `create`, `update`
- **Ads** — `list`, `get`, `create`, `update`
- **Creatives** — `list`, `get`, `create` (single-image)
- **Insights** — `get` with date presets, custom ranges, fields, breakdowns
- **Creative inspection** — `ad_image_get` / `creative_image_get` return the
  creative as an inline image so Claude can read on-image copy and classify
  format; `ad_video_get` returns the spoken script of a video ad as a
  timestamped transcript (keyframes optional).

> **Always pass `ad_account_id` explicitly** to `ad_image_get`,
> `creative_image_get`, and `ad_video_get` when working on any account other
> than the `AD_ACCOUNT_ID` env default. Asset lookups are account-scoped, and
> without the right account they degrade silently — a 64px thumbnail instead of
> the full-resolution creative, with no error to tell you.

### Video creative analysis (`ad_video_get`)

Body copy can't tell you what a video ad's hook was — the hook is spoken, and
the script appears in none of the creative's text fields. `ad_video_get`
resolves ad → creative → `video_id`, gets the video's `source` URL from the
Graph API, and returns the **spoken script as a timestamped transcript**, plus
duration and detected language.

**Nothing is downloaded or stored.** ffmpeg reads the video over the network
and pipes out only the decoded audio, which is transcribed in memory. The video
file never exists on disk, so there's nothing to clean up and no cache to grow.
It's also faster than downloading — pulling just the audio stream takes about a
second versus ~7 to fetch a 23 MB file.

**Keyframes are opt-in** (`include_keyframes=True`), because the transcript is
what carries the script and images are expensive in context. Turn them on when
the *visual* is the question: judging scroll-stop from the opening frame, or
reading an ad whose message is carried by on-screen text rather than speech
(worth remembering — most Meta video is watched muted). You get 5 frames at 0s,
1s, 3s, midpoint, and final; three land inside the 3-second hook window on
purpose. These also stream straight from the URL via HTTP range requests, so
they don't touch disk either.

Two things to know:

- **Whisper model choice.** Default is `small`. Never pass a `.en` model
  (`small.en`, `medium.en`) unless you know the audio is English — `.en` models
  *translate* non-English audio instead of transcribing it, silently losing the
  original language. For known non-English audio, pass `language="es"` with a
  non-`.en` model.
- **The `source` field is permission-gated.** For page-owned videos Meta often
  requires a Page access token (`pages_read_engagement`, `pages_show_list`)
  rather than a system-user token. When that happens the tool fails with an
  actionable error rather than a raw 400: either swap in a Page token, or fall
  back to `ad_image_get` for the thumbnail and diagnose the copy layer only —
  flagging the output `(creative unverified — copy-layer diagnosis only)` so a
  copy-only read never gets mistaken for a full creative diagnosis.

Static creatives raise a clear error pointing you at `ad_image_get` instead.

For anything not yet wrapped (catalogs, product sets, datasets/Pixels, pages), use the `meta_raw` escape hatch tool. It accepts any `meta ads <args...>` invocation. Promote raw calls to typed tools when a workflow proves it needs them.

## Adding new tools

Open `mcp_meta_ads/server.py` and add:

```python
@mcp.tool()
def catalog_create(name: str) -> Any:
    """Create a product catalog."""
    return run_meta(["catalog", "create", *_flag("--name", name)])
```

The function signature becomes the JSON schema Claude sees. Keep docstrings tight — they're the tool description.

## Security model

- Tokens live in `~/.env` on the operator's machine. They are loaded into the MCP server process environment and passed to the `meta` CLI as-is.
- Outbound network calls are limited to:
  - the `meta` CLI, which talks directly to `graph.facebook.com` (no third-party proxy);
  - direct `graph.facebook.com` GETs for the two endpoints the CLI doesn't expose (`/act_X/adimages` hash lookups, `/{video_id}?fields=source`);
  - creative asset reads from Meta's CDN (`fbcdn.net`);
  - a one-time Whisper model download from `huggingface.co` on the first `ad_video_get` call.
- Transcription runs locally and in memory. No creative content is sent to any transcription service, and no video, audio, or transcript is written to disk.
- No telemetry. The wrapper does not log requests or responses to any remote service.

## License

Personal use.
