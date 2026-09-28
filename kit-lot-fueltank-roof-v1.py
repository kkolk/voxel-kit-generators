#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT fuel tank rig part: roof.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-15,15), y [-15,15).
  Authored at +(15,15); file min = (2,2,16), so frame = file + (-13,-13,0).
  RIG SLOT: ft_roof (part identity).

Shallow cone z 16..21 (r 13 -> 4), ft_roof; vent neck r=2 z 21..22 with
r=3 cap z 22..23. Sits on the shell (shell top z=16).

Slug: kit-lot-fueltank-roof-v1.
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

FOOTPRINT = (2, 29, 2, 29, 16, 23)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (15,15))."""
    random.seed(117)
    vox = {}
    roof = C["ft_roof"]
    for z in range(16, 21):
        r = 13 - (z - 16) * 2.2
        for gx in range(-13, 14):
            for gy in range(-13, 14):
                if gx * gx + gy * gy <= r * r:
                    vox[(gx + 15, gy + 15, z)] = roof
    for gx in range(-2, 3):                       # vent neck r<=2, z 21..22
        for gy in range(-2, 3):
            if gx * gx + gy * gy <= 4:
                vox[(gx + 15, gy + 15, 21)] = roof
    for gx in range(-3, 4):                       # vent cap r<=3, z 22..23
        for gy in range(-3, 4):
            if gx * gx + gy * gy <= 9:
                vox[(gx + 15, gy + 15, 22)] = roof
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-fueltank-roof-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z18.png"), vox, PALETTE, 18)
