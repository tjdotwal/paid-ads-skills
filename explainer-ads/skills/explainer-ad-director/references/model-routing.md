# Model routing

Verify with `models_explore action:"get" model_id:"<id>"` before a run. Model
parameters change; this table is a starting point, not an authority.

## Image — scene keyframes

| Model | Reference elements | Use for |
| --- | :---: | --- |
| `gpt_image_2` | yes | Keyframes needing legible structure — diagrams, charts, step-throughs. Strong at reproducing a supplied label. Default when a packshot is involved. |
| `seedream_v5_pro` | **no** | Style-faithful keyframes, best style hold — but **cannot take reference elements**. Only for runs with no packshot and no character element. |
| `nano_banana_pro` | yes | High-resolution finals, or when a keyframe doubles as a static ad. |
| `nano_banana_2`, `seedream_v4_5`, `seedream_v5_lite` | yes | Alternates when elements are needed. |

**Check before choosing.** Reference elements (`show_reference_elements`) work only on
the models marked yes. Picking `seedream_v5_pro` on a run with a packshot silently
loses the packshot — or fails.

## Video — scene animation

| Model | Duration | Res | Key media roles | Use for |
| --- | ---: | --- | --- | --- |
| `minimax_h3` | 4–15s | 2K | `start_image`, `end_image` | **Default for finals.** Start+end keyframes give real control of the motion inside a scene. |
| `gemini_omni` | 4–10s | 720p | `image_references` | **Draft tier.** Cheap, and the only video model here supporting free-trial unlim. |
| `flux_3_video` | 5–20s | 1080p | `start_image`, `end_image` | Storyboard-tagged, good continuity. Second choice for finals. |
| `seedance_2_5` | 4–30s | 1080p | `omni_reference`, `start`/`end` | Long scenes only. Set `generate_audio:false`. |
| `grok_video_v15` | **2–15s** | 1080p | `start_image` | The only model that renders under 4s natively. |

## Two-tier rendering

Video is the dominant cost in a run. Rough it cheap, finish it properly.

1. **Draft pass** — `gemini_omni` at 720p across every scene. Confirms the beat plan
   reads, the motion ideas work, and the cut has rhythm. A whole ad drafted here costs
   a fraction of one finished scene.
2. **Final pass** — re-render approved scenes on `minimax_h3` at 2K.

Skip the draft only for a short ad, a repeat format, or a brand who has already
signed off the same beat plan in another style.

## Known API constraints

Learned by hitting them. All produce clean rejections without charging.

- **`minimax_h3`: `start_image`/`end_image` cannot be mixed with `image_references`.**
  422. Not a problem — the keyframe already carries the locked style, so drop the
  style reference from the video call and keep the keyframes.
- **Preset interception.** A video batch can return `submission_failed` with a preset
  recommendation instead of jobs. Nothing charged. Pass `declined_preset_id` on every
  request and resubmit.
- **Failed jobs do not charge.** Two consecutive failures on one scene usually means
  the prompt is internally impossible — a small move asked to produce a large framing
  change — not that the API is flaky. Run the impossibility check in `scene-renderer`
  before blaming the model. Then enlarge the move, shrink the framing change, split
  the beat, or animate locally.

## What comes back

- `minimax_h3` returns **1440x2560 at 24fps**, about **1.17s longer than requested**
  (a 5s request yields ~5.17s). That surplus is free trim headroom — record it.
- **Clips carry an AAC track even with no audio requested.** Strip it with `-an`.
- Because every clip is natively 24fps, **normalize the run to 24fps**, not 30.
  Resampling 24→30 duplicates every fourth frame and judders smooth camera pushes.

## The minimum-duration trap

Most models floor at 4s (`minimax_h3`, `seedance_2_5`, `gemini_omni`) or 5s
(`flux_3_video`). A HOOK beat is 3s.

**Generate at the model's minimum, then trim to the exact beat length locally.** Never
round a beat up to the model minimum — a 3s hook stretched to 4s wrecks the pacing
that makes it a hook. Trim from the tail, keeping frame 1.

Use `grok_video_v15` when a beat is under 3s and the trim costs too much motion.

## Audio

Do **not** use the video models' native audio. `generate_audio:false` wherever the
parameter exists. Voice comes from ElevenLabs — see `narration`.

## Cost discipline

**Quote the cost before every paid step and wait for a yes.** See the gate table in
the director skill.

1. **Narrate before you animate.** A timing error found in audio costs cents.
2. **Draft tier before finals.**
3. **Keyframe before clip.** An image regeneration is a fraction of a video one, and
   most bad scenes are already visible in the still.
4. **Regenerate one scene, never the run.** Freeze accepted indices.
5. **Reuse narration across style variants.** Identical audio, no reason to re-spend.

Never pass `use_unlim` unless the user explicitly asks to spend a free-trial
allowance. Pass `use_unlim:false` on batch calls to avoid an `unlim_choice` stall.
