---
name: ppt-image-to-editable
description: Convert image-only or AI-generated PPTX decks into editable PowerPoint files by reconstructing backgrounds, full visual elements, shapes, and editable text. Use when a PPT has flattened slide images and the user wants text, tables, cards, icons, charts, and diagrams made editable or partially editable. Always produce one sample slide first and wait for user approval before converting the whole deck.
metadata:
  short-description: Image-only PPT to editable PPT, sample first
---

# PPT Image To Editable

Use this skill for flattened/image-only PPTX conversion. The goal is not a lazy screenshot clone; it is a visually close editable deck where text and simple PPT structures are selectable, and complex visual elements are complete high-resolution local images or complete redrawn element groups.

## Required Workflow

1. Inspect the source PPTX:
   - detect slide size and page count;
   - confirm whether slides are flattened images;
   - render or extract slide PNGs;
   - create a contact sheet if converting more than one page.
2. Classify page types:
   - cover, title/chapter, directory, content/card, table, flow/process, chart/data, photo/product-heavy.
3. Generate exactly one sample slide first:
   - choose the page requested by the user, or the first representative page;
   - output a standalone `editable_output_pageN.pptx`;
   - report object counts and what is editable;
   - stop and ask for approval before batch conversion.
4. After approval, convert the full deck using the accepted style and extraction rules.

## Mandatory Asset Audit Gate

After the sample is approved, do not jump directly from the sample style to full-deck reconstruction. Before writing or running the batch build script, create an asset decision record for every requested slide.

This gate is mandatory even when the slide looks simple:

- List every non-text visual element that is not purely page chrome: product photos, icons, icon badges, card illustrations, diagrams, arrows, decorative groups, tables/charts treated as images, logos, seals, placeholders, and complex card/table/flow chrome.
- For each element, record the decision chain in this exact order:
  1. `crop`: Can the element be cleanly cropped from the original slide as a complete independent element?
  2. `registry`: If not, is there an element-registry match with estimated similarity about 70% or higher?
  3. `image`: If not, regenerate/redraw it with image generation.
- Record the reason for the chosen decision, the crop box or registry candidate when applicable, and an estimated similarity score for any registry reuse.
- If an element is reproduced with native PPT shapes instead of crop/registry/image, explicitly mark it as `native_shape` and state why the geometry is simple enough to match faithfully.
- Slides with no missing/generated assets may be marked `no_new_image_assets_required`, but only after the element list proves every required asset is either a clean crop, a high-similarity registry reuse, or a faithful native shape.
- Stop and create/update the asset plan before converting if any slide lacks this record.

Do not treat a previous sample, a generic icon name, or an existing batch script as permission to skip this audit. A full-deck output without this per-element decision record is a draft, not a completed conversion.

## Current Conversion Logic

For each slide, first inspect the rendered slide image and make a page-level decision record before building PPT objects.

1. **Text classification**
   - Text visually overlaid on cards, tables, callouts, labels, titles, subtitles, footers, and page numbers becomes editable PPT text.
   - Text that is part of a product photo, logo, seal, screenshot, printed device label, or image pattern stays inside that image element. Do not force it into a text box.
   - When unsure, preserve image-integrated text inside the element and note it in the report; do not create floating editable text that changes the object identity.
2. **Shape fidelity**
   - When redrawing cards, tabs, pills, tables, callouts, and boxes with PPT-native shapes, match not only color but also corner radius, border thickness, border color, internal fill, transparency, shadows/glow, and header strip geometry.
   - If the original frame has nonstandard gradients, glass effects, complex shadows, double borders, or decorative breaks, treat it as a visual element instead of a generic shape.
3. **Asset need decision**
   - For every non-text visual element that cannot be faithfully reproduced with simple shapes, decide in this order:
     1. Can it be cleanly cropped from the original slide as a complete independent element?
     2. If not, does a registry asset match at about 70%+ similarity in silhouette, color, style, badge/background, orientation, and required size?
     3. If no suitable match exists, generate/redraw it with image generation.
   - Similarity below roughly 70% means regenerate; do not use an unrelated icon just because the concept name matches.
4. **Per-page/batched image generation**
   - Exclude slides with no new assets needed from image generation.
   - For remaining slides, batch up to 4 slides per image-generation request by creating a transparent element sheet containing only the new non-text visual assets for those slides.
   - Keep assets separated, with transparent padding and no labels/numbers.
5. **Reconstruction**
   - Add clean page background.
   - Add native shapes for simple faithful geometry.
   - Add cropped/reused/generated image elements, large elements first.
   - Add editable text last.

Use `references/conversion-playbook.md` for detailed implementation rules and use the bundled scripts when possible.

## Page-By-Page Custom Reconstruction

When the user requests high fidelity conversion, every requested slide must be handled as a custom page. This is a hard requirement.

- Look at the original slide image before writing code for that page.
- Split only complete semantic elements: cards, whole diagrams, whole icon groups, tables, charts, product images, banners, and connected patterns. Do not use arbitrary connected-component fragments.
- Write page-specific coordinates, font sizes, element dimensions, layer order, and asset filenames in a dedicated script or dedicated page section.
- Manually correct text content, font size, line breaks, and placement against the original image or a trusted editable source. OCR is only a hint and must not be copied blindly.
- Fix jagged assets by regenerating or rasterizing at 2x-4x display size before placing them in PowerPoint.
- Before redrawing icons or decorative raster elements, write a short visual specification from the original slide. The specification must describe the element before invoking image generation or drawing code.
- For text over patterned elements, first create or redraw the complete no-text pattern, then place editable text boxes last. Do not hide old text with patches that damage the pattern.
- Batch scripts may only assemble already-customized page definitions. They must not generically redraw all slides from OCR/components.
- If a page is not yet custom-tuned, mark it incomplete rather than filling it with generic approximations.

## Cropping, Reuse, Or Regenerate

For each visual asset candidate:

- **Clean crop is allowed** when the element is already complete, independent, high-resolution, and does not include editable overlay text or neighboring strokes. Typical examples: square/circular large icons, product photos, seals, logos, clean badges.
- **Do not crop** when the crop would include card borders, nearby text, broken shadows, overlapping elements, or partial icons. Use registry search or image generation instead.
- **Registry reuse is allowed** only when visual similarity is high enough: same silhouette, same badge shape/background, similar line weight, same color family, same rendering style, and acceptable sharpness at target size.
- **Regenerate with image generation** when similarity is below about 70%, when a complex icon has no clean crop, or when the object is complete but contains removable overlay text.

Slides whose required assets are all clean crops or registry matches are marked as `no_new_image_assets_required` and should not consume image-generation calls.

## Icon And Element Redraw Brief

For every non-text icon, symbol, or decorative element that must be redrawn or regenerated, first create a brief with these fields:

- Element role and page location: e.g. "page 4, first KPI card, lightning icon".
- Original geometry: outline shape, internal strokes, angle, proportions, negative space, and whether corners are sharp/rounded.
- Style: flat/gradient, line width, fill color, shadow, glow, transparency, background circle, border, and highlight direction.
- Composition: icon size relative to its card, center alignment, padding, nearby text clearance, and any cropping.
- Fidelity constraints: what must match exactly and what may be approximate.
- Text handling: confirm the element contains no baked-in text, or list which text must be removed and restored as editable PPT text.

Use the brief as the prompt or drawing checklist. Do not generate icons from only generic names such as "gear icon" or "shield icon" when a reference icon exists in the original slide.

## Layer Order

For each reconstructed page:

1. Full-slide clean background image for that page type.
2. Complete no-text visual elements extracted or regenerated from the original page, ordered back-to-front by size.
3. PPT-native shapes only for elements the user has accepted as editable geometry, or for tiny labels/page chrome where fidelity is not affected.
4. Editable text boxes on top, always last.

Do not use the original full slide screenshot as the final background except as a temporary analysis source.

## Element Rules

- Treat a semantic visual as one complete element. Do not split a card, table, diagram, product image, chart, or repeated decoration into fragments.
- If an element has no text, use it directly as a complete image element only when it is already complete and clean. Otherwise regenerate it with gpt-image from the original slide reference as one complete high-resolution image.
- If an element contains text:
  - first use gpt-image with the original slide or element crop as reference to regenerate a no-text version of the full element;
  - preserve complete background patterns, rings, icons, grids, gradients, connectors, arrows, charts, and decoration;
  - never bake holes, label boxes, blur blocks, fill patches, or text-removal patches into the image;
  - add all text back as editable PowerPoint text boxes after every image and shape layer.
- For repeated elements, create once and reuse.
- Draw generated/raster element assets at 2x-4x display resolution to avoid jagged icons.
- When the user prioritizes visual fidelity over shape editability, card backgrounds, lines, flow structures, table grids, icons, decorations, and product/device visuals must be complete raster elements regenerated with gpt-image from the original slide reference, with all text removed, then overlaid with editable text. Do not simplify them into generic PPT shapes.

## Bundled Scripts

Prefer these scripts instead of rewriting utility code:

- `scripts/element_registry.py`: list/search/add registry assets and keep `outputs/element_registry/element_registry.json` consistent.
- `scripts/split_transparent_sheet.py`: split a transparent element sheet into alpha-connected PNG elements, with padding and minimum-size filters.
- `scripts/build_element_sheet_prompt.py`: read a slide asset plan JSON and emit batched image-generation prompts for up to 4 slides at a time, skipping `no_new_image_assets_required` slides.
- `scripts/validate_asset_decision_plan.py`: validate that every requested slide has a per-element decision record and that crop/registry/image/native-shape decisions include required evidence.
- `scripts/validate_layout_plan.py`: validate per-page text, native shape, arrow, rounded-corner, and geometry records before building PPTX.
- `scripts/validate_media_refs.py`: check PPT build scripts for referenced images that no longer exist in the current workspace.
- `scripts/validate_pptx_integrity.py`: inspect the generated PPTX package for XML errors, missing relationships/media, negative shape dimensions, and compatibility warnings that can trigger PowerPoint repair prompts.
- `scripts/pptx_object_helpers.js`: reusable pptxgenjs helpers for integer text sizing, line-break policy, positive arrow geometry, arrow presets, and rounded-corner ratio conversion.

The scripts are helpers, not substitutes for judgment. The agent must still inspect each page image, classify text vs image-integrated content, and decide crop/reuse/regenerate per element.

Before full-deck conversion, run the validator against the asset decision plan, for example:

```bash
python scripts/validate_asset_decision_plan.py outputs/asset_decision_plan.json --slides 1-25
```

If validation fails, fix the plan or missing assets before generating the final PPT.

Before building each requested page, create a page-specific layout plan and validate it, for example:

```bash
python scripts/validate_layout_plan.py outputs/page_layout_plan.json --strict
```

The layout plan must record text boxes, integer font sizes, line-break policy, arrow kind, rounded-corner radius, native shape fidelity metadata, and layer order.

Before running the build script, validate local media references when the script names image files directly, for example:

```bash
python scripts/validate_media_refs.py build_deck.js --root outputs/assets --root outputs/element_registry/assets
```

After generating the PPTX, validate the package:

```bash
python scripts/validate_pptx_integrity.py editable_output.pptx --strict
```

## Hard Prohibitions

- Do not batch-convert a deck after sample approval until every requested slide has a per-element asset decision record.
- Do not assume sample-page reconstruction rules apply to every page. Each page still needs its own element list, crop/registry/image decisions, coordinates, and layer plan.
- Do not use registry assets without a recorded similarity estimate. Concept match alone is insufficient; below roughly 70% similarity, regenerate with image generation.
- Do not use an old batch transparent visual layer as a shortcut after the user has approved a complete-element/redraw approach.
- Do not split a single coherent card, chart, table, diagram, circular management graphic, or callout into many image fragments.
- Do not put text inside element images unless the user explicitly accepts non-editable text.
- Do not remove text by covering it with opaque rectangles inside the element image when that breaks rings, grids, arrows, or decorative continuity.
- Do not remove text with local fill, blur, smudge, clone, or patch遮挡. Text removal must be done by gpt-image regenerating a clean no-text element from the original reference.
- Do not ship jagged low-resolution icon/card images; redraw at 4x when in doubt.
- Do not replace original icons, card chrome, table grids, arrows, or decorative shapes with simplified lookalike shapes when the user asks for image-based extraction/regeneration.
- Do not crop product/device visuals so tightly that the visible object is incomplete. Preserve the complete visible object as one semantic element.
- Do not create lines or shapes with negative width/height in generated PPTX XML. If a line needs to go left/up, change the start point and use positive dimensions.
- Do not rely on fragile or poorly supported preset shapes such as `arc` when a stable line/freeform approximation will do.
- Do not reference media from directories that may have been deleted or renamed. Missing images must be caught before generation.
- Do not use fractional font sizes. Reproduced text must use integer point sizes.
- Do not insert hard line breaks to imitate visual wrapping unless the line break is classified as source-explicit or intentionally placed after visual inspection.
- Do not use a generic arrow shape when the source uses a specific arrow family, head style, cap, dash, or block/chevron form.
- Do not use default rounded-rectangle corners without measuring or classifying the source corner radius.

## Reusable Object Reconstruction Rules

Use `references/object-reconstruction.md` for object-level rules and keep the relevant metadata in the page layout plan.

- Text boxes: distinguish explicit source line breaks from automatic wrapping caused by textbox width. Use `\n` only for `explicit_source`, `intentional_layout`, or `manual_after_visual_check`; use unbroken text with normal wrapping for `wrap_by_box`. Font size must be an integer.
- Shapes/cards: record fill, border, opacity, shadow, layer, and measured or classified corner radius. Match card roundness, border style, and internal fill before accepting native shapes.
- Arrows/connectors: record `arrow_kind`, stroke, width, cap, dash, direction, and head style. Use line arrows, block arrows, chevrons, curved arrows, and elbow connectors only when they match the original class.
- Rounded corners: estimate radius from the source image and convert to PPT radius using `scripts/pptx_object_helpers.js` when building with pptxgenjs.
- Efficiency: validate asset plans first, then layout plans, then media refs, then PPTX package integrity. Renderer preview/export is optional and should be used only when requested or when troubleshooting a reported file-open problem.

## High-Fidelity Image Element Mode

Use this mode when the user says card/line/flow/table/icon/decorative elements should come from image extraction or should match the original exactly.

- Use the original slide image as the visual reference.
- Identify each complete semantic visual region: card group, table, flow chart, diagram, product/device visual, banner, footer decoration, icon row, and decorative connector group.
- For every element, card frame, icon, arrow, connector, table, chart, banner, and decorative piece, send the original slide or element crop to gpt-image and regenerate a separate no-text image element.
- Keep original icons, gradients, borders, shadows, arrows, table lines, and decorative continuity.
- Remove text through gpt-image regeneration/inpainting only, not by local filling, blurring, or遮挡.
- Place the no-text image element back at the exact original coordinates and size.
- Add all text as editable PPT text boxes last.
- If a product/device appears in the original page, keep the complete visible product/device as one element; do not use a partial crop unless the original itself is visibly cropped by the slide.
- Only use PPT-native shapes for deliberate editable overlays such as newly created text boxes, not for simplifying the original visual chrome.
- Local crops may be used as references/prompts for gpt-image, but should not be used as final no-text assets if they still contain text or local fill/blur artifacts.

### Prohibited Shortcuts In This Mode

- Do not make one large content-area layer and treat it as a substitute for per-element analysis.
- Do not generate transparency by subtracting a clean background from the original slide. This drops low-contrast borders, shadows, connector lines, table grids, and pale decorative elements.
- Do not remove text by blurring OCR boxes over the original image. This creates visible cloudy blocks and destroys nearby icons, card edges, table lines, and product details.
- Do not remove text by drawing local solid-color fills over the original image. This leaves flat blocks and breaks the original gradients/shadows.
- Do not use OCR boxes as the only basis for text removal. Manually inspect every affected element and protect nearby visual strokes before removing text.
- Do not ship a page where text removal leaves blue/gray blur patches, missing borders, broken arrows, incomplete icons, or separated product/device parts.
- If exact extraction cannot preserve a complete element, use gpt-image regeneration on that specific element from the original reference, then verify it visually before building the PPT. Do not fall back to local patching.

## Per-Page Transparent Element Sheet Mode

Use this mode when image generation calls are expensive or limited, but visual fidelity still matters.

Goal: generate at most one gpt-image asset sheet per slide, then split it locally into independent elements.

- Rebuild single-color or simple geometry with PPT-native shapes:
  - card borders and fills when they are simple;
  - table/grid lines;
  - straight/dashed connector lines;
  - arrows with simple flat/gradient shape;
  - simple rounded rectangles, pills, tabs, dividers, and footer chrome.
- Put only visually complex elements onto the per-page element sheet:
  - icons and icon badges;
  - product/device/photos/renderings;
  - complex decorative marks;
  - complex glossy chain links, seals, badges, target symbols, circular tech halos, or illustration-like objects.
- The element sheet must have a fully transparent background.
- Every element on the sheet must have transparent padding around it and must not touch, overlap, intersect, or cast shadows onto another element.
- Arrange elements in a simple grid with enough spacing for reliable local cutting.
- The sheet must contain no text, no numbers, no watermark, and no baked labels.
- After generation, split the sheet into separate transparent PNG elements using bounding boxes or alpha connected components, then place each element back at its page-specific coordinates and size.
- Add all text as editable PPT text boxes last.
- If an element sheet output has a checkerboard background baked into RGB instead of true transparency, convert/remove only the outer background and validate alpha before use.
- Do not use this mode for elements that overlap or need exact inter-element alignment unless the sheet preserves enough transparent spacing for clean separation.

## Shared Element Registry And Reuse

For a full PPT deck, many visual elements repeat. Maintain a reusable element registry so repeated icons and decorative elements are generated once and reused.

- After splitting any gpt-image element sheet, register each reusable element in a project-local manifest, for example `outputs/element_registry/element_registry.json`.
- Store reusable assets in a stable folder such as `outputs/element_registry/assets/`.
- Each registry item should include:
  - stable `id`, e.g. `warning_badge_red_triangle`, `target_icon_blue`, `shield_check_badge`;
  - file path;
  - source slide/page and source crop/reference;
  - visual description;
  - intended display size or original bounding box;
  - tags such as `warning`, `shield`, `target`, `product`, `arrow`, `badge`;
  - whether the element is text-free and alpha-validated;
  - notes about acceptable reuse scale.
- Before generating a new element sheet, inspect the registry and reuse matching elements when the silhouette, color, style, and required size match the current slide.
- Do not regenerate a repeated element only because it appears on a different page.
- Do regenerate when the same concept has a visibly different style, color, orientation, rendering, crop, or icon composition.
- If an element is reused, record that reuse in the slide report or notes.
- Prefer registry reuse for common deck elements: warning badges, shield/check icons, target icons, leaf/snow icons, factory icons, chart/growth icons, gear icons, people/team icons, chain links, product/device cutouts, and recurring footer/decorative badges.

## Token Discipline

Keep context small:

- inspect only the pages being sampled or requested;
- use contact sheets instead of describing every slide in text;
- write scripts for repeated extraction/rebuild work;
- load `references/conversion-playbook.md` only when implementation details are needed.

## Verification

For each sample or final deck, verify:

- page count and slide size;
- package integrity with `scripts/validate_pptx_integrity.py --strict`;
- layout plan with `scripts/validate_layout_plan.py --strict`;
- all build-script media references with `scripts/validate_media_refs.py` when applicable;
- no negative `a:ext cx/cy` dimensions in slide XML;
- number of text, image, and shape objects;
- that the output is not just full-page screenshots;
- that element images are complete and high-resolution;
- that OCR-uncertain text is noted in slide notes or a conversion report.

When the user rejects a sample, update the method before continuing. Do not batch convert using a rejected approach.
