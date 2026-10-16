#!/usr/bin/env python3
"""encamp_checkpoint_v1.py — Strike Bay encampment CANVAS set piece:
FORTIFIED CHECKPOINT (kkolk/strike-bay #675).

LANDMARK MAP (file coords; x right, y depth, z UP, 1 voxel = 0.15 m,
origin = pad footprint min corner at ground level, pad top z=1).
FRONT FACES FILE -y (min y): the hut doorway, lanterns, crate stacks and
the X tank trap are on the -y half; the sandbag wrap + wing and the flag
mast are on the +y (back) half. Left = min x viewed from the front.

  FOOTPRINT (53, 49): pad x 0..52, y 0..48 (7.95 x 7.35 m).
  HEIGHT     38 voxels (flag mast finial ~5.6 m; sandbag wall top z=19).

  pad        dirt_patch_pad z=0: flat dirt patches, ragged grass fringe,
             10 grass tufts on the fringe (welded to filled cells).
  hut        x 14..33, y 20..39 (2.85 x 2.85 m), plank walls z 1..13
             (3 flat tones + dark gap lines); doorway x 21..25, z 1..10
             open on the front wall (y=20) with a dark recess 3 deep;
             four 2x2 timber corner posts z 1..30 (rise through the
             sandbags); twin baffle walls inside the door (shadow
             detail); flat roof deck z 29..30, 3-voxel overhang, ring
             beams + fascia z 27..28. The bags wrap the plank walls:
             only the doorway and the wall above z=14 read as planks.
  sandbags   THE dominant mass: running-bond individual bags (~4-5 long
             x 2 x 2, tones #b89a6a / #a8895a / #c8aa7a, adjacent bags
             never share a tone, 1-voxel #806642 seams), 9 courses
             (top z=19, ~2.85 m of wall; the hut peeks above it):
               left wall  x 8..9,   y 16..42 (along the hut's left);
               back wall  x 8..48,  y 40..41, continuous behind the
                          hut, from the left wall to the pad's right;
               wing       x 40..48, y 40..45 (6 thick), stepping down
                          9 -> 7 -> 5 courses toward the right end
                          (~3 m of tapering wing behind the boom).
  lanterns   2x2 bright #f2c84b lantern cores with dark caps + ribs on
             the front posts at x 17..18 and x 28..29, y 18..19,
             z 8..11, clear of the sandbag line (bags end at y=16).
  roof net   camo net x 11..36, y 17..42 at z=32: LARGE irregular
             value-noise blotches (cell 5.5 -> 4-8 voxel blobs; 3 greens
             + brown), ragged rim with drooping edge voxels z 30..31,
             interior sag blotches z=31. Open band z 20..29 between the
             sandbag top and the net (posts + upper hut walls read
             through it).
  boom       front-right: 2x2 timber pivot post (33..34, 6..7) z 1..15
             with metal hinge cap z 15..16; olive 4x4x4 counterweight
             crate on its -x side (29..32, 6..9); striped arm x 35..51,
             2 thick in y (6..7), z 8..11: red #b8282a / white
             #e8e8e0 bands, 3 voxels per band, timber spar at z=8;
             rest post (49..51, 8..10) z 1..9 under the far end.
  trap       UPRIGHT X tank trap front-left: two 2x2 timber beams
             crossed in a VERTICAL plane rotated 45deg about z (normal
             along the front-left diagonal, so it faces the game
             camera): feet at (4,4)/(15,4)/(4,15)/(15,15), apex
             z=13 (~1.95 m), tie band at the crossing, foot blocks at
             every toe. Reads as a standing X from both game yaws.
  rail       low timber rail across the hut front on either side of the
             door at y=18: top beam z=5, continuous foot z=1, end posts
             z 2..4 (x 11..19 and x 27..35).
  crates     three stacks (olive / slate / amber, 4x3x3 up, dark base
             band + light lid) on the open pad in front of the hut:
             left-of-door (17, 10) 3 high, right-of-door (28, 10)
             2 high, right by the boom post (26, 3) 2 high; ammo can
             at (24, 11).
  flag       part: slim 1x1 dark-brown #3a2c20 mast at (47, 33),
             z 1..37 + rope bands + finial (clears the net top z=32 by
             ~0.75 m); 7x5 solid-olive #5a6b2f flag with a 2-thick
             light #d8d0a0 chevron at y=33, z 28..32, flying -x.

  DOOR_POINT (23, 17, 1) — on the pad just in front of the hut doorway
             (door x 21..25 at y=20): where spawned infantry step out.
  FLAG_PIVOT (47, 33, 1) — mast base; the flag part rotates about this
             z axis to sway.

Parts:
  body  everything static (pad, hut, sandbags, net, boom, trap, rail,
        crates, tufts) — ONE 6-connected component.
  flag  mast + chevron flag, separate so it can sway about FLAG_PIVOT.
  assembled  body + flag merged (preview only).

Voxel budget: ~10k total (cap ~12k), pad included.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import encamp_canvas as E

rng = random.Random(675)

PALETTE = [  # (name, rgb); color index = position + 1
    ("dirt",          (150, 110,  72)),   # 1 pad dirt
    ("dirt_dark",     (118,  84,  54)),   # 2 pad dark patch
    ("dirt_dark2",    (102,  74,  48)),   # 3 pad darker patch
    ("dirt_light",    (168, 128,  86)),   # 4 pad light patch
    ("grass",         (107, 132,  62)),   # 5 pad fringe
    ("grass_dark",    ( 82, 104,  48)),   # 6 pad fringe shade
    ("sand_tan1",     (184, 154, 106)),   # 7 sandbag tone #b89a6a
    ("sand_tan2",     (168, 137,  90)),   # 8 sandbag tone #a8895a
    ("sand_tan3",     (200, 170, 122)),   # 9 sandbag tone #c8aa7a
    ("sand_seam",     (128, 100,  66)),   # 10 sandbag seams #806642
    ("timber",        (122,  88,  54)),   # 11 hut corner posts
    ("timber_dark",   ( 88,  62,  38)),   # 12 beams, boom posts, fascia
    ("timber_light",  (148, 112,  70)),   # 13 ring beams, trap faces
    ("plank1",        (150, 118,  76)),   # 14 hut wall tone 1
    ("plank2",        (138, 106,  66)),   # 15 hut wall tone 2
    ("plank3",        (160, 128,  86)),   # 16 hut wall tone 3
    ("plank_dark",    (112,  84,  52)),   # 17 wall gap lines, baffle
    ("deck_dark",     (104,  76,  46)),   # 18 roof deck under-layer
    ("net_olive",     ( 90, 107,  47)),   # 19 camo net green 1
    ("net_moss",      (108, 126,  58)),   # 20 camo net green 2
    ("net_olive_dk",  ( 68,  82,  36)),   # 21 camo net green 3
    ("net_brown",     (110,  82,  48)),   # 22 camo net brown
    ("olive",         ( 90, 107,  47)),   # 23 olive crate body
    ("olive_dark",    ( 64,  78,  34)),   # 24 olive crate band
    ("olive_lite",    (118, 134,  66)),   # 25 olive crate lid
    ("slate",         ( 74,  80,  88)),   # 26 slate crate body
    ("slate_dark",    ( 52,  56,  64)),   # 27 slate crate band
    ("slate_lite",    (100, 106, 116)),   # 28 slate crate lid
    ("amber",         (168, 118,  58)),   # 29 amber crate body
    ("amber_dark",    (128,  86,  42)),   # 30 amber crate band
    ("amber_lite",    (198, 150,  84)),   # 31 amber crate lid
    ("can",           ( 58,  66,  52)),   # 32 ammo-can body
    ("can_dark",      ( 40,  46,  36)),   # 33 ammo-can latch
    ("can_lite",      ( 86,  96,  76)),   # 34 ammo-can lid
    ("red",           (184,  40,  42)),   # 35 boom stripe #b8282a
    ("white",         (232, 232, 224)),   # 36 boom stripe #e8e8e0
    ("lantern",       (242, 200,  75)),   # 37 lantern core #f2c84b
    ("lantern_glow",  (255, 232, 140)),   # 38 lantern hot core
    ("metal_dark",    ( 52,  50,  46)),   # 39 lantern caps, hinge
    ("flag_olive",    ( 90, 107,  47)),   # 40 flag field #5a6b2f
    ("flag_mark",     (216, 208, 160)),   # 41 flag chevron #d8d0a0
    ("rope",          (168, 144,  92)),   # 42 mast rope bands
    ("mast_dark",     ( 58,  44,  32)),   # 43 mast #3a2c20
    ("dark",          ( 30,  24,  18)),   # 44 doorway recess
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

FOOTPRINT = (53, 49)
HEIGHT = 38
DOOR_POINT = (23, 17, 1)
FLAG_PIVOT = (47, 33, 1)

body = {}
flag = {}
assembled = {}

NET_TONES = ("net_olive", "net_moss", "net_olive_dk", "net_brown")
SAND_TONES = ("sand_tan1", "sand_tan2", "sand_tan3")
SAND_SEAM = "sand_seam"

# ---------------------------------------------------------------- pad
E.dirt_patch_pad(body, CI, rng, 0, 53, 0, 49)
# weld off-diagonal pad nibbles to the main sheet (single component)
for (x, y, _z) in list(body.keys()):
    if (x, y, 0) not in body:
        continue
    if not any((x + dx, y + dy, 0) in body
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= x + dx < 53 and 0 <= y + dy < 49:
                body[(x + dx, y + dy, 0)] = CI["grass_dark"]
                break
for (tx, ty) in ((3, 5), (10, 3), (26, 2), (44, 4), (50, 16), (4, 30),
                 (14, 46), (38, 47), (50, 40), (28, 46)):
    E.grass_tuft(body, CI, tx, ty, rng)

# ---------------------------------------------------------------- hut
HX0, HX1, HY0, HY1 = 14, 33, 20, 39   # exclusive; walls on the perimeter
POSTS = ((HX0, HY0), (HX1 - 2, HY0), (HX0, HY1 - 2), (HX1 - 2, HY1 - 2))


def wall_tone(x, y):
    """Flat per-plank tone, 3 shades; front/back walls plank along x."""
    if y in (HY0, HY1 - 1):
        return ("plank1", "plank2")[(x // 3) % 2]
    return ("plank2", "plank3")[(y // 3) % 2]


for x in range(HX0, HX1):
    for y in (HY0, HY1 - 1):
        for z in range(1, 14):
            body[(x, y, z)] = CI[wall_tone(x, y)]
for y in range(HY0, HY1):
    for x in (HX0, HX1 - 1):
        for z in range(1, 14):
            body[(x, y, z)] = CI[wall_tone(x, y)]
for x in range(HX0, HX1):                       # plank gap lines
    for z in range(1, 14):
        if (x - HX0) % 3 == 2:
            body[(x, HY0, z)] = CI["plank_dark"]
            body[(x, HY1 - 1, z)] = CI["plank_dark"]
for y in range(HY0, HY1):
    for z in range(1, 14):
        if (y - HY0) % 3 == 2:
            body[(HX0, y, z)] = CI["plank_dark"]
            body[(HX1 - 1, y, z)] = CI["plank_dark"]
for (px, py) in POSTS:                          # 2x2 corner posts to z30
    E.box(body, CI, px, px + 2, py, py + 2, 1, 30, "timber")
# doorway x 21..25 (0.75 m), z 1..10, dark recess 3 deep
for x in range(21, 26):
    for z in range(1, 11):
        body.pop((x, HY0, z), None)
E.box(body, CI, 21, 26, HY0 + 1, HY0 + 3, 0, 1, "dark")   # recess floor
for x in range(21, 26):                         # recess back + soffit
    for z in range(1, 11):
        body[(x, HY0 + 3, z)] = CI["dark"]
    body[(x, HY0 + 1, 10)] = CI["dark"]
    body[(x, HY0 + 2, 10)] = CI["dark"]
for bx in (17, 28):                             # twin baffle inside (shadow)
    E.box(body, CI, bx, bx + 1, HY0 + 4, HY0 + 10, 1, 8, "plank_dark")
# roof deck z 29..30, 3-voxel overhang; fascia + ring beams z 27..28
for x in range(HX0 - 3, HX1 + 3):
    for y in range(HY0 - 3, HY1 + 3):
        body[(x, y, 29)] = CI["deck_dark"]
        body[(x, y, 30)] = CI["plank2" if (x // 3) % 2 else "plank1"]
for x in range(HX0 - 3, HX1 + 3):
    for z, c in ((28, "timber_dark"), (27, "timber_light")):
        body[(x, HY0 - 3, z)] = CI[c]
        body[(x, HY1 + 2, z)] = CI[c]
for y in range(HY0 - 3, HY1 + 3):
    for z, c in ((28, "timber_dark"), (27, "timber_light")):
        body[(HX0 - 3, y, z)] = CI[c]
        body[(HX1 + 2, y, z)] = CI[c]
for (px, py) in POSTS:                          # corner stubs to the net
    E.box(body, CI, px, px + 2, py, py + 2, 30, 32, "timber")

# ---------------------------------------------------------------- sandbags
# 9 courses (2-tall each) to z=19: the dominant mass wrapping the hut.
E.sandbag_bond_wall(body, CI, rng, 8, 10, 16, 42, 1, 9, SAND_TONES,
                    SAND_SEAM, axis="y")         # left wall along the hut
E.sandbag_bond_wall(body, CI, rng, 10, 48, 40, 42, 1, 9, SAND_TONES,
                    SAND_SEAM, axis="x")         # back wall, full width
# wing: 6 thick, steps 9 -> 7 -> 5 courses toward the right end
WING = ((40, 48, 9), (40, 48, 7), (40, 48, 5))   # (x0, x1, courses) rows
for k, (wx0, wx1, nc) in enumerate(WING):
    E.sandbag_bond_wall(body, CI, rng, wx0, wx1, 42 + 2 * k, 44 + 2 * k,
                        1, nc, SAND_TONES, SAND_SEAM, axis="x")

# ---------------------------------------------------------------- lanterns
for lx in (17, 28):
    E.lantern(body, CI, lx, HY0 - 1, 8, glow="lantern", frame="metal_dark")
    body[(lx, HY0 - 1, 10)] = CI["lantern_glow"]  # hot core centre voxel

# ---------------------------------------------------------------- camo net
E.camo_net(body, CI, rng, 11, 36, 17, 42, 32, NET_TONES, cover=0.62,
           cell=5.5)

# ---------------------------------------------------------------- boom barrier
# ~3.5 m arm: 23 voxels x 36..58 won't fit the 53-wide pad from post 33;
# pivot post at x 33, arm x 35..51 (16 voxels visible) + rest at 48..50.
BPX, BPY = 33, 6                                # pivot post 2x2
E.box(body, CI, BPX, BPX + 2, BPY, BPY + 2, 1, 15, "timber_dark")
E.box(body, CI, BPX, BPX + 2, BPY, BPY + 2, 15, 16, "metal_dark")  # hinge
E.crate(body, CI, 29, BPY, 1, 4, 4, 4, base="olive", dark="olive_dark",
        edge="olive_dark")                       # counterweight (-x side)
for i, x in enumerate(range(35, 52)):            # striped arm along +x
    c = "red" if (i // 3) % 2 == 0 else "white"
    for yy in (BPY, BPY + 1):                    # 2-thick arm
        for zz in (9, 10, 11):
            body[(x, yy, zz)] = CI[c]
        body[(x, yy, 8)] = CI["timber_dark"]     # underside spar (weld)

# ---------------------------------------------------------------- tank trap
def beam_line(d, p0, p1, c1="timber_light", c2="timber", thick=2):
    """Straight 2x2 beam from p0 to p1 (3-tuples, any direction):
    interpolated samples welded with axis-unit steps so it is
    face-connected end to end."""
    n = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]), abs(p1[2] - p0[2])))
    pts = []
    for i in range(n + 1):
        t = i / n
        p = (p0[0] + round((p1[0] - p0[0]) * t),
             p0[1] + round((p1[1] - p0[1]) * t),
             p0[2] + round((p1[2] - p0[2]) * t))
        if not pts or p != pts[-1]:
            pts.append(p)
    for (a, b) in zip(pts, pts[1:]):
        x, y, z = a
        while True:
            for dx in range(thick):
                for dy in range(thick):
                    d[(x + dx, y + dy, z)] = CI[
                        c1 if (dx + dy) % 2 == 0 else c2]
            if (x, y, z) == b:
                break
            if x != b[0]:
                x += 1 if b[0] > x else -1
            elif y != b[1]:
                y += 1 if b[1] > y else -1
            else:
                z += 1 if b[2] > z else -1


# UPRIGHT X in a vertical plane rotated 45deg about z (normal along the
# front-left diagonal): faces the yaw-0 game camera dead-on and stays
# readable at yaw+45. Apex ~1.35 m, feet on the pad.
beam_line(body, (4, 4, 1), (15, 15, 13))         # rising beam  /
beam_line(body, (4, 15, 13), (15, 4, 1))         # falling beam \
for t in range(3):                               # tie band at the crossing
    body[(9 + t, 9 + t, 7)] = CI["timber_dark"]
    body[(10 + t, 9 + t, 7)] = CI["timber_dark"]
for (fx, fy) in ((4, 4), (15, 4), (4, 15), (15, 15)):   # foot blocks
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            body[(fx + dx, fy + dy, 1)] = CI["timber_dark"]

# ---------------------------------------------------------------- front rail
for (rx0, rx1) in ((11, 20), (27, 36)):          # either side of the door
    for rx in range(rx0, rx1):
        body[(rx, 18, 5)] = CI["timber_light"]   # top rail
        body[(rx, 18, 1)] = CI["timber_dark"]    # continuous foot (weld)
    for rx in (rx0, rx1 - 1):
        for z in range(2, 5):
            body[(rx, 18, z)] = CI["timber_dark"]

# ---------------------------------------------------------------- crates + can
E.crate(body, CI, 17, 10, 1, 5, 4, 4, base="olive", dark="olive_dark",
        edge="olive_dark")                       # left-of-door stack, 3 high
E.crate(body, CI, 18, 11, 5, 4, 3, 3, base="slate", dark="slate_dark",
        edge="slate_dark")
E.crate(body, CI, 19, 11, 8, 4, 3, 3, base="amber", dark="amber_dark",
        edge="amber_dark")
E.crate(body, CI, 28, 10, 1, 4, 4, 4, base="amber", dark="amber_dark",
        edge="amber_dark")                       # right-of-door stack
E.crate(body, CI, 29, 11, 5, 4, 3, 3, base="olive", dark="olive_dark",
        edge="olive_dark")
E.crate(body, CI, 26, 3, 1, 4, 4, 4, base="slate", dark="slate_dark",
        edge="slate_dark")                       # right stack by boom
E.crate(body, CI, 27, 4, 5, 4, 3, 3, base="amber", dark="amber_dark",
        edge="amber_dark")
E.ammo_can(body, CI, 24, 11, 1, body_c="can", lid="can_lite",
           latch="can_dark")

# ---------------------------------------------------------------- flag part
E.flag_mast(flag, CI, 47, 33, 1, 37, color="mast_dark", cap="timber_dark",
            rope="rope")
E.flag_chevron(flag, CI, 40, 33, 28, 7, 5, "flag_olive", "flag_mark",
               thick=2)

# ---------------------------------------------------------------- assemble
assembled.update(body)
assembled.update(flag)

if __name__ == "__main__":
    print(f"body={len(body)} flag={len(flag)} assembled={len(assembled)}")
    print(f"components: body={E.n_components(body)} "
          f"flag={E.n_components(flag)}")
    print(f"FOOTPRINT={FOOTPRINT} HEIGHT={HEIGHT} DOOR_POINT={DOOR_POINT} "
          f"FLAG_PIVOT={FLAG_PIVOT}")
    print(f"bbox assembled: {E.bbox(assembled)}")
