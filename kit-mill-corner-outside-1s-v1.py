#!/usr/bin/env python3
"""Strike Bay modular factory kit — MILL outside corner, 1 story.

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint x [0,24) x y [0,24); trim may use x in [-1,24) (west face
  normal) and y in [-1,25) (south face normal) — water table/cornice proud 1
  along each walled face's normal per the grid contract. z [0,H+2].
  Seam rule: mill load-bearing brick has no pilasters — plain wall ends meet
  complementary at bay lines. The 1-wide half-columns at the open edges
  (east x=24, north y=24) are subsumed in the 2-thick wall; the corner writes
  its seam half, the neighbour's plain wall end completes the join.
  Outer corner column 2x2 at (0..2, 0..2) completed whole; concave
  courtyard column 2x2 at (22..24, 22..24) completed whole.
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
  Wall top H=10; corbelled brick cornice z H..H+2 proud 1.

MILL story rhythm (base s): water table z s+0..s+2 proud 1 (ground only);
concrete sill z s+1; glass band z s+2..s+8 (steel_dark sash); concrete
lintel z s+9. Window bands: south face x 3..9 and 15..21, west face
y 3..9 and 15..21.

Slug: kit-mill-corner-outside-1s-v1.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import (B, S, T, MILL_PALETTE, CI, box, floater_sweep,
                          mill_window,
                          write_vox, render_preview, render_slice)

PALETTE = [
    ("concrete", (170, 166, 158)),
    ("concrete_dark", (112, 108, 100)),
    ("coping", (202, 198, 190)),
    ("brick", (150, 90, 66)),
    ("brick_dark", (120, 68, 50)),
    ("glass", (72, 98, 118)),
    ("glass_dark", (44, 62, 78)),
    ("steel", (122, 126, 134)),
    ("steel_dark", (62, 64, 72)),
    ("white", (235, 235, 230)),
    ("window", (18, 26, 38)),
    ("dark", (32, 34, 40)),
    ("green", (100, 118, 94)),
    ("green_dark", (70, 88, 68)),
    ("roof", (100, 104, 100)),
    ("band_red", (158, 62, 52)),
    ("band_white", (224, 220, 212)),
    ("patina", (96, 142, 118)),
    ("patina_dark", (66, 104, 88)),
]
C = CI(PALETTE)

H = 10
FOOTPRINT = (-1, 24, -1, 25, 0, H + 2)  # trim: x -1 (west face), y -1 (south)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(101)
    vox = {}
    brick, brick_dark = C["brick"], C["brick_dark"]
    concrete = C["concrete"]

    # ---- floor edge: perimeter strip T wide, z 0..1
    box(vox, 0, 24, 0, 2, 0, 1, brick)
    box(vox, 0, 24, 22, 24, 0, 1, brick)
    box(vox, 0, 2, 2, 22, 0, 1, brick)
    box(vox, 22, 24, 2, 22, 0, 1, brick)

    # ---- columns (brick, z 0..H); seam halves at the open edges are
    # subsumed in the 2-thick wall below — written to document the seam
    box(vox, 0, 2, 0, 2, 0, H, brick)      # outer corner, whole 2x2
    box(vox, 22, 24, 22, 24, 0, H, brick)  # concave courtyard, whole 2x2
    box(vox, 23, 24, 0, 2, 0, H, brick)    # half: south face, east edge
    box(vox, 0, 2, 23, 24, 0, H, brick)    # half: west face, north edge

    # ---- walls + mill rhythm, per story
    for s in range(0, H, 10):
        box(vox, 0, 24, 0, 2, s, s + 10, brick)   # south wall
        box(vox, 0, 2, 0, 24, s, s + 10, brick)   # west wall
        if s == 0:  # concrete water table, proud 1 along face normals
            box(vox, 0, 24, -1, 3, 0, 2, concrete)
            box(vox, -1, 3, 0, 24, 0, 2, concrete)
        mill_window(vox, C, 'y', 0, -1, s, 3, 9)
        mill_window(vox, C, 'y', 0, -1, s, 15, 21)
        mill_window(vox, C, 'x', 0, -1, s, 3, 9)
        mill_window(vox, C, 'x', 0, -1, s, 15, 21)

    # ---- corbelled brick cornice z H..H+2, proud 1
    # (south strip extends to x=-1 to close the outside corner voxel)
    box(vox, -1, 24, -1, 3, H, H + 2, brick)
    box(vox, -1, 3, 0, 24, H, H + 2, brick)
    for i in range(1, 24, 3):  # dentil course
        vox[(i, 0, H)] = brick_dark
        vox[(0, i, H)] = brick_dark

    # ---- sealed interior room (damage reveal), walls on floor strips
    rx0, rx1, ry0, ry1 = 9, 15, 9, 15
    box(vox, rx0, rx1, ry0, ry1, 0, 1, brick)          # floor pad
    for z in range(1, 7):
        for x in range(rx0, rx1):
            vox[(x, ry0, z)] = brick_dark
            vox[(x, ry1 - 1, z)] = brick_dark
        for y in range(ry0, ry1):
            vox[(rx0, y, z)] = brick_dark
            vox[(rx1 - 1, y, z)] = brick_dark
    for x in range(11, 13):                               # door recess
        for z in range(1, 4):
            vox[(x, ry0, z)] = C["dark"]
    box(vox, rx0, rx1, ry0, ry1, 6, 7, C["concrete_dark"])  # cap

    # ---- subtle weathering (mill family signature)
    for (x, y, z), ci in list(vox.items()):
        if ci == brick and random.random() < 0.06:
            vox[(x, y, z)] = brick_dark
        elif ci == concrete and random.random() < 0.04:
            vox[(x, y, z)] = C["concrete_dark"]

    return vox, FOOTPRINT


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:  # footprint guard
        assert x0 <= x < x1, f"x breach {x}"
        assert y0 <= y < y1, f"y breach {y}"
        assert z0 <= z <= z1, f"z breach {z}"
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    write_vox(os.path.join(here, "kit-mill-corner-outside-1s-v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "kit-mill-corner-outside-1s-v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "kit-mill-corner-outside-1s-v1_slice_z5.png"), vox, PALETTE, 5)
