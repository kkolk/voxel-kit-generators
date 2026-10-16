#!/usr/bin/env python3
"""encamp_medical_tent_v1.py — Strike Bay encampment TIMBER set piece: MEDICAL TENT.

Gitea kkolk/strike-bay #669. Concept:
.claude/workspace/encampment/medical-tent-concept.png

LANDMARK MAP (file coords; z-up, 1 voxel = 0.15 m, origin at the pad
footprint min corner, ground level = pad top z=1, front faces file -y):

  FRAME: +x right when viewed from the front, +y toward the rear,
         +z up. FRONT is -y (the open long side, wall plane y=12).

  PAD:   dirt pad x0..44, y0..39, z=0 (surface z=1) with grass fringe;
         ~0.6-0.8 m dirt margins beyond the outermost props/stakes.

  TENT:  house-shaped ridge tent x8..34 (3.9 m wide), y12..30 (2.7 m
         deep): vertical canvas back/side walls z1..9 (~1.2 m) panelled
         in three olive tones (#5f6b3a / #6b7842 / #545f33) with dark
         seams and a dark hem band; gabled side walls rise into the
         roof (ridge z=15 along x at y=21, dark ridge pole x5..37 with
         a 1-voxel poke past each gable, dark ridge-end caps on both
         gable peaks). Roof slopes one flat olive
         tone each (FRONT y12..21 flush to the eave, no awning droop;
         BACK y21..32) with large darker camo patches (#3a441f), never
         per-voxel noise or per-row bands.

  FRONT: the -y long side is fully OPEN x8..34 (no front wall below the
         eave), framed by 3 full-height dark posts (x12/21/30, y12,
         z1..9). Rolled-up canvas tube (2x2 darker olive, x8..34, y12,
         z7..9) with dark tie straps along the eave, so the game
         camera sees the cots and crates under the roof.

  CROSS: 10x8 WHITE plate (#ecebe4, x16..26, rows y12..19, ~1.5 x 1.2
         m) laid on the front slope over the opening, no frame, crisp
         RED cross (#c0282a) with full-bleed 2-thick arms (vertical
         x20..21, horizontal y15..16). The dominant read.

  DOOR_POINT (21, 6, 1): on the pad in front of the opening, centred.

  INTERIOR (visible at game yaw 0 through the opening): 2 folding cots
         along y (A x14..17, B x24..27, y13..26, olive tops z4, dark X
         legs, paper pillows at the head y13..15); medical crate stacks
         along the rear wall (olive x9..14 / slate+amber x28..33,
         y25..28, 2 high) with a white/red-cross box on the left stack;
         white 2-high medical column centre-back (x18..22, y25..28,
         small red crosses); amber+olive stack mid-left (x9..13,
         y17..20).

  TABLE: front-right outside (x26..32, y5..9, pale top z5): white
         first-aid box (x27..30, y6..8, z6..8, red crosses on front and
         top faces), olive crate below (x27..31, y5..8, z1..4).

  CRATES: rectilinear 2x2 crates 2 high + 1 on top toward the outer
         side (5 per stack), each 4x3x3 with square edges, flat olive
         #5a6b2f / slate #4a5058 sides, lighter top faces, 1-voxel tan
         #a8763a rims on the top edge only: left x4..12, right x32..40,
         both y2..8.

  GUYS:   rope lines from the eaves to stakes over bare dirt: front
         eaves flank the door path outside the stacks to (15,3)/(27,3),
         rear eaves to (4,34)/(38,34).

  PARTS:
    body — everything static. One 6-connected component. No flag in the
    concept: no FLAG_PIVOT, no flag part.

Printed by the generator: FOOTPRINT, HEIGHT, DOOR_POINT, body count and
component count.
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import encamp_timber as E

rng = random.Random(669)

BASE_PALETTE = [  # (name, rgb); color index = position + 1
    ("dirt",          (150, 110,  72)),  # 1  pad dirt
    ("dirt_dark",     (118,  84,  54)),  # 2  pad speckle
    ("grass",         (107, 132,  62)),  # 3  pad border
    ("grass_dark",    ( 82, 104,  48)),  # 4  pad border shade
    ("timber",        (122,  88,  54)),  # 5  light wood
    ("timber_dark",   ( 88,  62,  38)),  # 6  posts, beams, ridge
    ("plank",         (158, 124,  80)),  # 7  table legs
    ("plank_dark",    (128,  98,  62)),  # 8  wood shade
    ("olive",         ( 90, 107,  47)),  # 9  crates (#5a6b2f)
    ("olive_dark",    ( 64,  78,  34)),  # 10 crate bands/corners
    ("olive_lite",    (118, 134,  66)),  # 11 crate lids
    ("slate",         ( 74,  80,  88)),  # 12 slate crates (#4a5058)
    ("slate_dark",    ( 52,  56,  64)),  # 13 slate bands
    ("slate_lite",    ( 93, 100, 108)),  # 14 slate lids
    ("amber",         (168, 118,  58)),  # 15 amber crates (#a8763a)
    ("amber_dark",    (128,  86,  42)),  # 16 amber bands
    ("amber_lite",    (198, 150,  84)),  # 17 amber lids
    ("canvas",        ( 95, 107,  58)),  # 18 wall/roof panel A (#5f6b3a)
    ("canvas_mid",    ( 84,  95,  51)),  # 19 panel B (#545f33)
    ("canvas_lite",   (107, 120,  66)),  # 20 panel C (#6b7842)
    ("canvas_seam",   ( 62,  70,  38)),  # 21 seams + hem band
    ("patch_dark",    ( 58,  68,  31)),  # 22 large camo patches (#3a441f)
    ("paper",         (232, 228, 216)),  # 23 pillows (#e8e4d8)
    ("pale_wood",     (201, 164, 106)),  # 24 table top (#c9a46a)
    ("rope",          (186, 158, 108)),  # 25 guy ropes
    ("white",         (236, 235, 228)),  # 26 cross plate (#ecebe4)
    ("red",           (192,  40,  42)),  # 27 cross (#c0282a)
]
CI = {name: i + 1 for i, (name, _) in enumerate(BASE_PALETTE)}
DOOR_POINT = (21, 6, 1)
FOOTPRINT = (44, 39)
HEIGHT = 16

TONES = ("canvas", "canvas_mid", "canvas_lite")

body = {}

OLIVE = ("olive", "olive_dark", "olive_lite")
SLATE = ("slate", "slate_dark", "slate_lite")
AMBER = ("amber", "amber_dark", "amber_lite")


def crate(x, y, z, w, dp, h, trio):
    E.hero_crate(body, CI, x, y, z, w, dp, h, trio)


# ------------------------------------------------------------ pad (z=0, top z=1)
E.dirt_pad(body, CI, rng, 0, 44, 0, 39)
for _p in [p for p in body if p[2] == 0]:  # bitten-edge singletons
    _x, _y, _z = _p
    if not any(q in body for q in ((_x + 1, _y, _z), (_x - 1, _y, _z),
                                   (_x, _y + 1, _z), (_x, _y - 1, _z))):
        del body[_p]

# ------------------------------------------------------------ roof slope law (shared walls+roof)
RIDGE_Y, EAVE_Z, RIDGE_Z = 21, 9, 15


def slope_z(y):
    """Roof sheet height at row y (front y12..21, back y21..32)."""
    if y <= RIDGE_Y:
        return EAVE_Z + (y - 10) * 6 // 11
    return RIDGE_Z - (y - RIDGE_Y) * 6 // 11


# ------------------------------------------------------------ walls (canvas, panelled)
E.canvas_panel_wall(body, CI, 8, 34, 29, 30, 1, 11, TONES,  # back, to eave+1
                    seam="canvas_seam", hem="canvas_seam", panel=5, axis="x")
for _gx in (8, 33):  # gable side walls: full columns into the roof
    for _y in range(12, 30):
        _ztop = slope_z(_y)
        for _z in range(1, _ztop + 1):
            _k = _y - 12
            if 19 <= _y <= 23 and _z >= _ztop - 1:
                _c = "timber_dark"  # dark ridge-end cap, not an olive lump
            elif _z < 2:
                _c = "canvas_seam"
            elif _k % 5 == 0:
                _c = "canvas_seam"
            else:
                _c = TONES[(_k // 5) % 3]
            body[(_gx, _y, _z)] = CI[_c]

# ------------------------------------------------------------ 3 front posts, full height to eave
for _px in (12, 21, 30):
    E.box(body, CI, _px, _px + 1, 12, 13, 1, 9, "timber_dark")

# ------------------------------------------------------------ rolled-up front canvas (top of opening)
# rolled-up front canvas (2x2 darker-olive tube along the full eave)
for _x in range(8, 34):
    for _z in range(7, 9):
        body[(_x, 12, _z)] = CI["patch_dark"]
for _x in range(10, 34, 6):  # dark tie straps
    body[(_x, 12, 7)] = CI["timber_dark"]
    body[(_x, 12, 8)] = CI["timber_dark"]

# ------------------------------------------------------------ eave beam (front) ties posts to roof
E.box(body, CI, 8, 34, 12, 13, 9, 10, "timber_dark")

# ------------------------------------------------------------ roof sheets: one flat tone per slope
# (front pulled back flush to the eave at y12, no awning droop) with
# large camo patches, never per-voxel noise or per-row bands
ROOF_X0, ROOF_X1 = 6, 36
for _x in range(ROOF_X0, ROOF_X1):
    for _y in range(12, 33):
        body[(_x, _y, slope_z(_y))] = CI["canvas"]
for _x in range(ROOF_X0, ROOF_X1):  # bridge slope steps from below
    for _y in range(13, 33):
        if slope_z(_y) != slope_z(_y - 1):
            _zh = slope_z(_y)
            if (_x, _y, _zh - 1) not in body:
                body[(_x, _y, _zh - 1)] = CI["canvas_seam"]
for _px, _py, _pr in ((11, 16, 3), (14, 26, 4), (28, 25, 3)):
    for _x in range(ROOF_X0, ROOF_X1):
        for _y in range(12, 33):
            if (_x - _px) ** 2 + (_y - _py) ** 2 <= _pr ** 2:
                body[(_x, _y, slope_z(_y))] = CI["patch_dark"]

# ------------------------------------------------------------ ridge pole (1-voxel poke past each gable)
E.box(body, CI, 5, 37, 21, 22, 15, 16, "timber_dark")

# ------------------------------------------------------------ cross plate: 10x8 white sign laid on
# the front slope (rows y12..19, ~1.5 x 1.2 m), full-bleed 2-thick red
# cross arms, no frame — the dominant read
for _x in range(16, 26):
    for _y in range(12, 20):
        if 20 <= _x <= 21 or 15 <= _y <= 16:
            _c = "red"
        else:
            _c = "white"
        body[(_x, _y, slope_z(_y) + 1)] = CI[_c]

# ------------------------------------------------------------ cots (2): olive tops, dark X legs
def cot(x0):
    E.box(body, CI, x0, x0 + 4, 13, 26, 4, 5, "olive")  # top
    for _lx in (x0, x0 + 3):
        for _ly in (13, 25):
            E.box(body, CI, _lx, _lx + 1, _ly, _ly + 1, 1, 4, "timber_dark")
        E.box(body, CI, _lx, _lx + 1, 13, 26, 3, 4, "timber_dark")  # rail
        E.line6(body, CI, (_lx, 13, 1), (_lx, 25, 3), color="timber_dark")
        E.line6(body, CI, (_lx, 13, 3), (_lx, 25, 1), color="timber_dark")
    E.box(body, CI, x0, x0 + 4, 13, 15, 5, 6, "paper")  # pillow (head, front)


cot(14)
cot(24)

# ------------------------------------------------------------ interior crate stacks (rear + mid walls)
crate(9, 25, 1, 5, 3, 4, OLIVE)
crate(9, 25, 5, 5, 3, 3, OLIVE)
crate(28, 25, 1, 5, 3, 4, SLATE)
crate(28, 25, 5, 5, 3, 3, AMBER)
crate(9, 17, 1, 4, 3, 3, AMBER)
crate(9, 17, 4, 4, 3, 3, OLIVE)
# white med box with red cross on the left-rear stack
E.box(body, CI, 10, 13, 25, 27, 8, 10, "white")
for _rx in range(10, 13):
    body[(_rx, 25, 9)] = CI["red"]  # front-face bar
    body[(_rx, 26, 9)] = CI["red"]  # top-face bar
body[(11, 25, 8)] = CI["red"]
body[(11, 26, 9)] = CI["red"]
# white medical crate column (2-high, small red crosses) centre-back
for _wz in (1, 4):
    E.box(body, CI, 18, 22, 25, 28, _wz, _wz + 3, "white")
for _wx in (19, 20):  # small red crosses on both front faces ...
    for _wz in range(1, 4):
        body[(_wx, 25, _wz)] = CI["red"]
    for _wz in range(4, 7):
        body[(_wx, 25, _wz)] = CI["red"]
for _wx in range(18, 22):
    body[(_wx, 25, 2)] = CI["red"]
    body[(_wx, 25, 5)] = CI["red"]
for _wy in range(25, 28):  # ... and on the top face
    body[(19, _wy, 6)] = CI["red"]
    body[(20, _wy, 6)] = CI["red"]
for _wx in range(18, 22):
    body[(_wx, 26, 6)] = CI["red"]

# ------------------------------------------------------------ corner stacks: 2x2 crates 2 high + 1
# on top toward the outer side (5 crates each), flat olive/slate sides
# with square edges, lighter top faces, tan rims on the top edge only
def flat_crate(x, y, z, trio):
    base, _dark, lite = trio
    E.box(body, CI, x, x + 4, y, y + 3, z, z + 3, base)
    for _xx in range(x, x + 4):
        for _yy in range(y, y + 3):
            _edge = _xx in (x, x + 3) or _yy in (y, y + 2)
            body[(_xx, _yy, z + 2)] = CI["amber" if _edge else lite]
for _cx, _a, _b, _toff in ((4, OLIVE, SLATE, 0), (32, SLATE, OLIVE, 4)):
    flat_crate(_cx, 2, 1, _a)
    flat_crate(_cx + 4, 2, 1, _b)
    flat_crate(_cx, 5, 1, _b)
    flat_crate(_cx + 4, 5, 1, _a)
    flat_crate(_cx, 2, 4, _b)
    flat_crate(_cx + 4, 2, 4, _a)
    flat_crate(_cx, 5, 4, _a)
    flat_crate(_cx + 4, 5, 4, _b)
    flat_crate(_cx + _toff, 2, 7, _a)

# ------------------------------------------------------------ table (front-right) + aid box + crate below
E.box(body, CI, 27, 31, 5, 8, 1, 4, "olive")  # crate below (olive 4x3x3)
E.box(body, CI, 27, 31, 5, 8, 3, 4, "olive_dark")  # lid band read
for _lx in (26, 31):
    for _ly in (5, 8):
        E.box(body, CI, _lx, _lx + 1, _ly, _ly + 1, 1, 5, "plank_dark")
E.box(body, CI, 26, 32, 5, 9, 5, 6, "pale_wood")  # pale top
for _x in range(26, 32):  # darker board gaps on front/rear top edges
    if _x % 3 == 2:
        body[(_x, 5, 5)] = CI["plank_dark"]
        body[(_x, 8, 5)] = CI["plank_dark"]
E.box(body, CI, 27, 30, 6, 8, 6, 8, "white")  # first-aid box
body[(28, 6, 6)] = CI["red"]
body[(28, 6, 7)] = CI["red"]
body[(27, 6, 7)] = CI["red"]
body[(29, 6, 7)] = CI["red"]  # front-face cross
body[(28, 6, 7)] = CI["red"]
body[(28, 7, 7)] = CI["red"]
body[(27, 7, 7)] = CI["red"]
body[(29, 7, 7)] = CI["red"]  # top-face cross

# ------------------------------------------------------------ guy ropes + stakes (front pairs flank
# the door path outside the crate stacks; rear pairs to the back
# corners, all over bare dirt)
for _sx, _sy in ((15, 3), (27, 3), (4, 34), (38, 34)):
    E.box(body, CI, _sx, _sx + 1, _sy, _sy + 1, 1, 3, "timber_dark")
E.line6(body, CI, (8, 12, 10), (15, 3, 2), color="rope")
E.line6(body, CI, (34, 12, 10), (27, 3, 2), color="rope")
E.line6(body, CI, (8, 32, 9), (4, 34, 2), color="rope")
E.line6(body, CI, (34, 32, 9), (38, 34, 2), color="rope")

assembled = dict(body)

PALETTE = BASE_PALETTE

PARTS = {"body": body, "assembled": assembled}


def write_vox(path, vox, palette=None):
    import struct
    pal = palette or BASE_PALETTE
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    sx, sy, sz = max(xs) + 1, max(ys) + 1, max(zs) + 1
    xyzi = bytearray()
    for (x, y, z), ci in sorted(vox.items()):
        xyzi += struct.pack("BBBB", x, z, y, ci)  # z-up -> magica y-up
    rgba = bytearray()
    for i in range(256):
        if i < len(pal):
            r, g, b = pal[i][1]
            rgba += struct.pack("BBBB", r, g, b, 255)
        else:
            rgba += struct.pack("BBBB", 0, 0, 0, 0)
    kids = bytearray()
    for tag, content in ((b"SIZE", struct.pack("<iii", sx, sy, sz)),
                         (b"XYZI", struct.pack("<i", len(vox)) + bytes(xyzi)),
                         (b"RGBA", bytes(rgba))):
        kids += tag + struct.pack("<ii", len(content), 0) + content
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 150)
                + b"MAIN" + struct.pack("<ii", 0, len(kids)) + bytes(kids))
    print(f"wrote {path} ({len(vox)} voxels)")


if __name__ == "__main__":
    import json

    print(f"body: {len(body)} voxels, {E.n_components(body)} component(s)")
    print(f"DOOR_POINT={DOOR_POINT} FOOTPRINT={FOOTPRINT} HEIGHT={HEIGHT}")
    (bb0, bb1) = E.bbox(assembled)
    print(f"assembled bbox: {bb0}..{bb1}")
    if "--viewer-json" in sys.argv:
        print(json.dumps({
            "parts": {
                "body": {"voxels": len(body), "pivot": None},
            },
            "palette_names": [n for n, _ in BASE_PALETTE],
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
        write_vox(os.path.join(out, "encamp_medical_tent_v1_body.vox"), body)
