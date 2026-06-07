#!/usr/bin/env python3
"""Maintain a reusable PPT image-conversion element registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def registry_path(workspace: Path) -> Path:
    return workspace / "outputs" / "element_registry" / "element_registry.json"


def load_registry(workspace: Path) -> list[dict[str, Any]]:
    path = registry_path(workspace)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(workspace: Path, items: list[dict[str, Any]]) -> None:
    path = registry_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    items = sorted(items, key=lambda item: item.get("id", ""))
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_list(args: argparse.Namespace) -> None:
    items = load_registry(args.workspace)
    for item in items:
        print(f"{item.get('id','')} | {item.get('path','')} | {','.join(item.get('tags', []))}")
    print(f"total={len(items)}")


def cmd_search(args: argparse.Namespace) -> None:
    items = load_registry(args.workspace)
    tags = {t.strip().lower() for t in (args.tags or "").split(",") if t.strip()}
    query = (args.query or "").lower()
    for item in items:
        hay = " ".join(
            [
                str(item.get("id", "")),
                str(item.get("description", "")),
                " ".join(item.get("tags", [])),
            ]
        ).lower()
        item_tags = {t.lower() for t in item.get("tags", [])}
        if tags and not tags.intersection(item_tags):
            continue
        if query and query not in hay:
            continue
        print(json.dumps(item, ensure_ascii=False, indent=2))


def cmd_add(args: argparse.Namespace) -> None:
    items = load_registry(args.workspace)
    by_id = {item.get("id"): item for item in items if item.get("id")}
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    by_id[args.id] = {
        "id": args.id,
        "path": args.path.replace("\\", "/"),
        "source_slide": args.source_slide,
        "source_asset": args.source_asset.replace("\\", "/") if args.source_asset else args.path.replace("\\", "/"),
        "description": args.description or "",
        "tags": tags,
        "original_bbox_px": None,
        "recommended_display_px": None,
        "alpha_validated": bool(args.alpha_validated),
        "text_free": bool(args.text_free),
        "reuse_notes": args.reuse_notes or "Reuse only when visual similarity is about 70% or higher.",
    }
    save_registry(args.workspace, list(by_id.values()))
    print(f"saved {args.id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("search")
    p.add_argument("--tags", default="")
    p.add_argument("--query", default="")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("add")
    p.add_argument("--id", required=True)
    p.add_argument("--path", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--description", default="")
    p.add_argument("--source-slide", type=int, default=None)
    p.add_argument("--source-asset", default="")
    p.add_argument("--reuse-notes", default="")
    p.add_argument("--alpha-validated", action="store_true", default=True)
    p.add_argument("--text-free", action="store_true", default=True)
    p.set_defaults(func=cmd_add)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.workspace = args.workspace.resolve()
    args.func(args)


if __name__ == "__main__":
    main()
