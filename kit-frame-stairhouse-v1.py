#!/usr/bin/env python3
"""Strike Bay modular factory kit — FRAME stairhouse. Hollow concrete box z 0..7 with a dark door on the +x face (z 1..5), cap slab z 7..8, coping z 8..9.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint x [0,8) x y [0,6), z [0,9]; trim may exceed 1 voxel along wall-face normals only.
  Seam rule: 2-wide columns centred on bay lines; each module writes its
  half on each walled face (full 2-wide columns at interior bay lines).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
Clutter: seats on any flat roof slab.
Slug: kit-frame-stairhouse-v1.
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

FOOTPRINT = (0, 8, 0, 6, 0, 9)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(56)
    vox = {}
    conc = C["concrete"]
    box(vox, 0, 8, 0, 1, 0, 7, conc)      # walls
    box(vox, 0, 8, 5, 6, 0, 7, conc)
    box(vox, 0, 1, 1, 5, 0, 7, conc)
    box(vox, 7, 8, 1, 5, 0, 7, conc)
    box(vox, 7, 8, 2, 4, 1, 5, C["dark"])  # door, +x face
    box(vox, 0, 8, 0, 6, 7, 8, conc)      # cap slab
    box(vox, 0, 8, 0, 6, 8, 9, C["coping"])
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
    write_vox(os.path.join(here, "kit-frame-stairhouse-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-frame-stairhouse-v1_preview.png"), vox, PALETTE)
