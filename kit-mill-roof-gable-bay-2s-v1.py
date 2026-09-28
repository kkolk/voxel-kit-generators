#!/usr/bin/env python3
"""Strike Bay modular factory kit — MILL gable roof bay, 2 stories.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Seam rule: mill load-bearing brick, no pilasters; wall ends meet
  complementary at bay lines. Trim may exceed footprint 1 voxel along the
  wall-face normal only, never along the bay-run direction.
  Hollow shell + sealed interior room z 1..7 (damage reveal).

Gable roof tile for a 12-wide mill bay, 2-story hall. Footprint 12x24; trim y in [-1,25); z [21,29]. Eave z 22, ridge z 28 at y=12 (slope 0.5), patina planes 2 thick, ridge roll, seam rib on the west edge. Gable ends open (endwall-gable caps them).
Slug: kit-mill-roof-gable-bay-2s-v1.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import (B, S, T, MILL_PALETTE, CI, box, floater_sweep,
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
    sash = C["steel_dark"]
    for x in range(x0, x1):
        for z in range(s + 2, s + 8):
            vox[(x, ya, z)] = C["glass"]
            vox[(x, ya + 1, z)] = C["window"]
    for z in range(s + 2, s + 8):
        vox[(x0, ya, z)] = sash
        vox[(x1 - 1, ya, z)] = sash
    for x in range(x0, x1):
        vox[(x, ya, s + 4)] = sash
        vox[(x, ya, s + 6)] = sash
    for z in (s + 2, s + 3, s + 7):
        vox[(x0 + 2, ya, z)] = sash
    for x in range(x0 - 1, x1 + 1):
        vox[(x, ya, s + 1)] = C["concrete"]
        vox[(x, ya, s + 9)] = C["concrete"]


def band_x(vox, s, xa, y0, y1):
    """Mill window band on an x-face wall (wall x xa..xa+2, outer face xa)."""
    sash = C["steel_dark"]
    for y in range(y0, y1):
        for z in range(s + 2, s + 8):
            vox[(xa, y, z)] = C["glass"]
            vox[(xa + 1, y, z)] = C["window"]
    for z in range(s + 2, s + 8):
        vox[(xa, y0, z)] = sash
        vox[(xa, y1 - 1, z)] = sash
    for y in range(y0, y1):
        vox[(xa, y, s + 4)] = sash
        vox[(xa, y, s + 6)] = sash
    for z in (s + 2, s + 3, s + 7):
        vox[(xa, y0 + 2, z)] = sash
    for y in range(y0 - 1, y1 + 1):
        vox[(xa, y, s + 1)] = C["concrete"]
        vox[(xa, y, s + 9)] = C["concrete"]


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
FOOTPRINT = (0, 12, -1, 25, 21, 29)
SEED = 432

def build_module():
    random.seed(SEED)
    vox = {}
    patina, patina_dark = C["patina"], C["patina_dark"]
    for yy, sgn in ((0, 1), (24, -1)):                     # eave fascia
        box(vox, 0, 12, yy - 1 if sgn > 0 else yy - 1,
            yy + 2 if sgn > 0 else yy + 1, H + 1, H + 3, patina_dark)
    for x in range(0, 12):                                 # roof planes
        for y in range(0, 13):
            zt = H + 2 + round(y * 0.5)
            box(vox, x, x + 1, y, y + 1, zt - 1, zt + 1, patina)
        for y in range(13, 24):
            zt = H + 2 + round((24 - y) * 0.5)
            box(vox, x, x + 1, y, y + 1, zt - 1, zt + 1, patina)
    box(vox, 0, 12, 11, 13, H + 8, H + 9, patina_dark)     # ridge roll
    for y in range(1, 23):                                 # seam rib (west)
        zt = H + 2 + round(min(y, 24 - y) * 0.5)
        box(vox, 0, 1, y, y + 1, zt, zt + 2, patina_dark)
    # sparse seam lines along the slope
    for x in range(2, 12, 3):
        for y in range(1, 23):
            zt = H + 2 + round(min(y, 24 - y) * 0.5)
            vox[(x, y, zt)] = patina_dark
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
    write_vox(os.path.join(here, "kit-mill-roof-gable-bay-2s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-mill-roof-gable-bay-2s-v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "kit-mill-roof-gable-bay-2s-v1_slice.png"), vox, PALETTE, 25)
