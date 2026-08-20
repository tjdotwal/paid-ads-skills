# JSON prompt architecture for image generation

Image models process JSON-structured prompts more precisely than natural language. Separating visual components into distinct key-value pairs prevents concept bleeding — where colors, textures, or styles leak between elements — and gives reproducible, batch-friendly output.

Three properties make it worth the extra structure:

- **Separation of concerns.** Each key isolates one instruction, so the model processes them independently rather than blending them.
- **Surgical variation.** Swapping a single key (`Background`, `ColorRestriction`) changes that element without disturbing the rest. This is how you get true A/B assets with one controlled variable.
- **Portability.** A template becomes reusable across brands by replacing only the bracketed values.

Written against Nano Banana 2 and models in that family. The key structure carries over to most current image models.

## Key reference

Not every key is required for every ad type. Use what the format demands.

| Key | Purpose |
|---|---|
| `label` | Internal name for the prompt. Use for logging and batch tracking |
| `tags` | High-level keywords anchoring the overall aesthetic and ad type |
| `Style` | Rendering style descriptors (commercial-product-photography, editorial-layout) |
| `Subject` | Main subject(s) — product shots, people, objects. Array for multi-subject scenes |
| `TextOverlay` | All text elements: headlines, CTAs, quotes, benefit lists, step numbers |
| `Background` | Scene setting and background description |
| `ColorRestriction` | Constrains the palette. Prevents rainbow bleed. Critical for brand consistency |
| `Lighting` | Light source, direction, quality, mood |
| `Camera` | Lens focal length, aperture, angle. Controls depth of field and perspective |
| `Arrangement` | Spatial layout — where each element sits in the frame |
| `OutputStyle` | Overall rendering instruction (photorealistic, editorial, meme-authentic) |
| `Mood` | Emotional tone of the final image |
| `meta` | Technical settings: `aspect_ratio` (1:1, 4:5, 9:16, 16:9), `quality`, `seed` |

## Two-stage workflow

**Stage 1 — brand DNA.** In a fresh conversation, have the model research the brand and produce a structured document covering:

1. **Brand identity** — mission, values, voice and tone, personality traits, target audience
2. **Visual identity** — colors with hex codes, typography style, imagery style, aesthetic
3. **Product positioning** — value prop, differentiators, price positioning, hero products
4. **Messaging framework** — tagline, top 5 selling points, objections, emotional triggers
5. **Audience insights** — ideal customer, pain points solved, aspirational identity
6. **Competitive landscape** — primary competitors, differentiation angles

This document stays in context for stage 2. If a `competitor-research` brief already exists for the brand, use it instead — it's deeper and evidence-backed, and this stage is a thinner substitute for it.

**Stage 2 — JSON generation.** In the same conversation, attach 1–3 product images and ask for brand-specific versions of the templates you want. Rules to pass along:

- Maintain the exact JSON structure and keys of each template
- Replace all `[BRACKETED]` placeholders with brand-specific values
- Use the brand's actual hex colors in `ColorRestriction`
- Use the brand's actual voice in all `TextOverlay` copy
- Reference the attached product images where `Subject` calls for product shots
- Keep `meta.aspect_ratio` as specified in the template
- Output each prompt as valid JSON, numbered and labeled, ready to paste

## Worked example

Template 45 (Research Receipt / Journal Screenshot Ad) as a complete JSON prompt:

```json
{
  "label": "[BRAND]-research-receipt-ad",
  "tags": [
    "static-ad",
    "research-citation",
    "journal-screenshot",
    "authority",
    "social-proof",
    "reframe"
  ],
  "Style": [
    "academic-journal-mimicry",
    "credibility-stack-commercial"
  ],
  "Subject": [
    "top panel: a recreated research-journal article block styled to read as a real peer-reviewed paper at first glance",
    "journal masthead [JOURNAL_NAME] with [PUBLISHER] logo, article title, author line, publication date and citation, and a highlighted Result line",
    "bottom panel: a recreated social-media comment from a real customer — avatar, name, comment text, timestamp, reaction count"
  ],
  "TextOverlay": {
    "journal_masthead": "[JOURNAL_NAME] / [PUBLISHER]",
    "article_label": "Research article",
    "study_title": "[VERIFIED_STUDY_TITLE]",
    "authors": "[VERIFIED_AUTHOR_LINE]",
    "pub_meta": "Published: [DATE] • [VERIFIED_JOURNAL_CITATION]",
    "result_label": "Result:",
    "result_text": "[ONE_LINE_FINDING_WITH_VERIFIED_STAT]",
    "result_highlight": "soft highlighter color behind the single key stat line only",
    "reframe_headline": "[REFRAME_LINE_PART_1]",
    "reframe_headline_style": "large bold serif, near-black, centered",
    "reframe_subhead": "[REFRAME_LINE_PART_2]",
    "reframe_subhead_style": "italic serif in [ACCENT_COLOR], centered, directly beneath headline",
    "testimonial_name": "[CUSTOMER_NAME]",
    "testimonial_text": "[REAL_CUSTOMER_COMMENT]",
    "testimonial_meta": "[TIMESTAMP] • Like • Reply, with reaction-count badge"
  },
  "Background": "deep [BRAND_DARK] canvas behind two stacked white rounded-corner cards; subtle blurred texture in the dark margins",
  "ColorRestriction": [
    "[BRAND_DARK] canvas background",
    "white card panels #FFFFFF for journal block and testimonial",
    "near-black #111111 for study title, author line, and reframe headline",
    "[ACCENT_COLOR] for the italic reframe subhead and seal accent",
    "soft pale highlight behind the result stat line",
    "platform-native grays for the testimonial UI text",
    "no additional colors introduced"
  ],
  "Lighting": "flat even editorial lighting; cards sit on the dark canvas with a soft drop shadow for depth",
  "Camera": {
    "lens": "50mm",
    "aperture": "f/8",
    "angle": "straight-on flat composition, screenshot-accurate, no perspective distortion"
  },
  "Arrangement": "vertical three-act stack — journal article card top, bold reframe statement in the gap between cards, customer comment card bottom",
  "OutputStyle": "credibility-stack static ad: an authentic-looking research citation reframes the problem, a bold line lands the new belief, a real customer comment proves it",
  "Mood": "authoritative, credible, reframing, trustworthy",
  "meta": {
    "aspect_ratio": "4:5"
  }
}
```

The bracketed values on a format like this are not free variables. `[VERIFIED_STUDY_TITLE]`, `[VERIFIED_AUTHOR_LINE]`, and `[ONE_LINE_FINDING_WITH_VERIFIED_STAT]` must come from a real paper — see the substantiation gate in `format-detail.md`.

## Technical notes

**`ColorRestriction` is the most powerful key.** It stops the model introducing random colors. Always specify exactly which colors belong where. For a two-tone design, say so explicitly.

**Camera settings control perceived quality.** An 85mm at f/2.0 gives a portrait-quality product shot with natural background blur. A 35mm at f/5.6 gives a flat, informational look. Match the camera to the ad's intent.

**Swap one key at a time for variations.** To create five variations of the same ad, duplicate the JSON and change only `Background` or `ColorRestriction`. That gives A/B assets with controlled variables instead of five unrelated images.

**Aspect ratio lives in `meta`, not the prompt text.** If your generation tool has its own aspect-ratio control, remove `meta.aspect_ratio` and set it in the UI instead. Generating natively, keep it in the JSON.

## Improving the copy

Auto-generated copy from brand research is functional but generic. Three fixes, in order of how much they help:

1. **Run it through `direct-response-copywriter`.** It applies the upstream diagnostic — offer, customer, market sophistication, resistance type, mechanism, big idea — and writes `TextOverlay` copy against it rather than describing the product.
2. **Mine customer reviews.** Pull emotionally resonant language from real reviews and put actual customer words in the headline. `competitor-research` does this systematically.
3. **Manual headline swap.** Before generating, replace `TextOverlay.headline` yourself. The rest of the JSON — layout, lighting, colors — stays identical.

## Capturing a new format

When you see an ad worth replicating: screenshot it, paste the image into a fresh conversation, and ask for a standardized JSON template using the key structure above, with all brand-specific content replaced by `[BRACKETED]` placeholders. Then add it to the library per the "Extending the library" steps in `SKILL.md`.
