#!/usr/bin/env python3
"""Strike Bay — SAM launcher v2: 2K12 Kub (SA-6) style, three missiles on a
traversing, elevating launcher. Two mounts share the launcher:

  tracked   the zsu2 chassis (zsu_aa_v2 hull() + tracks(), imported, same
            design frame) — the Kub rides the same GM chassis family
  fixed     a trailer-type olive box on stabilizer outriggers in a sandbag
            revetment (owner concept); replaces the old fixed
            SamSite (VoxelShapes.sam_site / sam_rack)

Missiles stay the in-game white with red tips (owner), not the concept's
olive.

Rig parts (coarse 0.09 m = TURRET_VOXEL unless noted):

  sa6_turntable_v1  traverse about z at TRAVERSE_PIVOT (tracked) or
                    FIXED_TRAVERSE_PIVOT (fixed pad)
  sa6_launcher_v1   elevation about x at ELEVATION_PIVOT, child of the
                    turntable; authored level, rails along +y; the game
                    pitches it nose-up (Kub fires at ~20-60 deg)
  sa6_missile_v1    FINE grid 0.045 m; one shared missile, placed at each
                    of MISSILE_SEATS as a child of the launcher
  sa6_pad_v1        static fixed-mount base (own file frame, see FIXED_*)
  sa6_hull_v1       static: the zsu2 hull + a raised crew cab (kub_hull())
  tracks            reuse zsu2_tracks_v1.vox as shipped (same file frame)

LANDMARK MAP (design coords; file = design + (FILE_XOFF, FILE_YOFF, 0) for
coarse parts, fine file = 2 * coarse file; printed by the generator):
  frame       x right (+x = vehicle right), y forward (+y = nose), z up
  front/back  hull nose plate y 76, rear plate y 9, exhausts y 7
  hull        x 0..33, y 7..76, z 0..18 (deck top face z 19)
  turntable   lip r12 about (17, 42), low dome to z 25, rear bustle y 26..33,
              trunnion cheeks x 8..9 and 24..25 at y 32..38 (top z 29), ram
              clevises at x 6..9 / 26..29, y 46..49
  rams        barrels pivot on x at (y 47, z 21), x 7..8 and 27..28; rods
              ride the launcher, eye at (y 47, z 26)
  launcher    x 2..32, y 29..63, z 27..39; arms x 5..9 / 15..19 / 25..29
              (rail top face z 30), crossbeams y 33..37 and 56..59, hoop
              guards (inverted U, chamfered) at y 39 and y 55, tops z 39
  crew cab    hull dress, x 3..16, y 55..62, z 19..23 (driver's side, left)
  fixed pad   ground z 0, sandbag U x -10..44 / y 10..69 (open at +y),
              equipment box x 4..30 / y 29..55 roof z 19 = turntable seat,
              outriggers from the box corners to feet ~12 out diagonally
  missiles    nose tips MISSILE_NOSES, tails 88 fine behind; body dia 8 fine
  pivots      TRAVERSE_PIVOT, ELEVATION_PIVOT (axis along x)
  muzzles     the missile nose tips (launch along the launcher's +y)
"""
import math
import os

import zsu_aa_v2 as base
from zsu_aa_v2 import box, cyl_x, cyl_z, put, recolor, write_vox, components

PALETTE = list(base.PALETTE) + [
    ("missile_white", (232, 232, 226)),  # 16 missile body
    ("missile_shade", (176, 178, 176)),  # 17 intakes, wing roots, joints
    ("missile_red",   (196,  38,  34)),  # 18 nose tip
    ("concrete",      (142, 140, 132)),  # 19 pad, walls
    ("concrete_dark", (106, 104,  98)),  # 20 joints, stains, shadow faces
    ("concrete_lite", (168, 166, 158)),  # 21 wall caps
    ("earth",         (104,  88,  62)),  # 22 ground
    ("sandbag",       (170, 152, 112)),  # 23 revetment bags
    ("sandbag_dark",  (128, 112,  80)),  # 24 bag seams
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}
base.CI.update(CI)          # the shared primitives look colours up in base.CI

TRAVERSE_PIVOT = base.TRAVERSE_PIVOT            # (17, 42, 19)
ELEVATION_PIVOT = (17, 35, 28)                  # x-axis, rear of the turntable
RAIL_X = (7, 17, 27)                            # rail centre columns
RAIL_TOP = 30                                   # rail top face (z)
TAIL_Y = 20                                     # missile tail plane (coarse)
MIS_LEN = 104                                   # fine voxels, 4.7 m
MIS_R = 5                                       # fine body radius (dia 10)

# fixed pad: pier top sits FIXED_DROP below the chassis deck
FIXED_DROP = 0
FIXED_TRAVERSE_PIVOT = (TRAVERSE_PIVOT[0], TRAVERSE_PIVOT[1], TRAVERSE_PIVOT[2] - FIXED_DROP)


# ================================================================ HULL (Kub dress)
def kub_hull():
    """The zsu2 hull with a raised crew cab forward of the turntable (vision
    blocks across its face, two hatches) for the Kub's stepped silhouette."""
    h = dict(base.hull_v)
    z0 = base.DECK_Z
    CX0, CX1 = 3, 17                                              # driver's side
    box(h, CX0, CX1, 55, 63, z0, z0 + 4, "olive")
    box(h, CX0, CX1, 55, 63, z0 + 4, z0 + 5, "olive_light")       # roof
    box(h, CX0 + 1, CX1 - 1, 56, 62, z0 + 4, z0 + 5, "olive")
    box(h, CX0, CX1, 55, 56, z0, z0 + 4, "olive_dark")            # rear face
    box(h, CX0 + 3, CX0 + 11, 62, 63, z0 + 2, z0 + 3, "glass")    # vision strip
    box(h, CX0 + 2, CX0 + 9, 57, 61, z0 + 5, z0 + 6, "olive_dark")  # hatch
    put(h, CX0 + 8, 60, z0 + 6, "steel_dark")
    return h


# ================================================================ TURNTABLE
RAM_X = (7, 27)                       # ram columns, under the outer rails
RAM_Y = 47
RAM_BASE_Z = 21                       # barrel clevis on the turntable lip
RAM_TOP_Z = 26                        # rod eye under the launcher arm


def turntable():
    t = {}
    px, py, pz = TRAVERSE_PIVOT
    cyl_z(t, px, py, 12, pz, pz + 1, "olive_dark")              # bearing skirt
    cyl_z(t, px, py, 12, pz + 1, pz + 2, "olive_light")         # lit lip rim
    cyl_z(t, px, py, 11, pz + 1, pz + 2, "olive")
    for (r, z, c) in ((10.5, pz + 2, "olive"), (10, pz + 3, "olive"), (9, pz + 4, "olive"),
                      (8, pz + 5, "olive_light"), (6, pz + 6, "olive_light")):
        cyl_z(t, px, py, r, z, z + 1, c)                        # low dome
    for a in range(16):
        ang = a * math.pi / 8
        put(t, round(px + 11.5 * math.cos(ang)), round(py + 11.5 * math.sin(ang)), pz, "steel_dark")
    # rear electronics bustle and a hatch on the dome
    box(t, 12, 23, 26, 34, pz + 1, pz + 5, "olive")
    box(t, 12, 23, 26, 34, pz + 5, pz + 6, "olive_light")
    box(t, 12, 23, 26, 27, pz + 1, pz + 2, "olive_dark")
    for x in (14, 17, 20):
        box(t, x, x + 1, 25, 26, pz + 2, pz + 5, "dark")         # cooling slots
    for a in range(12):                                          # dome seam ring
        ang = a * math.pi / 6
        put(t, round(px + 8.6 * math.cos(ang)), round(py + 8.6 * math.sin(ang)), pz + 4, "olive_dark")
    # trunnion cheeks: plate uprights on the dome carrying the elevation axis
    ex, ey, ez = ELEVATION_PIVOT
    for (x0, x1) in ((8, 10), (24, 26)):
        for z in range(pz + 1, ez + 2):
            half = 3 if z < ez - 2 else 2
            box(t, x0, x1, ey - half, ey + half + 1, z, z + 1, "olive")
        box(t, x0, x1, ey - 3, ey + 4, pz + 1, pz + 2, "olive_dark")
        cyl_x(t, ey, ez, 1, x0, x1, "steel_dark")                # bearing cap
    box(t, 8, 26, ey - 3, ey + 4, pz + 1, pz + 2, "olive")       # cheek feet
    for rx in RAM_X:                                            # ram clevises
        box(t, rx - 1, rx + 3, RAM_Y - 1, RAM_Y + 3, pz + 1, RAM_BASE_Z + 1, "olive_dark")
    return t


def ram_barrel(rx):
    """Pivots about (RAM_Y, RAM_BASE_Z) on x; the game aims it at the rod."""
    d = {}
    box(d, rx, rx + 2, RAM_Y, RAM_Y + 2, RAM_BASE_Z + 1, RAM_TOP_Z - 1, "gunmetal")
    box(d, rx, rx + 2, RAM_Y, RAM_Y + 2, RAM_BASE_Z + 1, RAM_BASE_Z + 2, "gunmetal_dark")
    return d


def ram_rod(rx):
    """Rides the launcher (child of the elevation node)."""
    d = {}
    put(d, rx, RAM_Y, RAM_TOP_Z - 1, "steel")
    put(d, rx, RAM_Y, RAM_TOP_Z, "steel_dark")                  # rod eye
    return d


# ================================================================ LAUNCHER
def launcher():
    L = {}
    ex, ey, ez = ELEVATION_PIVOT
    cyl_x(L, ey, ez, 1.5, 10, 24, "steel_dark")                 # trunnion shaft
    box(L, 2, 33, ey - 2, ey + 3, ez - 1, ez + 1, "olive_dark")  # rear crossbeam
    box(L, 2, 33, 56, 60, ez - 1, ez + 1, "olive_dark")         # front crossbeam
    for x in (2, 32):                                           # side stringers
        box(L, x, x + 1, ey - 2, 60, ez - 1, ez + 1, "olive_dark")
    for rx in RAIL_X:
        box(L, rx - 2, rx + 3, 29, 64, ez - 1, RAIL_TOP, "olive")       # launcher arm
        box(L, rx - 2, rx + 3, 29, 64, ez - 1, ez, "olive_dark")         # underside
        box(L, rx, rx + 1, 29, 64, RAIL_TOP - 1, RAIL_TOP, "gunmetal")   # guide slot
        for y in (31, 52):
            box(L, rx - 1, rx + 2, y, y + 2, RAIL_TOP, RAIL_TOP + 1, "steel_dark")  # shoes
        box(L, rx - 2, rx + 3, 63, 64, ez - 1, RAIL_TOP, "olive_dark")          # arm cap
        for y in (40, 48):
            put(L, rx - 2, y, ez + 1, "steel_dark"); put(L, rx + 2, y, ez + 1, "steel_dark")
    # olive brace plates between the arms, rear and mid, so the rows read
    for (bx0, bx1) in ((RAIL_X[0] + 3, RAIL_X[1] - 2), (RAIL_X[1] + 3, RAIL_X[2] - 2)):
        box(L, bx0 + 1, bx1 - 1, 29, 64, RAIL_TOP - 1, RAIL_TOP, "olive_dark")   # gap strip
        for y in (32, 45):
            box(L, bx0, bx1, y, y + 5, ez - 1, RAIL_TOP, "olive_dark")
            box(L, bx0, bx1, y, y + 5, RAIL_TOP, RAIL_TOP + 1, "olive_dark")
    # hoop guards: thin inverted U tubes over the missiles, 3-voxel chamfers
    for hy in (39, 55):
        for (x, sx) in ((2, 1), (32, -1)):
            box(L, x, x + 1, hy, hy + 1, ez - 1, 36, "olive")
            for k in range(1, 4):
                put(L, x + sx * k, hy, 35 + k, "olive")
                put(L, x + sx * k, hy, 34 + k, "olive")
        box(L, 5, 30, hy, hy + 1, 38, 39, "olive")
        box(L, 5, 30, hy, hy + 1, 39, 40, "olive_light")
    for (x, lx) in ((2, 5), (32, 29)):
        box(L, lx, lx + 1, 40, 55, 39, 40, "olive_light")       # top longerons
        for i in range(9):                                      # rear diagonal brace
            put(L, x, 38 - i, 35 - i, "olive_dark")
            put(L, x, 38 - i, 34 - i, "olive_dark")
    return L


# ================================================================ MISSILE (fine grid)
OGIVE = MIS_LEN - 26        # ogive start (t)


def _radius(t):
    if t < 2:
        return MIS_R - 1.5                                      # nozzle
    if t < OGIVE:
        return MIS_R
    f = (t - OGIVE) / (MIS_LEN - OGIVE)
    return max(0.6, MIS_R * math.sqrt(max(0.0, 1.0 - f * f)))   # ogive


def missile():
    """Fine-grid missile, nose toward +y. Axis at (0,0) in x/z offsets of
    +0.5 (an even 8-voxel disc), tail at t=0."""
    m = {}
    half = 0.5
    for t in range(MIS_LEN):
        r = _radius(t)
        for x in range(-7, 7):
            for z in range(-7, 7):
                dx, dz = x + half, z + half
                if dx * dx + dz * dz <= r * r:
                    c = "missile_white"
                    if t < 2:
                        c = "dark"
                    elif t >= MIS_LEN - 13:
                        c = "missile_red"
                    elif t in (36, 37, 70):
                        c = "missile_shade"                     # section joints
                    m[(x, t, z)] = CI[c]
    # X-config surfaces: mid wings and tail fins, 2 voxels thick on the diagonal
    def fin(t0, t1, tip0, tip1, span):
        for t in range(t0, t1):
            for s in range(MIS_R - 1, span + 1):
                if not (tip0 <= t < tip1) and s > MIS_R + (span - MIS_R) * 0.45:
                    continue
                for sx in (-1, 1):
                    for sz in (-1, 1):
                        for w in (0, 1):
                            x = int(math.floor(sx * s / math.sqrt(2) + half)) - (w if sx > 0 else 0)
                            z = int(math.floor(sz * s / math.sqrt(2) + half)) - (0 if sx > 0 else w)
                            c = "missile_shade" if s >= span - 1 or t in (t0, t1 - 1) else "missile_white"
                            m.setdefault((x, t, z), CI[c])
    fin(44, 70, 52, 64, 12)                                     # wings
    fin(2, 16, 4, 12, 13)                                        # tail fins
    # four ramjet intakes on the + axes, cheek ducts running aft
    for t in range(26, 52):
        for (x, z) in ((0, 5), (-1, 5), (0, -6), (-1, -6), (5, 0), (5, -1), (-6, 0), (-6, -1)):
            m[(x, t, z)] = CI["missile_shade"] if t > 26 else CI["dark"]
    for (x, z) in ((0, 5), (-1, 5), (0, -6), (-1, -6), (5, 0), (5, -1), (-6, 0), (-6, -1)):
        m[(x, 51, z)] = CI["dark"]                                  # intake mouth
    return m


def _seat(rx):
    """Fine-grid placement offset: missile local (0,0,0) -> fine design."""
    fx = rx * 2 + 1              # even disc (centre at local x 0.0) on coarse column rx's centre
    fz = RAIL_TOP * 2 + MIS_R    # body bottom on the rail top
    fy = TAIL_Y * 2
    return (fx, fy, fz)


MISSILE_SEATS = [_seat(rx) for rx in RAIL_X]                    # fine, tail centre
MISSILE_NOSES = [(sx, sy + MIS_LEN - 1, sz) for (sx, sy, sz) in MISSILE_SEATS]


def placed_missile(seat):
    sx, sy, sz = seat
    return {(x + sx, y + sy, z + sz): c for (x, y, z), c in missile_v.items()}


# ================================================================ FIXED MOUNT
def _sandbag_row(p, cells, z, phase):
    """Lay one course of bags along a list of (x, y) cells; bags 4 long with
    a dark seam between, staggered by `phase` per course."""
    for i, (x, y) in enumerate(cells):
        seam = (i + phase) % 4 == 0
        put(p, x, y, z, "sandbag_dark" if seam else "sandbag")


def pad():
    """Trailer-type fixed mount on bare earth inside a sandbag revetment:
    an olive equipment box (the turntable rides its roof), four splayed
    stabilizer outriggers to ground pads, a cable coil and ammo crates."""
    p = {}
    px, py, pz = FIXED_TRAVERSE_PIVOT                            # box roof z 19
    X0, X1, Y0, Y1 = -10, 45, 10, 76
    box(p, X0, X1, Y0, Y1, 0, 1, "earth")                        # ground plate
    for (x, y) in ((X0 + 9, Y0 + 7), (X1 - 6, Y1 - 9), (X0 + 15, Y1 - 5), (X1 - 13, Y0 + 12),
                   (X0 + 4, Y0 + 30), (X1 - 4, Y0 + 40)):
        box(p, x, x + 2, y, y + 3, 0, 1, "olive_dark")           # scrub tufts
    # revetment: 4 courses of chunky bags (2 voxels high, 4 thick), stepping
    # in a voxel per course, on three sides; open front with short returns
    W = 4
    def bag(x, y, z, along, course):
        seam = (along + 3 * course) % 6 == 0
        top = z % 2 == 0
        put(p, x, y, z, "sandbag_dark" if seam else ("sandbag" if top else "sandbag"))
    for course in range(4):
        ins = course
        for z in (1 + 2 * course, 2 + 2 * course):
            for y in range(Y0, Y1 - 6):
                for x in range(X0 + ins, X0 + W + ins):
                    bag(x, y, z, y, course)
                for x in range(X1 - W - ins, X1 - ins):
                    bag(x, y, z, y, course)
            for x in range(X0, X1):
                for y in range(Y0 + ins, Y0 + W + ins):
                    bag(x, y, z, x, course)
            if course < 2:
                for (x0, x1) in ((X0, X0 + 10), (X1 - 10, X1)):
                    for x in range(x0, x1):
                        for y in range(Y1 - 6, Y1 - 2):
                            bag(x, y, z, x, course)
    # bag bottoms read as a darker seam line under each course
    for (x, y, z), c in list(p.items()):
        if c == CI["sandbag"] and z % 2 == 1 and z > 1 and (x, y, z + 1) in p:
            p[(x, y, z)] = CI["sandbag_dark"] if (x + y) % 3 == 0 else c
    # equipment box: the trailer body, turntable on its roof
    BX0, BX1, BY0, BY1 = px - 13, px + 14, py - 13, py + 14
    box(p, BX0, BX1, BY0, BY1, 1, pz - 1, "olive")
    box(p, BX0, BX1, BY0, BY1, pz - 1, pz, "olive_light")        # roof
    box(p, BX0, BX1, BY0, BY1, 1, 2, "olive_dark")               # skirt
    box(p, BX0 + 1, BX1 - 1, BY0 + 1, BY1 - 1, pz - 1, pz, "olive")
    cyl_z(p, px, py, 9, pz - 1, pz, "gunmetal_dark")             # bearing seat
    # panel doors: two per long side, one on each end, with handles
    for (fx, ox) in ((BX0, BX0 - 1), (BX1 - 1, BX1)):
        for (y0, y1) in ((BY0 + 2, BY0 + 11), (BY0 + 14, BY1 - 2)):
            box(p, fx, fx + 1, y0, y1, 3, pz - 3, "olive_dark")
            box(p, fx, fx + 1, y0 + 1, y1 - 1, 4, pz - 4, "olive")
            put(p, ox, y1 - 2, 8, "steel_dark")                  # handle
    for (fy, oy) in ((BY0, BY0 - 1), (BY1 - 1, BY1)):
        box(p, BX0 + 3, BX1 - 3, fy, fy + 1, 3, pz - 3, "olive_dark")
        box(p, BX0 + 4, BX1 - 4, fy, fy + 1, 4, pz - 4, "olive")
        for x in range(BX0 + 5, BX1 - 5, 2):
            put(p, x, oy, pz - 6, "dark")                        # louvres
        put(p, px, oy, 8, "steel_dark")
    # stabilizer outriggers: I-beams from the box corners down to pads
    for (sx, sy, cx, cy) in ((-1, -1, BX0, BY0), (1, -1, BX1 - 1, BY0),
                             (-1, 1, BX0, BY1 - 1), (1, 1, BX1 - 1, BY1 - 1)):
        for i in range(12):
            x, y = cx + sx * i, cy + sy * i
            z = 8 - (i * 2) // 3
            for (xx, yy) in ((x, y), (x + sx, y), (x, y + sy), (x + sx, y + sy)):
                put(p, xx, yy, z, "olive_light")
                put(p, xx, yy, max(1, z - 1), "olive_dark")
        fx, fy = cx + sx * 12, cy + sy * 12
        box(p, min(fx - sx, fx + 3 * sx), max(fx - sx, fx + 3 * sx) + 1,
            min(fy - sy, fy + 3 * sy), max(fy - sy, fy + 3 * sy) + 1, 1, 2, "steel_dark")   # foot
        box(p, min(fx, fx + 2 * sx), max(fx, fx + 2 * sx) + 1,
            min(fy, fy + 2 * sy), max(fy, fy + 2 * sy) + 1, 2, 3, "gunmetal")    # jack
    # cable coil, ammo crates, jerrycan, shovel, dirt speckle
    cx0, cy0 = px + 17, py + 20
    for x in range(cx0 - 5, cx0 + 6):
        for y in range(cy0 - 5, cy0 + 6):
            if 6 <= (x - cx0) ** 2 + (y - cy0) ** 2 <= 22:
                put(p, x, y, 1, "dark")
                put(p, x, y, 2, "steel" if (x - cx0) ** 2 + (y - cy0) ** 2 >= 16 else "gunmetal_dark")
    for i, (x, y) in enumerate(((px - 22, py + 10), (px - 22, py + 15), (px - 17, py + 13))):
        c, lid = ("olive_dark", "olive") if i != 1 else ("sandbag_dark", "sandbag")
        box(p, x, x + 4, y, y + 3, 1, 4, c)
        box(p, x, x + 4, y, y + 3, 4, 5, lid)
        put(p, x + 2, y + 3, 3, "steel_dark")
    box(p, px + 16, px + 18, py - 18, py - 15, 1, 5, "olive")    # jerrycan
    put(p, px + 17, py - 18, 5, "steel_dark")
    box(p, px - 6, px - 5, py + 21, py + 26, 1, 2, "rust")       # shovel haft
    box(p, px - 7, px - 4, py + 26, py + 29, 1, 2, "steel_dark")  # blade
    import random
    rng = random.Random(464)
    for _ in range(40):
        x, y = rng.randrange(X0 + 5, X1 - 5), rng.randrange(Y0 + 5, Y1)
        if p.get((x, y, 1)) is None and p.get((x, y, 0)) == CI["earth"]:
            p[(x, y, 0)] = CI["rust"] if rng.random() < 0.6 else CI["olive_dark"]
    return p


# ---------------------------------------------------------------- assembly
def upsample(d):
    out = {}
    for (x, y, z), c in d.items():
        for i in (0, 1):
            for j in (0, 1):
                for k in (0, 1):
                    out[(2 * x + i, 2 * y + j, 2 * z + k)] = c
    return out


def drop(d, dz):
    return {(x, y, z - dz): c for (x, y, z), c in d.items()}


turntable_v = turntable()
launcher_v = launcher()
missile_v = missile()
pad_v = pad()
hull_v = kub_hull()
tracks_v = base.tracks_v

top_coarse = {}
top_coarse.update(turntable_v); top_coarse.update(launcher_v)
for rx in RAM_X:
    top_coarse.update(ram_barrel(rx)); top_coarse.update(ram_rod(rx))
missiles_fine = {}
for s in MISSILE_SEATS:
    missiles_fine.update(placed_missile(s))

tracked_coarse = {}
for part in (tracks_v, hull_v, top_coarse):
    tracked_coarse.update(part)
assembled = upsample(tracked_coarse)
assembled.update(missiles_fine)

fixed_coarse = dict(pad_v)
fixed_coarse.update(drop(top_coarse, FIXED_DROP))
fixed_assembled = upsample(fixed_coarse)
fixed_assembled.update(drop(missiles_fine, 2 * FIXED_DROP))
missile_view = missile_v

# zsu2's own file offset, so these parts composite with the shipped hull/tracks
FILE_XOFF = -min(p[0] for p in base.assembled)
FILE_YOFF = -min(p[1] for p in base.assembled)

PARTS_COARSE = {"sa6_hull_v1": hull_v, "sa6_turntable_v1": turntable_v, "sa6_launcher_v1": launcher_v}
for i, rx in enumerate(RAM_X):
    side = "l" if i == 0 else "r"
    PARTS_COARSE[f"sa6_ram_barrel_{side}_v1"] = ram_barrel(rx)
    PARTS_COARSE[f"sa6_ram_rod_{side}_v1"] = ram_rod(rx)

if __name__ == "__main__":
    import sys
    if "--viewer-json" in sys.argv[1:]:
        import json
        print(json.dumps({"palette_names": [
            {"index": i + 1, "name": name} for i, (name, _) in enumerate(PALETTE)]}))
        raise SystemExit(0)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "sa6")
    os.makedirs(out, exist_ok=True)
    f = lambda p: (p[0] + FILE_XOFF, p[1] + FILE_YOFF, p[2])
    print(f"file offset ({FILE_XOFF},{FILE_YOFF}) == zsu2's")
    print("TRAVERSE_PIVOT file", f(TRAVERSE_PIVOT), "ELEVATION_PIVOT file", f(ELEVATION_PIVOT))
    for name, d in PARTS_COARSE.items():
        write_vox(os.path.join(out, name + ".vox"), d, PALETTE, FILE_XOFF, FILE_YOFF)
        print(f"  {name}: {components(d)} component(s)")
    # the missile file: its own frame, tail-centre origin at file (12, 0, 12)
    m = {(x, y, z + 12): c for (x, y, z), c in missile_v.items()}
    write_vox(os.path.join(out, "sa6_missile_v1.vox"), m, PALETTE, 12, 0)
    print(f"  sa6_missile_v1: {components(missile_v)} component(s); local origin (tail centre) "
          f"= missile file (12,0,12) - 0.5 in x/z; nose tip file y {MIS_LEN - 1}")
    print("MISSILE_SEATS fine design (tail origin):", MISSILE_SEATS)
    print("MISSILE_SEATS fine file:", [(sx + 2 * FILE_XOFF, sy + 2 * FILE_YOFF, sz) for (sx, sy, sz) in MISSILE_SEATS])
    print("MISSILE_NOSES fine file:", [(sx + 2 * FILE_XOFF, sy + 2 * FILE_YOFF, sz) for (sx, sy, sz) in MISSILE_NOSES])
    pxo = -min(p[0] for p in pad_v); pyo = -min(p[1] for p in pad_v)
    write_vox(os.path.join(out, "sa6_pad_v1.vox"), pad_v, PALETTE, pxo, pyo)
    print(f"  sa6_pad_v1: {components(pad_v)} component(s); pad file offset ({pxo},{pyo}); "
          f"FIXED_TRAVERSE_PIVOT pad file {(FIXED_TRAVERSE_PIVOT[0] + pxo, FIXED_TRAVERSE_PIVOT[1] + pyo, FIXED_TRAVERSE_PIVOT[2])}")
