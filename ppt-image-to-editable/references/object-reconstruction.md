# Object Reconstruction Rules

Use this reference when rebuilding a flattened slide as editable PPT objects. The
goal is repeatable fidelity: each object type has a decision rule, required
metadata, and a verification step.

## Per-Page Layout Plan

Create a page-specific layout plan before building each slide. It should record:

- slide/page id and pixel size;
- every image asset with source decision: clean crop, registry reuse, image generation, or native shape;
- every text box with exact text, bbox, integer font size, color, weight, alignment, and line-break policy;
- every native shape with fill, border, opacity, corner radius, shadow, and layer;
- every arrow/connector with arrow kind, stroke width, cap, dash, color, and start/end points;
- layer order from background to images/shapes to editable text.

Run `scripts/validate_layout_plan.py` on this plan before generating the PPTX.

## Text Boxes And Line Breaks

First decide why a visual line breaks:

- `explicit_source`: the source has a deliberate hard break, such as a title split, bullet continuation, table row line, or manually arranged label.
- `intentional_layout`: the source likely inserted a break for visual rhythm even if OCR cannot prove it.
- `wrap_by_box`: the source text is a continuous sentence/paragraph and appears multi-line only because the box width wraps it.
- `manual_after_visual_check`: use only when a human/agent visually checked and intentionally inserted breaks to match the reference.
- `single_line`: text should remain on one line.

Rules:

- Use `\n` only for `explicit_source`, `intentional_layout`, or `manual_after_visual_check`.
- For `wrap_by_box`, do not bake line breaks into the string. Set the textbox width/height and let PowerPoint wrap.
- Use integer point sizes only. Round the estimated OCR size to the nearest integer, then visually adjust by integer steps.
- Prefer changing textbox dimensions or integer font size over inserting fake line breaks.
- If OCR text is uncertain, add a note in the conversion report or slide notes instead of silently guessing.

## Native Shapes

Native shapes are allowed only when they can faithfully match the original.
Record the reason in the asset/layout plan.

Cards and panels:

- record fill color, transparency, border color, border width, and shadow;
- record corner radius in pixels or as one of `square`, `small`, `medium`, `large`, `pill`;
- do not use the default rounded rectangle radius blindly;
- measure corner radius from the source image when possible: radius is the distance from the outside corner to the point where the straight edge begins.

Tables and grids:

- use native shapes/tables only when lines, fills, row heights, and text placement are simple and repeatable;
- otherwise keep the table/grid chrome as a no-text image element and overlay editable text.

## Rounded Corners

Rounded corner fidelity matters because bad radius changes the page style.

Approximate classes:

- `square`: 0 px;
- `small`: about 4-8 px on a 1920 px wide slide;
- `medium`: about 9-18 px;
- `large`: about 19-36 px;
- `pill`: radius is about half of the element height.

For pptxgenjs, compute `rectRadius` as `corner_radius_px / min(box_width_px, box_height_px)`, clamped to `0..0.5`. Use `scripts/pptx_object_helpers.js` `cornerRadiusRatio()` when possible.

## Arrows And Connectors

Classify arrows before drawing. Do not use a generic line arrow for everything.

Common arrow kinds:

- `line_no_head`: plain connector line;
- `line_end_triangle`: thin line with triangular head at end;
- `line_begin_triangle`: thin line with triangular head at start;
- `line_double_triangle`: heads at both ends;
- `line_end_stealth`: thin line with narrow/stealth head;
- `line_end_oval`: line ending in a dot/circle;
- `block_right`, `block_left`, `block_up`, `block_down`: thick filled PowerPoint block arrow;
- `block_double`: double-headed filled arrow;
- `chevron`: separate chevron/step arrow shape;
- `curved`: curved arrow or arc-like arrow, preferably image asset if PPT arc risks repair issues;
- `elbow_connector`: right-angle connector.

Record stroke width, color, cap style, dash pattern, head shape, and direction.
Generated PPTX must not contain negative line dimensions: reverse start/end points and swap arrowhead side when needed.

## Image Assets

For each non-text visual element:

1. Try a clean crop only when it is complete, independent, sharp, and free of overlay text or neighboring shapes.
2. If crop is not clean, search the element registry and estimate similarity. Reuse only at about 70% or higher.
3. If similarity is below threshold or text removal is required, regenerate the complete no-text element with image generation from the original reference.
4. Use native shape only when the object is simple enough to match without visible drift.

Do not split coherent cards, diagrams, tables, or product/device visuals into tiny fragments. Preserve semantic whole objects.

## Efficient Check Flow

Recommended order:

1. Inspect the slide image and write the per-page asset/layout plan.
2. Run `validate_asset_decision_plan.py` for visual asset decisions.
3. Run `validate_layout_plan.py --strict` for text, arrow, rounded-corner, and native-shape metadata.
4. Validate media paths before build with `validate_media_refs.py`.
5. Build the PPTX with reusable object helpers where applicable.
6. Run `validate_pptx_integrity.py --strict`.
7. Create/update the conversion report. Renderer preview is optional and should be used only when requested or when package validation/user feedback indicates a problem.
