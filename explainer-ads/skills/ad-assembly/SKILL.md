---
name: ad-assembly
description: Assemble per-scene clips and narration into a finished vertical video ad with local ffmpeg — trims each clip to its beat length, concatenates to a clean master, lays in sample-exact voiceover, and burns TikTok-style captions plus on-screen text. Handles ffmpeg builds with or without libass. Use when stitching scenes, assembling a video ad, burning captions or subtitles into an ad, or when the explainer-ad-director pipeline reaches its assembly phase.
---

# Ad assembly

Local ffmpeg. Two outputs: `out/master.mp4` stays clean with no burned text, and
`out/final.mp4` carries the captions. Every text change re-burns from the master, so
a caption fix never means re-rendering scenes.

Every command below was verified against ffmpeg 8.1.1 on 2026-08-25.

## 0. Capability check — run this first

Text rendering is the one thing that varies by build. Check before assuming:

```bash
ffmpeg -hide_banner -filters | grep -cE ' (ass|subtitles|drawtext) '
```

- **Returns 0** — no libass/freetype. Use **Path B** for captions. This is the case
  on the current machine: its ffmpeg 8.1.1 was built without libass, freetype, or
  fontconfig, so `ass`, `subtitles`, and `drawtext` are all unavailable. `overlay`
  and `drawbox` are present.
- **Returns 3** — use **Path A**, which is simpler.

## 1. Trim each clip to its beat length

Clips were generated at the model minimum, usually longer than the beat.

```bash
ffmpeg -y -i clips/scene_01_raw.mp4 -t 3.0 -an \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p clips/scene_01.mp4
```

Re-encode rather than `-c copy` — a stream copy cuts at the nearest keyframe, so the
clip comes out the wrong length. `-an` drops any native audio.

## 2. Normalize before concatenating

Clips from different models differ in resolution, frame rate, and pixel format, and
the concat demuxer needs them identical.

```bash
ffmpeg -y -i clips/scene_01.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fps=30,setsar=1" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -an clips/scene_01_norm.mp4
```

Verified: 720x1280@24 and 1080x1920@30 inputs both normalize to 1080x1920@30 with
durations preserved exactly.

If a clip needs real padding to reach 9:16, that is a generation failure — send it
back to `scene-renderer` rather than padding it into place.

## 3. Concatenate to video-only

```bash
printf "file 'scene_01_norm.mp4'\nfile 'scene_02_norm.mp4'\n" > clips/concat.txt
ffmpeg -y -f concat -safe 0 -i clips/concat.txt -c copy out/video_only.mp4
```

Build `concat.txt` from the scene order in `run.json`, never from a shell glob —
`scene_10` sorts before `scene_2`.

Hard cuts between scenes. No crossfades: they blur the beat boundary that gives the
ad its pace.

## 4. Narration — use WAV intermediates

**Do not concatenate MP3s.** MP3 frames are a fixed 1152 samples, so an MP3 cannot be
an exact arbitrary length and concatenating them accumulates rounding error. Measured:
two scenes that should total 8.000s produced an 8.030s MP3, plus non-monotonic DTS
warnings. Over a 9-scene ad that drift desyncs captions from the picture.

Pad each scene's audio to its exact scene length as PCM WAV, which is sample-exact:

```bash
ffmpeg -y -i audio/scene_01.mp3 -af "apad=whole_dur=3.0" \
  -ar 44100 -ac 2 -c:a pcm_s16le audio/scene_01_pad.wav
```

Then concatenate the WAVs and mux, encoding to AAC once:

```bash
printf "file 'scene_01_pad.wav'\nfile 'scene_02_pad.wav'\n" > audio/concat.txt
ffmpeg -y -f concat -safe 0 -i audio/concat.txt -c copy audio/vo.wav

ffmpeg -y -i out/video_only.mp4 -i audio/vo.wav \
  -c:v copy -c:a aac -b:a 192k -shortest out/master.mp4
```

Verified exact: 3.000 + 5.000 → 8.000000, with video and audio stream durations both
8.000000.

A single-pass filtergraph works too, and is worth using when you want to avoid
intermediates:

```bash
ffmpeg -y -i audio/scene_01.mp3 -i audio/scene_02.mp3 -filter_complex \
  "[0:a]apad=whole_dur=3.0,aresample=44100[a0];[1:a]apad=whole_dur=5.0,aresample=44100[a1];[a0][a1]concat=n=2:v=0:a=1[out]" \
  -map "[out]" -ar 44100 -ac 2 -c:a pcm_s16le audio/vo.wav
```

Confirm alignment before continuing — the two should match within ~0.1s:

```bash
ffprobe -v error -show_entries stream=codec_type,duration -of csv=p=0 out/master.mp4
```

## 5. Captions

Timings come from the per-scene audio durations in `run.json`, which are exact — we
wrote the words, so no transcription is needed. Where word-level timing is wanted,
transcribe `vo.wav` with ElevenLabs `speech_to_text`.

Chunk captions the way native social captions read: two to four words per cue, one
or two lines, centred, above the platform UI.

### Path A — libass available

Write an ASS file and burn it:

```bash
ffmpeg -y -i out/master.mp4 -vf "ass=captions/captions.ass" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a copy out/final.mp4
```

Use `PlayResX: 1080`, `PlayResY: 1920`, `Alignment: 2`, and `MarginV: 420` to clear
the bottom UI.

### Path B — no libass (current machine)

Pillow draws the text into transparent PNGs; ffmpeg only composites with `overlay`.
Use the bundled renderer at `${CLAUDE_PLUGIN_ROOT}/scripts/render_captions.py`
(i.e. `scripts/render_captions.py` relative to this plugin's root).

Pillow is not in the system Python. Use a venv:

```bash
python3 -m venv ~/.cache/explainer-captions && ~/.cache/explainer-captions/bin/pip install -q pillow
```

Write cues as JSON, then render:

```bash
~/.cache/explainer-captions/bin/python \
  "${CLAUDE_PLUGIN_ROOT}/scripts/render_captions.py" \
  captions/cues.json captions/png --size 86 --margin-v 420
```

`cues.json` is `[{"start": 0.0, "end": 0.9, "text": "Most implant"}, ...]`. The
script writes `cue_000.png`… plus `filtergraph.txt`, and prints the full ffmpeg
command to stderr.

Two things that will bite:

1. **`-loop 1` on every PNG input is mandatory.** A single-frame PNG input is
   exhausted immediately and the time-gated overlay then never composites — the
   render succeeds and silently contains no captions. Verified failure mode.
2. **Build the input list as a shell array.** In zsh an unquoted `$VAR` does not
   word-split, so a flat string collapses into one argument and ffmpeg reports
   "Invalid file index 1".

```bash
inputs=(); for p in captions/png/cue_*.png; do inputs+=(-loop 1 -i "$p"); done
GRAPH=$(cat captions/png/filtergraph.txt)
LAST="v$(( $(ls captions/png/cue_*.png | wc -l) - 1 ))"
ffmpeg -y -i out/master.mp4 "${inputs[@]}" -filter_complex "$GRAPH" \
  -map "[$LAST]" -map 0:a -shortest \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a copy out/final.mp4
```

Fonts available on this machine: Avenir Next, Helvetica Neue, and Arial Bold, in
`/System/Library/Fonts` and `/System/Library/Fonts/Supplemental`. `.ttc` files need
`index=0`, which the script handles.

### Verify captions actually rendered

`-shortest` plus a silently-inactive overlay can produce a clean exit and no
captions, so check pixels rather than the exit code. Sample frames across the
timeline and confirm white-on-black stroke text in the caption band:

```bash
ffmpeg -y -ss 2.4 -i out/final.mp4 -frames:v 1 /tmp/chk.png
ffmpeg -y -i /tmp/chk.png -vf "crop=1080:280:0:1280" /tmp/band.png
```

Then look at `/tmp/band.png`. Check at least one frame per scene.

## 5b. Loudness

Social platforms target about **-14 LUFS integrated**. A peak check is not enough — a
track can peak at -1dB and still be far too quiet or too hot overall.

Two-pass loudnorm, measuring then correcting:

```bash
# pass 1 - measure
ffmpeg -i out/master.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=summary -f null -
# pass 2 - apply the measured values
ffmpeg -y -i out/master.mp4 \
  -af loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=<mi>:measured_TP=<mtp>:measured_LRA=<mlra>:measured_thresh=<mt>:linear=true \
  -c:v copy -c:a aac -b:a 192k out/master_norm.mp4
```

Normalize the master *before* burning captions, so `final.mp4` inherits it and both
outputs match. Verify:

```bash
ffmpeg -i out/master_norm.mp4 -af loudnorm=I=-14:TP=-1.5:print_format=summary -f null -
```

Single-pass `loudnorm` also works but is less accurate on a 30s clip, because it
adapts as it goes rather than applying one correction.

## 6. On-screen text and logo

The PROOF number, price, CTA, and wordmark burn in the same pass. With no `drawtext`
available, render them as PNGs the same way and add `overlay` links to the chain. A
logo, gated to the first three seconds:

```bash
-loop 1 -i brand/logo.png
# ...;[vN][K:v]overlay=W-w-60:80:enable='between(t,0,3)'[vout]
```

Keep the logo out of the bottom 25% where captions and platform UI live.

## 7. Delivery check

- Duration matches the target within ~0.2s.
- 1080x1920, 30fps, H.264, yuv420p, AAC. Plays in QuickTime and the Meta Ads preview.
- Captions verified by pixel check, not by exit code.
- No cue clipped at the bottom or overlapping a scene cut awkwardly.
- Narration audible without clipping — `ffmpeg -i out/final.mp4 -af volumedetect -f null -`,
  aim for max around -1dB.
- `master.mp4` retained clean.

Send `final.mp4` with SendUserFile. Record status `delivered` in `run.json`.

## Optional: upgrade ffmpeg to simplify this

`brew upgrade ffmpeg` moves 8.1.1 → 9.0.1, whose homebrew-core formula includes
libass. That enables Path A and `drawtext`, and removes the Pillow dependency. Path
B exists so the pipeline works either way. Note `brew` fails when the working
directory is unreadable — run it from `/tmp`.
