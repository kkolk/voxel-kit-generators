#!/usr/bin/env python3
"""Strike Bay modular factory kit — FRAME pipe run. Three concrete saddles (x 1, 6, 11) z 0..1 carrying a 2x2 steel pipe z 1..3 along x, with steel collars at the saddles.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint x [0,12) x y [0,3), z [0,3]; trim may exceed 1 voxel along wall-face normals only.
  Seam rule: 2-wide columns centred on bay lines; each module writes its
  half on each walled face (full 2-wide columns at interior bay lines).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
Clutter: seats on any flat roof slab.
Slug: kit-frame-piperun-v1.
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

FOOTPRINT = (0, 12, 0, 3, 0, 3)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(57)
    vox = {}
    box(vox, 1, 2, 1, 2, 0, 1, C["concrete_dark"])   # saddles
    box(vox, 6, 7, 1, 2, 0, 1, C["concrete_dark"])
    box(vox, 11, 12, 1, 2, 0, 1, C["concrete_dark"])
    box(vox, 0, 12, 0, 2, 1, 3, C["steel"])         # pipe
    for xs in (1, 6, 11):                            # collars
        box(vox, xs, xs + 1, 0, 2, 1, 3, C["steel_dark"])
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
    write_vox(os.path.join(here, "kit-frame-piperun-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-frame-piperun-v1_preview.png"), vox, PALETTE)
