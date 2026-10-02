#!/usr/bin/env python3
"""
gunfighter_open_maw_v4.py — Strike Bay "Open Maw" gunfighter, proportions pass.

v4 re-measures the concept sheet (top/side/front orthographic) and rebuilds
the silhouette to match it; finish is deliberately plain (flat greys + the
concept's red lip/nose/tail bands) pending a camo pass.

Measured from the concept sheet (fuselage nose->nozzle = 220 vox):
  - fuselage r 20.5, rounded taper to r 15.5 at the intake lip (not flared)
  - tail tapers to r 16 at the nozzle; nozzle exit y -110
  - narrow canopy (half-width ~6.5) that continues aft as a raised dorsal
    spine all the way to the fin root and a pointed fairing past the nozzle
  - mid wing (z ~ -1), clean 38 deg LE sweep, unswept TE at y -53,
    half-span 107, tip rails
  - tall swept fin: tip z 66, tip TE ~20 vox aft of the nozzle
  - stabilator mid-high (z ~5), half-span 46, swept
  - weapon pods under the wings at |x| 54; twin cannons at |x| ~72

Nine destructible parts, one shared frame. x lateral, y forward (nose +y),
z up. FIGHTER_VOXEL 0.075 m.

Finish variants (same geometry, rig and pivots):
  python3 gunfighter_open_maw_v4.py                 # plain greys -> *-v4.*
  python3 gunfighter_open_maw_v4.py --finish camo   # off-grey camo -> *-v4-camo.*
  python3 gunfighter_open_maw_v4.py --finish jungle # SEA jungle camo -> *-v4-jungle.*
"""
import argparse
import math
import os
import struct
import json

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette
# idx0 unused. Greys + red on the airframe; functional colors elsewhere.
PALETTE = [
    None,
    ("airframe",     (178, 184, 190)),   # 1 main light grey
    ("airframe_mid", (138, 144, 150)),   # 2 tonal grey
    ("panel",        ( 88,  93,  99)),   # 3 hinge lines (dark grey)
    ("red",          (198,  32,  32)),   # 4 markings
    ("groove",       ( 58,  60,  64)),   # 5 vents / cockpit tub
    ("blade",        (205, 210, 216)),   # 6 intake splitter (light)
    ("gunmetal",     ( 48,  50,  54)),   # 7 barrels
    ("bore",         ( 16,  16,  18)),   # 8 intake duct interior (near-black)
    ("canopy",       (150, 200, 232)),   # 9 glass (functional)
    ("pilot",        ( 74,  84,  62)),   # 10 pilot (functional)
    ("helmet",       (210, 210, 208)),   # 11 helmet (functional)
    ("steel",        (118, 123, 129)),   # 12 nozzle
    ("steel_dark",   ( 78,  83,  89)),   # 13 nozzle dark
    ("airframe_lt",  (160, 165, 170)),   # 14 light tonal step
    ("tire",         ( 34,  34,  36)),   # 15 landing-gear tires
    ("camo_light",   (170, 171, 165)),   # 16 warm off-grey
    ("camo_mid",     (134, 140, 142)),   # 17 blue-grey
    ("camo_dark",    ( 99, 105, 110)),   # 18 slate grey
    ("belly",        (192, 196, 198)),   # 19 pale underside
    ("jungle_tan",   (158, 127,  86)),   # 20 SEA tan
    ("jungle_green", ( 92, 102,  58)),   # 21 SEA medium green
    ("jungle_dark",  ( 56,  66,  44)),   # 22 SEA dark green
    ("jungle_belly", (206, 206, 196)),   # 23 light grey underside
]
(A, AM, P, R, G, B, M, O, C, PI, H, S, SD, AL, T,
 CL, CM, CD, BL, JT, JG, JD, JB) = range(1, 24)

parts = {n: {} for n in (
    "core", "canopy", "pilot",
    "wing_l", "wing_r", "guns_l", "guns_r", "fin", "stabilator",
    "gear_nose", "gear_l", "gear_r")}
# optional parts: left out of the in-flight merged model
GEAR_PARTS = ("gear_nose", "gear_l", "gear_r")


def lerp_table(table, v):
    """Piecewise-linear lookup; table is [(key, value)] sorted descending."""
    if v >= table[0][0]:
        return table[0][1]
    for (k0, v0), (k1, v1) in zip(table, table[1:]):
        if k1 <= v <= k0:
            return v0 + (v1 - v0) * (k0 - v) / (k0 - k1)
    return table[-1][1]


# ---------------------------------------------------------------- fuselage
NOSE_Y, TAIL_Y = 110, -110
R_BODY, R_LIP, R_NOZZLE = 20.5, 15.5, 16.0


def fuselage_r(y):
    """Outer radius. Rounded taper into the intake lip at y=110; tail tapers
    to the nozzle at y=-110."""
    if y >= 72:
        t = (NOSE_Y - y) / 38.0               # 0 at lip -> 1 at y 72
        return R_LIP + (R_BODY - R_LIP) * math.sin(t * math.pi / 2)
    if y >= -60:
        return R_BODY
    if y >= -98:
        u = (-60 - y) / 38.0
        return R_BODY - (R_BODY - R_NOZZLE) * (1 - math.cos(u * math.pi)) / 2
    return R_NOZZLE - 0.5 * (-98 - y) / 12.0


def body_d(x, y, z):
    """Normalized radial distance from the fuselage axis (1.0 = skin)."""
    r = fuselage_r(y)
    return math.hypot(x / (r * 0.98), z / r)


core = parts["core"]
SHELL_INNER = 0.86   # ~3 vox shell at r 20.5

for y in range(TAIL_Y, NOSE_Y + 1):
    r = fuselage_r(y)
    ir = int(math.ceil(r)) + 1
    for x in range(-ir, ir + 1):
        for z in range(-ir, ir + 1):
            if SHELL_INNER <= body_d(x, y, z) <= 1.0:
                core[(x, y, z)] = A

# dorsal spine: canopy fairing continues aft to the fin root, ending in a
# pointed fairing past the nozzle. Top height / half-width by station.
SPINE_TOP = [(38, 29.5), (10, 28.5), (-54, 24.0), (-80, 21.5),
             (-105, 20.5), (-118, 18.5)]
SPINE_W = [(38, 6.2), (-54, 5.0), (-80, 3.8), (-105, 3.2), (-118, 0.5)]


def spine_top(y):
    return lerp_table(SPINE_TOP, y)


for y in range(-118, 38):                # canopy part covers y 38..72
    ztop = spine_top(y)
    w = lerp_table(SPINE_W, y)
    if y >= -104:
        zc = fuselage_r(y) * 0.75        # buried in the body
        hz = ztop - zc
        zlo = int(zc)
    else:
        hz = 3.0                         # free-standing bullet tail
        zc = ztop - hz
        zlo = int(math.floor(zc - hz))
    for x in range(-int(w) - 1, int(w) + 2):
        for z in range(zlo, int(ztop) + 1):
            if (x / w) ** 2 + ((z - zc) / hz) ** 2 > 1.0:
                continue
            if y >= TAIL_Y and body_d(x, y, z) < SHELL_INNER:
                continue                 # hollow interior
            core[(x, y, z)] = A

# spine antenna blades (raked)
for y0 in (23, -10):
    zt = int(spine_top(y0))
    for k in range(4):
        for yy in (y0 - k, y0 - k + 1):
            core[(0, yy, zt + k)] = A

# canopy bubble outline (y 38..72): the front of the dorsal spine
CAN_TOP = [(72, 20.5), (66, 26.0), (60, 29.5), (53, 30.5), (38, 29.5)]
CAN_W = [(72, 4.5), (66, 6.2), (53, 6.8), (38, 6.2)]

# cockpit: open the skin under the canopy, line it with a dark tub
CK_Y0, CK_Y1, CK_FLOOR = 40, 70, 11


def ck_w(y):
    """Cockpit opening half-width: tucked inside the canopy sill."""
    return int(lerp_table(CAN_W, y) - 1.5)


for (x, y, z) in list(core):
    if CK_Y0 <= y <= CK_Y1 and abs(x) <= ck_w(y) and z >= CK_FLOOR + 1:
        del core[(x, y, z)]
for y in range(CK_Y0 - 1, CK_Y1 + 2):
    cw = ck_w(min(max(y, CK_Y0), CK_Y1))
    for x in range(-cw - 1, cw + 2):
        top = int(math.sqrt(max(0.0, fuselage_r(y) ** 2 - x * x)))
        wall = abs(x) == cw + 1 or y in (CK_Y0 - 1, CK_Y1 + 1)
        for z in range(CK_FLOOR, top + 1):
            if z == CK_FLOOR or wall:
                core[(x, y, z)] = G

# intake lip: red outer ring, steel inner lip, down to the bore (r 11.5)
for y in range(108, NOSE_Y + 1):
    r = fuselage_r(y)
    for x in range(-17, 18):
        for z in range(-17, 18):
            d = body_d(x, y, z)
            if SHELL_INNER <= d <= 1.0:
                core[(x, y, z)] = R
            elif 11.5 / r <= d < SHELL_INNER:
                core[(x, y, z)] = S

# intake duct: dark backstop disc deep in the maw
for x in range(-20, 21):
    for z in range(-20, 21):
        if body_d(x, 86, z) < SHELL_INNER + 0.02:
            core[(x, 86, z)] = O

# splitter blade: thin vertical divider, recessed behind the lip (dark gunmetal)
for y in range(86, 106):
    for z in range(-20, 21):
        if body_d(0, y, z) < SHELL_INNER + 0.02:
            core[(0, y, z)] = M

# gun vents: dark slots flanking the nose
for sx in (-1, 1):
    for i in range(4):
        y = 92 - i * 3
        x = sx * int(fuselage_r(y) * 0.98)
        for z in range(1, 6):
            for xx in (x, x - sx):
                if (xx, y, z) in core:
                    core[(xx, y, z)] = G

# red bands: second nose band + wide tail band (tail band wraps the spine)
NOSE_BAND = range(96, 101)
TAIL_BAND = range(-86, -70)
for (x, y, z), c in core.items():
    if (y in NOSE_BAND or y in TAIL_BAND) and c == A:
        core[(x, y, z)] = R

# tail nozzle: steel petals at the exit + dark interior disc
for y in range(TAIL_Y, -98):
    r = fuselage_r(y)
    for x in range(-17, 18):
        for z in range(-17, 18):
            d = body_d(x, y, z)
            if SHELL_INNER <= d <= 1.0:
                sector = int((math.degrees(math.atan2(z, x)) % 360) // 15)
                core[(x, y, z)] = S if sector % 2 == 0 else SD
            elif y == -102 and d < SHELL_INNER:
                core[(x, y, z)] = O
for x in range(-17, 18):
    for z in range(-17, 18):
        if 0.8 <= body_d(x, TAIL_Y, z) <= 1.0:
            core[(x, TAIL_Y, z)] = SD

# ---------------------------------------------------------------- canopy + pilot
canopy = parts["canopy"]
pilot = parts["pilot"]
CAN_ZC = 17.0
for y in range(38, 73):
    ztop = lerp_table(CAN_TOP, y)
    w = lerp_table(CAN_W, y)
    hz = ztop - CAN_ZC
    for x in range(-int(w) - 1, int(w) + 2):
        for z in range(int(CAN_ZC), int(ztop) + 1):
            e = math.hypot(x / w, (z - CAN_ZC) / hz)
            if e > 1.0 or e < 0.72:
                continue
            if body_d(x, y, z) <= 1.0 and not (abs(x) <= ck_w(y)
                                              and CK_Y0 <= y <= CK_Y1):
                continue                 # don't overlap the skin
            frame = y in (38, 39, 62, 63) or z <= int(fuselage_r(y)) + 1
            canopy[(x, y, z)] = A if frame else C
# pilot: seat back, torso, helmet
for y in range(44, 47):
    for x in range(-4, 5):
        for z in range(12, 25):
            pilot[(x, y, z)] = G
for y in range(47, 53):
    for x in range(-3, 4):
        for z in range(12, 22):
            pilot[(x, y, z)] = PI
for x in range(-3, 4):
    for y in range(47, 54):
        for z in range(21, 28):
            if x * x + (y - 50) ** 2 + (z - 24) ** 2 <= 7:
                pilot[(x, y, z)] = H

# ---------------------------------------------------------------- wings
WING_ZC = -1
WING_TIP = 107
WING_TE = -53


def wing_le(ix):
    return 34.4 - max(0, ix - 20) * 0.791     # 38 deg sweep


def wing_thick(ix):
    t = max(0.0, (ix - 20) / 87.0)
    return int(round(7 - 4 * t))              # 7 at root -> 3 at tip


def build_wing(side, pname):
    w = parts[pname]
    for ix in range(8, WING_TIP + 1):
        le = int(wing_le(ix))
        thick = wing_thick(ix)
        z0 = WING_ZC - thick // 2
        for iy in range(WING_TE, le + 1):
            for iz in range(z0, z0 + thick):
                # round LE/TE: outer skins stop one short of the edges
                skin = iz in (z0, z0 + thick - 1) and thick > 2
                if skin and (iy == le or iy == WING_TE):
                    continue
                w[(side * ix, iy, iz)] = A
        # flap/aileron hinge line on the top skin
        if 22 <= ix <= WING_TIP - 3:
            w[(side * ix, -42, z0 + thick - 1)] = P
    # aileron/flap split
    for iy in range(WING_TE, -41):
        w[(side * 70, iy, WING_ZC - wing_thick(70) // 2 + wing_thick(70) - 1)] = P
    # wing fence
    fx = 60
    ztop = WING_ZC - wing_thick(fx) // 2 + wing_thick(fx) - 1
    for iy in range(-40, int(wing_le(fx)) - 1):
        for iz in range(ztop + 1, ztop + 3):
            w[(side * fx, iy, iz)] = A
    # tip rail with pointed ends
    for ix in (WING_TIP + 1, WING_TIP + 2):
        for iy in range(-60, -21):
            for iz in (WING_ZC - 1, WING_ZC):
                w[(side * ix, iy, iz)] = A
    for iy in (-61, -21, -20):
        w[(side * (WING_TIP + 1), iy, WING_ZC)] = A


build_wing(-1, "wing_l")
build_wing(1, "wing_r")

# ---------------------------------------------------------------- fin
fin = parts["fin"]
FIN_TIP_Z = 66
for iz in range(19, FIN_TIP_Z + 1):
    le = -54 - max(0, iz - 22) * (54.0 / 44.0)
    te = -99 - (iz - 19) * (29.7 / 47.0)
    chord = le - te
    for iy in range(int(te), int(le) + 1):
        for dx in (-1, 0, 1):
            c = A
            # rudder hinge (aft 30%), above the spine
            if iz >= 26 and int(te + chord * 0.30) == iy:
                c = P
            # tail band continues up the fin root
            if iz <= 26 and -86 <= iy <= -71:
                c = R
            fin[(dx, iy, iz)] = c
# tip fairing rod
for iy in range(-131, -103):
    fin[(0, iy, FIN_TIP_Z + 1)] = A
    fin[(0, iy, FIN_TIP_Z)] = A

# ---------------------------------------------------------------- stabilators
st = parts["stabilator"]
STAB_ZC = 5
for side in (-1, 1):
    for ix in range(0, 47):
        u = max(0.0, (ix - 17) / 29.0)
        le = -69.7 - u * 31.9
        te = -110 - u * 16
        thick = 4 if u < 0.5 else 3
        z0 = STAB_ZC - thick // 2
        hinge = int(te + (le - te) * 0.35)
        for iy in range(int(te), int(le) + 1):
            for iz in range(z0, z0 + thick):
                c = A
                if iy == hinge and iz == z0 + thick - 1 and ix > 18:
                    c = P
                st[(side * ix, iy, iz)] = c
    # tip rod
    for iy in range(-127, -99):
        st[(side * 47, iy, STAB_ZC)] = A
        st[(side * 47, iy, STAB_ZC + 1)] = A

# ---------------------------------------------------------------- guns: pods + cannons
POD_X, POD_ZC = 54, -17.5
CAN_X = (70, 75)
for side, pname in ((-1, "guns_l"), (1, "guns_r")):
    g = parts[pname]
    cx = side * POD_X

    def in_pod(x, z, rx=6.0, rz=6.5):
        return ((x - cx) / rx) ** 2 + ((z - POD_ZC) / rz) ** 2 <= 1.0

    # pod body y -44..12, blunt front taper 12..16, cone tail -44..-50
    for y in range(-50, 17):
        if y > 12:
            k = 1.0 - (y - 12) * 0.08
        elif y < -44:
            k = 1.0 - (-44 - y) * 0.09
        else:
            k = 1.0
        for x in range(cx - 7, cx + 8):
            for z in range(-25, -10):
                if in_pod(x, z, 6.0 * k, 6.5 * k):
                    c = A
                    if y == 16:
                        c = M
                    g[(x, y, z)] = c
    # muzzle grid on the nose plate
    for dx in (-2, 0, 2):
        for mz in (-19, -16):
            g[(cx + dx, 16, mz)] = O
    # side cooling grilles
    for y in range(-30, 6, 4):
        for z in range(-21, -14):
            g[(cx + side * 6, y, z)] = G
    # pylon pod -> wing
    for x in range(cx - 1, cx + 2):
        for y in range(-30, 5):
            for z in range(-11, -1):
                g[(x, y, z)] = A
    # cannon housing under the wing
    hx = side * 72.5
    for x in range(int(hx) - 6, int(hx) + 7):
        for y in range(-28, -5):
            for z in range(-9, -2):
                if ((x - hx) / 5.0) ** 2 + ((z + 5.5) / 3.5) ** 2 <= 1.0:
                    g[(x, y, z)] = A
    # twin barrels, 3x3, with dark bores at the muzzle
    for bx in CAN_X:
        x0 = side * bx
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for y in range(-6, 9):
                    c = SD if y in (0, 7, 8) else M
                    if y == 8 and dx == 0 and dz == 0:
                        c = O
                    g[(x0 + dx, y, -6 + dz)] = c
    # spar buried in the wing slab, ties pylon to housing
    sx0, sx1 = sorted((side * POD_X, side * 72))
    for x in range(sx0, sx1 + 1):
        for y in range(-24, -11):
            for z in (-2, -1):
                g[(x, y, z)] = A

# ---------------------------------------------------------------- landing gear (optional)
# Parked pose: wheels on the ground plane, each leg its own part so it can
# retract about its hinge pivot. Ground clears the pods by ~6 vox.
GROUND_Z = -31
NOSE_GEAR_Y, MAIN_GEAR_Y, MAIN_GEAR_X = 64, -21, 33


def wheel(d, cy, rad, x0, x1, hub=True):
    """Wheel with its axle along x, sitting on the ground plane."""
    cz = GROUND_Z + rad
    for x in range(x0, x1 + 1):
        for y in range(int(cy - rad) - 1, int(cy + rad) + 2):
            for z in range(int(cz - rad) - 1, int(cz + rad) + 2):
                e = math.hypot(y - cy, z - cz)
                if e <= rad:
                    d[(x, y, z)] = S if hub and e <= rad * 0.45 else T


def strut(d, xs, ys, z0, z1, c=M):
    for x in xs:
        for y in ys:
            for z in range(z0, z1 + 1):
                d[(x, y, z)] = c


# nose gear: twin small wheels, single strut up to the belly skin
ng = parts["gear_nose"]
NW = 4                                         # nose wheel radius
wheel(ng, NOSE_GEAR_Y, NW, -5, -3)
wheel(ng, NOSE_GEAR_Y, NW, 3, 5)
strut(ng, range(-5, 6), (NOSE_GEAR_Y,), GROUND_Z + NW, GROUND_Z + NW)  # axle
strut(ng, (-1, 0, 1), (NOSE_GEAR_Y - 1, NOSE_GEAR_Y), GROUND_Z + NW + 1, -21)
strut(ng, (-1, 0, 1), (NOSE_GEAR_Y - 2,), -24, -21, SD)                     # oleo collar
# nose gear doors, hanging open either side of the bay
for sx in (-1, 1):
    strut(ng, (sx * 7,), range(NOSE_GEAR_Y - 7, NOSE_GEAR_Y + 6), -24, -20, A)
strut(ng, range(-6, 7), (NOSE_GEAR_Y,), -21, -21, SD)                       # door link

# main gear: twin wheels per leg, strut up to the wing underside, side-stay
MW = 5                                         # main wheel radius
for side, pname in ((-1, "gear_l"), (1, "gear_r")):
    mg = parts[pname]
    cx = side * MAIN_GEAR_X
    xa, xb = sorted((cx - side * 7, cx - side * 4))   # inboard wheel
    wheel(mg, MAIN_GEAR_Y, MW, xa, xb)
    xa, xb = sorted((cx + side * 4, cx + side * 7))   # outboard wheel
    wheel(mg, MAIN_GEAR_Y, MW, xa, xb)
    strut(mg, range(cx - 7, cx + 8), (MAIN_GEAR_Y,),
          GROUND_Z + MW, GROUND_Z + MW)                # axle
    wing_bot = WING_ZC - wing_thick(MAIN_GEAR_X) // 2 - 1
    strut(mg, (cx - 1, cx, cx + 1), (MAIN_GEAR_Y - 1, MAIN_GEAR_Y),
          GROUND_Z + MW + 1, wing_bot)
    strut(mg, (cx - 1, cx, cx + 1), (MAIN_GEAR_Y + 1,), -20, -17, SD)  # oleo collar
    # side-stay: strut mid-height -> wing underside, inboard
    for k in range(11):
        x = cx - side * k
        z = -15 + k
        if z > wing_bot:
            break
        mg[(x, MAIN_GEAR_Y, z)] = M
        mg[(x, MAIN_GEAR_Y, z - 1)] = M
    # gear door, outboard of the leg, hanging open
    for y in range(MAIN_GEAR_Y - 9, MAIN_GEAR_Y + 8):
        for z in range(-16, wing_bot + 1):
            mg[(cx + side * 3, y, z)] = A
    strut(mg, (cx + side * 2,), (MAIN_GEAR_Y,), -10, -8, SD)                 # door link

# ---------------------------------------------------------------- finish: camo schemes
# Three-tone blob camo on upper surfaces, pale belly. Sampled in the shared
# frame so the pattern runs unbroken across part seams. Only plain airframe
# voxels (A) are repainted; red, glass, metal and hinge lines are kept.
# tones run light -> dark against rising noise; cuts split the noise bands.
CAMO_SCHEMES = {
    # off-grey: small diagonal blobs
    "camo": dict(tones=(CL, CM, CD), cuts=(0.42, 0.58), belly=BL,
                 scale=(30.0, 16.0), angle=35, seed=7),
    # jungle (SEA-style): larger blobs, greens dominant over tan
    "jungle": dict(tones=(JT, JG, JD), cuts=(0.40, 0.53), belly=JB,
                   scale=(38.0, 22.0), angle=20, seed=11),
}


def _hash(ix, iy, iz, seed):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 1442695041)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def _value_noise(u, v, w, seed):
    i, j, k = math.floor(u), math.floor(v), math.floor(w)
    fu, fv, fw = u - i, v - j, w - k
    su, sv, sw = (f * f * (3 - 2 * f) for f in (fu, fv, fw))
    acc = 0.0
    for di, wu in ((0, 1 - su), (1, su)):
        for dj, wv in ((0, 1 - sv), (1, sv)):
            for dk, ww in ((0, 1 - sw), (1, sw)):
                acc += wu * wv * ww * _hash(i + di, j + dj, k + dk, seed)
    return acc


def camo_tone(x, y, z, sch):
    a = math.radians(sch["angle"])
    ca, sa = math.cos(a), math.sin(a)
    long_s, short_s = sch["scale"]
    u = (x * ca + y * sa) / long_s       # long axis
    v = (-x * sa + y * ca) / short_s
    w = z / short_s
    seed = sch["seed"]
    n = (0.7 * _value_noise(u, v, w, seed)
         + 0.3 * _value_noise(u * 2.3, v * 2.3, w * 2.3 + 9.1, seed))
    light, mid, dark = sch["tones"]
    lo, hi = sch["cuts"]
    return light if n < lo else mid if n < hi else dark


def apply_camo(scheme):
    sch = CAMO_SCHEMES[scheme]
    for name, vox in parts.items():
        for (x, y, z), c in vox.items():
            if c != A:
                continue
            below, above = (x, y, z - 1) in vox, (x, y, z + 1) in vox
            underside = (not below and above) or name in GEAR_PARTS
            # fuselage: belly below a wavy line on the flanks
            if name == "core" and z < -0.45 * fuselage_r(y) + 2.5 * math.sin(y / 9.0):
                underside = True
            vox[(x, y, z)] = sch["belly"] if underside else camo_tone(x, y, z, sch)



# ---------------------------------------------------------------- frame / pivots / write
FRAME_LO = (-111, -132, GROUND_Z - 1)
FRAME_HI = (111, 112, 70)
FRAME_SIZE = tuple(h - l + 1 for l, h in zip(FRAME_LO, FRAME_HI))
FRAME_OFF = tuple(-l for l in FRAME_LO)
VOXEL_M = 0.075

PIVOTS = {
    "core": (0, 0, 0),
    "canopy": (0, 55, 26),
    "pilot": (0, 50, 18),
    "wing_l": (-20, -10, WING_ZC),
    "wing_r": (20, -10, WING_ZC),
    "guns_l": (-POD_X, -15, -10),
    "guns_r": (POD_X, -15, -10),
    "fin": (0, -80, 30),
    "stabilator": (0, -95, STAB_ZC),
    # retraction hinges at the strut tops
    "gear_nose": (0, NOSE_GEAR_Y, -21),
    "gear_l": (-MAIN_GEAR_X, MAIN_GEAR_Y, WING_ZC - wing_thick(MAIN_GEAR_X) // 2 - 1),
    "gear_r": (MAIN_GEAR_X, MAIN_GEAR_Y, WING_ZC - wing_thick(MAIN_GEAR_X) // 2 - 1),
}


def write_vox_frame(path, vox):
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children

    sx, sy, sz = FRAME_SIZE
    ox, oy, oz = FRAME_OFF
    for (x, y, z) in vox:
        assert 0 <= x + ox < sx and 0 <= y + oy < sy and 0 <= z + oz < sz, (x, y, z)
    xyzi = struct.pack("<i", len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("BBBB", x + ox, y + oy, z + oz, ci)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for e in PALETTE if e for _, (r, g, b) in [e])
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - (len(PALETTE) - 1))
    main_children = (chunk(b"SIZE", struct.pack("<iii", sx, sy, sz))
                     + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba))
    with open(path, "wb") as f:
        f.write(b"VOX ")
        f.write(struct.pack("<i", 150))
        f.write(chunk(b"MAIN", b"", main_children))
    print(f"wrote {path} ({len(vox)} voxels)")


def bbox_of(vox):
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    return [min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)]


FINISHES = ("plain",) + tuple(CAMO_SCHEMES)
FINISH = "plain"
TAG = "v4"


def main():
    global FINISH, TAG
    ap = argparse.ArgumentParser()
    ap.add_argument("--finish", choices=FINISHES, default="plain")
    FINISH = ap.parse_args().finish
    TAG = "v4" if FINISH == "plain" else f"v4-{FINISH}"
    if FINISH in CAMO_SCHEMES:
        apply_camo(FINISH)
    from preview_camera import render_camera
    manifest_parts = []
    merged = {}
    parked = {}
    for name, vox in parts.items():
        path = os.path.join(OUT, f"gunfighter-{name}-{TAG}.vox")
        write_vox_frame(path, vox)
        manifest_parts.append({
            "name": name,
            "file": os.path.basename(path),
            "pivot": list(PIVOTS[name]),
            "voxels": len(vox),
            "bbox_design": bbox_of(vox),
            "optional": name in GEAR_PARTS,
        })
        if name not in GEAR_PARTS:
            merged.update(vox)
        parked.update(vox)
    mpath = os.path.join(OUT, f"gunfighter-merged-{TAG}.vox")
    write_vox_frame(mpath, merged)
    ppath = os.path.join(OUT, f"gunfighter-merged-parked-{TAG}.vox")
    write_vox_frame(ppath, parked)
    bb = bbox_of(merged)
    manifest = {
        "model": f"gunfighter-open-maw-{TAG}",
        "finish": FINISH,
        "frame": {"x": "lateral (port -x)", "y": "forward (nose +y)",
                  "z": "up, z=0 on the fuselage axis",
                  "size": list(FRAME_SIZE), "offset": list(FRAME_OFF),
                  "voxel_m": VOXEL_M,
                  "length_m": round((bb[4] - bb[1] + 1) * VOXEL_M, 2),
                  "span_m": round((bb[3] - bb[0] + 1) * VOXEL_M, 2)},
        "parts": manifest_parts + [{
            "name": "merged", "file": os.path.basename(mpath),
            "pivot": [0, 0, 0], "voxels": len(merged),
            "bbox_design": bb}, {
            "name": "merged_parked", "file": os.path.basename(ppath),
            "pivot": [0, 0, 0], "voxels": len(parked),
            "bbox_design": bbox_of(parked), "ground_z": GROUND_Z}],
    }
    jpath = os.path.join(OUT, f"pivot_manifest_{TAG}.json")
    with open(jpath, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"wrote {jpath}")

    pal = [p for p in PALETTE if p]
    render_camera(os.path.join(OUT, f"preview_hero_{TAG}.png"), merged, pal,
                  cam_pos=(-95, 215, 85), look_at=(0, 0, 8), scale=5)
    render_camera(os.path.join(OUT, f"preview_side_{TAG}.png"), merged, pal,
                  cam_pos=(-270, -10, 20), look_at=(0, -10, 20), scale=4)
    render_camera(os.path.join(OUT, f"preview_top_{TAG}.png"), merged, pal,
                  cam_pos=(0, -10, 290), look_at=(0, -10, 4), up=(0, 1, 0), scale=4)
    render_camera(os.path.join(OUT, f"preview_nose_{TAG}.png"), merged, pal,
                  cam_pos=(-45, 240, 30), look_at=(0, 95, 0), scale=7,
                  size=(1000, 1000))
    render_camera(os.path.join(OUT, f"preview_front_{TAG}.png"), merged, pal,
                  cam_pos=(0, 270, 20), look_at=(0, 0, 20), scale=5,
                  size=(1500, 1100))
    render_camera(os.path.join(OUT, f"preview_parked_{TAG}.png"), parked, pal,
                  cam_pos=(-150, 170, 10), look_at=(0, 10, -8), scale=5)
    render_camera(os.path.join(OUT, f"preview_parked_front_{TAG}.png"), parked, pal,
                  cam_pos=(0, 270, -5), look_at=(0, 0, -5), scale=5,
                  size=(1500, 1100))


if __name__ == "__main__":
    main()
