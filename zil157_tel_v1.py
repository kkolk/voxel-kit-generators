#!/usr/bin/env python3
"""Strike Bay — ZIL-157 P-15 mobile launcher (TEL), v1 (#421, epic #417).

Fourth ZIL-157 variant, to the OWNER BLUEPRINT
(zil157-p15-mobile-launcher-blueprint): twin elevating launch rails with
two P-15s, a folding radar mast, rear stabiliser legs, platform locking.

Reuses zil157_truck_v2 unchanged: chassis, cab, wheels (front/rear). The
spare is dropped (the mast and the missile noses take its place).

SCALES   coarse TEL_VOXEL = 0.09 m (as the truck body); the P-15 is
         authored at 0.045 m = the truck's fine grid, so a missile drops
         onto the fine assembly 1:1.

Frame (as zil157 v2): z-up, ground z=0, x = width [0,25) centre 12.5,
y = length with the bumper at y=0; forward = file -y.

Every moving part is authored at REST (transport): launcher level,
mast folded back along the bed, legs up.

Parts (coarse unless noted):
  zil157-tel-bed-v1        static: launch platform, pivot trunnions, travel
                           lock, leg housings, mast base, ram mounts
  zil157-tel-launcher-v1   elevates about x through LAUNCH_PIVOT (nose up,
                           0..LAUNCH_ELEV deg): twin rail pairs, cross
                           members, shoes; carries both missiles
  zil157-tel-ram-barrel-l/r-v1  pivot about x at RAM_BASE; aim at RAM_TOP
  zil157-tel-ram-rod-l/r-v1     pivot about x at RAM_TOP (rides the launcher);
                                aim at RAM_BASE
  zil157-tel-mast-v1       folds about x through MAST_PIVOT: rest lies
                           back along the bed (+y); deployed = -90 deg (up)
  zil157-tel-antenna-v1    child of the mast; spins about the mast axis
  zil157-tel-leg-l/r-v1    slide down LEG_TRAVEL voxels to deploy
Missile seats (fine coords, nose tip; axis along -y at rest):
  MISSILE_SEATS

Landmarks (coarse file cells unless noted, for agents without vision):
  FRONT  bumper y=0, cab y 2..34 (forward = -y). BACK  bed/chassis end y=77.
  UP     +z, ground z=0. LEFT = low x (x 0..4 leg-l), RIGHT = high x.
  Missiles ride the launcher NOSE FORWARD (toward the cab): nose tips at
         coarse (4.5, 40, 24.75) and (20.5, 40, 24.75) = fine (9|41, 80,
         49.5); tails toward the rear pivot. Raising the launcher lifts the
         noses (front end) up to 25 deg about the REAR line y=76, z=17;
         missiles fire forward-up over the cab.
  Parts  chassis (v2) x 0..24  y 0..77  z 3..11
         cab (v2)     x 0..24  y 2..34  z 6..26
         bed          x 0..25  y 34..77 z 7..26
         launcher     x 0..24  y 40..79 z 11..24  pivot (y 76, z 17)
         ram barrel   x 3..5 | 19..21  y 50..57 z 15..18  pivot (50, 15.5)
         ram rod      x 4 | 20         y 56..62 z 16      pivot (62, 16.5)
         mast         x 9..15  y 34..64 z 13..19  folded back (+y);
                      hinge (y 36.5, z 16.5), deploy -90 deg -> upright
         antenna      x 11..13 y 65..84 z 12..23  (mast tip, at rest)
         legs         x 0..4 | 20..25  y 68..74  z 6..11; deploy = z -4
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    import zil157_truck_v2 as zil
    import p15_termit_v1 as p15

TEL_VOXEL = zil.TRUCK_VOXEL
PALETTE = list(zil.PALETTE) + [
    ("m_olive",       ( 92,  98,  62)),  # 23 missile (preview only)
    ("m_olive_dark",  ( 66,  71,  45)),  # 24
    ("m_olive_light", (114, 120,  80)),  # 25
    ("m_yellow",      (206, 170,  52)),  # 26
    ("m_radome",      (122, 126,  92)),  # 27
    ("m_booster",     ( 98, 102,  78)),  # 28
    ("m_booster_dk",  ( 80,  84,  64)),  # 29
    ("hazard",        (196, 160,  48)),  # 30 platform hazard edging
    ("deck",          ( 66,  70,  50)),  # 31 platform (darker than the body)
    ("deck_light",    ( 80,  84,  62)),  # 32 tread plate
    ("rod",           (176, 180, 186)),  # 33 polished ram rods
    ("steel_light",   (150, 154, 160)),  # 34
]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

DECK_Z = 14               # platform top
BEAM_BOT, BEAM_TOP = 14, 20   # girder rails at rest (sit on the deck)
MIS_X = (4.5, 20.5)       # missile axes (coarse, continuous)
LAUNCH_PIVOT = (76.0, 17.0)   # (y, z) of the x-axis trunnion line
LAUNCH_ELEV = 25.0
RAM_BASE = (50.0, 15.5)       # (y, z)
RAM_TOP = (62.0, 16.5)        # on the launcher, at rest
MAST_PIVOT = (36.5, 16.5)     # (y, z), x line; mast centre x 12.5
MAST_LEN = 26
LEG_TRAVEL = 4
NOSE_Y = 40.0                 # coarse y of the missile noses at rest


def put(d, x, y, z, c):
    d[(x, y, z)] = CI[c]


def box(d, x0, x1, y0, y1, z0, z1, c):
    for x in range(x0, x1):
        for y in range(y0, y1):
            for z in range(z0, z1):
                put(d, x, y, z, c)


def cyl(d, axis, c0, c1, r, lo, hi, c):
    for a in range(int(c0 - r - 1), int(c0 + r + 2)):
        for b in range(int(c1 - r - 1), int(c1 + r + 2)):
            if (a + 0.5 - c0) ** 2 + (b + 0.5 - c1) ** 2 <= r * r:
                for t in range(lo, hi):
                    p = {"x": (t, a, b), "y": (a, t, b), "z": (a, b, t)}[axis]
                    d[p] = CI[c]


# ================================================================ BED (static)
def bed():
    d = {}
    y0, y1 = 36, 77
    for x0 in (8, 15):
        box(d, x0, x0 + 2, y0, y1, 11, 13, "olive_dark")            # sub-sills on the rails
    for y in range(y0 + 1, y1, 5):
        box(d, 0, 25, y, y + 1, 12, 13, "gunmetal_dark")            # outriggers
    box(d, 0, 25, y0, y1, 13, DECK_Z, "deck")                        # platform deck
    for x in range(0, 25):
        for y in range(y0, y1):
            if (x + y) % 4 == 0:
                put(d, x, y, DECK_Z - 1, "deck_light")               # tread plate
            if y in (y0, y1 - 1):
                put(d, x, y, DECK_Z - 1, "steel")
    for y in range(y0, y1):
        for x in (0, 24):
            put(d, x, y, DECK_Z - 1, "hazard" if (y // 2) % 2 else "dark")   # edge hazard
    for (xa, xb) in ((0, 9), (16, 25)):
        box(d, xa, xb, y0, y0 + 1, DECK_Z, DECK_Z + 3, "olive_dark")    # front coaming
    for x0 in (0, 19):
        box(d, x0, x0 + 6, 45, 72, 12, 13, "olive_dark")             # fenders
    # travel lock (platform locking mechanism): yoke posts over each rail
    # pair's front end, locking bar with a red pin + yellow flag
    for mx in MIS_X:
        cx = int(mx)
        box(d, cx - 4, cx - 3, 37, 39, DECK_Z, BEAM_TOP + 4, "gunmetal")
        box(d, cx + 4, cx + 5, 37, 39, DECK_Z, BEAM_TOP + 4, "gunmetal")
        box(d, cx - 4, cx + 5, 37, 40, BEAM_TOP + 4, BEAM_TOP + 5, "gunmetal_dark")   # locking bar over the stop
        box(d, cx - 4, cx - 3, 36, 37, BEAM_TOP + 1, BEAM_TOP + 3, "red")
        box(d, cx + 4, cx + 5, 36, 37, BEAM_TOP + 1, BEAM_TOP + 3, "red")
        box(d, cx, cx + 2, 37, 38, BEAM_TOP + 5, BEAM_TOP + 7, "hazard")                  # flag
    # rear elevation pivot housing: bulky gunmetal block + trunnion bosses
    py, pz = LAUNCH_PIVOT
    box(d, 0, 25, int(py) - 5, int(py) + 1, DECK_Z, int(pz) - 1, "gunmetal")
    box(d, 0, 25, int(py) - 5, int(py) - 4, DECK_Z, int(pz) - 1, "gunmetal_dark")
    for x0 in (0, 10, 22):
        box(d, x0, x0 + 3, int(py) - 4, int(py) + 1, int(pz) - 1, int(pz) + 2, "gunmetal")
        cyl(d, "x", py - 1.5, pz + 0.5, 1.8, x0, x0 + 3, "gunmetal_dark")
    for x in range(1, 24, 3):
        put(d, x, int(py) - 6, DECK_Z, "hazard"); put(d, x + 1, int(py) - 6, DECK_Z, "dark")   # chevron
    # ram base clevises
    by, bz = RAM_BASE
    for mx in MIS_X:
        cx = int(mx)
        for x in (cx - 2, cx + 2):
            box(d, x, x + 1, int(by) - 2, int(by) + 2, DECK_Z, int(bz) + 2, "gunmetal_dark")
    # stabiliser leg housings + diagonal braces at the rear corners
    for x0 in (0, 21):
        box(d, x0, x0 + 4, 69, 74, 7, DECK_Z, "gunmetal")
        box(d, x0, x0 + 4, 69, 70, 7, DECK_Z, "gunmetal_dark")
        for i in range(0, 5):
            box(d, x0 + 1, x0 + 3, 64 + i, 65 + i, 11 - i, 13 - i, "gunmetal_dark")
    # mast pedestal (gimbal base) + rear mast rest cradle between rail pairs
    my, mz = MAST_PIVOT
    box(d, 10, 15, int(my) - 2, int(my) + 2, DECK_Z, int(mz) - 1, "gunmetal")
    box(d, 9, 16, int(my) - 2, int(my) + 2, DECK_Z, DECK_Z + 1, "gunmetal_dark")
    box(d, 10, 15, int(my) + MAST_LEN - 4, int(my) + MAST_LEN - 2, DECK_Z, DECK_Z + 2, "gunmetal")
    for x in (10, 14):
        box(d, x, x + 1, int(my) + MAST_LEN - 4, int(my) + MAST_LEN - 2, DECK_Z + 2, DECK_Z + 5, "gunmetal")
    # control box + cable reel at the front corners
    box(d, 0, 3, 37, 41, DECK_Z, DECK_Z + 5, "olive")
    box(d, 0, 3, 37, 41, DECK_Z + 5, DECK_Z + 6, "olive_light")
    put(d, 1, 36, DECK_Z + 3, "steel")
    cyl(d, "x", 39.0, DECK_Z + 2.5, 2.5, 21, 25, "gunmetal_dark")
    cyl(d, "x", 39.0, DECK_Z + 2.5, 1.2, 20, 26, "steel_dark")
    # rear bumper + lamp block
    box(d, 2, 23, 77, 78, 9, 12, "gunmetal_dark")
    for x0 in (2, 20):
        box(d, x0, x0 + 3, 77, 78, 11, 13, "red")
    return d


# ================================================================ LAUNCHER (rest = level)
def launcher():
    """Two box-girder rail pairs on a common frame, cradle saddles, tie-down
    straps, trunnion tube, ram lugs, blast deflectors."""
    d = {}
    for mx in MIS_X:
        cx = int(mx)
        for bx in (cx - 4, cx + 2):                                  # girders, 3 wide x 6 deep
            box(d, bx, bx + 3, 40, 80, BEAM_BOT, BEAM_TOP, "steel_dark")
            box(d, bx, bx + 3, 40, 80, BEAM_TOP - 1, BEAM_TOP, "steel")          # running face
            box(d, bx, bx + 3, 40, 80, BEAM_BOT, BEAM_BOT + 1, "steel")          # flange
            ox = bx if bx < cx else bx + 2                                         # outer web face
            for y in range(44, 80, 10):
                box(d, ox, ox + 1, y, y + 1, BEAM_BOT + 1, BEAM_TOP - 1, "steel")   # stiffener rib
                for yy in range(y + 3, y + 7):
                    for zz in (BEAM_BOT + 2, BEAM_BOT + 3):
                        d.pop((ox, yy, zz), None)                                   # lightening slot
        for y in (44, 58, 72):                                       # cradle saddles
            box(d, cx - 4, cx + 5, y, y + 3, BEAM_TOP, BEAM_TOP + 2, "steel")
            for x in (cx - 4, cx + 4):
                box(d, x, x + 1, y, y + 3, BEAM_TOP + 2, BEAM_TOP + 4, "steel")
            put(d, cx - 4, y + 1, BEAM_TOP + 4, "hazard"); put(d, cx + 4, y + 1, BEAM_TOP + 4, "hazard")   # strap eyes
        for y in (50, 64, 78):
            box(d, cx - 1, cx + 2, y, y + 1, BEAM_BOT, BEAM_BOT + 2, "gunmetal_dark")   # cross ties
        box(d, cx - 4, cx + 5, 40, 41, BEAM_TOP, BEAM_TOP + 3, "steel_dark")          # front stop
        box(d, cx - 4, cx + 5, 79, 80, BEAM_BOT - 3 if BEAM_BOT >= 3 else 0, BEAM_BOT, "gunmetal_dark")  # deflector
    for y in (48, 66):                                               # frame girders between pairs
        box(d, int(MIS_X[0]) + 5, int(MIS_X[1]) - 4, y, y + 2, BEAM_BOT, BEAM_BOT + 3, "gunmetal")
    py, pz = LAUNCH_PIVOT
    cyl(d, "x", py - 1.5, pz + 0.5, 1.4, 0, 25, "steel_dark")       # trunnion tube
    ty, tz = RAM_TOP
    for mx in MIS_X:
        box(d, int(mx) - 1, int(mx) + 2, int(ty) - 1, int(ty) + 2, BEAM_BOT, BEAM_BOT + 3, "steel_dark")
        put(d, int(mx), int(ty), BEAM_BOT + 3, "hazard")
    return d


def _bar(d, a, b, frac, x0, w, c, c_top=None):
    """Bar of w x w section from a toward b (y, z), 6-connected."""
    (ay, az), (by_, bz_) = a, b
    n = 60
    prev = None
    for i in range(0, n + 1):
        t = frac * i / n
        y = int(math.floor(ay + (by_ - ay) * t))
        z = int(math.floor(az + (bz_ - az) * t))
        z_lo = min(z, prev) if prev is not None else z
        for zz in range(z_lo, max(z, prev if prev is not None else z) + w):
            for x in range(x0, x0 + w):
                put(d, x, y, zz, c)
        if c_top:
            for x in range(x0, x0 + w):
                put(d, x, y, z + w - 1, c_top)
        prev = z


def ram_barrel(mx):
    d = {}
    _bar(d, RAM_BASE, RAM_TOP, 0.6, int(mx) - 1, 3, "gunmetal", "steel_dark")
    return d


def ram_rod(mx):
    d = {}
    _bar(d, RAM_TOP, RAM_BASE, 0.45, int(mx), 1, "rod")
    return d


# ================================================================ MAST (rest = folded back)
def mast():
    """3x3 lattice mast lying back along the bed between the rail pairs;
    gimbal box at the foot, head plate at the tip."""
    d = {}
    my, mz = MAST_PIVOT
    z0 = int(mz) - 1
    for i in range(0, MAST_LEN):
        y = int(my) + 1 + i
        for (x, z) in ((11, z0), (13, z0), (11, z0 + 2), (13, z0 + 2), (10, z0 + 1), (14, z0 + 1)):
            put(d, x, y, z, "steel")                                  # corner posts
        k = i % 4
        zig = ((12, z0), (13, z0 + 1), (12, z0 + 2), (11, z0 + 1))[k]
        put(d, zig[0], y, zig[1], "steel_dark")                       # lacing
        if i % 8 == 0:
            box(d, 11, 14, y, y + 1, z0, z0 + 3, "steel_dark")        # batten frames
    box(d, 10, 15, int(my) - 2, int(my) + 2, z0 - 1, z0 + 4, "gunmetal")   # gimbal box
    put(d, 10, int(my), z0 + 1, "hazard")
    ty = int(my) + 1 + MAST_LEN
    box(d, 9, 16, ty - 1, ty + 2, z0 - 2, z0 + 5, "gunmetal")        # gimbal head block
    put(d, 9, ty, z0 + 1, "hazard")
    return d


ANT_LEN, ANT_H = 18, 11


def antenna():
    """Open mesh search antenna on the mast head. At rest it stands edge-up
    (plane y-z) between the missiles; it spins about the mast axis."""
    d = {}
    my, mz = MAST_PIVOT
    ty = int(my) + 1 + MAST_LEN + 2
    z0 = int(mz) - 1
    box(d, 12, 13, ty, ty + 2, z0, z0 + 3, "gunmetal_dark")         # spindle
    yc = ty + 2
    for yi in range(0, ANT_LEN):
        for zi in range(0, ANT_H):
            y = yc + yi
            z = z0 - 3 + zi
            frame = yi in (0, ANT_LEN - 1) or zi in (0, ANT_H - 1)
            if frame or yi % 3 == 1 or zi % 3 == 1:
                put(d, 12, y, z, "steel_light" if frame else "gunmetal_dark")
    box(d, 11, 14, yc + ANT_LEN // 2 - 1, yc + ANT_LEN // 2 + 1, z0, z0 + 3, "gunmetal")   # hub
    put(d, 12, yc + ANT_LEN // 2, z0 + ANT_H - 3, "red")
    return d


# ================================================================ LEGS (rest = up)
def leg(x0):
    """3x3 jack column + 6x6 foot pad, retracted into the housing."""
    d = {}
    pad_z = 2 + LEG_TRAVEL                                         # pad bottom at rest
    box(d, x0 + 1, x0 + 3, 70, 73, pad_z + 1, 12, "steel")
    box(d, x0 + 1, x0 + 3, 70, 71, pad_z + 1, 12, "steel_light")
    box(d, x0 - 1 if x0 > 0 else 0, x0 + 5, 68, 75, pad_z, pad_z + 1, "steel_light")     # foot pad
    box(d, x0 + 1, x0 + 3, 68, 69, pad_z + 1, pad_z + 2, "hazard")
    return d


# ================================================================ PREVIEW ROTATIONS
def rot_x(d, pivot_yz, ang_deg, fine=False):
    """Rotate about an x-axis line (pivot (y, z)); nose-up positive for
    parts whose front is -y. Splats 2x2 sub-samples."""
    py, pz = pivot_yz
    a = math.radians(ang_deg)
    ca, sa = math.cos(a), math.sin(a)
    out = {}
    for (x, y, z), c in d.items():
        for oy in (0.25, 0.75):
            for oz in (0.25, 0.75):
                dy, dz = y + oy - py, z + oz - pz
                ny = py + dy * ca + dz * sa
                nz = pz - dy * sa + dz * ca
                out[(x, int(math.floor(ny)), int(math.floor(nz)))] = c
    return out


def missile_fine(seat_x_fine, nose_y_fine, axis_z_fine):
    names = {i + 1: n for i, (n, _) in enumerate(p15.PALETTE)}
    remap = {"olive": "m_olive", "olive_dark": "m_olive_dark", "olive_light": "m_olive_light",
             "yellow": "m_yellow", "radome": "m_radome", "gunmetal": "gunmetal", "dark": "dark",
             "booster": "m_booster", "booster_dark": "m_booster_dk", "steel": "steel", "red": "red"}
    ox = int(math.floor(seat_x_fine - p15.AX + 0.5))
    oz = int(math.floor(axis_z_fine - p15.AZ + 0.5))
    oy = int(math.floor(nose_y_fine + 0.5))
    return {(x + ox, y + oy, z + oz): CI[remap[names[c]]]
            for (x, y, z), c in p15.assembled_stowed.items()}


bed_v = bed()
launcher_v = launcher()
ram_b_v = {}
ram_r_v = {}
for _mx in MIS_X:
    ram_b_v.update(ram_barrel(_mx)); ram_r_v.update(ram_rod(_mx))
mast_v = mast()
antenna_v = antenna()
leg_l_v = leg(0)
leg_r_v = leg(21)
legs_v = {**leg_l_v, **leg_r_v}
AXIS_Z = BEAM_TOP + 0.5 + p15.R * p15.MISSILE_VOXEL / TEL_VOXEL    # coarse
MISSILE_SEATS = [(mx * 2, NOSE_Y * 2, AXIS_Z * 2) for mx in MIS_X]   # fine


def upsample(d):
    out = {}
    for (x, y, z), c in d.items():
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    out[(2 * x + dx, 2 * y + dy, 2 * z + dz)] = c
    return out


def assemble(deployed):
    """Fine-grid assembly; shifted +X_PAD so overhanging tailplanes stay >= 0."""
    out = {}
    base = [zil.chassis_v, zil.cab_v, bed_v]
    for d in base:
        out.update(upsample(d))
    for d in (zil.wheels_front_v, zil.wheels_rear_v):
        out.update(d)
    mis = {}
    for (sx, sy, sz) in MISSILE_SEATS:
        mis.update(missile_fine(sx, sy, sz))
    if deployed:
        piv = LAUNCH_PIVOT
        out.update(upsample(rot_x(launcher_v, piv, LAUNCH_ELEV)))
        out.update(rot_x(mis, (piv[0] * 2, piv[1] * 2), LAUNCH_ELEV))
        # rams: barrel + rod re-aimed between the base and the moved lug
        ty, tz = RAM_TOP
        dy, dz = ty - piv[0], tz - piv[1]
        a = math.radians(LAUNCH_ELEV)
        top = (piv[0] + dy * math.cos(a) + dz * math.sin(a), piv[1] - dy * math.sin(a) + dz * math.cos(a))
        rams = {}
        for mx in MIS_X:
            _bar(rams, RAM_BASE, top, 0.6, int(mx) - 1, 3, "gunmetal", "steel_dark")
            _bar(rams, top, RAM_BASE, 0.45, int(mx), 1, "rod")
        out.update(upsample(rams))
        mp = MAST_PIVOT
        out.update(upsample(rot_x(mast_v, mp, -90)))
        out.update(upsample(rot_x(antenna_v, mp, -90)))
        out.update(upsample({(x, y, z - LEG_TRAVEL): c for (x, y, z), c in legs_v.items()}))
    else:
        for d in (launcher_v, ram_b_v, ram_r_v, mast_v, antenna_v, legs_v):
            out.update(upsample(d))
        out.update(mis)
    pad = 20
    out = {(x + pad, y, z): c for (x, y, z), c in out.items() if z >= 0}
    return out


assembled_transport = assemble(False)
assembled_deployed = assemble(True)

PARTS = {
    "zil157-tel-bed-v1": bed_v,
    "zil157-tel-launcher-v1": launcher_v,
    "zil157-tel-ram-barrel-l-v1": ram_barrel(MIS_X[0]),
    "zil157-tel-ram-barrel-r-v1": ram_barrel(MIS_X[1]),
    "zil157-tel-ram-rod-l-v1": ram_rod(MIS_X[0]),
    "zil157-tel-ram-rod-r-v1": ram_rod(MIS_X[1]),
    "zil157-tel-mast-v1": mast_v,
    "zil157-tel-antenna-v1": antenna_v,
    "zil157-tel-leg-l-v1": leg_l_v,
    "zil157-tel-leg-r-v1": leg_r_v,
    "zil157-tel-assembled-transport-v1": assembled_transport,
    "zil157-tel-assembled-deployed-v1": assembled_deployed,
}


def components(vox):
    return zil.components(vox)


if __name__ == "__main__":
    if "--viewer-json" in sys.argv[1:]:
        import json
        print(json.dumps({"palette_names": [
            {"index": i + 1, "name": name} for i, (name, _) in enumerate(PALETTE)]}))
        raise SystemExit(0)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "zil157_tel_v1")
    os.makedirs(out, exist_ok=True)
    for name, d in PARTS.items():
        zil.write_vox(os.path.join(out, name + ".vox"), d, PALETTE)
        if "assembled" not in name:
            print(f"  {name}: {components(d)} component(s)")
    print("LAUNCH_PIVOT (y,z)", LAUNCH_PIVOT, "LAUNCH_ELEV", LAUNCH_ELEV)
    print("RAM_BASE", RAM_BASE, "RAM_TOP", RAM_TOP, "MAST_PIVOT", MAST_PIVOT, "LEG_TRAVEL", LEG_TRAVEL)
    print("MISSILE_SEATS (fine, nose tip)", MISSILE_SEATS)
