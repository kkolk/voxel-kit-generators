#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT fuel tank rig part: shell.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-15,15), y [-15,15).
  Authored at +(15,15); file min = (1,1,0), so frame = file + (-14,-14,0).
  RIG SLOT: ft_shell (part identity).

Cylinder r=13, z 0..16, ft_shell: 2-thick wall (11 < r <= 13), floor disc
z 0..1, proud top rim (13 < r <= 14) at z 15..16; vertical weld-seam rust
lines at 8 angles + sparse rust (seed 116).

Slug: kit-lot-fueltank-shell-v1.
"""
import math
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

FOOTPRINT = (1, 30, 1, 30, 0, 16)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (15,15))."""
    random.seed(116)
    vox = {}
    shell, rust = C["ft_shell"], C["rust"]

    def wall(gx, gy):
        r2 = gx * gx + gy * gy
        return 121 < r2 <= 169

    for gx in range(-14, 15):
        for gy in range(-14, 15):
            r2 = gx * gx + gy * gy
            fx, fy = gx + 15, gy + 15
            if r2 <= 169:
                vox[(fx, fy, 0)] = shell          # floor disc
            if wall(gx, gy):
                for z in range(0, 16):
                    ci = rust if random.random() < 0.015 else shell
                    vox[(fx, fy, z)] = ci
            if 169 < r2 <= 196:                   # proud top rim
                vox[(fx, fy, 15)] = shell
    # vertical weld seams: rust lines at 8 angles
    for a in range(0, 360, 45):
        dx = round(12 * math.cos(math.radians(a)))
        dy = round(12 * math.sin(math.radians(a)))
        if wall(dx, dy):
            for z in range(0, 16):
                vox[(dx + 15, dy + 15, z)] = rust
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-fueltank-shell-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z8.png"), vox, PALETTE, 8)
