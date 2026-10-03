#!/usr/bin/env python3
"""kit-frame-roof-mast-v1 — minimal untapered steel rooftop mast for the frame factory.

A constant-cross-section (untapered) steel mast: base frame, 4x4 box column,
stiffeners, cap plate, whip antenna. Seats on the frame flat roof at
+5,+7,z=H+2 (structure origin = roof slab top).

GRID: z-up. Footprint x [-4,4) x y [-4,4), z [0,33).
Slug: kit-frame-roof-mast-v1.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import (FRAME_PALETTE, CI, box, floater_sweep,
                          write_vox, render_preview)

PALETTE = [
    ("concrete",      (170, 166, 158)),
    ("concrete_dark", (112, 108, 100)),
    ("coping",        (202, 198, 190)),
    ("brick",         (150,  90,  66)),
    ("brick_dark",    (120,  68,  50)),
    ("glass",         ( 72,  98, 118)),
    ("glass_dark",    ( 44,  62,  78)),
    ("steel",         (122, 126, 134)),
    ("steel_dark",    ( 62,  64,  72)),
    ("white",         (235, 235, 230)),
    ("window",        ( 18,  26,  38)),
    ("dark",          ( 32,  34,  40)),
    ("green",         (100, 118,  94)),
    ("green_dark",    ( 70,  88,  68)),
    ("roof",          (100, 104, 100)),
]
C = CI(PALETTE)
vox = {}
here = os.path.dirname(os.path.abspath(__file__))

# --- base frame: 4 feet + base plate (feet sit on the roof slab)
for sx in (-1, 1):
    for sy in (-1, 1):
        x0 = 2 if sx > 0 else -4
        y0 = 2 if sy > 0 else -4
        box(vox, x0, x0 + 2, y0, y0 + 2, 0, 2, C["steel_dark"])
box(vox, -4, 4, -4, 4, 2, 3, C["steel_dark"])          # base plate 8x8

# --- untapered column: constant 4x4 cross-section, 20 tall
box(vox, -2, 2, -2, 2, 3, 23, C["steel_dark"])

# --- stiffener plates: base plate to column, one per face
box(vox, 2, 3, -2, 2, 3, 8, C["steel"])                # +x
box(vox, -3, -2, -2, 2, 3, 8, C["steel"])              # -x
box(vox, -2, 2, 2, 3, 3, 8, C["steel"])                # +y
box(vox, -2, 2, -3, -2, 3, 8, C["steel"])              # -y

# --- top: cap plate + whip antenna + tip
box(vox, -3, 3, -3, 3, 23, 24, C["steel"])             # cap 6x6
box(vox, 0, 1, 0, 1, 24, 32, C["steel_dark"])          # whip 8 tall
box(vox, 0, 1, 0, 1, 32, 33, C["white"])              # tip

# --- footprint guard + validation
for (x, y, z) in vox:
    assert -4 <= x < 4, "x breach %d" % x
    assert -4 <= y < 4, "y breach %d" % y
    assert 0 <= z < 33, "z breach %d" % z
bad = floater_sweep(vox)
assert not bad, "floaters: %d" % len(bad)

write_vox(os.path.join(here, "kit-frame-roof-mast-v1.vox"), vox, PALETTE)
render_preview(os.path.join(here, "kit-frame-roof-mast-v1_preview.png"),
               vox, PALETTE)
print(f"kit-frame-roof-mast-v1: {len(vox)} voxels, 1 component")
