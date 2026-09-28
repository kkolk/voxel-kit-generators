#!/usr/bin/env python3
"""Strike Bay modular factory kit — MILL flue duct, 1 story.

Horizontal flue duct connecting a building wall to a chimney/smokestack.
Runs along x from the wall face (x=0) to the chimney (x=12).

GRID CONTRACT (see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, z-up.
  Origin at footprint min corner, ground level. No slab, no yard.

Design:
  - Duct body: x 1..11, y 10..14, z 3..7 (4x4 cross-section), brick
  - Flue interior: y 11..13, z 4..6, dark (open at chimney end x=11)
  - Wall collar: x 0..1, y 9..15, z 2..8, concrete flange
  - Chimney collar: x 11..12, y 9..15, z 2..8, concrete flange
  - Support pier: x 5..7, y 11..13, z 0..3, brick with concrete cap
  - Cleanout door on south face, steel bands at x=3 and x=9
  - Corbelled brick course at duct top (mill family signature)

Slug: kit-mill-flue-duct-v1.
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

FOOTPRINT = (0, 12, 9, 15, 0, 8)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(201)
    vox = {}
    brick, brick_dark = C["brick"], C["brick_dark"]
    concrete = C["concrete"]
    steel_dark = C["steel_dark"]
    dark = C["dark"]

    # ---- duct body: brick shell, x 1..11, y 10..14, z 3..7
    # bottom slab
    box(vox, 1, 11, 10, 14, 3, 4, brick)
    # top slab
    box(vox, 1, 11, 10, 14, 6, 7, brick)
    # side walls (north/south)
    box(vox, 1, 11, 10, 11, 4, 6, brick)
    box(vox, 1, 11, 13, 14, 4, 6, brick)
    # flue interior: dark (2x2: y 11..13, z 4..6)
    box(vox, 1, 11, 11, 13, 4, 6, dark)

    # ---- corbelled brick course at duct top (z=7), proud 1 on sides
    box(vox, 1, 11, 9, 15, 7, 8, brick)
    # dentil detailing
    for x in range(2, 11, 3):
        vox[(x, 9, 7)] = brick_dark
        vox[(x, 14, 7)] = brick_dark

    # ---- wall collar at x=0: concrete flange, y 9..15, z 2..8
    box(vox, 0, 1, 9, 15, 2, 8, concrete)
    # opening through collar (aligns with flue)
    box(vox, 0, 1, 11, 13, 4, 6, dark)

    # ---- chimney collar at x=11: concrete flange, y 9..15, z 2..8
    box(vox, 11, 12, 9, 15, 2, 8, concrete)
    # open flue at chimney end
    box(vox, 11, 12, 11, 13, 4, 6, dark)

    # ---- support pier: x 5..7, y 11..13, z 0..3, brick
    box(vox, 5, 7, 11, 13, 0, 2, brick)
    # concrete cap
    box(vox, 5, 7, 11, 13, 2, 3, concrete)

    # ---- cleanout door on south face (y=10), x 5..7, z 3..5
    for x in range(5, 7):
        for z in range(3, 5):
            vox[(x, 10, z)] = dark
    # steel frame around door
    for x in range(4, 8):
        vox[(x, 10, 2)] = steel_dark
        vox[(x, 10, 5)] = steel_dark
    for z in range(2, 6):
        vox[(4, 10, z)] = steel_dark
        vox[(7, 10, z)] = steel_dark

    # ---- steel bands around duct at x=3 and x=9
    for bx in (3, 9):
        for y in range(10, 14):
            vox[(bx, y, 3)] = steel_dark
            vox[(bx, y, 6)] = steel_dark
        for z in range(3, 7):
            vox[(bx, 10, z)] = steel_dark
            vox[(bx, 13, z)] = steel_dark

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
    for (x, y, z) in vox:  # footprint guard
        assert x0 <= x < x1, f"x breach {x}"
        assert y0 <= y < y1, f"y breach {y}"
        assert z0 <= z <= z1, f"z breach {z}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    write_vox(os.path.join(here, "kit-mill-flue-duct-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-mill-flue-duct-v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "kit-mill-flue-duct-v1_slice.png"), vox, PALETTE, 5)
    print(f"mill flue duct: {len(vox)} voxels")
