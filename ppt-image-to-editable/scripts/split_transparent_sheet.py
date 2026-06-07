#!/usr/bin/env python3
"""Split a transparent element sheet into separate PNG elements."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image


def components(alpha: Image.Image, threshold: int, min_area: int) -> list[tuple[int, int, int, int, int]]:
    w, h = alpha.size
    pix = alpha.load()
    seen = bytearray(w * h)
    out: list[tuple[int, int, int, int, int]] = []

    for y in range(h):
        for x in range(w):
            idx = y * w + x
            if seen[idx] or pix[x, y] <= threshold:
                seen[idx] = 1
                continue
            q = deque([(x, y)])
            seen[idx] = 1
            minx = maxx = x
            miny = maxy = y
            area = 0
            while q:
                cx, cy = q.popleft()
                area += 1
                minx = min(minx, cx)
                maxx = max(maxx, cx)
                miny = min(miny, cy)
                maxy = max(maxy, cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        nidx = ny * w + nx
                        if not seen[nidx]:
                            seen[nidx] = 1
                            if pix[nx, ny] > threshold:
                                q.append((nx, ny))
            if area >= min_area:
                out.append((minx, miny, maxx + 1, maxy + 1, area))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prefix", default="element")
    parser.add_argument("--threshold", type=int, default=12)
    parser.add_argument("--min-area", type=int, default=350)
    parser.add_argument("--pad", type=int, default=18)
    args = parser.parse_args()

    img = Image.open(args.sheet).convert("RGBA")
    alpha = img.getchannel("A")
    comps = components(alpha, args.threshold, args.min_area)
    comps.sort(key=lambda b: (b[1], b[0]))
    args.out.mkdir(parents=True, exist_ok=True)

    w, h = img.size
    for i, (x0, y0, x1, y1, area) in enumerate(comps, start=1):
        box = (
            max(0, x0 - args.pad),
            max(0, y0 - args.pad),
            min(w, x1 + args.pad),
            min(h, y1 + args.pad),
        )
        out_path = args.out / f"{args.prefix}_{i:02d}.png"
        img.crop(box).save(out_path)
        print(f"{out_path}\tbox={box}\tarea={area}")


if __name__ == "__main__":
    main()
