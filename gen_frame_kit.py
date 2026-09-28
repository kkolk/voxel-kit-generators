#!/usr/bin/env python3
"""Meta-generator: emits the 27 frame-kit generator files (corners, endwalls,
roofs, steps, connectors, clutter) for the Strike Bay modular factory kit."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

HDR = '''#!/usr/bin/env python3
"""{doc}

GRID CONTRACT (identical in every kit module; see kit_contract.py):
  B=12 bay width, S=10 story height, T=2 wall thickness, wing depth 24.
  Origin at footprint min corner, ground level, z-up. No slab, no yard.
  Footprint {fpstr}; trim may exceed 1 voxel along wall-face normals only.
  Seam rule: 2-wide columns centred on bay lines; each module writes its
  half on each walled face (full 2-wide columns at interior bay lines).
  Hollow shell (walls + floor edge) + sealed interior room z 1..7.
{extra}
Slug: {slug}.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import (B, S, T, FRAME_PALETTE, CI, box, floater_sweep,
                          write_vox, render_preview)

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
]
C = CI(PALETTE)

FOOTPRINT = {fp}

@@BODY@@

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vox, fp = build_module()
    x0, x1, y0, y1, z0, z1 = fp
    for (x, y, z) in vox:  # footprint guard
        assert x0 <= x < x1, "x breach %d" % x
        assert y0 <= y < y1, "y breach %d" % y
        assert 0 <= z <= z1, "z breach %d" % z
    bad = floater_sweep(vox)
    assert not bad, "floaters!"
    write_vox(os.path.join(here, "{slug}.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "{slug}_preview.png"), vox, PALETTE)
'''

WEATHER = '''
    for (_x, _y, _z), _ci in list(vox.items()):
        if _ci == brick and random.random() < 0.06:
            vox[(_x, _y, _z)] = brick_dark
        elif _ci == conc and random.random() < 0.04:
            vox[(_x, _y, _z)] = C["concrete_dark"]'''

ROOM = '''
    rx0, rx1, ry0, ry1 = @@RX0@@, @@RX1@@, @@RY0@@, @@RY1@@
    box(vox, rx0, rx1, ry0, ry1, 0, 1, conc)
    for z in range(1, 7):
        for x in range(rx0, rx1):
            vox[(x, ry0, z)] = brick_dark
            vox[(x, ry1 - 1, z)] = brick_dark
        for y in range(ry0, ry1):
            vox[(rx0, y, z)] = brick_dark
            vox[(rx1 - 1, y, z)] = brick_dark
    for x in range(rx0 + 2, rx0 + 4):
        for z in range(1, 4):
            vox[(x, ry0, z)] = C["dark"]
    box(vox, rx0, rx1, ry0, ry1, 6, 7, C["steel_dark"])'''

# ---------------------------------------------------------------- corners
CO_BODY = '''H = @@H@@
RIBBONS = ((2, 10), (14, 22))
MULLS = (4, 7, 16, 19)


def story_south(vox, s):
    conc, brick, glass = C["concrete"], C["brick"], C["glass"]
    sash = C["steel_dark"]
    zc = s + 2 if s == 0 else s
    box(vox, -1, 3, -1, 3, zc, s + 10, conc)    # outer corner, whole + proud
    box(vox, 11, 13, -1, 3, zc, s + 10, conc)   # bay line x=12, full 2-wide
    box(vox, 23, 24, -1, 3, zc, s + 10, conc)   # east seam half
    box(vox, 0, 24, 0, 1, s + 2, s + 8, brick)  # infill, recessed 1
    box(vox, 0, 24, 0, 1, s + 2, s + 3, conc)   # sill
    for xa, xb in RIBBONS:
        for x in range(xa, xb):
            for z in range(s + 3, s + 7):
                vox[(x, 0, z)] = glass
    for x in MULLS:
        for z in range(s + 3, s + 7):
            vox[(x, 0, z)] = sash
    box(vox, 0, 24, -1, 3, s + 8, s + 10, conc)  # header beam, proud 1


def story_west(vox, s):
    conc, brick, glass = C["concrete"], C["brick"], C["glass"]
    sash = C["steel_dark"]
    zc = s + 2 if s == 0 else s
    box(vox, 11, 13, -1, 3, zc, s + 10, conc)   # (corner col shared w/ south)
    box(vox, -1, 3, 11, 13, zc, s + 10, conc)   # bay line y=12, full 2-wide
    box(vox, -1, 3, 23, 24, zc, s + 10, conc)   # north seam half
    box(vox, 0, 1, 0, 24, s + 2, s + 8, brick)
    box(vox, 0, 1, 0, 24, s + 2, s + 3, conc)
    for ya, yb in RIBBONS:
        for y in range(ya, yb):
            for z in range(s + 3, s + 7):
                vox[(0, y, z)] = glass
    for y in MULLS:
        for z in range(s + 3, s + 7):
            vox[(0, y, z)] = sash
    box(vox, -1, 3, 0, 24, s + 8, s + 10, conc)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc, brick, brick_dark = C["concrete"], C["brick"], C["brick_dark"]
    box(vox, 0, 24, 0, 2, 0, 1, conc)     # floor edge
    box(vox, 0, 24, 22, 24, 0, 1, conc)
    box(vox, 0, 2, 2, 22, 0, 1, conc)
    box(vox, 22, 24, 2, 22, 0, 1, conc)
    box(vox, 0, 24, -1, 3, 0, 2, conc)    # plinth, proud along face normals
    box(vox, -1, 3, 0, 24, 0, 2, conc)
    box(vox, 22, 24, 22, 24, 0, H, conc)  # concave courtyard column, whole
    for s in range(0, H, 10):
        story_south(vox, s)
        story_west(vox, s)
''' + ROOM.replace("@@RX0@@", "9").replace("@@RX1@@", "15"
    ).replace("@@RY0@@", "9").replace("@@RY1@@", "15") + WEATHER + '''
    return vox, FOOTPRINT
'''

CI_BODY = '''H = @@H@@
RIBBONS = ((2, 10), (14, 22))
MULLS = (4, 7, 16, 19)


def story_north(vox, s):
    conc, brick, glass = C["concrete"], C["brick"], C["glass"]
    sash = C["steel_dark"]
    zc = s + 2 if s == 0 else s
    box(vox, 21, 25, 21, 25, zc, s + 10, conc)  # concave corner, whole + proud
    box(vox, 11, 13, 21, 25, zc, s + 10, conc)  # bay line x=12, full 2-wide
    box(vox, 0, 1, 21, 25, zc, s + 10, conc)    # west seam half
    box(vox, 0, 24, 23, 24, s + 2, s + 8, brick)
    box(vox, 0, 24, 23, 24, s + 2, s + 3, conc)
    for xa, xb in RIBBONS:
        for x in range(xa, xb):
            for z in range(s + 3, s + 7):
                vox[(x, 23, z)] = glass
    for x in MULLS:
        for z in range(s + 3, s + 7):
            vox[(x, 23, z)] = sash
    box(vox, 0, 24, 21, 25, s + 8, s + 10, conc)


def story_east(vox, s):
    conc, brick, glass = C["concrete"], C["brick"], C["glass"]
    sash = C["steel_dark"]
    zc = s + 2 if s == 0 else s
    box(vox, 21, 25, 11, 13, zc, s + 10, conc)  # bay line y=12, full 2-wide
    box(vox, 21, 25, 0, 1, zc, s + 10, conc)    # south seam half
    box(vox, 23, 24, 0, 24, s + 2, s + 8, brick)
    box(vox, 23, 24, 0, 24, s + 2, s + 3, conc)
    for ya, yb in RIBBONS:
        for y in range(ya, yb):
            for z in range(s + 3, s + 7):
                vox[(23, y, z)] = glass
    for y in MULLS:
        for z in range(s + 3, s + 7):
            vox[(23, y, z)] = sash
    box(vox, 21, 25, 0, 24, s + 8, s + 10, conc)


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc, brick, brick_dark = C["concrete"], C["brick"], C["brick_dark"]
    box(vox, 0, 24, 0, 2, 0, 1, conc)
    box(vox, 0, 24, 22, 24, 0, 1, conc)
    box(vox, 0, 2, 2, 22, 0, 1, conc)
    box(vox, 22, 24, 2, 22, 0, 1, conc)
    box(vox, 0, 24, 21, 25, 0, 2, conc)
    box(vox, 21, 25, 0, 24, 0, 2, conc)
    for s in range(0, H, 10):
        story_north(vox, s)
        story_east(vox, s)
''' + ROOM.replace("@@RX0@@", "9").replace("@@RX1@@", "15"
    ).replace("@@RY0@@", "9").replace("@@RY1@@", "15") + WEATHER + '''
    return vox, FOOTPRINT
'''

# ---------------------------------------------------------------- endwall
EW_BODY = '''H = @@H@@


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc, brick, brick_dark = C["concrete"], C["brick"], C["brick_dark"]
    glass, sash = C["glass"], C["steel_dark"]
    cop, roof = C["coping"], C["roof"]
    box(vox, -2, 0, 0, 2, 0, 1, conc)    # floor edge
    box(vox, -2, 0, 22, 24, 0, 1, conc)
    box(vox, -3, 0, 0, 24, 0, 2, conc)   # plinth, proud -x
    for s in range(0, H, 10):
        zc = s + 2 if s == 0 else s
        box(vox, -3, 0, 0, 2, zc, s + 10, conc)    # corner columns, whole
        box(vox, -3, 0, 22, 24, zc, s + 10, conc)
        box(vox, -3, 0, 11, 13, zc, s + 10, conc)  # intermediate, bay line
        box(vox, -1, 0, 0, 2, zc, s + 10, conc)    # seam halves for y-faces
        box(vox, -1, 0, 22, 24, zc, s + 10, conc)
        box(vox, -1, 0, 0, 24, s + 2, s + 8, brick)
        box(vox, -1, 0, 0, 24, s + 2, s + 3, conc)
        for ya, yb in ((2, 10), (14, 22)):
            for y in range(ya, yb):
                for z in range(s + 3, s + 7):
                    vox[(-1, y, z)] = glass
        for y in (4, 7, 16, 19):
            for z in range(s + 3, s + 7):
                vox[(-1, y, z)] = sash
        box(vox, -3, 0, 0, 24, s + 8, s + 10, conc)  # header beam
    box(vox, -2, 0, 0, 24, H, H + 2, roof)       # slab strip
    box(vox, -2, -1, 0, 24, H + 2, H + 5, conc)  # end parapet
    box(vox, -2, 0, 0, 1, H + 2, H + 5, conc)    # returns
    box(vox, -2, 0, 23, 24, H + 2, H + 5, conc)
    box(vox, -3, -1, 0, 24, H + 5, H + 6, cop)   # coping, proud -x
    box(vox, -2, 0, 0, 1, H + 5, H + 6, cop)
    box(vox, -2, 0, 23, 24, H + 5, H + 6, cop)
    box(vox, -2, 0, 9, 15, 0, 1, conc)           # interior room
    for z in range(1, 7):
        for x in range(-2, 0):
            vox[(x, 9, z)] = brick_dark
            vox[(x, 14, z)] = brick_dark
    box(vox, -2, 0, 9, 15, 6, 7, C["steel_dark"])
''' + WEATHER + '''
    return vox, FOOTPRINT
'''

# ---------------------------------------------------------------- roofs
RF_BODY = '''H = @@H@@


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc, roof, cop = C["concrete"], C["roof"], C["coping"]
    box(vox, 0, 12, 0, 24, H, H + 2, roof)      # slab
    box(vox, 0, 12, 0, 1, H + 2, H + 5, conc)   # parapets, y faces only
    box(vox, 0, 12, 23, 24, H + 2, H + 5, conc)
    box(vox, 0, 12, -1, 2, H + 5, H + 6, cop)   # coping, proud 1
    box(vox, 0, 12, 22, 25, H + 5, H + 6, cop)
    return vox, FOOTPRINT
'''

RCO_BODY = '''H = @@H@@


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc, roof, cop = C["concrete"], C["roof"], C["coping"]
    box(vox, 0, 24, 0, 24, H, H + 2, roof)
    box(vox, 0, 24, 0, 1, H + 2, H + 5, conc)   # parapets: south + west faces
    box(vox, 0, 1, 0, 24, H + 2, H + 5, conc)
    box(vox, 0, 24, -1, 2, H + 5, H + 6, cop)
    box(vox, -1, 2, 0, 24, H + 5, H + 6, cop)
    return vox, FOOTPRINT
'''

RCI_BODY = '''H = @@H@@


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc, roof, cop = C["concrete"], C["roof"], C["coping"]
    box(vox, 0, 24, 0, 24, H, H + 2, roof)
    box(vox, 0, 24, 23, 24, H + 2, H + 5, conc)  # parapets: north + east faces
    box(vox, 23, 24, 0, 24, H + 2, H + 5, conc)
    box(vox, 0, 24, 22, 25, H + 5, H + 6, cop)
    box(vox, 22, 25, 0, 24, H + 5, H + 6, cop)
    return vox, FOOTPRINT
'''

# ---------------------------------------------------------------- steps
STEP_BODY = '''HA, HB, HC = @@HA@@, @@HB@@, @@HC@@
SECS = ((0, 4, HA, True), (4, 8, HB, False), (8, 12, HC, True))  # x, x, H, ribbon


def stories(Hs):
    out, s = [], 0
    while s + 10 <= Hs:
        out.append((s, True))
        s += 10
    if s < Hs:
        out.append((s, False))
    return out


def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc, brick, brick_dark = C["concrete"], C["brick"], C["brick_dark"]
    glass, sash = C["glass"], C["steel_dark"]
    cop = C["coping"]
    box(vox, 0, 12, 0, 2, 0, 1, conc)
    box(vox, 0, 12, 22, 24, 0, 1, conc)
    box(vox, 0, 2, 2, 22, 0, 1, conc)
    box(vox, 10, 12, 2, 22, 0, 1, conc)
    box(vox, 0, 12, -1, 3, 0, 2, conc)   # plinth, ground story
    box(vox, 0, 12, 21, 25, 0, 2, conc)
    for sx0, sx1, Hs, rib in SECS:
        for s, full in stories(Hs):
            ztop = s + 10 if full else Hs
            for yo0, yo1, yp in ((-1, 3, 0), (21, 25, 23)):
                zc = s + 2 if s == 0 else s
                box(vox, sx0, sx0 + 1, yo0, yo1, zc, ztop, conc)
                box(vox, sx1 - 1, sx1, yo0, yo1, zc, ztop, conc)
                box(vox, sx0 + 1, sx1 - 1, yp, yp + 1, s + 2, ztop - 2 if full else ztop, brick)
                if full:
                    box(vox, sx0 + 1, sx1 - 1, yp, yp + 1, s + 2, s + 3, conc)
                    if rib:
                        for x in range(sx0 + 1, sx1 - 1):
                            for z in range(s + 3, s + 7):
                                vox[(x, yp, z)] = glass
                        for z in range(s + 3, s + 7):
                            vox[((sx0 + sx1) // 2, yp, z)] = sash
        box(vox, sx0, sx1, -1, 3, Hs - 2, Hs, conc)    # header at section top
        box(vox, sx0, sx1, 21, 25, Hs - 2, Hs, conc)
    for xb, Hlo, Hhi in ((4, HB, HA), (8, HC, HB)):    # step faces + coping
        box(vox, xb - 1, xb + 1, 0, 24, Hlo, Hhi, conc)
        box(vox, xb - 1, xb + 1, 0, 24, Hlo, Hlo + 1, cop)
''' + ROOM.replace("@@RX0@@", "3").replace("@@RX1@@", "9"
    ).replace("@@RY0@@", "9").replace("@@RY1@@", "15") + WEATHER + '''
    return vox, FOOTPRINT
'''

# ---------------------------------------------------------------- walkway / dock
WALKWAY_BODY = '''
def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc, brick, glass = C["concrete"], C["brick"], C["glass"]
    sash, roof, cop = C["steel_dark"], C["roof"], C["coping"]
    box(vox, 0, 12, 0, 8, 0, 1, conc)      # floor
    box(vox, 0, 12, -1, 3, 0, 2, conc)     # plinth
    box(vox, 0, 12, 5, 9, 0, 2, conc)
    for yo0, yo1, yp in ((-1, 3, 0), (5, 9, 7)):
        box(vox, 0, 1, yo0, yo1, 2, 8, conc)
        box(vox, 5, 7, yo0, yo1, 2, 8, conc)
        box(vox, 11, 12, yo0, yo1, 2, 8, conc)
        box(vox, 1, 11, yp, yp + 1, 2, 6, brick)
        box(vox, 1, 11, yp, yp + 1, 2, 3, conc)
        for x in range(2, 10):
            for z in range(3, 6):
                vox[(x, yp, z)] = glass
        for x in (4, 7):
            for z in range(3, 6):
                vox[(x, yp, z)] = sash
        box(vox, 0, 12, yo0, yo1, 6, 8, conc)  # top band
    for xe in (0, 11):                        # end surrounds, openings y 2..6 z 1..7
        box(vox, xe, xe + 1, 0, 8, 0, 1, conc)
        box(vox, xe, xe + 1, 0, 8, 7, 8, conc)
        box(vox, xe, xe + 1, 0, 2, 1, 7, conc)
        box(vox, xe, xe + 1, 6, 8, 1, 7, conc)
    box(vox, 0, 12, 0, 8, 8, 9, roof)        # canopy slab
    box(vox, 0, 12, 0, 1, 9, 10, conc)       # parapet
    box(vox, 0, 12, 7, 8, 9, 10, conc)
    box(vox, 0, 12, -1, 2, 10, 11, cop)      # coping
    box(vox, 0, 12, 6, 9, 10, 11, cop)
    return vox, FOOTPRINT
'''

DOCK_BODY = '''
def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc, cdark = C["concrete"], C["concrete_dark"]
    roof = C["roof"]
    box(vox, 0, 12, 0, 10, 0, 2, conc)      # platform
    box(vox, 0, 12, 0, 10, 2, 3, conc)
    box(vox, 0, 12, 0, 1, 2, 3, cdark)      # dark edge band
    box(vox, 0, 12, 9, 10, 2, 3, cdark)
    box(vox, 0, 1, 1, 9, 2, 3, cdark)
    box(vox, 11, 12, 1, 9, 2, 3, cdark)
    box(vox, 2, 4, 8, 10, 0, 9, conc)       # columns
    box(vox, 8, 10, 8, 10, 0, 9, conc)
    box(vox, 0, 12, 0, 10, 9, 10, roof)     # canopy slab
    box(vox, 0, 12, 0, 1, 8, 10, conc)      # fascia
    box(vox, 0, 12, 9, 10, 8, 10, conc)
    box(vox, 0, 1, 1, 9, 8, 10, conc)
    box(vox, 11, 12, 1, 9, 8, 10, conc)
    return vox, FOOTPRINT
'''

# ---------------------------------------------------------------- clutter
VENT_BODY = '''
def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc = C["concrete"]
    box(vox, 0, 4, 0, 4, 0, 1, C["steel_dark"])  # flashing
    box(vox, 1, 3, 1, 3, 1, 4, conc)            # louver box
    for z in range(1, 4):                        # slats, south + north
        box(vox, 1, 3, 0, 1, z, z + 1, C["steel_dark"])
        box(vox, 1, 3, 3, 4, z, z + 1, C["steel_dark"])
    box(vox, 0, 4, 0, 4, 4, 5, conc)            # cap
    return vox, FOOTPRINT
'''

SKYLIGHT_BODY = '''
def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc = C["concrete"]
    box(vox, 0, 8, 0, 4, 0, 1, conc)            # curb
    box(vox, 0, 8, 0, 1, 1, 2, C["steel_dark"])  # frame
    box(vox, 0, 8, 3, 4, 1, 2, C["steel_dark"])
    box(vox, 0, 1, 1, 3, 1, 2, C["steel_dark"])
    box(vox, 7, 8, 1, 3, 1, 2, C["steel_dark"])
    box(vox, 1, 7, 1, 3, 1, 2, C["glass"])      # glass
    box(vox, 0, 8, 0, 1, 2, 3, conc)            # cap rim
    box(vox, 0, 8, 3, 4, 2, 3, conc)
    box(vox, 0, 1, 1, 3, 2, 3, conc)
    box(vox, 7, 8, 1, 3, 2, 3, conc)
    return vox, FOOTPRINT
'''

STAIR_BODY = '''
def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    conc = C["concrete"]
    box(vox, 0, 8, 0, 1, 0, 7, conc)      # walls
    box(vox, 0, 8, 5, 6, 0, 7, conc)
    box(vox, 0, 1, 1, 5, 0, 7, conc)
    box(vox, 7, 8, 1, 5, 0, 7, conc)
    box(vox, 7, 8, 2, 4, 1, 5, C["dark"])  # door, +x face
    box(vox, 0, 8, 0, 6, 7, 8, conc)      # cap slab
    box(vox, 0, 8, 0, 6, 8, 9, C["coping"])
    return vox, FOOTPRINT
'''

PIPE_BODY = '''
def build_module():
    """Return (vox dict, footprint). Authoring coords == game coords."""
    random.seed(@@SEED@@)
    vox = {}
    box(vox, 1, 2, 1, 2, 0, 1, C["concrete_dark"])   # saddles
    box(vox, 6, 7, 1, 2, 0, 1, C["concrete_dark"])
    box(vox, 11, 12, 1, 2, 0, 1, C["concrete_dark"])
    box(vox, 0, 12, 0, 2, 1, 3, C["steel"])         # pipe
    for xs in (1, 6, 11):                            # collars
        box(vox, xs, xs + 1, 0, 2, 1, 3, C["steel_dark"])
    return vox, FOOTPRINT
'''

# ---------------------------------------------------------------- table
MODULES = [
    # slug, seed, footprint, fpstr, doc, extra, body, subs
    ("kit-frame-corner-outside-1s-v1", 31, (-1, 24, -1, 25, 0, 10),
     "x [0,24) x y [0,24), trim x/y -1 (face normals), z [0,H], H=10",
     "Strike Bay modular factory kit — FRAME outside corner, 1 story. "
     "Walls on the south (y=0) and west (x=0) faces; open (concave) faces "
     "east and north join the wing bays.",
     "Wall top H=10. Ribbons: south face x 2..10 and 14..22, west face "
     "y 2..10 and 14..22. Full 2-wide columns at the interior bay lines "
     "(x=12, y=12); outer corner column 2x2 at (0..2, 0..2) whole; concave "
     "courtyard column 2x2 at (22..24, 22..24) whole; seam halves at the "
     "open edges (x 23..24, y 23..24).",
     CO_BODY, {"@@H@@": "10", "@@SEED@@": "31"}),
    ("kit-frame-corner-outside-2s-v1", 32, (-1, 24, -1, 25, 0, 20),
     "x [0,24) x y [0,24), trim x/y -1 (face normals), z [0,H], H=20",
     "Strike Bay modular factory kit — FRAME outside corner, 2 stories. "
     "Walls on the south (y=0) and west (x=0) faces; open (concave) faces "
     "east and north join the wing bays.",
     "Wall top H=20. Ribbons per story: south face x 2..10 and 14..22, "
     "west face y 2..10 and 14..22. Full 2-wide columns at interior bay "
     "lines; outer corner 2x2 whole; concave 2x2 whole; seam halves at "
     "the open edges.",
     CO_BODY, {"@@H@@": "20", "@@SEED@@": "32"}),
    ("kit-frame-corner-outside-3s-v1", 33, (-1, 24, -1, 25, 0, 30),
     "x [0,24) x y [0,24), trim x/y -1 (face normals), z [0,H], H=30",
     "Strike Bay modular factory kit — FRAME outside corner, 3 stories. "
     "Walls on the south (y=0) and west (x=0) faces; open (concave) faces "
     "east and north join the wing bays.",
     "Wall top H=30. Ribbons per story: south face x 2..10 and 14..22, "
     "west face y 2..10 and 14..22. Full 2-wide columns at interior bay "
     "lines; outer corner 2x2 whole; concave 2x2 whole; seam halves at "
     "the open edges.",
     CO_BODY, {"@@H@@": "30", "@@SEED@@": "33"}),
    ("kit-frame-corner-inside-1s-v1", 34, (0, 25, 0, 25, 0, 10),
     "x [0,24) x y [0,24), trim +1 on x/y (far-face normals), z [0,H], H=10",
     "Strike Bay modular factory kit — FRAME inside (concave) corner, "
     "1 story. Walls on the north (y=24) and east (x=24) faces, concave "
     "point at (24,24).",
     "Wall top H=10. Ribbons: north face x 2..10 and 14..22, east face "
     "y 2..10 and 14..22. Full 2-wide columns at interior bay lines; "
     "concave corner column 2x2 at (22..24, 22..24) whole; seam halves on "
     "the west face (x 0..1) and south face (y 0..1).",
     CI_BODY, {"@@H@@": "10", "@@SEED@@": "34"}),
    ("kit-frame-corner-inside-2s-v1", 35, (0, 25, 0, 25, 0, 20),
     "x [0,24) x y [0,24), trim +1 on x/y (far-face normals), z [0,H], H=20",
     "Strike Bay modular factory kit — FRAME inside (concave) corner, "
     "2 stories. Walls on the north (y=24) and east (x=24) faces.",
     "Wall top H=20. Ribbons per story both faces. Concave corner column "
     "2x2 whole; full columns at interior bay lines; seam halves on the "
     "open edges.",
     CI_BODY, {"@@H@@": "20", "@@SEED@@": "35"}),
    ("kit-frame-corner-inside-3s-v1", 36, (0, 25, 0, 25, 0, 30),
     "x [0,24) x y [0,24), trim +1 on x/y (far-face normals), z [0,H], H=30",
     "Strike Bay modular factory kit — FRAME inside (concave) corner, "
     "3 stories. Walls on the north (y=24) and east (x=24) faces.",
     "Wall top H=30. Ribbons per story both faces. Concave corner column "
     "2x2 whole; full columns at interior bay lines; seam halves on the "
     "open edges.",
     CI_BODY, {"@@H@@": "30", "@@SEED@@": "36"}),
    ("kit-frame-endwall-flat-1s-v1", 37, (-3, 0, -1, 25, 0, 16),
     "x [-2,0) x y [0,24), trim x -3 (face normal), z [0,H+6], H=10",
     "Strike Bay modular factory kit — FRAME flat endwall cap, 1 story. "
     "Closes the west end of a wing (x -2..0); seam halves at y 0..2 and "
     "22..24 meet the wall bays' south/north faces.",
     "Wall top H=10. Whole corner columns at (x -2..0, y 0..2/22..24), "
     "intermediate column at y 11..13, ribbons y 2..10 and 14..22. End "
     "parapet U (x -2..-1 + returns y 0..1/23..24, z H+2..H+5) with coping "
     "z H+5..H+6 proud -x; slab strip z H..H+2.",
     EW_BODY, {"@@H@@": "10", "@@SEED@@": "37"}),
    ("kit-frame-endwall-flat-2s-v1", 38, (-3, 0, -1, 25, 0, 26),
     "x [-2,0) x y [0,24), trim x -3 (face normal), z [0,H+6], H=20",
     "Strike Bay modular factory kit — FRAME flat endwall cap, 2 stories.",
     "Wall top H=20. Whole corner columns, intermediate column, ribbons "
     "per story, end parapet U with coping proud -x, slab strip.",
     EW_BODY, {"@@H@@": "20", "@@SEED@@": "38"}),
    ("kit-frame-endwall-flat-3s-v1", 39, (-3, 0, -1, 25, 0, 36),
     "x [-2,0) x y [0,24), trim x -3 (face normal), z [0,H+6], H=30",
     "Strike Bay modular factory kit — FRAME flat endwall cap, 3 stories.",
     "Wall top H=30. Whole corner columns, intermediate column, ribbons "
     "per story, end parapet U with coping proud -x, slab strip.",
     EW_BODY, {"@@H@@": "30", "@@SEED@@": "39"}),
    ("kit-frame-roof-flat-1s-v1", 40, (0, 12, -1, 25, 0, 16),
     "x [0,12) x y [0,24), trim y -1 (face normal), z [H,H+6], H=10",
     "Strike Bay modular factory kit — FRAME flat roof tile, 1-story hall. "
     "Slab z H..H+2 (roof grey), concrete parapet z H+2..H+5 on the y=0 "
     "and y=24 faces only, coping z H+5..H+6 proud 1. No x-face parapets: "
     "adjacent tiles share the seam.",
     "Seats on wall tops at H=10.",
     RF_BODY, {"@@H@@": "10", "@@SEED@@": "40"}),
    ("kit-frame-roof-flat-2s-v1", 41, (0, 12, -1, 25, 0, 26),
     "x [0,12) x y [0,24), trim y -1 (face normal), z [H,H+6], H=20",
     "Strike Bay modular factory kit — FRAME flat roof tile, 2-story hall. "
     "Slab + y-face parapets + coping; no x-face parapets.",
     "Seats on wall tops at H=20.",
     RF_BODY, {"@@H@@": "20", "@@SEED@@": "41"}),
    ("kit-frame-roof-flat-3s-v1", 42, (0, 12, -1, 25, 0, 36),
     "x [0,12) x y [0,24), trim y -1 (face normal), z [H,H+6], H=30",
     "Strike Bay modular factory kit — FRAME flat roof tile, 3-story hall. "
     "Slab + y-face parapets + coping; no x-face parapets.",
     "Seats on wall tops at H=30.",
     RF_BODY, {"@@H@@": "30", "@@SEED@@": "42"}),
    ("kit-frame-roof-flat-corner-outside-1s-v1", 43, (-1, 25, -1, 25, 0, 16),
     "x [0,24) x y [0,24), trim x/y -1 (face normals), z [H,H+6], H=10",
     "Strike Bay modular factory kit — FRAME flat roof tile for outside "
     "corners, 1-story hall. Slab z H..H+2, parapet z H+2..H+5 on the "
     "south (y=0) and west (x=0) faces, coping z H+5..H+6 proud 1.",
     "Seats on the outside corner piece at H=10.",
     RCO_BODY, {"@@H@@": "10", "@@SEED@@": "43"}),
    ("kit-frame-roof-flat-corner-outside-2s-v1", 44, (-1, 25, -1, 25, 0, 26),
     "x [0,24) x y [0,24), trim x/y -1 (face normals), z [H,H+6], H=20",
     "Strike Bay modular factory kit — FRAME flat roof tile for outside "
     "corners, 2-story hall. Slab + south/west parapets + coping.",
     "Seats on the outside corner piece at H=20.",
     RCO_BODY, {"@@H@@": "20", "@@SEED@@": "44"}),
    ("kit-frame-roof-flat-corner-outside-3s-v1", 45, (-1, 25, -1, 25, 0, 36),
     "x [0,24) x y [0,24), trim x/y -1 (face normals), z [H,H+6], H=30",
     "Strike Bay modular factory kit — FRAME flat roof tile for outside "
     "corners, 3-story hall. Slab + south/west parapets + coping.",
     "Seats on the outside corner piece at H=30.",
     RCO_BODY, {"@@H@@": "30", "@@SEED@@": "45"}),
    ("kit-frame-roof-flat-corner-inside-1s-v1", 46, (0, 25, 0, 25, 0, 16),
     "x [0,24) x y [0,24), trim +1 on x/y (face normals), z [H,H+6], H=10",
     "Strike Bay modular factory kit — FRAME flat roof tile for inside "
     "(concave) corners, 1-story hall. Slab z H..H+2, parapet z H+2..H+5 "
     "on the north (y=24) and east (x=24) faces, coping z H+5..H+6 "
     "proud 1.",
     "Seats on the inside corner piece at H=10.",
     RCI_BODY, {"@@H@@": "10", "@@SEED@@": "46"}),
    ("kit-frame-roof-flat-corner-inside-2s-v1", 47, (0, 25, 0, 25, 0, 26),
     "x [0,24) x y [0,24), trim +1 on x/y (face normals), z [H,H+6], H=20",
     "Strike Bay modular factory kit — FRAME flat roof tile for inside "
     "(concave) corners, 2-story hall. Slab + north/east parapets + "
     "coping.",
     "Seats on the inside corner piece at H=20.",
     RCI_BODY, {"@@H@@": "20", "@@SEED@@": "47"}),
    ("kit-frame-roof-flat-corner-inside-3s-v1", 48, (0, 25, 0, 25, 0, 36),
     "x [0,24) x y [0,24), trim +1 on x/y (face normals), z [H,H+6], H=30",
     "Strike Bay modular factory kit — FRAME flat roof tile for inside "
     "(concave) corners, 3-story hall. Slab + north/east parapets + "
     "coping.",
     "Seats on the inside corner piece at H=30.",
     RCI_BODY, {"@@H@@": "30", "@@SEED@@": "48"}),
    ("kit-frame-step-1to2-v1", 49, (0, 12, -1, 25, 0, 20),
     "x [0,12) x y [0,24), trim y -1 (face normal), z [0,20]",
     "Strike Bay modular factory kit — FRAME stepped transition bay, "
     "1 to 2 stories. Sections x 0..4 (H=20) / x 4..8 (H=15) / x 8..12 "
     "(H=10); step faces at x=4 and x=8 are vertical concrete with a "
     "coping ledge at the lower section's top.",
     "Tall and low sections carry glass ribbons on their full stories; "
     "the mid section is plain. Header beam at each section top; plinth "
     "on the ground story.",
     STEP_BODY, {"@@HA@@": "20", "@@HB@@": "15", "@@HC@@": "10",
                 "@@SEED@@": "49"}),
    ("kit-frame-step-1to3-v1", 50, (0, 12, -1, 25, 0, 30),
     "x [0,12) x y [0,24), trim y -1 (face normal), z [0,30]",
     "Strike Bay modular factory kit — FRAME stepped transition bay, "
     "1 to 3 stories. Sections x 0..4 (H=30) / x 4..8 (H=20) / x 8..12 "
     "(H=10); concrete step faces with coping ledges at x=4 and x=8.",
     "Tall and low sections carry glass ribbons on full stories; mid "
     "section plain. Header beam at each section top.",
     STEP_BODY, {"@@HA@@": "30", "@@HB@@": "20", "@@HC@@": "10",
                 "@@SEED@@": "50"}),
    ("kit-frame-step-2to3-v1", 51, (0, 12, -1, 25, 0, 30),
     "x [0,12) x y [0,24), trim y -1 (face normal), z [0,30]",
     "Strike Bay modular factory kit — FRAME stepped transition bay, "
     "2 to 3 stories. Sections x 0..4 (H=30) / x 4..8 (H=25) / x 8..12 "
     "(H=20); concrete step faces with coping ledges at x=4 and x=8.",
     "Tall and low sections carry glass ribbons on full stories; mid "
     "section plain. Header beam at each section top.",
     STEP_BODY, {"@@HA@@": "30", "@@HB@@": "25", "@@HC@@": "20",
                 "@@SEED@@": "51"}),
    ("kit-frame-walkway-1s-v1", 52, (0, 12, -1, 9, 0, 11),
     "x [0,12) x y [0,8), trim y -1, z [0,11]",
     "Strike Bay modular factory kit — FRAME enclosed walkway, 1 story. "
     "Floor z 0..1, concrete columns + brick infill walls on the y=0 and "
     "y=8 faces (glass ribbon z 3..6), open ends at x=0 and x=12 with a "
     "concrete surround around the y 2..6 / z 1..7 opening.",
     "Canopy slab z 8..9, parapet z 9..10, coping z 10..11.",
     WALKWAY_BODY, {"@@SEED@@": "52"}),
    ("kit-frame-dock-1s-v1", 53, (0, 12, 0, 10, 0, 10),
     "x [0,12) x y [0,10), z [0,10]",
     "Strike Bay modular factory kit — FRAME covered loading dock, 1 "
     "story. Concrete platform z 0..3 with a dark edge band, two concrete "
     "columns (x 2..4 / 8..10, y 8..10) carrying a roof-grey canopy slab "
     "z 9..10 with a concrete fascia z 8..10. Back (y=0) open.",
     "Seats on grade; no parapet.",
     DOCK_BODY, {"@@SEED@@": "53"}),
    ("kit-frame-vent-v1", 54, (0, 4, 0, 4, 0, 5),
     "x [0,4) x y [0,4), z [0,5]",
     "Strike Bay modular factory kit — FRAME roof vent. Steel flashing "
     "z 0..1, concrete louver box z 1..4 with steel slats, concrete cap "
     "z 4..5.",
     "Clutter: seats on any flat roof slab; single connected component "
     "to z=0.",
     VENT_BODY, {"@@SEED@@": "54"}),
    ("kit-frame-skylight-v1", 55, (0, 8, 0, 4, 0, 3),
     "x [0,8) x y [0,4), z [0,3]",
     "Strike Bay modular factory kit — FRAME skylight. Concrete curb "
     "z 0..1, steel-framed glass pane z 1..2, concrete cap rim z 2..3.",
     "Clutter: seats on any flat roof slab.",
     SKYLIGHT_BODY, {"@@SEED@@": "55"}),
    ("kit-frame-stairhouse-v1", 56, (0, 8, 0, 6, 0, 9),
     "x [0,8) x y [0,6), z [0,9]",
     "Strike Bay modular factory kit — FRAME stairhouse. Hollow concrete "
     "box z 0..7 with a dark door on the +x face (z 1..5), cap slab "
     "z 7..8, coping z 8..9.",
     "Clutter: seats on any flat roof slab.",
     STAIR_BODY, {"@@SEED@@": "56"}),
    ("kit-frame-piperun-v1", 57, (0, 12, 0, 3, 0, 3),
     "x [0,12) x y [0,3), z [0,3]",
     "Strike Bay modular factory kit — FRAME pipe run. Three concrete "
     "saddles (x 1, 6, 11) z 0..1 carrying a 2x2 steel pipe z 1..3 along "
     "x, with steel collars at the saddles.",
     "Clutter: seats on any flat roof slab.",
     PIPE_BODY, {"@@SEED@@": "57"}),
]


def main():
    for slug, seed, fp, fpstr, doc, extra, body, subs in MODULES:
        for k, v in subs.items():
            body = body.replace(k, v)
        src = HDR.replace("{doc}", doc).replace("{fpstr}", fpstr
            ).replace("{extra}", extra).replace("{fp}", repr(fp)
            ).replace("{slug}", slug).replace("@@BODY@@", body)
        path = os.path.join(HERE, slug + ".py")
        with open(path, "w") as f:
            f.write(src)
        print("wrote", path)


if __name__ == "__main__":
    main()
