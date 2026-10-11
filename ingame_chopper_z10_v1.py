#!/usr/bin/env python3
"""Player attack helicopter v3 (Z-10 style), built natively at game voxel scale.

Replaces the Apache v2 (ingame_chopper_apache_v2.py) on the same voxel size
(0.042 m) and roughly the same length (~130 voxels nose to fin), so the
game's scale couplings (wash, hitbox, unit heights, camera) carry over.

Look (owner concept, strike-bay .claude/workspace/chopper2-concept.jpg):
slender slab-sided fuselage, stepped tandem glasshouse (gunner low in
front, pilot high behind) with framed flat panes, green nose with a chin
sensor turret, single-barrel chin cannon, shoulder engine nacelles with
round intakes and out-turned exhausts, tall mast with a mast-mounted
radar dome above a 5-blade main rotor, swept fin with a starboard
X ("scissor") tail rotor, boom stabiliser, ventral fin + tail wheel,
fixed main wheels, stub wings with an inner 19-tube rocket pod and an
outer 4-round ATGM rack per side. Sand tan base with large green patches.

LANDMARK MAP (design voxels; the generator prints these)
  Frame: x lateral, +x = RIGHT (starboard); y forward, +y = NOSE; z up,
         wheels touch z = 0. Rotor mast axis at x = 0, y = 0.
  Front: nose tip ~ (0, 56, 19); chin sensor lens front (0, 57.0, 15.25).
  Back:  fin trailing edge ~ y -80; tail rotor hub TAIL_HUB.
  Parts (one shared frame; file = design + PARTS_FILE_OFFSET):
    body      fuselage, canopy wells + crew, nacelles, mast + radar dome,
              wings, pods, ATGM racks, gear, fin, stabiliser. Static.
    canopy    glass panes (canopy_glass) + frames. Static, translucent.
    gun       chin cannon turret; yaws about z at GUN_PIVOT, barrel +y.
    tailrotor X tail rotor; spins about x at TAIL_HUB.
    rotor     5-blade main rotor + hub; spins about z at ROTOR_HUB.
              Hub has a hole the static mast passes through to the dome.
  Joints: rotor hub rings the mast at z ROTOR_Z; tail rotor shaft meets
          the fin gearbox at x = 3; gun ring sits under the chin at z 13.5.
  Points: POD_MUZZLES (rocket pod faces), ATGM_MUZZLES (missile noses),
          SMOKE (between nacelle exhausts), SENSOR_LENS, CREW seats.
Needs numpy.
"""
import os
import sys
import json
import math
import struct
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ingame_chopper_apache_v2 import CREW_BUST, CREW_KEY  # shared crew bust (viewer #24)


def c8(v):
    return int(v * 255.0 + 0.5)


PALETTE = [
    ("tan",          (200, 178, 128)),
    ("tan_light",    (222, 202, 152)),
    ("tan_dark",     (160, 140, 98)),
    ("green",        (96, 122, 74)),
    ("green_light",  (118, 146, 92)),
    ("green_dark",   (66, 86, 52)),
    ("canopy_glass", (c8(0.55), c8(0.80), c8(0.95))),   # == game CHOPPER_GLASS
    ("gunmetal",     (c8(0.30), c8(0.31), c8(0.34))),
    ("dark",         (c8(0.22), c8(0.23), c8(0.27))),
    ("cockpit",      (c8(0.12), c8(0.12), c8(0.14))),
    ("black",        (c8(0.10), c8(0.10), c8(0.12))),
    ("steel",        (150, 154, 160)),
    ("rotor_blade",  (92, 96, 102)),
    ("rotor_tip",    (60, 62, 68)),
    ("rubber",       (c8(0.13), c8(0.13), c8(0.15))),
    ("red_light",    (c8(0.86), c8(0.16), c8(0.12))),
    ("green_light_nav", (c8(0.20), c8(0.80), c8(0.30))),
    ("lens",         (40, 60, 70)),
    ("soft_black",   (c8(0.17), c8(0.18), c8(0.21))),
    # crew colours, copied from infantry-green-v2 (viewer #24)
    ("crew_jacket",       (60, 68, 36)),
    ("crew_jacket_dark",  (45, 52, 28)),
    ("crew_trouser",      (55, 62, 34)),
    ("crew_tan",          (130, 128, 66)),
    ("crew_skin",         (222, 176, 133)),
    ("crew_skin_shadow",  (166, 132, 100)),
    ("crew_eyes",         (41, 33, 26)),
    ("crew_helmet",       (128, 128, 76)),
    ("crew_helmet_top",   (141, 141, 94)),
    ("crew_helmet_brim",  (102, 102, 61)),
]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

# ------------------------------------------------------------------ grid
X0, Y0, Z0 = -62, -98, 0
NX, NY, NZ = 124, 160, 74
PARTS_FILE_OFFSET = (-X0, -Y0, -Z0)


class Layer:
    def __init__(self):
        self.a = np.zeros((NX, NY, NZ), np.uint8)

    def _grid(self, bb):
        x0, x1, y0, y1, z0, z1 = bb
        x0, y0, z0 = max(int(math.floor(x0)), X0), max(int(math.floor(y0)), Y0), max(int(math.floor(z0)), Z0)
        x1, y1, z1 = min(int(math.ceil(x1)), X0 + NX), min(int(math.ceil(y1)), Y0 + NY), min(int(math.ceil(z1)), Z0 + NZ)
        sl = (slice(x0 - X0, x1 - X0), slice(y0 - Y0, y1 - Y0), slice(z0 - Z0, z1 - Z0))
        X = (np.arange(x0, x1, dtype=float) + 0.5)[:, None, None]
        Y = (np.arange(y0, y1, dtype=float) + 0.5)[None, :, None]
        Z = (np.arange(z0, z1, dtype=float) + 0.5)[None, None, :]
        return sl, X, Y, Z

    def paint(self, bb, fn, color, empty_only=False, only=None):
        sl, X, Y, Z = self._grid(bb)
        sub = self.a[sl]
        m = np.broadcast_to(fn(X, Y, Z), sub.shape)
        if empty_only:
            m = m & (sub == 0)
        if only is not None:
            m = m & np.isin(sub, [CI[c] for c in only])
        sub[m] = CI[color] if isinstance(color, str) else color

    def full(self):
        X = (np.arange(X0, X0 + NX, dtype=float) + 0.5)[:, None, None]
        Y = (np.arange(Y0, Y0 + NY, dtype=float) + 0.5)[None, :, None]
        Z = (np.arange(Z0, Z0 + NZ, dtype=float) + 0.5)[None, None, :]
        return [np.broadcast_to(v, self.a.shape) for v in (X, Y, Z)]


# ------------------------------------------------------------------ shapes
def rcyl_y(xc, zc, r, y0, y1, rr_f=0.0, rr_b=0.0):
    """cylinder along y with rounded ends (front = y1, back = y0)"""
    def fn(X, Y, Z):
        rho = np.sqrt((X - xc) ** 2 + (Z - zc) ** 2)
        lim = np.full(np.broadcast(rho, Y).shape, float(r))
        if rr_f > 0:
            t = np.clip(Y - (y1 - rr_f), 0, None)
            lim = np.minimum(lim, r - rr_f + np.sqrt(np.maximum(rr_f ** 2 - t ** 2, 0)))
        if rr_b > 0:
            t = np.clip((y0 + rr_b) - Y, 0, None)
            lim = np.minimum(lim, r - rr_b + np.sqrt(np.maximum(rr_b ** 2 - t ** 2, 0)))
        return (rho <= lim) & (Y >= y0) & (Y <= y1)
    return (xc - r - 1, xc + r + 1, y0 - 1, y1 + 1, zc - r - 1, zc + r + 1), fn


def cyl_x(yc, zc, r, x0, x1):
    def fn(X, Y, Z):
        return ((Y - yc) ** 2 + (Z - zc) ** 2 <= r * r) & (X >= x0) & (X <= x1)
    return (x0 - 1, x1 + 1, yc - r - 1, yc + r + 1, zc - r - 1, zc + r + 1), fn


def cyl_z(xc, yc, r, z0, z1, r_in=None):
    def fn(X, Y, Z):
        d2 = (X - xc) ** 2 + (Y - yc) ** 2
        m = (d2 <= r * r) & (Z >= z0) & (Z <= z1)
        if r_in is not None:
            m &= d2 > r_in * r_in
        return m
    return (xc - r - 1, xc + r + 1, yc - r - 1, yc + r + 1, z0 - 1, z1 + 1), fn


def ball(c, r, sx=1.0, sy=1.0, sz=1.0):
    cx, cy, cz = c
    def fn(X, Y, Z):
        return ((X - cx) / (r * sx)) ** 2 + ((Y - cy) / (r * sy)) ** 2 + ((Z - cz) / (r * sz)) ** 2 <= 1.0
    return (cx - r * sx - 1, cx + r * sx + 1, cy - r * sy - 1, cy + r * sy + 1,
            cz - r * sz - 1, cz + r * sz + 1), fn


def box(x0, x1, y0, y1, z0, z1):
    def fn(X, Y, Z):
        return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1) & (Z >= z0) & (Z <= z1)
    return (x0 - 1, x1 + 1, y0 - 1, y1 + 1, z0 - 1, z1 + 1), fn


def capsule(p0, p1, r):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    d = p1 - p0
    dd = float(d @ d)
    def fn(X, Y, Z):
        px, py, pz = X - p0[0], Y - p0[1], Z - p0[2]
        t = np.clip((px * d[0] + py * d[1] + pz * d[2]) / dd, 0, 1)
        dx, dy, dz = px - t * d[0], py - t * d[1], pz - t * d[2]
        return dx * dx + dy * dy + dz * dz <= r * r
    lo = np.minimum(p0, p1) - r - 1
    hi = np.maximum(p0, p1) + r + 1
    return (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]), fn


# ------------------------------------------------------------------ key dims (voxels)
ROTOR_Z = 54.0
ROTOR_HUB = (0.0, 0.0, ROTOR_Z)
ROTOR_R = 60.0
DOME_C, DOME_R = (0.0, 0.0, 60.5), 5.2
TR_X = 5.0                                  # starboard tail rotor plane
TAIL_HUB = (TR_X, -77.0, 57.0)
TR_R = 13.0
GUN_PIVOT = (0.0, 42.0, 13.5)
GUN_TIP_Y = 60.0
NAC_X, NAC_R, NAC_Z = 10.0, 5.0, 40.5
NAC_Y0, NAC_Y1 = -28.0, -2.0
WING_Z = 22.0
POD_X, POD_ZC = 12.5, 15.5
ATGM_X, ATGM_ZC = 22.5, 15.5
GUNNER_SILL, PILOT_SILL = 26.0, 32.0
CABIN_POST_Y = 22.5
# canopy top profile (y, z): rear fairing, pilot roof, pilot windshield,
# gunner roof, gunner windshield down to the nose
# Apache v2 canopy profile, stretched to the longer nose and lowered with
# the leaner deck: rear fairing, pilot roof, pilot windshield, gunner
# roof, gunner windshield down to the nose
CAN_PY = [4.0, 7.0, 16.0, 22.0, 30.0, 45.0]
CAN_PZ = [41.0, 44.0, 44.0, 38.0, 37.0, GUNNER_SILL]
CAN_HW0, CAN_LEAN = 6.5, 0.16
CAMO_SEED = 11
GREEN_SHARE = 0.08


def place_crew(L, y0, z_top, z_min):
    for i, rows in enumerate(CREW_BUST):
        z = z_top - i
        if z < z_min:
            break
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ".":
                    L.a[dx - 4 - X0, y0 + dy - Y0, z - Z0] = CI[CREW_KEY[ch]]


# fuselage loft: y, top z, bottom z, half width
FUS_Y = [-72, -62, -48, -36, -26, -14, 4, 4.5, 22, 22.5, 26, 38, 44, 49, 53, 56]
FUS_T = [30, 31, 33, 36, 39, 40, 40, 32, 32, 26, 26, 26, 25, 23, 21, 19.5]
FUS_B = [25, 24, 22, 20, 17, 15, 14, 14, 14, 14, 14, 14.5, 15, 16, 17, 18]
FUS_W = [2.0, 2.6, 3.2, 4.0, 5.2, 6.4, 6.6, 6.4, 6.2, 6.0, 5.8, 5.2, 4.4, 3.5, 2.6, 1.8]


def fus_fn(X, Y, Z):
    w = np.interp(Y, FUS_Y, FUS_W)
    top = np.interp(Y, FUS_Y, FUS_T)
    bot = np.interp(Y, FUS_Y, FUS_B)
    zc, hz = (top + bot) / 2, np.maximum((top - bot) / 2, 0.01)
    u = (Z - zc) / hz
    # slab sides leaning in above the waist, chamfered below it
    wz = w * np.where(u > 0, 1.0 - 0.30 * u, 1.0 - 0.35 * np.clip((-u - 0.45) / 0.55, 0, 1))
    return (np.abs(X) <= wz) & (np.abs(u) <= 1.0) & (Y >= FUS_Y[0]) & (Y <= FUS_Y[-1])


def build_body(L):
    L.paint((-8, 8, FUS_Y[0], FUS_Y[-1], 10, 47), fus_fn, "tan")

    # ---- cockpit wells, seats, crew (seen through the glass) -------------
    L.paint(*box(-5, 5, 24, 43, 25, 26.6), "cockpit")                 # gunner floor
    L.paint(*box(-4, 4, 41, 43, 26, 29), "dark")                      # gunner coaming
    L.paint(*box(-5, 5, 5, 22, 31, 32.6), "cockpit")                  # pilot floor
    L.paint(*box(-5, 5, 20, 22.9, 25, 32.6), "cockpit")               # step face
    L.paint(*box(-4, 4, 18, 20, 32, 35), "dark")                      # pilot coaming
    place_crew(L, 27, 34, int(GUNNER_SILL))
    place_crew(L, 9, 42, int(PILOT_SILL))

    # ---- spine and engine deck --------------------------------------------
    L.paint(*box(-4, 4, -26, 4, 39, 41.5), "tan")                      # spine
    for s in (-1, 1):
        xc = s * NAC_X
        # saddle under the pod only, so the pod reads as its own barrel
        L.paint(*box(min(s * 3, s * 8), max(s * 3, s * 8), NAC_Y0 + 3, NAC_Y1 - 3, 34, 38.5), "tan")
        # concept nacelle in three sections: rounded intake bullet with a
        # side mesh screen, boxy green midsection, round rear barrel
        L.paint(*rcyl_y(xc, NAC_Z, NAC_R - 0.5, NAC_Y1 - 9, NAC_Y1 + 1, 5.0, 0), "tan")
        def mesh(X, Y, Z, xc=xc, s=s):
            out = (X - xc) * s
            return ((out > 1.5) & (np.abs(Z - NAC_Z) < 3.2) & (Y > NAC_Y1 - 8) & (Y < NAC_Y1 - 2)
                    & ((np.floor(Y) + np.floor(Z)) % 2 == 0))
        L.paint((xc - 6, xc + 6, NAC_Y1 - 9, NAC_Y1, NAC_Z - 4, NAC_Z + 4), mesh, "tan_dark", only=["tan"])
        def boxy(X, Y, Z, xc=xc):
            dx, dz = np.abs(X - xc), np.abs(Z - NAC_Z)
            return ((dx <= 5.0) & (dz <= 5.5) & (dx + dz <= 9.2)
                    & (Y >= NAC_Y0 + 3) & (Y <= NAC_Y1 - 8))
        L.paint((xc - 6, xc + 6, NAC_Y0 + 5, NAC_Y1 - 7, NAC_Z - 6, NAC_Z + 6), boxy, "green")
        L.paint(*rcyl_y(xc, NAC_Z, NAC_R - 0.8, NAC_Y0, NAC_Y0 + 7, 0, 1.0), "tan")
        p0 = (xc, NAC_Y0 + 2, NAC_Z + 0.5)
        p1 = (s * (NAC_X + 2.2), NAC_Y0 - 3.5, NAC_Z + 1.2)
        L.paint(*capsule(p0, p1, 3.4), "tan")
        p2 = (s * (NAC_X + 3.0), NAC_Y0 - 5.5, NAC_Z + 1.6)
        L.paint(*capsule(p1, p2, 3.1), "dark")                           # angled nozzle
        L.paint(*capsule(p2, (s * (NAC_X + 3.3), NAC_Y0 - 6.3, NAC_Z + 1.7), 2.8), "steel")   # flared rim
        L.paint(*capsule((s * (NAC_X + 3.2), NAC_Y0 - 6.0, NAC_Z + 1.7),
                         (s * (NAC_X + 3.6), NAC_Y0 - 7.2, NAC_Z + 1.8), 1.6), "black")    # mouth
        # access panel outline on the box's outer face
        L.paint(*box(min(s * (NAC_X + 3.6), s * (NAC_X + 5)), max(s * (NAC_X + 3.6), s * (NAC_X + 5)),
                     -19, -11, NAC_Z - 3.5, NAC_Z + 2.5), "green_dark", only=["green"])
        L.paint(*box(min(s * (NAC_X + 3.6), s * (NAC_X + 5)), max(s * (NAC_X + 3.6), s * (NAC_X + 5)),
                     -18, -12, NAC_Z - 2.5, NAC_Z + 1.5), "green", only=["green_dark"])

    # ---- mast, swashplate, radar dome --------------------------------------
    L.paint(*box(-5, 5, -9, 8, 40, 44), "tan")                          # mast fairing
    L.paint(*box(-3.5, 3.5, -6, 5, 44, 47), "tan")
    L.paint(*cyl_z(0, 0, 3.0, 47, 49.5), "gunmetal")                     # swashplate housing
    L.paint(*cyl_z(0, 0, 1.8, 47, 57.5), "steel")                        # mast through the hub
    L.paint(*ball(DOME_C, DOME_R, 1, 1, 0.75), "green")
    L.paint(*cyl_z(0, 0, DOME_R + 0.1, DOME_C[2] - 0.5, DOME_C[2] + 0.5), "green_dark",
            only=["green"])                                             # seam band

    # ---- nose: sensor turret, cone, lights -----------------------------------
    L.paint(*box(-5, 5, 44, 58, 14, 30), "green", only=["tan"])          # green nose cap
    L.paint(*ball((0, 52.0, 15.0), 4.2), "green")                        # chin sensor turret
    L.paint(*box(-2, 2, 54.5, 57, 13.5, 17), "lens")                     # sensor window
    L.paint(*box(-1, 1, 55.5, 57.1, 14.5, 16), "black")
    L.paint(*ball((0, 53.0, 21.5), 1.5), "dark")                         # pilot sight

    # ---- belly keel, avionics cheeks ------------------------------------------
    L.paint(*box(-2, 2, -20, 40, 13, 14.5), "tan_dark", empty_only=True)
    for s in (-1, 1):
        L.paint(*rcyl_y(s * 5.0, 18.0, 2.2, 2, 38, 3.0, 3.0), "tan")

    # ---- stub wings -----------------------------------------------------------
    for s in (-1, 1):
        def wing(X, Y, Z, s=s):
            ax = np.abs(X)
            le = 0.0 - (ax - 5) * 0.30
            te = -15.0 - (ax - 5) * 0.02
            zc = WING_Z - (ax - 5) * 0.08
            le = le - np.clip(ax - 25, 0, None) * 1.2          # chamfered outer front corner
            return ((ax >= 4) & (ax <= 28) & (Y <= le) & (Y >= te) &
                    (np.abs(Z - zc) <= 1.0) & (X * s > 0))
        wb = (min(s * 3, s * 30), max(s * 3, s * 30), -18, 2, 18, 28)
        L.paint(wb, wing, "tan")
        L.paint(wb, lambda X, Y, Z, s=s: wing(X, Y, Z, s) & ~wing(X, Y + 1.5, Z, s), "tan_dark")
        L.paint(*box(min(s * 4, s * 8), max(s * 4, s * 8), -13, 0, 21, 26), "tan")     # root fairing
        tx, tz = s * 28.5, WING_Z - 23 * 0.08
        L.paint(*box(tx - 1, tx + 1, -13, -6, tz - 2.5, tz + 1.5), "tan")             # tip fairing
        L.paint(*box(tx - 1, tx + 1, -6.5, -5.5, tz - 1, tz + 1), "red_light" if s < 0 else "green_light_nav")

        # inner hardpoint: 19-tube rocket pod
        px = s * POD_X
        wz = WING_Z - (POD_X - 5) * 0.08 - 1.0
        L.paint(*box(px - 1, px + 1, -12, -3, POD_ZC + 3, wz), "gunmetal")            # pylon
        L.paint(*rcyl_y(px, POD_ZC, 4.2, -17, 2, 1.2, 2.5), "green")                   # pod body
        L.paint(*rcyl_y(px, POD_ZC, 4.2, 1, 2.5, 0, 0), "green_dark")                  # front rim
        L.paint(*rcyl_y(px, POD_ZC, 4.2, -9, -8, 0, 0), "green_dark")                  # strap
        inside = lambda X, Z, px=px: ((X - px) ** 2 + (Z - POD_ZC) ** 2) <= 3.3 ** 2
        def tube(X, Y, Z, px=px):
            cx, cz = np.floor(X - px), np.floor(Z - POD_ZC)
            return inside(X, Z) & (Y >= 1.5) & (Y <= 2.5) & ((cx + cz) % 2 == 0)
        fb = (px - 5, px + 5, 0, 4, POD_ZC - 5, POD_ZC + 5)
        L.paint(fb, lambda X, Y, Z: inside(X, Z) & (Y >= 1.5) & (Y <= 2.5), "gunmetal")
        L.paint(fb, tube, "black")
        L.paint(*rcyl_y(px, POD_ZC, 2.0, -18.5, -17, 0, 0), "black")                   # rear exhaust

        # outer hardpoint: 4-round ATGM rack (2 x 2)
        ax0 = s * ATGM_X
        wz2 = WING_Z - (ATGM_X - 5) * 0.08 - 1.0
        L.paint(*box(ax0 - 1, ax0 + 1, -12, -3, ATGM_ZC + 4.5, wz2), "gunmetal")      # pylon
        L.paint(*box(ax0 - 3.5, ax0 + 3.5, -15, 0, ATGM_ZC + 3.5, ATGM_ZC + 4.5), "green_dark")  # rack beam
        L.paint(*box(ax0 - 0.5, ax0 + 0.5, -15, 0, ATGM_ZC - 3, ATGM_ZC + 4), "dark")  # centre plate
        for dx in (-2.0, 2.0):
            for dz in (-1.7, 1.7):
                mx, mz = ax0 + dx, ATGM_ZC + dz
                L.paint(*rcyl_y(mx, mz, 1.6, -18, 2, 1.5, 0), "green_light")
                L.paint(*rcyl_y(mx, mz, 1.6, -3, -2, 0, 0), "green_dark")               # band
                L.paint(*rcyl_y(mx, mz, 1.6, 1, 2, 0, 0), "steel")                     # seeker nose
                L.paint(*box(mx - 0.5, mx + 0.5, 2, 3, mz - 0.5, mz + 0.5), "steel")

    # ---- main gear: trailing struts, wheels ------------------------------------
    for s in (-1, 1):
        wx = s * 9.0
        L.paint(*capsule((s * 5.0, 27.0, 15.0), (wx, 21.0, 3.5), 1.0), "dark")       # oleo
        L.paint(*capsule((s * 5.0, 16.0, 15.0), (wx, 21.0, 3.5), 0.8), "gunmetal")   # drag brace
        L.paint(*cyl_x(21.0, 3.0, 3.0, wx - 1.2 if s > 0 else wx - 1.0, wx + 1.0 if s > 0 else wx + 1.2), "rubber")
        L.paint(*cyl_x(21.0, 3.0, 1.4, wx - 1.6, wx + 1.6), "gunmetal")              # hub

    # ---- tail: boom stabiliser, fin, gearbox, ventral fin, tail wheel -----------
    def fin(X, Y, Z):
        le = -56.0 - (Z - 30) * 0.68
        te = -68.0 - (Z - 30) * 0.44
        cap = 61.0 - 0.7 * np.clip(Y + 80.0, 0, None)       # slanted top
        return (np.abs(X) <= 1.0) & (Y <= le) & (Y >= te) & (Z >= 29) & (Z <= cap)
    L.paint((-2, 2, -84, -53, 28, 62), fin, "tan")
    L.paint((-2, 2, -84, -53, 52, 62), lambda X, Y, Z: fin(X, Y, Z) & (Z >= 52), "green")
    L.paint(*box(-1.2, 3.0, -80, -74.5, 54, 59.5), "green")                              # gearbox fairing
    L.paint(*cyl_x(TAIL_HUB[1], TAIL_HUB[2], 2.2, 1, 3.5), "gunmetal")                  # gearbox (starboard)
    L.paint(*box(-0.5, 0.5, -80, -79, 60, 61.2), "red_light")                           # anti-collision
    def stab(X, Y, Z):
        ax = np.abs(X)
        le = -54.0 - ax * 0.36
        te = -64.0 - ax * 0.22
        return (ax <= 12) & (Y <= le) & (Y >= te) & (Z >= 29) & (Z <= 30.6)
    L.paint((-13, 13, -72, -54, 28, 32), stab, "tan")
    L.paint((-13, 13, -72, -54, 28, 32), lambda X, Y, Z: stab(X, Y, Z) & (np.abs(X) >= 10.5), "dark")
    def ventral(X, Y, Z):
        le = -61.0 - (25 - Z) * 0.30
        te = -66.0 - (25 - Z) * 0.10
        return (np.abs(X) <= 1.0) & (Y <= le) & (Y >= te) & (Z >= 17) & (Z <= 26)
    L.paint((-2, 2, -72, -54, 14, 27), ventral, "tan")
    L.paint(*capsule((0, -66, 18), (0, -66, 3.5), 1.0), "gunmetal")                  # tail-wheel strut
    L.paint(*cyl_x(-66.0, 2.2, 2.2, -1.0, 1.0), "rubber")
    L.paint(*cyl_x(-66.0, 2.2, 1.0, -1.4, 1.4), "gunmetal")

    # ---- panel seams and lights --------------------------------------------
    for sy in (-40.0, -54.0):
        L.paint(*box(-8, 8, sy - 0.5, sy + 0.5, 18, 47), "tan_dark", only=["tan"])
    def flank(s, y, z, col):
        xs = np.nonzero(L.a[:, y - Y0, z - Z0])[0] + X0
        xs = [int(x) for x in xs if x * s >= 0 and abs(x) <= 8]
        if xs:
            far = max(xs, key=lambda v: v * s)
            L.a[far - X0, y - Y0, z - Z0] = CI[col]
    for s in (-1, 1):
        flank(s, 2, 24, "red_light" if s < 0 else "green_light_nav")


def camo(a):
    """large green patches over the tan base: smooth value noise, threshold
    measured so GREEN_SHARE of the tan hull goes green"""
    rng = np.random.default_rng(CAMO_SEED)
    cell = 17.0
    g = rng.random((int(NX / cell) + 3, int(NY / cell) + 3, int(NZ / cell) + 3))
    ix, iy, iz = [np.arange(n) / cell for n in a.shape]
    def lerp_axis(v, t, axis):
        i0 = np.floor(t).astype(int)
        f = (t - i0)
        f = f * f * (3 - 2 * f)
        sh = [1, 1, 1]; sh[axis] = -1
        return np.take(v, i0, axis=axis) * (1 - f.reshape(sh)) + np.take(v, i0 + 1, axis=axis) * f.reshape(sh)
    n = lerp_axis(lerp_axis(lerp_axis(g, ix, 0), iy, 1), iz, 2)
    t = a == CI["tan"]
    X, Y, Z = [np.broadcast_to(v, a.shape) for v in (
        (np.arange(X0, X0 + NX) + 0.5)[:, None, None],
        (np.arange(Y0, Y0 + NY) + 0.5)[None, :, None],
        (np.arange(Z0, Z0 + NZ) + 0.5)[None, None, :])]
    # designed scheme: green nose + a long low swoosh from the chin to the
    # tail; tan top and mid; a few big soft patches break the tan up
    zline = np.interp(Y, [-84, -62, -44, -24, 0, 20, 36], [36, 30, 24, 21, 20, 19.5, 21]) + 1.6 * np.sin(Y / 6.5)
    band = (Z < zline) | (Y > 38.0)
    a[t & band] = CI["green"]
    t = a == CI["tan"]
    th = np.quantile(n[t], 1.0 - GREEN_SHARE)
    a[t & (n > th)] = CI["green"]


def shade_top(a):
    """cel highlight: hull voxels with open air directly above go light"""
    e = np.ones(a.shape, bool)
    e[:, :, :-1] = (a[:, :, 1:] == 0)
    for base, light in (("tan", "tan_light"), ("green", "green_light")):
        a[(a == CI[base]) & e] = CI[light]


def build_canopy():
    """stepped tandem glasshouse: 1-voxel shell, flat leaning panes, frames"""
    C = Layer()
    X, Y, Z = C.full()
    ztop = np.interp(Y, CAN_PY, CAN_PZ)
    sill = np.where(Y < CABIN_POST_Y, PILOT_SILL, GUNNER_SILL)
    hw = CAN_HW0 - CAN_LEAN * (Z - GUNNER_SILL)
    S = (Y >= CAN_PY[0]) & (Y <= CAN_PY[-1]) & (Z >= sill) & (Z <= ztop) & (np.abs(X) <= hw)
    pad = np.pad(S, 1)
    inner = pad.copy()
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0):          # open underneath: no lid over the cockpit floor
                if dx or dy or dz:
                    inner &= np.roll(pad, (dx, dy, dz), axis=(0, 1, 2))
    inner = inner[1:-1, 1:-1, 1:-1]
    shell = S & ~inner & (Z >= sill + 0.5)
    C.a[shell] = CI["canopy_glass"]
    near_top = (ztop - Z) < 1.2
    frame = (                                               # Apache v2 framing
        (Z < sill + 1.0) |                                  # sill rail
        (np.abs(X) > hw - 1.0) & near_top |                 # side/top edge
        (Y < CAN_PY[1] + 0.5) |                             # rear fairing solid
        (np.abs(Y - CABIN_POST_Y) < 0.6) |                  # post between cabins
        (np.abs(Y - 15.5) < 0.6) & near_top |               # pilot windshield top
        (np.abs(Y - 29.5) < 0.6) & near_top                 # gunner windshield top
    )
    C.a[shell & frame] = CI["green_dark"]
    C.a[shell & (Y < CAN_PY[1] + 0.5)] = CI["tan"]
    return C.a


def build_gun():
    G = Layer()
    mx, my, mz = GUN_PIVOT
    G.paint(*cyl_z(mx, my, 2.6, mz - 1.5, mz + 0.5), "dark")                   # turret ring
    G.paint(*box(mx - 2.5, mx + 2.5, my - 3, my + 3, mz - 5, mz - 1.5), "gunmetal")   # cradle
    G.paint(*box(mx - 1.5, mx + 1.5, my + 3, my + 8, mz - 4.5, mz - 2.5), "dark")     # recoil sleeve
    G.paint(*box(mx - 0.5, mx + 0.5, my + 8, GUN_TIP_Y - 2, mz - 4, mz - 3), "gunmetal")  # barrel
    G.paint(*box(mx - 1, mx + 1, GUN_TIP_Y - 2, GUN_TIP_Y, mz - 4.5, mz - 2.5), "steel")  # muzzle brake
    G.paint(*box(mx + 2.5, mx + 4, my - 2, my + 2, mz - 4.5, mz - 2), "dark")         # ammo chute
    return G.a


def build_tail_rotor():
    """X tail rotor: two blade pairs 55 degrees apart (scissor)"""
    T = Layer()
    _, hy, hz = TAIL_HUB
    T.paint(*cyl_x(hy, hz, 1.6, TR_X - 1, TR_X + 1), "gunmetal")
    T.paint(*cyl_x(hy, hz, 0.9, 2.5, TR_X), "steel")                           # shaft to the gearbox
    for ang in (0.0, 55.0, 180.0, 235.0):
        a = math.radians(ang)
        dy, dz = math.cos(a), math.sin(a)
        p0 = (TR_X, hy + dy * 1.5, hz + dz * 1.5)
        p1 = (TR_X, hy + dy * TR_R, hz + dz * TR_R)
        T.paint(*capsule(p0, p1, 1.0), "rotor_blade")
        q0 = (TR_X, hy + dy * (TR_R - 2.5), hz + dz * (TR_R - 2.5))
        T.paint(*capsule(q0, p1, 1.0), "rotor_tip")
    return T.a


def build_rotor():
    """5-blade main rotor, blade 0 along +y at rest, hub ringing the mast"""
    R = Layer()
    hz = ROTOR_Z
    R.paint(*cyl_z(0, 0, 7.2, hz - 1.5, hz + 0.5, r_in=2.2), "dark")          # hub disc
    R.paint(*cyl_z(0, 0, 5.0, hz - 1.5, hz + 1.5, r_in=2.2), "gunmetal")      # hub plate
    R.paint(*cyl_z(0, 0, 3.4, hz + 1.5, hz + 2.5, r_in=2.2), "dark")          # cap ring
    for k in range(5):
        a = math.radians(90.0 + 72.0 * k)
        ca, sa = math.cos(a), math.sin(a)
        def blade(X, Y, Z, ca=ca, sa=sa, r0=4.0, r1=ROTOR_R, half=None):
            along = X * ca + Y * sa
            perp = -X * sa + Y * ca
            hw = (1.75 - 0.55 * along / ROTOR_R) if half is None else half
            return (along >= r0) & (along <= r1) & (np.abs(perp) <= hw) & (Z >= hz - 1) & (Z <= hz + 1)
        bb = (-ROTOR_R - 2, ROTOR_R + 2, -ROTOR_R - 2, ROTOR_R + 2, hz - 2, hz + 2)
        R.paint(bb, blade, "rotor_blade")
        R.paint(bb, lambda X, Y, Z, ca=ca, sa=sa: blade(X, Y, Z, ca, sa, ROTOR_R - 6, ROTOR_R), "rotor_tip")
        R.paint(bb, lambda X, Y, Z, ca=ca, sa=sa: blade(X, Y, Z, ca, sa, 4.0, 13.0, 2.2)
                & (Z >= hz - 1.5) & (Z <= hz + 1.5), "gunmetal")                # blade grip
    return R.a


# ------------------------------------------------------------------ output
def to_vox(arrays):
    m = np.zeros(arrays[0].shape, np.uint8)
    for a in arrays:
        sel = a != 0
        m[sel] = a[sel]
    idx = np.argwhere(m)
    return {(int(i) + X0, int(j) + Y0, int(k) + Z0): int(m[i, j, k]) for i, j, k in idx}


def write_vox_framed(path, a):
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    idx = np.argwhere(a)
    xyzi = struct.pack("<i", len(idx)) + b"".join(
        struct.pack("BBBB", int(i), int(j), int(k), int(a[i, j, k])) for i, j, k in idx)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in PALETTE)
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(PALETTE))
    main = chunk(b"SIZE", struct.pack("<iii", NX, NY, NZ)) + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 150) + chunk(b"MAIN", b"", main))
    print(f"wrote {os.path.basename(path)}  {len(idx)} vox  (shared frame {NX}x{NY}x{NZ})")


def components(vox):
    vset = set(vox)
    seen, sizes = set(), []
    for start in vset:
        if start in seen:
            continue
        n, stack = 0, [start]
        seen.add(start)
        while stack:
            x, y, z = stack.pop()
            n += 1
            for q in ((x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)):
                if q in vset and q not in seen:
                    seen.add(q)
                    stack.append(q)
        sizes.append(n)
    return sorted(sizes, reverse=True)


_body = Layer()
build_body(_body)
camo(_body.a)
shade_top(_body.a)
_canopy, _gun, _tail, _rotor = build_canopy(), build_gun(), build_tail_rotor(), build_rotor()
PARTS = {"body": _body.a, "canopy": _canopy, "gun": _gun, "tailrotor": _tail, "rotor": _rotor}

body = to_vox([_body.a])
canopy = to_vox([_canopy])
gun = to_vox([_gun])
tailrotor = to_vox([_tail])
rotor = to_vox([_rotor])
assembled_no_rotor = to_vox([_body.a, _canopy, _gun, _tail])
assembled = to_vox([_body.a, _canopy, _gun, _tail, _rotor])

POD_MUZZLES = [(s * POD_X, 2.5, POD_ZC) for s in (1, -1)]
ATGM_MUZZLES = [(s * ATGM_X + dx, 3.0, ATGM_ZC + dz) for s in (1, -1) for dz in (-1.5, 1.5) for dx in (-1.5, 1.5)]
LANDMARKS = {
    "frame": "design voxels: x lateral (+x right/starboard), y forward (+y nose), z up, wheels z=0; "
             "parts/: file = design + parts_file_offset",
    "voxel_m": 0.042,
    "parts_file_offset": list(PARTS_FILE_OFFSET),
    "nose_tip": [0, 56, 19],
    "fin_trailing_edge_y": -80,
    "rotor": {"pivot": list(ROTOR_HUB), "axis": "z", "radius": ROTOR_R, "blades": 5},
    "tailrotor": {"pivot": list(TAIL_HUB), "axis": "x", "radius": TR_R, "side": "starboard (+x)"},
    "gun": {"pivot": list(GUN_PIVOT), "axis": "z", "barrel": "+y", "reach": GUN_TIP_Y - GUN_PIVOT[1],
            "muzzle": [0, GUN_TIP_Y, GUN_PIVOT[2] - 3.5]},
    "radar_dome": {"centre": list(DOME_C), "radius": DOME_R},
    "sensor_lens": [0, 57.0, 15.25],
    "pod_muzzles": [list(p) for p in POD_MUZZLES],
    "atgm_muzzles": [list(p) for p in ATGM_MUZZLES],
    "smoke": [0.0, NAC_Y0 - 4, NAC_Z + 1],
    "crew_gunner_back_y": 27, "crew_pilot_back_y": 9,
    "main_wheels": [[s * 9.0, 21.0, 3.0] for s in (1, -1)],
    "tail_wheel": [0, -66, 2.2],
    "canopy_glass_palette_index": CI["canopy_glass"],
}

if __name__ == "__main__":
    for name, arr in PARTS.items():
        comps = components(to_vox([arr]))
        print(f"{name}: {sum(comps)} vox, components {len(comps)} {comps[:4]}")
    vs = list(assembled)
    for i, ax in enumerate("xyz"):
        print(f"extent {ax}: {min(v[i] for v in vs)}..{max(v[i] for v in vs)}")
    print(json.dumps(LANDMARKS, indent=1))
    if "--write" in sys.argv:
        pdir = os.path.join(HERE, "out", "chopper_z10")
        os.makedirs(pdir, exist_ok=True)
        for name, arr in PARTS.items():
            write_vox_framed(os.path.join(pdir, f"ingame-chopper-z10-v1-{name}.vox"), arr)
        with open(os.path.join(pdir, "ingame_chopper_z10_landmarks.json"), "w") as f:
            json.dump(LANDMARKS, f, indent=2)
