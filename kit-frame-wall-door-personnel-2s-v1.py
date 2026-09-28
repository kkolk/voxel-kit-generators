#!/usr/bin/env python3
"""Strike Bay modular factory kit — FRAME wall bay, personnel-door variant, 2 stories.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint [0,12) x [0,24); trim may use y in [-1,25) (face normal only).
  Seam rule: 2-wide columns centred on bay lines, each module writing its
  half (x0..x0+1 and x0+11..x0+12) on each walled face.
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
  Wall top H=20.

FRAME story rhythm (base s): plinth z s+0..s+2 proud 1 (ground only);
2-wide columns on bay lines, z s+2..s+10 (ground) / s..s+10 (upper), proud 1;
ground story: personnel doors x 4..7 z 1..8 on both faces (dark leaf z 2..6, steel_dark surround); upper stories: glass ribbons;
concrete sill z s+2..s+3, brick spandrel z s..s+2 under the sill
(upper stories, solid wall below the window band),
header beam z s+8..s+10 proud 1.

Slug: kit-frame-wall-door-personnel-2s-v1.  Cloned from golden reference kit-frame-wall-window-2s-v1.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import (B, S, T, FRAME_PALETTE, CI, box, floater_sweep,
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
]
C = CI(PALETTE)

FOOTPRINT = (0, 12, 0, 24, 0, 20)   # trim may use y in [-1, 25)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(62)
    vox = {}
    concrete, brick, brick_dark = C["concrete"], C["brick"], C["brick_dark"]
    glass, sash = C["glass"], C["steel_dark"]
    green, dark = C["green"], C["dark"]
    H = 20

    # ---- floor edge: perimeter strip, z 0..1
    box(vox, 0, 12, 0, 2, 0, 1, concrete)
    box(vox, 0, 12, 22, 24, 0, 1, concrete)
    box(vox, 0, 2, 2, 22, 0, 1, concrete)
    box(vox, 10, 12, 2, 22, 0, 1, concrete)

    # ---- plinth, proud 1 (ground story)
    box(vox, 0, 12, -1, 3, 0, 2, concrete)
    box(vox, 0, 12, 21, 25, 0, 2, concrete)

    stories = [0, 10]
    for s in stories:
        zc0 = s + 2 if s == 0 else s       # columns start above plinth
        for (ya, yb, face) in ((0, 2, 0), (22, 24, 23)):
            yo0, yo1 = (-1, 3) if ya == 0 else (21, 25)   # proud 1
            # half-columns on bay lines (seam rule)
            box(vox, 0, 1, yo0, yo1, zc0, s + 10, concrete)
            box(vox, 11, 12, yo0, yo1, zc0, s + 10, concrete)
            # brick infill, recessed 1 behind the column face
            box(vox, 1, 11, face, face + 1, s + 2, s + 8, brick)
            if s > 0:  # spandrel: solid brick below the sill (no between-story gap)
                box(vox, 1, 11, face, face + 1, s, s + 2, brick)
            if s == 0:
                # ---- personnel door: opening x 4..7, z 1..8 (both faces)
                box(vox, 4, 7, face, face + 1, 1, 2, concrete)   # threshold
                for jx in (3, 7):                                # steel jambs
                    box(vox, jx, jx + 1, face, face + 1, 1, 7, sash)
                box(vox, 3, 8, face, face + 1, 7, 8, sash)        # steel header
                box(vox, 4, 7, face, face + 1, 2, 6, dark)        # leaf
                for x in (1, 2, 3, 8, 9, 10):                    # sill stubs
                    vox[(x, face, s + 2)] = concrete
            else:
                        for x in range(1, 11):                        # concrete sill
                            vox[(x, face, s + 2)] = concrete
                        for x in range(2, 10):                        # glass ribbon
                            for z in range(s + 3, s + 7):
                                vox[(x, face, z)] = glass
                        for x in (4, 7):                              # mullions
                            for z in range(s + 3, s + 7):
                                vox[(x, face, z)] = sash
            # header beam band, proud 1, full bay width
            box(vox, 0, 12, yo0, yo1, s + 8, s + 10, concrete)


    # ---- sealed interior room (damage reveal), concrete + steel
    rx0, rx1, ry0, ry1 = 3, 9, 9, 15
    box(vox, rx0, rx1, ry0, ry1, 0, 1, concrete)
    for z in range(1, 7):
        for x in range(rx0, rx1):
            vox[(x, ry0, z)] = C["concrete_dark"]
            vox[(x, ry1 - 1, z)] = C["concrete_dark"]
        for y in range(ry0, ry1):
            vox[(rx0, y, z)] = C["concrete_dark"]
            vox[(rx1 - 1, y, z)] = C["concrete_dark"]
    for x in range(5, 7):
        for z in range(1, 4):
            vox[(x, ry0, z)] = C["dark"]
    box(vox, rx0, rx1, ry0, ry1, 6, 7, C["steel_dark"])

    # ---- subtle weathering
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
    write_vox(os.path.join(here, "kit-frame-wall-door-personnel-2s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-frame-wall-door-personnel-2s-v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "kit-frame-wall-door-personnel-2s-v1_slice_z5.png"), vox, PALETTE, 5)
