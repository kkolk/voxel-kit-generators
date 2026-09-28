#!/usr/bin/env python3
"""Strike Bay modular factory kit — FRAME inside (concave) corner, 2 stories. Walls on the north (y=24) and east (x=24) faces.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint x [0,24) x y [0,24), trim +1 on x/y (far-face normals), z [0,H], H=20; trim may exceed 1 voxel along wall-face normals only.
  Seam rule: 2-wide columns centred on bay lines; each module writes its
  half on each walled face (full 2-wide columns at interior bay lines).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
Wall top H=20. Ribbons per story both faces. Concave corner column 2x2 whole; full columns at interior bay lines; seam halves on the open edges.
Slug: kit-frame-corner-inside-2s-v1.
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

FOOTPRINT = (0, 25, 0, 25, 0, 20)

H = 20
RIBBONS = ((2, 10), (14, 22))
MULLS = (4, 7, 16, 19)


def story_north(vox, s):
    conc, brick, glass = C["concrete"], C["brick"], C["glass"]
    sash = C["steel_dark"]
    zc = s + 2 if s == 0 else s
    box(vox, 21, 25, 21, 25, zc, s + 10, conc)  # concave corner, whole + proud
    box(vox, 11, 13, 21, 25, zc, s + 10, conc)  # bay line x=12, full 2-wide
    box(vox, 0, 1, 21, 25, zc, s + 10, conc)    # west seam half
    box(vox, 0, 24, 23, 24, s + 2, s + 8, brick)
    if s > 0:  # spandrel: solid brick below the sill
        box(vox, 0, 24, 23, 24, s, s + 2, brick)
    box(vox, 0, 24, 23, 24, s + 2, s + 3, conc)
    for xa, xb in RIBBONS:
        for x in range(xa, xb):
            for z in range(s + 3, s + 7):
                vox[(x, 23, z)] = glass
    for x in MULLS:
        for z in range(s + 3, s + 7):
            vox[(x, 23, z)] = sash
    box(vox, 0, 24, 21, 25, s + 8, s + 10, conc)


def story_east(vox, s):
    conc, brick, glass = C["concrete"], C["brick"], C["glass"]
    sash = C["steel_dark"]
    zc = s + 2 if s == 0 else s
    box(vox, 21, 25, 11, 13, zc, s + 10, conc)  # bay line y=12, full 2-wide
    box(vox, 21, 25, 0, 1, zc, s + 10, conc)    # south seam half
    box(vox, 23, 24, 0, 24, s + 2, s + 8, brick)
    if s > 0:  # spandrel
        box(vox, 23, 24, 0, 24, s, s + 2, brick)
    box(vox, 23, 24, 0, 24, s + 2, s + 3, conc)
    for ya, yb in RIBBONS:
        for y in range(ya, yb):
            for z in range(s + 3, s + 7):
                vox[(23, y, z)] = glass
    for y in MULLS:
        for z in range(s + 3, s + 7):
            vox[(23, y, z)] = sash
    box(vox, 21, 25, 0, 24, s + 8, s + 10, conc)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(35)
    vox = {}
    conc, brick, brick_dark = C["concrete"], C["brick"], C["brick_dark"]
    box(vox, 0, 24, 0, 2, 0, 1, conc)
    box(vox, 0, 24, 22, 24, 0, 1, conc)
    box(vox, 0, 2, 2, 22, 0, 1, conc)
    box(vox, 22, 24, 2, 22, 0, 1, conc)
    box(vox, 0, 24, 21, 25, 0, 2, conc)
    box(vox, 21, 25, 0, 24, 0, 2, conc)
    for s in range(0, H, 10):
        story_north(vox, s)
        story_east(vox, s)

    rx0, rx1, ry0, ry1 = 9, 15, 9, 15
    box(vox, rx0, rx1, ry0, ry1, 0, 1, conc)
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
    box(vox, rx0, rx1, ry0, ry1, 6, 7, C["steel_dark"])
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
    write_vox(os.path.join(here, "kit-frame-corner-inside-2s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-frame-corner-inside-2s-v1_preview.png"), vox, PALETTE)
