#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT fuel tank rig part: ladder.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-15,15), y [-15,15).
  Authored at +(15,15); file min = (27,13,0), so frame = file + (+12,-2,0).
  RIG SLOT: ft_ladder_steel (part identity).

On the +x side, outside the shell (r=13): rails at game (14,+-1), z 0..18;
rungs every 2 z (z odd); 3 cage hoops (square rings) at z 6, 12, 16;
standoff brackets to the shell at z 4, 8, 12, 16; top platform
game x [12,17) y [-2,3) z 18..19. All ft_ladder_steel.

Slug: kit-lot-fueltank-ladder-v1.
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

FOOTPRINT = (27, 32, 13, 18, 0, 19)
OX, OY = 15, 15  # file = game + (15,15)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (15,15))."""
    random.seed(118)
    vox = {}
    lad = C["ft_ladder_steel"]

    def B(gx0, gx1, gy0, gy1, z0, z1):
        box(vox, gx0 + OX, gx1 + OX, gy0 + OY, gy1 + OY, z0, z1, lad)

    B(14, 15, -1, 0, 0, 18)      # rails
    B(14, 15, 1, 2, 0, 18)
    for z in range(1, 18, 2):    # rungs
        B(14, 15, -1, 2, z, z + 1)
    for z in (4, 8, 12, 16):    # standoff brackets to the shell
        B(13, 14, -1, 2, z, z + 1)
    for z in (6, 12, 16):       # cage hoops (square rings)
        for gx in range(13, 16):
            for gy in (-2, 2):
                vox[(gx + OX, gy + OY, z)] = lad
        for gy in range(-2, 3):
            for gx in (13, 15):
                vox[(gx + OX, gy + OY, z)] = lad
    B(12, 17, -2, 3, 18, 19)    # top platform
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-fueltank-ladder-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z9.png"), vox, PALETTE, 9)
