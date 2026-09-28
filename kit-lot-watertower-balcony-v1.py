#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT water tower rig part: balcony.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-14,14), y [-14,14), z 0..77.
  Authored at +(14,14); file min = (1,1,47), so frame = file + (-13,-13,0).
  RIG SLOT: wood (part identity).

z 50..54: wood deck ring, game x [-13,13) y [-13,13), 3 wide (20x20 hole
for the tank); iron railing posts + 2 rails (z 52..54); iron_dark support
brackets (diagonals) under the deck at the 4 leg lines. The deck ring sits
on the leg tops (legs end z=50), so the assembled union connects.

Slug: kit-lot-watertower-balcony-v1.
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

FOOTPRINT = (1, 28, 1, 28, 47, 54)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (14,14))."""
    random.seed(113)
    vox = {}
    wood, iron, dark = C["wood"], C["iron"], C["iron_dark"]
    # deck ring: file 1..27 (game -13..13), 3 wide
    for fx in range(1, 28):
        for fy in range(1, 28):
            if fx < 4 or fx >= 24 or fy < 4 or fy >= 24:
                vox[(fx, fy, 50)] = wood
    # railing posts (file coords; game x -12..12 step 4 at y=+-12, etc.)
    for fx in range(2, 28, 4):
        for fy in (2, 26):
            box(vox, fx, fx + 1, fy, fy + 1, 51, 54, iron)
    for fy in range(6, 24, 4):
        for fx in (2, 26):
            box(vox, fx, fx + 1, fy, fy + 1, 51, 54, iron)
    # railing rails, 2 courses
    for fx in range(2, 27):
        for fy in (2, 26):
            vox[(fx, fy, 52)] = iron
            vox[(fx, fy, 53)] = iron
    for fy in range(2, 27):
        for fx in (2, 26):
            vox[(fx, fy, 52)] = iron
            vox[(fx, fy, 53)] = iron
    # support brackets: 6-connected stair diagonals from the leg lines
    # out under the deck edge (kept clear of the leg sections so the union
    # merge never recolours leg faces)
    for fy in (4, 24):            # east/west faces at game y=+-10
        for fx, z in ((25, 47), (25, 48), (26, 48), (26, 49)):
            vox[(fx, fy, z)] = dark      # game x 11->12
        for fx, z in ((2, 47), (2, 48), (1, 48), (1, 49)):
            vox[(fx, fy, z)] = dark      # game x -12->-13
    for fx in (4, 24):            # north/south faces at game x=+-10
        for fy, z in ((25, 47), (25, 48), (26, 48), (26, 49)):
            vox[(fx, fy, z)] = dark
        for fy, z in ((2, 47), (2, 48), (1, 48), (1, 49)):
            vox[(fx, fy, z)] = dark
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-watertower-balcony-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z50.png"), vox, PALETTE, 50)
