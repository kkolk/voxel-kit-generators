#!/usr/bin/env python3
"""encamp_comms_tower_v1.py — Strike Bay encampment TIMBER set piece: RADIO / COMMS TOWER.

Landmark map (file coords, z-up, 1 voxel = 0.15 m; origin = pad footprint
min corner at ground level = pad top z=1):
  frame:   x = left/right (left = min x viewed from the front),
           y = depth (FRONT = file -y, min y), z = up.
  front:   cabin fronts at y=16 (doors + windows face -y); mast front face
           at y=17; open crate yard y4..14 before them.
  mast:    square timber lattice x19..28, y17..26 (10x10 voxels = 1.5 m
           square), 4 corner posts 2x2 (z1..57, dark timber), lighter warm
           wood (#8a6238) rung frames on all 4 faces every 8 voxels
           (z9..57), ONE diagonal per bay on FRONT + BACK only
           (alternating direction), side faces rungs only, dark base
           collar z3..4. NO solid cap: the top rung (z57) closes the
           lattice. Interior is empty air.
  ladder:  dark-wood ladder up the front face of the front-left post
           (rails x19..20, y16, z2..57 + rung bars x18..21 every 4 z).
  head:    2-wide grey mount bar (x23..24, y18..26, z58) + 1-voxel
           crossbar x18..28 at y22, z59 with 4 vertical whip antennas 1x1
           (x20/22/24/26, 8/12/9/12 tall: 3 heights) and a 3x3x2 relay
           box hung on the east end. Top voxel z71.
  guys:    4 mid-grey 1-voxel true-diagonal wires (own part "wires",
           26-connected: diagonal-adjacent voxels allowed, exactly 1 voxel
           per step, NO 6-connectivity staircase) from the corner posts at
           z38 (2/3 height) down to ground stakes 0.5 m inside the pad
           corners: 3x3x1 anchor block + 2x2x4 dark-wood post. Wire voxels
           never overlap body (ends sit adjacent to post/stake wood). The
           game drops "wires" when the mast is destroyed.
Constants:
  DOOR_POINT = (10, 12, 1) -- soldiers step out here (pad, before left door)
  FOOTPRINT  = (48, 44)    -- pad bbox in voxels (7.2 x 6.6 m)
  HEIGHT     = 72          -- tallest whip tip voxel z=71
  (NO flag in the concept: no FLAG_PIVOT, no flag part.)
Parts:
  body -- everything static except the wires (ONE 6-connected component)
  wires -- 4 guy wires (4 components, 26-connected, droppable)
  assembled -- body + wires (rendering)
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import encamp_timber as E

rng = random.Random(671)

PALETTE = [  # (name, rgb); color index = position + 1
    ("dirt",          (150, 110,  72)),  # 1  pad dirt
    ("dirt_dark",     (118,  84,  54)),  # 2  pad speckle
    ("grass",         (107, 132,  62)),  # 3  pad border
    ("grass_dark",    ( 82, 104,  48)),  # 4  pad border shade
    ("timber",        (122,  88,  54)),  # 5  mast posts, frames
    ("timber_dark",   ( 88,  62,  38)),  # 6  collars, seams, cap
    ("plank",         (158, 124,  80)),  # 7  steps, door frames
    ("plank_dark",    (128,  98,  62)),  # 8  step nosing
    ("lattice",       (138,  98,  56)),  # 9  mast rungs + braces (#8a6238)
    ("olive",         ( 90, 107,  47)),  # 10 crates (#5a6b2f)
    ("olive_dark",    ( 64,  78,  34)),  # 11 crate bands/corners
    ("olive_lite",    (118, 134,  66)),  # 12 crate lids
    ("slate",         ( 74,  80,  88)),  # 13 slate crates (#4a5058)
    ("slate_dark",    ( 52,  56,  64)),  # 14 slate bands/corners
    ("slate_lite",    ( 93, 100, 108)),  # 15 slate lids
    ("amber",         (168, 118,  58)),  # 16 amber crates (#a8763a)
    ("amber_dark",    (128,  86,  42)),  # 17 amber bands/corners
    ("amber_lite",    (198, 150,  84)),  # 18 amber lids
    ("cabin",         ( 82,  98,  54)),  # 19 container walls
    ("cabin_dark",    ( 58,  72,  38)),  # 20 ribs, base course, roof rim
    ("cabin_lite",    (110, 126,  74)),  # 21 roof plate
    ("metal",         (154, 158, 162)),  # 22 crossbar, whips, vents (#9a9ea2)
    ("metal_dark",    ( 70,  72,  78)),  # 23 vent shade
    ("wire",          (106, 110, 114)),  # 24 guy wires (#6a6e72)
    ("glass_dark",    ( 28,  32,  38)),  # 25 windows
    ("door_dark",     ( 34,  38,  26)),  # 26 doors
]

DOOR_POINT = (10, 12, 1)
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

FOOTPRINT = (48, 44)
HEIGHT = 72

body = {}

OLIVE = ("olive", "olive_dark", "olive_lite")
SLATE = ("slate", "slate_dark", "slate_lite")
AMBER = ("amber", "amber_dark", "amber_lite")


def crate(x, y, z, w, dp, h, trio):
    E.hero_crate(body, CI, x, y, z, w, dp, h, trio)


def ammo_can(x, y, z):
    """Small olive ammo can 3x2x3 with a darker lid band."""
    E.box(body, CI, x, x + 3, y, y + 2, z, z + 3, "olive")
    E.box(body, CI, x, x + 3, y, y + 2, z + 2, z + 3, "olive_dark")


# ------------------------------------------------------------ pad (z=0, top z=1)
E.dirt_pad(body, CI, rng, 0, 48, 0, 44)
for _p in [p for p in body if p[2] == 0]:  # bitten-edge singletons
    _x, _y, _z = _p
    if not any(q in body for q in ((_x + 1, _y, _z), (_x - 1, _y, _z),
                                   (_x, _y + 1, _z), (_x, _y - 1, _z),
                                   (_x, _y, _z + 1))):
        del body[_p]

# ------------------------------------------------------------ mast posts (2x2 timber, z1..57)
for _px in (19, 27):
    for _py in (17, 25):
        E.box(body, CI, _px, _px + 2, _py, _py + 2, 1, 58, "timber")
# dark base collar beams on all 4 faces (z3..4)
E.box(body, CI, 19, 29, 17, 18, 3, 5, "timber_dark")  # front
E.box(body, CI, 19, 29, 26, 27, 3, 5, "timber_dark")  # back
E.box(body, CI, 19, 20, 17, 27, 3, 5, "timber_dark")  # left
E.box(body, CI, 28, 29, 17, 27, 3, 5, "timber_dark")  # right

# ------------------------------------------------------------ rung frames (lattice wood, every 8)
LEVELS = [9, 17, 25, 33, 41, 49, 57]
for _z in LEVELS:
    E.box(body, CI, 19, 29, 17, 18, _z, _z + 1, "lattice")  # front rung
    E.box(body, CI, 19, 29, 26, 27, _z, _z + 1, "lattice")  # back rung
    E.box(body, CI, 19, 20, 17, 27, _z, _z + 1, "lattice")  # left rung
    E.box(body, CI, 28, 29, 17, 27, _z, _z + 1, "lattice")  # right rung
_prev = 1
for _bi, _zhi in enumerate(LEVELS):
    # ONE diagonal per bay on FRONT + BACK only (alternating direction),
    # sides carry rungs only: real see-through gaps in the 3/4 views.
    _zlo = _prev + 1
    if _bi % 2 == 0:
        E.line6(body, CI, (19, 17, _zlo), (28, 17, _zhi - 1), "lattice")
        E.line6(body, CI, (28, 26, _zlo), (19, 26, _zhi - 1), "lattice")
    else:
        E.line6(body, CI, (28, 17, _zlo), (19, 17, _zhi - 1), "lattice")
        E.line6(body, CI, (19, 26, _zlo), (28, 26, _zhi - 1), "lattice")
    _prev = _zhi

# ------------------------------------------------------------ ladder up the front-left post
E.box(body, CI, 19, 20, 16, 17, 2, 58, "timber_dark")  # rail L (on post)
E.box(body, CI, 20, 21, 16, 17, 2, 58, "timber_dark")  # rail R (on post)
for _rz in range(4, 58, 4):  # rung bars, protruding past both rails
    E.box(body, CI, 18, 22, 16, 17, _rz, _rz + 1, "timber_dark")

# No solid cap: the top rung (z57) closes the lattice; a 2-wide grey mount
# bar spans front-back across the middle, carrying the antenna crossbar.
E.box(body, CI, 23, 25, 18, 27, 58, 59, "metal")  # mount bar, 2 wide
E.box(body, CI, 18, 29, 22, 23, 59, 60, "metal")  # crossbar, 1 thick
for _wx, _wh in ((20, 8), (22, 12), (24, 9), (26, 12)):  # 4 whips, 1x1
    E.box(body, CI, _wx, _wx + 1, 22, 23, 60, 60 + _wh, "metal")
E.box(body, CI, 28, 31, 21, 24, 59, 61, "metal")  # side box (dish/relay)

# ------------------------------------------------------------ corner stakes (body) + guy wires (own part)
for _sx, _sy in ((3, 3), (43, 3), (3, 39), (43, 39)):
    E.box(body, CI, _sx, _sx + 3, _sy, _sy + 3, 1, 2, "timber_dark")  # anchor
    E.box(body, CI, _sx, _sx + 2, _sy, _sy + 2, 1, 5, "timber")       # 2x2x4
wires = {}


def dline(a, b):
    """True 1-voxel diagonal from a to b in the wires part: exactly one
    voxel per step along the longest axis, others rounded (26-connected,
    NOT 6-connected: diagonal-adjacent voxels allowed). Voxels landing
    inside body (mast posts, stake tops) are skipped so the parts never
    share a voxel; the wire ends adjacent to the wood it ties to."""
    _n = max(abs(b[0] - a[0]), abs(b[1] - a[1]), abs(b[2] - a[2]))
    for _i in range(_n + 1):
        _t = _i / _n
        _p = (round(a[0] + (b[0] - a[0]) * _t),
              round(a[1] + (b[1] - a[1]) * _t),
              round(a[2] + (b[2] - a[2]) * _t))
        if _p not in body:
            wires[_p] = CI["wire"]


dline((20, 17, 38), (4, 4, 4))
dline((27, 17, 38), (44, 4, 4))
dline((20, 26, 38), (4, 40, 4))
dline((27, 26, 38), (44, 40, 4))


# ------------------------------------------------------------ equipment cabins (ribbed, hollow)
def cabin(x0, door_cx):
    """14x12 olive cabin: floor z1, ribbed walls z2..11, roof z12 + rim z13,
    door + window on the front face (y=16), vent + pipe on the roof.
    door_cx = door centre x."""
    x1, y0, y1 = x0 + 14, 16, 28
    E.box(body, CI, x0, x1, y0, y1, 1, 2, "timber_dark")  # skid floor
    for _z in range(2, 12):  # walls with dark ribs every 3rd column
        for _x in range(x0, x1):
            for _y in (y0, y1 - 1):
                _c = "cabin_dark" if (_x - x0) % 3 == 2 or _z == 2 else "cabin"
                body[(_x, _y, _z)] = CI[_c]
        for _y in range(y0 + 1, y1 - 1):
            for _xx in (x0, x1 - 1):
                _c = "cabin_dark" if (_y - y0) % 3 == 2 or _z == 2 else "cabin"
                body[(_xx, _y, _z)] = CI[_c]
    E.box(body, CI, x0, x1, y0, y1, 12, 13, "cabin_lite")  # roof plate
    for _x in range(x0, x1):  # dark roof rim
        for _y in range(y0, y1):
            if _x in (x0, x1 - 1) or _y in (y0, y1 - 1):
                body[(_x, _y, 13)] = CI["cabin_dark"]
    E.box(body, CI, x0 + 8, x0 + 11, y0 + 4, y0 + 7, 13, 15, "metal")  # vent
    E.box(body, CI, x0 + 8, x0 + 11, y0 + 4, y0 + 7, 15, 16, "metal_dark")
    E.box(body, CI, x0 + 3, x0 + 4, y0 + 8, y0 + 9, 13, 16, "metal_dark")  # pipe
    _dx0 = door_cx - 1  # 3-wide dark door z2..8 + timber frame
    E.box(body, CI, _dx0, _dx0 + 3, y0, y0 + 1, 2, 9, "door_dark")
    E.box(body, CI, _dx0 - 1, _dx0, y0, y0 + 1, 2, 9, "timber")
    E.box(body, CI, _dx0 + 3, _dx0 + 4, y0, y0 + 1, 2, 9, "timber")
    E.box(body, CI, _dx0 - 1, _dx0 + 4, y0, y0 + 1, 9, 10, "timber")  # lintel
    E.box(body, CI, _dx0 - 1, _dx0 + 4, y0 - 3, y0, 1, 2, "plank")  # step
    _wx0 = _dx0 + 5  # 2x2 dark window z6..7 + frame
    E.box(body, CI, _wx0, _wx0 + 2, y0, y0 + 1, 6, 8, "glass_dark")
    E.box(body, CI, _wx0 - 1, _wx0 + 3, y0, y0 + 1, 5, 6, "timber")
    E.box(body, CI, _wx0 - 1, _wx0 + 3, y0, y0 + 1, 8, 9, "timber")


cabin(5, 10)    # left cabin, door centre x=10
cabin(29, 34)   # right cabin, door centre x=34

# ------------------------------------------------------------ crates + ammo cans
crate(7, 5, 1, 5, 4, 4, OLIVE)     # front-left stack, base
crate(8, 6, 5, 4, 3, 3, SLATE)     # front-left stack, topper
crate(20, 4, 1, 4, 3, 3, AMBER)    # front-middle stack, base
crate(20, 4, 4, 4, 3, 3, SLATE)    # front-middle stack, topper
crate(33, 4, 1, 5, 4, 4, SLATE)    # right stack, base
crate(34, 5, 5, 4, 3, 3, OLIVE)    # right stack, topper
crate(39, 8, 1, 4, 3, 3, AMBER)    # right single
crate(1, 20, 1, 4, 3, 3, AMBER)    # left flank, base
crate(1, 24, 1, 4, 3, 3, SLATE)    # left flank, second
crate(1, 24, 4, 4, 3, 3, OLIVE)    # left flank, topper
crate(8, 33, 1, 4, 3, 3, OLIVE)    # back-left single
crate(30, 32, 1, 5, 4, 4, AMBER)   # back-right single
ammo_can(17, 12, 1)
ammo_can(25, 12, 1)
ammo_can(38, 12, 1)

assembled = dict(body)
assembled.update(wires)

PARTS = {"body": body, "wires": wires, "assembled": assembled}


def write_vox(path, vox, palette=PALETTE):
    import struct
    xs = [p[0] for p in vox]
    ys = [p[1] for p in vox]
    zs = [p[2] for p in vox]
    sx, sy, sz = max(xs) + 1, max(ys) + 1, max(zs) + 1
    pal = [rgb for _, rgb in palette] + [(0, 0, 0)] * (256 - len(palette))
    xyzi = bytearray(struct.pack("<i", len(vox)))
    for (x, y, z), ci in sorted(vox.items()):
        xyzi += struct.pack("<BBBB", x, y, z, ci)
    size_c = struct.pack("<iii", sx, sy, sz)
    rgba_c = b"".join(struct.pack("<BBBB", r, g, b, 255) for r, g, b in pal)
    kids = (b"SIZE" + struct.pack("<ii", 12, 0) + size_c
            + b"XYZI" + struct.pack("<ii", len(xyzi), 0) + bytes(xyzi)
            + b"RGBA" + struct.pack("<ii", 1024, 0) + rgba_c)
    main = b"MAIN" + struct.pack("<ii", 0, len(kids)) + kids
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 150) + main)
    print(f"wrote {path} ({len(vox)} voxels)")


if __name__ == "__main__":
    import json

    print(f"body: {len(body)} voxels, {E.n_components(body)} component(s)")
    print(f"wires: {len(wires)} voxels, {E.n_components(wires)} component(s)")
    print(f"DOOR_POINT={DOOR_POINT} FOOTPRINT={FOOTPRINT} HEIGHT={HEIGHT}")
    (bb0, bb1) = E.bbox(assembled)
    print(f"assembled bbox: {bb0}..{bb1}")
    if "--viewer-json" in sys.argv:
        print(json.dumps({
            "parts": {
                "body": {"voxels": len(body), "pivot": None},
                "wires": {"voxels": len(wires), "pivot": None},
            },
            "palette_names": [n for n, _ in PALETTE],
            "landmarks": {
                "DOOR_POINT": list(DOOR_POINT),
                "FOOTPRINT": list(FOOTPRINT),
                "HEIGHT": HEIGHT,
            },
        }))
    if "--write-vox" in sys.argv:
        here = os.path.dirname(os.path.abspath(__file__))
        out = os.path.join(here, "out")
        os.makedirs(out, exist_ok=True)
        write_vox(os.path.join(out, "encamp_comms_tower_v1_body.vox"), body)
        write_vox(os.path.join(out, "encamp_comms_tower_v1_wires.vox"), wires)
