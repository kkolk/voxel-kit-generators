#!/usr/bin/env python3
"""Strike Bay modular factory kit — FRAME stepped transition bay, 2 to 3 stories. Sections x 0..4 (H=30) / x 4..8 (H=25) / x 8..12 (H=20); concrete step faces with coping ledges at x=4 and x=8.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint x [0,12) x y [0,24), trim y -1 (face normal), z [0,30]; trim may exceed 1 voxel along wall-face normals only.
  Seam rule: 2-wide columns centred on bay lines; each module writes its
  half on each walled face (full 2-wide columns at interior bay lines).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
Tall and low sections carry glass ribbons on full stories; mid section plain. Header beam at each section top.
Slug: kit-frame-step-2to3-v1.
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

FOOTPRINT = (0, 12, -1, 25, 0, 30)

HA, HB, HC = 30, 25, 20
SECS = ((0, 4, HA, True), (4, 8, HB, False), (8, 12, HC, True))  # x, x, H, ribbon


def stories(Hs):
    out, s = [], 0
    while s + 10 <= Hs:
        out.append((s, True))
        s += 10
    if s < Hs:
        out.append((s, False))
    return out


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(51)
    vox = {}
    conc, brick, brick_dark = C["concrete"], C["brick"], C["brick_dark"]
    glass, sash = C["glass"], C["steel_dark"]
    cop = C["coping"]
    box(vox, 0, 12, 0, 2, 0, 1, conc)
    box(vox, 0, 12, 22, 24, 0, 1, conc)
    box(vox, 0, 2, 2, 22, 0, 1, conc)
    box(vox, 10, 12, 2, 22, 0, 1, conc)
    box(vox, 0, 12, -1, 3, 0, 2, conc)   # plinth, ground story
    box(vox, 0, 12, 21, 25, 0, 2, conc)
    for sx0, sx1, Hs, rib in SECS:
        for s, full in stories(Hs):
            ztop = s + 10 if full else Hs
            for yo0, yo1, yp in ((-1, 3, 0), (21, 25, 23)):
                zc = s + 2 if s == 0 else s
                box(vox, sx0, sx0 + 1, yo0, yo1, zc, ztop, conc)
                box(vox, sx1 - 1, sx1, yo0, yo1, zc, ztop, conc)
                zlo = s if s > 0 else s + 2  # spandrel: no between-story gap
                box(vox, sx0 + 1, sx1 - 1, yp, yp + 1, zlo, ztop - 2 if full else ztop, brick)
                if full:
                    box(vox, sx0 + 1, sx1 - 1, yp, yp + 1, s + 2, s + 3, conc)
                    if rib:
                        for x in range(sx0 + 1, sx1 - 1):
                            for z in range(s + 3, s + 7):
                                vox[(x, yp, z)] = glass
                        for z in range(s + 3, s + 7):
                            vox[((sx0 + sx1) // 2, yp, z)] = sash
        box(vox, sx0, sx1, -1, 3, Hs - 2, Hs, conc)    # header at section top
        box(vox, sx0, sx1, 21, 25, Hs - 2, Hs, conc)
    for xb, Hlo, Hhi in ((4, HB, HA), (8, HC, HB)):    # step faces + coping
        box(vox, xb - 1, xb + 1, 0, 24, Hlo, Hhi, conc)
        box(vox, xb - 1, xb + 1, 0, 24, Hlo, Hlo + 1, cop)

    rx0, rx1, ry0, ry1 = 3, 9, 9, 15
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
    write_vox(os.path.join(here, "kit-frame-step-2to3-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-frame-step-2to3-v1_preview.png"), vox, PALETTE)
