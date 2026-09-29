#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT water tower rig part: balcony (v2).

v2 rescale per kkolk/strike-bay#167 (see leg-fl-v2 docstring): the balcony
is now circular to match the round tank, like the original water_tower_v1.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-10,10), y [-10,10), z 0..54.
  Authored at +(10,10); file min = (1,1,28), so frame = file + (-9,-9,0).
  RIG SLOT: wood (part identity).

z 30..32: wood deck ring, r 7.5..9.5; iron railing posts (8, r=9) +
2 rails (z 34..35); iron_dark corbels (2x2, z 28..30) on the outer side
of each leg, tying the deck to the leg tops. The deck ring sits on the
leg tops (legs end z=30), so the assembled union connects.

Slug: kit-lot-watertower-balcony-v2.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import LOT_PALETTE, CI, box, floater_sweep, write_vox, render_preview, render_slice

PALETTE = [
    ("stone", (148, 142, 130)),
    ("stone_dark", (110, 104, 94)),
    ("capstone", (200, 196, 188)),
    ("iron", (70, 74, 82)),
    ("iron_dark", (38, 40, 46)),
    ("mesh", (105, 110, 120)),
    ("wood", (125, 92, 62)),
    ("wood_dark", (90, 66, 44)),
    ("concrete", (170, 166, 158)),
    ("wt_leg_steel", (120, 124, 132)),
    ("wt_brace_steel", (96, 100, 108)),
    ("wt_tank_steel", (158, 162, 170)),
    ("wt_roof_steel", (110, 114, 122)),
    ("ft_shell", (108, 122, 100)),
    ("ft_roof", (90, 94, 90)),
    ("ft_ladder_steel", (80, 84, 90)),
    ("ft_pipe", (110, 114, 120)),
    ("rust", (142, 82, 50)),
]
C = CI(PALETTE)

FOOTPRINT = (1, 20, 1, 20, 28, 36)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (10,10))."""
    random.seed(213)
    vox = {}
    wood, iron, dark = C["wood"], C["iron"], C["iron_dark"]
    # deck ring: r 7.5..9.5 around file (10,10)
    for fx in range(1, 20):
        for fy in range(1, 20):
            d2 = (fx - 10) ** 2 + (fy - 10) ** 2
            if 56.25 <= d2 <= 90.25:
                for z in (30, 31):
                    vox[(fx, fy, z)] = wood
    # railing posts: 8 at r=9
    for k in range(8):
        a = k * math.pi / 4
        fx = 10 + round(9 * math.cos(a))
        fy = 10 + round(9 * math.sin(a))
        box(vox, fx, fx + 1, fy, fy + 1, 32, 36, iron)
    # railing rails: 2 courses, r 8.5..9.5
    for fx in range(1, 20):
        for fy in range(1, 20):
            d2 = (fx - 10) ** 2 + (fy - 10) ** 2
            if 72.25 <= d2 <= 90.25:
                vox[(fx, fy, 34)] = iron
                vox[(fx, fy, 35)] = iron
    # corbels: 2x2 iron_dark, z 28..30, on each leg's two outer sides.
    # Shares a full face with the leg (z 28..30 vs leg x/y ranges) and
    # meets the deck underside at z=30; kept clear of the bracing planes
    # so the union merge never recolours brace voxels.
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        lx0 = 15 if sx > 0 else 3   # leg file min-x (leg is 2x2)
        ly0 = 15 if sy > 0 else 3   # leg file min-y
        # outer-x side: 2 wide in y like the leg, 2 deep in x past the leg face
        cx0, cx1 = (lx0 + 2, lx0 + 4) if sx > 0 else (lx0 - 2, lx0)
        box(vox, cx0, cx1, ly0, ly0 + 2, 28, 30, dark)
        # outer-y side
        cy0, cy1 = (ly0 + 2, ly0 + 4) if sy > 0 else (ly0 - 2, ly0)
        box(vox, lx0, lx0 + 2, cy0, cy1, 28, 30, dark)
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-watertower-balcony-v2"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z31.png"), vox, PALETTE, 31)
