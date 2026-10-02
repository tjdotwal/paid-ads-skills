---
name: explainer-ad-director
description: Produce a finished scene-to-scene animated explainer video ad from a direct-response script — beat-planned scenes, one locked animation style, ElevenLabs narration recorded before any video, burned captions, ffmpeg assembly, delivered as a vertical MP4 ready to test. Use whenever the user wants an animated video ad, an explainer ad, a motion-graphics ad, a "script to video" ad, an animated Meta/TikTok ad, scene-to-scene animation, or wants to test animation styles on an ad. Also use for batch style or hook variants of one ad. Trigger on "make an animated ad", "turn this script into a video", "explainer video ad", "animated explainer", "video ad for [brand]", "test animation styles". NOT for talking-head or spokesperson video, UGC, creator ads, AI avatars, or anything using a person's likeness — this plugin does not produce those. NOT for static image ads (use ad-creative-strategist) or for writing the script itself (use direct-response-copywriter).
---

# Explainer ad director

Owns the pipeline from a direct-response script to a finished vertical animated ad.
No manual editing step, no CapCut, no tool switching.

## Scope

**We produce:** scene-to-scene animated explainer ads, 15s to 90s+, in a chosen
animation style, narrated, captioned, vertical, ready to upload as test creative.

**We do not produce:** talking-head video, spokespeople, AI avatars, creator-style
UGC, or anything imitating a real person's likeness or voice. This plugin treats
synthetic people delivering scripted endorsements as misleading and does not make
them. If a request needs one, say so and offer the animated route
instead. Do not route to the Higgsfield `ugc-*` workflows.

## Why this pipeline is ours

No Higgsfield bundle serves this. The `ugc-*` bundles are out of scope on
principle, and `faceless-video` explicitly refuses product and brand ads. We build
on ungated primitives: the explainer style-preset catalog, `generate_image` /
`generate_video`, ElevenLabs, and local ffmpeg. The value we add is the
direct-response beat grammar, which none of the bundles model because they all
encode channel storytelling instead.

## The four rules that decide output quality

Learned the hard way. Violating any one of them costs a re-render.

1. **Narration before animation.** Record the VO and measure it *before* generating
   a single clip, then size the scenes to the measured audio. Planning estimates
   are wrong — see `references/beat-grammar.md`.
2. **The real product photo is the only product authority.** Attach the brand's
   packshot to every frame showing the product. Never let a model redraw a label,
   wordmark, or price from memory.
3. **Chain the frames.** Every keyframe references the previous accepted keyframe,
   not just the style anchor. This is what stops a recurring object drifting
   between scenes.
4. **Never generate text.** All words burn in post.

## References

- `references/beat-grammar.md` — beat types, duration arcs, word budgets. **Read
  before planning any scene.**
- `references/style-catalog.md` — the 22 style presets and how the style lock works.
- `references/model-routing.md` — model choice, the draft tier, the minimum-duration
  trim rule, known API constraints, cost discipline.
- `references/animation-constraints.md` — negative constraints and the per-scene QA
  gate. **Every generation prompt gets a block from here.**
- `references/run-state.md` — the on-disk state contract.

Sub-skills: `beat-planner`, `scene-renderer`, `narration`, `ad-assembly`.

## Six gates

Every paid step is gated, and **the cost is quoted before the spend, not reported
after**. Show the estimate, wait for a yes, then generate.

| Gate | What is approved | Cost |
| ---: | --- | --- |
| 1 | Brief — script, duration, brand, approved claims, style | free |
| 2 | Beat plan **and the per-scene prompt map** | free |
| 3 | Style lock, packshot authority, asset masters | low |
| 4 | Narration and the final scene timings | low |
| 5 | Keyframes, as a set | medium |
| 6 | Animated clips | **the expensive one** |

Gate 4 sitting before gates 5 and 6 is the whole point. Timing errors caught in
audio cost cents; caught after animation they cost the entire video spend.

## Pipeline

### Phase 0 — Intake · Gate 1

Collect, asking only for what is genuinely missing and bundling the asks:

- **Script or brief.** A rough brief goes to `direct-response-copywriter` first.
- **Duration.** Offer 15s, 30s, 60s.
- **Brand and product.**
- **Approved claims** — the complete allowlist the brand has signed off. With none,
  write to observable mechanics only.
- **Style.** Offer three presets from different groups in `style-catalog.md`.
- **Brand assets.** Packshot, logo, palette, fonts. The packshot is required if the
  product appears on screen — see rule 2.

Do not ask about models, resolution, batching, or aspect ratio. Vertical 9:16 default.

### Phase 1 — Beat plan and prompt map · Gate 2

Invoke `beat-planner`. It maps the script onto the arc for the target duration and
writes the scene list into `run.json`.

Then write the **per-scene prompt map** into `run.json` before generating anything:
the scene line, the verbatim style clause, the palette, the verbatim asset-roster
strings, and the constraint block. Approve the map, not just the beat table —
re-describing a recurring object in different words per scene is the single most
common continuity defect, and it is free to catch here.

### Phase 2 — Style lock and masters · Gate 3

1. `get_explainer_presets`, then `resolve_explainer_preset` on the chosen preset.
2. Store `preset_id`, `preset_title`, `style_media_id`, and the verbatim
   `style_clause` in `run.json`. Resolve once per run; reuse that one `media_id`.
3. **Packshot authority.** Import the brand's product photo and register it as a
   reference element. Every scene showing the product attaches it.
4. Generate a master still for any recurring character or complex object, approve
   it, then freeze it. Regenerating a master invalidates every keyframe built on it.

### Phase 3 — Narration · Gate 4

Invoke `narration` **before any video generation**. Per-scene audio, one locked
brand voice, then measure every file with `ffprobe` and re-time the beats to the
measured durations. Write the final timings into `run.json`.

Nobody is on camera, so there is no lip sync to honour — which is why narration is
free to lead here, and why a consistent brand voice across every ad costs nothing.

### Phase 4 — Keyframes · Gate 5

Invoke `scene-renderer` for the keyframe pass, with **frame chaining**: scene K's
prompt carries the previous accepted keyframe as a reference alongside the style
anchor and the packshot.

Show the keyframes **as a set** — a contact sheet, not one at a time. Style drift
and asset drift are only visible in comparison. Regenerate rejected scenes by index.

### Phase 5 — Animate · Gate 6

`scene-renderer` again, animating approved keyframes to the timings fixed at gate 4.
Apply **clip contracts**: where a scene's motion ends somewhere specific, that end
frame becomes the next scene's start image, so adjacent clips join cleanly.

Route per `model-routing.md`. Consider the draft tier first for a cheap read of
whether the beat plan works. Generate at the model minimum and record what was
generated so assembly knows the trim.

Run the per-scene QA gate from `animation-constraints.md`. Regenerate failures by
index; freeze what passed.

### Phase 6 — Assemble

Invoke `ad-assembly`. Trims to beat length, concatenates to `out/master.mp4`, lays
the narration under it, normalizes loudness, then burns captions and on-screen text
to `out/final.mp4`. Keep `master.mp4` clean.

### Phase 7 — Deliver

Return the path, duration, style, and the beat plan as shipped. Send the file with
SendUserFile. Report actual spend against the quotes.

Then offer, without doing it unasked: **style variants** (same script and narration,
different style — reuse the audio), **hook variants** (swap scene 1 only), or a
**paused Meta draft** via `meta-ads`.

## Standing rules

- **One beat, one scene, one clip, one narration line.**
- **Quote cost before every paid step.**
- **Never generate text.** See `animation-constraints.md`.
- **Never generate native audio.** `generate_audio:false`.
- **One style reference on every scene call**, plus the chained previous frame.
- **Only approved claims.** No invented statistics, testimonials, or outcomes.
- **Write `run.json` after every phase**, so a run is resumable.
- **Regenerate by scene index, never the whole run.**
