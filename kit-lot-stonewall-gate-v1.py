#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT stone wall gate (pillars + opening).

GRID CONTRACT (see kit_contract.py): B=12 bay, S=10 story, T=2 wall.
Origin at footprint min corner, ground level, z-up. No slab, no yard.
Footprint [0,12) x [0,2) x [0,14). Stone variation random (seed 104);
coursing will not match abutting wall modules.

Pillars x 0..3 and x 9..12 (3x2), z 0..12 stone / stone_dark,
capstone caps z 12..14 (flush). 6-wide open gap x 3..9.

Slug: kit-lot-stonewall-gate-v1.
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

FOOTPRINT = (0, 12, 0, 2, 0, 14)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(104)
    vox = {}
    stone, dark, cap = C["stone"], C["stone_dark"], C["capstone"]
    for (px0, px1) in ((0, 3), (9, 12)):
        box(vox, px0, px1, 0, 2, 0, 12, stone)
        box(vox, px0, px1, 0, 2, 0, 1, dark)    # dark base course
        box(vox, px0, px1, 0, 2, 12, 14, cap)   # capstone cap
    for (x, y, z), ci in list(vox.items()):
        if ci == stone and random.random() < 0.18:
            vox[(x, y, z)] = dark
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and 0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-stonewall-gate-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z6.png"), vox, PALETTE, 6)
