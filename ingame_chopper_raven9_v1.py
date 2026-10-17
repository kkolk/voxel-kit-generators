#!/usr/bin/env python3
"""Player chopper v3: the Raven-9 'Ghost' armed transport (strike-bay
.claude/workspace/raven9-concept-*.jpg; brief raven9-brief.md).

True to the 1.5 m infantry (owner, 2026-10-17): ~14.3 m nose face to fin,
7 m main rotor radius, a troop cabin a soldier walks into through a side
door or the rear ramp. Voxel 0.03 m (half the troops' 0.06).

Shapes are authored in METRES and sampled at VOXEL_M; the generator prints
every landmark in metres AND file voxels.

LANDMARK MAP (metres; file voxel = round(m / VOXEL_M) + the part's offset)
  Frame: x lateral, +x = RIGHT (starboard); y forward, +y = NOSE; z up,
         wheels touch z = 0. Rotor mast axis x = 0, y = 0.
  Front: nose face y 5.95 (sensor turret SENSOR); chin gun muzzle
         GUN_MUZZLE (y 6.62).
  Back:  fin / fan housing trailing edge ~ y -8.3; fenestron hub TAIL_HUB.
  Parts (one shared frame; each written as its own .vox, <= 256 per axis,
  with its own file offset printed in LANDMARKS["parts"]):
    body_fore  nose, cockpit, cabin front, wings, pods, nose + main gear
               (y >= FORE_SPLIT_Y). Static.
    body_aft   cabin rear, engines, mast, ramp well (BOOM_SPLIT_Y..FORE_SPLIT_Y).
               Static.
    boom       tail boom, fenestron shroud, fin, stabilisers (y < BOOM_SPLIT_Y).
               Static in life; snaps off at BOOM_JOINT in a crash.
    canopy     cockpit glazing flush in the faceted nose (side panes + roof
               strip). Static, translucent glass.
    gun        chin cannon; yaws about z at GUN_PIVOT, barrel +y.
    tailrotor  fenestron fan; spins about x at TAIL_HUB.
    hub        main rotor hub + blade grips; spins about z at ROTOR_HUB.
    blade      one main-rotor blade along +y from the hub axis; the game
               instances it ROTOR_BLADES times round ROTOR_HUB (also crash
               debris).
    door_l, door_r  cabin side doors, closed; hinge about z at DOOR_HINGE_*.
    ramp       rear loading ramp, closed; hinge about x at RAMP_HINGE.
Needs numpy.
"""
import os
import sys
import json
import math
import struct
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VOXEL_M = 0.03


def c8(v):
    return int(round(v * 255))


PALETTE = [
    ("hull",         (104, 110, 92)),    # olive-grey base
    ("hull_light",   (128, 134, 114)),
    ("hull_dark",    (70, 76, 64)),
    ("camo_dark",    (72, 78, 68)),
    ("camo_tan",     (132, 128, 104)),
    ("seam",         (40, 43, 40)),
    ("canopy_glass", (c8(0.55), c8(0.80), c8(0.95))),   # == game CHOPPER_GLASS
    ("frame",        (60, 64, 58)),
    ("cockpit",      (c8(0.12), c8(0.12), c8(0.14))),
    ("gunmetal",     (c8(0.30), c8(0.31), c8(0.34))),
    ("steel",        (150, 154, 160)),
    ("black",        (c8(0.10), c8(0.10), c8(0.12))),
    ("rubber",       (c8(0.13), c8(0.13), c8(0.15))),
    ("rotor_blade",  (78, 82, 86)),
    ("rotor_tip",    (196, 170, 60)),
    ("intake",       (24, 26, 28)),
    ("exhaust",      (62, 52, 46)),
    ("window",       (34, 44, 52)),
    ("red_light",    (c8(0.86), c8(0.16), c8(0.12))),
    ("green_light",  (c8(0.20), c8(0.80), c8(0.30))),
    ("lens",         (40, 60, 70)),
    ("missile",      (196, 196, 186)),
    ("missile_band", (184, 150, 60)),
    ("walkway",      (60, 64, 60)),
]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

# ------------------------------------------------------------------ grid (file voxels, airframe)
X0, Y0, Z0 = -110, -292, 0
NX, NY, NZ = 220, 520, 180


def vi(m):
    return int(math.floor(m / VOXEL_M))


class Layer:
    """voxel array whose shape functions take metre coordinates"""
    def __init__(self):
        self.a = np.zeros((NX, NY, NZ), np.uint8)

    def _grid(self, bb):
        x0, x1, y0, y1, z0, z1 = [v / VOXEL_M for v in bb]
        i0, j0, k0 = max(int(math.floor(x0)), X0), max(int(math.floor(y0)), Y0), max(int(math.floor(z0)), Z0)
        i1, j1, k1 = min(int(math.ceil(x1)), X0 + NX), min(int(math.ceil(y1)), Y0 + NY), min(int(math.ceil(z1)), Z0 + NZ)
        sl = (slice(i0 - X0, i1 - X0), slice(j0 - Y0, j1 - Y0), slice(k0 - Z0, k1 - Z0))
        X = ((np.arange(i0, i1, dtype=float) + 0.5) * VOXEL_M)[:, None, None]
        Y = ((np.arange(j0, j1, dtype=float) + 0.5) * VOXEL_M)[None, :, None]
        Z = ((np.arange(k0, k1, dtype=float) + 0.5) * VOXEL_M)[None, None, :]
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

    def carve(self, bb, fn):
        sl, X, Y, Z = self._grid(bb)
        sub = self.a[sl]
        if sub.size:
            sub[np.broadcast_to(fn(X, Y, Z), sub.shape)] = 0

    def coords(self):
        X = ((np.arange(X0, X0 + NX, dtype=float) + 0.5) * VOXEL_M)[:, None, None]
        Y = ((np.arange(Y0, Y0 + NY, dtype=float) + 0.5) * VOXEL_M)[None, :, None]
        Z = ((np.arange(Z0, Z0 + NZ, dtype=float) + 0.5) * VOXEL_M)[None, None, :]
        return [np.broadcast_to(v, self.a.shape) for v in (X, Y, Z)]


# ------------------------------------------------------------------ primitives (metres)
def box(x0, x1, y0, y1, z0, z1):
    return ((x0, x1, y0, y1, z0, z1),
            lambda X, Y, Z: (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1) & (Z >= z0) & (Z <= z1))


def cyl_y(xc, zc, r, y0, y1, r_in=0.0):
    def f(X, Y, Z):
        d = (X - xc) ** 2 + (Z - zc) ** 2
        return (d <= r * r) & (d >= r_in * r_in) & (Y >= y0) & (Y <= y1)
    return (xc - r, xc + r, y0, y1, zc - r, zc + r), f


def cyl_x(yc, zc, r, x0, x1, r_in=0.0):
    def f(X, Y, Z):
        d = (Y - yc) ** 2 + (Z - zc) ** 2
        return (d <= r * r) & (d >= r_in * r_in) & (X >= x0) & (X <= x1)
    return (x0, x1, yc - r, yc + r, zc - r, zc + r), f


def cyl_z(xc, yc, r, z0, z1, r_in=0.0):
    def f(X, Y, Z):
        d = (X - xc) ** 2 + (Y - yc) ** 2
        return (d <= r * r) & (d >= r_in * r_in) & (Z >= z0) & (Z <= z1)
    return (xc - r, xc + r, yc - r, yc + r, z0, z1), f


def ball(c, r, sx=1.0, sy=1.0, sz=1.0):
    def f(X, Y, Z):
        return ((X - c[0]) / sx) ** 2 + ((Y - c[1]) / sy) ** 2 + ((Z - c[2]) / sz) ** 2 <= r * r
    return (c[0] - r * sx, c[0] + r * sx, c[1] - r * sy, c[1] + r * sy, c[2] - r * sz, c[2] + r * sz), f


# ------------------------------------------------------------------ key dims (metres)
# Measured off raven9-concept-4-port-profile.jpg (0.0125 m/px, mast axis at
# px 640, ground line at px 607) and checked with the skill's overlay.py.
ROTOR_Z = 4.78
ROTOR_HUB = (0.0, 0.0, ROTOR_Z)
ROTOR_R = 7.0
ROTOR_BLADES = 5
TAIL_HUB = (0.0, -7.19, 3.00)
FAN_R_IN = 0.86                    # duct radius (fan blades inside it)
SHROUD_R = 1.12                    # octagonal housing round the duct
GUN_PIVOT = (0.0, 5.02, 0.70)
GUN_MUZZLE = (0.0, 6.62, 0.66)
SENSOR = (0.0, 5.96, 1.16)         # lens on the chin sensor housing
WING_Z, WING_TIP = 2.62, 2.45     # stub wing height at the root, tip half-span
POD_X, POD_Z = 2.25, 1.74          # rocket pods under the wing tips
FPOD_X, FPOD_Z = 1.42, 1.24        # forward weapon pods on the cheeks (4 tubes each)
FPOD_Y0, FPOD_Y1, FPOD_TUBE_Y = 1.90, 3.30, 3.88
MAIN_WHEEL = (1.46, -1.75, 0.32)   # x, y, radius (centre z = radius)
NOSE_WHEEL = (0.24, 3.30, 0.22)
DOOR_Y0, DOOR_Y1, DOOR_Z0, DOOR_Z1 = -0.88, 1.06, 0.88, 2.36
SPONSON = (1.20, 1.62, -2.62, -0.94, 0.80, 1.82)            # fuel cell: x0, x1, y0, y1, z0, z1
RAMP_Y0, RAMP_Y1 = -3.28, -2.30    # ramp spans the sloped rear belly
FORE_SPLIT_Y = 1.20               # ahead of the door and its step
BOOM_SPLIT_Y = -3.36
CABIN_FLOOR = 0.86
CAMO_SEED = 9

# fuselage loft: half-width, top, bottom per station. The cabin ends in a
# hard step (y -3.30 -> -3.40) into a thick, high boom.
FUS_Y = [-6.30, -4.50, -3.40, -3.30, -2.65, -2.30, -1.00, 0.50, 1.25, 2.40, 3.50, 4.75, 5.45, 5.95]
FUS_W = [0.38, 0.42, 0.48, 0.95, 1.18, 1.26, 1.30, 1.30, 1.28, 1.22, 1.12, 0.94, 0.72, 0.52]
FUS_T = [3.44, 3.30, 3.30, 3.36, 3.36, 3.30, 3.24, 3.62, 3.86, 3.52, 3.03, 2.46, 2.06, 1.74]
FUS_B = [2.30, 2.18, 2.10, 1.40, 1.10, 0.86, 0.78, 0.78, 0.78, 0.78, 0.78, 0.78, 0.84, 1.00]
CHAMFER_TOP = 0.45   # 45-degree facets along the roof edges
CHAMFER_BOT = 0.32
LEAN = 0.16          # upper sides lean in (tumblehome) per metre above the waist
# from the cockpit forward the upper hull leans in hard from just above the
# cheeks, so the glazing sits on a narrow ~1.4 m hood (front schematic)
NOSE_LEAN, NOSE_LEAN_FROM = 0.52, 0.60   # per metre, above belly + this
NOSE_BLEND_Y = (1.2, 2.0)                # cabin section -> nose section
PANE_POST = 0.09                         # frame post between the side panes
HOOD_HALF = 0.46                         # half-width of the cockpit hood's flat top


def loft(y):
    return (np.interp(y, FUS_Y, FUS_W), np.interp(y, FUS_Y, FUS_T), np.interp(y, FUS_Y, FUS_B))


def fus_fn(X, Y, Z, grow=0.0):
    """the faceted hull; grow offsets every face by the same distance (the
    section is shaped from the base loft first, so a negative grow is a
    true inner shell -- shaping the shrunk loft instead leaned it in less
    than the outer hull and broke through it at the hood)"""
    w, t, b = loft(Y)
    f = np.clip((Y - NOSE_BLEND_Y[0]) / (NOSE_BLEND_Y[1] - NOSE_BLEND_Y[0]), 0, 1)
    ct = np.minimum(CHAMFER_TOP * (1 - 0.75 * f), (t - b) * 0.40)
    cb = np.minimum(CHAMFER_BOT, (t - b) * 0.30)
    ax = np.abs(X)
    waist = (t + b) / 2 * (1 - f) + (b + NOSE_LEAN_FROM) * f
    lean = np.clip(Z - waist, 0, None) * (LEAN * (1 - f) + NOSE_LEAN * f)
    # the hood keeps a flat top: never lean in past HOOD_HALF + the roof facet
    lean = np.minimum(lean, np.maximum(w - (HOOD_HALF + ct), 0) * f + lean * (1 - f))
    hw = w - lean
    inside = (ax <= hw + grow) & (Z <= t + grow) & (Z >= b - grow)
    inside &= ax + (Z - (t - ct)) <= hw + grow * 1.414 + 1e-6
    inside &= ax + ((b + cb) - Z) <= w + grow * 1.414 + 1e-6
    return inside & (Y >= FUS_Y[0] - grow) & (Y <= FUS_Y[-1] + grow)


def skin_fn(X, Y, Z):
    """the outer 2-3 voxels of the hull"""
    return fus_fn(X, Y, Z) & ~fus_fn(X, Y, Z, grow=-0.075)


# cockpit glazing: raked side panes and a glazed roof strip cut into the
# faceted hull, measured off the port profile: each side pane's front edge
# leans back with the nose line (top further aft), its rear edge nearly upright
def window_fn(X, Y, Z):
    w, t, b = loft(Y)
    ax = np.abs(X)
    g_front = 4.82 - (Z - 1.94) * 0.68
    gunner = (Y >= 3.62 + (Z - 1.94) * 0.10) & (Y <= g_front) & (Z >= 1.94) & (Z <= t - 0.16)
    # pilot (rear seat): a plain polygon -- level sill, upright rear edge, top
    # on the hull line, front edge one frame post behind the gunner pane's
    # rear edge so the two panes meet (owner, r7)
    g_rear = 3.62 + (Z - 1.94) * 0.10
    pilot = (Y >= 1.80) & (Y <= g_rear - PANE_POST) & (Z >= 2.59) & (Z <= t - 0.16)
    # roof strip over both seats (owner's r4 pick): rectangular panes split
    # by straight frame bars; it stops 0.06 m short of the hood edges so the
    # bars always meet the side frames
    roof = (Y >= 1.95) & (Y <= 5.30) & (ax <= 0.40) & (Z >= t - 0.12)
    posts = (np.abs(Y - 2.62) <= 0.045) | (np.abs(Y - 3.48) <= 0.05) | (np.abs(Y - 4.30) <= 0.045)
    return (gunner | pilot | roof) & ~(roof & posts)


COCKPITS = ((3.55, 4.76, 1.36), (1.84, 3.45, 1.86))
NAC_X, NAC_Z = 0.80, 3.40          # shoulder engine nacelle centreline
NAC_RX, NAC_RZ = 0.40, 0.48        # its half-width and half-height (front view)
SPINE_Y = [-2.05, -1.85, 0.20, 1.40]   # raised mast housing between the nacelles
SPINE_Z = [3.30, 4.40, 4.40, 3.80]   # (y0, y1, floor z): gunner, pilot


def nacelle_fn(X, Y, Z, s, grow=0.0):
    """shoulder engine nacelle: rounded box, intake face at y 0.55, exhaust at -3.22"""
    xc = s * NAC_X
    f = np.interp(Y, [-3.22, -2.70, 0.20, 0.55], [0.82, 1.0, 1.0, 0.92])
    rx, rz = NAC_RX * f + grow, NAC_RZ * f + grow
    dx, dz = (X - xc) * s, Z - NAC_Z                      # dx > 0 outboard
    front = 0.55 + grow - (NAC_Z + 0.5 - Z) * 0.30          # raked intake face, top leading
    # angular section: the top slopes down and outward off the mast tower
    # (front schematic), a small chamfer at the outer bottom
    return (np.abs(dx) <= rx) & (np.abs(dz) <= rz) & (dz <= rz - (dx + rx) * 0.45) \
        & (dx - dz <= rx + rz * 0.6) & (Y >= -3.22 - grow) & (Y <= front)


# ------------------------------------------------------------------ body
def build_body(L):
    L.paint((-1.5, 1.5, FUS_Y[0], FUS_Y[-1], 0, 4.0), fus_fn, "hull")

    # nose: forward sensor turret proud of the blunt face, a dark crease
    # along the chin facet
    L.paint(*box(-0.30, 0.30, 5.62, 6.02, SENSOR[2] - 0.17, SENSOR[2] + 0.15), "gunmetal")
    L.paint(*box(-0.24, 0.24, 6.02, 6.05, SENSOR[2] - 0.12, SENSOR[2] + 0.10), "black")
    L.paint(*box(0.04, 0.18, 6.04, 6.07, SENSOR[2] - 0.08, SENSOR[2] + 0.06), "lens")
    L.paint(*box(-0.04, 0.00, 6.04, 6.07, SENSOR[2] - 0.10, SENSOR[2] - 0.07), "green_light")
    L.paint((-1.0, 1.0, 4.6, 6.0, 0.7, 1.4), lambda X, Y, Z: np.abs(np.abs(X) + (1.10 - Z) - (loft(Y)[0] - 0.05)) <= 0.03,
            "seam", only=["hull"])

    # cockpits: hollow behind the glazing, dark floors, helmeted crew
    for y0, y1, fz in COCKPITS:
        L.carve((-1.3, 1.3, y0, y1, fz, 4.0), lambda X, Y, Z, fz=fz: fus_fn(X, Y, Z, grow=-0.075) & (Z >= fz))
        L.paint((-1.3, 1.3, y0, y1, fz - 0.08, fz), lambda X, Y, Z: fus_fn(X, Y, Z, grow=-0.075), "cockpit")
    for (y0, y1, fz) in COCKPITS:
        yc = y0 + 0.55
        L.paint(*box(-0.36, 0.36, yc - 0.32, yc + 0.05, fz, fz + 0.36), "black")          # seat
        L.paint(*box(-0.22, 0.22, yc - 0.18, yc + 0.18, fz, fz + 0.52), "hull_dark")      # torso
        L.paint(*ball((0.0, yc + 0.02, fz + 0.66), 0.15), "camo_dark")                   # helmet
        L.paint(*box(-0.08, 0.08, yc + 0.12, yc + 0.17, fz + 0.58, fz + 0.68), "black")  # visor
        L.paint(*box(-0.50, 0.50, y1 - 0.10, y1, fz, fz + 0.45), "gunmetal")             # instrument panel
    L.carve((-1.5, 1.5, 1.7, 5.4, 1.8, 4.0), window_fn_skin)

    # raised spine between the nacelles: the mast housing, rising off the
    # canopy roof, flat-topped from the mast aft, stepping down at its tail
    def spine(X, Y, Z):
        h = np.interp(Y, SPINE_Y, SPINE_Z)
        ax = np.abs(X)
        return (Y >= SPINE_Y[0]) & (Y <= SPINE_Y[-1]) & (Z >= 3.0) & (Z <= h) \
            & (ax <= 0.66 - (Z - 3.0) * 0.20) & (ax + (Z - (h - 0.10)) <= 0.66 - (Z - 3.0) * 0.20)
    L.paint((-0.7, 0.7, SPINE_Y[0], SPINE_Y[-1], 3.0, 4.45), spine, "hull")
    L.paint(*box(-0.50, 0.50, -1.86, -1.80, 3.3, 4.38), "seam", only=["hull"])
    L.paint(*box(-0.42, 0.42, -0.90, -0.86, 4.0, 4.42), "seam", only=["hull"])
    L.paint(*cyl_z(0.0, 0.0, 0.17, 4.30, ROTOR_Z - 0.16), "gunmetal")
    L.paint(*cyl_z(0.0, 0.0, 0.26, 4.30, 4.42), "hull_dark")          # mast base collar
    # engine-deck grille aft of the spine, between the nacelles
    def grille(X, Y, Z):
        t = loft(Y)[1]
        return (np.abs(X) <= 0.34) & (Y >= -3.25) & (Y <= -2.12) & (Z >= t - 0.06) & ((np.floor((Y + 3.25) / 0.09) % 2) == 0)
    L.paint((-0.4, 0.4, -3.3, -2.1, 3.1, 3.5), grille, "intake", only=["hull"])

    # shoulder engine nacelles beside the spine: raked intakes forward, the
    # main exhaust high at the rear and a smaller vent below it
    for s in (1, -1):
        xc = s * NAC_X
        L.paint((xc - 0.6, xc + 0.6, -3.3, 0.8, 2.8, 4.0), lambda X, Y, Z, s=s: nacelle_fn(X, Y, Z, s), "hull")
        def intake(X, Y, Z, s=s, xc=xc):
            front = 0.55 - (NAC_Z + 0.5 - Z) * 0.30
            return ((X - xc) ** 2 / 0.30 ** 2 + (Z - NAC_Z + 0.06) ** 2 / 0.32 ** 2 <= 1.0) & (Y >= front - 0.10) & (Y <= front + 0.01)
        L.paint((xc - 0.4, xc + 0.4, 0.2, 0.8, 2.9, 3.9), intake, "intake")
        L.paint(*cyl_y(xc, NAC_Z + 0.06, 0.24, -3.24, -3.08), "gunmetal")
        L.paint(*cyl_y(xc, NAC_Z + 0.06, 0.16, -3.26, -3.12), "black")
        def vent(X, Y, Z, s=s, xc=xc):
            return (X * s >= NAC_X + NAC_RX - 0.10) & ((Y + 2.30) ** 2 / 0.32 ** 2 + (Z - (NAC_Z - 0.16)) ** 2 / 0.12 ** 2 <= 1.0)
        L.paint((-1.5, 1.5, -2.7, -1.9, 3.0, 3.4), vent, "intake", only=["hull"])
        # flank openings, as the concept draws them: the intake scoop forward,
        # the exhaust aft, both dark ovals on the nacelle's outer face
        for yc, zc, ry, rz, col in ((0.18, NAC_Z + 0.04, 0.34, 0.30, "intake"), (-2.96, NAC_Z + 0.08, 0.24, 0.20, "black")):
            def flank(X, Y, Z, s=s, yc=yc, zc=zc, ry=ry, rz=rz):
                return (X * s >= NAC_X + NAC_RX - 0.12) & ((Y - yc) ** 2 / ry ** 2 + (Z - zc) ** 2 / rz ** 2 <= 1.0)
            def rim(X, Y, Z, s=s, yc=yc, zc=zc, ry=ry, rz=rz):
                q = (Y - yc) ** 2 / ry ** 2 + (Z - zc) ** 2 / rz ** 2
                return (X * s >= NAC_X + NAC_RX - 0.12) & (q > 1.0) & (q <= 1.35)
            L.paint((-1.6, 1.6, yc - ry - 0.1, yc + ry + 0.1, zc - rz - 0.1, zc + rz + 0.1), rim, "gunmetal", only=["hull"])
            L.paint((-1.6, 1.6, yc - ry, yc + ry, zc - rz, zc + rz), flank, col, only=["hull"])
        for ys in (-0.6, -1.6):
            L.paint(*box(xc - 0.6, xc + 0.6, ys - 0.015, ys + 0.015, 2.9, 3.95), "seam", only=["hull"])

    # stub wings above the door, planform off the top schematic: a broad
    # swept trapezoid (root chord y 0.37..-2.0, tip y -0.30..-1.42 at 2.45 m),
    # 20 deg anhedral, a rocket pod under each tip (owner keeps them)
    for s in (1, -1):
        def wing(X, Y, Z, s=s):
            ax = X * s
            f = np.clip((ax - 1.15) / (WING_TIP - 1.15), 0, 1)
            le = 0.37 + (-0.30 - 0.37) * f
            te = -2.00 + (-1.42 + 2.00) * f
            zc = WING_Z - (ax - 1.15) * 0.36           # 20 deg anhedral (front schematic)
            return (ax >= 1.0) & (ax <= WING_TIP) & (Y <= le) & (Y >= te) & (np.abs(Z - zc) <= 0.08)
        L.paint((-2.6, 2.6, -2.1, 0.45, 1.9, 2.75), wing, "hull")
        L.paint(*box(s * (WING_TIP - 0.05) - 0.05, s * (WING_TIP - 0.05) + 0.05, -0.75, -0.55, 2.06, 2.20),
                "green_light" if s > 0 else "red_light")
        # rocket pod under the outer wing: tube bundle, faceted dark face
        L.paint(*box(s * POD_X - 0.05, s * POD_X + 0.05, -1.2, -0.5, POD_Z + 0.25, 2.25), "gunmetal")
        L.paint(*cyl_y(s * POD_X, POD_Z, 0.33, -1.75, 0.10), "hull_dark")
        L.paint(*cyl_y(s * POD_X, POD_Z, 0.29, 0.10, 0.17), "gunmetal")
        for ang in range(0, 360, 51):
            q = math.radians(ang)
            L.paint(*cyl_y(s * POD_X + 0.18 * math.cos(q), POD_Z + 0.18 * math.sin(q), 0.06, -0.05, 0.18), "black")
        L.paint(*cyl_y(s * POD_X, POD_Z, 0.06, -0.05, 0.18), "black")
        L.paint(*cyl_y(s * POD_X, POD_Z, 0.33, -1.2, -1.17), "seam", only=["hull_dark"])

        # forward weapon pod on each cheek: a faceted box on a short pylon,
        # four tubes (2 x 2) proud of its nose
        def pod(X, Y, Z, s=s):
            ax = np.abs(X - s * FPOD_X)
            dz = np.abs(Z - FPOD_Z)
            nose = np.clip(Y - (FPOD_Y1 - 0.35), 0, None) * 0.5
            return (ax <= 0.27 - nose) & (dz <= 0.25 - nose) & (ax + dz <= 0.40 - nose) & (Y >= FPOD_Y0) & (Y <= FPOD_Y1)
        L.paint((s * FPOD_X - 0.3, s * FPOD_X + 0.3, FPOD_Y0, FPOD_Y1, FPOD_Z - 0.3, FPOD_Z + 0.3), pod, "hull_dark")
        L.paint(*box(min(s * 1.0, s * FPOD_X), max(s * 1.0, s * FPOD_X), FPOD_Y0 + 0.3, FPOD_Y1 - 0.5, FPOD_Z - 0.06, FPOD_Z + 0.06), "gunmetal")
        for dx in (-0.11, 0.11):
            for dz in (-0.10, 0.10):
                L.paint(*cyl_y(s * FPOD_X + dx, FPOD_Z + dz, 0.07, FPOD_Y1 - 0.4, FPOD_TUBE_Y), "gunmetal")
                L.paint(*cyl_y(s * FPOD_X + dx, FPOD_Z + dz, 0.035, FPOD_TUBE_Y - 0.1, FPOD_TUBE_Y + 0.01), "black")
        L.paint(*box(s * FPOD_X - 0.28, s * FPOD_X + 0.28, FPOD_Y0 + 0.40, FPOD_Y0 + 0.43, FPOD_Z - 0.26, FPOD_Z + 0.26), "seam", only=["hull_dark"])

        # fuel-cell sponson behind the door, rounded ends; the main wheel under it
        x0, x1, y0, y1, z0, z1 = SPONSON
        def spon(X, Y, Z, s=s):
            ax = X * s
            rr = 0.5
            yy = np.clip(np.maximum(y0 + rr - Y, Y - (y1 - rr)), 0, None)
            return (ax >= x0 - 0.3) & (ax <= x1) & (Z >= z0) & (Z <= z1) & (Y >= y0) & (Y <= y1) \
                & ((ax - (x1 - rr)).clip(0) ** 2 + yy ** 2 <= rr * rr)
        L.paint((-1.7, 1.7, y0, y1, z0, z1), spon, "hull")
        L.paint(*box(min(s * 1.40, s * 1.60), max(s * 1.40, s * 1.60), -1.85, -1.55, 1.30, 1.40), "seam", only=["hull"])
    # nose gear: twin wheels on a strut; main gear: trailing arms off the sponsons
    for s in (1, -1):
        L.paint(*cyl_x(NOSE_WHEEL[1], NOSE_WHEEL[2], NOSE_WHEEL[2], s * NOSE_WHEEL[0] - 0.07, s * NOSE_WHEEL[0] + 0.07), "rubber")
        L.paint(*cyl_x(NOSE_WHEEL[1], NOSE_WHEEL[2], 0.09, s * NOSE_WHEEL[0] - 0.08, s * NOSE_WHEEL[0] + 0.08), "steel")
    L.paint(*box(-0.18, 0.18, NOSE_WHEEL[1] - 0.04, NOSE_WHEEL[1] + 0.04, NOSE_WHEEL[2] - 0.02, NOSE_WHEEL[2] + 0.02), "gunmetal")
    L.paint(*box(-0.05, 0.05, NOSE_WHEEL[1] - 0.04, NOSE_WHEEL[1] + 0.04, NOSE_WHEEL[2], 0.85), "gunmetal")
    L.paint(*box(-0.05, 0.05, NOSE_WHEEL[1] - 0.04, NOSE_WHEEL[1] + 0.30, 0.55, 0.62), "gunmetal")
    for s in (1, -1):
        wx, wy, wr = s * MAIN_WHEEL[0], MAIN_WHEEL[1], MAIN_WHEEL[2]
        L.paint(*cyl_x(wy, wr, wr, wx - 0.12, wx + 0.12), "rubber")
        L.paint(*cyl_x(wy, wr, 0.14, wx - 0.13, wx + 0.13), "steel")
        L.paint(*box(wx - 0.05, wx + 0.05, wy - 0.05, wy + 0.05, wr, 0.84), "gunmetal")
        L.paint(*box(wx - 0.05, wx + 0.05, wy - 0.05, wy + 0.45, 0.60, 0.68), "gunmetal")

    # panel seams round the airframe: cabin bulkheads and the boom break
    for ys in (3.56, -2.30):
        L.paint((-1.5, 1.5, ys - 0.015, ys + 0.015, 0.3, 4.0), lambda X, Y, Z: np.ones_like(X * Y * Z, bool), "seam", only=["hull"])
    # door wells: recessed, dark inside; a dark gap frames each, a step under it
    for s in (1, -1):
        def door_well(X, Y, Z, s=s):
            w, t, b = loft(Y)
            return (X * s >= w - 0.11) & (Y >= DOOR_Y0) & (Y <= DOOR_Y1) & (Z >= DOOR_Z0) & (Z <= DOOR_Z1)
        L.carve((-1.5, 1.5, DOOR_Y0, DOOR_Y1, DOOR_Z0, DOOR_Z1), door_well)
        def door_in(X, Y, Z, s=s):
            w, t, b = loft(Y)
            return (X * s >= w - 0.14) & (X * s < w - 0.11) & (Y >= DOOR_Y0) & (Y <= DOOR_Y1) & (Z >= DOOR_Z0) & (Z <= DOOR_Z1)
        L.paint((-1.5, 1.5, DOOR_Y0, DOOR_Y1, DOOR_Z0, DOOR_Z1), door_in, "cockpit")
        def door_gap(X, Y, Z, s=s):
            w, t, b = loft(Y)
            ring = (Y >= DOOR_Y0 - 0.05) & (Y <= DOOR_Y1 + 0.05) & (Z >= DOOR_Z0 - 0.05) & (Z <= DOOR_Z1 + 0.05)
            return ring & (X * s >= w - 0.20)
        L.paint((-1.5, 1.5, DOOR_Y0 - 0.06, DOOR_Y1 + 0.06, DOOR_Z0 - 0.06, DOOR_Z1 + 0.06), door_gap, "seam", only=["hull"])
        L.paint(*box(min(s * 1.20, s * 1.42), max(s * 1.20, s * 1.42), DOOR_Y0 + 0.30, DOOR_Y1 - 0.30, 0.42, 0.48), "gunmetal")
        for yy in (DOOR_Y0 + 0.30, DOOR_Y1 - 0.36):
            L.paint(*box(min(s * 1.20, s * 1.30), max(s * 1.20, s * 1.30), yy, yy + 0.06, 0.42, 0.95), "gunmetal")
        # cabin window aft of the door
        def win(X, Y, Z, s=s):
            w, t, b = loft(Y)
            return (X * s >= w - 0.08) & (Y >= -2.05) & (Y <= -1.35) & (Z >= 2.00) & (Z <= 2.40)
        L.paint((-1.5, 1.5, -2.1, -1.3, 1.95, 2.45), win, "window", only=["hull"])
    # ramp well: the ramp part fills the sloped rear belly, framed by a gap
    L.carve((-1.1, 1.1, RAMP_Y0, RAMP_Y1, 0.5, 2.4), ramp_fn)
    L.paint((-1.1, 1.1, RAMP_Y0 - 0.05, RAMP_Y1 + 0.05, 0.5, 2.4),
            lambda X, Y, Z: ramp_fn(X, Y, Z, grow=0.03) & ~ramp_fn(X, Y, Z), "cockpit", only=["hull"])
    def ramp_gap(X, Y, Z):
        w, t, b = loft(Y)
        side = (np.abs(np.abs(X) - 0.98) <= 0.04) & (Y >= RAMP_Y0) & (Y <= RAMP_Y1)
        end = (np.abs(Y - RAMP_Y0) <= 0.04) & (np.abs(X) <= 1.02)
        return (side | end) & (Z <= b + 0.18)
    L.paint((-1.1, 1.1, RAMP_Y0 - 0.06, RAMP_Y1 + 0.06, 0.5, 2.4), ramp_gap, "seam", only=["hull"])
    L.paint(*cyl_x(RAMP_Y1 + 0.02, 0.88, 0.05, -0.96, 0.96), "gunmetal")

    # nav + anti-collision lights
    L.paint(*box(-0.05, 0.05, -1.4, -1.2, 3.24, 3.32), "red_light", empty_only=True)
    L.paint(*box(-0.05, 0.05, 1.0, 1.2, 0.70, 0.78), "red_light", empty_only=True)


def window_fn_skin(X, Y, Z):
    """glass: the hull's outer 0.12 m inside the panes -- thick enough that a
    pane on the steep nose lean stays one 6-connected sheet"""
    return fus_fn(X, Y, Z) & ~fus_fn(X, Y, Z, grow=-0.12) & window_fn(X, Y, Z)


def ramp_fn(X, Y, Z, grow=0.0):
    """the rear loading ramp: the sloped belly between RAMP_Y0 and RAMP_Y1,
    0.12 m thick, as wide as the cabin floor"""
    w, t, b = loft(Y)
    return (np.abs(X) <= 0.94 + grow) & (Y >= RAMP_Y0 - grow) & (Y <= RAMP_Y1 + grow) \
        & (Z >= b - grow) & (Z <= b + 0.12 + grow)


# ------------------------------------------------------------------ tail
def shroud_fn(X, Y, Z, r_out=SHROUD_R):
    dy, dz = np.abs(Y - TAIL_HUB[1]), np.abs(Z - TAIL_HUB[2])
    octa = (np.maximum(dy, dz) <= r_out) & (dy + dz <= r_out * 1.30)
    return octa & (dy * dy + dz * dz >= FAN_R_IN ** 2) & (np.abs(X) <= 0.32)


def build_tail(L):
    hy, hz = TAIL_HUB[1], TAIL_HUB[2]
    # octagonal housing round the duct, faired into the boom
    L.paint((-0.35, 0.35, hy - 1.2, hy + 1.2, hz - 1.2, hz + 1.2), shroud_fn, "hull")
    L.paint(*cyl_x(hy, hz, FAN_R_IN + 0.03, -0.31, 0.31, r_in=FAN_R_IN), "hull_dark")
    L.paint(*box(-0.04, 0.04, hy - FAN_R_IN, hy + FAN_R_IN, hz - 0.03, hz + 0.03), "gunmetal")
    L.paint(*cyl_x(hy, hz, 0.16, -0.12, 0.12), "gunmetal")
    # vertical stabiliser above the housing: big, nearly upright, flat top
    def fin(X, Y, Z):
        zz = Z - (hz + 0.80)
        le = hy + 0.82 - zz * 0.80
        te = hy - 1.10 - zz * 0.02
        return (zz >= 0) & (Z <= 5.15) & (Y <= le) & (Y >= te) & (np.abs(X) <= 0.13 - 0.03 * zz)
    L.paint((-0.2, 0.2, hy - 1.3, hy + 1.0, hz + 0.7, 5.2), fin, "hull")
    L.paint(*box(-0.08, 0.08, hy - 1.12, hy - 0.96, 5.05, 5.17), "red_light")
    # tail skid under the housing
    L.paint(*box(-0.04, 0.04, hy - 0.30, hy - 0.22, 1.50, hz - 1.05), "gunmetal")
    L.paint(*box(-0.04, 0.04, hy - 0.62, hy - 0.22, 1.50, 1.56), "gunmetal")
    # horizontal stabilisers low on the boom, ahead of the housing, with tall
    # raked endplates canted 15 deg out
    for s in (1, -1):
        def stab(X, Y, Z, s=s):
            ax = X * s
            return (ax >= 0.2) & (ax <= 1.05) & (Y <= -4.85 - (ax - 0.2) * 0.20) & (Y >= -6.10 - (ax - 0.2) * 0.05) \
                & (Z >= 2.62) & (Z <= 2.71)
        L.paint((-1.4, 1.4, -6.2, -4.8, 2.6, 2.75), stab, "hull")
        def endplate(X, Y, Z, s=s):
            zz = Z - 2.62
            cx = s * (1.02 + np.clip(zz, 0, None) * 0.27)
            return (np.abs(X - cx) <= 0.06) & (zz >= -0.18) & (zz <= 1.26) \
                & (Y <= -5.05 - zz * 0.72) & (Y >= -6.10 - zz * 0.24)
        L.paint((-1.8, 1.8, -6.5, -5.0, 2.4, 3.9), endplate, "hull")


# ------------------------------------------------------------------ livery
def livery(a):
    """olive-grey hull broken by angular two-tone camo (dark + tan), lighter
    on upward faces"""
    hull = a == CI["hull"]
    rng = np.random.default_rng(CAMO_SEED)
    # angular patches: nearest seed point on a rotated lattice (Voronoi cells
    # read as hard-edged facets), each cell dark, tan or base
    n = 260
    pts = np.stack([rng.uniform(-3.2, 3.2, n), rng.uniform(-8.8, 6.8, n), rng.uniform(0, 5.4, n)], 1)
    kind = rng.choice([0, 1, 2], n, p=[0.42, 0.33, 0.25])
    idx = np.argwhere(hull)
    P = np.stack([(idx[:, 0] + X0 + 0.5) * VOXEL_M, (idx[:, 1] + Y0 + 0.5) * VOXEL_M, (idx[:, 2] + Z0 + 0.5) * VOXEL_M], 1)
    best = np.full(len(P), np.inf)
    lab = np.zeros(len(P), int)
    for i, p in enumerate(pts):
        d = np.abs(P[:, 0] - p[0]) * 0.8 + np.abs(P[:, 1] - p[1]) + np.abs(P[:, 2] - p[2]) * 1.3   # L1: faceted cells
        m = d < best
        best[m] = d[m]
        lab[m] = kind[i]
    col = np.where(lab == 1, CI["camo_dark"], np.where(lab == 2, CI["camo_tan"], CI["hull"]))
    a[idx[:, 0], idx[:, 1], idx[:, 2]] = col
    # top faces a shade lighter
    e = np.zeros(a.shape, bool)
    e[:, :, :-1] = (a[:, :, 1:] == 0)
    a[(a == CI["hull"]) & e] = CI["hull_light"]


# ------------------------------------------------------------------ separate parts
def build_canopy():
    """cockpit glazing: the hull's own outer skin inside the window panes
    (window_fn), so the glass sits flush in the faceted nose; the hull keeps
    the frames between panes"""
    c = Layer()
    c.paint((-1.5, 1.5, 1.7, 5.4, 1.8, 4.0), window_fn_skin, "canopy_glass")
    return c.a


def build_gun():
    """chin turret: a ball under the nose with a long single barrel along +y"""
    g = Layer()
    px, py, pz = GUN_PIVOT
    g.paint(*cyl_z(px, py, 0.14, pz, FUS_B[-3] + 0.02), "gunmetal")            # yaw ring up into the belly
    g.paint(*ball((px, py, pz), 0.24, sz=0.80), "gunmetal")
    g.paint(*cyl_y(px, pz - 0.03, 0.10, py, py + 0.55), "gunmetal")            # recoil housing
    g.paint(*cyl_y(px, pz - 0.03, 0.05, py + 0.55, GUN_MUZZLE[1] - 0.14), "black")   # barrel
    g.paint(*cyl_y(px, pz - 0.03, 0.08, GUN_MUZZLE[1] - 0.14, GUN_MUZZLE[1]), "gunmetal")  # muzzle brake
    g.paint(*box(-0.14, -0.08, py - 0.12, py + 0.40, pz - 0.06, pz + 0.08), "steel")  # ammo chute
    return g.a


def build_fan():
    f = Layer()
    hy, hz = TAIL_HUB[1], TAIL_HUB[2]
    f.paint(*cyl_x(hy, hz, 0.15, -0.10, 0.10), "steel")
    n = 10
    for i in range(n):
        a0 = 2 * math.pi * i / n
        def blade(X, Y, Z, a0=a0):
            dy, dz = Y - hy, Z - hz
            r = np.sqrt(dy * dy + dz * dz)
            th = np.arctan2(dz, dy)
            dth = np.angle(np.exp(1j * (th - a0 - (r - 0.15) * 0.35)))
            return (r >= 0.12) & (r <= FAN_R_IN - 0.03) & (np.abs(dth * r) <= 0.05) & (np.abs(X) <= 0.05)
        f.paint((-0.06, 0.06, hy - FAN_R_IN, hy + FAN_R_IN, hz - FAN_R_IN, hz + FAN_R_IN), blade, "rotor_blade")
    return f.a


def build_hub():
    h = Layer()
    z = ROTOR_Z
    h.paint(*cyl_z(0, 0, 0.30, z - 0.14, z + 0.10), "gunmetal")
    h.paint(*cyl_z(0, 0, 0.22, z + 0.10, z + 0.22), "hull_dark")
    h.paint(*ball((0, 0, z + 0.22), 0.20, sz=0.5), "hull_dark")      # hub cap
    for i in range(ROTOR_BLADES):
        a = 2 * math.pi * i / ROTOR_BLADES
        cx, cy = math.sin(a), math.cos(a)
        def grip(X, Y, Z, cx=cx, cy=cy):
            along = X * cx + Y * cy
            across = -X * cy + Y * cx
            return (along >= 0.2) & (along <= 0.62) & (np.abs(across) <= 0.09) & (Z >= z - 0.08) & (Z <= z + 0.04)
        h.paint((-0.7, 0.7, -0.7, 0.7, z - 0.1, z + 0.06), grip, "steel")
    return h.a


def build_blade_dict():
    """one main-rotor blade at rest along +y from the hub axis: root at the
    grip, swept tip; its own small grid (x across chord, y along span)."""
    out = {}
    z0 = vi(ROTOR_Z) - 1
    for j in range(vi(0.60), vi(ROTOR_R) + 1):
        y = (j + 0.5) * VOXEL_M
        chord = 0.50 - 0.20 * (y - 0.6) / (ROTOR_R - 0.6)        # tapered 0.50 -> 0.30 m
        lead = 0.0 if y < ROTOR_R - 0.5 else (y - (ROTOR_R - 0.5)) * 0.4   # tip swept back
        x0, x1 = -chord * 0.35 - lead, chord * 0.65 - lead
        col = CI["rotor_tip"] if y > ROTOR_R - 0.35 else CI["rotor_blade"]
        for i in range(vi(x0), vi(x1) + 1):
            out[(i, j, z0)] = col
            if y < 1.0 or abs((i + 0.5) * VOXEL_M - 0.0) < 0.10:
                out[(i, j, z0 + 1)] = col   # thicker root and spar line
    return out


def rotate_z(d, ang):
    """d turned by ang about the z axis, resampled from the destination
    side so the rotated part has no holes"""
    out = {}
    c, s = math.cos(ang), math.sin(ang)
    r = max(math.hypot(x + 0.5, y + 0.5) for x, y, _ in d) + 1
    zs = sorted({z for _, _, z in d})
    n = int(math.ceil(r))
    for x in range(-n, n + 1):
        for y in range(-n, n + 1):
            xx, yy = x + 0.5, y + 0.5
            sx, sy = int(math.floor(xx * c + yy * s)), int(math.floor(-xx * s + yy * c))
            for z in zs:
                col = d.get((sx, sy, z))
                if col:
                    out[(x, y, z)] = col
    return out


# ------------------------------------------------------------------ assembly
def to_vox(arrays):
    m = np.zeros(arrays[0].shape, np.uint8)
    for a in arrays:
        sel = a != 0
        m[sel] = a[sel]
    idx = np.argwhere(m)
    return {(int(i) + X0, int(j) + Y0, int(k) + Z0): int(m[i, j, k]) for i, j, k in idx}


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


def prune_crumbs(vox, min_size=10):
    """drop 6-connected pieces under min_size voxels: sampling crumbs where a
    pane edge meets a cut-out, never real detail (those are printed and
    attached, see the components check)"""
    vset, seen, keep = set(vox), set(), {}
    for start in vox:
        if start in seen:
            continue
        cells, stack = [], [start]
        seen.add(start)
        while stack:
            x, y, z = stack.pop()
            cells.append((x, y, z))
            for q in ((x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)):
                if q in vset and q not in seen:
                    seen.add(q)
                    stack.append(q)
        if len(cells) >= min_size:
            keep.update({c: vox[c] for c in cells})
    return keep


def split_y(a, y_lo, y_hi):
    out = np.zeros_like(a)
    j0 = max(vi(y_lo) - Y0, 0) if y_lo is not None else 0
    j1 = min(vi(y_hi) - Y0, NY) if y_hi is not None else NY
    out[:, j0:j1, :] = a[:, j0:j1, :]
    return out


def write_vox(path, vox):
    """one .vox per part, cropped to its own bounds (<= 256 per axis);
    returns the file offset: file = frame voxel + offset"""
    xs, ys, zs = zip(*vox)
    lo = (min(xs), min(ys), min(zs))
    size = (max(xs) - lo[0] + 1, max(ys) - lo[1] + 1, max(zs) - lo[2] + 1)
    assert max(size) <= 256, (path, size)
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    xyzi = struct.pack("<i", len(vox)) + b"".join(
        struct.pack("BBBB", x - lo[0], y - lo[1], z - lo[2], c) for (x, y, z), c in vox.items())
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in PALETTE)
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(PALETTE))
    main = chunk(b"SIZE", struct.pack("<iii", *size)) + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 150) + chunk(b"MAIN", b"", main))
    print(f"wrote {os.path.basename(path)}  {len(vox)} vox  size {size}  offset {tuple(-v for v in lo)}")
    return tuple(-v for v in lo)


_body = Layer()
build_body(_body)
build_tail(_body)
livery(_body.a)

_door_l, _door_r, _ramp = Layer(), Layer(), Layer()
for _s, _d in ((-1, _door_l), (1, _door_r)):
    def _door(X, Y, Z, s=_s):
        w, t, b = loft(Y)
        return (X * s >= w - 0.11) & (X * s <= w - 0.01) & (Y >= DOOR_Y0 + 0.02) & (Y <= DOOR_Y1 - 0.02) \
            & (Z >= DOOR_Z0 + 0.02) & (Z <= DOOR_Z1 - 0.02)
    _d.paint((-1.4, 1.4, DOOR_Y0, DOOR_Y1, DOOR_Z0, DOOR_Z1), _door, "hull")
    _d.paint((-1.4, 1.4, DOOR_Y0, DOOR_Y1, DOOR_Z0, DOOR_Z1),
             lambda X, Y, Z: (Y <= DOOR_Y0 + 0.10) | (Y >= DOOR_Y1 - 0.10) | (Z <= DOOR_Z0 + 0.10) | (Z >= DOOR_Z1 - 0.10),
             "hull_dark", only=["hull"])
    # door window and handle
    def _dwin(X, Y, Z, s=_s):
        w, t, b = loft(Y)
        return (X * s >= w - 0.04) & ((Y >= -0.70) & (Y <= -0.14) | (Y >= 0.32) & (Y <= 0.88)) & (Z >= 1.86) & (Z <= 2.22)
    _d.paint((-1.5, 1.5, -0.8, 1.0, 1.8, 2.3), _dwin, "window", only=["hull"])
    # four-panel door: a cross seam
    _d.paint((-1.5, 1.5, DOOR_Y0, DOOR_Y1, DOOR_Z0, DOOR_Z1),
             lambda X, Y, Z: (np.abs(Y - (DOOR_Y0 + DOOR_Y1) / 2) <= 0.02) | (np.abs(Z - 1.62) <= 0.02),
             "seam", only=["hull"])
    _d.paint((-1.4, 1.4, DOOR_Y1 - 0.25, DOOR_Y1 - 0.12, 1.35, 1.42),
             lambda X, Y, Z, s=_s: X * s >= loft(Y)[0] - 0.04, "steel", only=["hull"])
_ramp.paint((-1.1, 1.1, RAMP_Y0, RAMP_Y1, 0.5, 2.4), ramp_fn, "hull_dark")
_ramp.paint((-1.1, 1.1, RAMP_Y0, RAMP_Y1, 0.5, 2.4),
            lambda X, Y, Z: (np.abs(X) <= 0.85) & ((np.abs(X) % 0.3) < 0.04), "walkway", only=["hull_dark"])

_canopy, _gun, _fan, _hub = build_canopy(), build_gun(), build_fan(), build_hub()
_blade = build_blade_dict()

_fore = split_y(_body.a, FORE_SPLIT_Y, None)
_aft = split_y(_body.a, BOOM_SPLIT_Y, FORE_SPLIT_Y)
_boom = split_y(_body.a, None, BOOM_SPLIT_Y)

PARTS = {"body_fore": prune_crumbs(to_vox([_fore])), "body_aft": prune_crumbs(to_vox([_aft])), "boom": prune_crumbs(to_vox([_boom])),
         "canopy": to_vox([_canopy]), "gun": to_vox([_gun]), "tailrotor": to_vox([_fan]),
         "hub": to_vox([_hub]), "blade": _blade,
         "door_l": to_vox([_door_l.a]), "door_r": to_vox([_door_r.a]), "ramp": to_vox([_ramp.a])}

airframe = {}
for _n, _v in PARTS.items():
    if _n != "blade":
        airframe.update(_v)
rotor = {}
for _i in range(ROTOR_BLADES):
    rotor.update(rotate_z(_blade, 2 * math.pi * _i / ROTOR_BLADES + math.radians(18)))
assembled = dict(airframe)
assembled.update(rotor)
# a short-blade stub view keeps the airframe readable at contact-sheet scale
stub = dict(airframe)
for _i in range(ROTOR_BLADES):
    stub.update(rotate_z({k: v for k, v in _blade.items() if k[1] * VOXEL_M < 2.6}, 2 * math.pi * _i / ROTOR_BLADES + math.radians(18)))

# ------------------------------------------------------------------ landmarks
BOOM_JOINT = (0.0, BOOM_SPLIT_Y, 2.75)
DOOR_HINGE = {"l": (-1.30, DOOR_Y1, DOOR_Z0), "r": (1.30, DOOR_Y1, DOOR_Z0)}
RAMP_HINGE = (0.0, RAMP_Y1, 0.88)
POD_MUZZLES = [(s * POD_X, 0.18, POD_Z) for s in (1, -1)]                 # wing rocket pods
FPOD_MUZZLES = [(s * FPOD_X + dx, FPOD_TUBE_Y, FPOD_Z + dz) for s in (1, -1) for dz in (0.10, -0.10) for dx in (-0.11, 0.11)]
SEATS = [(s * 0.80, y, CABIN_FLOOR + 0.42) for s in (1, -1) for y in (1.30, 0.62, -0.06, -0.74, -1.42)]


def _pt(p):
    return {"m": [round(v, 3) for v in p], "voxel": [round(v / VOXEL_M, 2) for v in p]}


LANDMARKS = {
    "frame": "x lateral (+x right/starboard), y forward (+y nose), z up, wheels z=0. "
             "metres; frame voxel = m / voxel_m; part file voxel = frame voxel + part offset",
    "voxel_m": VOXEL_M,
    "nose_tip": _pt((0, FUS_Y[-1], (FUS_T[-1] + FUS_B[-1]) / 2)),
    "sensor": _pt(SENSOR),
    "rotor": dict(_pt(ROTOR_HUB), axis="z", radius_m=ROTOR_R, blades=ROTOR_BLADES,
                  note="blade part at rest along +y; instance it every 360/blades deg"),
    "tailrotor": dict(_pt(TAIL_HUB), axis="x", radius_m=FAN_R_IN, kind="fenestron"),
    "gun": dict(_pt(GUN_PIVOT), axis="z", barrel="+y", muzzle=_pt(GUN_MUZZLE)),
    "pod_muzzles": [_pt(p) for p in POD_MUZZLES],
    "forward_pod_muzzles": [_pt(p) for p in FPOD_MUZZLES],
    "smoke": [_pt((s * NAC_X, -3.26, NAC_Z + 0.06)) for s in (1, -1)],
    "main_wheels": [_pt((s * MAIN_WHEEL[0], MAIN_WHEEL[1], MAIN_WHEEL[2])) for s in (1, -1)],
    "nose_wheels": _pt((0, NOSE_WHEEL[1], NOSE_WHEEL[2])),
    "boom_joint": _pt(BOOM_JOINT),
    "door_hinges": {k: dict(_pt(v), axis="z") for k, v in DOOR_HINGE.items()},
    "ramp_hinge": dict(_pt(RAMP_HINGE), axis="x"),
    "cabin_floor_z_m": CABIN_FLOOR,
    "seats": [_pt(p) for p in SEATS],
    "canopy_glass_palette_index": CI["canopy_glass"],
}

if __name__ == "__main__":
    for name, vox in PARTS.items():
        comps = components(vox)
        print(f"{name}: {sum(comps)} vox, components {len(comps)} {comps[:4]}")
    vs = list(airframe)
    for i, ax in enumerate("xyz"):
        lo, hi = min(v[i] for v in vs), max(v[i] for v in vs)
        print(f"airframe {ax}: voxels {lo}..{hi}  m {lo * VOXEL_M:.2f}..{(hi + 1) * VOXEL_M:.2f}")
    if "--write" in sys.argv:
        pdir = os.path.join(HERE, "out", "chopper_raven9_v1")
        os.makedirs(pdir, exist_ok=True)
        LANDMARKS["parts"] = {}
        for name, vox in PARTS.items():
            off = write_vox(os.path.join(pdir, f"ingame-chopper-raven9-v1-{name}.vox"), vox)
            LANDMARKS["parts"][name] = {"file_offset": list(off)}
        with open(os.path.join(pdir, "ingame_chopper_raven9_v1_landmarks.json"), "w") as f:
            json.dump(LANDMARKS, f, indent=2)
    print(json.dumps({k: LANDMARKS[k] for k in ("nose_tip", "rotor", "tailrotor", "gun", "door_hinges", "ramp_hinge")}, indent=1))
