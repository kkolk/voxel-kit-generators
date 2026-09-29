#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT water tower rig part: roof (v2).

v2 rescale per kkolk/strike-bay#167 (see leg-fl-v2 docstring): a stepped
circular cone to sit on the round v2 tank, instead of the v1 square
pyramid.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-10,10), y [-10,10), z 0..54.
  Authored at +(10,10); file min = (2,2,44), so frame = file + (-8,-8,0).
  RIG SLOT: wt_roof_steel (part identity).

Stepped cone z 44..51 (r 8 -> 6 -> 4 -> 2), wt_roof_steel with light rust
(seed 215); iron_dark finial 1x1 z 51..54. Sits on the tank shell
(shell top z=44).

Slug: kit-lot-watertower-roof-v2.
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

FOOTPRINT = (2, 19, 2, 19, 44, 54)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (10,10))."""
    random.seed(215)
    vox = {}
    roof, rust, dark = C["wt_roof_steel"], C["rust"], C["iron_dark"]
    for z0, z1, r in ((44, 46, 8), (46, 48, 6), (48, 50, 4), (50, 51, 2)):
        r2max = r * r
        for fx in range(10 - r, 10 + r + 1):
            for fy in range(10 - r, 10 + r + 1):
                if (fx - 10) ** 2 + (fy - 10) ** 2 <= r2max:
                    for z in range(z0, z1):
                        ci = rust if random.random() < 0.02 else roof
                        vox[(fx, fy, z)] = ci
    box(vox, 10, 11, 10, 11, 51, 54, dark)   # finial
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-watertower-roof-v2"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z47.png"), vox, PALETTE, 47)
