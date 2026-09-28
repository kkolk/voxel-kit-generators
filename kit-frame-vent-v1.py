#!/usr/bin/env python3
"""Strike Bay modular factory kit — FRAME roof vent. Steel flashing z 0..1, concrete louver box z 1..4 with steel slats, concrete cap z 4..5.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint x [0,4) x y [0,4), z [0,5]; trim may exceed 1 voxel along wall-face normals only.
  Seam rule: 2-wide columns centred on bay lines; each module writes its
  half on each walled face (full 2-wide columns at interior bay lines).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
Clutter: seats on any flat roof slab; single connected component to z=0.
Slug: kit-frame-vent-v1.
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

FOOTPRINT = (0, 4, 0, 4, 0, 5)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(54)
    vox = {}
    conc = C["concrete"]
    box(vox, 0, 4, 0, 4, 0, 1, C["steel_dark"])  # flashing
    box(vox, 1, 3, 1, 3, 1, 4, conc)            # louver box
    for z in range(1, 4):                        # slats, south + north
        box(vox, 1, 3, 0, 1, z, z + 1, C["steel_dark"])
        box(vox, 1, 3, 3, 4, z, z + 1, C["steel_dark"])
    box(vox, 0, 4, 0, 4, 4, 5, conc)            # cap
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
    write_vox(os.path.join(here, "kit-frame-vent-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-frame-vent-v1_preview.png"), vox, PALETTE)
