# Contributing

## Development Principles

- Preserve the sample-first workflow.
- Keep generated files and private decks out of the repository.
- Prefer small, focused validation scripts over broad implicit behavior.
- Add examples when changing expected JSON schema.
- Run the relevant validators before submitting changes.

## Checks

```bash
python ppt-image-to-editable/scripts/validate_asset_decision_plan.py examples/asset_decision_plan.example.json --slides 1
python ppt-image-to-editable/scripts/validate_layout_plan.py examples/layout_plan.example.json --strict
```

