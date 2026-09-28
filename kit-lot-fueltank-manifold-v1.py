#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT fuel tank rig part: manifold.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-15,15), y [-15,15).
  Authored at +(15,15); file min = (13,28,1), so frame = file + (-2,+13,0).
  RIG SLOT: ft_pipe (part identity).

Front (+y): horizontal pipe game x [-1,1) y [13,19) z 1..3 (2x2), ft_pipe,
entering the shell wall (r=13 at game y=13); 2 vertical valve bodies
(y [14,16) and [17,19), z 1..5); rust valve wheel (disc r=2, z 5..6) atop
the first body; sparse rust (seed 119).

Slug: kit-lot-fueltank-manifold-v1.
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

FOOTPRINT = (13, 18, 28, 34, 1, 6)
OX, OY = 15, 15  # file = game + (15,15)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (15,15))."""
    random.seed(119)
    vox = {}
    pipe, rust = C["ft_pipe"], C["rust"]

    def B(gx0, gx1, gy0, gy1, z0, z1, ci):
        box(vox, gx0 + OX, gx1 + OX, gy0 + OY, gy1 + OY, z0, z1, ci)

    B(-1, 1, 13, 19, 1, 3, pipe)     # horizontal pipe
    B(-1, 1, 14, 16, 1, 5, pipe)     # valve bodies
    B(-1, 1, 17, 19, 1, 5, pipe)
    for gx in range(-2, 3):          # valve wheel (disc r=2) at z 5..6
        for gy in range(13, 18):
            if gx * gx + (gy - 15) * (gy - 15) <= 4:
                vox[(gx + OX, gy + OY, 5)] = rust
    for (x, y, z), ci in list(vox.items()):
        if ci == pipe and random.random() < 0.03:
            vox[(x, y, z)] = rust
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-fueltank-manifold-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z2.png"), vox, PALETTE, 2)
