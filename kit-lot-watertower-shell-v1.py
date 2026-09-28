#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT water tower rig part: tank shell.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-14,14), y [-14,14), z 0..77.
  Authored at +(14,14); file min = (2,2,52), so frame = file + (-12,-12,0).
  RIG SLOT: wt_tank_steel (part identity).

Tank z 52..70: 24x24 box (game x [-12,12), y [-12,12)) with 3x3 corner
cuts, 2-thick walls, wt_tank_steel; floor plate z 52..53; horizontal band
courses wt_roof_steel at z 58 and 64; rust streaks (seed 114). Sits on the
balcony deck ring (deck top z=51).

Slug: kit-lot-watertower-shell-v1.
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

FOOTPRINT = (2, 26, 2, 26, 52, 70)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (14,14))."""
    random.seed(114)
    vox = {}
    steel, band, rust = C["wt_tank_steel"], C["wt_roof_steel"], C["rust"]

    def corner(gx, gy):
        return ((gx < -9 or gx >= 9) and (gy < -9 or gy >= 9))

    for gx in range(-12, 12):
        for gy in range(-12, 12):
            if corner(gx, gy):
                continue
            fx, fy = gx + 14, gy + 14
            wall = gx < -10 or gx >= 10 or gy < -10 or gy >= 10
            if wall:
                for z in range(52, 70):
                    ci = band if z in (58, 64) else steel
                    if ci == steel and random.random() < 0.03:
                        ci = rust
                    vox[(fx, fy, z)] = ci
            else:
                vox[(fx, fy, 52)] = steel   # floor plate
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-watertower-shell-v1"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z60.png"), vox, PALETTE, 60)
