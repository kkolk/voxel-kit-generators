#!/usr/bin/env python3
"""Strike Bay BODEGA TOWN — port-town expansion of the bodega tileset
(kkolk/strike-bay#296, 2026-10-05).

Same grid contract as bodega_corner_v1.py (whose palette, skins, helpers and
writers this reuses): B = 12 bay, S = 10 story, T = 2 wall, z-up, canonical
orientation faces SOUTH (exterior wall at y 0..2), seam rule (nothing proud
of x 0..12 along the bay run), protrusions only along the wall normal, open
interiors, every window/door inset 1, NO LETTERING. In game the kit draws at
0.3 m per voxel: 3 m story, 3.6 m bay.

Same four skins (bodega / cement / brick / mural) via the VARIANT remap;
roof tile, corrugated sheet, pier concrete and props keep their colours in
every skin (only plaster / trim / awning remap).

PARTS (local frames; bay parts are 12x12, props have their own footprint):
  low caps   cap-1s, cap-1s-corner (placed at s=10), cap-2s, cap-2s-corner
             (s=20): cornice + roof slab + parapet in one piece.
  ground     g-garage, g-warehouse, g-warehouse-corner, g-cafe, g-row-door
  upper      u-loggia
  civic      civic-tower (on the roof deck), civic-portico (ground bay)
  gable      roof-gable-1b-{tile,corrugated} (one bay deep, 1:1 pitch),
             roof-gable-2b-{tile,corrugated} (half of a two-bay-deep gable,
             1:2 pitch; the far half is the same part rotated k=2), both
             ridge 6 above the wall top; gable-end-1b, gable-end-2b-l/-r
             (ridge on the left / right of the face, seen from outside).
  plaza      prop-monument, prop-obelisk, prop-fountain, prop-bandstand,
             prop-bench, prop-lamp, prop-palm
  street     prop-kiosk, prop-pole, prop-bollard, prop-trashcans
  pier       pier-deck (kerb on the S edge), pier-deck-plain, pier-pile
             (20 tall = 6 m, the game cuts it to the seabed), pier-head
             (36x12 T-head, berth face S, finger joins at x 12..24 on N),
             pier-bollard, pier-fender, pier-crane, pier-steps,
             harbor-shed (3x2-bay gable warehouse, assembled from parts)

Lite interiors: every ground part here takes lite=True (slabs and stairs
only); `part(name, variant, lite)` builds any bodega part, old or new.

Run: python3 bodega_town_v1.py [variant ...] [--lite] [--out DIR]
writes bodega-{skin}-<part>.vox + _preview.png per part, and a town preview
assembly bodega-town-{skin}-v1.vox + _preview.png.
"""
import math
import os
import sys

import bodega_corner_v1 as bc
from bodega_corner_v1 import B, cut, ground_slab, story_slab, peel, \
    rust_streak, shutter_window, band, sign_band, awning, barrel, rot, place


# ---------------------------------------------------------------- low roof caps
def _cap(corner, parapet_h, dentils):
    """Cornice + roof slab + parapet + coping in one piece, local z 0 = top
    of the walls. 4-story tops use top-cornice (2) + roof-parapet (5); low
    buildings get a lighter cap so their silhouette reads lower."""
    v = {}
    cz = 2 if dentils else 1                   # cornice height
    if corner:
        B(v, -1, 2, -1, 2, 0, cz, "coping")    # corner block
        B(v, 2, 12, -1, 2, 0, 1, "coping")
        B(v, -1, 2, 2, 12, 0, 1, "coping")
    else:
        B(v, 0, 12, -1, 2, 0, 1, "coping")
    if dentils:
        x0 = 2 if corner else 0
        for x in range(x0, 12, 4):
            B(v, x, x + 2, -1, 2, 1, 2, "coping")
            B(v, x + 2, min(x + 4, 12), -1, 2, 1, 2, "stone_dark")
        if corner:
            for y in range(2, 12, 4):
                B(v, -1, 2, y, y + 2, 1, 2, "coping")
                B(v, -1, 2, y + 2, min(y + 4, 12), 1, 2, "stone_dark")
    B(v, 0, 12, 0, 12, cz, cz + 1, "roof")     # roof slab, full bay
    top = cz + 1 + parapet_h
    B(v, 0, 12, 0, 2, cz + 1, top, "plaster")  # parapet
    B(v, 0, 12, -1, 2, top, top + 1, "coping")
    if corner:
        B(v, 0, 2, 2, 12, cz + 1, top, "plaster")
        B(v, -1, 2, -1, 2, top, top + 1, "coping")
        B(v, -1, 2, 2, 12, top, top + 1, "coping")
    return v


def cap_1s():
    """One-story cap: plain coping course, slab, parapet 2, coping."""
    return _cap(False, 2, False)


def cap_1s_corner():
    return _cap(True, 2, False)


def cap_2s():
    """Two-story cap: dentil cornice, slab, parapet 3, coping."""
    return _cap(False, 3, True)


def cap_2s_corner():
    return _cap(True, 3, True)


# ---------------------------------------------------------------- ground variants
def g_garage(lite=False):
    """Garage bay, faces S. Corrugated roll door (inset 1), stone lintel,
    blank sign band; workshop bench, oil drum, tyre stack."""
    v = {}
    ground_slab(v)
    story_slab(v)
    B(v, 0, 12, -1, 2, 0, 1, "stone")          # threshold, proud 1
    B(v, 0, 12, 0, 2, 0, 10, "plaster")
    cut(v, 2, 10, 0, 1, 1, 7)                  # punch outer voxel
    for z in range(1, 7):                      # roll door slats, 1 deep
        B(v, 2, 10, 1, 2, z, z + 1, "corr" if z % 2 else "corr_dark")
    B(v, 2, 10, 1, 2, 6, 7, "iron")            # door box
    B(v, 1, 11, 0, 2, 7, 8, "stone")           # lintel
    sign_band(v)
    B(v, 2, 3, 0, 1, 2, 5, "rust")             # oil stain run on the jamb
    peel(v, [(10, 3, 2, 2)])
    if lite:
        return v
    B(v, 2, 8, 9, 11, 1, 3, "wood")            # workbench
    B(v, 2, 3, 9, 11, 0, 1, "wood_dark")       # bench legs
    B(v, 7, 8, 9, 11, 0, 1, "wood_dark")
    B(v, 2, 8, 10, 11, 3, 6, "wood_dark")      # tool board
    B(v, 9, 11, 8, 10, 0, 3, "rust")           # oil drum
    B(v, 9, 11, 8, 10, 1, 2, "iron")
    for z in (0, 1):                           # tyre stack (ring)
        B(v, 3, 6, 3, 6, z, z + 1, "rubber")
        v.pop((4, 4, z), None)
    return v


def _warehouse_face(v, x0, door):
    """South face of a warehouse bay from x0: plaster wall, optional wide
    plank loading door, barred high window."""
    B(v, x0, 12, 0, 2, 0, 10, "plaster")
    if door:
        cut(v, 1, 8, 0, 1, 1, 8)               # punch outer voxel
        for x in range(1, 8):                  # vertical planks, 1 deep
            B(v, x, x + 1, 1, 2, 1, 8, "wood" if x % 2 else "wood_dark")
        B(v, 1, 8, 1, 2, 4, 5, "iron")         # strap hinge line
        B(v, 0, 9, 0, 2, 8, 9, "stone")        # lintel
        wx0 = 9
    else:
        wx0 = 6
    cut(v, wx0, wx0 + 2, 0, 1, 5, 8)           # high window, sill 1.5 m
    B(v, wx0, wx0 + 2, 1, 2, 5, 8, "glass_dark")
    B(v, wx0, wx0 + 2, 1, 2, 6, 7, "iron")     # bars
    B(v, wx0 - 1, wx0 + 3, -1, 2, 4, 5, "stone")  # sill, proud 1
    band(v, 0, x0, 12)
    B(v, x0, 12, -1, 2, 0, 1, "stone")         # plinth, proud 1


def g_warehouse(lite=False):
    """Warehouse bay, faces S. Wide plank loading door, barred high window;
    crate stacks and sacks."""
    v = {}
    ground_slab(v)
    story_slab(v)
    _warehouse_face(v, 0, door=True)
    rust_streak(v, 10, 4, 2)
    peel(v, [(3, 9, 3, 1)])
    if lite:
        return v
    B(v, 2, 6, 7, 11, 0, 2, "wood")            # crate stack
    B(v, 3, 5, 8, 10, 2, 4, "wood")
    B(v, 2, 6, 7, 8, 0, 2, "wood_dark")        # battens
    B(v, 7, 10, 8, 11, 0, 2, "sack")           # sacks
    B(v, 8, 9, 9, 10, 2, 3, "sack")
    return v


def g_warehouse_corner(lite=False):
    """Warehouse corner, faces S+W. Stone corner column whole, a barred high
    window per face (no door; the long sides take g-warehouse)."""
    v = {}
    ground_slab(v)
    story_slab(v, south=True, west=True)
    _warehouse_face(v, 2, door=False)
    w = {}
    _warehouse_face(w, 2, door=False)
    for (x, y, z), ci in w.items():            # west face = mirrored south
        v[(y, x, z)] = ci
    B(v, -1, 2, -1, 2, 0, 1, "stone")          # corner base, proud both faces
    B(v, 0, 2, 0, 2, 1, 10, "stone")           # corner column whole
    if lite:
        return v
    B(v, 6, 10, 7, 11, 0, 2, "wood")           # crates
    B(v, 7, 9, 8, 10, 2, 4, "wood")
    return v


def g_cafe(lite=False):
    """Cafe bay, faces S. Open arcade: piers + beam on the street line, a
    covered loggia (y 2..5, checker floor) with tables, glazed shopfront set
    back at y 5..6 with a door."""
    v = {}
    ground_slab(v)
    story_slab(v)
    for x in range(12):                        # checker tile loggia floor
        for y in range(0, 6):
            B(v, x, x + 1, y, y + 1, 0, 1,
              "stone" if (x + y) % 2 else "stone_dark")
    B(v, 0, 12, -1, 0, 0, 1, "stone")          # kerb step, proud 1
    for px0, px1 in ((0, 1), (5, 7), (11, 12)):  # piers (half at bay edges)
        B(v, px0, px1, 0, 2, 1, 8, "stone")
    B(v, 0, 12, 0, 2, 7, 8, "wood_dark")       # beam
    B(v, 0, 12, 1, 2, 8, 9, "stone")
    sign_band(v)
    B(v, 0, 12, 0, 2, 9, 10, "stone")          # entablature
    B(v, 0, 12, 2, 5, 9, 10, "wood_floor")     # loggia ceiling = slab above
    awning(v)
    # glazed shopfront, set back
    B(v, 0, 12, 5, 6, 1, 9, "wood_dark")       # frame
    for x0, x1 in ((1, 4), (8, 11)):           # windows
        B(v, x0, x1, 5, 6, 2, 7, "glass_dark")
    B(v, 5, 7, 5, 6, 1, 7, "teal")             # door
    B(v, 5, 7, 5, 6, 3, 6, "glass_dark")
    if lite:
        return v
    for tx, chairs in ((3, ((1, 0),)), (8, ((6, 5), (10, 11)))):
        B(v, tx, tx + 1, 3, 4, 1, 3, "iron")   # table leg
        B(v, tx - 1, tx + 2, 2, 5, 3, 4, "wood")  # top
        for cx, bx in chairs:                  # (seat x, back x)
            B(v, cx, cx + 1, 3, 4, 1, 2, "wood_dark")
            B(v, bx, bx + 1, 3, 4, 1, 3, "wood_dark")
    B(v, 3, 9, 9, 11, 0, 3, "wood")            # counter inside
    B(v, 3, 9, 9, 11, 3, 4, "wood_dark")
    return v


def g_row_door(lite=False):
    """Row-house entry, faces S. Narrow raised door with stone surround and a
    2-step stoop (proud 2), shuttered window; interior stair up (kept lite)."""
    v = {}
    ground_slab(v)
    story_slab(v)
    B(v, 0, 12, 0, 2, 0, 10, "plaster")
    B(v, 0, 12, -1, 0, 0, 1, "stone")          # water table, proud 1
    B(v, 3, 8, -2, 0, 0, 1, "stone")           # stoop, proud 2
    B(v, 3, 8, -1, 0, 1, 2, "stone")
    B(v, 3, 8, 0, 2, 1, 9, "stone")            # door surround
    cut(v, 4, 7, 0, 1, 2, 8)                   # punch outer voxel
    B(v, 4, 7, 1, 2, 2, 8, "wood")             # door leaf, 1 deep
    B(v, 4, 7, 1, 2, 4, 5, "wood_dark")        # panel line
    B(v, 4, 7, 1, 2, 7, 8, "glass_dark")       # fanlight
    B(v, 6, 7, 1, 2, 5, 6, "iron_dark")        # knob
    shutter_window(v, 9, 11, 0)
    band(v, 0)
    peel(v, [(1, 3, 2, 2)])
    rust_streak(v, 10, 2, 2)
    # stair up along the east wall (each step lands on the last)
    for i in range(8):
        B(v, 9, 11, 3 + i, 4 + i, 0, i + 1, "wood")
    return v


# ---------------------------------------------------------------- upper variant
def u_loggia():
    """Loggia bay, faces S. Recessed balcony (6 wide, 4 deep) behind an iron
    balustrade on the wall line, French door in the back wall."""
    v = {}
    story_slab(v)
    B(v, 0, 12, 0, 2, 0, 10, "plaster")
    cut(v, 3, 9, 0, 2, 0, 8)                   # the recess opening
    B(v, 2, 3, 2, 5, 0, 9, "plaster")          # recess side walls
    B(v, 9, 10, 2, 5, 0, 9, "plaster")
    B(v, 3, 9, 0, 4, 0, 1, "stone")            # loggia floor
    B(v, 3, 9, 4, 5, 0, 9, "plaster")          # back wall
    B(v, 3, 9, 2, 4, 8, 9, "plaster")          # recess ceiling
    cut(v, 4, 8, 4, 5, 1, 7)
    B(v, 4, 8, 4, 5, 1, 7, "teal")             # French door
    B(v, 5, 7, 4, 5, 2, 6, "glass_dark")
    for px in (4, 6, 8):                       # balustrade posts
        B(v, px, px + 1, 0, 1, 1, 3, "iron")
    B(v, 3, 9, 0, 1, 3, 4, "iron")             # rail
    B(v, 1, 2, 0, 1, 5, 8, "rust")
    band(v, 0)
    peel(v, [(10, 3, 2, 2)])
    return v


# ---------------------------------------------------------------- civic
def _tower_face():
    """South face of the tower: 2 stories, small window below, arched
    belfry opening above, cornice."""
    v = {}
    B(v, 0, 12, 0, 2, 0, 20, "plaster")
    cut(v, 5, 7, 0, 1, 3, 7)                   # lower window, inset 1
    B(v, 5, 7, 1, 2, 3, 7, "teal")
    B(v, 4, 8, -1, 0, 2, 3, "stone")           # sill
    B(v, 0, 12, 0, 1, 8, 9, "teal")            # band
    cut(v, 3, 9, 0, 2, 11, 17)                 # belfry arch, open through
    cut(v, 4, 8, 0, 2, 17, 18)
    B(v, 3, 9, -1, 0, 10, 11, "stone")         # belfry sill
    B(v, 0, 12, -1, 2, 20, 21, "coping")       # cornice, proud 1
    return v


def civic_tower():
    """Civic tower, 12x12, base z 0 on the roof deck. 2 stories (lower
    windows, belfry arches), cornice, stepped tile pyramid, flagpole+flag."""
    v = {}
    f = _tower_face()
    for k in range(4):
        v.update(rot(f, k))
    B(v, 2, 10, 2, 10, 9, 10, "wood_floor")    # belfry floor
    B(v, 5, 7, 5, 7, 10, 14, "iron_dark")      # bell frame + bell
    B(v, 4, 8, 5, 7, 14, 15, "iron_dark")
    B(v, 5, 7, 5, 7, 11, 13, "bronze")
    for i in range(6):                         # pyramid, z 21..27
        B(v, i, 12 - i, i, 12 - i, 21 + i, 22 + i,
          "tile_dark" if i % 2 else "tile")
    B(v, 5, 6, 5, 6, 27, 38, "iron")           # flagpole
    B(v, 6, 11, 5, 6, 33, 37, "red")           # flag
    return v


def civic_portico(lite=False):
    """Columned portico ground bay, faces S. Raised stylobate with 2 steps
    (proud 2), 2 columns + half pilasters at bay edges, entablature with a
    cornice; recessed back wall with a double door and windows."""
    v = {}
    B(v, 0, 12, 0, 12, 0, 2, "stone_dark")     # raised floor
    B(v, 0, 12, -2, 0, 0, 1, "stone")          # steps, proud 2
    B(v, 0, 12, -1, 0, 1, 2, "stone")
    for cx0, cx1 in ((0, 1), (3, 5), (7, 9), (11, 12)):
        B(v, cx0, cx1, 0, 2, 2, 3, "coping")   # base
        B(v, cx0, cx1, 0, 2, 3, 8, "stone")    # shaft
        B(v, cx0, cx1, 0, 2, 8, 9, "coping")   # capital
    B(v, 0, 12, 0, 2, 9, 10, "stone")          # entablature
    B(v, 0, 12, -1, 0, 9, 10, "coping")        # cornice, proud 1
    B(v, 0, 12, 2, 12, 9, 10, "wood_floor")    # ceiling = slab above
    B(v, 0, 12, 6, 8, 2, 9, "plaster")         # back wall
    cut(v, 4, 8, 6, 7, 2, 8)                   # double door, inset 1
    B(v, 4, 8, 7, 8, 2, 8, "wood")
    B(v, 6, 7, 7, 8, 2, 8, "wood_dark")
    for wx in (1, 9):                          # tall windows, inset 1
        cut(v, wx, wx + 2, 6, 7, 3, 8)
        B(v, wx, wx + 2, 7, 8, 3, 8, "glass_dark")
    B(v, 0, 12, 6, 7, 8, 9, "teal")            # band
    if lite:
        return v
    B(v, 3, 9, 10, 11, 2, 4, "wood")           # bench along the hall wall
    B(v, 2, 4, 9, 11, 2, 5, "wood_dark")       # desk
    return v


# ---------------------------------------------------------------- gable roofs
def _gable_h1(y):
    """1-bay gable, 1:1 pitch: roof top z at y, y -1..12 (eaves at -1, 12)."""
    return min(y + 1, 12 - y)


def _gable_h2(y):
    """Half of a 2-bay gable, 1:2 pitch: eave at y -1, ridge at y 11."""
    return (y + 1) // 2


def _roof(hfun, ys, skin):
    """Stepped roof 2 thick (each column [h-1, h]) so neighbouring columns
    share a face. tile: courses along the ridge; corrugated: ribs across."""
    v = {}
    for y in ys:
        h = hfun(y)
        for x in range(12):
            if skin == "tile":
                ci = "tile_dark" if (y % 3 == 0) else "tile"
            else:
                ci = "corr_dark" if x % 2 else "corr"
                if bc._hash2(x, y // 4, salt=5) < 7:  # rust runs downslope
                    ci = "rust"
            B(v, x, x + 1, y, y + 1, max(h - 1, 0), h + 1, ci)
    return v


def roof_gable_1b(skin):
    def fn():
        v = _roof(_gable_h1, range(-1, 13), skin)
        if skin == "tile":                     # ridge cap
            B(v, 0, 12, 5, 7, 7, 8, "tile_dark")
        return v
    return fn


def roof_gable_2b(skin):
    def fn():
        v = _roof(_gable_h2, range(-1, 12), skin)
        if skin == "tile":                     # half ridge cap (meets k=2 twin)
            B(v, 0, 12, 11, 12, 7, 8, "tile_dark")
        return v
    return fn


def _gable_end(heights):
    """Gable end wall, faces S, base z 0 = top of the end wall. heights[x] =
    roof top z over column x; the wall stops under the 2-thick roof."""
    v = {}
    for x, h in enumerate(heights):
        top = max(h - 1, 0)
        if top:
            B(v, x, x + 1, 0, 2, 0, top, "plaster")
            B(v, x, x + 1, -1, 0, top - 1, top, "coping")  # verge, proud 1
    return v


def gable_end_1b():
    v = _gable_end([_gable_h1(11 - x) for x in range(12)])
    cut(v, 5, 7, 0, 1, 2, 4)                   # attic vent, inset 1
    B(v, 5, 7, 1, 2, 2, 4, "glass_dark")
    return v


def gable_end_2b_l():
    """Ridge at the left (x 0) as seen from outside."""
    return _gable_end([_gable_h2(11 - x) for x in range(12)])


def gable_end_2b_r():
    """Ridge at the right (x 11) as seen from outside."""
    return _gable_end([_gable_h2(x) for x in range(12)])


# ---------------------------------------------------------------- plaza props
def _disc(cx, cy, r):
    return [(x, y) for x in range(int(cx - r), int(cx + r) + 1)
            for y in range(int(cy - r), int(cy + r) + 1)
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r]


def prop_monument():
    """Stepped plinth (8x8) and a bronze heroic figure (~2.1 m), arm up."""
    v = {}
    B(v, 0, 8, 0, 8, 0, 1, "stone_dark")
    B(v, 1, 7, 1, 7, 1, 2, "stone")
    B(v, 2, 6, 2, 6, 2, 6, "stone")
    B(v, 1, 7, 1, 7, 6, 7, "coping")
    B(v, 3, 5, 3, 5, 7, 8, "bronze_dark")      # base slab
    B(v, 3, 4, 3, 5, 8, 11, "bronze")          # legs
    B(v, 4, 5, 4, 5, 8, 10, "bronze")          # striding leg
    B(v, 3, 5, 3, 5, 11, 14, "bronze")         # torso
    B(v, 3, 4, 3, 4, 14, 15, "bronze_dark")    # head
    B(v, 5, 6, 3, 4, 13, 14, "bronze")         # raised arm
    B(v, 5, 6, 3, 4, 14, 17, "bronze")
    B(v, 2, 3, 4, 5, 11, 13, "bronze")         # lowered arm
    return v


def prop_obelisk():
    """Square tapering obelisk (~6.3 m) on a stepped 11x11 base, a red
    5-point star (tip up) standing on top in the x-z plane."""
    v = {}
    B(v, 0, 11, 0, 11, 0, 1, "stone_dark")
    B(v, 1, 10, 1, 10, 1, 2, "stone")
    B(v, 3, 8, 3, 8, 2, 10, "coping")
    B(v, 4, 7, 3, 8, 10, 18, "coping")
    B(v, 3, 8, 4, 7, 10, 18, "coping")
    B(v, 4, 7, 4, 7, 18, 21, "coping")
    B(v, 5, 6, 5, 6, 21, 24, "red")            # stem into the star
    cx, cz, R, r0 = 5.5, 25.6, 5.6, 0.42       # star, 1 thick at y 5
    for x in range(11):
        for z in range(21, 31):
            dx, dz = x + 0.5 - cx, z + 0.5 - cz
            t = ((math.degrees(math.atan2(dz, dx)) - 90) % 72) / 36.0
            if math.hypot(dx, dz) <= R * (1 - (1 - r0) * (1 - abs(t - 1))):
                B(v, x, x + 1, 5, 6, z, z + 1, "red")
    return v


def prop_fountain():
    """Round basin (14 across), rim 2 high, water, centre column with a
    bowl and spout."""
    v = {}
    disc = _disc(7, 7, 7)
    inner = set(_disc(7, 7, 5.6))
    for (x, y) in disc:
        B(v, x, x + 1, y, y + 1, 0, 1, "stone_dark")
        if (x, y) in inner:
            B(v, x, x + 1, y, y + 1, 1, 2, "water")
        else:
            B(v, x, x + 1, y, y + 1, 1, 3, "stone")
    B(v, 6, 8, 6, 8, 1, 6, "stone")            # column
    for (x, y) in _disc(7, 7, 2.6):            # bowl
        B(v, x, x + 1, y, y + 1, 6, 7, "stone")
    B(v, 6, 8, 6, 8, 7, 8, "water")            # spout
    B(v, 7, 8, 7, 8, 8, 9, "water")
    return v


def prop_bandstand():
    """Octagonal raised bandstand (16 across): stone platform with steps, 8
    iron posts, railing, stepped tile roof and finial."""
    v = {}
    oct16 = [(x, y) for x in range(16) for y in range(16)
             if abs(x - 7.5) + abs(y - 7.5) <= 11]
    for (x, y) in oct16:
        B(v, x, x + 1, y, y + 1, 0, 2, "stone")
    B(v, 6, 10, -2, 0, 0, 1, "stone")          # steps on the S side
    B(v, 6, 10, -1, 0, 1, 2, "stone")
    posts = [(1, 5), (1, 10), (5, 1), (10, 1), (14, 5), (14, 10), (5, 14),
             (10, 14)]
    for (x, y) in posts:
        B(v, x, x + 1, y, y + 1, 2, 10, "iron")
    for (x, y) in oct16:                       # railing ring (open on S steps)
        edge = abs(x - 7.5) + abs(y - 7.5) > 9.5 or x in (0, 15) or y in (0, 15)
        if edge and not (6 <= x < 10 and y < 3):
            B(v, x, x + 1, y, y + 1, 4, 5, "iron")
    for i in range(5):                         # roof
        cells = [(x, y) for (x, y) in oct16
                 if abs(x - 7.5) + abs(y - 7.5) <= 11 - 2.2 * i
                 and i <= x < 16 - i and i <= y < 16 - i]
        for (x, y) in cells:
            B(v, x, x + 1, y, y + 1, 10 + i, 11 + i,
              "tile_dark" if i % 2 else "tile")
    B(v, 7, 9, 7, 9, 15, 17, "iron")           # finial
    return v


def prop_bench():
    """Park bench, 6 long (1.8 m): iron legs, wood seat and back."""
    v = {}
    for x in (0, 5):
        B(v, x, x + 1, 0, 2, 0, 1, "iron")
        B(v, x, x + 1, 1, 2, 1, 3, "iron")
    B(v, 0, 6, 0, 2, 1, 2, "wood")             # seat
    B(v, 0, 6, 1, 2, 2, 3, "wood_dark")        # back
    return v


def prop_lamp():
    """Street lamp post (~4.2 m): stone footing, iron post, lantern."""
    v = {}
    B(v, 0, 2, 0, 2, 0, 1, "stone")
    B(v, 0, 1, 0, 1, 1, 12, "iron")
    B(v, 0, 2, 0, 1, 11, 12, "iron")           # arm
    B(v, 1, 2, 0, 1, 12, 14, "lamp")          # lantern
    B(v, 1, 2, 0, 1, 14, 15, "iron_dark")      # cap
    return v


def prop_palm():
    """Palm in a square stone planter: leaning trunk, cross of fronds."""
    v = {}
    B(v, 0, 5, 0, 5, 0, 3, "stone")
    B(v, 1, 4, 1, 4, 2, 3, "soil")
    x, y = 2, 2
    for z in range(3, 17):                     # trunk leans +x every 5
        if z in (8, 13):
            B(v, x, x + 1, y, y + 1, z, z + 1, "trunk")
            x += 1
        B(v, x, x + 1, y, y + 1, z, z + 1,
          "trunk" if z % 3 else "wood_dark")
    tx, ty, tz = x, y, 17
    B(v, tx, tx + 1, ty, ty + 1, tz, tz + 1, "leaf_dark")
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for i in range(1, 5):                  # fronds droop
            z = tz - (i // 2)
            B(v, tx + dx * i, tx + dx * i + 1, ty + dy * i, ty + dy * i + 1,
              z, z + 1, "leaf" if i % 2 else "leaf_dark")
            if i < 4 and i % 2 == 1:
                B(v, tx + dx * i, tx + dx * i + 1, ty + dy * i,
                  ty + dy * i + 1, z - 1, z, "leaf")
    return v


# ---------------------------------------------------------------- street props
def prop_kiosk():
    """Newspaper / snack kiosk, 5x5: wood box, teal shutter flap counter
    window on S, overhanging iron roof. No lettering."""
    v = {}
    B(v, 0, 5, 0, 5, 0, 1, "stone")
    B(v, 0, 5, 0, 5, 1, 7, "teal_dark")
    cut(v, 1, 4, 0, 1, 3, 6)                   # serving window, inset 1
    B(v, 1, 4, 1, 2, 3, 6, "glass_dark")
    B(v, 0, 5, -1, 0, 3, 4, "wood")            # counter
    B(v, -1, 6, -1, 6, 7, 8, "corr")           # roof
    B(v, 1, 4, 1, 4, 8, 9, "corr_dark")
    B(v, 4, 5, 0, 1, 1, 3, "rust")
    return v


def prop_pole():
    """Phone / power pole (~8.4 m): wood pole at x 3, 7-wide crossarm with
    insulators."""
    v = {}
    B(v, 3, 4, 0, 1, 0, 28, "wood_dark")
    B(v, 0, 7, 0, 1, 25, 26, "wood")           # crossarm
    for x in (0, 2, 5, 6):
        B(v, x, x + 1, 0, 1, 26, 27, "glass")  # insulators
    B(v, 2, 5, 0, 1, 24, 25, "iron")           # brace
    B(v, 4, 5, 0, 1, 15, 17, "iron_dark")      # junction box
    return v


def prop_bollard():
    """Street bollard, 1x1 x 3 (0.9 m), iron with a teal band."""
    v = {}
    B(v, 0, 1, 0, 1, 0, 3, "iron")
    B(v, 0, 1, 0, 1, 2, 3, "teal")
    return v


def prop_trashcans():
    """Two 2x2 metal bins, one with a lid ajar (bodega palette)."""
    v = {}
    B(v, 0, 2, 0, 2, 0, 3, "teal_dark")
    B(v, 0, 2, 0, 2, 1, 2, "teal")
    B(v, 0, 2, 0, 2, 3, 4, "iron")             # lid
    B(v, 3, 5, 0, 2, 0, 3, "iron")
    B(v, 3, 5, 0, 1, 0, 2, "rust")
    B(v, 3, 5, 1, 2, 3, 4, "iron_dark")        # lid ajar (half)
    return v


# ---------------------------------------------------------------- pier set
def pier_deck():
    """Deck module 12x12, 2 thick; kerb on the S edge (rotate for the other
    side), drain gaps every 4; drip edge proud 1 along the normal."""
    v = {}
    B(v, 0, 12, 0, 12, 0, 2, "pier")
    for x in range(12):
        if x % 4 != 3:
            B(v, x, x + 1, 0, 1, 2, 3, "pier_dark")
    B(v, 0, 12, -1, 0, 1, 2, "pier_dark")     # drip edge
    return v


def pier_deck_plain():
    """Deck module 12x12, 2 thick, no kerb (inner modules of a wide deck)."""
    v = {}
    B(v, 0, 12, 0, 12, 0, 2, "pier")
    B(v, 0, 12, 5, 6, 1, 2, "pier_dark")       # expansion joint
    return v


def pier_pile():
    """Concrete pile 2x2 x 20 (6 m) with a 4x4 cap; the game cuts it to the
    local seabed. Base z 0 = pile toe, cap top at z 21 meets the deck."""
    v = {}
    B(v, 1, 3, 1, 3, 0, 20, "pier")
    B(v, 1, 3, 1, 3, 0, 8, "pier_dark")        # wet / weed line below water
    B(v, 0, 4, 0, 4, 20, 21, "pier")
    return v


def pier_head():
    """T-head 36x12, 2 thick. Berth face S (kerb + drip edge), kerbs on the
    W/E ends and the N side except where the finger joins (x 12..24)."""
    v = {}
    B(v, 0, 36, 0, 12, 0, 2, "pier")
    for x in range(36):
        if x % 4 != 3:
            B(v, x, x + 1, 0, 1, 2, 3, "pier_dark")
        if (x < 12 or x >= 24) and x % 4 != 3:
            B(v, x, x + 1, 11, 12, 2, 3, "pier_dark")
    for y in range(1, 11):
        B(v, 0, 1, y, y + 1, 2, 3, "pier_dark")
        B(v, 35, 36, y, y + 1, 2, 3, "pier_dark")
    B(v, 0, 36, -1, 0, 1, 2, "pier_dark")      # drip edge
    for x in (2, 16, 33):                      # rail track pad marks
        B(v, x, x + 1, 4, 8, 1, 2, "pier_dark")
    return v


def pier_bollard():
    """Mooring bollard: 2x2 base, iron post with a mushroom cap."""
    v = {}
    B(v, 0, 3, 0, 3, 0, 1, "iron_dark")
    B(v, 1, 2, 1, 2, 1, 3, "iron")
    B(v, 0, 3, 1, 2, 3, 4, "iron")
    B(v, 1, 2, 0, 3, 3, 4, "iron")
    return v


def pier_fender():
    """Tyre fender: a 4x4 tyre ring in the x-z plane on a chain; base z 0 is
    the tyre bottom, the chain's top voxel hooks over the kerb (y 0..2)."""
    v = {}
    for x in range(4):
        for z in range(4):
            if x in (0, 3) or z in (0, 3):
                B(v, x, x + 1, 0, 1, z, z + 1, "rubber")
    B(v, 1, 2, 0, 1, 4, 7, "iron_dark")        # chain
    B(v, 1, 2, 0, 3, 7, 8, "iron_dark")        # hook over the deck edge
    return v


def pier_crane():
    """Small travelling crane, 12x8 portal on rail bogies (~9 m): 4 legs,
    portal beams, cab, slewing jib reaching 12 past the S face, hook."""
    v = {}
    for x0 in (0, 10):
        B(v, x0, x0 + 2, 0, 8, 0, 1, "iron_dark")  # bogie on the rail
        for y0 in (0, 6):
            B(v, x0, x0 + 2, y0, y0 + 2, 1, 14, "crane")
        B(v, x0, x0 + 2, 2, 6, 7, 8, "crane")  # knee brace
    B(v, 0, 12, 0, 8, 14, 16, "crane")         # portal deck
    B(v, 3, 9, 1, 7, 16, 22, "crane")          # cab
    cut(v, 3, 9, 1, 2, 18, 21)                 # cab window, inset 1
    B(v, 3, 9, 2, 3, 18, 21, "glass_dark")
    B(v, 5, 7, -12, 4, 22, 23, "crane")        # jib
    B(v, 5, 7, 5, 9, 22, 24, "iron_dark")      # counterweight
    B(v, 5, 6, -11, -10, 12, 22, "iron_dark")  # hook cable
    B(v, 4, 7, -11, -10, 11, 12, "iron")       # hook block
    B(v, 0, 2, 0, 1, 1, 3, "rust")
    return v


def pier_steps():
    """Landing steps down the S face of a deck: 3 wide (y -3..0, along the
    normal), 8 steps; base z 0 is the water landing, top step meets the
    deck top (z 8 = deck surface when placed at deck z - 6)."""
    v = {}
    for i in range(8):
        B(v, i, i + 1, -3, 0, 0, i + 1, "pier" if i % 2 else "pier_dark")
    B(v, 0, 8, -1, 0, 0, 1, "pier_dark")       # weed line
    return v


# ---------------------------------------------------------------- harbor shed
def harbor_shed(lite=False):
    """Gable warehouse in bodega skin, 3x2 bays (36x24), one story: warehouse
    corners + loading doors on both long sides, a corrugated 2-bay gable,
    gable ends on W and E. Composed from parts (see build_shed)."""
    v = {}
    build_shed(v, lambda n: _part_canon(n, lite), 0, 0)
    return v


def build_shed(w, get, ox, oy):
    """Harbor shed layout (3x2 bays) with part getter get(name)."""
    corner, mid = get("bodega-g-warehouse-corner"), get("bodega-g-warehouse")
    for bx, by, k in ((0, 0, 0), (2, 0, 1), (2, 1, 2), (0, 1, 3)):
        place(w, corner, bx, by, 0, k, ox, oy)
    place(w, mid, 1, 0, 0, 0, ox, oy)
    place(w, mid, 1, 1, 0, 2, ox, oy)
    roof = get("bodega-roof-gable-2b-corrugated")
    for bx in range(3):
        place(w, roof, bx, 0, 10, 0, ox, oy)
        place(w, roof, bx, 1, 10, 2, ox, oy)
    # gable ends: W face (k=3) and E face (k=1)
    place(w, get("bodega-gable-end-2b-l"), 0, 0, 10, 3, ox, oy)
    place(w, get("bodega-gable-end-2b-r"), 0, 1, 10, 3, ox, oy)
    place(w, get("bodega-gable-end-2b-r"), 2, 0, 10, 1, ox, oy)
    place(w, get("bodega-gable-end-2b-l"), 2, 1, 10, 1, ox, oy)


# ---------------------------------------------------------------- registry
# name -> (builder, takes_lite)
TOWN_BUILDERS = [
    ("bodega-cap-1s", cap_1s, False),
    ("bodega-cap-1s-corner", cap_1s_corner, False),
    ("bodega-cap-2s", cap_2s, False),
    ("bodega-cap-2s-corner", cap_2s_corner, False),
    ("bodega-g-garage", g_garage, True),
    ("bodega-g-warehouse", g_warehouse, True),
    ("bodega-g-warehouse-corner", g_warehouse_corner, True),
    ("bodega-g-cafe", g_cafe, True),
    ("bodega-g-row-door", g_row_door, True),
    ("bodega-u-loggia", u_loggia, False),
    ("bodega-civic-tower", civic_tower, False),
    ("bodega-civic-portico", civic_portico, True),
    ("bodega-roof-gable-1b-tile", roof_gable_1b("tile"), False),
    ("bodega-roof-gable-1b-corrugated", roof_gable_1b("corrugated"), False),
    ("bodega-roof-gable-2b-tile", roof_gable_2b("tile"), False),
    ("bodega-roof-gable-2b-corrugated", roof_gable_2b("corrugated"), False),
    ("bodega-gable-end-1b", gable_end_1b, False),
    ("bodega-gable-end-2b-l", gable_end_2b_l, False),
    ("bodega-gable-end-2b-r", gable_end_2b_r, False),
    ("bodega-prop-monument", prop_monument, False),
    ("bodega-prop-obelisk", prop_obelisk, False),
    ("bodega-prop-fountain", prop_fountain, False),
    ("bodega-prop-bandstand", prop_bandstand, False),
    ("bodega-prop-bench", prop_bench, False),
    ("bodega-prop-lamp", prop_lamp, False),
    ("bodega-prop-palm", prop_palm, False),
    ("bodega-prop-kiosk", prop_kiosk, False),
    ("bodega-prop-pole", prop_pole, False),
    ("bodega-prop-bollard", prop_bollard, False),
    ("bodega-prop-trashcans", prop_trashcans, False),
    ("bodega-pier-deck", pier_deck, False),
    ("bodega-pier-deck-plain", pier_deck_plain, False),
    ("bodega-pier-pile", pier_pile, False),
    ("bodega-pier-head", pier_head, False),
    ("bodega-pier-bollard", pier_bollard, False),
    ("bodega-pier-fender", pier_fender, False),
    ("bodega-pier-crane", pier_crane, False),
    ("bodega-pier-steps", pier_steps, False),
    ("bodega-harbor-shed", harbor_shed, True),
]

ALL_BUILDERS = {n: (fn, n in bc.LITE_BUILDERS) for n, fn in bc.BUILDERS}
ALL_BUILDERS.update({n: (fn, tl) for n, fn, tl in TOWN_BUILDERS})


def _part_canon(name, lite=False):
    """Canonical (bodega-skin colour) part, local frame."""
    fn, takes_lite = ALL_BUILDERS[name]
    return fn(lite=lite) if takes_lite else fn()


def part(name, variant="bodega", lite=False):
    """Any bodega part (core or town) in a skin, local frame, colour indices
    into bc.variant_palette(variant). The entry point for prefab builders."""
    fn, takes_lite = ALL_BUILDERS[name]
    return bc.make_part(fn, variant, bc.variant_index(variant)[1], lite,
                        takes_lite)


def footprint(v):
    """(x0, x1, y0, y1, z0, z1) half-open bounds of a part."""
    return tuple(f(p[a] for p in v) + d for a in range(3)
                 for f, d in ((min, 0), (max, 1)))


# ---------------------------------------------------------------- preview assembly
def build_town(w, get):
    """Town preview: a street of new parts. Each lot sits on its own bay
    grid offset; base z 0 everywhere except the pier (deck on piles)."""
    P = get
    # 1) one-story 3x2 block: arcade corners W, warehouse corners E,
    #    garage S, warehouse N, low 1s caps
    ox, oy = 0, 0
    for bx, by, k, n in ((0, 0, 0, "bodega-g-arcade-corner"),
                         (0, 1, 3, "bodega-g-arcade-corner"),
                         (2, 0, 1, "bodega-g-warehouse-corner"),
                         (2, 1, 2, "bodega-g-warehouse-corner"),
                         (1, 0, 0, "bodega-g-garage"),
                         (1, 1, 2, "bodega-g-warehouse")):
        place(w, P(n), bx, by, 0, k, ox, oy)
        cap = "bodega-cap-1s-corner" if "corner" in n else "bodega-cap-1s"
        place(w, P(cap), bx, by, 10, k, ox, oy)

    # 2) two-story row house: row door + cafe, loggia above, 1-bay tile gable
    ox, oy = 48, 0
    place(w, P("bodega-g-row-door"), 0, 0, 0, 0, ox, oy)
    place(w, P("bodega-g-cafe"), 1, 0, 0, 0, ox, oy)
    place(w, P("bodega-u-loggia"), 0, 0, 10, 0, ox, oy)
    place(w, P("bodega-u-shutter"), 1, 0, 10, 0, ox, oy)
    for bx in (0, 1):
        place(w, P("bodega-roof-gable-1b-tile"), bx, 0, 20, 0, ox, oy)
    place(w, P("bodega-gable-end-1b"), 0, 0, 20, 3, ox, oy)
    place(w, P("bodega-gable-end-1b"), 1, 0, 20, 1, ox, oy)

    # 3) civic: portico ground + 2s cap + tower on the roof deck
    ox, oy = 84, 0
    place(w, P("bodega-civic-portico"), 0, 0, 0, 0, ox, oy)
    place(w, P("bodega-u-balcony"), 0, 0, 10, 0, ox, oy)
    place(w, P("bodega-cap-2s"), 0, 0, 20, 0, ox, oy)
    place(w, P("bodega-civic-tower"), 0, 0, 23, 0, ox, oy)

    # 4) plaza props on a 48x36 square south of the street
    ox, oy = 0, -48
    place(w, P("bodega-prop-fountain"), 0, 0, 0, 0, ox + 2, oy + 2)
    place(w, P("bodega-prop-monument"), 0, 0, 0, 0, ox + 22, oy + 4)
    place(w, P("bodega-prop-obelisk"), 0, 0, 0, 0, ox + 34, oy + 2)
    place(w, P("bodega-prop-bandstand"), 0, 0, 0, 0, ox + 4, oy + 20)
    for i in range(3):
        place(w, P("bodega-prop-bench"), 0, 0, 0, 0, ox + 24 + 8 * i, oy + 20)
        place(w, P("bodega-prop-lamp"), 0, 0, 0, 0, ox + 23 + 8 * i, oy + 26)
    place(w, P("bodega-prop-palm"), 0, 0, 0, 0, ox + 24, oy + 30)
    place(w, P("bodega-prop-palm"), 0, 0, 0, 0, ox + 40, oy + 30)
    place(w, P("bodega-prop-kiosk"), 0, 0, 0, 0, ox + 50, oy + 4)
    place(w, P("bodega-prop-pole"), 0, 0, 0, 0, ox + 60, oy + 14)
    for i in range(4):
        place(w, P("bodega-prop-bollard"), 0, 0, 0, 0, ox + 50 + 3 * i,
              oy + 26)
    place(w, P("bodega-prop-trashcans"), 0, 0, 0, 0, ox + 50, oy + 32)

    # 5) harbor: shed on the quay (y >= oy); a 12-wide finger pier runs 3
    #    modules out (-y) to a T-head whose berth face looks S. Deck top at
    #    z deck_z + 2, on piles from z 0 (the seabed in this preview).
    ox, oy = 100, -48
    build_shed(w, P, ox, oy)
    deck_z = 21
    fx = ox + 48                               # finger x origin
    deck = P("bodega-pier-deck")
    for j in range(1, 4):                      # kerbs W (k=3) and E (k=1)
        fy = oy - 12 * j
        place(w, deck, 0, 0, deck_z, 3, fx, fy)
        place(w, deck, 0, 0, deck_z, 1, fx, fy)
        for px in (1, 7):
            place(w, P("bodega-pier-pile"), 0, 0, 0, 0, fx + px, fy + 4)
        if j == 2:
            place(w, P("bodega-pier-steps"), 0, 0, deck_z - 6, 3, fx, fy)
    hx, hy = fx - 12, oy - 48                  # head: finger joins x 12..24
    for (x, y, z), ci in P("bodega-pier-head").items():
        w[(x + hx, y + hy, z + deck_z)] = ci
    for px in (1, 13, 25, 31):
        place(w, P("bodega-pier-pile"), 0, 0, 0, 0, hx + px, hy + 4)
    for px in (3, 17, 31):
        place(w, P("bodega-pier-bollard"), 0, 0, deck_z + 2, 0, hx + px,
              hy + 2)
    for px in (8, 24):                         # fenders hook over the kerb
        place(w, P("bodega-pier-fender"), 0, 0, deck_z - 5, 0, hx + px,
              hy - 2)
    place(w, P("bodega-pier-crane"), 0, 0, deck_z + 2, 0, hx + 12, hy + 2)


# ---------------------------------------------------------------- driver
def build_variant(out, variant, lite=False):
    pal, vidx, _ = bc.variant_index(variant)
    sfx = "-lite" if lite else ""
    pstem = "bodega" if variant == "bodega" else f"bodega-{variant}"
    parts = {}
    for name, fn, takes_lite in TOWN_BUILDERS:
        v = bc.make_part(fn, variant, vidx, lite, takes_lite)
        bad = bc.floater_sweep(v)
        assert not bad, f"{variant}/{name}: {len(bad)} bad components"
        parts[name] = v
        bc.write_part(out, f"{pstem}-{name[7:]}{sfx}", v, pal, preview=True)
        print(f"part {variant}/{name}{sfx}: {len(v)} vox "
              f"bounds {footprint(v)}")

    def get(n):
        return parts[n] if n in parts else part(n, variant, lite)

    world = {}
    build_town(world, get)
    bad = bc.floater_sweep(world)
    assert not bad, f"{variant}: floaters in town assembly"
    mx = min(p[0] for p in world)
    my = min(p[1] for p in world)
    mz = min(p[2] for p in world)
    world = {(x - mx, y - my, z - mz): ci for (x, y, z), ci in world.items()}
    fp = footprint(world)
    assert fp[1] <= 256 and fp[3] <= 256 and fp[5] <= 256, fp
    stem = f"bodega-town-{variant}-v1{sfx}"
    bc.write_vox(os.path.join(out, stem + ".vox"), world, pal)
    bc.render_preview(os.path.join(out, stem + "_preview.png"), world, pal,
                      scale=4)
    print(f"variant {variant}{sfx}: town {len(world)} voxels, bounds {fp}")


if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))
    args = bc.parse_args(sys.argv[1:])
    out = args.out or HERE
    os.makedirs(out, exist_ok=True)
    for variant in args.variants:
        print(f"=== variant: {variant}{' (lite)' if args.lite else ''} ===")
        build_variant(out, variant, args.lite)
