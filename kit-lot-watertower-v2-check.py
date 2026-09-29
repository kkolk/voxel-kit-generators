#!/usr/bin/env python3
"""Assembled check for the v2 water tower rig (kkolk/strike-bay#167).

Unions the 8 part generators in the same order compound.py loads them
(legs, bracing, balcony, shell, roof — dict.update, so later parts win
overlaps), then:
  - asserts the union is a single 6-connected component,
  - reports overall bounds / max z / voxel count / per-palette-slot counts,
  - renders an assembled preview + a plan slice through the tank wall.

Not shipped to the viewer; local validation only.
"""
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import render_preview, render_slice

import importlib

PARTS = [
    "kit-lot-watertower-leg-fl-v2",
    "kit-lot-watertower-leg-fr-v2",
    "kit-lot-watertower-leg-rl-v2",
    "kit-lot-watertower-leg-rr-v2",
    "kit-lot-watertower-bracing-v2",
    "kit-lot-watertower-balcony-v2",
    "kit-lot-watertower-shell-v2",
    "kit-lot-watertower-roof-v2",
]


def components(vox):
    """Yield 6-connected components as sets of coords."""
    seen = set()
    for start in vox:
        if start in seen:
            continue
        comp, stack = set(), [start]
        seen.add(start)
        while stack:
            p = stack.pop()
            comp.add(p)
            x, y, z = p
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                      (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in vox and q not in seen:
                    seen.add(q)
                    stack.append(q)
        yield comp


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    union = {}
    palettes = {}
    for slug in PARTS:
        path = os.path.join(here, slug + ".py")
        spec = importlib.util.spec_from_file_location(slug.replace("-", "_"), path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        vox, _fp = mod.build_module()
        union.update(vox)          # same merge semantics as compound.py
        palettes[slug] = mod.PALETTE
    comps = list(components(union))
    xs = [x for x, _y, _z in union]
    ys = [y for _x, y, _z in union]
    zs = [z for _x, _y, z in union]
    print(f"parts: {len(PARTS)}, voxels: {len(union)}")
    print(f"x {min(xs)}..{max(xs)}  y {min(ys)}..{max(ys)}  z {min(zs)}..{max(zs)}")
    print(f"components: {len(comps)}")
    assert len(comps) == 1, f"union is not one component: {len(comps)}"
    slot_counts = {}
    for ci in union.values():
        slot_counts[ci] = slot_counts.get(ci, 0) + 1
    pal = palettes[PARTS[-1]]
    for ci in sorted(slot_counts):
        print(f"  slot {pal[ci - 1][0]:>14}: {slot_counts[ci]}")
    render_preview(os.path.join(here, "kit-lot-watertower-v2-assembled_check.png"),
                   union, pal)
    render_slice(os.path.join(here, "kit-lot-watertower-v2-assembled_slice_z38.png"),
                 union, pal, 38)
    print("wrote assembled check images")


if __name__ == "__main__":
    main()
