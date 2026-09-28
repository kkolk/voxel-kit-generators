#!/usr/bin/env python3
"""Strike Bay modular factory kit — FRAME enclosed walkway, 1 story. Floor z 0..1, concrete columns + brick infill walls on the y=0 and y=8 faces (glass ribbon z 3..6), open ends at x=0 and x=12 with a concrete surround around the y 2..6 / z 1..7 opening.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint x [0,12) x y [0,8), trim y -1, z [0,11]; trim may exceed 1 voxel along wall-face normals only.
  Seam rule: 2-wide columns centred on bay lines; each module writes its
  half on each walled face (full 2-wide columns at interior bay lines).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
Canopy slab z 8..9, parapet z 9..10, coping z 10..11.
Slug: kit-frame-walkway-1s-v1.
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

FOOTPRINT = (0, 12, -1, 9, 0, 11)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(52)
    vox = {}
    conc, brick, glass = C["concrete"], C["brick"], C["glass"]
    sash, roof, cop = C["steel_dark"], C["roof"], C["coping"]
    box(vox, 0, 12, 0, 8, 0, 1, conc)      # floor
    box(vox, 0, 12, -1, 3, 0, 2, conc)     # plinth
    box(vox, 0, 12, 5, 9, 0, 2, conc)
    for yo0, yo1, yp in ((-1, 3, 0), (5, 9, 7)):
        box(vox, 0, 1, yo0, yo1, 2, 8, conc)
        box(vox, 5, 7, yo0, yo1, 2, 8, conc)
        box(vox, 11, 12, yo0, yo1, 2, 8, conc)
        box(vox, 1, 11, yp, yp + 1, 2, 6, brick)
        box(vox, 1, 11, yp, yp + 1, 2, 3, conc)
        for x in range(2, 10):
            for z in range(3, 6):
                vox[(x, yp, z)] = glass
        for x in (4, 7):
            for z in range(3, 6):
                vox[(x, yp, z)] = sash
        box(vox, 0, 12, yo0, yo1, 6, 8, conc)  # top band
    for xe in (0, 11):                        # end surrounds, openings y 2..6 z 1..7
        box(vox, xe, xe + 1, 0, 8, 0, 1, conc)
        box(vox, xe, xe + 1, 0, 8, 7, 8, conc)
        box(vox, xe, xe + 1, 0, 2, 1, 7, conc)
        box(vox, xe, xe + 1, 6, 8, 1, 7, conc)
    box(vox, 0, 12, 0, 8, 8, 9, roof)        # canopy slab
    box(vox, 0, 12, 0, 1, 9, 10, conc)       # parapet
    box(vox, 0, 12, 7, 8, 9, 10, conc)
    box(vox, 0, 12, -1, 2, 10, 11, cop)      # coping
    box(vox, 0, 12, 6, 9, 10, 11, cop)
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
    write_vox(os.path.join(here, "kit-frame-walkway-1s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-frame-walkway-1s-v1_preview.png"), vox, PALETTE)
