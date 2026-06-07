# PPT Image To Editable

English | [简体中文](README.zh-CN.md)

This repository provides a Codex skill for converting slide images into
editable PowerPoint files.

It is not a standalone PPT generator. It does not design a deck from a prompt
or create PPT pages by itself. Its purpose is to help Codex reconstruct an
existing PPT image as faithfully as possible into an editable `.pptx` file:
editable text boxes, native shapes where appropriate, and complete image
elements for visuals that should remain visually intact.

The prerequisite is that you already have PPT slide images. A recommended
workflow is to generate or obtain the slide images first, for example with
`gpt-image`, and then use this skill to convert those images into editable
PowerPoint slides.

## What It Does

- Guides Codex through high-fidelity image-to-PPT reconstruction.
- Requires one approved sample slide before batch conversion.
- Converts slide-image content into editable PowerPoint objects where possible.
- Preserves complex visual elements as complete high-resolution image assets
  when native shapes would reduce fidelity.
- Rebuilds visible text as editable PowerPoint text boxes unless the text is
  part of a logo, product photo, screenshot, or another baked-in visual.
- Validates asset plans, layout plans, media references, and generated PPTX
  packages before delivery.

## What It Does Not Do

- It does not directly generate a complete PPT from a text prompt.
- It does not replace a presentation design model or image-generation model.
- It does not remove the need for source slide images.
- It does not guarantee that every visual element becomes a native editable
  shape; fidelity is prioritized when exact shape reconstruction would be
  unreliable.

## Recommended Workflow

1. Generate or obtain PPT slide images.
   - Recommended: use `gpt-image` to create polished slide images first.
   - Also supported: rendered images from an existing flattened/image-only
     PowerPoint deck.
2. Install or copy `ppt-image-to-editable/` as a Codex skill.
3. Ask Codex to inspect the slide image or image-only PPTX.
4. Build exactly one editable sample slide first.
5. Review the sample and approve the reconstruction style.
6. After approval, create an asset decision plan for every requested slide.
7. Build page-specific layout plans.
8. Convert the full deck and validate the generated `.pptx`.

## Project Structure

```text
.
|-- README.md
|-- README.zh-CN.md
|-- requirements.txt
|-- examples/
|   |-- asset_decision_plan.example.json
|   `-- layout_plan.example.json
`-- ppt-image-to-editable/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- references/
    |   |-- conversion-playbook.md
    |   `-- object-reconstruction.md
    `-- scripts/
        |-- build_element_sheet_prompt.py
        |-- element_registry.py
        |-- pptx_object_helpers.js
        |-- split_transparent_sheet.py
        |-- validate_asset_decision_plan.py
        |-- validate_layout_plan.py
        |-- validate_media_refs.py
        `-- validate_pptx_integrity.py
```

## Requirements

- Python 3.10+
- Pillow, used by the transparent sheet splitter
- Node.js, only when using `pptx_object_helpers.js` from a JavaScript PPTX
  build script
- A PPTX generation workflow such as `pptxgenjs` for actual deck assembly

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

## Validation Examples

```bash
python ppt-image-to-editable/scripts/validate_asset_decision_plan.py examples/asset_decision_plan.example.json --slides 1
python ppt-image-to-editable/scripts/validate_layout_plan.py examples/layout_plan.example.json --strict
python ppt-image-to-editable/scripts/validate_pptx_integrity.py editable_output.pptx --strict
```

## Conversion Principles

The skill avoids shallow screenshot-only conversion. The target output should
look close to the source image while exposing useful editable layers:

1. Inspect slide size, page count, and whether the deck is flattened.
2. Classify page types such as cover, directory, content cards, charts, tables,
   process flows, and product-heavy pages.
3. Produce one sample slide and wait for approval.
4. Audit every non-text visual element.
5. Decide whether each visual should be cropped, reused from a registry,
   regenerated as an image, or rebuilt as a native shape.
6. Place visual layers first and editable text layers last.
7. Run validation before delivery.

## Validation Tools

- `validate_asset_decision_plan.py`: confirms every slide has complete
  crop/registry/image/native-shape decisions.
- `validate_layout_plan.py`: catches non-integer font sizes, missing line-break
  policy, negative geometry, and incomplete shape metadata.
- `validate_media_refs.py`: checks build scripts for missing image references.
- `validate_pptx_integrity.py`: inspects generated PPTX packages for XML,
  relationship, media, and geometry problems.
- `split_transparent_sheet.py`: splits generated transparent element sheets
  into separate PNG assets.
- `element_registry.py`: manages reusable visual assets across a deck.
- `build_element_sheet_prompt.py`: creates batched image-generation prompts
  from an asset decision plan.

## Repository Notes

Generated decks, rendered previews, local slide images, and private project
materials should stay out of Git. Use local `outputs/`, `assets/`, or
`samples/` folders for active conversion work.

