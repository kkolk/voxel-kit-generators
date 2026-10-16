#!/usr/bin/env python3
"""encamp_field_kitchen_v1.py — Strike Bay encampment TIMBER set piece: FIELD KITCHEN.

Landmark map (file coords, z-up, 1 voxel = 0.15 m; origin = pad footprint
min corner at ground level = pad top z=1):
  frame:   x = left/right (left = min x viewed from the front),
           y = depth (FRONT = file -y, min y), z = up.
  front:   open-sided sloped fly (front eave z13~2.0 m, beam z14; back
           beam z17~2.55 m) on 3 short + 3 tall light-timber 1x1 posts;
           3 hanging pots/pans + 2 glowing lanterns under the front beam.
           NO flag in the concept: no FLAG_PIVOT, no flag part.
  fly:     olive-only canvas sheet x8..37, y14..36 (ends AT the front
           posts, no front overhang), sloping 14 (front) to 18 (back)
           with 1-voxel between-post sag; flat per-panel tones
           (#5f6b3a / #545f33 / #6b7842) with darker seams running ONE
           way only (front-to-back, every 5), 2 large darker camo
           patches, dark hem band round the edges; light-timber purlins
           run underneath the sheet and land on the beams; sloped
           light-timber side plates (line6 staircases) tie front to back
           beams; slope steps are bridged from BELOW so no bars sit on
           the canvas.
  posts:   front row y14 (x10/22/34, z1..14), back row y34 (x10/22/34,
           z1..17); dark beams along x at y14 z14 and y34 z17; knee braces
           on the back row + sides only (front stays open so the game
           camera sees the stove and table).
  stove:   big dark-iron range x13..23, y19..24, z1..8 (~1.6x0.9x1.0 m,
           charcoal #3a3d40/#4a4e52 flat per-course tones, lighter top
           plate): 2 oven doors on the FRONT face (dark plates + light
           handles), bright firebox slot 3x1 #ff8a30 facing front with an
           ember bed below, 2 stew pots with lids on top; tall black 2x2
           stovepipe x16..18, y20..22, z8..27 rising THROUGH the canvas
           (iron collar ties the sheet in); shrinking light-grey smoke
           puffs z28..33 drifting up-back are the separate `smoke` part.
  wood:    split-log pile x4..11, y17..20, z1..4 front-left beside the
           stove (~1.2x0.6x0.6 m, brown stack, tan end-grain front face
           with dark stacking seams, dark top logs).
  table:   prep table x25..33, y10..14 (ahead of the front posts, fully
           outside the fly): pale-wood top #c9a46a z6, 4 legs, lower
           shelf with a stores box; white paper #e8e4d8 3x2 + plate 2x2.
  bench:   wooden bench x25..31, y6..7 (front edge 8 voxels ahead of the
           front posts, outside the fly, as in the concept), seat z3..4.
  hang:    from the front beam (y14, z14): 2 dark-grey stew pots 2x2x2
           with lids + 1 flat pan 3x3x1 on 1-voxel hooks, and 2 warm
           lanterns (dark caps z13, glow cores z11..12 #ffc860) between.
  crates:  hero boxes (>=4x3x3, dark base band + light lid + dark corners)
           in olive / slate / amber: 2-high stacks along the back edge
           (x12..16, x18..22 at y35..37) + a 3-high hero stack at the
           right edge (x36..40, y26..29) + a small 3-high stack of 2x2x2
           boxes back-left beside the stove (x9..10, y28..29); 3 olive
           3x2x3 ammo cans with dark lid bands by the back posts plus a
           row of 2 cans (y31) and an olive 2x3x4 water jerrycan with a
           dark cap at the right side.
Constants:
  DOOR_POINT = (27, 3, 1) -- soldiers step out here (pad front-centre,
           in front of the bench, clear of the fly posts)
  FOOTPRINT  = (45, 40)   -- pad bbox in voxels (6.75 x 6.0 m)
  HEIGHT     = 27          -- stovepipe top voxel z=26
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import encamp_timber as E

rng = random.Random(673)

BASE_PALETTE = [  # (name, rgb); color index = position + 1
    ("dirt",          (150, 110,  72)),  # 1  pad dirt
    ("dirt_dark",     (118,  84,  54)),  # 2  pad speckle
    ("grass",         (107, 132,  62)),  # 3  pad border
    ("grass_dark",    ( 82, 104,  48)),  # 4  pad border shade
    ("timber",        (122,  88,  54)),  # 5  posts, braces, purlins
    ("timber_dark",   ( 88,  62,  38)),  # 6  beams, seams
    ("plank",         (158, 124,  80)),  # 7  table, bench
    ("plank_dark",    (128,  98,  62)),  # 8  wood shade
    ("olive",         ( 90, 107,  47)),  # 9  crates (#5a6b2f)
    ("olive_dark",    ( 64,  78,  34)),  # 10 crate bands/corners
    ("olive_lite",    (118, 134,  66)),  # 11 crate lids
    ("slate",         ( 74,  80,  88)),  # 12 slate crates (#4a5058)
    ("slate_dark",    ( 52,  56,  64)),  # 13 slate bands, ammo shade
    ("slate_lite",    ( 93, 100, 108)),  # 14 slate lids
    ("amber",         (168, 118,  58)),  # 15 amber crates (#a8763a)
    ("amber_dark",    (128,  86,  42)),  # 16 amber bands
    ("amber_lite",    (198, 150,  84)),  # 17 amber lids
    ("canvas",        ( 95, 107,  58)),  # 18 fly panel A (#5f6b3a)
    ("canvas_mid",    ( 84,  95,  51)),  # 19 fly panel B (#545f33)
    ("canvas_lite",   (107, 120,  66)),  # 20 fly panel C (#6b7842)
    ("canvas_seam",   ( 62,  70,  38)),  # 21 fly seams + hem band
    ("patch_dark",    ( 58,  68,  34)),  # 22 large darker camo patches
    ("iron",          ( 58,  61,  64)),  # 23 stove body (#3a3d40)
    ("iron_lite",     ( 74,  78,  82)),  # 24 stove courses/top (#4a4e52)
    ("iron_dark",     ( 36,  38,  40)),  # 25 oven doors, pots, pipe
    ("firebox",       (255, 138,  48)),  # 26 glowing slot (#ff8a30)
    ("ember",         (196,  88,  28)),  # 27 ember bed
    ("lamp_glow",     (255, 200,  96)),  # 28 lantern core (#ffc860)
    ("lamp_frame",    ( 60,  50,  36)),  # 29 lantern cap
    ("paper",         (232, 228, 216)),  # 30 paper / plate (#e8e4d8)
    ("pale_wood",     (201, 164, 106)),  # 31 pale table top (#c9a46a)
    ("log_end",       (210, 180, 130)),  # 32 firewood end grain
    ("smoke",         (200, 200, 200)),  # 33 smoke puff (#c8c8c8)
    ("smoke_lite",    (224, 224, 224)),  # 34 smoke fade (#e0e0e0)
]
CI = {name: i + 1 for i, (name, _) in enumerate(BASE_PALETTE)}
DOOR_POINT = (27, 3, 1)
FOOTPRINT = (45, 40)
HEIGHT = 27

body = {}
smoke = {}

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
E.dirt_pad(body, CI, rng, 0, 45, 0, 36)
for _p in [p for p in body if p[2] == 0]:  # bitten-edge singletons
    _x, _y, _z = _p
    if not any(q in body for q in ((_x + 1, _y, _z), (_x - 1, _y, _z),
                                   (_x, _y + 1, _z), (_x, _y - 1, _z))):
        del body[_p]

# ------------------------------------------------------------ posts: short front, tall back
POST_XS = (10, 22, 34)
for px in POST_XS:
    E.box(body, CI, px, px + 1, 8, 9, 1, 14, "timber")    # front, ~2.0 m
    E.box(body, CI, px, px + 1, 28, 29, 1, 17, "timber")  # back, ~2.4 m

# ------------------------------------------------------------ beams + sloped side plates
E.box(body, CI, 10, 35, 8, 9, 14, 15, "timber_dark")    # front beam (low)
E.box(body, CI, 10, 35, 28, 29, 17, 18, "timber_dark")  # back beam (high)
E.line6(body, CI, (10, 8, 13), (10, 28, 16), color="timber")
E.line6(body, CI, (34, 8, 13), (34, 28, 16), color="timber")
E.box(body, CI, 10, 11, 28, 29, 17, 18, "timber")  # risers to the back beam
E.box(body, CI, 34, 35, 28, 29, 17, 18, "timber")
# knee braces: back row + sides only, front stays open for the camera
for px in POST_XS:
    E.knee(body, CI, px - 1 if px > 10 else px + 1, 28, 13,
           -1 if px > 10 else 1, 0, 4)
    E.knee(body, CI, px, 27, 13, 0, -1, 4)
E.knee(body, CI, 10, 9, 11, 0, 1, 4)
E.knee(body, CI, 10, 27, 13, 0, -1, 4)
E.knee(body, CI, 34, 9, 11, 0, 1, 4)
E.knee(body, CI, 34, 27, 13, 0, -1, 4)

# ------------------------------------------------------------ sloped olive canvas fly (13 front -> 18 back)
FLY_X0, FLY_X1, FLY_Y0, FLY_Y1 = 8, 37, 8, 30


def fly_z(x, y):
    return 14 + (y - 8) * 4 // 20


E.canvas_fly(body, CI, FLY_X0, FLY_X1, FLY_Y0, FLY_Y1, fly_z,
             ("canvas", "canvas_mid", "canvas_lite"),
             seam="canvas_seam", sag=1, panel=5)

_CX, _CY, _HX, _HY = 22.0, 18.5, 14.5, 11.0
_PATCHES = ((28, 22, 5), (13, 13, 4))


def _sheet_z(x, y):
    sag_here = 1 - int(min(1.0, ((x - _CX) / _HX) ** 2 + ((y - _CY) / _HY) ** 2))
    return fly_z(x, y) - sag_here


_TONES = ("canvas", "canvas_mid", "canvas_lite")
for _x in range(FLY_X0, FLY_X1):  # hem band + large darker camo patches
    for _y in range(FLY_Y0, FLY_Y1):
        _z = _sheet_z(_x, _y)
        if _x in (FLY_X0, FLY_X1 - 1) or _y in (FLY_Y0, FLY_Y1 - 1):
            body[(_x, _y, _z)] = CI["canvas_seam"]
        elif any((_x - _px) ** 2 + (_y - _py) ** 2 <= _pr ** 2
                 for _px, _py, _pr in _PATCHES):
            body[(_x, _y, _z)] = CI["patch_dark"]
        elif _y == (FLY_Y0 + FLY_Y1) // 2:  # undo canvas_fly's cross seam:
            body[(_x, _y, _z)] = CI[_TONES[((_x - FLY_X0) // 5) % 3]]
for _y in range(FLY_Y0 + 1, FLY_Y1):  # bridge slope steps from BELOW so no
    if fly_z(0, _y) != fly_z(0, _y - 1):  # bars sit on the canvas
        for _x in range(FLY_X0, FLY_X1):
            _zh = _sheet_z(_x, _y)
            if (_x, _y, _zh - 1) not in body:
                body[(_x, _y, _zh - 1)] = CI["canvas_seam"]
for _rx in (12, 22, 32):  # light-timber purlins under the sheet
    _zp = None
    for _y in range(FLY_Y0, FLY_Y1):
        _z = _sheet_z(_rx, _y) - 1
        body[(_rx, _y, _z)] = CI["timber"]
        if _zp is not None and _z == _zp + 1:
            body[(_rx, _y, _zp)] = CI["timber"]  # fill below the step riser
        _zp = _z
for _x in range(10, 35, 4):  # stitch tabs tying the sheet to the front beam
    body[(_x, 8, 13)] = CI["timber_dark"]
    # (no back tabs: the sagging sheet lands on the back beam directly,
    # and tabs there poke through the canvas)

# ------------------------------------------------------------ stove (x13..23, y13..18, z1..8)
for z in range(1, 7):  # flat per-course charcoal tones
    c = "iron_dark" if z == 1 else ("iron_lite" if z % 2 == 0 else "iron")
    E.box(body, CI, 13, 24, 13, 19, z, z + 1, c)
E.box(body, CI, 13, 24, 13, 19, 7, 8, "iron_lite")  # lighter top plate
# 2 oven doors on the FRONT face (y=13): dark plates + light handles
for dx in (14, 19):
    E.box(body, CI, dx, dx + 3, 13, 14, 3, 6, "iron_dark")
    E.box(body, CI, dx + 1, dx + 2, 13, 14, 4, 5, "iron_lite")  # handle
# bright firebox slot facing front + ember bed below
E.box(body, CI, 17, 20, 13, 14, 2, 3, "firebox")
E.box(body, CI, 16, 21, 13, 14, 1, 2, "ember")
# 2 stew pots with lids on top
for px in (14, 19):
    E.box(body, CI, px, px + 2, 15, 17, 8, 10, "iron_dark")
    E.box(body, CI, px, px + 2, 15, 17, 10, 11, "iron_lite")  # lid
# tall black stovepipe through the canvas
E.box(body, CI, 16, 18, 14, 16, 8, 27, "iron_dark")
E.box(body, CI, 16, 18, 14, 16, 26, 27, "iron")  # rim band
for dx in range(15, 19):  # iron collar where the pipe pierces the fly
    for dy in range(13, 17):
        if (dx, dy, 14) not in body and (dx, dy, 15) not in body:
            body[(dx, dy, 14)] = CI["iron_dark"]

# ------------------------------------------------------------ smoke: 3 shrinking puffs, up and back
E.box(smoke, CI, 15, 18, 14, 17, 28, 30, "smoke")          # 3x3 puff
E.box(smoke, CI, 16, 18, 15, 17, 30, 32, "smoke")          # 2x2, offset back
E.box(smoke, CI, 16, 18, 16, 18, 32, 34, "smoke_lite")     # 2x2, fade

# ------------------------------------------------------------ firewood pile (x4..11, y11..14, z1..4)
E.box(body, CI, 4, 12, 11, 15, 1, 4, "timber")
for x in range(4, 12):  # tan end-grain front face, dark stacking seams
    for z in range(1, 4):
        if ((x - 4) // 2 + z) % 2 == 0:
            body[(x, 11, z)] = CI["log_end"]
        else:
            body[(x, 11, z)] = CI["timber_dark"]
E.box(body, CI, 4, 12, 11, 15, 4, 5, "timber_dark")  # top logs
E.box(body, CI, 5, 7, 12, 14, 4, 5, "log_end")
E.box(body, CI, 9, 11, 12, 14, 4, 5, "log_end")
# ------------------------------------------------------------ hanging pots/pans + lanterns (front beam y8, z14)
def hang_pot(x, big=True):
    E.box(body, CI, x, x + 1, 8, 9, 12, 14, "iron_dark")  # hook
    if big:
        E.box(body, CI, x - 1, x + 1, 7, 9, 10, 12, "iron_dark")  # pot
        E.box(body, CI, x - 1, x + 1, 7, 9, 12, 13, "iron")  # lid band
    else:
        E.box(body, CI, x - 1, x + 2, 7, 10, 10, 11, "iron_dark")  # pan
        E.box(body, CI, x, x + 1, 8, 9, 11, 12, "iron_dark")  # handle stub


def hang_lamp(x):
    E.box(body, CI, x, x + 2, 8, 9, 13, 14, "lamp_frame")  # cap
    E.box(body, CI, x, x + 2, 8, 9, 11, 13, "lamp_glow")  # warm core


hang_pot(16)
hang_lamp(20)
hang_pot(24, big=False)
hang_lamp(27)
hang_pot(30)

# ------------------------------------------------------------ hero crate stacks (back + right edges)
crate(12, 29, 1, 5, 3, 4, OLIVE)
crate(12, 29, 5, 5, 3, 3, SLATE)
crate(18, 29, 1, 5, 3, 4, AMBER)
crate(18, 29, 5, 5, 3, 3, OLIVE)
crate(36, 20, 1, 5, 4, 4, AMBER)   # right-edge hero stack, 3 high
crate(36, 20, 5, 5, 4, 3, OLIVE)
crate(36, 20, 8, 5, 4, 3, SLATE)
# olive ammo cans by the back posts, 1-voxel gaps
ammo_can(25, 29, 1)
ammo_can(29, 29, 1)
ammo_can(33, 29, 1)
# small 2x2x2 boxes, 3 high, back-left beside the stove
def small_box(x, y, z, base, dark, lite):
    E.box(body, CI, x, x + 2, y, y + 2, z, z + 2, base)
    E.box(body, CI, x, x + 2, y, y + 2, z, z + 1, dark)  # base band
    E.box(body, CI, x, x + 2, y, y + 2, z + 1, z + 2, lite)  # lid
small_box(9, 22, 1, "olive", "olive_dark", "olive_lite")
small_box(9, 22, 3, "slate", "slate_dark", "slate_lite")
small_box(9, 22, 5, "amber", "amber_dark", "amber_lite")
# right side: row of 2 cans + olive water jerrycan 2x3x4 with a dark cap
ammo_can(30, 25, 1)
ammo_can(34, 25, 1)
E.box(body, CI, 38, 40, 25, 28, 1, 5, "olive")
E.box(body, CI, 38, 40, 25, 28, 4, 5, "olive_dark")  # cap band
E.box(body, CI, 38, 39, 26, 27, 5, 6, "olive_dark")  # cap

# ------------------------------------------------------------ shift the structure +6y so the
# bench/table zone fits in front: bench front edge y6 (8 voxels ahead of
# the y14 post line), table y10..14 just ahead of the posts, door y3 on
# a 4-voxel front margin. Table + bench are rebuilt below at absolute
# coords AFTER the shift; the pad is redrawn for the new extent.
DY = 6
body = {(x, y + DY, z): v for (x, y, z), v in body.items()}
smoke = {(x, y + DY, z): v for (x, y, z), v in smoke.items()}
# delete the shifted old table (x25..33, y21..26, z1..8) and bench
# (x25..31, y17..18, z1..4): nothing else lives in those rects
for _p in [p for p in body
           if 25 <= p[0] <= 33 and 21 <= p[1] <= 26 and 1 <= p[2] <= 8]:
    del body[_p]
for _p in [p for p in body
           if 25 <= p[0] <= 31 and 17 <= p[1] <= 18 and 1 <= p[2] <= 4]:
    del body[_p]
# redraw the pad for the new extent (x0..44, y2..41: 4-5 margin everywhere)
body = {p: v for p, v in body.items() if p[2] != 0}
E.dirt_pad(body, CI, rng, 0, 45, 2, 42)
for _p in [p for p in body if p[2] == 0]:  # bitten-edge singletons
    _x, _y, _z = _p
    if not any(q in body for q in ((_x + 1, _y, _z), (_x - 1, _y, _z),
                                   (_x, _y + 1, _z), (_x, _y - 1, _z))):
        del body[_p]

# ------------------------------------------------------------ prep table (x25..33, y10..14, top z6)
for lx in (25, 32):
    for ly in (10, 13):
        E.box(body, CI, lx, lx + 1, ly, ly + 1, 1, 6, "plank_dark")
E.box(body, CI, 25, 34, 10, 15, 6, 7, "pale_wood")  # pale top
for x in range(25, 34):  # darker board gaps across the top
    if x % 3 == 2:
        body[(x, 10, 6)] = CI["plank_dark"]
        body[(x, 14, 6)] = CI["plank_dark"]
E.box(body, CI, 26, 33, 11, 14, 3, 4, "plank_dark")  # lower shelf
E.box(body, CI, 27, 30, 11, 13, 4, 6, "amber")  # shelf stores box
# white paper + plate on top
E.box(body, CI, 27, 30, 11, 13, 7, 8, "paper")
E.box(body, CI, 31, 33, 11, 13, 7, 8, "paper")

# ------------------------------------------------------------ bench (x25..31, y6..7, seat z3..4)
E.box(body, CI, 25, 32, 6, 8, 3, 4, "plank")
for lx in (25, 30):
    E.box(body, CI, lx, lx + 1, 6, 8, 1, 3, "plank_dark")

assembled = dict(body)
assembled.update(smoke)

PALETTE = BASE_PALETTE

PARTS = {"body": body, "smoke": smoke, "assembled": assembled}


def write_vox(path, vox, palette=None):
    import struct
    pal = palette or BASE_PALETTE
    # Shared encampment frame (every other encamp_*_v1 writer): file coords
    # are design coords shifted so min x/y land on 0, z-up raw (the game
    # reader assumes z-up; the old (x, z, y) Magica y-up swap mirrored the
    # piece against its landmark constants).
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    xoff, yoff = -min(xs), -min(ys)
    sx, sy, sz = max(xs) + xoff + 1, max(ys) + yoff + 1, max(zs) + 1
    xyzi = bytearray()
    for (x, y, z), ci in sorted(vox.items()):
        xyzi += struct.pack("BBBB", x + xoff, y + yoff, z, ci)
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
    print(f"smoke: {len(smoke)} voxels, {E.n_components(smoke)} component(s)")
    print(f"DOOR_POINT={DOOR_POINT} FOOTPRINT={FOOTPRINT} HEIGHT={HEIGHT}")
    (bb0, bb1) = E.bbox(assembled)
    print(f"assembled bbox: {bb0}..{bb1}")
    if "--viewer-json" in sys.argv:
        print(json.dumps({
            "parts": {
                "body": {"voxels": len(body), "pivot": None},
                "smoke": {"voxels": len(smoke), "pivot": None},
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
        write_vox(os.path.join(out, "encamp_field_kitchen_v1_body.vox"), body)
        write_vox(os.path.join(out, "encamp_field_kitchen_v1_smoke.vox"), smoke)
