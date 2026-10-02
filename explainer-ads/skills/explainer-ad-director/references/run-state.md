# Run state

Pipeline state lives on disk, not in conversation context. A 9-scene ad involves
dozens of asset IDs and paths; carrying those in context is how a run loses scene 6
and silently ships an 8-scene ad.

## Layout

One directory per ad, under the working directory:

```
explainer-ads/<brand>/<slug>/
├── run.json              # the single source of truth
├── script.txt            # narration text, final, one line per scene
├── keyframes/
│   ├── scene_01.png
│   └── ...
├── clips/
│   ├── scene_01_raw.mp4  # as generated, at model-minimum duration
│   ├── scene_01.mp4      # trimmed to exact beat length
│   └── ...
├── audio/
│   ├── scene_01.mp3      # per-scene narration
│   └── vo.mp3            # concatenated track
├── captions/
│   └── captions.ass
└── out/
    ├── master.mp4        # clean, no burned text
    └── final.mp4         # captions and text burned in
```

`master.mp4` stays clean. Every text variant burns from it, so a caption change
never means re-rendering scenes.

## run.json

```json
{
  "brand": "acme-dental",
  "slug": "implant-cost-hook-a",
  "created": "2026-08-25",
  "duration_target": 30,
  "aspect": "9:16",
  "style": {
    "preset_id": "56fc6472-33b7-45dc-83ff-80c71d40aec6",
    "preset_title": "Editorial Motion Graphics",
    "style_media_id": "<resolved media_id — reused on every scene call>",
    "style_clause": "<the exact style string repeated verbatim in every scene prompt>",
    "palette": ["#0B3C5D", "#F2E8DC", "#D9534F"]
  },
  "voice": {
    "provider": "elevenlabs",
    "voice_id": "<voice_id>",
    "voice_name": "<name>"
  },
  "asset_roster": {
    "characters": [],
    "objects": [
      { "key": "invoice", "description": "<exact wording reused in every prompt>" }
    ],
    "locations": []
  },
  "approved_claims": [],
  "scenes": [
    {
      "index": 1,
      "beat": "HOOK",
      "seconds": 3.0,
      "narration": "Most implant quotes hide three fees.",
      "visual": "A dental invoice with three lines highlighted, snapping into view.",
      "onscreen_text": null,
      "keyframe_job_id": null,
      "keyframe_path": null,
      "keyframe_approved": false,
      "clip_model": "minimax_h3",
      "clip_generated_seconds": 4,
      "clip_job_id": null,
      "clip_path": null,
      "clip_approved": false
    }
  ],
  "status": "planned"
}
```

## Status values

`planned` → `style_locked` → `keyframes_generated` → `keyframes_approved` →
`clips_generated` → `clips_approved` → `narrated` → `assembled` → `delivered`

Write `run.json` after every phase. A run must be resumable from it alone: on
re-entry, read it, find the first phase with incomplete work, and continue from
there rather than starting over.

## Asset roster

Anything appearing in more than one scene goes in the roster with **one fixed
description string**, which is then pasted verbatim into every prompt that needs it.
Re-describing the same object in different words per scene is the main cause of an
object changing between scenes.

## Style clause

`style.style_clause` is the exact text repeated in every scene prompt. Store it once
and copy it — do not regenerate or paraphrase it per scene.

## Batch variants

Style or hook variants of one ad are sibling directories sharing a stem:

```
explainer-ads/acme-dental/implant-cost-hook-a/
explainer-ads/acme-dental/implant-cost-hook-b/
```

Each gets its own `run.json`. Variants testing style only should point
`voice.voice_id` at the same voice and reuse the same `audio/vo.mp3` — copy the
file in rather than regenerating it.
