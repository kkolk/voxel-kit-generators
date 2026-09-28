#!/usr/bin/env python3
"""Strike Bay modular factory kit — MILL inside corner, 3 stories.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Seam rule: mill load-bearing brick, no pilasters; wall ends meet
  complementary at bay lines. Trim may exceed footprint 1 voxel along the
  wall-face normal only, never along the bay-run direction.
  Hollow shell + sealed interior room z 1..7 (damage reveal).

Inside (concave) corner for L/T/courtyard plans, 3 stories. Footprint 24x24 at (0,0); trim 1 along +x (east) and +y (north) face normals; z [0,32]. Walls on the x=22..24 and y=22..24 faces (concave point (24,24)). Built as the outside corner rotated 180 deg about the plan centre; plain brick wall ends meet neighbours complementary at x=0 / y=0.
Slug: kit-mill-corner-inside-3s-v1.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import (B, S, T, MILL_PALETTE, CI, box, floater_sweep,
                          mill_window,
                          write_vox, render_preview, render_slice)

PALETTE = [
    ("concrete", (170, 166, 158)),
    ("concrete_dark", (112, 108, 100)),
    ("coping", (202, 198, 190)),
    ("brick", (150, 90, 66)),
    ("brick_dark", (120, 68, 50)),
    ("glass", (72, 98, 118)),
    ("glass_dark", (44, 62, 78)),
    ("steel", (122, 126, 134)),
    ("steel_dark", (62, 64, 72)),
    ("white", (235, 235, 230)),
    ("window", (18, 26, 38)),
    ("dark", (32, 34, 40)),
    ("green", (100, 118, 94)),
    ("green_dark", (70, 88, 68)),
    ("roof", (100, 104, 100)),
    ("band_red", (158, 62, 52)),
    ("band_white", (224, 220, 212)),
    ("patina", (96, 142, 118)),
    ("patina_dark", (66, 104, 88)),
]
C = CI(PALETTE)



def room(vox, rx0, rx1, ry0, ry1):
    """Sealed interior room (damage reveal) z 1..7 with floor pad."""
    brick, brick_dark = C["brick"], C["brick_dark"]
    box(vox, rx0, rx1, ry0, ry1, 0, 1, brick)
    for z in range(1, 7):
        for x in range(rx0, rx1):
            vox[(x, ry0, z)] = brick_dark
            vox[(x, ry1 - 1, z)] = brick_dark
        for y in range(ry0, ry1):
            vox[(rx0, y, z)] = brick_dark
            vox[(rx1 - 1, y, z)] = brick_dark
    for x in range(rx0 + 2, rx0 + 4):
        for z in range(1, 4):
            vox[(x, ry0, z)] = C["dark"]
    box(vox, rx0, rx1, ry0, ry1, 6, 7, C["concrete_dark"])


def weather(vox):
    """Mill family signature: sparse dark brick / dark concrete."""
    brick, brick_dark = C["brick"], C["brick_dark"]
    concrete = C["concrete"]
    for (x, y, z), ci in list(vox.items()):
        if ci == brick and random.random() < 0.06:
            vox[(x, y, z)] = brick_dark
        elif ci == concrete and random.random() < 0.04:
            vox[(x, y, z)] = C["concrete_dark"]


H = 30
FOOTPRINT = (0, 25, 0, 25, 0, 32)
SEED = 203

def _outside_into(vox, H):
    """Outside-corner construction (walls on y=0 and x=0 faces)."""
    brick = C["brick"]
    concrete = C["concrete"]
    box(vox, 0, 24, 0, 2, 0, 1, brick)
    box(vox, 0, 24, 22, 24, 0, 1, brick)
    box(vox, 0, 2, 2, 22, 0, 1, brick)
    box(vox, 22, 24, 2, 22, 0, 1, brick)
    box(vox, 0, 2, 0, 2, 0, H, brick)
    box(vox, 22, 24, 22, 24, 0, H, brick)
    box(vox, 23, 24, 0, 2, 0, H, brick)
    box(vox, 0, 2, 23, 24, 0, H, brick)
    for s in range(0, H, 10):
        box(vox, 0, 24, 0, 2, s, s + 10, brick)
        box(vox, 0, 2, 0, 24, s, s + 10, brick)
        if s == 0:
            box(vox, 0, 24, -1, 3, 0, 2, concrete)
            box(vox, -1, 3, 0, 24, 0, 2, concrete)
        mill_window(vox, C, 'y', 0, -1, s, 3, 9)
        mill_window(vox, C, 'y', 0, -1, s, 15, 21)
        mill_window(vox, C, 'x', 0, -1, s, 3, 9)
        mill_window(vox, C, 'x', 0, -1, s, 15, 21)
    box(vox, 0, 24, -1, 3, H, H + 2, brick)
    box(vox, -1, 3, 0, 24, H, H + 2, brick)
    for i in range(1, 24, 3):
        vox[(i, 0, H)] = C["brick_dark"]
        vox[(0, i, H)] = C["brick_dark"]
    room(vox, 9, 15, 9, 15)
    weather(vox)

def build_module():
    random.seed(SEED)
    vox = {}
    _outside_into(vox, H)          # build outside, then rotate 180 deg
    rot = {(23 - x, 23 - y, z): ci for (x, y, z), ci in vox.items()}
    return rot, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:  # footprint guard
        assert x0 <= x < x1, f"x breach {x}"
        assert y0 <= y < y1, f"y breach {y}"
        assert z0 <= z <= z1, f"z breach {z}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    write_vox(os.path.join(here, "kit-mill-corner-inside-3s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-mill-corner-inside-3s-v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "kit-mill-corner-inside-3s-v1_slice.png"), vox, PALETTE, 5)
