#!/usr/bin/env python3
"""encamp_supply_shack_v1.py — Strike Bay encampment TIMBER set piece: SUPPLY SHACK.

Landmark map (file coords, z-up, 1 voxel = 0.15 m; origin = pad footprint
min corner at ground level = pad top z=1):
  frame:   x = left/right (left = min x viewed from the front),
           y = depth (FRONT = file -y, min y), z = up.
  front:   open shack face at y=16 (4 posts + chunky top beam, deck porch
           juts 6 voxels toward -y). back: solid timber wall at y=38.
  shack:   31 x 23 voxels (~4.5 x 3.5 m). deck x8..37, y10..38 (floor
           voxels z=4, walk surface z=5), raised on posts over the pad.
  walls:   back y=38 + sides x=8 / x=37, z5..17 (1 thick, board-shaded)
           with dark vertical corner boards.
  roof:    single-slope weathered-wood planks y15..41, front lip z=22 over
           the open face, sloping down to z=18 at the back wall; each
           x-column one flat tone of 3 brown-greys with a dark gap column
           every 4th plank; 2-voxel overhang + thick fascia rim.
           bbox x6..39.
  chimney: dark stovepipe 2x2 at x11..12, y33..34, z19..24 + 3x3 cap z25.
  steps:   8 wide (x17..24), 4 treads descending y9 -> y6 to the pad.
  door:    open entrance between the front posts, centre x~21.
  shelves: back-wall unit x12..29 (uprights + boards z8, z11) with small
           boxes in olive / slate / amber, some 3 tall.
  lamps:   2 lanterns on brackets on the front posts (14,16) and (28,16),
           porch side: dark cap z19, warm glow z17..18, dark base z16.
  sign:    plain plate (NO lettering) on the beam face x30..33, y15, z20.
  lean-to: open light-timber frame (2x2 outer posts x45..46, rails to the
           shack wall at z10) with a flat 1-thick mottled olive/brown net
           sheet (sag 1 in the middle, tatters on the edge), 2-high crate
           stacks beneath.
  crates:  26 hero boxes (>=4x3x3, some 5x4x4) in olive / slate / amber
           with dark base band + light lid + dark corners: stack (a)
           front-left 3x2x2 + topper, stack (b) 3 on the deck inside the
           open front (low left, stacked right), stack (c) 5 under the net
           2 high, singles front-right / behind x2 / back-right.
  sandbags: two short walls flanking the steps at y=5 (x15..16, x26..28).
  pole:    flagpole 1x1 at (36,37), roof z18 -> z28 = 1.5 m above ridge.
  flag:    olive cloth x29..35, y37, z24..28 (7x5, ~1.05 x 0.75 m) with a
           yellow chevron pointing at the hoist (own part).

Constants:
  DOOR_POINT = (21, 4, 1)   -- soldiers step out here (pad, before steps)
  FOOTPRINT  = (52, 44)     -- pad bbox in voxels (7.8 x 6.6 m)
  HEIGHT     = 29           -- pole top voxel z=28
  FLAG_PIVOT = (36, 37, 28) -- pole top: flag's hoist-top corner
Parts:
  body -- everything static incl. pad, pole (ONE 6-connected component)
  flag -- cloth only (sways later; ONE 6-connected component)
  assembled -- body + flag (rendering)
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import encamp_timber as E

rng = random.Random(668)

PALETTE = [  # (name, rgb); color index = position + 1
    ("dirt",          (150, 110,  72)),  # 1  pad dirt
    ("dirt_dark",     (118,  84,  54)),  # 2  pad speckle, net mottling
    ("grass",         (107, 132,  62)),  # 3  pad border
    ("grass_dark",    ( 82, 104,  48)),  # 4  pad border shade
    ("timber",        (122,  88,  54)),  # 5  walls, posts, beams
    ("timber_dark",   ( 88,  62,  38)),  # 6  seams, corner boards, pole, fascia
    ("plank",         (158, 124,  80)),  # 7  deck, steps, shelves, sign plate
    ("plank_dark",    (128,  98,  62)),  # 8  deck shade, tread nosing
    ("roof_a",        (150, 132, 110)),  # 9  weathered plank tone A
    ("roof_b",        (134, 118,  98)),  # 10 weathered plank tone B
    ("roof_c",        (120, 106,  88)),  # 11 weathered plank tone C
    ("roof_seam",     ( 78,  68,  56)),  # 12 plank gap lines
    ("olive",         ( 90, 107,  47)),  # 13 olive crates, net
    ("olive_dark",    ( 64,  78,  34)),  # 14 olive base band + corners
    ("olive_lite",    (118, 134,  66)),  # 15 olive lid
    ("slate",         ( 74,  80,  88)),  # 16 slate-grey crates
    ("slate_dark",    ( 52,  56,  64)),  # 17 slate base band + corners
    ("slate_lite",    (100, 106, 116)),  # 18 slate lid
    ("amber",         (168, 118,  58)),  # 19 amber wood crates
    ("amber_dark",    (128,  86,  42)),  # 20 amber base band + corners
    ("amber_lite",    (198, 150,  84)),  # 21 amber lid
    ("sandbag",       (168, 148, 106)),  # 22 sandbags
    ("sandbag_dark",  (138, 120,  84)),  # 23 sandbag seams
    ("metal_dark",    ( 44,  44,  48)),  # 24 stovepipe
    ("lamp_glow",     (255, 176,  64)),  # 25 lantern glass
    ("lamp_frame",    ( 60,  50,  36)),  # 26 lantern frame
    ("flag_olive",    ( 96, 102,  52)),  # 27 flag cloth
    ("flag_yellow",   (214, 178,  60)),  # 28 flag chevron
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

DOOR_POINT = (21, 4, 1)
FOOTPRINT = (52, 44)
HEIGHT = 29
FLAG_PIVOT = (36, 37, 28)

body = {}
flag = {}

CRATE_TRIO = {
    "olive": ("olive", "olive_dark", "olive_lite"),
    "slate": ("slate", "slate_dark", "slate_lite"),
    "amber": ("amber", "amber_dark", "amber_lite"),
}


def hero_crate(x, y, z, w, dp, h, trio):
    """Bright hero crate: flat base faces, 1-voxel dark base band, light
    lid layer, dark vertical corner edges. Min sensible size 4x3x3."""
    base, dark, lite = CRATE_TRIO[trio]
    E.box(body, CI, x, x + w, y, y + dp, z, z + h, base)
    E.box(body, CI, x, x + w, y, y + dp, z, z + 1, dark)      # base band
    E.box(body, CI, x, x + w, y, y + dp, z + h - 1, z + h, lite)  # lid
    for zz in range(z, z + h):                                 # corners
        for xx in (x, x + w - 1):
            for yy in (y, y + dp - 1):
                body[(xx, yy, zz)] = CI[dark]


def wall_shaded(x0, x1, y0, y1, z0, z1):
    """Timber wall with a dark seam course every 3 layers."""
    for z in range(z0, z1):
        c = "timber_dark" if (z % 3 == 2) else "timber"
        E.box(body, CI, x0, x1, y0, y1, z, z + 1, c)


# ------------------------------------------------------------ pad (z=0, top z=1)
E.dirt_pad(body, CI, rng, 0, 52, 0, 44)

# ------------------------------------------------------------ deck posts + plank deck (porch juts to y10)
for px in (8, 15, 22, 29, 37):
    for py in (10, 18, 26, 34):
        E.pole(body, CI, px, py, 1, 4, "timber_dark")
E.plank_floor(body, CI, 8, 38, 10, 39, 4)            # deck floor, walk z=5
for y in range(10, 39, 4):                           # plank gap lines
    for x in range(8, 38):
        body[(x, y, 4)] = CI["plank_dark"]
E.box(body, CI, 8, 38, 10, 11, 3, 4, "timber_dark")   # porch fascia

# ------------------------------------------------------------ walls (back + sides, top z17)
wall_shaded(8, 38, 38, 39, 5, 18)    # back wall y=38
wall_shaded(8, 9, 16, 39, 5, 18)     # left wall x=8
wall_shaded(37, 38, 16, 39, 5, 18)   # right wall x=37
for cx, cy in ((8, 16), (37, 16), (8, 38), (37, 38)):
    E.pole(body, CI, cx, cy, 5, 18, "timber_dark")   # dark corner boards

# ------------------------------------------------------------ open front: 4 posts + chunky beam
for px in (8, 14, 28, 37):
    E.pole(body, CI, px, 16, 5, 21, "timber")
E.box(body, CI, 8, 38, 16, 17, 20, 22, "timber_dark")  # front top beam
E.box(body, CI, 30, 34, 15, 16, 20, 21, "plank")       # plain sign plate

# ------------------------------------------------------------ mid posts (roof support, interior)
E.pole(body, CI, 13, 26, 5, 20, "timber")
E.pole(body, CI, 31, 26, 5, 20, "timber")

# ------------------------------------------------------------ single-slope plank roof, front z22 -> back z18
def roof_z(y):
    return int(22 - (y - 15) * 4.0 / 26.0)

TONES = ("roof_a", "roof_b", "roof_c")
for y in range(15, 42):
    z = roof_z(y)
    for x in range(6, 40):
        if x % 4 == 3:
            c = "roof_seam"                          # gap line between planks
        else:
            c = TONES[x % 3]                         # one flat tone per plank
        body[(x, y, z)] = CI[c]
for rx in (10, 17, 24, 31, 36):                      # rafters under the boards
    for y in range(15, 42):
        body[(rx, y, roof_z(y) - 1)] = CI["timber_dark"]
for x in range(6, 40):                               # thick fascia: front/back
    body[(x, 15, roof_z(15) - 1)] = CI["timber_dark"]
    body[(x, 41, roof_z(41) - 1)] = CI["timber_dark"]
for y in range(15, 42):                              # thick fascia: sides
    body[(6, y, roof_z(y) - 1)] = CI["timber_dark"]
    body[(39, y, roof_z(y) - 1)] = CI["timber_dark"]
for x in range(6, 40):                               # darker ridge caps
    body[(x, 15, roof_z(15) + 1)] = CI["roof_seam"]   # high front lip
    body[(x, 41, roof_z(41) + 1)] = CI["roof_seam"]   # low back edge

# ------------------------------------------------------------ stovepipe chimney (slim, dark)
E.box(body, CI, 11, 13, 33, 35, 19, 25, "metal_dark")
E.box(body, CI, 10, 13, 32, 35, 25, 26, "metal_dark")  # 3x3 cap

# ------------------------------------------------------------ front steps (8 wide, 4 treads to the pad)
E.steps_front(body, CI, 17, 25, y_edge=10, z_top=5, n=4)

# ------------------------------------------------------------ back-wall shelf unit + small boxes
for ux in (12, 29):
    E.pole(body, CI, ux, 37, 5, 13, "plank")            # light-wood uprights
E.box(body, CI, 12, 30, 36, 38, 8, 9, "plank")       # shelf low (meets wall)
E.box(body, CI, 12, 30, 36, 38, 11, 12, "plank")     # shelf high (meets wall)
E.crate(body, CI, 13, 36, 9, w=2, dpt=2, h=3, base="amber", dark="amber_dark")
E.crate(body, CI, 16, 36, 9, w=2, dpt=2, h=2, base="olive_lite", dark="olive_dark")
E.crate(body, CI, 19, 36, 9, w=2, dpt=2, h=2, base="slate_lite", dark="slate_dark")
E.crate(body, CI, 22, 36, 9, w=2, dpt=2, h=3, base="olive", dark="olive_dark")
E.crate(body, CI, 26, 36, 9, w=2, dpt=2, h=2, base="amber_lite", dark="amber_dark")
E.crate(body, CI, 13, 36, 12, w=2, dpt=2, h=2, base="slate", dark="slate_dark")
E.crate(body, CI, 17, 36, 12, w=2, dpt=2, h=2, base="amber_lite", dark="amber_dark")
E.crate(body, CI, 21, 36, 12, w=2, dpt=2, h=2, base="olive_lite", dark="olive_dark")
E.crate(body, CI, 25, 36, 12, w=2, dpt=2, h=2, base="slate_lite", dark="slate_dark")

# ------------------------------------------------------------ 2 lanterns on the front posts, porch side
for lx in (14, 28):
    body[(lx, 15, 20)] = CI["timber_dark"]           # bracket (meets post+beam)
    body[(lx, 15, 19)] = CI["lamp_frame"]            # cap
    body[(lx, 15, 18)] = CI["lamp_glow"]             # warm glow
    body[(lx, 15, 17)] = CI["lamp_glow"]
    body[(lx, 15, 16)] = CI["lamp_frame"]            # base

# ------------------------------------------------------------ lean-to: open frame + flat net sheet
E.box(body, CI, 45, 47, 15, 17, 1, 11, "timber")     # outer post, front
E.box(body, CI, 45, 47, 29, 31, 1, 11, "timber")     # outer post, back
E.box(body, CI, 37, 47, 16, 17, 10, 11, "timber")    # rail to shack, front
E.box(body, CI, 37, 47, 30, 31, 10, 11, "timber")    # rail to shack, back
E.box(body, CI, 45, 47, 16, 31, 10, 11, "timber")    # outer rail joining posts
for nx in range(37, 47):                             # flat mottled sheet
    for ny in range(15, 32):
        sagged = (40 <= nx <= 43 and 20 <= ny <= 27)
        r = rng.random()
        c = CI["olive" if r < 0.45
               else ("olive_dark" if r < 0.8 else "dirt_dark")]
        body[(nx, ny, 11)] = c
        if sagged:
            body[(nx, ny, 10)] = c                    # 2-thick middle = the sag
for tx, ty in ((37, 20), (44, 15), (40, 31), (46, 24), (39, 16)):
    body[(tx, ty, 10)] = CI["olive_dark"]            # tatters on the edge
# stacks beneath the net, 2 high
hero_crate(38, 18, 1, 4, 4, 4, "amber")
hero_crate(38, 23, 1, 4, 4, 3, "olive")
hero_crate(38, 18, 5, 3, 3, 3, "slate")
hero_crate(39, 24, 4, 3, 3, 3, "amber")
hero_crate(42, 24, 1, 4, 3, 3, "slate")

# ------------------------------------------------------------ crate stack (a): front-left, 3x2x2 + topper
for i, trio in enumerate(("olive", "slate", "amber")):
    hero_crate(2 + 4 * i, 3, 1, 4, 3, 3, trio)
    hero_crate(2 + 4 * i, 6, 1, 4, 3, 3,
               ("amber", "olive", "slate")[i])
for i, trio in enumerate(("slate", "amber", "olive")):
    hero_crate(2 + 4 * i, 3, 4, 4, 3, 3, trio)
for i, trio in enumerate(("olive", "slate", "amber")):
    hero_crate(2 + 4 * i, 6, 4, 4, 3, 3, trio)
hero_crate(6, 4, 7, 4, 3, 3, "slate")        # topper
# crate stack (b): on the deck just inside the open front (low on the
# left so the back-wall shelf stays visible from the front-left)
hero_crate(9, 19, 5, 5, 4, 4, "olive")
hero_crate(14, 20, 5, 4, 4, 3, "slate")
hero_crate(32, 19, 5, 4, 3, 3, "slate")
hero_crate(32, 19, 8, 3, 2, 2, "amber")
# singles: front-right, behind, back-right
hero_crate(29, 5, 1, 5, 4, 3, "amber")
hero_crate(12, 39, 1, 4, 3, 3, "olive")
hero_crate(17, 39, 1, 4, 3, 3, "slate")
hero_crate(40, 34, 1, 4, 4, 3, "slate")
# note: 5 more heroes live under the lean-to net (above)

# ------------------------------------------------------------ sandbag flanks by the steps
E.sandbag_wall(body, CI, 15, 17, 5, 1, courses=2)
E.sandbag_wall(body, CI, 26, 29, 5, 1, courses=2)

# ------------------------------------------------------------ flagpole (cloth is the separate flag part)
E.pole(body, CI, 36, 37, 18, 29, "timber_dark")

# ------------------------------------------------------------ flag cloth (7x5) with yellow chevron to the hoist
for x in range(29, 36):
    for z in range(24, 29):
        flag[(x, 37, z)] = CI["flag_olive"]
for x, z in ((34, 25), (34, 26), (33, 25), (33, 26),
             (32, 24), (32, 27), (31, 24), (31, 27)):
    flag[(x, 37, z)] = CI["flag_yellow"]

assembled = dict(body)
assembled.update(flag)

PARTS = {"body": body, "flag": flag, "assembled": assembled}


def write_vox(path, vox, palette=PALETTE):
    import struct

    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children

    xs = [p[0] for p in vox]
    ys = [p[1] for p in vox]
    zs = [p[2] for p in vox]
    xoff, yoff = -min(xs), -min(ys)
    sx, sy, sz = max(xs) + xoff + 1, max(ys) + yoff + 1, max(zs) + 1
    xyzi = struct.pack("<i", len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("BBBB", x + xoff, y + yoff, z, ci)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in palette)
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(palette))
    with open(path, "wb") as f:
        f.write(b"VOX ")
        f.write(struct.pack("<i", 150))
        f.write(chunk(b"MAIN", b"", chunk(b"SIZE", struct.pack("<iii", sx, sy, sz))
                      + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)))
    print(f"wrote {path} ({len(vox)} voxels)")


if __name__ == "__main__":
    import json

    print(f"body: {len(body)} voxels, {E.n_components(body)} component(s)")
    print(f"flag: {len(flag)} voxels, {E.n_components(flag)} component(s)")
    print(f"assembled: {len(assembled)} voxels")
    print(f"DOOR_POINT={DOOR_POINT} FOOTPRINT={FOOTPRINT} HEIGHT={HEIGHT} "
          f"FLAG_PIVOT={FLAG_PIVOT}")
    (bb0, bb1) = E.bbox(assembled)
    print(f"assembled bbox: {bb0}..{bb1}")
    if "--viewer-json" in sys.argv:
        print(json.dumps({
            "parts": {
                "body": {"voxels": len(body), "pivot": None},
                "flag": {"voxels": len(flag), "pivot": list(FLAG_PIVOT)},
            },
            "palette_names": [n for n, _ in PALETTE],
            "landmarks": {
                "DOOR_POINT": list(DOOR_POINT),
                "FOOTPRINT": list(FOOTPRINT),
                "HEIGHT": HEIGHT,
                "FLAG_PIVOT": list(FLAG_PIVOT),
            },
        }))
    if "--write-vox" in sys.argv:
        here = os.path.dirname(os.path.abspath(__file__))
        out = os.path.join(here, "out")
        os.makedirs(out, exist_ok=True)
        write_vox(os.path.join(out, "encamp_supply_shack_v1_body.vox"), body)
        write_vox(os.path.join(out, "encamp_supply_shack_v1_flag.vox"), flag)
