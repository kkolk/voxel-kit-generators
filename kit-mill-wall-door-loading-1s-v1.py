#!/usr/bin/env python3
"""Strike Bay modular factory kit — MILL wall bay, loading-door variant, 1 story.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint [0,12) x [0,24); trim may use y in [-1,25) (face normal only).
  Seam rule: plain brick wall ends meet complementary at bay lines (x=0/12).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
  Wall top H=10; corbelled brick cornice z 10..12 proud 1.

Loading-door variant: ground story has a loading door on BOTH
  faces (opening x 2..10, z 1..9; recessed green leaf z 2..7 with
  steel panel lines + glass transom z 7..8; concrete posts x=1/10
  and lintel z 8..9). Upper stories get golden window bands.

Slug: kit-mill-wall-door-loading-1s-v1.
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

FOOTPRINT = (0, 12, 0, 24, 0, 12)   # + cornice; trim may use y in [-1, 25)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(36)
    vox = {}
    brick, brick_dark = C["brick"], C["brick_dark"]
    concrete, glass = C["concrete"], C["glass"]
    sash = C["steel_dark"]
    H = 10

    # ---- floor edge: perimeter strip T wide, z 0..1, + strips under room
    box(vox, 0, 12, 0, 2, 0, 1, brick)
    box(vox, 0, 12, 22, 24, 0, 1, brick)
    box(vox, 0, 2, 2, 22, 0, 1, brick)
    box(vox, 10, 12, 2, 22, 0, 1, brick)

    # ---- ground story: loading doors on BOTH faces
    for (ya, yb) in ((0, 2), (22, 24)):
        box(vox, 0, 12, ya, yb, 0, 10, brick)
    # concrete water table, cut at the door spans (x 2..10)
    for (pa, pb) in ((-1, 3), (21, 25)):
        for xr in ((0, 2), (10, 12)):
            box(vox, xr[0], xr[1], pa, pb, 0, 2, concrete)
    for (ya, yb) in ((0, 2), (22, 24)):
        yo = 0 if ya == 0 else 1              # outer layer index
        yi = 1 - yo                           # inner layer index
        # opening x 2..10, z 1..9 through both wall layers
        for x in range(2, 10):
            for z in range(1, 9):
                vox.pop((x, ya, z), None)
                vox.pop((x, ya + 1, z), None)
        # concrete surround: posts + lintel, full thickness
        for y in (ya, ya + 1):
            for z in range(1, 9):
                vox[(1, y, z)] = concrete
                vox[(10, y, z)] = concrete
            for x in range(1, 11):
                vox[(x, y, 8)] = concrete
        # recessed leaf (inner layer): green + steel_dark panel lines
        for x in range(2, 10):
            for z in range(2, 7):
                vox[(x, ya + yi, z)] = C["green"]
        for x in (4, 6, 8):
            for z in range(2, 7):
                vox[(x, ya + yi, z)] = sash
        for x in range(2, 10):
            vox[(x, ya + yi, 4)] = sash
        # glass transom z 7..8 with centre mullions
        for x in range(2, 10):
            vox[(x, ya + yi, 7)] = glass
        for x in (5, 6):
            vox[(x, ya + yi, 7)] = sash
    # ---- corbelled brick cornice z 10..12, proud 1
    box(vox, 0, 12, -1, 3, 10, 12, brick)
    box(vox, 0, 12, 21, 25, 10, 12, brick)
    for x in range(1, 12, 3):  # dentil course
        vox[(x, 0, 10)] = brick_dark
        vox[(x, 23, 10)] = brick_dark

    # ---- sealed interior room (damage reveal), walls on floor strips
    rx0, rx1, ry0, ry1 = 3, 9, 9, 15
    box(vox, rx0, rx1, ry0, ry1, 0, 1, brick)          # floor pad
    for z in range(1, 7):
        for x in range(rx0, rx1):
            vox[(x, ry0, z)] = brick_dark
            vox[(x, ry1 - 1, z)] = brick_dark
        for y in range(ry0, ry1):
            vox[(rx0, y, z)] = brick_dark
            vox[(rx1 - 1, y, z)] = brick_dark
    for x in range(5, 7):                               # door recess
        for z in range(1, 4):
            vox[(x, ry0, z)] = C["dark"]
    box(vox, rx0, rx1, ry0, ry1, 6, 7, C["concrete_dark"])  # cap

    # ---- subtle weathering (mill family signature)
    for (x, y, z), ci in list(vox.items()):
        if ci == brick and random.random() < 0.06:
            vox[(x, y, z)] = brick_dark
        elif ci == concrete and random.random() < 0.04:
            vox[(x, y, z)] = C["concrete_dark"]

    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:  # footprint guard (trim: y in [-1,25))
        assert x0 <= x < x1, f"x breach {x}"
        assert -1 <= y <= 24, f"y breach {y}"
        assert 0 <= z <= z1, f"z breach {z}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    write_vox(os.path.join(here, "kit-mill-wall-door-loading-1s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-mill-wall-door-loading-1s-v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "kit-mill-wall-door-loading-1s-v1_slice_z5.png"), vox, PALETTE, 5)
