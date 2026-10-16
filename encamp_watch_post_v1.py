#!/usr/bin/env python3
"""Strike Bay encampment set piece — WATCH POST (encamp_watch_post_v1, #671).

Raised timber observation post on a dirt-and-grass base pad, from the owner
concept: four timber posts with X-bracing carry a square deck ~3 m up; the
deck rim is a three-course sandbag parapet with an entry gap where a wooden
ladder lands; a light frame above carries a mottled camo-net roof with
hanging strands; a flagpole with a yellow-chevron olive flag stands at the
back-right; crates and grass tufts dress the base.

LANDMARK MAP (file coords; x right, y forward, FRONT FACES FILE -y, z up).
  FOOTPRINT  (48, 28, 46): pad 7.2 x 4.2 m, total height 6.9 m.
  HEIGHT     46 voxels (pole cap; net top at 33 = 4.95 m).

  pad        (0..47, 9..36, 0) dirt interior, grass fringe, nibbled edge;
             = (legs bbox + crate-stack bboxes) + 4 voxels every side.
  posts      five 2x2 legs z 1..17 at the corners (13,13)/(31,13)/(13,31)/
             (31,31) and front-mid (22,13), timber_light with olive_dark
             foot plates; X braces + twin girts z 2..16 on every face.
  deck       (12..32, 12..32, z 18..19): dark joist layer + 3-tone planks,
             dark fascia rim; hatch cut x 24..29 y 12..13 (ladder landing);
             walking level z=20 = 3.0 m. Corner tie plates z 20..21.
  parapet    individual-bag sandbag ring, 3 courses z 20..25 (top 3.9 m),
             2 thick on the deck rim; bags alternate 3 flat tones
             (#c8aa7a / #b89a6a / #a8895a), 1-voxel #7a6440 seams in the
             bond joints and between courses, mortared shut (no
             see-through); ENTRY GAP front face x 22..30, full height.
  roof       lookout band z 26..31 open (0.9 m): 1x1 amber posts on the
             parapet corners (13,13)/(31,13)/(13,31)/(31,31) rise z26..34;
             ring beam z=32 (x/y 13..31 rim); camo net sheet z=33 over
             x/y 13..31 as noise-driven blotches in olive/moss/olive_dark/
             brown (1-3 voxel scale), scattered 1-voxel holes, ragged edge
             + tatters drooping 1-3 voxels below the rim.
  ladder     leans front-right into the gap: 2x2 timber_dark rails x 23..24
             / 28..29 from (y=9, z=1) to (y=14, z=19), lighter rungs every
             2 z; lands through the deck hatch.
  crates     two 5-crate stacks (4x3x3 crates in a 2x2 grid + topper,
             8x6 footprint): olive #5a6b2f / slate #4a5058 alternating
             sides, top faces #7a8b45 with a 1-voxel #a8763a top-edge
             band; front-left and right of the tower. 2 ammo cans
             (3x2x2, #4a5a2a) beside them.
  piles      3 low sandbag piles on the pad (2 courses, stacked, no float).
  tufts      grass tufts on the pad fringe (deterministic rng, seed 671).

  DOOR_POINT (26, 11, 0) — pad, in front of the ladder / entry gap (-y
             side): where spawned infantry step out.
  FLAG_PIVOT (31, 31, 34) — pole base centre at the back-right corner
             post top; the flag part rotates about this z-axis to sway.

Parts:
  body  everything static (pad, legs, bracing, deck, parapet, roof,
        ladder, crates, tufts) — one 6-connected component.
  flag  1x1 dark pole (#3a2c20) from the back-right corner post (31,31)
        z 34..45, ~1.8 m above the net, + olive 7x5 cloth with a 2-thick
        light chevron (#d8d0a0) at the pole top z 40..44 flying -x;
        separate so it can sway about FLAG_PIVOT.
  assembled  body + flag merged (preview only).

Voxel budget: ~5.2k total (cap ~12k), pad included.
"""
import os
import random

import encamp_sandbag as fam

PALETTE = [
    # name           rgb
    ("timber_dark",  ( 92,  62,  38)),   # deck joists, fascia, ladder rails
    ("timber",       (128,  88,  52)),   # struts, girts, deck mid tone
    ("timber_light", (156, 116,  74)),   # posts, ring beam, deck planks, rungs
    ("sand",         (200, 170, 122)),   # sandbag light  #c8aa7a
    ("sand_dark",    (184, 154, 106)),   # sandbag mid    #b89a6a
    ("sand_shadow",  (168, 137,  90)),   # sandbag shade  #a8895a
    ("sand_gap",     (122, 100,  64)),   # bag seams      #7a6440
    ("moss",         (110, 122,  58)),   # camo patch     #6e7a3a
    ("olive",        ( 90, 107,  47)),   # camo patch     #5a6b2f
    ("brown_dark",   (107,  85,  52)),   # camo patch     #6b5534
    ("olive_dark",   ( 74,  82,  52)),   # net tatters, pole, foot plates
    ("dirt",         (150, 126,  92)),   # pad interior
    ("dirt_dark",    (128, 104,  74)),   # pad speckle
    ("grass",        (104, 116,  70)),   # pad fringe, tufts
    ("grass_dark",   ( 80,  92,  56)),
    ("crate_olive",  ( 90, 107,  47)),   # stack sides    #5a6b2f
    ("crate_slate",  ( 74,  80,  88)),   # stack sides    #4a5058
    ("crate_top",    (122, 139,  69)),   # stack top face #7a8b45
    ("crate_band",   (168, 118,  58)),   # top edge band  #a8763a
    ("can_olive",    ( 74,  90,  42)),   # ammo can       #4a5a2a
    ("pole",         ( 58,  44,  32)),   # flag pole      #3a2c20
    ("flag_mark",    (216, 208, 160)),   # chevron        #d8d0a0
]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

FOOTPRINT = (48, 28, 46)  # pad x0..47 / y9..36, z up to pole cap 45
HEIGHT = 46
DOOR_POINT = (26, 11, 0)  # pad, in front of the ladder / entry gap
FLAG_PIVOT = (31, 31, 34)  # pole base centre on the back-right corner post

body = {}
flag = {}
assembled = {}

rng = random.Random(671)


def box(d, x0, x1, y0, y1, z0, z1, c):
    ci = CI[c]
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                d[(x, y, z)] = ci


def line(d, x0, y0, z0, x1, y1, z1, c):
    ci = CI[c]
    n = max(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0), 1)
    for i in range(n + 1):
        t = i / n
        d[(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t),
           round(z0 + (z1 - z0) * t))] = ci


# ---------------------------------------------------------------- base pad + tufts
# pad = (tower legs bbox + crate-stack bboxes) + 4 voxels every side:
# legs x12..33/y13..32, stacks x4..43/y14..24 -> pad x0..47, y9..36
fam.dirt_pad(body, 0, 9, 47, 36, CI["dirt"], CI["dirt_dark"],
             CI["grass"], CI["grass_dark"], rng, fringe=3)
for (tx, ty) in ((5, 10), (6, 35), (39, 10), (38, 35), (2, 25), (45, 25),
                 (10, 12), (35, 12), (20, 35), (30, 10)):
    fam.grass_tuft(body, tx, ty, CI["grass"], CI["grass_dark"], rng)

# ---------------------------------------------------------------- legs + X-bracing
LEGS = [(13, 13), (31, 13), (13, 31), (31, 31), (22, 13)]
for (lx, ly) in LEGS:                          # 2x2 posts, lighter wood
    for x in (lx, lx + 1):
        for y in (ly, ly + 1):
            for z in range(1, 18):
                body[(x, y, z)] = CI["timber_light"]
    box(body, lx - 1, lx + 2, ly - 1, ly + 2, 1, 1, "olive_dark")  # foot plate

FACES = (((13, 13), (31, 13)),      # front (-y)
         ((13, 31), (31, 31)),      # back
         ((13, 13), (13, 31)),      # left
         ((31, 13), (31, 31)))      # right
for (a, b) in FACES:
    (ax, ay), (bx, by) = a, b
    horiz = ay == by              # front/back faces thicken in y, sides in x
    for (za, zb) in ((2, 16), (3, 16), (16, 2), (15, 2)):   # X brace
        for o in (0, 1):
            ox = 0 if horiz else o
            oy = o if horiz else 0
            for dz in (0, 1):        # z-thick too: bridges diagonal steps
                line(body, ax + 1 + ox, ay + 1 + oy, za + dz,
                     bx + 1 + ox, by + 1 + oy, zb + dz, "timber")
    line(body, ax + 1, ay + 1, 10, bx + 1, by + 1, 10, "timber_dark")  # girts
    line(body, ax + 1, ay + 1, 11, bx + 1, by + 1, 11, "timber_dark")
for x in range(12, 33):                          # deck: joists + planks
    for y in range(12, 33):
        body[(x, y, 18)] = CI["timber_dark"]
        body[(x, y, 19)] = (CI["timber_light"] if y % 4 in (0, 1)
                            else CI["timber"])
for x in range(12, 33):                          # fascia
    for y in (12, 32):
        body[(x, y, 18)] = CI["timber_dark"]
        body[(x, y, 19)] = CI["timber_dark"]
for y in range(12, 33):
    for x in (12, 32):
        body[(x, y, 18)] = CI["timber_dark"]
        body[(x, y, 19)] = CI["timber_dark"]
for x in range(24, 30):                           # hatch: ladder lands on deck
    for y in (12, 13):
        for z in (18, 19):
            body.pop((x, y, z), None)
for x in range(23, 30):                           # shadowed threshold strip
    for y in (14, 15, 16):
        if (x, y, 19) in body:
            body[(x, y, 19)] = CI["timber_dark"]

# ---------------------------------------------------------------- sandbag parapet
fam.parapet_ring(body, 12, 12, 32, 32, 20, 3,
                 CI["sand"], CI["sand_dark"], CI["sand_shadow"],
                 ci_seam=CI["sand_gap"], gaps=(("s", 22, 30),))
for (cx, cy) in ((13, 13), (31, 13), (13, 31), (31, 31)):
    box(body, cx - 1, cx, cy - 1, cy, 20, 21, "timber_dark")  # corner ties

# ---------------------------------------------------------------- camo-net roof
# net clears the sandbags AND overhangs nothing: bag top z25, lookout band
# z26..31 (0.9 m) open on all sides, frame posts z26..33, net sheet inset
# (x14..30) so the band reads from game yaw 0.
for (px, py) in ((13, 13), (31, 13), (13, 31), (31, 31)):
    for z in range(26, 35):         # 1x1 light posts on the parapet corners
        body[(px, py, z)] = CI["crate_band"]
for x in range(13, 32):                         # ring beam under the net rim
    for y in range(13, 32):
        if x in (13, 31) or y in (13, 31):
            body[(x, y, 32)] = CI["timber_light"]
_pc = {n: CI[n] for n in ("olive", "moss", "olive_dark", "brown_dark")}
for x in range(13, 32):
    for y in range(13, 32):
        edge = x in (13, 31) or y in (13, 31)
        if edge and (x * 7 + y * 13) % 4 == 0:
            continue                            # ragged net edge
        # noise-driven blotches, 1-3 voxel scale (not a checkerboard)
        h = ((x * 11 + y * 7) % 5) + ((x // 3) * 3 + (y // 3) * 5) % 7
        if ((x * 13 + y * 17) % 23) % 11 == 0:
            continue                            # a few 1-voxel holes
        c = ("olive" if h % 5 < 2 else "moss" if h % 5 < 4
             else "olive_dark" if h % 5 == 4 else "brown_dark")
        body[(x, y, 33)] = _pc[c]
for (x, y) in ((13, 18), (13, 25), (18, 13), (25, 13), (31, 19), (31, 26),
               (18, 31), (26, 31), (31, 31), (13, 15)):
    if (x, y, 33) not in body:
        continue                                # ragged edge skipped
    for dz in range(1, 1 + (x * 3 + y) % 3):    # drooping tatters 1-3 deep
        body[(x, y, 33 - dz)] = CI["olive_dark"]

# ---------------------------------------------------------------- ladder (front-right)
for x in (23, 24, 28, 29):                       # rails: 2 wide x 2 deep, solid
    for z in range(1, 20):
        y = 9 + round(5 * (z - 1) / 18)
        body[(x, y, z)] = CI["timber_dark"]
        if y < 14:
            body[(x, y + 1, z)] = CI["timber_dark"]
for z in range(1, 20, 2):                       # rungs, lighter wood
    y = 9 + round(5 * (z - 1) / 18)
    for x in range(24, 29):
        body[(x, y, z)] = CI["timber_light"]

# ---------------------------------------------------------------- crates + piles
# two 5-crate stacks (4x3x3 in a 2x2 grid + topper) + 2 ammo cans
fam.crate_stack(body, 4, 14, CI)
fam.crate_stack(body, 36, 15, CI)
fam.ammo_can(body, 13, 20, 1, CI["can_olive"], CI["can_olive"])
fam.ammo_can(body, 13, 23, 1, CI["can_olive"], CI["can_olive"])
# low sandbag piles on the pad (in front of the ladder and by the stacks)
fam.bag_pile(body, 20, 10, 3, CI["sand"], CI["sand_dark"], CI["sand_shadow"])
fam.bag_pile(body, 33, 11, 2, CI["sand"], CI["sand_dark"], CI["sand_shadow"])
fam.bag_pile(body, 8, 33, 2, CI["sand"], CI["sand_dark"], CI["sand_shadow"])

# ---------------------------------------------------------------- flag part
# 1x1 dark pole on the back-right corner post, ~1.5 m above the net;
# 7x5 olive cloth with a 2-thick light chevron hangs at the pole top
fam.flagpole(flag, 31, 31, 34, 45, CI["pole"], CI["pole"])
fam.flag_chevron(flag, 30, 31, 40, 7, 5, CI["olive"], CI["flag_mark"])

# ---------------------------------------------------------------- assembled + checks
assembled.update(body)
assembled.update(flag)


def components(d):
    """Count 6-connected components."""
    seen = set()
    n = 0
    for p in d:
        if p in seen:
            continue
        n += 1
        stack = [p]
        while stack:
            (x, y, z) = stack.pop()
            if (x, y, z) in seen:
                continue
            seen.add((x, y, z))
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                      (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in d:
                    stack.append(q)
    return n


# ---------------------------------------------------------------- .vox writer (MagicaVoxel 150) — verbatim boilerplate
def write_vox(path, vox, PALETTE):
    import struct
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    sx, sy, sz = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) + 1
    xoff, yoff = -min(xs), -min(ys)
    size_content = struct.pack("<iii", sx, sy, sz)
    xyzi = struct.pack("<i", len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("<BBBB", x + xoff, y + yoff, z, ci)
    rgba = b"".join(struct.pack("<BBBB", r, g, b, 255) for _, (r, g, b) in PALETTE)
    rgba += struct.pack("<BBBB", 0, 0, 0, 0) * (256 - len(PALETTE))
    main_children = chunk(b"SIZE", size_content) + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)
    with open(path, "wb") as f:
        f.write(b"VOX ")
        f.write(struct.pack("<i", 150))
        f.write(chunk(b"MAIN", b"", main_children))
    print(f"wrote {path} ({len(vox)} voxels)")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "out")
    os.makedirs(out, exist_ok=True)
    for name, part in (("body", body), ("flag", flag),
                       ("assembled", assembled)):
        write_vox(os.path.join(out, f"encamp_watch_post_{name}_v1.vox"),
                  part, PALETTE)
    print(f"body={len(body)} flag={len(flag)} assembled={len(assembled)}")
    print(f"components body={components(body)} flag={components(flag)}")
    print(f"FOOTPRINT={FOOTPRINT} HEIGHT={HEIGHT} DOOR_POINT={DOOR_POINT} "
          f"FLAG_PIVOT={FLAG_PIVOT}")
