#!/usr/bin/env python3
"""Check a PPT build script for missing local PNG/JPG media references."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MEDIA_RE = re.compile(r"""['"]([^'"]+\.(?:png|jpg|jpeg|webp))['"]""", re.IGNORECASE)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", type=Path)
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        help="asset root to search, may be repeated",
    )
    args = parser.parse_args()

    if not args.script.exists():
        print(f"ERROR: missing script {args.script}", file=sys.stderr)
        return 2

    text = args.script.read_text(encoding="utf-8", errors="replace")
    refs = sorted(set(MEDIA_RE.findall(text)))
    roots = [Path(r) for r in args.root] or [args.script.parent]

    missing: list[str] = []
    for ref in refs:
        p = Path(ref)
        if p.is_absolute():
            ok = p.exists()
        else:
            ok = any((root / ref).exists() for root in roots)
        if not ok:
            missing.append(ref)

    if missing:
        for ref in missing:
            print(f"ERROR: missing media reference {ref}", file=sys.stderr)
        return 1

    print(f"OK: {args.script} media references found ({len(refs)} refs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
