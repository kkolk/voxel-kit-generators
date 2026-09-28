#!/usr/bin/env python3
"""Strike Bay modular factory kit — FRAME covered loading dock, 1 story. Concrete platform z 0..3 with a dark edge band, two concrete columns (x 2..4 / 8..10, y 8..10) carrying a roof-grey canopy slab z 9..10 with a concrete fascia z 8..10. Back (y=0) open.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint x [0,12) x y [0,10), z [0,10]; trim may exceed 1 voxel along wall-face normals only.
  Seam rule: 2-wide columns centred on bay lines; each module writes its
  half on each walled face (full 2-wide columns at interior bay lines).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
Seats on grade; no parapet.
Slug: kit-frame-dock-1s-v1.
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

FOOTPRINT = (0, 12, 0, 10, 0, 10)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(53)
    vox = {}
    conc, cdark = C["concrete"], C["concrete_dark"]
    roof = C["roof"]
    box(vox, 0, 12, 0, 10, 0, 2, conc)      # platform
    box(vox, 0, 12, 0, 10, 2, 3, conc)
    box(vox, 0, 12, 0, 1, 2, 3, cdark)      # dark edge band
    box(vox, 0, 12, 9, 10, 2, 3, cdark)
    box(vox, 0, 1, 1, 9, 2, 3, cdark)
    box(vox, 11, 12, 1, 9, 2, 3, cdark)
    box(vox, 2, 4, 8, 10, 0, 9, conc)       # columns
    box(vox, 8, 10, 8, 10, 0, 9, conc)
    box(vox, 0, 12, 0, 10, 9, 10, roof)     # canopy slab
    box(vox, 0, 12, 0, 1, 8, 10, conc)      # fascia
    box(vox, 0, 12, 9, 10, 8, 10, conc)
    box(vox, 0, 1, 1, 9, 8, 10, conc)
    box(vox, 11, 12, 1, 9, 8, 10, conc)
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
    write_vox(os.path.join(here, "kit-frame-dock-1s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-frame-dock-1s-v1_preview.png"), vox, PALETTE)
