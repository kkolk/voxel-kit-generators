#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT water tower rig part: rear-right leg (v2).

v2 rescale per kkolk/strike-bay#167 (see leg-fl-v2 docstring).

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-10,10), y [-10,10), z 0..54.
  Authored at +(10,10); file min = (14,2,0), so frame = file + (+4,-8,0).
  Legs are 2x2 centred at (+-6,+-6); this leg: game x [5,7), y [-7,-5).
  RIG SLOT: wt_leg_steel (part identity).

Leg 2x2 z 0..30 wt_leg_steel; iron_dark base plate 4x4 z 0..1;
2-thick tie plates (4x4) at z 10 and 20.

Slug: kit-lot-watertower-leg-rr-v2.
"""
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

# file coords = game coords + (10, 10); this leg: game x [5,7), y [-7,-5)
LX0, LX1, LY0, LY1 = 15, 17, 3, 5
PX0, PX1, PY0, PY1 = 14, 18, 2, 6   # plates (game [4,8) x [-8,-4))
FOOTPRINT = (14, 18, 2, 6, 0, 30)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (10,10))."""
    random.seed(208)
    vox = {}
    steel, dark = C["wt_leg_steel"], C["iron_dark"]
    box(vox, LX0, LX1, LY0, LY1, 0, 30, steel)
    box(vox, PX0, PX1, PY0, PY1, 0, 1, dark)
    for pz in (10, 20):
        box(vox, PX0, PX1, PY0, PY1, pz, pz + 1, steel)
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and 0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-watertower-leg-rr-v2"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z15.png"), vox, PALETTE, 15)
