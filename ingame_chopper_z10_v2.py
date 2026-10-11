#!/usr/bin/env python3
"""Player attack helicopter v3 (Z-10 style), v2 of the design: concept-measured
profile on a finer voxel grid.

Shapes are authored in DESIGN UNITS (1 unit = 0.042 m, the old chopper
voxel; ~131 units nose to fin = the 5.5 m game hull) and sampled at K
voxels per unit, so the game voxel is 0.042 / K m. Proportions are measured
off the owner's concept sheet (strike-bay .claude/workspace/chopper2-concept.jpg):
low-slung slab fuselage whose top line rises as one wedge from the nose to
the mast, belly ~5 units off the ground, thin tail boom, short swept stub
wings, rotor just above the deck, very swept fin with an X tail rotor.
Canopy: the Apache v2 raked tandem glasshouse (owner request), refitted.

LANDMARK MAP (design units; the generator prints design AND file voxels)
  Frame: x lateral, +x = RIGHT (starboard); y forward, +y = NOSE; z up,
         wheels touch z = 0. Rotor mast axis x = 0, y = 0.
  Front: nose tip ~ (0, 50, 10); gun muzzle GUN_MUZZLE.
  Back:  fin trailing edge ~ y -81.5; tail rotor hub TAIL_HUB.
  Parts (one shared frame; file voxel = round(design * K) + PARTS_FILE_OFFSET):
    body      fuselage forward of y -34, crew, engines, mast + radar dome,
              wings, pods, ATGM racks, main gear. Static.
    boom      tail boom aft of the y -34 seam: fin, stabiliser, ventral fin,
              tail wheel. Static in life; snaps off at BOOM_JOINT in a crash.
    canopy    glass panes + frames. Static, translucent.
    gun       chin cannon; yaws about z at GUN_PIVOT, barrel +y.
    tailrotor X tail rotor; spins about x at TAIL_HUB.
    rotor     5-blade main rotor + hub; spins about z at ROTOR_HUB. The hub
              rings the static mast that carries the dome.
    blade     one loose main-rotor blade along +y (crash debris).
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
from ingame_chopper_z10_v1 import PALETTE as _Z10_PALETTE, rcyl_y, cyl_x, cyl_z, ball, box, capsule
import ingame_chopper_apache_v2 as _apache

# Z-10 build palette + the Apache v2 livery colours (owner: camo and markings
# like the current chopper): mottled olive / olive_dark / camo_tan with
# yellow accents.
_LIVERY = ("olive", "olive_dark", "olive_light", "olive_deep", "camo_tan", "yellow", "deck_line", "steel_dark")
PALETTE = list(_Z10_PALETTE) + [(n, rgb) for n, rgb in _apache.PALETTE if n in _LIVERY]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

K = 1.6                                   # voxels per design unit
VOXEL_M = 0.042 / K

# ------------------------------------------------------------------ grid (file voxels)
X0, Y0, Z0 = -96, -150, 0                 # fine-voxel index origin
NX, NY, NZ = 192, 250, 64
PARTS_FILE_OFFSET = (-X0, -Y0, -Z0)


class Layer:
    """voxel array whose shape functions take design-unit coordinates"""
    def __init__(self):
        self.a = np.zeros((NX, NY, NZ), np.uint8)

    def _grid(self, bb):
        x0, x1, y0, y1, z0, z1 = [v * K for v in bb]
        i0, j0, k0 = max(int(math.floor(x0)), X0), max(int(math.floor(y0)), Y0), max(int(math.floor(z0)), Z0)
        i1, j1, k1 = min(int(math.ceil(x1)), X0 + NX), min(int(math.ceil(y1)), Y0 + NY), min(int(math.ceil(z1)), Z0 + NZ)
        sl = (slice(i0 - X0, i1 - X0), slice(j0 - Y0, j1 - Y0), slice(k0 - Z0, k1 - Z0))
        X = ((np.arange(i0, i1, dtype=float) + 0.5) / K)[:, None, None]
        Y = ((np.arange(j0, j1, dtype=float) + 0.5) / K)[None, :, None]
        Z = ((np.arange(k0, k1, dtype=float) + 0.5) / K)[None, None, :]
        return sl, X, Y, Z

    def paint(self, bb, fn, color, empty_only=False, only=None):
        sl, X, Y, Z = self._grid(bb)
        sub = self.a[sl]
        if sub.size == 0:
            return
        m = np.broadcast_to(fn(X, Y, Z), sub.shape)
        if empty_only:
            m = m & (sub == 0)
        if only is not None:
            m = m & np.isin(sub, [CI[c] for c in only])
        sub[m] = CI[color] if isinstance(color, str) else color

    def full(self):
        X = ((np.arange(X0, X0 + NX, dtype=float) + 0.5) / K)[:, None, None]
        Y = ((np.arange(Y0, Y0 + NY, dtype=float) + 0.5) / K)[None, :, None]
        Z = ((np.arange(Z0, Z0 + NZ, dtype=float) + 0.5) / K)[None, None, :]
        return [np.broadcast_to(v, self.a.shape) for v in (X, Y, Z)]


def fi(v):
    """design coordinate -> fine voxel index"""
    return int(math.floor(v * K))


# ------------------------------------------------------------------ key dims (design units)
ROTOR_Z = 32.0
ROTOR_HUB = (0.0, 0.0, ROTOR_Z)
ROTOR_R = 58.0
DOME_C, DOME_R, DOME_SZ = (0.0, 0.0, 35.8), 4.6, 0.6
TR_X = 2.6
TAIL_HUB = (TR_X, -76.7, 28.4)
TR_R = 10.8
GUN_PIVOT = (0.0, 41.0, 4.4)
GUN_TIP_Y = 60.0
NAC_X, NAC_Z = 7.6, 20.5
WING_Z = 13.0
POD_X, POD_ZC = 11.4, 8.2
ATGM_X, ATGM_ZC = 17.0, 8.4
WHEEL = (8.7, 18.0, 2.6)
TAIL_WHEEL = (0.0, -64.6, 1.3)
GUNNER_SILL, PILOT_SILL = 17.0, 21.0
CABIN_POST_Y = 22.2
CAN_PY = [3.5, 7.0, 15.0, 21.7, 29.0, 37.5]
CAN_PZ = [29.3, 28.4, 27.2, 22.6, 22.1, GUNNER_SILL]
CAN_HW0, CAN_LEAN = 4.6, 0.20
CAMO_SEED = 11

# fuselage loft, measured off the concept side/top/front views
FUS_Y = [-77, -66, -56, -46, -36, -26, -18, -8, 3, 3.5, 22, 22.5, 37, 43, 47, 50]
FUS_T = [15.5, 17.0, 18.2, 19.2, 20.5, 23.5, 27.0, 29.0, 29.8, GUNNER_SILL + 4, PILOT_SILL,
         GUNNER_SILL, GUNNER_SILL, 16.4, 16.0, 14.8]
FUS_B = [13.5, 12.5, 11.5, 10.5, 9.5, 8.6, 7.6, 6.6, 6.0, 6.0, 4.9, 4.9, 4.2, 4.0, 4.2, 5.0]
FUS_W = [1.8, 2.4, 3.0, 3.6, 4.4, 5.8, 6.8, 7.4, 7.6, 7.6, 7.8, 7.8, 7.4, 6.4, 5.2, 3.8]


def fus_fn(X, Y, Z):
    w = np.interp(Y, FUS_Y, FUS_W)
    top = np.interp(Y, FUS_Y, FUS_T)
    bot = np.interp(Y, FUS_Y, FUS_B)
    zc, hz = (top + bot) / 2, np.maximum((top - bot) / 2, 0.01)
    u = (Z - zc) / hz
    # slab sides leaning in above the waist (narrow top), chined below it
    wz = w * np.where(u > -0.2, 1.0 - 0.24 * (u + 0.2), 1.0 - 0.40 * np.clip((-u - 0.45) / 0.55, 0, 1))
    return (np.abs(X) <= wz) & (np.abs(u) <= 1.0) & (Y >= FUS_Y[0]) & (Y <= FUS_Y[-1])


def place_crew(L, y0, z_top, z_min):
    """stamp the bust one cell per FILE voxel (0.6 design units: crew sized
    for the concept's low cockpit); back at design y0, helmet at z_top"""
    jy, kz, kmin = fi(y0), fi(z_top), fi(z_min)
    for i, rows in enumerate(CREW_BUST):
        k = kz - i
        if k < kmin:
            break
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ".":
                    L.a[dx - 4 - X0, jy + dy - Y0, k - Z0] = CI[CREW_KEY[ch]]


def build_body(L):
    L.paint((-7, 7, FUS_Y[0], FUS_Y[-1], 3, 31), fus_fn, "tan")

    # ---- cockpit wells + crew ------------------------------------------------
    L.paint(*box(-3.8, 3.8, 22.8, 37, GUNNER_SILL - 1.2, GUNNER_SILL), "cockpit")
    L.paint(*box(-3.2, 3.2, 35, 36.6, GUNNER_SILL, GUNNER_SILL + 1.6), "dark")   # coaming
    L.paint(*box(-3.6, 3.6, 4.5, 22, PILOT_SILL - 1.2, PILOT_SILL), "cockpit")
    L.paint(*box(-3.6, 3.6, 20.8, 22.6, GUNNER_SILL - 1.2, PILOT_SILL), "cockpit")  # step face
    L.paint(*box(-3.0, 3.0, 18.4, 20, PILOT_SILL, PILOT_SILL + 1.6), "dark")
    place_crew(L, 25.5, 21.5, GUNNER_SILL - 0.5)
    place_crew(L, 8.0, 26.6, PILOT_SILL - 0.5)

    # ---- engines: intake bullet, boxy midsection, rear drum, angled exhaust ----
    for s in (-1, 1):
        xc = s * NAC_X
        L.paint(*rcyl_y(xc, NAC_Z, 3.9, -3, 11.0, 4.5, 0), "tan")
        L.paint(*rcyl_y(xc, NAC_Z, 2.3, 9.6, 11.1, 0, 0), "black")             # intake mouth
        L.paint(*rcyl_y(xc, NAC_Z, 1.0, 9.4, 11.2, 0, 0), "dark")              # inlet hub
        def mesh(X, Y, Z, xc=xc, s=s):
            out = (X - xc) * s
            return ((out > 1.2) & (np.abs(Z - NAC_Z) < 2.4) & (Y > 1.5) & (Y < 7.5)
                    & ((np.floor(Y * K) + np.floor(Z * K)) % 2 == 0))
        L.paint((xc - 5, xc + 5, -1, 6, NAC_Z - 3, NAC_Z + 3), mesh, "tan_dark", only=["tan"])
        def boxy(X, Y, Z, xc=xc):
            dx, dz = np.abs(X - xc), np.abs(Z - NAC_Z)
            return (dx <= 4.6) & (dz <= 4.3) & (dx + dz <= 7.8) & (Y >= -18.5) & (Y <= -1.5)
        L.paint((xc - 5, xc + 5, -19, -1, NAC_Z - 5, NAC_Z + 5), boxy, "green")
        L.paint((xc - 5, xc + 5, -19, -1, NAC_Z - 5, NAC_Z + 5),
                lambda X, Y, Z, xc=xc: boxy(X, Y, Z, xc) & (Z < NAC_Z - 3.7), "green_dark")   # shadow line
        px0, px1 = sorted((s * (NAC_X + 3.7), s * (NAC_X + 4.7)))
        L.paint(*box(px0, px1, -14, -5, NAC_Z - 2.4, NAC_Z + 1.8), "green_dark", only=["green"])
        L.paint(*box(px0, px1, -13.3, -5.7, NAC_Z - 1.7, NAC_Z + 1.1), "green", only=["green_dark"])
        L.paint(*rcyl_y(xc, NAC_Z, 3.6, -22.5, -18, 0, 0.8), "tan")            # rear drum
        p0 = (xc, -20.5, NAC_Z + 0.2)
        p1 = (s * (NAC_X + 2.0), -24.0, NAC_Z + 1.0)
        L.paint(*capsule(p0, p1, 3.2), "tan")
        p2 = (s * (NAC_X + 2.6), -25.6, NAC_Z + 1.4)
        L.paint(*capsule(p1, p2, 3.2), "gunmetal")                             # angled nozzle
        L.paint(*capsule(p2, (s * (NAC_X + 2.4), -26.2, NAC_Z + 1.5), 3.0), "rotor_blade")   # mid-grey rim
        L.paint(*capsule((s * (NAC_X + 2.3), -25.9, NAC_Z + 1.5),
                         (s * (NAC_X + 2.7), -27.0, NAC_Z + 1.6), 1.7), "black")         # mouth
        L.paint(*box(min(s * 3, s * 8), max(s * 3, s * 8), -20, 4, 17.0, 20.5), "tan")   # saddle

    # ---- mast, swashplate, radar dome -------------------------------------
    L.paint(*box(-3.2, 3.2, -6, 5, 28.5, 30.6), "tan")                          # mast fairing
    L.paint(*cyl_z(0, 0, 2.0, 30.4, 31.2), "gunmetal")                          # swashplate
    L.paint(*cyl_z(0, 0, 1.1, 30.4, DOME_C[2] - 2.0), "steel")                  # mast
    L.paint(*ball(DOME_C, DOME_R, 1, 1, DOME_SZ), "green")
    L.paint(*cyl_z(0, 0, DOME_R + 0.1, DOME_C[2] - 0.35, DOME_C[2] + 0.3), "green_dark", only=["green"])

    # ---- nose: green sensor housing, chin turret, pilot sight --------------
    L.paint(*box(-8, 8, 40.5, 54, 3, 18), "green", only=["tan"])
    X_, Y_, Z_ = L.full()                                                       # chamfer nose front edges
    L.a[(Y_ > 46.0) & (np.abs(X_) > 3.8 - (Y_ - 46.0) * 0.5) & (Z_ < 18) & np.isin(L.a, [CI["green"]])] = 0
    L.paint(*ball((0, 49.4, 6.6), 3.4), "green")                                # chin sensor turret
    lens = lambda X, Y, Z: ball((0, 49.4, 6.6), 3.4)[1](X, Y, Z) & (Y > 51.4) & (np.abs(X) < 1.9) & (np.abs(Z - 6.6) < 1.9)
    L.paint((-3, 3, 50, 54, 4, 11), lens, "steel")
    L.paint((-3, 3, 50, 54, 4, 11), lambda X, Y, Z: lens(X, Y, Z) & ((X ** 2 + (Z - 6.6) ** 2) < 1.6 ** 2), "lens")
    L.paint(*ball((0, 47.0, 14.4), 1.2), "dark")                                # upper sight

    # ---- cheeks + keel -------------------------------------------------------
    for s in (-1, 1):
        L.paint(*rcyl_y(s * 4.4, 9.0, 1.6, -6, 36, 2.5, 2.5), "tan")

    # ---- stub wings + stores ------------------------------------------------
    for s in (-1, 1):
        def wing(X, Y, Z, s=s):
            ax = np.abs(X)
            t = np.clip((ax - 4.5) / 15.8, 0, 1)
            le = 2.5 - 4.5 * t
            te = -9.0 + 1.0 * t
            zc = WING_Z - (ax - 4.5) * 0.05
            return (ax >= 4) & (ax <= 20.3) & (Y <= le) & (Y >= te) & (np.abs(Z - zc) <= 0.65) & (X * s > 0)
        wb = (min(s * 3, s * 22), max(s * 3, s * 22), -11, 4, 10, 16)
        L.paint(wb, wing, "tan")
        L.paint(wb, lambda X, Y, Z, s=s: wing(X, Y, Z, s) & ~wing(X, Y + 0.9, Z, s), "tan_dark")
        L.paint(*box(min(s * 4, s * 6.5), max(s * 4, s * 6.5), -8, 1.5, 11.6, 14.6), "tan")   # root fairing
        tx, tz = s * 20.2, WING_Z - 15.8 * 0.05
        L.paint(*box(tx - 0.6, tx + 0.6, -7.6, -2.6, tz - 1.4, tz + 0.9), "tan")            # tip fairing
        L.paint(*box(tx - 0.6, tx + 0.6, -2.9, -2.2, tz - 0.6, tz + 0.6),
                "red_light" if s < 0 else "green_light_nav")

        # inner hardpoint: rocket pod
        px = s * POD_X
        wz = WING_Z - (POD_X - 4.5) * 0.05 - 0.6
        L.paint(*box(px - 0.6, px + 0.6, -6.5, -0.5, POD_ZC + 1.8, wz), "dark")
        L.paint(*rcyl_y(px, POD_ZC, 2.7, -9.5, 3.0, 0.8, 1.6), "green_dark")
        L.paint(*rcyl_y(px, POD_ZC, 2.7, 2.2, 3.0, 0, 0), "dark")
        L.paint(*rcyl_y(px, POD_ZC, 2.7, -4.6, -4.0, 0, 0), "dark")
        inside = lambda X, Z, px=px: ((X - px) ** 2 + (Z - POD_ZC) ** 2) <= 2.2 ** 2
        def tube(X, Y, Z, px=px):
            cx, cz = np.floor((X - px) * K), np.floor((Z - POD_ZC) * K)
            return inside(X, Z) & (Y >= 2.4) & ((cx + cz) % 2 == 0)
        fb = (px - 3, px + 3, 1, 3.5, POD_ZC - 3, POD_ZC + 3)
        L.paint(fb, lambda X, Y, Z: inside(X, Z) & (Y >= 2.4) & (Y <= 3.0), "gunmetal")
        L.paint(fb, lambda X, Y, Z: ~inside(X, Z) & (((X - px) ** 2 + (Z - POD_ZC) ** 2) <= 2.75 ** 2)
                & (Y >= 2.2) & (Y <= 3.0), "steel")                                   # mouth ring
        L.paint(fb, lambda X, Y, Z: tube(X, Y, Z) & (Y <= 3.0), "black")
        L.paint(*rcyl_y(px, POD_ZC, 1.1, -10.4, -9.4, 0, 0), "black")

        # outer hardpoint: 4-round ATGM rack (2 x 2)
        ax0 = s * ATGM_X
        wz2 = WING_Z - (ATGM_X - 4.5) * 0.05 - 0.6
        L.paint(*box(ax0 - 0.6, ax0 + 0.6, -7, -0.5, ATGM_ZC + 2.4, wz2), "dark")
        L.paint(*box(ax0 - 2.0, ax0 + 2.0, -9, 2, ATGM_ZC + 1.8, ATGM_ZC + 2.5), "green_dark")
        L.paint(*box(ax0 - 0.3, ax0 + 0.3, -9, 2, ATGM_ZC - 1.8, ATGM_ZC + 2.2), "green_dark")
        for dx in (-1.0, 1.0):
            for dz in (-0.95, 0.95):
                mx, mz = ax0 + dx, ATGM_ZC + dz
                L.paint(*rcyl_y(mx, mz, 0.85, -12, 5.5, 0.8, 0), "green_light")
                L.paint(*rcyl_y(mx, mz, 0.85, -1.5, -1.0, 0, 0), "green_dark")
                L.paint(*rcyl_y(mx, mz, 0.85, 4.6, 5.6, 0.8, 0), "steel")             # seeker
                for f in (-1, 1):                                                      # tail fins
                    L.paint(*box(mx - 0.25 + f * 0.7, mx + 0.25 + f * 0.7, -12, -10.6, mz - 0.25, mz + 0.25),
                            "green_dark", empty_only=True)

    # ---- main gear (trailing struts) + tail wheel -----------------------------
    wx, wy, wzc = WHEEL
    for s in (-1, 1):
        L.paint(*capsule((s * 4.6, 23.4, 9.0), (s * wx, wy, wzc + 0.6), 0.6), "dark")       # oleo
        L.paint(*capsule((s * 4.6, 15.0, 8.0), (s * wx, wy, wzc + 0.6), 0.5), "gunmetal")   # drag brace
        x0w, x1w = sorted((s * (wx - 0.8), s * (wx + 0.8)))
        L.paint(*cyl_x(wy, wzc, 2.6, x0w, x1w), "rubber")
        L.paint(*cyl_x(wy, wzc, 1.1, x0w - 0.3, x1w + 0.3), "gunmetal")
    tx_, ty_, tz_ = TAIL_WHEEL
    def ventral(X, Y, Z):
        le = -54.0 - (11.5 - Z) * 0.5
        te = -59.0 - (11.5 - Z) * 0.2
        return (np.abs(X) <= 0.6) & (Y <= le) & (Y >= te) & (Z >= 5.0) & (Z <= 12)
    L.paint((-1, 1, -66, -52, 4.5, 12.5), ventral, "tan")
    L.paint(*capsule((0, -59.0, 6.0), (0, ty_, tz_ + 0.3), 0.75), "gunmetal")
    L.paint(*cyl_x(ty_, tz_, 1.3, -0.6, 0.6), "rubber")
    L.paint(*cyl_x(ty_, tz_, 0.7, -0.9, 0.9), "gunmetal")

    # ---- tail: fin, gearbox, stabiliser, antenna ------------------------------
    def fin(X, Y, Z):
        le = np.interp(Z, [13.0, 17.5, 30.0], [-50.0, -58.0, -78.5])
        te = np.interp(Z, [13.0, 30.5], [-73.0, -81.5])
        return (np.abs(X) <= 0.65) & (Y <= le) & (Y >= te) & (Z >= 13.0) & (Z <= 30.5)
    L.paint((-1, 1, -83, -48, 12.5, 31), fin, "tan")
    L.paint(*box(-0.9, 2.0, -80.3, -74.6, 26.6, 30.6), "tan")                   # gearbox fairing
    L.paint(*cyl_x(TAIL_HUB[1], TAIL_HUB[2], 1.4, 0.6, 2.2), "gunmetal")
    L.paint(*box(-0.35, 0.35, -79.5, -78.9, 30.0, 31.0), "red_light")           # anti-collision
    def stab(X, Y, Z):
        ax = np.abs(X)
        le = -59.5 - ax * 0.32
        te = -65.5 - ax * 0.18
        return (ax <= 13.4) & (Y <= le) & (Y >= te) & (Z >= 14.0) & (Z <= 15.0)
    L.paint((-14, 14, -68, -58, 13.5, 15.5), stab, "green")
    L.paint((-14, 14, -68, -58, 13.5, 15.5), lambda X, Y, Z: stab(X, Y, Z) & (np.abs(X) >= 12.4), "green_dark")
    L.paint(*box(-0.35, 0.35, -55, -53.4, 18.5, 21.4), "tan")                   # dorsal antenna fin

    # ---- seams + flank lights ----------------------------------------------
    for sy in (-34.0, -50.0):
        L.paint(*box(-7, 7, sy - 0.3, sy + 0.3, 8, 31), "tan_dark", only=["tan"])
    X, Y, Z = L.full()
    for s in (-1, 1):
        sel = (L.a != 0) & (np.abs(Y - 1.0) < 0.35) & (np.abs(Z - 12.0) < 0.35) & (X * s > 0)
        idx = np.argwhere(sel)
        if len(idx):
            far = idx[np.argmax(idx[:, 0] * s)]
            L.a[tuple(far)] = CI["red_light" if s < 0 else "green_light_nav"]


def camo(a):
    """concept scheme: green nose, engine boxes, a band across the deck behind
    the mast, a low swoosh under the wings to the boom, green tail end;
    a few soft patches break the tan"""
    X, Y, Z = [np.broadcast_to(v, a.shape) for v in (
        ((np.arange(X0, X0 + NX) + 0.5) / K)[:, None, None],
        ((np.arange(Y0, Y0 + NY) + 0.5) / K)[None, :, None],
        ((np.arange(Z0, Z0 + NZ) + 0.5) / K)[None, None, :])]
    t = a == CI["tan"]
    zline = np.interp(Y, [-82, -70, -56, -40, -20, 0, 20, 38], [24, 16, 12.5, 11.5, 10.5, 9.0, 8.0, 9.5]) \
        + 0.8 * np.sin(Y / 5.0)
    boom_top = np.interp(Y, FUS_Y, FUS_T)
    green = ((Z < zline) | (Y > 40.5) | ((Y < -2) & (Y > -12) & (Z > 25)) | ((Y < -66) & (Z < 20))
             | ((Y < -18) & (Y > -60) & (Z > boom_top - 4.8 + 0.6 * np.sin(Y / 4.0)) & (Z < boom_top - 0.5)
                & (np.abs(X) > 0.9))
             | ((Y < -56) & (Z < 22) & (np.abs(X) < 1.0)))
    a[t & green] = CI["green"]
    rng = np.random.default_rng(CAMO_SEED)
    cell = 9.0
    g = rng.random((int(NX / K / cell) + 3, int(NY / K / cell) + 3, int(NZ / K / cell) + 3))
    def lerp_axis(v, tt, axis):
        i0 = np.floor(tt).astype(int)
        f = tt - i0
        f = f * f * (3 - 2 * f)
        sh = [1, 1, 1]; sh[axis] = -1
        return np.take(v, i0, axis=axis) * (1 - f.reshape(sh)) + np.take(v, i0 + 1, axis=axis) * f.reshape(sh)
    ix, iy, iz = [np.arange(n) / K / cell for n in a.shape]
    n = lerp_axis(lerp_axis(lerp_axis(g, ix, 0), iy, 1), iz, 2)
    # (no noise patches: the concept's scheme is a few big designed shapes)


def shade_top(a):
    e = np.ones(a.shape, bool)
    e[:, :, :-1] = (a[:, :, 1:] == 0)
    for base, light in (("tan", "tan_light"), ("green", "green_light")):
        a[(a == CI[base]) & e] = CI[light]


def apache_livery(a):
    """Apache v2 livery on the Z-10 airframe: olive hull mottled to olive_dark /
    camo_tan (v2's noise: 5-unit cells, 36/64 split), olive_dark engine boxes,
    dome and stabiliser, steel_dark rocket pods with yellow rails and yellow
    rocket noses, yellow diagonal boom band, yellow stabiliser tips and wingtip
    pods (v2's accents)."""
    X, Y, Z = [np.broadcast_to(v, a.shape) for v in (
        ((np.arange(X0, X0 + NX) + 0.5) / K)[:, None, None],
        ((np.arange(Y0, Y0 + NY) + 0.5) / K)[None, :, None],
        ((np.arange(Z0, Z0 + NZ) + 0.5) / K)[None, None, :])]
    tan, green = a == CI["tan"], a == CI["green"]
    eng = (np.abs(np.abs(X) - NAC_X) <= 4.7) & (Y >= -18.6) & (Y <= -1.4) & (np.abs(Z - NAC_Z) <= 4.4)
    dome = Z > DOME_C[2] - DOME_R * DOME_SZ - 0.2
    stab = (Y < -58) & (Y > -72) & (np.abs(Z - 14.5) < 0.8) & (np.abs(X) > 1.0)
    pods = (np.abs(np.abs(X) - POD_X) < 3.0) & (Y > -11) & (Y < 3.2) & (np.abs(Z - POD_ZC) < 3.0)
    a[green & (eng | dome | stab)] = CI["olive_dark"]
    a[(a == CI["green_dark"]) & pods] = CI["steel_dark"]
    a[(a == CI["dark"]) & pods & (Y > -5) & (Y < -3.8)] = CI["gunmetal"]            # pod straps
    a[(a == CI["black"]) & pods & (Y > 2.2)] = CI["deck_line"]                     # rocket noses
    a[(tan | green) & (a != CI["olive_dark"])] = CI["olive"]
    # v2 mottle: value noise over 5-unit cells
    rng = np.random.default_rng(7)
    cell = 5.0
    g = rng.random((int(NX / K / cell) + 3, int(NY / K / cell) + 3, int(NZ / K / cell) + 3))
    def lerp_axis(v, tt, axis):
        i0 = np.floor(tt).astype(int)
        f = tt - i0
        f = f * f * (3 - 2 * f)
        sh = [1, 1, 1]; sh[axis] = -1
        return np.take(v, i0, axis=axis) * (1 - f.reshape(sh)) + np.take(v, i0 + 1, axis=axis) * f.reshape(sh)
    ix, iy, iz = [np.arange(n) / K / cell for n in a.shape]
    n = lerp_axis(lerp_axis(lerp_axis(g, ix, 0), iy, 1), iz, 2)
    o = a == CI["olive"]
    a[o & (n < 0.36)] = CI["olive_dark"]
    a[o & (n > 0.64)] = CI["camo_tan"]
    # trims
    for src, dst in (("tan_dark", "olive_deep"), ("green_dark", "olive_dark"), ("green_light", "olive_light")):
        a[a == CI[src]] = CI[dst]
    hull = np.isin(a, [CI["olive"], CI["olive_dark"], CI["camo_tan"]])
    u = Y + 0.9 * (Z - 16.0) + 40.0                                                # boom band, swept aft
    a[hull & (u >= 0) & (u < 3.0) & (Y < -30)] = CI["yellow"]
    a[(a == CI["olive_dark"]) & stab & (np.abs(X) >= 11.6)] = CI["yellow"]        # stab tips
    tip = (np.abs(np.abs(X) - 20.2) <= 0.7) & (Y > -7.7) & (Y < -2.5) & (np.abs(Z - WING_Z) < 2)
    a[tip & hull] = CI["yellow"]                                                  # wingtip pods
    rail = pods & (np.abs(np.abs(X) - POD_X) < 0.7) & (Z > POD_ZC + 2.0) & (a == CI["steel_dark"])
    a[rail] = CI["yellow"]                                                        # pod rails


def build_canopy():
    """Apache v2 raked tandem glasshouse refitted to the low cockpit:
    1-voxel shell, leaning sides, v2 framing"""
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
            for dz in (-1, 0):
                if dx or dy or dz:
                    inner &= np.roll(pad, (dx, dy, dz), axis=(0, 1, 2))
    inner = inner[1:-1, 1:-1, 1:-1]
    shell = S & ~inner & (Z >= sill + 0.3)
    C.a[shell] = CI["canopy_glass"]
    near_top = (ztop - Z) < 0.8
    frame = (
        (Z < sill + 0.7) |                                  # sill rail
        (np.abs(X) > hw - 0.65) & near_top |                # side/top edge
        (Y < CAN_PY[1] + 0.3) |                             # rear fairing
        (np.abs(Y - CABIN_POST_Y) < 0.4) |                  # post between cabins
        (np.abs(Y - 15.0) < 0.4) & near_top |               # pilot windshield top
        (np.abs(Y - 29.0) < 0.4) & near_top                 # gunner windshield top
    )
    C.a[shell & frame] = CI["olive_dark"]
    C.a[shell & (Y < CAN_PY[1] + 0.3)] = CI["olive"]
    return C.a


def build_gun():
    G = Layer()
    mx, my, mz = GUN_PIVOT
    G.paint(*cyl_z(mx, my, 1.6, mz - 0.9, mz + 0.4), "dark")                       # turret ring
    G.paint(*ball((mx, my, mz - 1.6), 1.7), "gunmetal")                            # turret
    G.paint(*box(mx - 0.9, mx + 0.9, my + 1.0, my + 5.0, mz - 2.4, mz - 1.0), "dark")   # recoil sleeve
    G.paint(*box(mx - 0.35, mx + 0.35, my + 5.0, GUN_TIP_Y - 1.2, mz - 2.0, mz - 1.4), "gunmetal")  # barrel
    G.paint(*box(mx - 0.6, mx + 0.6, GUN_TIP_Y - 1.2, GUN_TIP_Y, mz - 2.3, mz - 1.1), "steel")   # muzzle
    return G.a


def build_tail_rotor():
    T = Layer()
    _, hy, hz = TAIL_HUB
    T.paint(*cyl_x(hy, hz, 1.0, TR_X - 0.7, TR_X + 0.7), "gunmetal")
    T.paint(*cyl_x(hy, hz, 0.6, 1.8, TR_X), "steel")
    for ang in (0.0, 55.0, 180.0, 235.0):
        a = math.radians(ang)
        dy, dz = math.cos(a), math.sin(a)
        p0 = (TR_X, hy + dy * 1.0, hz + dz * 1.0)
        p1 = (TR_X, hy + dy * TR_R, hz + dz * TR_R)
        T.paint(*capsule(p0, p1, 0.7), "rotor_blade")
        q0 = (TR_X, hy + dy * (TR_R - 2.0), hz + dz * (TR_R - 2.0))
        T.paint(*capsule(q0, p1, 0.7), "rotor_tip")
    return T.a


def build_rotor():
    R = Layer()
    hz = ROTOR_Z
    R.paint(*cyl_z(0, 0, 4.4, hz - 0.9, hz + 0.3, r_in=1.4), "dark")             # hub disc
    R.paint(*cyl_z(0, 0, 3.0, hz - 0.9, hz + 0.9, r_in=1.4), "gunmetal")         # hub plate
    for k in range(5):
        a = math.radians(90.0 + 72.0 * k)
        ca, sa = math.cos(a), math.sin(a)
        def blade(X, Y, Z, ca=ca, sa=sa, r0=2.5, r1=ROTOR_R, half=None, th=0.65):
            along = X * ca + Y * sa
            perp = -X * sa + Y * ca
            hw = (1.35 - 0.35 * along / ROTOR_R) if half is None else half
            return (along >= r0) & (along <= r1) & (np.abs(perp) <= hw) & (np.abs(Z - hz) <= th)
        bb = (-ROTOR_R - 2, ROTOR_R + 2, -ROTOR_R - 2, ROTOR_R + 2, hz - 2, hz + 2)
        R.paint(bb, blade, "rotor_blade")
        R.paint(bb, lambda X, Y, Z, ca=ca, sa=sa: blade(X, Y, Z, ca, sa, ROTOR_R - 5, ROTOR_R), "rotor_tip")
        R.paint(bb, lambda X, Y, Z, ca=ca, sa=sa: blade(X, Y, Z, ca, sa, 2.5, 8.5, 1.5, 0.95), "gunmetal")  # sleeve
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
apache_livery(_body.a)
_canopy, _gun, _tail, _rotor = build_canopy(), build_gun(), build_tail_rotor(), build_rotor()

# Crash parts (#491 death animations). The tail boom is its own part, split
# on the y = -34 panel seam, so a break-up can snap it off at BOOM_JOINT
# (fin, stabiliser, ventral fin and tail wheel ride with it; the tail rotor
# hangs off it at TAIL_HUB). The game draws body + boom together in life.
# BLADE is one loose main-rotor blade at rest along +y from the hub (the
# rotor part's blade 0, no hub) for blades flung off in a rotor failure.
BOOM_SPLIT_Y = -34.0
BOOM_JOINT = (0.0, BOOM_SPLIT_Y, 16.0)
_split = fi(BOOM_SPLIT_Y) - Y0
_boom = np.zeros_like(_body.a)
_boom[:, :_split, :] = _body.a[:, :_split, :]
_front = _body.a.copy()
_front[:, :_split, :] = 0


def build_blade():
    B = Layer()
    hz = ROTOR_Z
    def blade(X, Y, Z, r0=2.5, r1=ROTOR_R, half=None, th=0.65):
        hw = (1.35 - 0.35 * Y / ROTOR_R) if half is None else half
        return (Y >= r0) & (Y <= r1) & (np.abs(X) <= hw) & (np.abs(Z - hz) <= th)
    bb = (-3, 3, 0, ROTOR_R + 2, hz - 2, hz + 2)
    B.paint(bb, blade, "rotor_blade")
    B.paint(bb, lambda X, Y, Z: blade(X, Y, Z, ROTOR_R - 5, ROTOR_R), "rotor_tip")
    B.paint(bb, lambda X, Y, Z: blade(X, Y, Z, 2.5, 8.5, 1.5, 0.95), "gunmetal")
    return B.a


_blade = build_blade()
PARTS = {"body": _front, "boom": _boom, "canopy": _canopy, "gun": _gun, "tailrotor": _tail,
         "rotor": _rotor, "blade": _blade}

body = to_vox([_body.a])
canopy = to_vox([_canopy])
assembled_no_rotor = to_vox([_body.a, _canopy, _gun, _tail])
assembled = to_vox([_body.a, _canopy, _gun, _tail, _rotor])

GUN_MUZZLE = (0.0, GUN_TIP_Y, GUN_PIVOT[2] - 1.7)
POD_MUZZLES = [(s * POD_X, 3.0, POD_ZC) for s in (1, -1)]
ATGM_MUZZLES = [(s * ATGM_X + dx, 5.6, ATGM_ZC + dz) for s in (1, -1) for dz in (-0.95, 0.95) for dx in (-1.0, 1.0)]


def _pt(p):
    return {"design": [round(v, 2) for v in p], "voxel": [round(v * K, 2) for v in p]}


LANDMARKS = {
    "frame": "x lateral (+x right/starboard), y forward (+y nose), z up, wheels z=0. "
             "design units = 0.042 m; file voxel = design * K + parts_file_offset",
    "K": K, "voxel_m": VOXEL_M,
    "parts_file_offset": list(PARTS_FILE_OFFSET),
    "nose_tip": _pt((0, 50, 10)),
    "rotor": dict(_pt(ROTOR_HUB), axis="z", radius_design=ROTOR_R, blades=5),
    "tailrotor": dict(_pt(TAIL_HUB), axis="x", radius_design=TR_R, side="starboard (+x)"),
    "gun": dict(_pt(GUN_PIVOT), axis="z", barrel="+y", muzzle=_pt(GUN_MUZZLE)),
    "radar_dome": _pt(DOME_C),
    "sensor_lens": _pt((0, 52.8, 6.6)),
    "pod_muzzles": [_pt(p) for p in POD_MUZZLES],
    "atgm_muzzles": [_pt(p) for p in ATGM_MUZZLES],
    "smoke": _pt((0.0, -24.0, NAC_Z + 1)),
    "main_wheels": [_pt((s * WHEEL[0], WHEEL[1], WHEEL[2])) for s in (1, -1)],
    "tail_wheel": _pt(TAIL_WHEEL),
    "boom_joint": _pt(BOOM_JOINT),
    "blade_root": _pt((0.0, 2.5, ROTOR_Z)),
    "canopy_glass_palette_index": CI["canopy_glass"],
}

if __name__ == "__main__":
    for name, arr in PARTS.items():
        comps = components(to_vox([arr]))
        print(f"{name}: {sum(comps)} vox, components {len(comps)} {comps[:4]}")
    vs = list(assembled)
    for i, ax in enumerate("xyz"):
        lo, hi = min(v[i] for v in vs), max(v[i] for v in vs)
        print(f"extent {ax}: voxels {lo}..{hi}  design {lo / K:.1f}..{(hi + 1) / K:.1f}")
    print(json.dumps(LANDMARKS, indent=1))
    if "--write" in sys.argv:
        pdir = os.path.join(HERE, "out", "chopper_z10_v2")
        os.makedirs(pdir, exist_ok=True)
        for name, arr in PARTS.items():
            write_vox_framed(os.path.join(pdir, f"ingame-chopper-z10-v2-{name}.vox"), arr)
        with open(os.path.join(pdir, "ingame_chopper_z10_v2_landmarks.json"), "w") as f:
            json.dump(LANDMARKS, f, indent=2)
