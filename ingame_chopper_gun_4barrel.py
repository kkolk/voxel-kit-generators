#!/usr/bin/env python3
"""Chin minigun rework: 4 barrels instead of 2.

The original chopper_gun() had 6 barrel columns at 1:1; at 4x the
adjacent 1-wide columns merged into 2 horizontal bars. This rework keeps
only the 4 corner barrels [(-1,-2),(1,-2),(-1,-4),(1,-4)] so the cluster
reads as 4 separate barrels. Breech, muzzle rings, and mount unchanged.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ingame_chopper_v1 as g

S = 4

def build_gun1():
    d = g.VD()
    d.cylinder(1, (0, 0), 2.2, -2, 0, "dark")
    d.box((-2, -4, -2), (2, -2, 3), "gunmetal")
    d.cylinder(2, (0, -3), 1.6, 3, 5, "dark")
    for off in [(-1, -2), (1, -2), (-1, -4), (1, -4)]:
        d.cylinder(2, off, 0.4, 5, 15, "black")  # barrels protrude 1 past the ring
    d.cylinder(2, (0, -3), 1.7, 9, 9, "gunmetal")
    d.cylinder(2, (0, -3), 1.7, 14, 14, "gunmetal")
    return d

def build_gun4():
    parts1 = {}
    for name, vd, offset in g.PART_DEFS:
        parts1[name] = g.remap(vd.d, offset)
    # mount shifted 1 back (z=10) so the protruding barrels stay under the cap
    gun1 = g.remap(build_gun1().d, (0, 0, 10))
    out = {}
    for (x, y, z), ci in gun1.items():
        bx, by, bz = x * S, y * S, z * S
        for dx in range(S):
            for dy in range(S):
                for dz in range(S):
                    out[(bx + dx, by + dy, bz + dz)] = ci
    return out

if __name__ == "__main__":
    gun4 = build_gun4()
    xs = [p[0] for p in gun4]; ys = [p[1] for p in gun4]; zs = [p[2] for p in gun4]
    dims = (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) + 1)
    print(f"gun 4-barrel: {len(gun4)} vox, dims={dims}")
    assert all(x <= 255 for x in dims)
    print("floaters:", len(g.floater_sweep(gun4)))
    vpath = os.path.join(HERE, "ingame-chopper-4x-gun-v1.vox")
    ppath = os.path.join(HERE, "ingame-chopper-4x-gun-v1_preview.png")
    g.write_vox(vpath, gun4)
    g.render_preview(ppath, gun4, scale=1)
    print("done")
