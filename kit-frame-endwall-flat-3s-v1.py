#!/usr/bin/env python3
"""Strike Bay modular factory kit — FRAME flat endwall cap, 3 stories.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint x [-2,0) x y [0,24), trim x -3 (face normal), z [0,H+6], H=30; trim may exceed 1 voxel along wall-face normals only.
  Seam rule: 2-wide columns centred on bay lines; each module writes its
  half on each walled face (full 2-wide columns at interior bay lines).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
Wall top H=30. Whole corner columns, intermediate column, ribbons per story, end parapet U with coping proud -x, slab strip.
Slug: kit-frame-endwall-flat-3s-v1.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import (B, S, T, FRAME_PALETTE, CI, box, floater_sweep,
                          write_vox, render_preview)

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
]
C = CI(PALETTE)

FOOTPRINT = (-3, 0, -1, 25, 0, 36)

H = 30


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(39)
    vox = {}
    conc, brick, brick_dark = C["concrete"], C["brick"], C["brick_dark"]
    glass, sash = C["glass"], C["steel_dark"]
    cop, roof = C["coping"], C["roof"]
    box(vox, -2, 0, 0, 2, 0, 1, conc)    # floor edge
    box(vox, -2, 0, 22, 24, 0, 1, conc)
    box(vox, -3, 0, 0, 24, 0, 2, conc)   # plinth, proud -x
    for s in range(0, H, 10):
        zc = s + 2 if s == 0 else s
        box(vox, -3, 0, 0, 2, zc, s + 10, conc)    # corner columns, whole
        box(vox, -3, 0, 22, 24, zc, s + 10, conc)
        box(vox, -3, 0, 11, 13, zc, s + 10, conc)  # intermediate, bay line
        box(vox, -1, 0, 0, 2, zc, s + 10, conc)    # seam halves for y-faces
        box(vox, -1, 0, 22, 24, zc, s + 10, conc)
        box(vox, -1, 0, 0, 24, s + 2, s + 8, brick)
        if s > 0:  # spandrel: solid brick below the sill
            box(vox, -1, 0, 0, 24, s, s + 2, brick)
        box(vox, -1, 0, 0, 24, s + 2, s + 3, conc)
        for ya, yb in ((2, 10), (14, 22)):
            for y in range(ya, yb):
                for z in range(s + 3, s + 7):
                    vox[(-1, y, z)] = glass
        for y in (4, 7, 16, 19):
            for z in range(s + 3, s + 7):
                vox[(-1, y, z)] = sash
        box(vox, -3, 0, 0, 24, s + 8, s + 10, conc)  # header beam
    box(vox, -2, 0, 0, 24, H, H + 2, roof)       # slab strip
    box(vox, -2, -1, 0, 24, H + 2, H + 5, conc)  # end parapet
    box(vox, -2, 0, 0, 1, H + 2, H + 5, conc)    # returns
    box(vox, -2, 0, 23, 24, H + 2, H + 5, conc)
    box(vox, -3, 0, -1, 25, H + 5, H + 6, cop)  # 3-wide full cap   # coping, proud -x
    box(vox, -2, 0, -1, 2, H + 5, H + 6, cop)   # return coping, proud
    box(vox, -2, 0, 22, 25, H + 5, H + 6, cop)
    box(vox, -2, 0, 9, 15, 0, 1, conc)           # interior room
    for z in range(1, 7):
        for x in range(-2, 0):
            vox[(x, 9, z)] = brick_dark
            vox[(x, 14, z)] = brick_dark
    box(vox, -2, 0, 9, 15, 6, 7, C["steel_dark"])

    for (_x, _y, _z), _ci in list(vox.items()):
        if _ci == brick and random.random() < 0.06:
            vox[(_x, _y, _z)] = brick_dark
        elif _ci == conc and random.random() < 0.04:
            vox[(_x, _y, _z)] = C["concrete_dark"]
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:  # footprint guard
        assert x0 <= x < x1, "x breach %d" % x
        assert y0 <= y < y1, "y breach %d" % y
        assert 0 <= z <= z1, "z breach %d" % z
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    write_vox(os.path.join(here, "kit-frame-endwall-flat-3s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-frame-endwall-flat-3s-v1_preview.png"), vox, PALETTE)
