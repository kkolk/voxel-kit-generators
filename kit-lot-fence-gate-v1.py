#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT chain-link double gate.

GRID CONTRACT (see kit_contract.py): B=12 bay, S=10 story, T=2 wall.
Origin at footprint min corner, ground level, z-up. No slab, no yard.
Footprint [0,12) x [0,2) x [0,9).

Gate posts 2x2x9 iron at x 0..2 and x 10..12. Two closed leaves z 1..8,
each 4 wide (x 2..6 and x 6..10) with an iron frame border 1 and
checkerboard mesh ((x+z)%2==0) inside. (Leaves are 4 wide rather than 5 so
the leaf ends land on the posts instead of inside them.)

Slug: kit-lot-fence-gate-v1.
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

FOOTPRINT = (0, 12, 0, 2, 0, 9)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(107)
    vox = {}
    iron, mesh = C["iron"], C["mesh"]
    # leaves first; posts overwrite where they meet
    for lx0, lx1 in ((2, 6), (6, 10)):
        for x in range(lx0, lx1):
            for z in range(1, 8):
                edge = (x == lx0 or x == lx1 - 1 or z == 1 or z == 7)
                if edge:
                    vox[(x, 0, z)] = iron
                elif (x + z) % 2 == 0:
                    vox[(x, 0, z)] = mesh
    # gate posts
    box(vox, 0, 2, 0, 2, 0, 9, iron)
    box(vox, 10, 12, 0, 2, 0, 9, iron)
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and 0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-fence-gate-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z4.png"), vox, PALETTE, 4)
