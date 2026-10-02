# Animation style catalog

Higgsfield ships a CMS-managed catalog of explainer style presets. Every one is
authored 9:16, which is what we want for Meta and TikTok placements.

## How the style lock works

1. `get_explainer_presets` — list the catalog. Do this at the start of every run;
   it is CMS-managed and changes without notice, so never trust the IDs below
   without a listing call.
2. `resolve_explainer_preset` with the chosen `preset_id` — the backend imports the
   preset's style image into our media storage and returns a **style reference
   `media_id`**.
3. Pass that one `media_id` as an `image_references` media on **every scene
   generation call in the run**.

Step 3 is the whole game. One resolved style reference, reused across every scene,
is what stops the look drifting between scene 2 and scene 7. Resolve once per ad,
store it in run state, never re-resolve mid-run.

## Catalog

IDs current as of 2026-08-25. Re-list to confirm.

### Explainer default — high trust, information-dense
Best for finance, B2B, healthcare, professional services. Reads credible and lets
you put numbers and diagrams on screen without looking childish.

| Style | Preset ID |
| --- | --- |
| Editorial Motion Graphics | `56fc6472-33b7-45dc-83ff-80c71d40aec6` |
| Isometric Flat Vector | `c109eddb-1a79-478a-afd5-273bd0b205e5` |
| Poster Vector | `8014a730-3092-4f3a-b880-0321ae1d207d` |
| 2D Illustrator | `5a1ae304-c541-4f11-9784-595e0f2c3d2b` |
| Pastel Flat 2D | `d0708b4f-a134-40f7-9884-9ad830904e71` |

Editorial Motion Graphics is the house default when the brand has no preference.

### Teaching — walks through a process
Best for MECHANISM-heavy ads and anything where the offer needs explaining before
it can be wanted. Cheap-looking on purpose, which reads as honest rather than
advertised.

| Style | Preset ID |
| --- | --- |
| Whiteboard Doodle | `b347d852-98fc-4013-92b7-6b0219fb21be` |
| Stickman Cartoon | `237dd06c-3729-4895-9672-1c623c4266e0` |
| Hand Drawn | `402635b8-7363-4172-ac78-7ffa9b999c94` |

### Tactile — scroll-stopping texture
Best for HOOK-led ads in crowded feeds. The physical-material look reads as "not an
ad" for the first second, which is what buys the next two.

| Style | Preset ID |
| --- | --- |
| Claymotion | `1de0f39e-c602-4b00-b54a-38440c7f63f7` |
| Paper Diorama | `83d276f6-e3aa-49b8-82f2-1a0bb7d0a370` |
| 3D Papercraft | `bb90786e-fa06-4911-884b-c576dcd20bef` |
| Paper collage | `bc3c6f53-762e-4806-84f0-37a85e278835` |
| Mixed Media | `80e4dd7b-cd65-42d4-b191-b58d62558602` |
| Fluffy Toy | `1fde6c92-721b-4824-b490-4ea75ad0665f` |

### 3D — product-forward
Best when a physical product has to look desirable, or when the brand's brand is
already 3D-rendered.

| Style | Preset ID |
| --- | --- |
| Colorful 3D | `30948d66-76b1-4c8e-884a-1854e08e91df` |
| Studio 3D | `ab43dacd-6bee-4f8e-98b7-c4ff678bfdbd` |
| 3D Mix | `daa250fe-c353-4d26-8ab2-fc1c4ec777a4` |
| Low Poly | `3e4bfd81-fbd8-4587-886d-296cbe48d152` |
| Mannequin | `32356614-40f8-42b2-8a57-2f7b30cfb473` |

### Stylized — use deliberately
Narrow but distinctive. Pixel Art suits gaming and dev tools; the painted looks
suit story-led brand ads more than direct response.

| Style | Preset ID |
| --- | --- |
| Pixel Art | `730d436b-c0d2-4346-a7e9-3d9a80065f30` |
| Watercolor Chronicle | `0029f935-be9e-46c7-a5d8-a4e0f81d49c8` |
| Fairy Tale & Myth | `de5b38ca-9134-4987-9d7a-d5e9085f0480` |

## Style testing

Style is the cheapest variable to A/B and usually the highest-variance one, because
it drives the first-second stop rate. To test it, hold the script, beat plan, and
narration **fixed** and swap only the resolved style reference. Reuse the same
narration audio across style variants — it costs nothing extra and keeps the test
clean.

Sensible first matrix for a new brand: one Explainer-default, one Teaching, one
Tactile. Those three read as genuinely different ads to a viewer, where two picks
from the same group will not.
