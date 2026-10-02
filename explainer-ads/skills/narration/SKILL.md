---
name: narration
description: Generate per-scene voiceover for an animated explainer ad with ElevenLabs, using one consistent brand voice, and reconcile each line's real audio duration against its planned scene length. Use when generating narration or voiceover for a video ad, picking or locking a brand brand voice, or when the explainer-ad-director pipeline reaches its narration phase.
---

# Narration

**Runs before any video is generated.** Scene lengths are set by measured audio, not
by planning estimates. Recording first costs cents; discovering a timing error after
animation costs the whole video spend.

Nobody is on camera in our ads, so there is no lip sync to match. Narration is a
free choice, which is why a single consistent voice per brand costs nothing and is
worth locking.

## Voice selection

1. `search_voices` to list voices already in the workspace. If the brand has a
   locked voice, reuse it — check `voice.voice_id` in a previous `run.json` for that
   brand.
2. For a new brand, shortlist two or three and generate the HOOK line in each so
   the choice is made on the actual line rather than a demo.
3. Record `voice_id` and `voice_name` in `run.json`. That is now the brand's voice
   across every ad.

Do not clone a real person's voice. Instant cloning is available on the account and
we do not use it for ads.

## Generation

One file per scene, so a single line can be redone without re-rendering the track.

`text_to_speech` per scene:

- `text` — the scene's narration line, alone.
- `voice_id` — the locked brand voice.
- `model_id` — `eleven_multilingual_v2` for delivery. `eleven_flash_v2_5` is fine
  for a draft pass.
- `stability` — `0.5`. Lower for a more expressive read on a HOOK, higher if a line
  comes back uneven.
- `speed` — leave at `1`. Never speed up a read to force a fit; move the beat instead.
- `output_directory` — the run's `audio/` directory.
- `output_format` — `mp3_44100_128`.

Rename outputs to `scene_NN.mp3`.

## Duration reconciliation — do not skip this

The word budget is an estimate. The audio is the fact. Measure every file:

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 audio/scene_01.mp3
```

Compare each against the scene's planned length:

- **Audio fits with a little room** — good. A scene should end with roughly 0.2–0.4s
  of visual after the line lands, so the cut does not clip the last word.
- **Audio is longer than the planned beat** — lengthen the beat. Because this runs
  before animation, the beat is still free to move. Only cut words if the beat cannot
  grow (see the cap in `beat-grammar.md`).
- **Audio is shorter** — shorten the beat to audio + tail. Do not leave the slack in;
  1.8s of dead air on a 6s scene reads as a stall.

**Re-time, then write the final timings into `run.json`.** That is the contract the
renderer and assembly both build against. Never animate to planned lengths when
measured ones exist.

Record real durations in `run.json`, then reconcile the total against the target.
Assembly times captions from these files, so they have to be right before it runs.

Hand the per-scene MP3s to `ad-assembly` as they are. It converts each to PCM WAV
before concatenating, because MP3 frames are fixed-size and concatenating MP3s
accumulates timing drift. Do not pre-concatenate them here.

## Cost

ElevenLabs is on the starter tier with a monthly character allowance. A 60s ad is
roughly 150 words, so a full ad is cheap — but style-variant testing multiplies it
for no benefit, because the narration is identical across style variants. Generate
once and copy `audio/` into the sibling variant directory.

Check the allowance with `check_subscription` before a large batch run.

## Music

A music bed is optional and off by default. Where the brand wants one, keep it well
under the voice and duck it further beneath the narration. Layer it at the assembly
step, not here.
