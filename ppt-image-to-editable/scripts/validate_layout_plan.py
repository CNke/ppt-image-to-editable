#!/usr/bin/env python3
"""Validate per-slide editable reconstruction layout plans.

The validator is intentionally small and schema-light. It catches the failure
classes that repeatedly damage image-to-PPT reconstruction quality:

- non-integer font sizes;
- ambiguous hard line breaks in text boxes;
- missing arrow-kind records;
- missing rounded-corner radius records;
- negative geometry;
- native shapes without enough fidelity metadata.

Expected input is JSON with either a top-level list of slides or an object with
`slides`. Each slide may contain `text_boxes`, `shapes`, and `arrows`.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


VALID_LINE_BREAK_POLICIES = {
    "explicit_source",
    "intentional_layout",
    "wrap_by_box",
    "manual_after_visual_check",
    "single_line",
}

VALID_ARROW_KINDS = {
    "line_no_head",
    "line_end_triangle",
    "line_begin_triangle",
    "line_double_triangle",
    "line_end_stealth",
    "line_begin_stealth",
    "line_double_stealth",
    "line_end_oval",
    "line_begin_oval",
    "line_double_oval",
    "block_right",
    "block_left",
    "block_up",
    "block_down",
    "block_double",
    "chevron",
    "curved",
    "elbow_connector",
}


def _slides(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("slides"), list):
            return data["slides"]
        if isinstance(data.get("pages"), list):
            return data["pages"]
    raise ValueError("Layout plan must be a list or contain a `slides` list.")


def _num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _check_box(path: str, obj: dict[str, Any], errors: list[str]) -> None:
    for key in ("x", "y", "w", "h"):
        if key in obj and not _num(obj[key]):
            errors.append(f"{path}.{key}: must be a finite number")
    for key in ("w", "h"):
        if key in obj and _num(obj[key]) and obj[key] < 0:
            errors.append(f"{path}.{key}: must not be negative")


def _font_size(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def validate_slide(slide: dict[str, Any], index: int, strict: bool) -> list[str]:
    slide_id = slide.get("slide") or slide.get("page") or slide.get("id") or index
    base = f"slide[{slide_id}]"
    errors: list[str] = []

    for i, box in enumerate(slide.get("text_boxes", []) or []):
        if not isinstance(box, dict):
            errors.append(f"{base}.text_boxes[{i}]: must be an object")
            continue
        path = f"{base}.text_boxes[{i}]"
        _check_box(path, box, errors)

        size = box.get("font_size", box.get("size"))
        if _font_size(size) is None:
            errors.append(f"{path}.font_size: must be an integer point size")

        text = str(box.get("text", ""))
        policy = box.get("line_break_policy")
        if "\n" in text:
            if policy not in {"explicit_source", "intentional_layout", "manual_after_visual_check"}:
                errors.append(
                    f"{path}.line_break_policy: hard line breaks require "
                    "explicit_source, intentional_layout, or manual_after_visual_check"
                )
        elif strict and policy not in VALID_LINE_BREAK_POLICIES:
            errors.append(f"{path}.line_break_policy: missing or invalid")

        if policy == "wrap_by_box" and "\n" in text:
            errors.append(f"{path}: wrap_by_box text must not contain hard line breaks")

    for i, shape in enumerate(slide.get("shapes", []) or []):
        if not isinstance(shape, dict):
            errors.append(f"{base}.shapes[{i}]: must be an object")
            continue
        path = f"{base}.shapes[{i}]"
        _check_box(path, shape, errors)
        shape_type = str(shape.get("shape_type", shape.get("type", ""))).lower()
        if shape_type in {"roundrect", "rounded_rect", "rounded_rectangle", "pill"}:
            has_radius = any(k in shape for k in ("corner_radius_px", "corner_radius_pt", "corner_radius_ratio", "corner_radius_class"))
            if not has_radius:
                errors.append(f"{path}: rounded shape must record corner radius")
        if shape.get("decision") == "native_shape":
            for key in ("fill", "border", "layer"):
                if key not in shape and strict:
                    errors.append(f"{path}.{key}: required for native_shape fidelity audit")

    for i, arrow in enumerate(slide.get("arrows", []) or []):
        if not isinstance(arrow, dict):
            errors.append(f"{base}.arrows[{i}]: must be an object")
            continue
        path = f"{base}.arrows[{i}]"
        _check_box(path, arrow, errors)
        kind = arrow.get("arrow_kind")
        if kind not in VALID_ARROW_KINDS:
            errors.append(f"{path}.arrow_kind: missing or unsupported arrow kind `{kind}`")
        for key in ("line_width", "stroke", "cap"):
            if strict and key not in arrow:
                errors.append(f"{path}.{key}: required for arrow fidelity audit")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Layout plan JSON file")
    parser.add_argument("--strict", action="store_true", help="Require optional fidelity audit fields")
    args = parser.parse_args()

    with args.plan.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    errors: list[str] = []
    for idx, slide in enumerate(_slides(data), start=1):
        if not isinstance(slide, dict):
            errors.append(f"slides[{idx}]: must be an object")
            continue
        errors.extend(validate_slide(slide, idx, args.strict))

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"OK: layout plan validated ({args.plan})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
