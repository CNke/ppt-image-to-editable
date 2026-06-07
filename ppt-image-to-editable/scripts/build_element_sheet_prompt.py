#!/usr/bin/env python3
"""Build 4-slide-batch transparent element sheet prompts from an asset plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_plan(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data.get("slides", [])
    return data


def slide_missing_assets(slide: dict[str, Any]) -> list[dict[str, Any]]:
    if slide.get("no_new_image_assets_required"):
        return []
    assets = []
    for item in slide.get("asset_candidates", []):
        decision = item.get("decision")
        if decision in {"image", "generate", "redraw"}:
            assets.append(item)
    return assets


def prompt_for_batch(batch: list[dict[str, Any]]) -> str:
    lines = [
        "Use the provided slide image(s) as visual references.",
        "Create one high-resolution transparent PNG element sheet for these slide(s).",
        "",
        "Include only the listed non-text visual elements. Do not include any text, numbers, labels, captions, watermarks, card frames, table grids, simple lines, or simple shapes that will be rebuilt in PowerPoint.",
        "Place every element separately on a fully transparent background, arranged in a clean grid with large transparent gaps. Elements must not overlap, touch, intersect, or cast shadows onto each other.",
        "Preserve each element's original icon style, color, gradient, gloss, shadow, silhouette, line weight, badge/background shape, and proportions from the reference slide.",
        "",
    ]
    for slide in batch:
        lines.append(f"Slide {slide.get('slide')}:")
        for i, item in enumerate(slide_missing_assets(slide), start=1):
            desc = item.get("visual_description") or item.get("description") or item.get("name")
            reason = item.get("reason", "")
            lines.append(f"{i}. {item.get('name')}: {desc}. {reason}".strip())
        lines.append("")
    lines.append("Output: one PNG with true alpha transparency. No background color.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()

    slides = [s for s in load_plan(args.plan) if slide_missing_assets(s)]
    args.out.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(slides), args.batch_size):
        batch = slides[start : start + args.batch_size]
        slide_ids = "_".join(str(s.get("slide")) for s in batch)
        out_path = args.out / f"element_sheet_prompt_slides_{slide_ids}.txt"
        out_path.write_text(prompt_for_batch(batch), encoding="utf-8")
        print(out_path)


if __name__ == "__main__":
    main()
