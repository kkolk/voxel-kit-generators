#!/usr/bin/env python3
"""Apache attack chopper v2 -- built natively at game voxel scale.

Every shape is sampled directly at final voxel centres (no supersample /
downsample), sized so parts land on whole voxels: even widths about the
x=0 centreline, 1-voxel canopy frames, 2-voxel fin / wing / blades.

Profile follows the side reference: low pointed nose with sensor ball,
raked tandem canopy (gunner low in front, pilot stepped up behind, both
windshields sloped, sides leaning in), shoulder nacelles level with the
canopy roof, thin boom rising to a swept fin with left tail rotor,
stub wings with two dumb-fire rocket pods each, Cobra-style skids,
cheek fairings, 4-barrel chin gun, crew busts from infantry-green-v2,
mottled olive/tan camo with yellow accents (boom band, stab tips, wingtip
pods, pod rails).

Frame: x lateral (0 = centreline, mirror symmetric), y forward (+y = nose),
z up, skids touch z=0, rotor mast axis at y=0. Writes:
  ingame-chopper-4x-apache-body-v1.vox               body (no canopy/gun/tail rotor)
  ingame-chopper-4x-apache-assembled-no-rotor-v1.vox body + canopy + gun + tail rotor
  ingame_chopper_apache_pivots.json                   rotor / tail rotor / gun pivots
Needs numpy. Preview: render_views.py.
"""
import os
import sys
import json
import math
import struct
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ palette
def c8(v):
    return int(v * 255.0 + 0.5)

# First 14 entries keep the old chopper palette order (viewer compat).
PALETTE = [
    ("olive",        (c8(0.46), c8(0.47), c8(0.28))),
    ("olive_dark",   (c8(0.34), c8(0.35), c8(0.20))),
    ("olive_light",  (c8(0.56), c8(0.57), c8(0.36))),
    ("gunmetal",     (c8(0.30), c8(0.31), c8(0.34))),
    ("dark",         (c8(0.22), c8(0.23), c8(0.27))),
    ("cockpit",      (c8(0.12), c8(0.12), c8(0.14))),
    ("canopy_glass", (c8(0.55), c8(0.80), c8(0.95))),
    ("steel_dark",   (c8(0.42), c8(0.44), c8(0.48))),
    ("deck_line",    (c8(0.90), c8(0.85), c8(0.30))),   # rocket-tip yellow
    ("black",        (c8(0.10), c8(0.10), c8(0.12))),
    ("rotor_blade",  (c8(0.07), c8(0.07), c8(0.08))),
    ("rotor_tip",    (c8(0.34), c8(0.34), c8(0.37))),
    ("olive_deep",   (c8(0.21), c8(0.22), c8(0.12))),
    ("soft_black",   (c8(0.17), c8(0.18), c8(0.21))),
    ("white",        (c8(0.92), c8(0.92), c8(0.88))),
    ("rubber",       (c8(0.13), c8(0.13), c8(0.15))),
    ("red_light",    (c8(0.86), c8(0.16), c8(0.12))),
    ("green_light",  (c8(0.20), c8(0.80), c8(0.30))),
    ("yellow",       (c8(0.85), c8(0.68), c8(0.10))),   # accent (v3 uses red)
    ("camo_tan",     (c8(0.58), c8(0.56), c8(0.38))),
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

# Crew bust cropped from infantry-green-v2 (viewer #24): its z 9..24 (belt to
# helmet), x 9..17 (T-pose arms trimmed), y 0..6 (+y = face). One tuple per z,
# top row first; one string per y; one char per x.
CREW_KEY = {"J": "crew_jacket", "j": "crew_jacket_dark", "t": "crew_trouser",
            "e": "crew_tan", "k": "soft_black", "g": "gunmetal",
            "s": "crew_skin", "S": "crew_skin_shadow", "o": "crew_eyes",
            "H": "crew_helmet", "h": "crew_helmet_top", "b": "crew_helmet_brim"}
CREW_BUST = [
    ('.........', '..hhhhh..', '..hhhhh..', '..hhhhh..', '..hhhhh..', '.........', '.........'),
    ('.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.........'),
    ('.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.........'),
    ('.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.........'),
    ('.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.HHHHHHH.', '.bbbbbbb.'),
    ('.........', '..sssss..', '..sssss..', '..sssss..', '..sosos..', '....S....', '.........'),
    ('.........', '..sssss..', '..sssss..', '..sssss..', '..sssss..', '..sssss..', '.........'),
    ('eeJkkkJee', 'eesssssee', 'eesssssee', 'eesssssee', 'eeSSSSSee', '..sssss..', '.........'),
    ('.JJjjjJJ.', 'JJJJJJJJJ', 'JJJJJJJJJ', 'JJJJJJJJJ', '.JJJJJJJ.', '.........', '.........'),
    ('.JJjjjJJ.', 'JJJJJJJJJ', 'JJJJJJJJJ', 'JJJJJJJJJ', '.JJJJJJJ.', '..ee.ee..', '.........'),
    ('.JJjjjJJ.', 'JJJJJJJJJ', 'JJJJJJJJJ', 'JJJJJJJJJ', '.JJJJJJJ.', '..ee.ee..', '.........'),
    ('.JJjjjJJ.', '.JJJJJJJ.', '.JJJJJJJ.', '.JJJJJJJ.', '.JJJJJJJ.', '.........', '.........'),
    ('.JJjjjJJ.', '.JJJJJJJ.', '.JJJJJJJ.', '.JJJJJJJ.', '.JJJJJJJ.', '.........', '.........'),
    ('kkkkkkkkk', 'kkkkkkkkk', 'kkkkkkkkk', 'kkkkkkkkk', 'kkkkkkkkk', '...ggg...', '.........'),
    ('kkkkkkkkk', 'kkkkkkkkk', 'kkkkkkkkk', 'kkkkkkkkk', 'kkkkkkkkk', '...ggg...', '.........'),
    ('.ttttttt.', '.ttttttt.', '.ttttttt.', '.ttttttt.', '.ttttttt.', '.........', '.........'),
]


def place_crew(L, y0, z_top, z_min):
    """stamp the bust with its back at world y0 and helmet top at z_top;
    rows below z_min are skipped (buried in the fuselage)"""
    for i, rows in enumerate(CREW_BUST):
        z = z_top - i
        if z < z_min:
            break
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ".":
                    L.a[dx - 4 - X0, y0 + dy - Y0, z - Z0] = CI[CREW_KEY[ch]]

# ------------------------------------------------------------------ grid (final voxels)
X0, Y0, Z0 = -36, -80, 0
NX, NY, NZ = 72, 132, 66


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

    def paint(self, bb, fn, color, empty_only=False):
        sl, X, Y, Z = self._grid(bb)
        sub = self.a[sl]
        m = np.broadcast_to(fn(X, Y, Z), sub.shape)
        if empty_only:
            m = m & (sub == 0)
        sub[m] = CI[color] if isinstance(color, str) else color

    def full(self):
        """broadcast voxel-centre coordinate grids for the whole layer"""
        X = (np.arange(X0, X0 + NX, dtype=float) + 0.5)[:, None, None]
        Y = (np.arange(Y0, Y0 + NY, dtype=float) + 0.5)[None, :, None]
        Z = (np.arange(Z0, Z0 + NZ, dtype=float) + 0.5)[None, None, :]
        return [np.broadcast_to(v, self.a.shape) for v in (X, Y, Z)]


# ------------------------------------------------------------------ shapes
def rcyl_y(xc, zc, r, y0, y1, rr_f=0.0, rr_b=0.0):
    """cylinder along y with rounded end corners (front = y1, back = y0)"""
    def fn(X, Y, Z):
        rho = np.sqrt((X - xc) ** 2 + (Z - zc) ** 2)
        lim = np.full(rho.shape, float(r))
        if rr_f > 0:
            t = np.clip(Y - (y1 - rr_f), 0, None)
            lim = np.minimum(lim, r - rr_f + np.sqrt(np.maximum(rr_f ** 2 - t ** 2, 0)))
        if rr_b > 0:
            t = np.clip((y0 + rr_b) - Y, 0, None)
            lim = np.minimum(lim, r - rr_b + np.sqrt(np.maximum(rr_b ** 2 - t ** 2, 0)))
        return (rho <= lim) & (Y >= y0) & (Y <= y1)
    bb = (xc - r - 1, xc + r + 1, y0 - 1, y1 + 1, zc - r - 1, zc + r + 1)
    return bb, fn


def cyl_x(yc, zc, r, x0, x1):
    def fn(X, Y, Z):
        return ((Y - yc) ** 2 + (Z - zc) ** 2 <= r * r) & (X >= x0) & (X <= x1)
    return (x0 - 1, x1 + 1, yc - r - 1, yc + r + 1, zc - r - 1, zc + r + 1), fn


def cyl_z(xc, yc, r, z0, z1):
    def fn(X, Y, Z):
        return ((X - xc) ** 2 + (Y - yc) ** 2 <= r * r) & (Z >= z0) & (Z <= z1)
    return (xc - r - 1, xc + r + 1, yc - r - 1, yc + r + 1, z0 - 1, z1 + 1), fn


def ball(c, r, sx=1.0, sy=1.0, sz=1.0):
    cx, cy, cz = c
    def fn(X, Y, Z):
        return ((X - cx) / (r * sx)) ** 2 + ((Y - cy) / (r * sy)) ** 2 + ((Z - cz) / (r * sz)) ** 2 <= 1.0
    return (cx - r * sx - 1, cx + r * sx + 1, cy - r * sy - 1, cy + r * sy + 1,
            cz - r * sz - 1, cz + r * sz + 1), fn


def box(x0, x1, y0, y1, z0, z1):
    """voxels whose centres fall inside [x0,x1] x [y0,y1] x [z0,z1]"""
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
ROTOR_Z = 55             # rotor plane (mast top)
HUB_Y = 0
CAMO_SEED = 7
NAC_X, NAC_R, NAC_Z = 8.5, 5.6, 39.5
NAC_Y0, NAC_Y1 = -45.0, -4.0
WING_Z = 23.0
POD_X, POD_ZC = 18.0, 17.0
FIN_HUB = (0.0, -70.0, 52.0)       # tail rotor hub (x set by gearbox)
TR_X = -4.5
TR_R = 11.5
GUN_MOUNT = (0.0, 24.0, 14.0)
SILL_Z = 28.0                       # fuselage top under the canopy / canopy base
# canopy top profile (y, z): rear fairing, pilot roof, pilot windshield,
# gunner roof, gunner windshield down to the nose
CAN_PY = [3.0, 6.0, 14.0, 19.0, 26.0, 38.0]
CAN_PZ = [43.0, 47.0, 47.0, 41.0, 40.0, SILL_Z]
CAN_HW0, CAN_LEAN = 7.0, 0.16       # canopy half-width at the sill, inward lean per voxel up


def build_body(L):
    # ---- fuselage loft (squarish superellipse sections) -----------------
    ys = [-75, -68, -48, -38, -26, -10, 3,  4,  34, 38, 42, 45]
    zt = [33,  35,  36,  37,  41,  43,  43, 28, 28, 28, 25, 23]
    zb = [30,  29,  27,  23,  17,  14,  14, 14, 15, 16, 18, 20]
    hw = [2.0, 2.5, 3.5, 4.5, 6.5, 7.5, 7.5, 7.5, 7, 6, 4.5, 3]

    def fus(X, Y, Z):
        w = np.interp(Y, ys, hw)
        top = np.interp(Y, ys, zt)
        bot = np.interp(Y, ys, zb)
        zc, hz = (top + bot) / 2, np.maximum((top - bot) / 2, 0.01)
        v = (np.abs(X) / np.maximum(w, 0.01)) ** 4 + (np.abs(Z - zc) / hz) ** 4
        return (v <= 1.0) & (Y >= ys[0]) & (Y <= ys[-1])
    L.paint((-9, 9, ys[0], ys[-1], 12, 46), fus, "olive")

    # yellow diagonal band round the boom, top edge swept aft
    def band(X, Y, Z):
        u = Y + 0.9 * (Z - 30) + 50
        return (u >= 0) & (u < 5) & (Y < -40)
    sl, X, Y, Z = L._grid((-9, 9, -70, -35, 12, 46))
    sub = L.a[sl]
    sub[(sub != 0) & np.broadcast_to(band(X, Y, Z), sub.shape)] = CI["yellow"]

    # cheek fairings (avionics bays) along the lower flanks, cockpit to wing
    for s in (-1, 1):
        L.paint(*rcyl_y(s * 6.0, 18.0, 3.0, -8, 34, 4.0, 3.0), "olive")
    # dark belly keel
    L.paint(*box(-2, 2, -20, 32, 13, 15), "olive_dark", empty_only=True)

    # ---- cockpit tub: floor, seats, crew, coaming (seen through glass) ---
    L.paint(*box(-6, 6, 4, 37, 27, 28.6), "cockpit")
    L.paint(*box(-5, 5, 35, 37, 28, 31), "dark")                  # gunner coaming
    L.paint(*box(-5, 5, 13, 15, 28, 36), "dark")                  # pilot coaming / bulkhead
    place_crew(L, 20, 38, 28)                                      # gunner, low in front
    place_crew(L, 6, 45, 28)                                       # pilot, raised behind

    # ---- engine nacelles + intakes + exhausts ---------------------------
    for s in (-1, 1):
        xc = s * NAC_X
        L.paint(*rcyl_y(xc, NAC_Z, NAC_R, NAC_Y0, NAC_Y1, 3.0, 2.0), "olive")
        L.paint(*rcyl_y(s * (NAC_X - 1), NAC_Z - 0.5, 4.2, NAC_Y1 - 1, NAC_Y1 + 5, 2.0, 0), "olive")
        L.paint(*rcyl_y(s * (NAC_X - 1), NAC_Z - 0.5, 2.2, NAC_Y1 + 4, NAC_Y1 + 5.5, 0, 0), "black")
        L.paint(*rcyl_y(xc, NAC_Z, 3.6, NAC_Y0 - 2.5, NAC_Y0 + 0.5, 0, 1.0), "black")   # exhaust
        # seam band near the back of the barrel
        def band(X, Y, Z, xc=xc):
            rho = np.sqrt((X - xc) ** 2 + (Z - NAC_Z) ** 2)
            return (rho <= NAC_R + 0.01) & (rho >= NAC_R - 1.2) & (np.abs(Y + 36.5) <= 0.5)
        L.paint((xc - 7, xc + 7, -38, -35, NAC_Z - 7, NAC_Z + 7), band, "olive_dark")
        # saddle fairing down to the fuselage shoulder
        L.paint(*box(min(s * 3, s * 8), max(s * 3, s * 8), -40, -6, 33, 40), "olive")

    # ---- top deck: mast fairing, mast, hub ------------------------------
    L.paint(*box(-4, 4, -10, 7, 42, 48), "olive")
    L.paint(*box(-3, 3, -8, 5, 47, 49), "olive_dark")
    L.paint(*cyl_z(0, HUB_Y, 2.0, 48, ROTOR_Z - 1), "steel_dark")
    L.paint(*cyl_z(0, HUB_Y, 3.2, ROTOR_Z - 2, ROTOR_Z - 1), "gunmetal")

    # ---- tail: fin, gearbox, stabilator, tail wheel ---------------------
    def fin(X, Y, Z):
        le = -60.0 - (Z - 33) * 0.30
        te = -71.0 - (Z - 33) * 0.18
        return (np.abs(X) <= 1.0) & (Y <= le) & (Y >= te) & (Z >= 31) & (Z <= 58)
    L.paint((-2, 2, -80, -55, 30, 59), fin, "olive")
    L.paint((-2, 2, -80, -55, 56, 59), lambda X, Y, Z: fin(X, Y, Z) & (Z >= 56), "olive_dark")
    fy, fz = FIN_HUB[1], FIN_HUB[2]
    L.paint(*cyl_x(fy, fz, 2.6, -3, -1), "olive_dark")            # gearbox housing (left)
    def stab(X, Y, Z):
        ax = np.abs(X)
        le = -59.0 - ax * 0.30
        te = -69.0 - ax * 0.08
        return (ax <= 14) & (Y <= le) & (Y >= te) & (Z >= 31) & (Z <= 33)
    L.paint((-15, 15, -75, -55, 30, 34), stab, "olive_dark")
    L.paint((-15, 15, -75, -55, 30, 34), lambda X, Y, Z: stab(X, Y, Z) & (np.abs(X) >= 11), "yellow")  # tip caps
    L.paint(*capsule((0, -64, 31), (0, -73, 26), 0.8), "gunmetal")   # tail skid

    # ---- stub wings: anhedral, dark leading edge, root fairing, tip pods ----
    for s in (-1, 1):
        def wing(X, Y, Z, s=s):
            ax = np.abs(X)
            le = 4.0 - (ax - 6) * 0.20
            te = -17.0 + (ax - 6) * 0.15
            zc = WING_Z - (ax - 6) * 0.09
            return ((ax >= 5) & (ax <= 27) & (Y <= le) & (Y >= te) &
                    (np.abs(Z - zc) <= 1.0) & (X * s > 0))
        wb = (min(s * 4, s * 29), max(s * 4, s * 29), -20, 6, 16, 26)
        L.paint(wb, wing, "olive")
        L.paint(wb, lambda X, Y, Z, s=s: wing(X, Y, Z, s) & ~wing(X, Y + 1.5, Z, s), "olive_dark")  # leading edge
        L.paint(wb, lambda X, Y, Z, s=s: wing(X, Y, Z, s) & (np.abs(np.abs(X) - 21.5) <= 0.5)
                & (Z > WING_Z - 1.4 - (np.abs(X) - 6) * 0.09), "olive_dark")                          # panel line
        L.paint(*box(min(s * 5, s * 9), max(s * 5, s * 9), -16, 4, 20, 25), "olive")                  # root fairing
        # wingtip countermeasure pod + nav light (red port / green starboard)
        tx, tz = s * 28.0, WING_Z - 22 * 0.09
        L.paint(*rcyl_y(tx, tz, 1.5, -14, 3, 1.5, 1.0), "yellow")
        L.paint(*box(tx - 1, tx + 1, 3, 4, tz - 1, tz + 1), "red_light" if s < 0 else "green_light")

        # two hardpoints per wing, each with a 19-tube dumb-fire rocket pod
        for px in (s * 13.0, s * 21.5):
            wz = WING_Z - (abs(px) - 6) * 0.09 - 1.0             # wing underside
            L.paint(*box(px - 1, px + 1, -10, 1, POD_ZC + 2, wz), "gunmetal")        # pylon
            L.paint(*box(px - 1, px + 1, -15, 3, POD_ZC + 2.2, POD_ZC + 3.4), "yellow")  # rail on the pod
            L.paint(*box(px - 1.5, px + 1.5, -8, -1, wz - 0.5, wz + 0.3), "dark")     # rack
            L.paint(*rcyl_y(px, POD_ZC, 3.2, -15, 3, 1.0, 2.5), "steel_dark")         # pod body
            L.paint(*rcyl_y(px, POD_ZC, 3.2, 2, 4, 1.0, 0), "gunmetal")               # front rim
            L.paint(*rcyl_y(px, POD_ZC, 3.2, -9, -8, 0, 0), "gunmetal")               # strap bands
            L.paint(*rcyl_y(px, POD_ZC, 3.2, -1, 0, 0, 0), "gunmetal")
            # launch face: yellow rocket noses in the tubes, black tube walls
            def face(X, Y, Z, px=px):
                cx, cz = np.floor(X - px), np.floor(Z - POD_ZC)
                return ((((X - px) ** 2 + (Z - POD_ZC) ** 2) <= 2.2 ** 2) &
                        (Y >= 3) & (Y <= 4) & ((cx + cz) % 2 == 0))
            L.paint((px - 3, px + 3, 2, 5, POD_ZC - 3, POD_ZC + 3), face, "deck_line")
            L.paint((px - 3, px + 3, 2, 5, POD_ZC - 3, POD_ZC + 3),
                    lambda X, Y, Z, px=px: (((X - px) ** 2 + (Z - POD_ZC) ** 2) <= 2.2 ** 2)
                    & (Y >= 3) & (Y <= 4) & ~face(X, Y, Z, px), "black")
            L.paint(*rcyl_y(px, POD_ZC, 1.4, -16.5, -15, 0, 0), "black")              # rear exhaust

    # ---- Cobra-style skids: two tubes on arched cross tubes ----------------
    for s in (-1, 1):
        x = s * 10.0
        L.paint(*capsule((x, -16, 1.0), (x, 15, 1.0), 1.0), "gunmetal")           # skid tube
        L.paint(*capsule((x, 15, 1.0), (x, 19, 3.5), 1.0), "gunmetal")           # upturned toe
        L.paint(*capsule((x, -16, 1.0), (x, -18, 2.0), 1.0), "gunmetal")         # heel
        for cy in (10.0, -9.0):                                                   # cross tubes
            L.paint(*capsule((x, cy, 1.5), (s * 10.5, cy, 8.0), 0.9), "dark")
            L.paint(*capsule((s * 10.5, cy, 8.0), (s * 6.0, cy, 14.5), 0.9), "dark")
        L.paint(*box(x - 1, x + 1, 5, 6, 0, 2), "black")                        # skid shoe
    for cy in (10.0, -9.0):
        L.paint(*box(-6, 6, cy - 1, cy + 1, 13, 15), "dark")                    # belly saddle

    # ---- nose: sensor turret + PNVS ball + lights ------------------------
    L.paint(*ball((0, 45.0, 20.5), 4.6), "steel_dark")
    L.paint(*box(-1.5, 1.5, 49, 50, 19, 22), "black")             # lens
    L.paint(*ball((0, 42.5, 26.5), 2.2), "gunmetal")               # pilot night-vision ball
    L.paint(*box(-1, 1, 44, 45, 26, 27), "black")

    # nav lights + exhaust vents, snapped to the actual hull surface
    def flank(s, y, z, col, depth=1):
        xs = np.nonzero(L.a[:, y - Y0, z - Z0])[0] + X0
        xs = [int(x) for x in xs if x * s >= 0 and abs(x) <= 9]
        if not xs:
            return
        far = max(xs, key=lambda v: v * s)
        for k in range(depth):
            L.a[far - s * k - X0, y - Y0, z - Z0] = CI[col]
    for s in (-1, 1):
        flank(s, 2, 22, "red_light")
        flank(s, 1, 22, "white")
        for vy in (-22, -23, -27, -28):
            flank(s, vy, 30, "black")


def camo(a):
    """mottled field camo: low-frequency value noise splits olive hull voxels
    into olive / olive_dark / camo_tan blotches"""
    rng = np.random.default_rng(CAMO_SEED)
    cell = 5.0
    g = rng.random((int(NX / cell) + 3, int(NY / cell) + 3, int(NZ / cell) + 3))
    ix, iy, iz = [np.arange(n) / cell for n in a.shape]
    def lerp_axis(v, t, axis):
        i0 = np.floor(t).astype(int)
        f = (t - i0)
        f = f * f * (3 - 2 * f)
        sh = [1, 1, 1]; sh[axis] = -1
        return np.take(v, i0, axis=axis) * (1 - f.reshape(sh)) + np.take(v, i0 + 1, axis=axis) * f.reshape(sh)
    n = lerp_axis(lerp_axis(lerp_axis(g, ix, 0), iy, 1), iz, 2)
    o = a == CI["olive"]
    a[o & (n < 0.36)] = CI["olive_dark"]
    a[o & (n > 0.64)] = CI["camo_tan"]


def shade_top(a):
    """cel highlight: hull voxels with open air directly above go light"""
    is_o = a == CI["olive"]
    e = np.ones(a.shape, bool)
    e[:, :, :-1] = (a[:, :, 1:] == 0)
    a[is_o & e] = CI["olive_light"]


def build_canopy():
    """Raked tandem glasshouse, 1-voxel shell with 1-voxel olive frames.

    Solid = above the sill, under the top profile (CAN_PY/CAN_PZ), inside
    the leaning side walls. Frames trace the sill, the side/top edge, the
    breaks between panes and the post between the two cabins.
    """
    C = Layer()
    X, Y, Z = C.full()
    ztop = np.interp(Y, CAN_PY, CAN_PZ)
    hw = CAN_HW0 - CAN_LEAN * (Z - SILL_Z)
    S = (Y >= CAN_PY[0]) & (Y <= CAN_PY[-1]) & (Z >= SILL_Z) & (Z <= ztop) & (np.abs(X) <= hw)
    pad = np.pad(S, 1)
    inner = pad.copy()
    for ax in range(3):
        for sg in (-1, 1):
            inner &= np.roll(pad, sg, axis=ax)
    inner = inner[1:-1, 1:-1, 1:-1]
    shell = S & ~inner & (Z >= SILL_Z + 0.5)
    C.a[shell] = CI["canopy_glass"]
    near_top = (ztop - Z) < 1.2
    frame = (
        (Z < SILL_Z + 1.0) |                                       # sill rail
        (np.abs(X) > hw - 1.0) & near_top |                        # side/top edge
        (Y < CAN_PY[1] + 0.5) |                                    # rear fairing solid
        (np.abs(Y - 19.5) < 0.6) |                                 # post between cabins
        (np.abs(Y - 13.5) < 0.6) & near_top |                      # pilot windshield top
        (np.abs(Y - 26.5) < 0.6) & near_top                        # gunner windshield top
    )
    C.a[shell & frame] = CI["olive_dark"]
    C.a[shell & (Y < CAN_PY[1] + 0.5)] = CI["olive"]               # rear fairing is hull
    return C.a


def build_gun():
    G = Layer()
    mx, my, mz = GUN_MOUNT
    G.paint(*cyl_z(mx, my, 3.2, mz - 2, mz + 0.5), "dark")                   # turret ring
    G.paint(*box(mx - 3, mx + 3, my - 4, my + 4, mz - 6, mz - 2), "gunmetal")
    G.paint(*box(mx - 3, mx + 3, my + 4, my + 6, mz - 6, mz - 2), "dark")    # barrel hub
    for bx in (-1.5, 1.5):
        for bz in (-2.5, -5.5):
            G.paint(*box(mx + bx - 0.5, mx + bx + 0.5, my + 6, my + 19, mz + bz - 0.5, mz + bz + 0.5), "black")
    G.paint(*box(mx - 2, mx + 2, my + 12, my + 13, mz - 6, mz - 2), "gunmetal")    # barrel clamp
    return G.a


def build_tail_rotor():
    T = Layer()
    hy, hz = FIN_HUB[1], FIN_HUB[2]
    T.paint(*cyl_x(hy, hz, 1.6, TR_X - 1, TR_X + 1), "gunmetal")
    for dy, dz in ((1, 0), (0, 1)):
        for sg in (-1, 1):
            p0 = (TR_X, hy + sg * dy * 1.5, hz + sg * dz * 1.5)
            p1 = (TR_X, hy + sg * dy * TR_R, hz + sg * dz * TR_R)
            T.paint(*capsule(p0, p1, 0.9), "rotor_blade")
            q0 = (TR_X, hy + sg * dy * (TR_R - 2.5), hz + sg * dz * (TR_R - 2.5))
            T.paint(*capsule(q0, p1, 0.9), "rotor_tip")
    return T.a


# ------------------------------------------------------------------ output
def to_vox(arrays):
    m = np.zeros(arrays[0].shape, np.uint8)
    for a in arrays:
        sel = a != 0
        m[sel] = a[sel]
    idx = np.argwhere(m)
    return {(int(i) + X0, int(j) + Y0, int(k) + Z0): int(m[i, j, k]) for i, j, k in idx}


def write_vox(path, vox):
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    assert min(zs) >= 0, "negative z"
    sx, sy, sz = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) + 1
    assert max(sx, sy, sz) <= 256, (sx, sy, sz)
    xoff, yoff = -min(xs), -min(ys)
    xyzi = struct.pack("<i", len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("BBBB", x + xoff, y + yoff, z, ci)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in PALETTE)
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(PALETTE))
    main = chunk(b"SIZE", struct.pack("<iii", sx, sy, sz)) + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 150) + chunk(b"MAIN", b"", main))
    print(f"wrote {os.path.basename(path)}  {len(vox)} vox  dims=({sx},{sy},{sz})  xoff={xoff} yoff={yoff}")
    return xoff, yoff


def floaters(vox):
    """voxels outside the largest 6-connected component"""
    vset = set(vox)
    seen, best = set(), 0
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
        best = max(best, n)
    return len(vset) - best


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else HERE
    body = Layer()
    build_body(body)
    camo(body.a)
    canopy, gun, tail = build_canopy(), build_gun(), build_tail_rotor()

    body_vox = to_vox([body.a])
    print("body floaters:", floaters(body_vox))
    bx, by = write_vox(os.path.join(outdir, "ingame-chopper-4x-apache-body-v1.vox"), body_vox)
    asm_vox = to_vox([body.a, canopy, gun, tail])
    print("assembly floaters:", floaters(asm_vox))
    ax, ay = write_vox(os.path.join(outdir, "ingame-chopper-4x-apache-assembled-no-rotor-v1.vox"), asm_vox)

    pivots = {
        "frame": "voxels: x lateral, y forward (nose +y), z up, wheels z=0; world = file - offset",
        "body_file_offset_xy": [bx, by],
        "assembly_file_offset_xy": [ax, ay],
        "rotor": {"world": [0, HUB_Y, ROTOR_Z], "axis": "z"},
        "tailrotor": {"world": [TR_X, FIN_HUB[1], FIN_HUB[2]], "axis": "x", "radius": TR_R},
        "gun": {"world": list(GUN_MOUNT), "axis": "z"},
    }
    with open(os.path.join(outdir, "ingame_chopper_apache_pivots.json"), "w") as f:
        json.dump(pivots, f, indent=2)
    print("done")
