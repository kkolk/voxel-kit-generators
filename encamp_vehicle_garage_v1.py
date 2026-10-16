#!/usr/bin/env python3
"""encamp_vehicle_garage_v1.py — Strike Bay encampment TIMBER set piece: VEHICLE GARAGE.

Landmark map (file coords, z-up, 1 voxel = 0.15 m; origin = pad footprint
min corner at ground level = pad top z=1):
  frame:   x = left/right (left = min x viewed from the front),
           y = depth (FRONT = file -y, min y), z = up.
  front:   fully open shed face at y=16 (2 heavy 2x2 corner posts + chunky
           top beam z18..19, inward knee braces only, 2 glowing lanterns
           hung in front of the beam). NO centre post: the truck nose sticks
           out past the posts. back: dark plank wall at y=56. NO flag in
           the concept: no FLAG_PIVOT, no flag part.
  shed:    outer posts x9..10 / x43..44 (2x2, 0.3 m), front y16..17, back
           y54..55, z1..17; mid side posts y32..33. ridge runs left-right
           (along x) at y35..37, eaves z20, ridge z26, caps z27.
  walls:   back wall x9..44 z1..13 (dark planks, seam every 3, battens);
           side walls rear half planked (y36..53, z2..12) between a bottom
           rail z5 and a mid rail z10, front half open.
  bay:     the shed is EMPTY in game: the game parks a real ZIL-157 in it.
           TRUCK_BAY = truck footprint min corner, nose 11 voxels past the
           front posts (nose faces -y, out the open front, yaw 0 = no
           rotation: the ZIL nose is file -y too). BAY_CLEAR = clear covered
           box over the truck rear; posts, braces, lanterns, shelf and
           crates all stay outside it.
  shelves: back-wall unit x10..15 (uprights + boards z8/z11) with small
           olive / slate / amber boxes.
  lamps:   2 lanterns hung in front of the beam at x14..15 and x36..37
           (y15..16): dark 2x2 cap z17, bright 2x2x2 core z15..16 (#ffc860).
  crates:  hero boxes (>=4x3x3, dark base band + subdued lid + dark
           corners) in olive / slate / amber: a 3x2-base pyramid of 5x4x4
           (6 + 2 + 1) at the front-left outside corner, a 2 wide x 2 high
           block along the right outer wall, 2-high stacks inside left and
           right clear of the bay, 4 separate olive 3x2x3 ammo cans with
           1-voxel gaps by the front-right post.
  roof:    smooth continuous 1-thick camo-net sheet y14..35 / y36..58,
           x7..46 (2 overhang, no height jitter): large irregular flat
           patches (~8 across) in olive / moss / brown / dark-olive, hidden
           timber stitches bridge the slope steps, light-timber rafters
           under every 5th column (tabs to the beams, tails protruding at
           the front eave — rafters show only there), sparse 1-voxel fringe
           every 3rd eave voxel, dark ridge caps along y36.
  floor:   dirt pad with grass border.
  preview: the `preview` dict = body + the real ZIL-157 v2 parts
           (chassis, cab, wheels-front, wheels-rear, bed-covered) resampled
           0.09/0.045 -> 0.15 m and placed at TRUCK_BAY. PREVIEW ONLY: the
           exported body has no truck voxels. The zil_* palette entries are
           preview-only too.

Constants:
  DOOR_POINT = (26, 2, 1)   -- soldiers step out here (pad, before the nose)
  FOOTPRINT  = (53, 63)     -- pad bbox in voxels (7.95 x 9.45 m)
  HEIGHT     = 28           -- ridge cap top voxel z=27
  TRUCK_BAY  = (19, 5, 1, 0) -- ZIL footprint min corner + yaw (nose -y)
  BAY_CLEAR  = ((16, 18, 1), (36, 55, 22)) -- clear box, inclusive
             -- 21 x 38 x 22 voxels = 3.15 x 5.7 x 3.3 m over the truck rear
Parts:
  body -- everything static incl. pad, NO truck (ONE 6-connected component)
  preview -- body + resampled ZIL at TRUCK_BAY (rendering only)
  assembled -- body (rendering; no flag part in this piece)
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import encamp_timber as E

rng = random.Random(670)

BASE_PALETTE = [  # (name, rgb); color index = position + 1
    ("dirt",          (150, 110,  72)),  # 1  pad dirt
    ("dirt_dark",     (118,  84,  54)),  # 2  pad speckle
    ("grass",         (107, 132,  62)),  # 3  pad border
    ("grass_dark",    ( 82, 104,  48)),  # 4  pad border shade
    ("timber",        (122,  88,  54)),  # 5  posts, braces, rafters, ribs
    ("timber_dark",   ( 88,  62,  38)),  # 6  beams, seams, battens
    ("plank",         (158, 124,  80)),  # 7  shelves
    ("plank_dark",    (128,  98,  62)),  # 8  shelf shade
    ("olive",         ( 90, 107,  47)),  # 9  crates + net patch A (#5a6b2f)
    ("olive_dark",    ( 64,  78,  34)),  # 10 crate bands/corners
    ("olive_lite",    (118, 134,  66)),  # 11 crate lids
    ("slate",         ( 74,  80,  88)),  # 12 slate crates
    ("slate_dark",    ( 52,  56,  64)),  # 13 slate bands, ammo can shade
    ("slate_lite",    ( 93, 100, 108)),  # 14 slate lids (#5d646c)
    ("amber",         (168, 118,  58)),  # 15 amber crates
    ("amber_dark",    (128,  86,  42)),  # 16 amber bands
    ("amber_lite",    (198, 150,  84)),  # 17 amber lids
    ("moss",          (110, 122,  58)),  # 18 net patch B (#6e7a3a)
    ("patch_brown",   (107,  85,  52)),  # 19 net patch C (#6b5534)
    ("patch_dark",    ( 63,  74,  36)),  # 20 net patch D (#3f4a24), caps
    ("lamp_glow",     (255, 200,  96)),  # 21 lantern core (#ffc860)
    ("lamp_frame",    ( 60,  50,  36)),  # 22 lantern cap
]
CI = {name: i + 1 for i, (name, _) in enumerate(BASE_PALETTE)}
DOOR_POINT = (26, 2, 1)
FOOTPRINT = (53, 63)
HEIGHT = 28
TRUCK_BAY = (19, 5, 1, 0)
BAY_CLEAR = ((16, 18, 1), (36, 55, 22))

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
E.dirt_pad(body, CI, rng, 0, 53, 0, 63)
for _p in [p for p in body if p[2] == 0]:  # bitten-edge singletons
    _x, _y, _z = _p
    if not any(q in body for q in ((_x + 1, _y, _z), (_x - 1, _y, _z),
                                   (_x, _y + 1, _z), (_x, _y - 1, _z),
                                   (_x, _y, _z + 1))):
        del body[_p]

# ------------------------------------------------------------ posts (2x2 heavy timber, z1..17)
for px in (9, 43):
    for py in (16, 54):
        E.box(body, CI, px, px + 2, py, py + 2, 1, 18, "timber")
for py in (32,):
    for px in (9, 43):
        E.box(body, CI, px, px + 2, py, py + 2, 1, 18, "timber")

# ------------------------------------------------------------ beams + wall plates (z18..19)
E.box(body, CI, 7, 47, 16, 18, 18, 20, "timber_dark")  # front beam (open face)
E.box(body, CI, 7, 47, 54, 56, 18, 20, "timber_dark")  # back beam
E.box(body, CI, 9, 11, 16, 56, 18, 19, "timber_dark")  # left plate
E.box(body, CI, 43, 45, 16, 56, 18, 19, "timber_dark")  # right plate

E.knee(body, CI, 11, 16, 14, 1, 0, 4)    # front-left post, along beam
E.knee(body, CI, 9, 18, 14, 0, 1, 4)     # front-left post, along wall
E.knee(body, CI, 42, 16, 14, -1, 0, 4)   # front-right post, along beam
E.knee(body, CI, 44, 18, 14, 0, 1, 4)    # front-right post, along wall
E.knee(body, CI, 11, 55, 14, 1, 0, 4)    # back-left post, along beam
E.knee(body, CI, 9, 53, 14, 0, -1, 4)    # back-left post, along wall
E.knee(body, CI, 42, 55, 14, -1, 0, 4)   # back-right post, along beam
E.knee(body, CI, 44, 53, 14, 0, -1, 4)   # back-right post, along wall
for px in (9, 43):                       # mid side posts brace along the wall
    E.knee(body, CI, px, 31, 12, 0, -1, 3)
    E.knee(body, CI, px, 34, 12, 0, 1, 3)

# ------------------------------------------------------------ back wall (dark planks, z1..13)
E.shaded_wall(body, CI, 9, 45, 56, 57, 1, 14, base="timber", seam="timber_dark")
for bx in range(11, 45, 6):              # vertical batten boards
    E.box(body, CI, bx, bx + 1, 56, 57, 1, 14, "timber_dark")

# ------------------------------------------------------------ side walls: rails full length, rear half planked
for sx in (9, 43):
    E.box(body, CI, sx, sx + 1, 16, 56, 5, 6, "timber")    # bottom rail
    E.box(body, CI, sx, sx + 1, 16, 56, 10, 11, "timber")  # mid rail
    E.shaded_wall(body, CI, sx, sx + 1, 36, 54, 2, 13,
                  base="timber", seam="timber_dark")       # rear infill

# ------------------------------------------------------------ camo-net gable roof (ridge along x, y35..37 z26)
def roof_z(y):
    if y <= 35:
        return 20 + (y - 14) * 6 // 21
    return 26 - (y - 36) * 6 // 22

RAFTER_XS = list(range(7, 47, 5))

TONES4 = ("olive", "moss", "patch_brown", "patch_dark")


def patch_at(x, y):
    """Large irregular flat-colour patch (~8 across, ragged boundaries)."""
    gx = (x + ((y // 4) % 3) * 2 - 2) // 8
    gy = (y + ((x // 6) % 2) * 4 - 2) // 8
    return TONES4[(gx * 7 + gy * 13) % 4]


for x in range(7, 47):                   # one smooth continuous sheet
    for y in range(14, 59):
        body[(x, y, roof_z(y))] = CI[patch_at(x, y)]
for y in range(15, 59):  # hidden timber stitches bridge slope steps
    if roof_z(y) != roof_z(y - 1):
        for x in range(7, 47):
            if roof_z(y) > roof_z(y - 1):  # ascending: stitch under new row
                body[(x, y, roof_z(y) - 1)] = CI["timber"]
            else:                          # descending: under old row
                body[(x, y - 1, roof_z(y))] = CI["timber"]
for rx in RAFTER_XS:                     # light rafters under the sheet
    for y in range(14, 59):
        body[(rx, y, roof_z(y) - 1)] = CI["timber"]
    for z in range(17, 20):              # connector tabs to the front beam
        body[(rx, 17, z)] = CI["timber"]
    for z in range(17, 22):              # connector tabs to the back beam
        body[(rx, 54, z)] = CI["timber"]
    body[(rx, 13, roof_z(14) - 1)] = CI["timber"]  # protruding tails, front
    body[(rx, 12, roof_z(14) - 1)] = CI["timber"]  # eave: rafters show here
for x in range(7, 47):                   # dark ridge caps
    body[(x, 36, 27)] = CI["patch_dark"]
for x in range(7, 47):                   # sparse 1-voxel fringe, every 3rd
    if x % 3 == 0:
        body[(x, 14, roof_z(14) - 1)] = CI["patch_dark"]
        body[(x, 58, roof_z(58) - 1)] = CI["patch_dark"]

# ------------------------------------------------------------ back-wall shelf unit + small boxes
for ux in (10, 15):
    E.box(body, CI, ux, ux + 1, 54, 56, 1, 13, "plank")  # uprights
E.box(body, CI, 10, 16, 54, 56, 8, 9, "plank")           # shelf boards
E.box(body, CI, 10, 16, 54, 56, 11, 12, "plank")
E.hero_crate(body, CI, 11, 54, 9, 2, 2, 2, OLIVE)
E.hero_crate(body, CI, 13, 54, 9, 2, 2, 2, SLATE)
E.hero_crate(body, CI, 11, 54, 12, 2, 2, 1, AMBER)
E.hero_crate(body, CI, 13, 54, 12, 2, 2, 1, OLIVE)

# ------------------------------------------------------------ 2 lanterns hung in front of the beam
for lx in (14, 36):
    E.box(body, CI, lx, lx + 2, 15, 17, 17, 18, "lamp_frame")  # dark cap
    E.box(body, CI, lx, lx + 2, 15, 17, 15, 17, "lamp_glow")   # warm core

# ------------------------------------------------------------ hero crate stacks
# pyramid, front-left outside corner: 3x2 base of 5x4x4, 2 on top, 1 crown
crate(1, 2, 1, 5, 4, 4, OLIVE)
crate(6, 2, 1, 5, 4, 4, SLATE)
crate(11, 2, 1, 5, 4, 4, AMBER)
crate(1, 6, 1, 5, 4, 4, SLATE)
crate(6, 6, 1, 5, 4, 4, AMBER)
crate(11, 6, 1, 5, 4, 4, OLIVE)
crate(3, 3, 5, 5, 4, 3, AMBER)
crate(8, 3, 5, 5, 4, 3, OLIVE)
crate(5, 3, 8, 5, 4, 3, SLATE)
# right outer wall: 2 wide x 2 high
crate(47, 22, 1, 4, 5, 4, AMBER)
crate(47, 27, 1, 4, 5, 4, OLIVE)
crate(47, 22, 5, 4, 5, 3, SLATE)
crate(47, 27, 5, 4, 5, 3, AMBER)
# inside left + right (clear of the bay): 2 high
crate(11, 38, 1, 4, 4, 4, AMBER)
crate(11, 38, 5, 4, 4, 3, OLIVE)
crate(38, 38, 1, 4, 4, 4, SLATE)
crate(38, 38, 5, 4, 4, 3, AMBER)
# olive ammo cans by the front-right post: 4 separate, 1-voxel gaps
ammo_can(36, 12, 1)
ammo_can(40, 12, 1)
ammo_can(44, 12, 1)
ammo_can(48, 12, 1)

assembled = dict(body)

# ------------------------------------------------------------ preview-only ZIL composite at TRUCK_BAY
ZIL_DIR = "/home/kkolk/src/strike-bay/assets/vox"
ZIL_PARTS = (  # slug, voxel size in m (wheels are a 2x fine grid)
    ("zil157-chassis-v2", 0.09),
    ("zil157-cab-v2", 0.09),
    ("zil157-wheels-front-v2", 0.045),
    ("zil157-wheels-rear-v2", 0.045),
    ("zil157-bed-covered-v2", 0.09),
)
BX, BY, BZ, _YAW = TRUCK_BAY

_zil = {}
_base_rgb = [rgb for _, rgb in BASE_PALETTE]
_extra_rgb = []
_extra_index = {}
for _slug, _vs in ZIL_PARTS:
    _s = _vs / 0.15
    _d, _pal, _size = E.read_vox(os.path.join(ZIL_DIR, _slug + ".vox"))
    for (_x, _y, _z), _ci0 in _d.items():
        _rgb = tuple(_pal[_ci0])
        if _rgb in _base_rgb:
            _ni = _base_rgb.index(_rgb) + 1
        else:
            if _rgb not in _extra_index:
                _extra_index[_rgb] = len(_extra_rgb)
                _extra_rgb.append(_rgb)
            _ni = len(_base_rgb) + _extra_index[_rgb] + 1
        _zil[(math.floor(_x * _s) + BX, math.floor(_y * _s) + BY,
              math.floor(_z * _s) + BZ)] = _ni

preview = dict(body)
preview.update(_zil)

PALETTE = BASE_PALETTE + [("zil_%02d" % i, rgb)
                          for i, rgb in enumerate(_extra_rgb)]

PARTS = {"body": body, "preview": preview, "assembled": assembled}


def write_vox(path, vox, palette=None):
    import struct

    if palette is None:
        palette = BASE_PALETTE

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
    print(f"preview: {len(preview)} voxels ({len(_zil)} zil voxels, "
          f"{len(_extra_rgb)} extra palette entries)")
    print(f"zil placed bbox: {E.bbox(_zil)}")
    print(f"DOOR_POINT={DOOR_POINT} FOOTPRINT={FOOTPRINT} HEIGHT={HEIGHT} "
          f"TRUCK_BAY={TRUCK_BAY} BAY_CLEAR={BAY_CLEAR}")
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
                "TRUCK_BAY": list(TRUCK_BAY),
                "BAY_CLEAR": [list(BAY_CLEAR[0]), list(BAY_CLEAR[1])],
            },
        }))
    if "--write-vox" in sys.argv:
        here = os.path.dirname(os.path.abspath(__file__))
        out = os.path.join(here, "out")
        os.makedirs(out, exist_ok=True)
        write_vox(os.path.join(out, "encamp_vehicle_garage_v1_body.vox"), body)
