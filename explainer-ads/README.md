# explainer-ads

Script to finished animated video ad, in one pass. No CapCut, no tool switching, no
manual edit step.

Give it a direct-response script, a brand, and a duration. It plans the scenes,
locks an animation style, renders and animates each scene, narrates in the brand's
voice, burns captions, and hands back a vertical MP4 ready to upload as test
creative.

## What it makes

Scene-to-scene animated explainer ads, 15s to 90s+, vertical 9:16, narrated and
captioned. One beat per scene: a 3s hook, a problem drill-down, a mechanism, a
solution, a CTA.

## What it does not make

Talking-head video, spokespeople, AI avatars, or creator-style UGC. This plugin treats
synthetic people delivering scripted endorsements as misleading and does not produce
them. Nothing here imitates a real person's likeness or voice.

## Usage

```
/explainer-ad
```

Or just ask — "make a 30 second animated ad for Acme Dental from this script".

## Skills

| Skill | Job |
| --- | --- |
| `explainer-ad-director` | Owns the pipeline and the run state. Start here. |
| `beat-planner` | Script → scene list with beats, durations, and word budgets. |
| `scene-renderer` | Style-locked keyframes, then animation. |
| `narration` | ElevenLabs voiceover, one locked voice per brand. |
| `ad-assembly` | ffmpeg trim, concat, mux, caption burn, delivery check. |

## Companion skill

Motion and camera vocabulary comes from the community
[higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill)
(MIT), installed separately at `~/.claude/skills/higgsfield`. It is a prompt-craft
reference library and dispatcher, not a pipeline — complementary to this plugin
rather than overlapping it.

We consult it for named camera presets, the one-move rule, and failure diagnosis.
It costs ~158 tokens always-on; its 33 sub-skills stay behind progressive disclosure
and only load when opened. Refresh with `git pull` in that directory — it is not a
plugin, so `claude plugin update` does not apply.

This plugin degrades gracefully without it: the beat table in `scene-renderer` names
the moves directly.

## Requirements

- **Higgsfield MCP** — image and video generation, and the explainer style catalog.
- **ElevenLabs MCP** — narration.
- **ffmpeg + ffprobe** on PATH. Verified against 8.1.1.

No API keys to configure; both are MCP connections.

### Caption rendering

Captions need text rendering, which varies by ffmpeg build. Check yours:

```
ffmpeg -hide_banner -filters | grep -cE ' (ass|subtitles|drawtext) '
```

- **3** — libass present, captions burn directly from an ASS file.
- **0** — no libass. `ad-assembly` falls back to `scripts/render_captions.py`, which
  draws captions with Pillow and composites them with `overlay`. Needs a venv with
  pillow; the skill has the commands.

The machine this was built on returns 0 — its ffmpeg 8.1.1 was compiled without
libass, freetype, or fontconfig. `brew upgrade ffmpeg` (8.1.1 → 9.0.1) enables the
direct path and is worth doing, but the fallback means it is not a blocker.

## Design notes

**Why we own this pipeline.** No Higgsfield bundle serves it. The `ugc-*` bundles are
out of scope on principle, and `faceless-video` explicitly refuses product and brand
ads. We build on the ungated primitives instead — the explainer style-preset
catalog, `generate_image` / `generate_video`, ElevenLabs, local ffmpeg. What we add
is the direct-response beat grammar, which none of the bundles model because they
encode channel storytelling instead.

**The four rules that decide output quality**, each learned by breaking it:

1. **Narration before animation.** Record and measure the VO first, then size scenes
   to the audio. Planning estimates are wrong — measured delivery ran 3.08 w/s
   against a planned 2.5, which put 4.4s of dead air in a 30s ad. A timing error
   found in audio costs cents; found after animation it costs the video spend.
2. **The real packshot is the only product authority.** Attach the brand's product
   photo to every frame showing it. Never let a model redraw a label or wordmark.
3. **Chain the frames.** Scene K references scene K-1's keyframe, not just the style
   anchor. Without it a recurring diagram comes back different in every scene, even
   with a perfect style lock.
4. **Never generate text.** All words burn in post with ffmpeg.

**Six gates**, each quoting its cost *before* the spend. Gate 4 (narration) sits
ahead of gates 5 and 6 (keyframes, clips) on purpose — that ordering is rule 1 made
operational.

**Two-tier rendering:** draft the whole ad on `gemini_omni` at 720p to check the cut
reads, then re-render approved scenes on `minimax_h3` at 2K.
