---
name: scene-renderer
description: Generate style-locked, frame-chained keyframe stills and animate them into per-scene clips for an animated explainer ad, using Higgsfield generate_image and generate_video with one shared style reference plus the brand's real packshot. Use when rendering scenes, generating keyframes, animating scenes for a video ad, or when the explainer-ad-director pipeline reaches its keyframe or animate phase.
---

# Scene renderer

Two passes: keyframes, then animation. Never animate an unapproved keyframe, and
never start either pass before the narration is measured — scene lengths come from
audio, not estimates.

Read `../explainer-ad-director/references/model-routing.md` and
`../explainer-ad-director/references/animation-constraints.md` first.

## Prompt structure

Layers, in order. Layers 2, 3 and 6 are copied **verbatim** from `run.json` —
byte-identical in every scene of the run.

1. **Scene** — the visual concept for this beat.
2. **Style** — `style_clause`, verbatim. Never paraphrased per scene.
3. **Palette** — named colours, not a mood.
4. **Assets** — the roster description string for anything recurring, verbatim.
5. **Motion** — clips only: one motion idea, with a direction.
6. **Constraints** — the relevant blocks from `animation-constraints.md`, always
   including the no-text and style-drift blocks.

## The three consistency mechanisms

Stack all three. Each catches drift the others miss.

### 1. Style anchor
The one `style_media_id` resolved at gate 3, attached to every keyframe call.

### 2. Packshot authority
**The brand's real product photo is the only product authority.** Register it as a
reference element and attach it to every frame showing the product. Never let a
model redraw a label, wordmark, price, or ingredient list from memory — generated
lettering degrades a little on each pass, and a wrong brand name is unshippable.

Amend the no-text constraint on product scenes:

> No text, lettering, numbers, captions, watermarks or signage anywhere in the frame
> EXCEPT the product's own printed label, which must reproduce the reference exactly.

### 3. Frame chaining
**Scene K's prompt carries scene K-1's accepted keyframe as an additional reference.**
Not just the style anchor — the actual previous frame.

This is the mechanism that keeps a recurring object identical across scenes. Without
it, one diagram drawn in three scenes comes back three different ways even with a
perfect style lock and one verbatim description. Higgsfield's own bundled workflows
do this ("append the cleaned previous board job ID as the final image media"), and it
is worth the sequential dependency it forces.

Consequence: keyframes generate **in scene order**, because K needs K-1. Batch only
where scenes share no recurring asset.

## Keyframe pass

Default `seedream_v5_pro`; `gpt_image_2` for scenes needing legible structure — a
diagram, a chart, a step-through.

**Reference-element caveat:** `seedream_v5_pro` does **not** support reference
elements. If the run uses a packshot or character element, the keyframe model must be
one of `gpt_image_2`, `nano_banana_pro`, `nano_banana_2`, `seedream_v4_5`, or
`seedream_v5_lite`. Verify against `show_reference_elements` before choosing.

Attach: `style_media_id`, the packshot on product scenes, and the previous accepted
keyframe from scene K-1. Aspect `9:16`.

Where a scene's motion has a defined destination, generate an **end keyframe** too.
Worth it for MECHANISM and SOLUTION beats; unnecessary for a simple push-in.

Then run the keyframe half of the QA gate and **show the set as a contact sheet.**
Style and asset drift are only visible in comparison — reviewing one frame at a time
will miss what a grid makes obvious. Record paths and `keyframe_approved` in
`run.json`.

## Animation pass

Per scene, on approved keyframes, to the timings fixed at gate 4:

- `start_image` — the approved keyframe.
- `end_image` — the end keyframe where one exists.
- `duration` — the model minimum at or above the beat length. **Never round the beat
  up to the model minimum.** Record `clip_generated_seconds`; assembly trims.
- `generate_audio` — `false` wherever the parameter exists.
- `aspect_ratio` — `9:16`.

**Known API constraint:** on `minimax_h3`, `start_image`/`end_image` **cannot** be
combined with `image_references` — the call is rejected 422. This is fine: the
keyframe was generated *with* the style anchor, so it already carries the locked
style. Drop the style reference on the video call and keep the keyframes.

**Preset interception:** a video batch may come back `submission_failed` with a
preset recommendation instead of jobs. Nothing is charged. Decline it by passing
`declined_preset_id` on every request and resubmit.

### Clip contracts

Where scene K ends on a specific composition and scene K+1 opens on the same subject,
bind them: **K's end frame becomes K+1's start image.** That makes the join read as
one continuous piece rather than two clips butted together.

Do not bind across a deliberate hard cut — a contract between unrelated compositions
just constrains both shots for nothing.

### Camera craft

Motion vocabulary comes from the `higgsfield` skill (installed at
`~/.claude/skills/higgsfield`). Load `skills/higgsfield-camera/SKILL.md` for the full
named-preset tables. Four rules from it that change how we write motion prompts:

**1. Name the exact preset.** Models are trained on the named moves — `Dolly In`,
`Super Dolly In`, `Crash Zoom In`, `Crane Up`, `Crane Down`, `Dolly Left/Right`. Plain
English ("a slow, small push in") is weaker than the name.

**2. One move per shot.** Their reference calls stacking moves "the #1 cause of
jitter, unwanted rotation, and failed generations." One primary move, never a
dolly-plus-pan-plus-tilt.

**3. Never write "zoom" for a physical move.** Name dolly / track / push-in /
pull-out. A zoom is a lens change; a dolly is the camera travelling. Asking for the
wrong one gets the wrong look.

**4. Micro-moves need travel *and* time.** A slow move without a stated distance gets
oversold by the model. Write it explicitly:

> over the full 5 seconds the camera pushes in only 10-15 centimetres — slow enough
> to barely register. No zoom, no sudden push.

Reliable phrasings, verbatim from their library:

| Intent | Phrase |
| --- | --- |
| No movement | `locked-off static camera, no movement` |
| Slow approach | `slow dolly push from medium shot to tight close-up over 8 seconds` |
| Reveal scale | `crane shot rising from ground level to overhead` |
| Hard emphasis | `crash zoom from wide to extreme close-up on impact` |

**Flat-art caveat.** Their vocabulary is cinematic and assumes a 3D world. Moves that
depend on parallax — orbit, `Crane Over The Head`, FPV — do not translate to flat
vector artwork and will produce warping. For our styles stick to `Dolly In` /
`Dolly Out`, lateral `Dolly Left/Right`, and locked-off static. Their
Product/E-commerce genre row agrees: orbit, slow push-in, static — avoid handheld and
whip pan.

### Motion direction per beat

| Beat | Named move | Notes |
| --- | --- | --- |
| HOOK | `Super Dolly In` or `Crash Zoom In` | Movement on frame 1. Exaggerated and fast — a hook has no time for a slow build. |
| PROBLEM | `Dolly In`, slow | State travel and time. Push onto the friction. |
| AGITATE | `locked-off static camera` | Hold the frame and let the escalating quantity carry the motion. |
| FAILED_ALT | `Dolly Left` or `Dolly Right` | Lateral track as the alternative is set aside. |
| MECHANISM | `locked-off static camera` | Parts assemble in sequence. The camera must not compete with the diagram. |
| SOLUTION | `Dolly In`, slow | Resolve onto the product. Packshot attached. |
| PROOF | `locked-off static camera, no movement` | Near-still so burned text carries it. |
| OBJECTION | `Dolly In`, short | The answer landing. |
| CTA | `locked-off static camera, no movement` | End card, room for text. |

### The impossibility check — run this before submitting

**The stated move must be able to produce the stated end framing.** A slow push cannot
get from a wide to an extreme close-up; a 10cm pull cannot land a full-body reveal.
When move and end frame disagree the prompt is internally impossible, and the model
either picks one and improvises the other or fails outright.

This is a diagnosed cause of repeat failure, not a theory. A HOOK written as a smooth
push-in from a wide two-subject shot to an extreme close diagram failed twice on
`minimax_h3` before being animated locally. The prompt was impossible: the move was
small, the framing change was enormous.

Fix on whichever side is cheaper:

- **Enlarge the move** — `Super Dolly In` or `Crash Zoom In` instead of a push.
- **Shrink the framing change** — start closer, or end wider.
- **Split the beat** into two single-keyframe shots.

Check every start/end keyframe pair this way before spending on video.

## When a scene will not generate

Some shots are beyond keyframe interpolation — a start and end frame with no shared
geometry (a wide subject cutting to an extreme close diagram) fails repeatedly rather
than producing something bad. Failed jobs do not charge.

After two failures, stop retrying and pick one:

1. **Split the beat** into two shorter single-keyframe shots.
2. **Animate locally.** For flat vector art a camera push is scale-and-translate,
   which ffmpeg does deterministically and free:

```bash
ffmpeg -loop 1 -i keyframe_2x.png -t 1.875 \
  -vf "zoompan=z='1+0.17*on/44':x='iw/2-(iw/zoom/2)':y='ih*0.46-(ih/zoom/2)':d=1:s=1080x1920:fps=24"
```

Render from a 2x plate so pushing in does not soften. For flat styles this is often
*better* than generated motion, which can wobble line weights. Say so in delivery
when a scene was animated this way.

## QA gate

Run the per-scene gate in `animation-constraints.md` on keyframes and again on clip
frames. Regenerate rejected scenes by index with the failed constraint strengthened.
Freeze accepted indices.

When a fix changes a recurring asset's design, **every scene showing that asset must
be regenerated too** — including the other half of a start/end pair. Fixing one frame
of a pair leaves a clip that morphs between two designs, which is worse than the
original defect.
