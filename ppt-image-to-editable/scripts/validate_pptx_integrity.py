#!/usr/bin/env python3
"""Validate PPTX package integrity before delivery.

This catches issues that can make Microsoft PowerPoint show "PowerPoint found
a problem with content" even when the ZIP and XML parse normally.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


SLIDE_RE = re.compile(r"ppt/slides/slide(\d+)\.xml$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--strict", action="store_true", help="fail on compatibility warnings")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    if not args.pptx.exists():
        print(f"ERROR: missing PPTX {args.pptx}", file=sys.stderr)
        return 2

    try:
        with zipfile.ZipFile(args.pptx) as z:
            names = set(z.namelist())

            # XML/rels parse check.
            for name in sorted(names):
                if name.endswith(".xml") or name.endswith(".rels"):
                    try:
                        ET.fromstring(z.read(name))
                    except Exception as exc:
                        errors.append(f"{name}: XML parse error: {exc}")

            # Relationship target existence check.
            for rel_name in sorted(n for n in names if n.endswith(".rels")):
                try:
                    root = ET.fromstring(z.read(rel_name))
                except Exception:
                    continue
                base = os.path.dirname(rel_name.replace("_rels/", ""))
                for rel in root:
                    target = rel.attrib.get("Target", "")
                    if not target or target.startswith("http") or target.startswith("#"):
                        continue
                    if target.startswith("/"):
                        resolved = target[1:]
                    else:
                        resolved = os.path.normpath(os.path.join(base, target)).replace("\\", "/")
                    if resolved not in names:
                        errors.append(f"{rel_name}: missing relationship target {target} -> {resolved}")

            # Slide geometry compatibility checks.
            for slide_name in sorted((n for n in names if SLIDE_RE.match(n)), key=slide_sort):
                xml = z.read(slide_name).decode("utf-8", errors="replace")
                slide_no = SLIDE_RE.match(slide_name).group(1)
                for tag in re.findall(r"<a:ext[^>]+>", xml):
                    cx = attr_int(tag, "cx")
                    cy = attr_int(tag, "cy")
                    if cx is not None and cx < 0:
                        errors.append(f"slide {slide_no}: negative width in {tag}")
                    if cy is not None and cy < 0:
                        errors.append(f"slide {slide_no}: negative height in {tag}")
                if 'prst="arc"' in xml:
                    warnings.append(f"slide {slide_no}: contains preset arc shape; replace with stable lines/freeform if PowerPoint repair appears")

    except zipfile.BadZipFile as exc:
        errors.append(f"not a valid zip/PPTX package: {exc}")

    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.strict and warnings:
        return 1

    print(f"OK: {args.pptx} passed PPTX integrity checks")
    return 0


def slide_sort(name: str) -> int:
    match = SLIDE_RE.match(name)
    return int(match.group(1)) if match else 0


def attr_int(tag: str, name: str) -> int | None:
    match = re.search(rf'{name}="(-?\d+)"', tag)
    return int(match.group(1)) if match else None


if __name__ == "__main__":
    raise SystemExit(main())
