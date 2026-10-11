#!/usr/bin/env python3
"""Strike Bay — T-54 road tank (kkolk/strike-bay#248).

A T-54/55 main battle tank on the ZSU v2 chassis: the zsu_aa_v2 hull and
running gear are imported unchanged (same geometry, frame and turret race),
and the tank's own fittings are attached onto that hull. On top sits a low
cast dome turret with a long 100 mm gun, an IR searchlight on the mantlet,
the commander's cupola and a DShK on the loader's hatch with its gunner.
No markings (owner: they do not read in game).

Rig parts, one design frame shared with zsu_aa_v2:

  t54_hull_v1    static: zsu_aa_v2 hull + attachments (rear fuel drums,
                 fender fuel tanks, left exhaust, glacis splash board,
                 spare track links, unditching log)
  zsu2_tracks_v1 reused unchanged (written here too, tread-scroll shader)
  t54_turret_v1  traverse about z at TRAVERSE_PIVOT
  t54_gun_v1     elevation about x at ELEVATION_PIVOT (child of turret);
                 authored at 0 deg pointing +y; IR searchlight rides it
  t54_pintle_v1  traverse about z at PINTLE_PIVOT (child of turret):
                 loader's hatch ring, post, gunner torso (swings with it)
  t54_mg_v1      elevation about x at MG_PIVOT (child of pintle);
                 DShK authored at 0 deg pointing +y
  t54_v1         assembled merge (browsing / reference)

LANDMARK MAP (design coords; the generator prints file coords too)
  Frame: x right (+x = tank's right side), y forward, z up. 0.09 m/voxel.
  Ground under the tracks at z = 0. Hull deck top face at z = 19.
  Front: hull nose y = 76; gun muzzle tip at MUZZLE (y ~ 107).
  Back:  rear plate y = 9; fuel drums reach y = 3.
  Pivots: TRAVERSE_PIVOT, ELEVATION_PIVOT, PINTLE_PIVOT, MG_PIVOT (below).
  Points of interest: MUZZLE (main gun bore exit), MG_MUZZLE (DShK, at
  rest), GUNNER_HEAD, EXHAUST (left fender, rear), CUPOLA (commander).
"""
import os
import zsu_aa_v2 as base
from zsu_aa_v2 import CI, put, box, cyl_x, cyl_y, cyl_z, ring_z, recolor

EXTRA = [
    ("white",    (226, 224, 214)),  # 16 turret number
    ("canvas",   (112, 106, 78)),   # 17 mantlet cover, tarp
    ("skin",     (188, 142, 112)),  # 18 gunner face, hands
    ("uniform",  (86, 92, 62)),     # 19 gunner coveralls
    ("helmet",   (44, 42, 38)),     # 20 padded tanker helmet
    ("wood",     (142, 108, 70)),    # 21 unditching log
    # gunner, styled after infantry_green_v2 (same colours)
    ("inf_jacket",      (60, 68, 36)),     # 22
    ("inf_jacket_dark", (45, 52, 28)),     # 23
    ("inf_epaulette",   (130, 128, 66)),   # 24 shoulder boards, pocket flaps
    ("inf_belt",        (25, 25, 28)),     # 25 belt, collar
    ("inf_skin",        (222, 176, 133)),  # 26
    ("inf_skin_shadow", (166, 132, 100)),  # 27
    ("inf_eyes",        (41, 33, 26)),     # 28
    ("inf_helmet",      (128, 128, 76)),   # 29
    ("inf_helmet_top",  (141, 141, 94)),   # 30
    ("inf_helmet_brim", (102, 102, 61)),   # 31
]
PALETTE = list(base.PALETTE) + EXTRA
for _i, (_n, _) in enumerate(PALETTE):
    CI[_n] = _i + 1

TRAVERSE_PIVOT = base.TRAVERSE_PIVOT       # (17, 42, 19) turret race centre
DECK_Z = base.DECK_Z                       # 19
TCX, TCY = 17, 43                          # dome centre (plan), a hair forward
DOME_RX, DOME_RY, DOME_RZ = 14.0, 12.0, 7.0
DOME_RY_REAR = 14.0                        # egg: long rear overhang
DOME_Z0 = DECK_Z + 1                       # dome sits on a 1-voxel ring
ELEVATION_PIVOT = (17, 53, 24)
BARREL_Z = ELEVATION_PIVOT[2]
MUZZLE = (17, 107, BARREL_Z)
CUPOLA = (11, 40)
EXHAUST = (1, 17, 15)


def dome_top(x, y):
    """Top z (exclusive) of the cast dome at plan cell (x, y), or None."""
    fy = y + 0.5 - (TCY + 0.5)
    dy = fy / (DOME_RY if fy >= 0 else DOME_RY_REAR)
    rx = DOME_RX * (1.0 - 0.1 * max(dy, 0.0))         # a touch narrower forward
    dx = (x + 0.5 - (TCX + 0.5)) / rx
    r2 = dx * dx + dy * dy
    if r2 > 1.0:
        return None
    # low, broad dome: flat-ish crown, steeper flanks
    h = DOME_RZ * (1.0 - r2 ** 1.6) ** 0.55
    return DOME_Z0 + 2 + int(round(h))


HATCH = (23, 43)                           # loader's hatch centre, right of the gun
_ZH = dome_top(*HATCH)                     # dome surface at the hatch
PINTLE_PIVOT = (HATCH[0], HATCH[1], _ZH + 1)   # top of the raised coaming
MG_PIVOT = (HATCH[0], HATCH[1] + 7, _ZH + 5)   # DShK cradle, ahead of the gunner
MG_MUZZLE = (HATCH[0], HATCH[1] + 17, _ZH + 6)
GUNNER_HEAD = (HATCH[0], HATCH[1], _ZH + 10)   # helmet crown
TREAR = int(TCY - DOME_RY_REAR)            # dome rear edge (y)


# ================================================================ HULL + attachments
def hull():
    h = base.hull()
    # --- rear plate: two 200 l drums across the back on brackets
    for (x0, x1) in ((3, 14), (20, 31)):
        cyl_x(h, 5, 17, 3, x0, x1, "olive")
        box(h, x0, x1, 4, 7, 20, 21, "steel")                  # bright painted crown
        for x in (x0, x1 - 1):
            cyl_x(h, 5, 17, 3, x, x + 1, "olive_dark")         # rolled rims
        for x in (x0 + 3, x1 - 4):
            cyl_x(h, 5, 17, 3, x, x + 1, "olive_dark")         # rolling hoops
        put(h, x0 + 1, 5, 18, "steel_dark")                    # bung
        box(h, (x0 + x1) // 2 - 1, (x0 + x1) // 2 + 1, 3, 8, 20, 21, "olive_dark")  # mid hoop
        for x in (x0 + 2, x1 - 3):
            box(h, x, x + 1, 6, 9, 13, 15, "steel_dark")       # bracket arms
            box(h, x, x + 1, 2, 9, 13, 14, "steel_dark")       # cradle strap
    # --- unditching log on the rear, under the drums
    cyl_x(h, 7, 11, 2.0, 1, 33, "wood")
    for x in (1, 32):
        cyl_x(h, 7, 11, 1.5, x, x + 1, "steel")                # chain wraps
    for x in (6, 27):
        box(h, x, x + 1, 7, 9, 10, 13, "steel_dark")           # log brackets
    # --- right fender: three external fuel tanks (rounded, piped)
    for (y0, y1) in ((14, 24), (26, 36), (49, 59)):
        for y in range(y0, y1):
            for (dx, z0, z1) in ((0, 14, 18), (1, 14, 19), (2, 14, 18)):
                box(h, 31 + dx, 32 + dx, y, y + 1, z0, z1, "olive")
        box(h, 31, 34, y0, y0 + 1, 14, 18, "olive_dark")       # end cap shadow
        box(h, 32, 33, y0, y1, 19, 20, "olive_light")          # lit crown
        put(h, 32, (y0 + y1) // 2, 20, "steel_dark")           # filler cap
    box(h, 32, 33, 24, 26, 18, 19, "gunmetal_dark")            # fuel line
    box(h, 32, 33, 36, 49, 18, 19, "gunmetal_dark")
    # --- left fender: exhaust outlet over the track at the rear
    ex, ey, ez = EXHAUST
    box(h, 0, 4, ey - 4, ey + 4, 13, 17, "gunmetal_dark")
    box(h, 0, 1, ey - 3, ey + 3, 14, 16, "dark")               # louvred mouth
    for y in range(ey - 3, ey + 3, 2):
        put(h, 0, y, 15, "gunmetal")
    recolor(h, lambda x, y, z: x == 0 and ey - 4 <= y < ey + 4 and z == 17, "rust")
    # --- glacis: V splash board, spare track links, driver vision
    for i in range(0, 9):
        y = 66 + i // 2
        zt = DECK_Z - (y - 63) * 5 // 13
        for x in (17 - 2 - i, 17 + 2 + i):
            if 1 <= x <= 32:
                put(h, x, y, zt, "olive_light")
                put(h, x, y, zt + 1, "olive_light")
    # headlights: 2x2 lenses in a dark bezel on both front fender corners
    for x0 in (1, 29):
        box(h, x0, x0 + 4, 74, 75, 13, 17, "dark")
        box(h, x0 + 1, x0 + 3, 74, 75, 14, 16, "lamp")
    # entrenching shovel + crowbar on the left front fender
    box(h, 1, 3, 61, 66, 14, 15, "wood")                     # shovel handle
    box(h, 1, 3, 66, 70, 14, 15, "steel")                    # shovel blade (flat)
    box(h, 4, 5, 58, 70, 14, 15, "steel")                    # crowbar
    for x0 in (4, 26):
        for k in range(3):
            y = 71 + k
            zt = DECK_Z - (y - 63) * 5 // 13
            box(h, x0, x0 + 4, y, y + 1, zt, zt + 1, "steel" if k % 2 == 0 else "gunmetal_dark")
    return h


# ================================================================ TURRET (traverse)
def turret():
    t = {}
    px, py, pz = TRAVERSE_PIVOT
    cyl_z(t, px, py, 11, pz, pz + 1, "olive_dark")             # race ring
    ring_z(t, px, py, 11, pz, pz + 1, "gunmetal_dark")
    # cast dome: a 2-voxel collar then the domed shell (solid)
    for x in range(int(TCX - DOME_RX - 1), int(TCX + DOME_RX + 2)):
        for y in range(int(TCY - DOME_RY - 1), int(TCY + DOME_RY + 2)):
            zt = dome_top(x, y)
            if zt is None:
                continue
            for z in range(DOME_Z0, zt):
                put(t, x, y, z, "olive")
    # shade: lower rim dark, crown light (cast texture reads from above)
    for (x, y, z), c in list(t.items()):
        if z == DOME_Z0:
            t[(x, y, z)] = CI["olive_dark"]
    # mantlet opening: flatten the front where the gun cradle sits
    for x in range(12, 23):
        for z in range(DOME_Z0 + 1, DOME_Z0 + 8):
            for y in range(53, 60):
                t.pop((x, y, z), None)
    box(t, 12, 23, 52, 53, DOME_Z0 + 1, DOME_Z0 + 8, "dark")   # embrasure shadow
    # commander's cupola (left rear) with periscopes + small IR lamp
    cx, cy = CUPOLA
    zc = dome_top(cx, cy)
    cyl_z(t, cx, cy, 4, zc - 1, zc + 2, "olive")
    ring_z(t, cx, cy, 4, zc + 1, zc + 2, "olive_dark")
    cyl_z(t, cx, cy, 3, zc + 2, zc + 3, "olive_light")          # hatch lid
    put(t, cx, cy - 2, zc + 3, "steel_dark")                     # hinge
    ring_z(t, cx, cy, 4, zc, zc + 1, "dark")                    # periscope strip
    for (dx, dy) in ((0, 4), (4, 0), (-4, 0)):
        put(t, cx + dx, cy + dy, zc, "glass")                   # vision blocks
    box(t, cx - 1, cx + 2, cy + 4, cy + 6, zc + 1, zc + 3, "steel_dark")
    put(t, cx, cy + 6, zc + 2, "glass")                          # OU-3 lamp lens
    # loader's hatch: raised coaming ring with a dark opening; the lid
    # lies open flat on the roof behind it (clear of the DShK's traverse)
    hx, hy = HATCH
    zh = _ZH
    cyl_z(t, hx, hy, 5, zh - 2, zh, "olive")                  # seat in the dome
    ring_z(t, hx, hy, 5, zh, zh + 1, "olive_dark")             # coaming
    ring_z(t, hx, hy, 4, zh, zh + 1, "olive_dark")
    cyl_z(t, hx, hy, 3.5, zh - 1, zh, "dark")                  # hatch opening
    for x in range(hx - 3, hx + 4):                            # open lid, folded back
        for y in range(hy - 12, hy - 5):
            zt = dome_top(x, y)
            if zt is not None:
                put(t, x, y, zt, "olive_light" if y > hy - 12 else "olive_dark")
    box(t, hx - 2, hx + 3, hy - 6, hy - 5, zh, zh + 1, "steel_dark")  # hinge
    # gunner's sight + vents on the crown, front left of the gun
    zs = dome_top(13, 51)
    box(t, 12, 15, 50, 52, zs - 1, zs + 1, "olive_dark")
    put(t, 13, 52, zs, "glass")
    zv = dome_top(17, 33)
    box(t, 15, 20, 32, 35, zv - 1, zv, "olive_dark")
    for x in (16, 18):
        put(t, x, 33, zv - 1, "dark")
    # stowage on the rear: snorkel tube + tarp roll
    box(t, 9, 22, TREAR - 1, TREAR, DOME_Z0 + 2, DOME_Z0 + 3, "olive_dark")   # snorkel tube
    box(t, 21, 22, TREAR - 1, TREAR, DOME_Z0 + 3, DOME_Z0 + 4, "gunmetal_dark")
    box(t, 10, 21, TREAR, TREAR + 1, DOME_Z0 + 4, DOME_Z0 + 5, "canvas")    # tarp roll
    for x in (10, 20):
        box(t, x, x + 1, TREAR - 1, TREAR + 5, DOME_Z0 + 1, DOME_Z0 + 4, "steel_dark")
    # grab rails along the flanks
    for (gx, s) in ((5, -1), (29, 1)):
        for y in range(36, 49):
            zt = dome_top(gx - s, y)
            if zt:
                put(t, gx, y, zt - 3, "steel_dark")

    # no markings: turret numbers do not read in game (owner)
    return t


DIGITS = {
    "8": ("111", "101", "111", "101", "111"),
    "0": ("111", "101", "101", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
}


def _numbers(t, text="809", y0=34, z_top=DOME_Z0 + 6):
    cols = []
    for ch in text:
        g = DIGITS[ch]
        for c in range(3):
            cols.append([g[r][c] == "1" for r in range(5)])
        cols.append([False] * 5)
    cols.pop()
    for side in (1, -1):
        for i, col in enumerate(cols):
            y = y0 + i if side == 1 else y0 + len(cols) - 1 - i
            for r, on in enumerate(col):
                if not on:
                    continue
                z = z_top - r
                xs = [x for (x, yy, zz) in t if yy == y and zz == z]
                if not xs:
                    continue
                x = max(xs) if side == 1 else min(xs)
                t[(x, y, z)] = CI["white"]


# ================================================================ GUN (elevate)
def gun():
    g = {}
    ex, ey, ez = ELEVATION_PIVOT
    cyl_x(g, ey, ez, 1.5, 11, 24, "steel_dark")                 # trunnion shaft
    # cradle in the embrasure, mantlet with a canvas cover
    box(g, 12, 23, ey - 1, ey + 4, ez - 3, ez + 4, "olive")
    # canvas cover: a wide, low wedge tapering onto the barrel
    for i, y in enumerate(range(ey + 4, ey + 11)):
        hw, hz = max(5 - i // 2, 2), max(3 - i // 2, 2)
        box(g, 17 - hw, 18 + hw, y, y + 1, ez - hz, ez + hz + 1, "canvas")
    for y in (ey + 6, ey + 9):
        box(g, 14, 21, y, y + 1, ez + 2, ez + 3, "olive_dark")     # cover folds
    # 100 mm barrel, bore evacuator two-thirds out, muzzle band
    my = MUZZLE[1]
    cyl_y(g, 17, ez, 1.5, ey + 9, my + 1, "olive")               # 3x3 barrel
    cyl_y(g, 17, ez, 2.0, ey + 9, ey + 14, "olive")              # breech collar
    cyl_y(g, 17, ez, 2.5, my - 17, my - 13, "olive")             # bore evacuator, 1 proud
    cyl_y(g, 17, ez, 2.5, my - 17, my - 16, "olive_dark")
    cyl_y(g, 17, ez, 2.5, my - 14, my - 13, "olive_dark")
    cyl_y(g, 17, ez, 2.0, my - 2, my, "olive_dark")              # muzzle band, 1 proud
    cyl_y(g, 17, ez, 1.5, my, my + 1, "gunmetal_dark")           # muzzle tip
    put(g, 17, my, ez, "dark")                                   # bore
    # lit top line along the barrel
    for y in range(ey + 9, my - 2):
        if (17, y, ez + 1) in g and g[(17, y, ez + 1)] == CI["olive"]:
            g[(17, y, ez + 1)] = CI["olive_light"]
    # L-2 IR searchlight on the right of the mantlet, linked to the gun
    lx, lz = 26, ez + 3
    box(g, 22, 26, ey + 3, ey + 5, ez, ez + 1, "steel_dark")     # link arm
    cyl_y(g, lx, lz, 2.0, ey + 2, ey + 7, "olive")
    cyl_y(g, lx, lz, 2.0, ey + 7, ey + 8, "gunmetal_dark")       # bezel
    cyl_y(g, lx, lz, 1.2, ey + 7, ey + 8, "dark")                # IR filter face
    put(g, lx, ey + 8, lz, "glass")
    box(g, lx, lx + 1, ey + 2, ey + 5, lz - 3, lz - 2, "steel_dark")
    box(g, 24, 27, ey + 3, ey + 4, ez, lz - 2, "steel_dark")      # bracket
    return g


# ================================================================ PINTLE (traverse) + gunner
def pintle():
    """Traverse ring on the coaming, a bracket out to the DShK post, and the
    gunner standing in the hatch, styled after infantry_green_v2 (olive
    jacket, tan shoulder boards and pocket flaps, black collar and belt,
    squared jaw, stern eyes, boxy olive-tan helmet with a brim), scaled to
    the tank's 0.09 m voxel."""
    p = {}
    hx, hy, hz = PINTLE_PIVOT
    mx, my, mz = MG_PIVOT
    for x in range(hx - 5, hx + 6):                            # traverse ring (4-connected band)
        for y in range(hy - 5, hy + 6):
            if 2.5 ** 2 < (x - hx) ** 2 + (y - hy) ** 2 <= 4.2 ** 2:
                put(p, x, y, hz, "gunmetal_dark")
    box(p, hx, hx + 1, hy + 3, my + 1, hz, hz + 1, "steel_dark")  # bracket arm
    box(p, mx, mx + 1, my, my + 1, hz, mz, "steel_dark")       # DShK post
    # --- gunner (rotates with the ring), waist up out of the hatch
    z0 = hz - 1
    box(p, hx - 2, hx + 3, hy - 1, hy + 2, z0, z0 + 1, "inf_jacket_dark")  # in the ring
    box(p, hx - 3, hx + 4, hy - 1, hy + 2, z0 + 1, z0 + 2, "inf_belt")     # belt
    box(p, hx - 4, hx - 3, hy, hy + 1, z0 + 1, z0 + 2, "gunmetal_dark")    # tie to ring
    box(p, hx - 2, hx + 3, hy - 1, hy + 2, z0 + 2, z0 + 6, "inf_jacket")   # jacket
    box(p, hx, hx + 1, hy - 1, hy, z0 + 2, z0 + 6, "inf_jacket_dark")     # back shading
    box(p, hx - 3, hx + 4, hy - 1, hy + 2, z0 + 6, z0 + 7, "inf_jacket")   # shoulder row
    for sx in (hx - 3, hx + 3):
        box(p, sx, sx + 1, hy - 1, hy + 2, z0 + 6, z0 + 7, "inf_epaulette")  # boards
    box(p, hx - 1, hx + 2, hy + 1, hy + 2, z0 + 6, z0 + 7, "inf_belt")    # collar
    for px in (hx - 2, hx + 2):
        put(p, px, hy + 2, z0 + 5, "inf_epaulette")                         # pocket flaps
    # arms forward to the DShK spade grips (grips at my-5..my-3)
    for sx, gx in ((hx - 3, mx - 1), (hx + 3, mx + 2)):
        box(p, sx, sx + 1, hy - 1, hy + 3, z0 + 5, z0 + 6, "inf_jacket")   # upper arm
        lo, hi = min(sx, gx), max(sx, gx)
        box(p, lo, hi + 1, hy + 3, hy + 4, z0 + 5, z0 + 6, "inf_jacket")   # forearm
        put(p, gx, my - 4, z0 + 5, "inf_skin")                              # hand on grip
        box(p, gx, gx + 1, hy + 4, my - 4, z0 + 5, z0 + 6, "inf_jacket")   # wrist reach
    # head: squared jaw, stern eyes
    zf = z0 + 7
    box(p, hx - 1, hx + 2, hy - 1, hy + 2, zf, zf + 3, "inf_skin")
    box(p, hx - 1, hx + 2, hy + 2, hy + 3, zf, zf + 1, "inf_skin")        # jutting jaw
    box(p, hx - 1, hx + 2, hy + 2, hy + 3, zf, zf + 1, "inf_skin_shadow") # jawline
    put(p, hx - 1, hy + 2, zf + 2, "inf_eyes"); put(p, hx + 1, hy + 2, zf + 2, "inf_eyes")
    put(p, hx, hy + 2, zf + 1, "inf_skin")                                 # nose
    # boxy helmet, low over the brow
    box(p, hx - 2, hx + 3, hy - 2, hy + 2, zf + 2, zf + 4, "inf_helmet")
    box(p, hx - 2, hx + 3, hy + 2, hy + 3, zf + 3, zf + 4, "inf_helmet_brim")  # brim lip
    box(p, hx - 1, hx + 2, hy - 1, hy + 2, zf + 4, zf + 5, "inf_helmet_top")   # flat top
    return p


# ================================================================ DShK (elevate)
def mg():
    m = {}
    mx, my, mz = MG_PIVOT
    box(m, mx - 1, mx + 2, my - 1, my + 2, mz, mz + 1, "steel_dark")    # cradle
    box(m, mx, mx + 2, my - 3, my + 3, mz + 1, mz + 3, "gunmetal")      # receiver (2x2)
    box(m, mx, mx + 2, my - 3, my + 3, mz + 3, mz + 4, "gunmetal_dark")  # top cover
    box(m, mx, mx + 2, my - 5, my - 3, mz + 1, mz + 2, "steel_dark")    # spade grips
    box(m, mx - 2, mx, my - 1, my + 2, mz, mz + 3, "olive")             # ammo box (left)
    box(m, mx - 2, mx, my - 1, my + 2, mz + 3, mz + 4, "olive_light")   # box lid
    box(m, mx, mx + 1, my + 3, MG_MUZZLE[1] - 1, mz + 1, mz + 2, "gunmetal")  # barrel
    for y in range(my + 6, my + 10, 2):
        put(m, mx, y, mz + 2, "gunmetal_dark")                            # cooling fins
    box(m, mx, mx + 1, MG_MUZZLE[1] - 1, MG_MUZZLE[1] + 1, mz + 1, mz + 2, "gunmetal_dark")  # brake
    put(m, mx, my + 3, mz + 3, "steel_dark")                              # ring sight
    return m


hull_v = hull()
tracks_v = base.tracks()
turret_v = turret()
gun_v = gun()
pintle_v = pintle()
mg_v = mg()
assembled = {}
for part in (tracks_v, hull_v, turret_v, gun_v, pintle_v, mg_v):
    assembled.update(part)

PARTS = {
    "t54_hull_v1": hull_v,
    "zsu2_tracks_v1": tracks_v,
    "t54_turret_v1": turret_v,
    "t54_gun_v1": gun_v,
    "t54_pintle_v1": pintle_v,
    "t54_mg_v1": mg_v,
    "t54_v1": assembled,
}


if __name__ == "__main__":
    import sys
    if "--viewer-json" in sys.argv[1:]:
        import json
        print(json.dumps({"palette_names": [
            {"index": i + 1, "name": name} for i, (name, _) in enumerate(PALETTE)]}))
        raise SystemExit(0)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "t54")
    os.makedirs(out, exist_ok=True)
    xoff = -min(p[0] for p in assembled); yoff = -min(p[1] for p in assembled)
    f = lambda p: (p[0] + xoff, p[1] + yoff, p[2])
    print(f"frame offset ({xoff},{yoff}); file coords:")
    for name in ("TRAVERSE_PIVOT", "ELEVATION_PIVOT", "PINTLE_PIVOT", "MG_PIVOT",
                 "MUZZLE", "MG_MUZZLE", "GUNNER_HEAD", "EXHAUST"):
        print(f"  {name} {f(globals()[name])}")
    for name, d in PARTS.items():
        base.write_vox(os.path.join(out, name + ".vox"), d, PALETTE, xoff, yoff)
        if name != "t54_v1":
            print(f"  {name}: {base.components(d)} component(s), "
                  f"bbox {tuple(min(p[i] for p in d) for i in range(3))}.."
                  f"{tuple(max(p[i] for p in d) for i in range(3))}")
