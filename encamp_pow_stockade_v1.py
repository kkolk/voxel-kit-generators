#!/usr/bin/env python3
"""encamp_pow_stockade_v1.py — Strike Bay encampment TIMBER set piece: POW STOCKADE (#682).

Square prisoner pen of rough timber posts strung with barbed wire, inward-
leaning wire overhang, wide double gate (own part), corner guard tower with
ladder and roof, lean-to shelter of planks and canvas, straw mats, water
bucket, trampled-mud pad with grass fringe.

Landmark map (file coords, z-up, 1 voxel = 0.15 m; origin = pad min corner
at ground level):
  frame:   x = left/right (left = min x viewed from the front),
           y = depth (FRONT = file -y, min y), z = up.
  front:   pen front wall at y=10 with the gate opening x20..27.
           back: pen back wall at y=41.
  pad:     x0..47, y0..47, z=0 (7.2 x 7.2 m): dirt interior with dark
           trample blotches inside the pen, grass fringe, nibbled edge.
           posts z1..13 (top jitter 13..14, mixed timber tones), 2x2
           corners, 2x2 gate jambs at x18..19 / x28..29 (z1..15).
  wire:    3 near-black steel barbed strands per wall at z3/7/11 (front
           split at gate): open faces so the dirt shows through.
  overhang: slanted timber outrigger arm at every wall post from
           (px,py,12) leaning 3 inward up to z14 + 2 iron ring strands
           per wall (front split).
  tower:   back-right, legs 2x2 at x32..37 / y34..39 z1..17 with X-braces;
           plank deck x31..38 y33..40 z17 (walk z18 = 2.7 m); railing
           z18..21 with ladder gap on the west face; roof posts z22..25,
           plank slab x30..39 y32..41 z26 + dark fascia (top 4.05 m).
  ladder:  west face x=30, rails y35/37 z1..18, rungs every 2 z.
  lean-to: x10..20, y34..40: front posts y34 z1..8 + beam, purlin y36
           z8..10, back beam y40 z11; plank roof y34..36, olive canvas fly
           y37..40, canvas drape on the east end x20 z1..7.
  mats:    3 straw mats (5x4 at (22,18), 4x3 at (29,24) + (14,22)), z1
           with dark edges; water bucket 2x2 at (27,30) z1..3 + dark rim.
  trough:  timber water trough x33..37, y12..14 (walls z1..2, water z2).
  firepit: scorched 3x3 at x22..24, y27..29: charred rim, ash bed, billets.
  gate:    (own part, authored closed at y=10) light-tan leaves x20..23 /
           x24..27: stiles z1..16 + dark caps, rails z3/13, iron infill,
           X-brace per leaf, locking bar z8 + padlock (23,10,7); risers on
           both jambs + header crossbar z17 + dark cap (portal top z18).

Constants:
  DOOR_POINT = (24, 5, 1)    -- pad outside the gate: prisoners gather here
  PEN_MIN    = (9, 11, 1)    -- interior floor rect min (prisoners stand)
  PEN_MAX    = (38, 40, 1)   -- interior floor rect max
  GATE_HINGE = (19, 10, 6)   -- right face of the left jamb, mid height
  FOOTPRINT  = (48, 48)      -- pad bbox in voxels (7.2 x 7.2 m)
  HEIGHT     = 27            -- tower roof top voxel z=26
Parts:
  body -- everything static incl. pad (ONE 6-connected component)
  gate -- double gate leaves (own part: the game breaks it separately)
  assembled -- body + gate (rendering)
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import encamp_timber as E

rng = random.Random(682)

PALETTE = [  # (name, rgb); color index = position + 1
    ("mud",           (138, 104,  70)),  # 1  trampled pad interior
    ("mud_dark",      (110,  82,  55)),  # 2  trample blotches, speckle
    ("grass",         (107, 132,  62)),  # 3  pad fringe
    ("grass_dark",    ( 82, 104,  48)),  # 4  fringe shade, tufts
    ("timber",        (122,  88,  54)),  # 5  posts, beams, braces
    ("timber_dark",   ( 88,  62,  38)),  # 6  jambs, seams, fascia, rails
    ("timber_grey",   (128, 110,  86)),  # 7  weathered grey-brown posts
    ("plank",         (158, 124,  80)),  # 8  deck, roof, lean-to roof
    ("plank_dark",    (128,  98,  62)),  # 9  plank shade, nosing
    ("wire",          (150, 154, 158)),  # 10 galvanised wire strands, mesh
    ("wire_dark",     (106, 110, 114)),  # 11 barbs, mesh shade
    ("canvas",        ( 96, 102,  52)),  # 12 olive canvas fly + drape
    ("canvas_dark",   ( 70,  76,  38)),  # 13 canvas seams, hem
    ("straw",         (196, 170, 110)),  # 14 sleeping mats
    ("straw_dark",    (160, 134,  86)),  # 15 mat edges
    ("bucket",        ( 74,  80,  88)),  # 16 water bucket body
    ("bucket_dark",   ( 52,  56,  64)),  # 17 bucket rim
    ("water",         ( 96, 116, 124)),  # 18 trough water (muted slate-blue)
    ("wire_iron",     ( 52,  56,  60)),  # 19 near-black steel strands, mesh
    ("plank_light",   (200, 164, 106)),  # 20 light tan gate frame #c8a46a
]

CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

DOOR_POINT = (24, 5, 1)
PEN_MIN = (9, 11, 1)
PEN_MAX = (38, 40, 1)
GATE_HINGE = (19, 10, 6)
FOOTPRINT = (48, 48)
HEIGHT = 27

body = {}
gate = {}

POST_TONES = ["timber", "timber", "timber_dark", "timber_grey"]


def post(x, y, jamb=False):
    """1x1 rough post (2x2 at corners/jambs): base z1, weathered tone, top
    jitter 13..14 (jambs 2x2, z1..15, dark)."""
    tone = POST_TONES[rng.randrange(len(POST_TONES))]
    if jamb:
        E.box(body, CI, x, x + 2, y, y + 2, 1, 15, "timber_dark")
        body[(x, y, 15)] = CI["timber"]
    else:
        top = 13 + rng.randrange(2)
        E.box(body, CI, x, x + 1, y, y + 1, 1, top, tone)


# ------------------------------------------------------------ pad (z=0) + trample + tufts
E.dirt_pad(body, CI, rng, 0, 47, 0, 47,
           dirt="mud", dirt_dark="mud_dark",
           grass="grass", grass_dark="grass_dark")
for _ in range(140):  # trampled-mud blotches inside the pen
    x, y = rng.randrange(9, 39), rng.randrange(11, 41)
    if (x, y, 0) in body and rng.random() < 0.6:
        body[(x, y, 0)] = CI["mud_dark"]
for (tx, ty) in ((2, 4), (45, 3), (3, 44), (44, 45), (22, 2), (36, 45),
                 (5, 20), (45, 24), (14, 45), (30, 2)):
    for dx, dy in ((0, 0), (1, 0), (0, 1)):
        if rng.random() < 0.8:
            body[(tx + dx, ty + dy, 1)] = CI["grass"]
            if rng.random() < 0.4:
                body[(tx + dx, ty + dy, 2)] = CI["grass_dark"]

# ------------------------------------------------------------ pen posts
FRONT_Y, BACK_Y, LEFT_X, RIGHT_X = 10, 41, 8, 39
for cx, cy in ((8, 10), (39, 10), (8, 41), (39, 41)):  # 2x2 corners
    E.box(body, CI, cx, cx + 2, cy, cy + 2, 1, 14, "timber_dark")
for px in (12, 16, 32, 36):
    post(px, FRONT_Y)
post(18, 9, jamb=True)   # gate jambs (2x2, face the opening)
post(28, 9, jamb=True)
for px in (12, 16, 20, 24, 28, 32, 36):
    post(px, BACK_Y)
for py in (14, 18, 22, 26, 30, 34, 38):
    post(LEFT_X, py)
    post(RIGHT_X, py)

# ------------------------------------------------------------ barbed strands (3x near-black steel)
for z in (3, 7, 11):
    E.barbed_run_x(body, CI, 8, 19, FRONT_Y, z, wire="wire_iron",   # front,
                   barb="wire_dark", every=5)                      # split gate
    E.barbed_run_x(body, CI, 29, 40, FRONT_Y, z, wire="wire_iron",
                   barb="wire_dark", every=5)
    E.barbed_run_x(body, CI, 8, 40, BACK_Y, z, wire="wire_iron",
                   barb="wire_dark", every=5)
    E.barbed_run_y(body, CI, 10, 42, LEFT_X, z, wire="wire_iron",
                   barb="wire_dark", every=5)
    E.barbed_run_y(body, CI, 10, 42, RIGHT_X, z, wire="wire_iron",
                   barb="wire_dark", every=5)

# ------------------------------------------------------------ slanted barbed outriggers
POSTS = ([(x, FRONT_Y, 0, 1) for x in (8, 12, 16, 32, 36, 39)]
         + [(x, BACK_Y, 0, -1) for x in (8, 12, 16, 20, 24, 28, 32, 36, 39)]
         + [(LEFT_X, y, 1, 0) for y in (10, 14, 18, 22, 26, 30, 34, 38, 41)]
         + [(RIGHT_X, y, -1, 0) for y in (10, 14, 18, 22, 26, 30, 34, 38, 41)])
for (px, py, dx, dy) in POSTS:  # arm slants 3 inward, up to z14
    E.line6(body, CI, (px, py, 12), (px + dx * 3, py + dy * 3, 14),
            "timber_dark")
for z, off in ((14, 3), (13, 2)):  # 2 barbed ring strands on the arms
    E.barbed_run_x(body, CI, 8, 19, FRONT_Y + off, z, wire="wire_iron",
                   barb="wire_dark", every=5)
    E.barbed_run_x(body, CI, 29, 40, FRONT_Y + off, z, wire="wire_iron",
                   barb="wire_dark", every=5)
    E.barbed_run_x(body, CI, 8, 40, BACK_Y - off, z, wire="wire_iron",
                   barb="wire_dark", every=5)
    E.barbed_run_y(body, CI, 10, 42, LEFT_X + off, z, wire="wire_iron",
                   barb="wire_dark", every=5)
    E.barbed_run_y(body, CI, 10, 42, RIGHT_X - off, z, wire="wire_iron",
                   barb="wire_dark", every=5)

# ------------------------------------------------------------ guard tower (back-right)
for lx in (32, 36):
    for ly in (34, 38):
        E.box(body, CI, lx, lx + 2, ly, ly + 2, 1, 17, "timber")
E.line6(body, CI, (32, 34, 2), (32, 39, 16), "timber_dark")   # X-braces
E.line6(body, CI, (32, 39, 2), (32, 34, 16), "timber_dark")
E.line6(body, CI, (37, 34, 2), (37, 39, 16), "timber_dark")
E.line6(body, CI, (37, 39, 2), (37, 34, 16), "timber_dark")
E.beam_x(body, CI, 31, 39, 34, 16, "timber_dark")             # deck bearers
E.beam_x(body, CI, 31, 39, 38, 16, "timber_dark")
E.plank_floor(body, CI, 31, 39, 33, 40, 17)                  # deck, walk z18
for x in range(31, 39):                                      # fascia rim
    body[(x, 33, 17)] = CI["timber_dark"]
    body[(x, 39, 17)] = CI["timber_dark"]
for y in range(33, 40):
    body[(31, y, 17)] = CI["timber_dark"]
    body[(38, y, 17)] = CI["timber_dark"]
for rx, ry in ((31, 33), (38, 33), (31, 40), (38, 40),
               (34, 33), (34, 40), (31, 36), (38, 36)):      # railing posts
    E.box(body, CI, rx, rx + 1, ry, ry + 1, 18, 22, "timber_dark")
for z in (19, 21):                                           # railing rails
    E.box(body, CI, 31, 39, 33, 34, z, z + 1, "timber")      # front rail
    E.box(body, CI, 31, 39, 40, 41, z, z + 1, "timber")      # back rail
    E.box(body, CI, 38, 39, 33, 41, z, z + 1, "timber")      # east rail
    E.box(body, CI, 31, 32, 33, 35, z, z + 1, "timber")      # west stubs
    E.box(body, CI, 31, 32, 38, 41, z, z + 1, "timber")      # (ladder gap)
for rx, ry in ((31, 33), (38, 33), (31, 40), (38, 40)):      # roof posts
    E.box(body, CI, rx, rx + 1, ry, ry + 1, 22, 26, "timber")
for x in range(30, 40):                                      # plank slab z26
    tone = ("plank", "plank_dark", "timber_grey")[(x // 2) % 3]
    for y in range(32, 41):
        rim = x in (30, 39) or y in (32, 40)
        body[(x, y, 26)] = CI["timber_dark"] if rim else CI[tone]
for z in range(1, 19):                                       # ladder rails
    for y in (35, 37):
        body[(30, y, z)] = CI["timber_dark"]
for z in range(2, 17, 2):                                    # ladder rungs
    body[(30, 36, z)] = CI["plank"]

# ------------------------------------------------------------ lean-to (planks + canvas)
for px in (10, 15, 20):
    E.pole(body, CI, px, 34, 1, 8, "timber")
E.beam_x(body, CI, 10, 21, 34, 8, "timber_dark")              # front beam
E.box(body, CI, 10, 21, 36, 37, 8, 10, "timber_dark")        # purlin
E.beam_x(body, CI, 10, 21, 40, 11, "timber_dark")             # back beam
for y in (34, 35, 36):                                       # plank roof slope
    z = 8 + (y - 34) * 3 // 6
    for x in range(10, 21):
        body[(x, y, z)] = CI["plank" if x % 2 else "plank_dark"]
_fly = {}
E.canvas_fly(_fly, CI, 10, 21, 37, 41, lambda x, y: 9 + (y - 37),
             ["canvas", "canvas_dark"], sag=1)                # canvas slope
for (x, y, z), ci in _fly.items():                           # stepped slope:
    body[(x, y, z)] = ci                                     # tread + dark
    body[(x, y, z - 1)] = CI["canvas_dark"]                  # riser, no floats
E.canvas_panel_wall(body, CI, 20, 21, 34, 41, 1, 8,
                    ["canvas", "canvas_dark"], axis="y")      # east drape

# ------------------------------------------------------------ mats + bucket
for x in range(22, 27):
    for y in range(18, 22):
        edge = x in (22, 26) or y in (18, 21)
        body[(x, y, 1)] = CI["straw_dark"] if edge else CI["straw"]
for x in range(29, 33):
    for y in range(24, 27):
        edge = x in (29, 32) or y in (24, 26)
        body[(x, y, 1)] = CI["straw_dark"] if edge else CI["straw"]
E.box(body, CI, 27, 29, 30, 32, 1, 3, "bucket")
E.box(body, CI, 27, 29, 30, 32, 3, 4, "bucket_dark")         # rim
for x in range(14, 18):                                       # third straw mat
    for y in range(22, 25):
        edge = x in (14, 17) or y in (22, 24)
        body[(x, y, 1)] = CI["straw_dark"] if edge else CI["straw"]
E.box(body, CI, 33, 38, 12, 15, 1, 2, "timber_dark")          # trough walls
E.box(body, CI, 34, 37, 13, 14, 2, 3, "water")                # trough water
for x in range(22, 25):                                       # fire pit: dark
    for y in range(27, 30):                                   # scorched base
        body[(x, y, 1)] = CI["mud_dark"]
for x, y in ((22, 27), (24, 27), (22, 29), (24, 29)):         # charred rim
    body[(x, y, 1)] = CI["timber_dark"]
body[(23, 28, 1)] = CI["timber_grey"]                         # ash bed
E.box(body, CI, 22, 25, 28, 29, 2, 3, "timber_dark")          # fuel billets

# ------------------------------------------------------------ gate part (authored closed at y=10)
for lx0, lx1 in ((20, 23), (24, 27)):                        # two light-tan
    for sx in (lx0, lx1):                                    # leaves, stiles
        E.box(gate, CI, sx, sx + 1, 10, 11, 1, 17, "plank_light")  # z1..16
        gate[(sx, 10, 16)] = CI["timber_dark"]                # cap
    for z in (3, 13):
        E.box(gate, CI, lx0, lx1 + 1, 10, 11, z, z + 1,       # rails
              "plank_light")
    E.mesh_panel_x(gate, CI, lx0, lx1 + 1, 10, 3, 13,         # iron infill
                   wire="wire_iron", step=3)
    E.line6(gate, CI, (lx0, 10, 3), (lx1, 10, 12), "timber_dark")  # X-brace
    E.line6(gate, CI, (lx0, 10, 12), (lx1, 10, 3), "timber_dark")
E.box(gate, CI, 20, 28, 10, 11, 8, 9, "timber_dark")          # locking bar
gate[(23, 10, 7)] = CI["bucket_dark"]                        # padlock
E.box(gate, CI, 18, 20, 9, 11, 15, 17, "plank_light")        # risers on the
E.box(gate, CI, 28, 30, 9, 11, 15, 17, "plank_light")        # jambs (z15..16)
E.box(gate, CI, 18, 30, 10, 11, 17, 18, "plank_light")       # header crossbar
E.box(gate, CI, 18, 30, 10, 11, 18, 19, "timber_dark")       # header cap

assembled = dict(body)
assembled.update(gate)

PARTS = {"body": body, "gate": gate, "assembled": assembled}


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
    print(f"gate: {len(gate)} voxels, {E.n_components(gate)} component(s)")
    print(f"total solid: {len(body) + len(gate)} (cap ~12k)")
    print(f"DOOR_POINT={DOOR_POINT} PEN_MIN={PEN_MIN} PEN_MAX={PEN_MAX} "
          f"GATE_HINGE={GATE_HINGE} FOOTPRINT={FOOTPRINT} HEIGHT={HEIGHT}")
    (bb0, bb1) = E.bbox(assembled)
    print(f"assembled bbox: {bb0}..{bb1}")
    if "--viewer-json" in sys.argv:
        print(json.dumps({
            "parts": {
                "body": {"voxels": len(body), "pivot": None},
                "gate": {"voxels": len(gate), "pivot": None},
            },
            "palette_names": [n for n, _ in PALETTE],
            "landmarks": {
                "DOOR_POINT": list(DOOR_POINT),
                "PEN_MIN": list(PEN_MIN),
                "PEN_MAX": list(PEN_MAX),
                "GATE_HINGE": list(GATE_HINGE),
                "FOOTPRINT": list(FOOTPRINT),
                "HEIGHT": HEIGHT,
            },
        }))
    if "--write-vox" in sys.argv:
        here = os.path.dirname(os.path.abspath(__file__))
        out = os.path.join(here, "out")
        os.makedirs(out, exist_ok=True)
        write_vox(os.path.join(out, "encamp_pow_stockade_v1_body.vox"), body)
        write_vox(os.path.join(out, "encamp_pow_stockade_v1_gate.vox"), gate)
