# Conversion Playbook

## Source Analysis

- PPTX is a zip: inspect `ppt/presentation.xml` for slide size and `ppt/slides/*.xml` for image/text objects.
- If each slide has one full-page image and no text, treat it as flattened.
- Extract slide images from `ppt/media` or render slides if needed.
- Build a contact sheet for multi-slide decks and classify page types visually.

## Page Decision Record

Before rebuilding a slide, create a compact page decision record. This can be a JSON object, a comment block inside the build script, or an entry in a page plan file.

For multi-slide conversion after sample approval, this record is mandatory. Build the full-deck script only after every requested slide has a record. If a slide has not been audited, mark it incomplete and stop rather than filling it with generic approximations.

Required fields:

```json
{
  "slide": 18,
  "page_type": "card-grid",
  "text_policy": {
    "editable_text": ["title", "subtitle", "card titles", "card bodies", "footer"],
    "image_integrated_text": ["logo text or product markings, if any"],
    "ocr_uncertain": []
  },
  "native_shapes": [
    {
      "name": "card frame",
      "must_match": "corner radius, pale blue border, white-to-blue fill, no shadow"
    }
  ],
  "asset_candidates": [
    {
      "name": "large pump icon",
      "role": "card illustration",
      "decision": "crop | registry | image",
      "reason": "clean circular icon crop available / registry match 82% / no clean crop and registry below 70%",
      "registry_candidate": "pump_badge_blue",
      "similarity_estimate": 82
    }
  ],
  "no_new_image_assets_required": false,
  "notes": "Text overlays will be restored as editable text boxes last."
}
```

This record prevents the failed shortcut of using whatever icon exists in the registry. The visual decision must be made per slide.

### Required Asset Decision Chain

For every non-text visual element, decide in this order and record the outcome:

1. **Clean crop**: Use only when the crop is complete, independent, sharp, and free of editable overlay text or neighboring elements.
2. **Registry reuse**: If a clean crop is not possible, search the registry and estimate similarity. Reuse only at about 70% or higher.
3. **Image generation**: If registry similarity is below about 70%, or if text must be removed from a complex visual element, regenerate/redraw the complete no-text element with image generation.
4. **Native shape**: Allowed only for simple geometry that can be matched faithfully. Record why this is acceptable, including color, corner radius, line weight, fill, shadow/glow, arrowhead, dash pattern, or table grid expectations.

Do not skip this chain because a page resembles an approved sample. The sample approves general style, not per-page asset choices.

### Registry Similarity Audit

When reusing an element-registry asset, record:

- `registry_candidate`;
- `similarity_estimate`;
- `similarity_basis`: silhouette, color/gradient, line weight, badge/background, orientation, crop, and target display size;
- `reuse_limits`: allowed scale range or pages where it can be reused safely.

If this information is absent, treat the asset as unaudited and do not reuse it in final output.

### Native Shape Audit

When choosing `native_shape`, record:

- what original element is being replaced by native shapes;
- why the element is simple enough for faithful shape recreation;
- expected fill, border, corner radius, shadow/glow, arrowhead, dash pattern, or table grid style;
- whether the user has previously accepted this class of element as editable geometry.

If a card, table, flow, arrow, or icon has gradients, irregular hand-drawn lines, complex shadows, or visual details that native shapes cannot match, it belongs in the crop/registry/image chain instead.

## Text Classification

The key decision is whether text is an overlay that should become editable text, or part of a visual object that should stay in the image.

Treat as editable text:

- slide titles and subtitles;
- body copy, bullets, table text, labels, card titles, card numbers, tags, footer slogans, page numbers;
- chart labels or callout text when the chart/card/table structure is being rebuilt.

Treat as image-integrated text:

- logos, seals, official marks, product-side printing, device labels, UI screenshots, photo signage;
- tiny text that is part of a product render or a complex diagram and cannot be separated without changing the visual identity;
- decorative typography that the user accepts as part of a retained local image element.

If uncertain, do not force the text into a floating PPT text box. Preserve it inside the visual element and report it.

## Native Shape Fidelity

When native shapes are used, visual fidelity matters. Match:

- corner radius, including whether cards are square, softly rounded, or pill-shaped;
- border color, thickness, opacity, double-border effects, and whether the border is continuous or interrupted;
- internal fill color, transparency, gradients, and whether the card reads as white, pale blue, or glassy;
- header strip shape, tab shape, badge overlap, and whether the tab protrudes from the card;
- line cap style, arrowhead shape, line width, dash pattern, and connector spacing;
- shadow/glow strength and whether the original has no shadow.

If these cannot be matched with simple PPT shapes without obvious drift, move that visual into the asset pipeline.

## Sample-First Rule

Always create one sample slide before full conversion. The sample should demonstrate:

- background reconstruction;
- complete visual element treatment;
- editable text placement;
- object layering;
- asset clarity.

Deliver the sample as `editable_output_pageN.pptx` and wait for user approval.

## Backgrounds

Use one clean full-slide background per page type. For generated backgrounds:

- no text;
- no icons/cards/charts/products unless they are part of background-only decoration;
- leave title/content areas clean;
- keep the deck's palette and visual rhythm.

Backgrounds may be reused across page types to reduce drift.

## Complete Element Strategy

Do not rely on generic connected-component splitting. It breaks coherent graphics.

Better strategies:

- Manually identify semantic regions from the reference page: card, table, chart, diagram, main product image, bottom callout, side panel.
- Create a no-text version of each semantic region as one image by sending the original slide or element crop to gpt-image as the reference.
- For generated/regenerated assets, output at 4x display pixel size and insert at normal display size.
- Local crops are allowed as references for gpt-image, but not as final no-text assets when they contain text or local cleanup artifacts.
- If text removal would require fill/blur/clone/patch遮挡, do not do it locally; regenerate the whole element with gpt-image.

Preferred final approach after iteration:

1. Rebuild each page from semantic complete elements, not arbitrary fragments.
2. For every element that originally contains text, build the full no-text background pattern first.
3. Add decorative/text containers as PPT shapes over the full pattern only if they are meant to be editable/selectable.
4. Add all text last as editable text boxes.
5. Verify the visual element is continuous before checking text alignment.

## Crop, Registry, Or Image Generation Decision

Use this order for every non-text visual element that is not a simple native shape.

Important lesson from failed conversions: do not start with "what can I draw quickly?" Start with "what non-text visual elements exist, and which path does each one require?" A quick native-shape rebuild without the asset decision record is only a rough draft.

### 1. Try clean crop from original slide

Use a direct crop as the final element only if all are true:

- the complete element is visible in the crop;
- the crop does not include editable overlay text, neighboring icons, card borders, table lines, or unrelated decoration;
- the element boundary is simple enough for clean alpha masking, usually square/circle/isolated object;
- the crop remains sharp at final display size;
- any baked text in the crop is truly image-integrated, such as logo/product markings.

Typical clean crops:

- round icon badges on card pages;
- square or circular large illustrations;
- official logo/seal;
- complete product/device object;
- isolated chain link/target badge/decorative medallion.

Do not use direct crop when it captures broken card chrome, nearby text, or incomplete shadows. A dirty crop is worse than regenerating.

### 2. Search element registry

Search `outputs/element_registry/element_registry.json` by tags, visual description, source slide, and display size.

Estimate similarity manually from the reference slide:

- silhouette/composition: 30 points;
- color/gradient/badge background: 20 points;
- line weight/stroke style/shadow/glow: 20 points;
- orientation/crop/proportions: 15 points;
- sharpness at target size: 15 points.

Reuse only when the total is roughly 70 or higher. A concept match is not enough. For example, a generic shield is not a match for a shield-with-lightning badge unless the badge background, line style, and internal icon are also close.

If the score is below 70, do not use the asset as a placeholder in a final deck. Generate/redraw the correct element or leave the slide incomplete and report the missing asset.

### 3. Generate/redraw with image generation

Use image generation when:

- no clean crop exists;
- registry similarity is below about 70%;
- the element has complex illustration style that cannot be reproduced by native shapes;
- text must be removed from a complex object without breaking visual continuity;
- the user explicitly prioritizes original-like visual fidelity.

The prompt must describe the specific source element, not just its generic name.

## High-Fidelity Image Element Mode

When the user rejects simplified shape redraws and asks for original-like image elements:

- Treat card chrome, table grids, arrows, flow lines, icon groups, and decorative structures as visual assets, not PPT shapes.
- Regenerate every complete no-text element with gpt-image from the original slide image or element crop. Keep gradients, shadows, line weights, borders, connector continuity, icon silhouettes, and product/device completeness.
- Place those no-text visual regions at exact original coordinates.
- Overlay editable text last.
- Do not replace original visual chrome with generic PowerPoint rectangles, lines, or simplified icons.
- Product/device visuals must be complete visible objects from the original composition. Use a larger crop or whole object extraction instead of tight partial crops.
- A full content-area image layer is not acceptable as a substitute for per-element reconstruction. Each card, table, flow, arrow, icon group, banner, and product/device element must be handled separately.
- Do not use local fill, blur, clone, smudge, background subtraction, or transparency-difference tricks to remove text.

## Per-Page Transparent Element Sheet Mode

Use this optimized mode when there are many icons/images on a page and image generation calls are limited.

### Decision Rules

Use PPT-native shapes for simple, mostly single-color geometry:

- card frames, rounded rectangles, pills, tabs, dividers;
- simple table grids and cell fills;
- straight connector lines, dashed lines, simple arrows;
- footer page-number blocks and simple page chrome.

Use the per-page element sheet for visual details that are expensive or risky to redraw with shapes:

- icons and icon badges;
- products, devices, compressor images, vehicles, photos, renders;
- complex glossy chains, target icons, seals, circular tech halos, decorative badges;
- any object whose silhouette or rendering style must closely match the original.

### Sheet Generation

For each slide or up to 4-slide batch:

1. Inspect the original slide and list all visual elements that should go on the sheet.
2. Exclude all text and numbers from the sheet.
3. Exclude slides where all assets are clean crops or registry matches; mark them as `no_new_image_assets_required`.
4. Ask gpt-image to generate a single transparent PNG sheet containing only missing/new elements.
4. Arrange elements in a clean grid, separated by generous transparent padding.
5. Require no overlap, no touching, no shared shadows, no background panels, no labels, and no watermark.
6. For image-generation efficiency, batch at most 4 slides per sheet request, excluding `no_new_image_assets_required` slides.
7. Save the generated sheet as `slides_XX_YY_element_sheet.png` or `slideXX_element_sheet.png`.

Prompt template:

```text
Use the provided slide image as the visual reference.
Create one transparent PNG element sheet for slide(s) <N...>.

Include only these non-text visual elements:
Slide <N>:
1. <element name and visual description>
2. <element name and visual description>

Slide <M>:
1. <element name and visual description>
...

Do not include any text, numbers, labels, captions, or watermark.
Do not include card frames, table grids, or simple lines if those will be rebuilt with PPT shapes.
Place every element separately on a fully transparent background.
Arrange the elements in a neat grid with large transparent gaps between them.
Elements must not overlap, touch, intersect, or cast shadows onto each other.
Preserve each element's original icon style, color, gradient, gloss, shadow, silhouette, and proportions from the reference slide.
Output should be a high-resolution PNG with true alpha transparency.
```

### Sheet Splitting

After generation:

- Split the element sheet into separate elements using alpha connected components or manually defined crop boxes.
- Save each element as `slideXX_element_<name>.png`.
- Validate every split:
  - transparent corners;
  - complete silhouette;
  - no clipped glow/shadow;
  - no neighboring element pixels;
  - no text artifacts;
  - enough resolution for final placement.
- If the image tool bakes a checkerboard into RGB, remove only the outer checkerboard and validate alpha before splitting.

### PPT Reconstruction

For each slide:

1. Add the clean background.
2. Add PPT-native simple shapes for frames, grids, connector lines, simple arrows, and tabs.
3. Add split image elements from the sheet at exact page-specific coordinates.
4. Add editable text boxes last.

This mode reduces gpt-image calls while avoiding the failed shortcuts of one large content layer, local text fill, blur, or background subtraction.

## Shared Element Registry

For deck-level conversion, keep a reusable registry of all generated/split elements. This prevents repeated image generation for the same icon or decorative object.

Recommended folder:

```text
outputs/element_registry/
  element_registry.json
  assets/
    warning_badge_red_triangle.png
    shield_check_badge.png
    target_icon_blue.png
```

Recommended JSON item:

```json
{
  "id": "warning_badge_red_triangle",
  "path": "outputs/element_registry/assets/warning_badge_red_triangle.png",
  "source_slide": 6,
  "source_asset": "outputs/page6_element_sheet/processed/p6_warning_badge.png",
  "description": "Pale blue circular badge with red rounded warning triangle and white exclamation mark.",
  "tags": ["warning", "badge", "red", "circle"],
  "original_bbox_px": [112, 333, 230, 451],
  "recommended_display_px": [118, 118],
  "alpha_validated": true,
  "text_free": true,
  "reuse_notes": "Reuse where the same warning badge style appears; scale between 80% and 130% preferred."
}
```

Before generating a new slide element sheet:

1. List the slide's non-text visual elements.
2. Search `element_registry.json` for matching tags and descriptions.
3. Compare style using the 70% similarity rule: silhouette, fill/line colors, gradient, shadow, orientation, badge shape, and expected size.
4. Reuse registered elements only when the score is high enough.
5. Put only missing/new visual elements into the gpt-image element sheet prompt.
6. After splitting new elements, add them to the registry.
7. In the conversion report, list reused assets and newly generated assets.

Reuse is allowed when:

- the element has the same icon composition and visual style;
- the target page only needs scale/position changes;
- the registry asset remains sharp at the required size;
- the alpha channel and transparent padding are clean.

Regenerate instead when:

- the same concept has a different icon shape or badge style;
- color, line weight, gloss, halo, or shadow differs materially;
- a product/device is shown from a different angle or crop;
- scaling would make the asset blurry or jagged;
- the existing asset contains artifacts from prior cleanup.

## Modular Scripts

This skill includes scripts for repeated work. Run them from the current project workspace.

### `scripts/element_registry.py`

Use to inspect and maintain `outputs/element_registry/element_registry.json`.

Common commands:

```powershell
python <skill>/scripts/element_registry.py list --workspace .
python <skill>/scripts/element_registry.py search --workspace . --tags shield,badge
python <skill>/scripts/element_registry.py add --workspace . --id target_badge_blue --path outputs/element_registry/assets/target.png --tags target,badge,blue --description "Blue circular target badge"
```

### `scripts/split_transparent_sheet.py`

Use after image generation returns a transparent asset sheet.

```powershell
python <skill>/scripts/split_transparent_sheet.py --sheet outputs/page18/assets/sheet.png --out outputs/page18/processed --prefix p18
```

It uses alpha connected components, padding, and minimum size filters. Validate the output visually after splitting.

### `scripts/build_element_sheet_prompt.py`

Use a page asset plan JSON to generate image prompts in 4-page batches while skipping slides marked `no_new_image_assets_required`.

```powershell
python <skill>/scripts/build_element_sheet_prompt.py --plan outputs/asset_plan.json --out outputs/element_sheet_prompts
```

The plan should list only missing/new assets after crop and registry decisions.

## Text Treatment

- OCR text and locate bounding boxes.
- Use editable text boxes for titles, labels, body, numbers, table text, chart labels, footers, and page numbers.
- Match approximate font family, weight, size, color, and alignment.
- Use integer point sizes only. Round OCR/visual estimates to the nearest integer and adjust by integer steps.
- Classify each multi-line text box before building:
  - `explicit_source` when the original visibly uses a deliberate hard break;
  - `intentional_layout` when the break is a deliberate visual layout choice;
  - `wrap_by_box` when the text only wraps because the textbox is narrow;
  - `manual_after_visual_check` when a hard break was inserted after visual inspection.
- For `wrap_by_box`, keep the text string continuous and let PowerPoint wrap it; do not insert fake `\n` line breaks.
- Place text last so it remains selectable.
- Add notes for OCR-uncertain text: `需人工校对`.

## Tables And Diagrams

For table pages:

- If the grid and icons are decorative and hard to recreate, create a complete no-text table image and overlay editable text.
- If the table is simple and user needs cell editing, use PPT-native table only when it will not reduce fidelity too much.

For diagrams:

- Make the continuous background pattern first, without labels or text boxes.
- Add labels/text boxes as PPT shapes/text over the pattern.
- Never bake label-box holes into the diagram image if it breaks rings, connectors, or arrows.

For circular/process diagrams:

- Draw the complete rings, connectors, orbit lines, nodes, arrows, and icons first.
- Keep the center/labels empty or lightly transparent, but do not erase the underlying ring structure.
- Use PPT-native label boxes above the pattern if the reference has boxes around text.
- If the original has a complete decorative pattern behind text, preserve that pattern even when text is removed.

## Asset Quality

- Minimum generated element quality: 2x display size; prefer 4x for icons, cards, tables, panels, and diagrams.
- Use transparent PNG for non-rectangular or overlay elements.
- Reuse repeated assets and icons within the deck.
- Place larger visual elements behind smaller ones and text.
- Each generated element must be text-free. Text is always restored as editable PPT text.

## Icon Redraw Brief Template

Before redrawing an icon or asking an image model to regenerate it, write a compact visual brief from the original slide. Keep this brief beside the page-specific coordinates.

Template:

```text
Element:
Reference position:
Geometry:
Style:
Composition:
Must match:
May approximate:
Text handling:
Output:
```

Example:

```text
Element: Page 4 input-voltage lightning icon.
Reference position: first KPI card, left circular badge, centered vertically.
Geometry: single solid lightning bolt, sharp zigzag, long upper diagonal, narrower lower tail, no outline.
Style: deep cobalt blue fill, soft pale-blue circular badge behind it, subtle glow/shadow, transparent outer background.
Composition: icon occupies about 55% of badge height, centered with generous padding, no clipping.
Must match: bolt direction, sharp angular silhouette, blue tone, circular badge scale.
May approximate: exact glow softness.
Text handling: no text in icon.
Output: transparent PNG at 4x display size.
```

Reject/redraw an asset when:

- the silhouette differs from the original at thumbnail size;
- stroke weight or fill/outline relationship changes the icon style;
- the icon is cropped, incomplete, or visually off-center;
- the raster edge looks jagged after insertion into PPT;
- regenerated decoration conflicts with text boxes or card borders.
- any text-removal trace remains, including flat fill patches, cloudy blur, cloned smears, broken gradients, or missing line segments.

## Reports

For final conversion, create a short conversion report:

- source file and output file;
- page count and ratio;
- asset decision record path;
- confirmation that every requested slide has a per-element decision record;
- what is editable;
- which elements remain images and why;
- which registry assets were reused, with similarity estimates;
- which elements required image generation;
- PPTX integrity validation result;
- optional renderer/open validation result only when requested or used for troubleshooting;
- OCR warnings.

## Common Failure Modes

- Splitting one complete graphic into many fragments: avoid by semantic region extraction.
- Low-resolution generated icons causing jagged edges: draw/generate at 4x.
- Generated elements drifting from the original: give gpt-image the original slide/element crop as direct reference and regenerate the specific element again.
- Text baked into images: remove or redraw text and overlay editable text.
- Diagram patterns broken by text boxes: generate complete pattern first, then overlay PPT text boxes.
- Local text cleanup artifacts: never ship; regenerate the element with gpt-image instead.
- PowerPoint repair prompt reported by user or renderer: treat as a blocking defect, even if ZIP/XML parsing passes.
- Negative shape dimensions in slide XML: avoid lines or shapes with negative width/height; reverse the start point and use positive dimensions.
- Fragile preset shapes such as `arc`: replace with stable lines/freeforms when they cause repair prompts or compatibility warnings.
- Missing local media references in build scripts: validate all image paths before generation; deleted output folders can leave scripts pointing at nonexistent files.

Lessons From Revisions

- A fast “OCR + transparent non-text layer” pass is useful only for rough drafts. It is not acceptable as the final method when the user asks for complete independent elements.
- Connected-component extraction often destroys meaning: one table/card/diagram can become dozens of pieces. Prefer manual semantic regions or scripted redraw templates.
- Repainting, local filling, blurring, cloning, or patching over text leaves visible blocks and cuts through decorative graphics. It is prohibited for final assets; use gpt-image regeneration from the original reference instead.
- Original-style icons are safer when drawn as PPT shapes or as high-resolution generated/redrawn assets. Low-res Pillow drawings create obvious jagged edges.
- Reuse accepted pages and assets, but do not reuse a rejected method globally.
- Always state which pages are handcrafted/confirmed and which are batch-redrawn so quality expectations are clear.
- Do not promote a quick full-deck rebuild to "final" when it skipped per-element asset decisions. Label it as a draft, then go back and create the crop/registry/image/native-shape record for every slide.
- Do not infer that an approved sample authorizes generic treatment of all remaining slides. The approved sample authorizes visual direction only; every later slide still needs its own non-text asset audit, similarity checks, coordinates, and layer plan.
- Run package integrity checks before delivery. Renderer preview/export is optional and should be used only when requested or when troubleshooting a reported file-open problem.
- If PowerPoint reports "found a problem with content", inspect slide XML for negative `a:ext` dimensions, unsupported/fragile preset shapes, and missing media relationships; fix the generation script, then regenerate the PPTX rather than relying on PowerPoint's repair-save result.
