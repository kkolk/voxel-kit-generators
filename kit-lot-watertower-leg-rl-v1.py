#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT water tower rig part: rear-left leg.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-14,14), y [-14,14), z 0..77.
  Authored at +(14,14); file min = (2,2,0), so frame = file + (-12,-12,0).
  Legs are 3x3 centred at (+-10,+-10); this leg: game x [-11,-8), y [-11,-8).
  RIG SLOT: wt_leg_steel (part identity).

Leg 3x3 z 0..50 wt_leg_steel; iron_dark base plate 5x5 z 0..1;
1-thick cross-brace plates (5x5) at z 10, 20, 30, 40.

Slug: kit-lot-watertower-leg-rl-v1.
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

# file coords = game coords + (14, 14); this leg: game x [-11,-8), y [-11,-8)
LX0, LX1, LY0, LY1 = 3, 6, 3, 6
PX0, PX1, PY0, PY1 = 2, 7, 2, 7   # base plate (game [-12,-7) x [-12,-7))
FOOTPRINT = (2, 7, 2, 7, 0, 50)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (14,14))."""
    random.seed(110)
    vox = {}
    steel, dark = C["wt_leg_steel"], C["iron_dark"]
    box(vox, LX0, LX1, LY0, LY1, 0, 50, steel)
    box(vox, PX0, PX1, PY0, PY1, 0, 1, dark)
    for pz in (10, 20, 30, 40):
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
    slug = "kit-lot-watertower-leg-rl-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z25.png"), vox, PALETTE, 25)
