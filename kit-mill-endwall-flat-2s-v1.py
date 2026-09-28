#!/usr/bin/env python3
"""Strike Bay modular factory kit — MILL flat endwall, 2 stories.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Seam rule: mill load-bearing brick, no pilasters; wall ends meet
  complementary at bay lines. Trim may exceed footprint 1 voxel along the
  wall-face normal only, never along the bay-run direction.
  Hollow shell + sealed interior room z 1..7 (damage reveal).

Flat end wall capping a mill wing end, 2 stories. Footprint x [-2,0), y [0,24); trim x in [-3,0), y in [-1,25) at coping; z [0,27]. Window bands per story on the outer (-x) face; U-shaped end parapet + coping; slab strip ties into the roof tile. Seam halves x -1..0 at the y-face edges meet the wall bays' plain ends.
Slug: kit-mill-endwall-flat-2s-v1.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import (B, S, T, MILL_PALETTE, CI, box, floater_sweep, mill_window,
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



def band_y(vox, s, ya, x0, x1):
    """Mill window band on a y-face wall (wall y ya..ya+2, outer face ya)."""
    mill_window(vox, C, "y", ya, -1, s, x0, x1)


def band_x(vox, s, xa, y0, y1):
    """Mill window band on an x-face wall (wall x xa..xa+2, outer face xa)."""
    mill_window(vox, C, "x", xa, -1, s, y0, y1)


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


H = 20
FOOTPRINT = (-3, 0, -1, 25, 0, 27)
SEED = 302

def build_module():
    random.seed(SEED)
    vox = {}
    brick, concrete = C["brick"], C["concrete"]
    for s in range(0, H, 10):
        box(vox, -2, 0, 0, 24, s, s + 10, brick)
        if s == 0:
            box(vox, -3, 0, 0, 24, 0, 2, concrete)   # water table proud -x
        band_x(vox, s, -2, 3, 9)
        band_x(vox, s, -2, 15, 21)
    box(vox, -3, 0, 0, 24, H, H + 2, brick)           # cornice proud -x
    for i in range(1, 24, 3):
        vox[(-2, i, H)] = C["brick_dark"]
    box(vox, -2, 0, 0, 24, H + 2, H + 3, C["roof"])   # slab strip
    box(vox, -2, -1, 0, 24, H + 3, H + 6, brick)      # end parapet
    box(vox, -3, 0, -1, 25, H + 6, H + 7, C["coping"])  # coping proud -x, 3-wide full cap
    for yy in ((0, 1), (23, 24)):                     # parapet returns
        box(vox, -2, 0, yy[0], yy[1], H + 3, H + 6, brick)
    box(vox, -2, 0, -1, 2, H + 6, H + 7, C["coping"])   # return coping, proud
    box(vox, -2, 0, 22, 25, H + 6, H + 7, C["coping"])
    weather(vox)
    return vox, FOOTPRINT


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
    write_vox(os.path.join(here, "kit-mill-endwall-flat-2s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-mill-endwall-flat-2s-v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "kit-mill-endwall-flat-2s-v1_slice.png"), vox, PALETTE, 5)
