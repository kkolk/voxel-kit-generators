#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT chain-link fence, L corner.

GRID CONTRACT (see kit_contract.py): B=12 bay, S=10 story, T=2 wall.
Origin at footprint min corner, ground level, z-up. No slab, no yard.
Footprint [0,12) x [0,12) x [0,8). The corner piece owns the whole
2x2 corner post at (0..2, 0..2).

X-run: y 0..1, posts at x 0,4,8,11, rails z 2, 4, 6 (middle rail keeps
every checkerboard mesh cell 6-connected), mesh (x+z)%2==0.
Y-run: x 0..1, posts at y 0,4,8,11, rails z 2, 4, 6, mesh (y+z)%2==0.
Corner post 2x2x8 iron at x 0..2, y 0..2.

Slug: kit-lot-fence-corner-v1.
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

FOOTPRINT = (0, 12, 0, 12, 0, 8)
POSTS = (0, 4, 8, 11)
RAIL_Z = (2, 4, 6)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(106)
    vox = {}
    iron, mesh = C["iron"], C["mesh"]
    # x-run (y 0..1)
    for px in POSTS:
        box(vox, px, px + 1, 0, 1, 0, 8, iron)
    for rz in RAIL_Z:
        box(vox, 0, 12, 0, 1, rz, rz + 1, iron)
    for x in range(12):
        if x in POSTS:
            continue
        for z in range(8):
            if z in RAIL_Z:
                continue
            if (x + z) % 2 == 0:
                vox[(x, 0, z)] = mesh
    # y-run (x 0..1)
    for py in POSTS:
        box(vox, 0, 1, py, py + 1, 0, 8, iron)
    for rz in RAIL_Z:
        box(vox, 0, 1, 0, 12, rz, rz + 1, iron)
    for y in range(12):
        if y in POSTS:
            continue
        for z in range(8):
            if z in RAIL_Z:
                continue
            if (y + z) % 2 == 0:
                vox[(0, y, z)] = mesh
    # corner post (owns the 2x2 corner)
    box(vox, 0, 2, 0, 2, 0, 8, iron)
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and 0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-fence-corner-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z4.png"), vox, PALETTE, 4)
