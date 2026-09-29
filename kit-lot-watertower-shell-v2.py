#!/usr/bin/env python3
"""Strike Bay modular factory kit — LOT water tower rig part: tank shell (v2).

v2 rescale per kkolk/strike-bay#167 (see leg-fl-v2 docstring): the v1 shell
was a square ring with gaps at the corners; v2 is a round, closed tank —
cylinder wall + ellipsoidal dish bottom, like the original water_tower_v1.

RIG PART contract (see kit_contract.py):
  Shared design frame: game x [-10,10), y [-10,10), z 0..54.
  Authored at +(10,10); file min = (1,1,25), so frame = file + (-9,-9,0).
  RIG SLOT: wt_tank_steel (part identity).

Cylinder wall r 7.5..8.5 z 32..44 (sits on the balcony deck, top z=32);
ellipsoidal dish bottom (3-thick, tip z~25 at the centre, edge meeting the
wall at z 32..34 — the tank's closed bottom); proud course bands r
8.5..9.5 at z 37 and 41 with iron_dark rivet dots every 30 degrees; light
rust streaking on the wall (seed 214).

Slug: kit-lot-watertower-shell-v2.
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

FOOTPRINT = (1, 20, 1, 20, 25, 44)


def build_module():
    """Return (vox dict, footprint) in file coords (frame + (10,10))."""
    random.seed(214)
    vox = {}
    steel, band, rivet, rust = C["wt_tank_steel"], C["wt_roof_steel"], C["iron_dark"], C["rust"]

    # cylinder wall: r 7.5..8.5 (17 wide), z 32..44
    for fx in range(1, 20):
        for fy in range(1, 20):
            d2 = (fx - 10) ** 2 + (fy - 10) ** 2
            if 56.25 <= d2 <= 72.25:
                for z in range(32, 44):
                    ci = steel
                    if random.random() < 0.03:
                        ci = rust
                    vox[(fx, fy, z)] = ci
    # proud course bands at z 37 and 41, with rivet dots every 30 degrees
    for fx in range(1, 20):
        for fy in range(1, 20):
            d2 = (fx - 10) ** 2 + (fy - 10) ** 2
            if 72.25 < d2 <= 90.25:
                ang = int(round(math.degrees(math.atan2(fy - 10, fx - 10)))) % 360
                ci = rivet if ang % 30 == 0 else band
                vox[(fx, fy, 37)] = ci
                vox[(fx, fy, 41)] = ci
    # ellipsoidal dish bottom, 3-thick; tip ~z 26 at centre, edge z 32..34
    TR = 8
    for dx in range(-TR, TR + 1):
        for dy in range(-TR, TR + 1):
            r2 = dx * dx + dy * dy
            if r2 <= TR * TR:
                r = math.sqrt(r2)
                zb = 32 - round(6 * (1 - (r / TR) ** 2))
                for z in (zb - 1, zb, zb + 1):
                    vox[(dx + 10, dy + 10, z)] = steel
    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:
        assert x0 <= x < x1 and y0 <= y < y1 and z0 <= z <= z1, f"breach {(x, y, z)}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    slug = "kit-lot-watertower-shell-v2"
    write_vox(os.path.join(here, slug + ".vox"), vox, PALETTE)
    render_preview(os.path.join(here, slug + "_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, slug + "_slice_z38.png"), vox, PALETTE, 38)
