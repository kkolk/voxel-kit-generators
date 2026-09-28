#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT water tower rig part: roof.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-14,14), y [-14,14), z 0..77.
  Authored at +(14,14); file min = (2,2,70), so frame = file + (-12,-12,0).
  RIG SLOT: wt_roof_steel (part identity).

Stepped pyramid z 70..77 (24 -> 6, 2 z per step), wt_roof_steel with light
rust (seed 115); iron_dark finial 1x1 z 77..79. Sits on the tank shell
(shell top z=70).

Slug: kit-lot-watertower-roof-v1.
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

FOOTPRINT = (2, 26, 2, 26, 70, 79)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (14,14))."""
    random.seed(115)
    vox = {}
    roof, rust, dark = C["wt_roof_steel"], C["rust"], C["iron_dark"]
    for z0, z1, s in ((70, 72, 24), (72, 74, 18), (74, 76, 12), (76, 77, 6)):
        h = s // 2
        for gx in range(-h, h):
            for gy in range(-h, h):
                ci = rust if random.random() < 0.02 else roof
                for z in range(z0, z1):
                    vox[(gx + 14, gy + 14, z)] = ci
    box(vox, 14, 15, 14, 15, 77, 79, dark)   # finial
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-watertower-roof-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z73.png"), vox, PALETTE, 73)
