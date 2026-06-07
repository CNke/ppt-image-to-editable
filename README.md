# PPT Image To Editable

Convert flattened or image-only PowerPoint decks into editable PPTX files by
reconstructing slide backgrounds, visual elements, native shapes, and editable
text layers.

This repository is packaged as a Codex skill. It contains the conversion
workflow, reusable validation scripts, and reference rules for high-fidelity
image-to-PPT reconstruction.

## What It Does

- Inspects source PPTX files and rendered slide images.
- Requires one approved sample slide before batch conversion.
- Tracks every non-text visual element with a crop, registry, image-generation,
  or native-shape decision.
- Rebuilds text as editable PowerPoint text boxes whenever text is not part of
  a photo, logo, screenshot, or other baked-in visual.
- Validates asset plans, layout plans, media references, and generated PPTX
  packages before delivery.

## Project Structure

```text
.
├── README.md
├── requirements.txt
├── examples/
│   ├── asset_decision_plan.example.json
│   └── layout_plan.example.json
└── ppt-image-to-editable/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── references/
    │   ├── conversion-playbook.md
    │   └── object-reconstruction.md
    └── scripts/
        ├── build_element_sheet_prompt.py
        ├── element_registry.py
        ├── pptx_object_helpers.js
        ├── split_transparent_sheet.py
        ├── validate_asset_decision_plan.py
        ├── validate_layout_plan.py
        ├── validate_media_refs.py
        └── validate_pptx_integrity.py
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

## Quick Start

1. Copy or install `ppt-image-to-editable/` as a Codex skill.
2. Inspect a source deck and render representative slide PNGs.
3. Build exactly one sample editable slide first.
4. After sample approval, create an asset decision plan for every requested
   slide.
5. Validate plans and media before building the final PPTX.
6. Validate the generated PPTX package.

Example validation commands:

```bash
python ppt-image-to-editable/scripts/validate_asset_decision_plan.py examples/asset_decision_plan.example.json --slides 1
python ppt-image-to-editable/scripts/validate_layout_plan.py examples/layout_plan.example.json --strict
python ppt-image-to-editable/scripts/validate_pptx_integrity.py editable_output.pptx --strict
```

## Core Workflow

The skill intentionally avoids quick screenshot-only conversion. Each deck
should follow this order:

1. Inspect the deck size, page count, and whether slides are flattened images.
2. Classify page types such as cover, directory, content cards, charts, tables,
   process flows, and product-heavy pages.
3. Produce one sample slide and wait for approval.
4. Audit assets for every requested page.
5. Build page-specific layout plans.
6. Assemble visual layers, then editable text layers.
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

