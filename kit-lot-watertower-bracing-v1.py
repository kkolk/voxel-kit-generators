#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT water tower rig part: X-bracing.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-14,14), y [-14,14), z 0..77.
  Authored at +(14,14); file min = (4,4,8), so frame = file + (-10,-10,0).
  Legs stand at game (+-10,+-10) with 3x3 section (game x [8,11)/[-11,-8)).
  RIG SLOT: wt_brace_steel (part identity).

X-braces on all 4 faces, z 8..48: 1-thick diagonals in the face planes
(game x=+-10 -> file x 4/24; game y=+-10 -> file y 4/24). Diagonal ends
land inside the leg sections, so the assembled union is one component.

Slug: kit-lot-watertower-bracing-v1.
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

FOOTPRINT = (4, 25, 4, 25, 8, 49)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (14,14)).

    Diagonals are drawn as 6-connected staircases: whenever the rounded
    span coordinate changes between z layers, the previous coordinate is
    repeated at the new z so no diagonal (non-6-connected) step remains.
    """
    random.seed(112)
    vox = {}
    br = C["wt_brace_steel"]

    def face(fixed, plane):
        prev_a = prev_b = None
        for z in range(8, 49):
            t = (z - 8) / 40.0
            a = int(4 + t * 20 + 0.5)    # file 4 -> 24 (game -10 -> +10)
            b = int(24 - t * 20 + 0.5)   # file 24 -> 4
            if plane == "yz":
                put = lambda v, zz: vox.__setitem__((fixed, v, zz), br)
            else:
                put = lambda v, zz: vox.__setitem__((v, fixed, zz), br)
            if prev_a is not None and a != prev_a:
                put(prev_a, z)           # stair intermediate
            if prev_b is not None and b != prev_b:
                put(prev_b, z)
            put(a, z)
            put(b, z)
            prev_a, prev_b = a, b

    face(24, "yz")   # east  (game x=+10)
    face(4, "yz")    # west  (game x=-10)
    face(24, "xz")   # north (game y=+10)
    face(4, "xz")    # south (game y=-10)
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-watertower-bracing-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z28.png"), vox, PALETTE, 28)
