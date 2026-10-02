# Animation constraint library

Negative constraints for **animated** explainer ads. These are not the same failure
modes as photoreal or live-action AI video — warped hands and waxy skin are not the
problem here. Style drift and baked text are.

Append the relevant block to every generation prompt.

## The big one — style drift

The most common way a multi-scene animated ad fails is that scene 7 does not look
like scene 2. Line weight changes, the palette warms, a flat 2D style grows soft
shading, a clay style goes glossy.

Defences, in order of effect:

1. **Chain the frames.** Pass scene K-1's accepted keyframe as a reference on scene
   K. This is the strongest defence and the one most often skipped — a style lock
   alone will still let a recurring diagram come back three different ways across
   three scenes. It forces keyframes to generate in scene order; accept that.
2. **Attach the real packshot** to every product frame. Never let a label be redrawn.
3. Pass the **same** resolved style-reference `media_id` on every scene call.
4. Repeat the style clause **verbatim** in every scene prompt. Copy the exact string
   from run state — do not paraphrase per scene.
5. Repeat the palette as named colours, not as a mood.
6. Write **one description string per recurring asset** in the roster and paste it
   byte-identical into every prompt that needs it. Describing "the same" object in
   different words per scene is how it stops being the same object.

Prompt clause:

> Identical rendering style in every frame: the same line weight, the same shading
> model, the same palette, the same level of detail as the style reference. No
> change in art style, no added realism, no added texture, no added gradient
> shading, no shift in colour temperature.

## Never bake text

Generation models produce gibberish, mirrored, or misspelled lettering, and they
cannot be trusted with a brand name, a price, or a statistic.

**Never generate on-screen text. Burn every word in post with ffmpeg.** This covers
captions, the PROOF number, the price, the CTA, and the wordmark. Where a scene
needs to leave room for text, ask for empty space, not for words.

Prompt clause:

> No text, no lettering, no numbers, no words, no labels, no captions, no logos, no
> wordmarks, no watermarks, no UI chrome, no signage anywhere in the frame. Leave
> the lower third uncluttered and free of detail.

## Geometry and motion

Animated models fail by melting, not by growing extra fingers.

Prompt clause:

> Stable geometry throughout: no morphing, melting, warping, or dissolving forms; no
> objects appearing or disappearing mid-shot; no drifting proportions; no
> flickering; no jittering outlines; consistent object count from first frame to
> last. One continuous camera move, no cuts inside the clip.

## Motion pacing

Over-busy motion is the second most common failure. A 3s clip with four things
moving reads as noise at feed scroll speed.

Stacking moves is the single biggest cause of jitter and outright generation
failure. One primary move per shot, always — and name it (`Dolly In`, not "a push").
Never write "zoom" for a physical camera move. Full named-preset tables live in the
`higgsfield` skill: `skills/higgsfield-camera/SKILL.md`.

Prompt clause:

> One clear named camera move only, at a calm readable speed. No stacked moves, no
> frantic movement, no camera shake, no whip pans, no rapid zooms, no strobing, no
> flashing, no ping-pong or looping-back motion. Motion resolves by the final frame
> and does not stop dead.

## Composition for placement

Meta and TikTok cover the top and bottom of a 9:16 frame with their own UI, and our
captions sit in the lower third.

Prompt clause:

> Vertical 9:16 composition. Subject centred within the middle 60% of the frame
> height. Keep the top 15% and the bottom 25% visually quiet and free of subject
> detail. No letterboxing, no pillarboxing, no black bars, no split screen, no
> border, no frame-within-a-frame.

## Style-specific additions

- **Flat 2D / vector styles** — "Flat colour fills only. No ambient occlusion, no
  drop shadows, no specular highlights, no photographic texture, no depth blur."
- **Clay / papercraft / tactile** — "Matte surfaces with visible material texture.
  No glossy plastic sheen, no chrome, no glass reflection, no studio product
  lighting."
- **Whiteboard / hand-drawn** — "Consistent hand-drawn line weight on a plain
  ground. No perspective rendering, no colour grading, no photographic elements."
- **3D styles** — "Even soft lighting. No lens flare, no bloom, no HDR glow, no
  teal-and-orange grade, no shallow depth of field."

## Per-scene QA gate

Inspect the keyframe before animating, and sample frames of every clip before
assembly. Reject and regenerate the scene when any of these is true:

- The art style does not match the previous accepted scene.
- Any text, number, or logo appears anywhere in the frame.
- The subject sits under where the caption or platform UI will be.
- A recurring character, product, or object is not recognisably the same as in its
  earlier scene.
- Geometry morphs, flickers, or changes count during the clip.
- The motion has not resolved by the final frame, or the clip ends mid-movement.
- The frame is letterboxed or is not a true 9:16.

Fix by regenerating that scene index only, with the failed constraint clause
strengthened. Never regenerate the whole run.

**One exception.** If the fix changes a recurring asset's *design*, every scene
showing that asset has to be regenerated with it — including the other half of any
start/end keyframe pair. A clip whose start and end show two different designs of the
same object morphs badly, which is worse than the inconsistency you set out to fix.
Check the whole set on a contact sheet after any asset-level change.
