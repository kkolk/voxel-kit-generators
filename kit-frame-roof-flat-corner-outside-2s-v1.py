#!/usr/bin/env python3
"""Strike Bay modular factory kit — FRAME flat roof tile for outside corners, 2-story hall. Slab + south/west parapets + coping.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint x [0,24) x y [0,24), trim x/y -1 (face normals), z [H,H+6], H=20; trim may exceed 1 voxel along wall-face normals only.
  Seam rule: 2-wide columns centred on bay lines; each module writes its
  half on each walled face (full 2-wide columns at interior bay lines).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
Seats on the outside corner piece at H=20.
Slug: kit-frame-roof-flat-corner-outside-2s-v1.
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

FOOTPRINT = (-1, 25, -1, 25, 0, 26)

H = 20


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(44)
    vox = {}
    conc, roof, cop = C["concrete"], C["roof"], C["coping"]
    box(vox, 0, 24, 0, 24, H, H + 2, roof)
    box(vox, 0, 24, 0, 1, H + 2, H + 5, conc)   # parapets: south + west faces
    box(vox, 0, 1, 0, 24, H + 2, H + 5, conc)
    box(vox, -1, 24, -1, 2, H + 5, H + 6, cop)  # closed corner
    box(vox, -1, 2, -1, 24, H + 5, H + 6, cop)
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
    write_vox(os.path.join(here, "kit-frame-roof-flat-corner-outside-2s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-frame-roof-flat-corner-outside-2s-v1_preview.png"), vox, PALETTE)
