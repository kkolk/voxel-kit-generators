#!/usr/bin/env python3
"""encamp_ammo_dump_v1.py — Strike Bay encampment TIMBER set piece: AMMUNITION DUMP.

Landmark map (file coords, z-up, 1 voxel = 0.15 m; origin = pad footprint
min corner at ground level = pad top z=1):
  frame:   x = left/right (left = min x viewed from the front),
           y = depth (FRONT = file -y, min y), z = up.
  front:   flat-cut earth face at y=10 with a dominant timber portal;
           single peak row y=28 (middle-rear). back: gentle tail slope
           down to the pad foot at y=45.
  mound:   x7..48, y10..45 (42 x 36 voxels, ~6.3 x 5.4 m). Ridge
           hx(x) = 1 + round(17*cos(nx*pi/2)^0.8), nx=(x-27.5)/21: crown
           voxel z=18 (~2.7 m) at cx=27..28, rounding to z=2 at the ends.
           Gentle brow y10..27 up from the face, single peak row y=28,
           gentle (1-u)^0.85 tail to the back foot. Smooth shell (no lump
           noise) + sparse 1-high grass tufts on ~5% of grass cells.
           Shell-hollow: 4-thick cap + full front wall, empty inside
           (dark recess box hides the void at the door).
  surface: coherent low-frequency blob patches (value-noise cell 6,
           neighbours mostly share a tone): 3 grass tones on top (~70%),
           earth #7a5a3a / #5e432a only where the base slope drops >=3
           (steep lower flanks) and in 3 flank scars (guarded below h=12,
           never on the crown); 6 embedded 2x2 cut-stone blocks (1 proud)
           on the flanks. Front face wall is earth with a single grass
           lip row set back at y=11 (nothing overhangs the y=10 edge).
  stone:   light ashlar facing (tan #c8b088 faces, darker mortar): left
           x7..21 z1..6, tall right panel x33..49 z1..8 carrying the sign;
           2-row header x21..33 z14..15 over the lintel with an arched
           centre cap z16.
  portal:  1.8 m wide x 2.1 m to the lintel top: 2x2 posts x21..22 /
           x31..32, y8..10, z1..11 (dark outer skin); thick lintel
           x20..34, y8..10, z12..13 (overhangs posts by 1 each side);
           light-timber knee braces from the inner posts to the lintel.
  door:    opening x23..30, z1..10. Dark recess x23..30, y12..16 (darkest
           voxels on the model: dark floor / side walls / back wall /
           ceiling slab z11). Double plank doors: left leaf closed at
           y=11 (x23..26, ledge rows); right leaf ajar from hinge x27
           (6-connected staircase out to (30,8), tip by the right post).
  ramp:    stone-slab apron x23..31, y3..9 (flush slabs with seam grid)
           + 1-high kerbs x21 / x32 + dark sill beam at the mouth.
  sign:    10x5 light board (#d8c8a0) x34..43, z6..10, flush in the face
           plane (y10) on the tall stone panel, dark border + 2 rows of
           dark text dashes (not lettering).
  crates:  hero boxes (>=4x3x3, dark base band + light lid + dark corners)
           in olive / slate / amber: big left stack x2..16 y3..6 (3 bases
           + 2 layer-2 + topper), big right stack x36..45 y3..6 (2 bases
           + 2 layer-2 + low topper, tan/olive under the sign).
  cans:    3 ammo cans (2x2x2 + lid + latch + handle bar): (19,4), (33,4),
           (33,6).
  pad:     50 x 49 dirt with speckles + bitten grass border (E.dirt_pad).

Constants:
  DOOR_POINT = (27, 2, 1)  -- soldiers step out here (pad, before the apron)
  FOOTPRINT  = (50, 49)    -- pad bbox in voxels (7.5 x 7.35 m)
  HEIGHT     = 19          -- crown top voxel z=18
Parts:
  body -- everything static (ONE 6-connected component)
  assembled -- body (rendering)
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import encamp_timber as E

rng = random.Random(672)

PALETTE = [  # (name, rgb); color index = position + 1
    ("dirt",          (150, 110,  72)),  # 1  pad dirt
    ("dirt_dark",     (118,  84,  54)),  # 2  pad speckle
    ("grass",         (107, 132,  62)),  # 3  pad border, mound cap
    ("grass_dark",    ( 82, 104,  48)),  # 4  pad border shade, cap patch
    ("moss_lite",     (140, 155,  85)),  # 5  cap light patch
    ("earth",         (122,  90,  58)),  # 6  exposed mound earth #7a5a3a
    ("earth_dark",    ( 94,  67,  42)),  # 7  earth shade #5e432a
    ("earth_lite",    (150, 116,  74)),  # 8  earth light patch
    ("stone",         (170, 150, 112)),  # 9  ashlar blocks, apron slabs
    ("stone_dark",    (110,  95,  70)),  # 10 mortar joints, kerbs
    ("stone_lite",    (200, 176, 136)),  # 11 facing tan faces #c8b088
    ("timber",        (122,  88,  54)),  # 12 posts, braces
    ("timber_dark",   ( 88,  62,  38)),  # 13 post skin, lintel, sill
    ("plank",         (158, 124,  80)),  # 14 door leaves
    ("plank_dark",    (128,  98,  62)),  # 15 door leaf shade
    ("sign_face",     (216, 200, 160)),  # 16 sign board #d8c8a0
    ("olive",         ( 90, 107,  47)),  # 17 olive crates #5a6b2f
    ("olive_dark",    ( 64,  78,  34)),  # 18 olive base band + corners
    ("olive_lite",    (118, 134,  66)),  # 19 olive lid
    ("slate",         ( 74,  80,  88)),  # 20 slate crates #4a5058
    ("slate_dark",    ( 52,  56,  64)),  # 21 slate base band + corners
    ("slate_lite",    (100, 106, 116)),  # 22 slate lid
    ("amber",         (168, 118,  58)),  # 23 amber crates #a8763a
    ("amber_dark",    (128,  86,  42)),  # 24 amber base band + corners
    ("amber_lite",    (198, 150,  84)),  # 25 amber lid
    ("can",           ( 58,  66,  52)),  # 26 ammo-can body
    ("can_dark",      ( 40,  46,  36)),  # 27 can latch + handle
    ("can_lite",      ( 86,  96,  76)),  # 28 can lid
    ("dark",          ( 22,  18,  14)),  # 29 doorway recess interior
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

DOOR_POINT = (27, 2, 1)
FOOTPRINT = (50, 49)
HEIGHT = 19

body = {}

OLIVE = ("olive", "olive_dark", "olive_lite")
SLATE = ("slate", "slate_dark", "slate_lite")
AMBER = ("amber", "amber_dark", "amber_lite")

GRASS3 = ("grass", "grass_dark", "moss_lite")
EARTH3 = ("earth", "earth_dark", "earth_lite")
STONE_FACE = ("stone_lite", "stone_lite", "stone")
STONE_TONES = ("stone", "stone", "stone_lite")

SCARS = ((14, 32, 4, 4), (41, 30, 4, 4), (24, 40, 5, 3))  # flanks only


def blob(x, y):
    """Low-frequency value noise 0..1 (cell 6, smoothstep interp): organic
    blobs ~6-15 voxels across; neighbours mostly share a quantized tone."""
    gx, gy = x / 6.0, y / 6.0
    x0, y0 = math.floor(gx), math.floor(gy)
    fx, fy = gx - x0, gy - y0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)

    def h(ix, iy):
        return ((ix * 73 + iy * 149) % 97) / 97.0

    lo = h(x0, y0) * (1 - sx) + h(x0 + 1, y0) * sx
    hi = h(x0, y0 + 1) * (1 - sx) + h(x0 + 1, y0 + 1) * sx
    return lo * (1 - sy) + hi * sy


def blob_tone(x, y, tones, dx=0):
    """Quantized blob: tone index from noise (dx decorrelates fields)."""
    return tones[int(blob(x + dx, y) * 2.999) % len(tones)]


def scarred(x, y, h):
    """True inside a bare-earth scar ellipse and below the crown third."""
    return h < 12 and any((x - sx) ** 2 / (rx * rx) + (y - sy) ** 2 / (ry * ry) <= 1.0
                          for sx, sy, rx, ry in SCARS)


# ------------------------------------------------------------ pad (z=0, top z=1)
E.dirt_pad(body, CI, rng, 0, 50, 0, 49)

# ------------------------------------------------------------ mound shell (hollow dome)
CX, RX = 27.5, 21.0
YF, YPEAK, YB = 10, 28, 46  # face / peak row (middle-rear) / back foot
H = 18


def ridge(x):
    nx = max(-1.0, min(1.0, (x - CX) / RX))
    return max(2, 1 + round(17 * (math.cos(nx * math.pi / 2) ** 0.8)))


def base_h(x, y):
    hx = ridge(x)
    if y <= YPEAK:
        t = 1 - 0.003 * (YPEAK - y)       # gentle brow up from the face
    else:
        u = (y - YPEAK) / float(YB - YPEAK)  # gentle tail to the back foot
        t = (1 - u) ** 0.85
    return max(1, 1 + round((hx - 1) * t))


bmap, hmap = {}, {}
for x in range(7, 49):
    for y in range(YF, YB):
        b = base_h(x, y)
        bmap[(x, y)] = b
        hmap[(x, y)] = max(1, min(H, b))  # smooth dome: no lump noise


def steep(x, y):
    b = bmap[(x, y)]
    return b - min(bmap.get((x + dx, y + dy), 1)
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 3


def grassy_cell(x, y, h):
    return (y >= 12 and not steep(x, y) and not scarred(x, y, h)
            and blob(x, y) < 0.72)


for (x, y), h in hmap.items():
    if h < 2:
        continue
    g = grassy_cell(x, y, h)
    for z in range(max(1, h - 3), h + 1):
        if z == h:
            c = blob_tone(x, y, GRASS3) if g else blob_tone(x, y, EARTH3, 40)
        else:
            c = blob_tone(x, y, EARTH3, 40)
        body[(x, y, z)] = CI[c]

# sparse 1-high grass tufts on ~5% of the grass top cells (dome reads smooth)
for (x, y), h in hmap.items():
    if h < 4 or h > 16 or (x, y, h) not in body or (x, y, h + 1) in body:
        continue
    if grassy_cell(x, y, h) and (x * 31 + y * 57) % 101 < 5:
        body[(x, y, h + 1)] = CI[blob_tone(x + 9, y, GRASS3)]

# front cut wall (2 thick, full height; doorway x23..30 left open).
# earth; grass lip is a single row set back at y=11 (no overhang past
# the y=10 face edge, so the header and sign read clean from the front).
for x in range(7, 49):
    if 23 <= x <= 30:
        continue
    top = bmap[(x, YF + 2)]
    for z in range(1, top + 1):
        for y in (10, 11):
            if z == top and y == 11:
                c = blob_tone(x, y, GRASS3)  # the single set-back lip row
            else:
                c = blob_tone(x, y, EARTH3, 40)
            body[(x, y, z)] = CI[c]

# 6 embedded cut-stone blocks poking out of the flanks (2x2, 1 proud)
for sx, sy in ((7, 22), (8, 32), (47, 22), (46, 32), (10, 40), (44, 40)):
    sh = hmap[(sx, sy)]
    E.box(body, CI, sx, sx + 2, sy, sy + 2, max(1, sh - 2), sh, "stone")
    E.box(body, CI, sx, sx + 2, sy, sy + 2, sh, sh + 1, "stone_lite")

# ------------------------------------------------------------ stone facing + header
E.stone_courses(body, CI, 7, 21, 9, 11, 1, 7, STONE_FACE)
E.stone_courses(body, CI, 33, 49, 9, 11, 1, 9, STONE_FACE)
E.stone_courses(body, CI, 21, 33, 10, 12, 14, 16, STONE_TONES)  # header
E.box(body, CI, 25, 30, 10, 12, 16, 17, "stone_lite")  # arch centre cap

# ------------------------------------------------------------ timber portal (1.8 m x 2.1 m)
for px0 in (21, 31):  # 2x2 posts with a dark outer skin
    E.box(body, CI, px0, px0 + 2, 8, 10, 1, 12, "timber")
    outer = px0 if px0 == 21 else px0 + 1
    E.box(body, CI, outer, outer + 1, 8, 10, 1, 12, "timber_dark")
E.box(body, CI, 20, 34, 8, 10, 12, 14, "timber_dark")  # thick lintel
E.knee(body, CI, 22, 9, 9, 1, 0, 3, "timber")   # left corner brace
E.knee(body, CI, 31, 9, 9, -1, 0, 3, "timber")  # right corner brace

# ------------------------------------------------------------ dark recess + double doors
E.box(body, CI, 23, 31, 12, 17, 0, 1, "dark")   # recess floor
for wx in (23, 30):                              # recess side walls
    E.box(body, CI, wx, wx + 1, 12, 17, 1, 12, "dark")
E.box(body, CI, 23, 31, 16, 17, 1, 12, "dark")  # recess back wall
E.box(body, CI, 23, 31, 12, 17, 11, 12, "dark")  # recess ceiling slab
for lx in range(23, 27):  # left leaf closed in the opening plane
    c = ("plank", "plank_dark")[(lx - 23) % 2]
    for z in range(1, 11):
        body[(lx, 11, z)] = CI["timber_dark" if z in (2, 7) else c]
for i in range(4):  # right leaf ajar, hinge (27,11) out to (30,8)
    c = ("plank", "plank_dark")[i % 2]
    for z in range(1, 11):
        cc = "timber_dark" if z in (2, 7) else c
        body[(27 + i, 11 - i, z)] = CI[cc]
        if i < 3:
            body[(28 + i, 11 - i, z)] = CI[cc]

# ------------------------------------------------------------ slab apron + kerbs + sill
for x in range(23, 32):
    for y in range(3, 9):
        if x % 3 == 0 or y % 2 == 0:
            body[(x, y, 0)] = CI["stone_dark"]  # seam grid (flush)
        else:
            body[(x, y, 0)] = CI[("stone", "stone_lite")[(x // 2 + y // 2) % 2]]
E.box(body, CI, 21, 22, 3, 8, 1, 2, "stone_dark")  # left kerb
E.box(body, CI, 32, 33, 3, 8, 1, 2, "stone_dark")  # right kerb
E.box(body, CI, 23, 31, 11, 12, 1, 2, "timber_dark")  # sill beam

# ------------------------------------------------------------ sign (10x5, flush on stone)
E.box(body, CI, 34, 44, 10, 11, 6, 11, "timber_dark")  # dark border
E.box(body, CI, 35, 43, 10, 11, 7, 10, "sign_face")    # light board
for tz in (8, 9):  # 2 rows of dark dashes (not lettering)
    for tx in range(35, 43):
        if tx % 2 == 0:
            body[(tx, 10, tz)] = CI["timber_dark"]

# ------------------------------------------------------------ big hero crate stacks
E.hero_crate(body, CI, 2, 3, 1, 5, 4, 4, OLIVE)    # left bases (clear portal)
E.hero_crate(body, CI, 7, 3, 1, 5, 4, 4, SLATE)
E.hero_crate(body, CI, 12, 3, 1, 5, 4, 4, AMBER)
E.hero_crate(body, CI, 2, 3, 5, 5, 4, 3, SLATE)    # left layer 2
E.hero_crate(body, CI, 7, 3, 5, 5, 4, 3, OLIVE)
E.hero_crate(body, CI, 4, 3, 8, 4, 4, 3, AMBER)    # left topper
E.hero_crate(body, CI, 36, 3, 1, 5, 4, 4, AMBER)   # right bases (tan/olive)
E.hero_crate(body, CI, 41, 3, 1, 5, 4, 4, OLIVE)
E.hero_crate(body, CI, 36, 3, 5, 5, 4, 3, OLIVE)   # right layer 2
E.hero_crate(body, CI, 41, 3, 5, 5, 4, 3, AMBER)
E.hero_crate(body, CI, 38, 3, 8, 4, 4, 2, SLATE)   # right topper (low)

# ------------------------------------------------------------ ammo cans
E.ammo_can(body, CI, 19, 4, 1)
E.ammo_can(body, CI, 33, 4, 1)
E.ammo_can(body, CI, 33, 6, 1)

assembled = dict(body)

PARTS = {"body": body, "assembled": assembled}


def write_vox(path, vox, palette=PALETTE):
    import struct
    xs = [x for x, _, _ in vox]; ys = [y for _, y, _ in vox]; zs = [z for _, _, z in vox]
    sx, sy, sz = max(xs) + 1, max(ys) + 1, max(zs) + 1
    with open(path, "wb") as f:
        f.write(b"VOX ")
        f.write(struct.pack("<i", 150))
        main_n = 4 + 24 + 4 + (4 + 12 + 4 + sx * sy * sz * 4) + 4 + (4 + 4 + 4 + len(palette) * 4)
        f.write(b"MAIN")
        f.write(struct.pack("<ii", 0, main_n))
        f.write(b"SIZE"); f.write(struct.pack("<ii", 12, 0)); f.write(struct.pack("<iii", sx, sy, sz))
        xyzi = struct.pack("<i", len(vox))
        for (x, y, z), c in vox.items():
            xyzi += struct.pack("BBBB", x, y, z, c)
        f.write(b"XYZI"); f.write(struct.pack("<ii", 4 + len(xyzi), 0)); f.write(xyzi)
        pal = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in palette)
        pal += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(palette))
        f.write(b"RGBA"); f.write(struct.pack("<ii", 1024, 0)); f.write(pal)
    print(f"wrote {path} ({len(vox)} voxels)")


if __name__ == "__main__":
    import json

    print(f"body: {len(body)} voxels, {E.n_components(body)} component(s)")
    print(f"assembled: {len(assembled)} voxels")
    print(f"DOOR_POINT={DOOR_POINT} FOOTPRINT={FOOTPRINT} HEIGHT={HEIGHT}")
    (bb0, bb1) = E.bbox(assembled)
    print(f"assembled bbox: {bb0}..{bb1}")
    if "--viewer-json" in sys.argv:
        print(json.dumps({
            "parts": {
                "body": {"voxels": len(body), "pivot": None},
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
        write_vox(os.path.join(out, "encamp_ammo_dump_v1_body.vox"), body)
