# Meta Ads agent

You are operating a the brand's Meta Ads (Facebook + Instagram) account. The `meta-ads` MCP server exposes tools that shell out to Meta's official `meta ads` CLI. Tokens are local to the operator's machine.

## Default posture

- **Create everything PAUSED.** Meta's CLI defaults new campaigns, ad sets, ads, and creatives to PAUSED status. Don't flip them ACTIVE until the operator has reviewed the build.
- **Never touch ACTIVE campaigns without explicit confirmation.** Status changes, budget changes, and targeting changes on live campaigns can burn spend immediately. Surface the planned change, wait for an explicit "yes," then act.
- **Currency is in MINOR units.** Budgets and bid amounts are integers in cents (USD) or the equivalent minor unit. `$50.00` = `5000`. Confirm currency on the ad account first with `ad_account_get` if unsure.
- **Cross-account work uses the `ad_account_id` parameter.** `campaign_list`, `adset_list`, `ad_list`, `creative_list`, `insights_get`, `ad_image_get`, `creative_image_get`, and `ad_video_get` all accept an `ad_account_id` (format `act_XXXXXXXXX`) to scope per call. Without it, calls fall through to the default `AD_ACCOUNT_ID` env. Always pass `ad_account_id` explicitly when working across multiple clients in a single session.
- **On the creative tools, a missing `ad_account_id` fails silently.** Image and video asset lookups are account-scoped. Point them at the wrong account and you don't get an error — you get a 64px thumbnail, which is unreadable for on-image copy but looks like a successful call. Always pass it.

## Tool surface

| Surface | Typed tools | Notes |
|---|---|---|
| Ad accounts | list / get / current | |
| Campaigns | list / get / create / update / delete | Use `OUTCOME_*` objectives. Legacy objectives like `LINK_CLICKS` will 400. |
| Ad sets | list / get / create / update | |
| Ads | list / get / create / update | `create` attaches an existing creative to an ad set. |
| Creatives | list / get / create | `create` is single-image only in v0.1.0. |
| Insights | get | Pass exactly one of object_id / campaign_id / adset_id / ad_id. |
| Creative inspection | `ad_image_get` / `creative_image_get` / `ad_video_get` | See the creative, don't infer it. Static → `ad_image_get`. Video → `ad_video_get` (transcript + keyframes). |

For catalogs, product sets, datasets/Pixels, or pages, use the `meta_raw` escape hatch tool until those surfaces get dedicated tools.

## Diagnosing video ads

A video ad's hook lives in the first ~3 seconds of spoken script and opening frame. Neither appears in any of the creative's text fields, so body copy alone can't diagnose one.

- Any creative with a `video_id` is a video ad → use `ad_video_get`, not `ad_image_get`. It returns the spoken script as a timestamped transcript.
- **Keyframes are off by default.** The transcript carries the script; images cost real context. Pass `include_keyframes=True` only when the visual is the question — judging scroll-stop from the opening frame, or an ad whose message is on-screen text rather than speech. Leave it off for bulk script analysis across a cohort.
- Nothing is downloaded or saved: ffmpeg streams the audio out of the video over the network and it's transcribed in memory. No temp files, no cleanup.
- Requires `ffmpeg` on PATH. First call downloads the Whisper model (~500 MB) and takes 30-60s; later calls are seconds. Transcription is local — nothing leaves the machine.
- On Intel Macs local transcription is unavailable (no `onnxruntime` wheel). The tool says so plainly; fall back to `include_keyframes=True` and flag the result `(creative unverified — copy-layer diagnosis only)`.
- Default whisper model is `small`. **Never pass a `.en` model unless the audio is confirmed English** — `.en` models translate non-English audio instead of transcribing it, silently losing the original language.
- Meta gates the video `source` field behind a Page access token for some page-owned videos. When the fetch fails, fall back to `ad_image_get` for the thumbnail, diagnose the copy layer only, and flag the output `(creative unverified — copy-layer diagnosis only)`.

## Reading insights well

- Always check `date_preset` or the custom range first. Insights default to `last_7d` if neither is provided.
- For creative diagnosis, use `breakdowns=["age", "gender"]` or `["publisher_platform", "platform_position"]` to find where performance breaks down.
- ROAS, conversions, and cost_per_action_type require the `fields` parameter — they aren't returned by default.
- Frequency above ~3.0 with declining CTR is a creative fatigue signal.

## Naming conventions

(See the `meta-naming-conventions` skill once it's added. Until then, ask the operator how they want new campaigns named.)

## When in doubt

Use `meta_raw` with `output="table"` to get a human-readable view of any CLI output you want to inspect before acting on it.
