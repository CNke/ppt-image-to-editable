#!/usr/bin/env python3
"""Validate per-slide asset decision records before full-deck conversion.

Expected JSON shape:

{
  "slides": [
    {
      "slide": 1,
      "asset_candidates": [
        {
          "name": "product photo",
          "decision": "crop",
          "reason": "complete isolated product crop",
          "crop_box": [100, 200, 500, 700]
        },
        {
          "name": "shield badge",
          "decision": "registry",
          "registry_candidate": "shield_check_badge",
          "similarity_estimate": 82,
          "similarity_basis": "same circle badge, stroke style, color"
        },
        {
          "name": "simple card frame",
          "decision": "native_shape",
          "reason": "single-color rounded rectangle, border and radius matchable"
        }
      ],
      "no_new_image_assets_required": true
    }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


VALID_DECISIONS = {"crop", "registry", "image", "native_shape"}


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path, help="asset decision plan JSON")
    parser.add_argument(
        "--slides",
        help="required slide numbers, e.g. 1-25 or 1,2,4,7-9",
    )
    args = parser.parse_args()

    data = load(args.plan)
    slides = data.get("slides")
    if not isinstance(slides, list):
        print("ERROR: top-level JSON must contain a 'slides' list", file=sys.stderr)
        return 2

    errors: list[str] = []
    seen: set[int] = set()

    for idx, slide in enumerate(slides):
        n = slide.get("slide")
        if not isinstance(n, int):
            errors.append(f"slides[{idx}]: missing integer slide")
            continue
        seen.add(n)
        assets = slide.get("asset_candidates")
        if assets is None:
            errors.append(f"slide {n}: missing asset_candidates")
            continue
        if not isinstance(assets, list):
            errors.append(f"slide {n}: asset_candidates must be a list")
            continue
        for j, asset in enumerate(assets):
            prefix = f"slide {n} asset[{j}]"
            name = asset.get("name")
            if not name:
                errors.append(f"{prefix}: missing name")
            decision = asset.get("decision")
            if decision not in VALID_DECISIONS:
                errors.append(f"{prefix} {name!r}: invalid or missing decision")
                continue
            if not asset.get("reason") and decision != "registry":
                errors.append(f"{prefix} {name!r}: missing reason")
            if decision == "crop" and not asset.get("crop_box"):
                errors.append(f"{prefix} {name!r}: crop decision missing crop_box")
            if decision == "registry":
                if not asset.get("registry_candidate"):
                    errors.append(f"{prefix} {name!r}: registry decision missing registry_candidate")
                score = asset.get("similarity_estimate")
                if not isinstance(score, (int, float)):
                    errors.append(f"{prefix} {name!r}: registry decision missing numeric similarity_estimate")
                elif score < 70:
                    errors.append(f"{prefix} {name!r}: registry similarity {score} is below 70; use image generation")
                if not asset.get("similarity_basis"):
                    errors.append(f"{prefix} {name!r}: registry decision missing similarity_basis")
            if decision == "image" and not (asset.get("generation_prompt") or asset.get("brief")):
                errors.append(f"{prefix} {name!r}: image decision missing generation_prompt or brief")
            if decision == "native_shape" and not asset.get("native_shape_basis"):
                errors.append(f"{prefix} {name!r}: native_shape decision missing native_shape_basis")

    if args.slides:
        required = parse_slide_spec(args.slides)
        missing = sorted(required - seen)
        if missing:
            errors.append(f"missing slide records: {missing}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"OK: validated {len(slides)} slide records in {args.plan}")
    return 0


def parse_slide_spec(spec: str) -> set[int]:
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out


if __name__ == "__main__":
    raise SystemExit(main())
