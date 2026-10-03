#!/usr/bin/env python3
"""Strike Bay - long-range surveillance radar dish (Soviet P-14 "Tall King" flavor).

A big, impressive early-warning array on a tapered concrete tower, built at
real scale against the 1.5 m infantryman (25 voxels): the dish is ~27 m across,
the tower top ~11.7 m, total height ~29 m.

Parts (z-up, dish faces +y at 0 deg traverse):
  radar_dish_pedestal_v1.vox  static: battered concrete tower (4 stepped
                              bands), buried ops room + upper equipment room,
                              door + steps, slit windows, cable trunking,
                              ladder, rotation deck with race ring + railing
  radar_dish_array_v1.vox     traverse: rotating platform, yoke A-frame with
                              trunnion drums, big truss-backed parabolic dish
                              (reflector face + lattice backing + rim tube),
                              feed horn on quadripod + cable loom
                              (rotates 360 deg about z at TRAVERSE_PIVOT)
  radar_dish_assembled_v1.vox merged pedestal + array at 0 deg (preview)

Rig pivot (file coords, x right / y forward / z up):
  TRAVERSE_PIVOT = (0, 0, 90)  z-axis; parent the array part here.
Elevation is FIXED at 28 deg (authored in place) - this is a surveillance
radar: the game rotates azimuth only, never elevation.

Rotation clearance (verified numerically in __main__): the array's lowest
sweeping voxels stay above the static deck/railing; the yoke feet orbit at
r=24 inside the railing (r=31) and the race ring (r=31..33).

Scale: FACTORY_VOXEL 0.13 m/voxel (structure class, same as farm buildings).
"""
import os
import math
import struct
from PIL import Image, ImageDraw

PALETTE = [
    ("concrete",       (138, 132, 120)),
    ("concrete_dark",  (102,  97,  86)),
    ("concrete_light", (168, 162, 150)),
    ("steel",          (148, 156, 138)),   # weathered sage truss paint
    ("steel_dark",     (108, 114, 100)),
    ("reflector",      (122, 126, 106)),   # dish face panels
    ("reflector_dark", ( 96, 100,  84)),
    ("dark",           ( 28,  28,  30)),   # cables, racks
    ("rust",           (142,  86,  52)),
    ("white",          (232, 230, 224)),   # markings, lights
    ("window",         ( 24,  34,  44)),
    ("red",            (200,  42,  36)),   # obstruction light
]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

TRAVERSE_PIVOT = (0, 0, 90)
TILT_DEG = 28

pedestal = {}
array = {}
face_tags = set()   # reflector-shell voxels: heal may not bridge these to the truss


# ---------------------------------------------------------------- builders
def box(d, x0, x1, y0, y1, z0, z1, c):
    """Exclusive upper bounds."""
    ci = CI[c]
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                d[(x, y, z)] = ci


def cyl_z(d, cx, cy, r, z0, z1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for y in range(cy - r, cy + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                for z in range(z0, z1):
                    d[(x, y, z)] = ci


def ring_z(d, cx, cy, r, z0, z1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for y in range(cy - r, cy + r + 1):
            dd = (x - cx) ** 2 + (y - cy) ** 2
            if (r - 1) ** 2 < dd <= r * r:
                for z in range(z0, z1):
                    d[(x, y, z)] = ci


def line3(d, p0, p1, t, c):
    """3D line with square t×t cross-section (cross-section in the two
    non-dominant axes)."""
    ci = CI[c]
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    n = int(max(abs(dx), abs(dy), abs(dz)))
    if n == 0:
        n = 1
    adx, ady, adz = abs(dx), abs(dy), abs(dz)
    dom = 0 if adx >= ady and adx >= adz else (1 if ady >= adz else 2)
    axes = [0, 1, 2]
    axes.remove(dom)
    h = t // 2
    for i in range(n + 1):
        s = i / n
        x = int(round(x0 + dx * s))
        y = int(round(y0 + dy * s))
        z = int(round(z0 + dz * s))
        for o1 in range(-h, -h + t):
            for o2 in range(-h, -h + t):
                p = [x, y, z]
                p[axes[0]] += o1
                p[axes[1]] += o2
                d[(p[0], p[1], p[2])] = ci


def _norm(v):
    l = math.sqrt(sum(c * c for c in v))
    return tuple(c / l for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def cyl_axis(d, p0, axis, r, length, c):
    """Cylinder from p0 along unit axis."""
    ci = CI[c]
    ax = _norm(axis)
    ref = (0, 0, 1) if abs(ax[2]) < 0.9 else (0, 1, 0)
    b1 = _norm(_cross(ax, ref))
    b2 = _cross(ax, b1)
    for s in range(int(length) + 1):
        cx = p0[0] + ax[0] * s
        cy = p0[1] + ax[1] * s
        cz = p0[2] + ax[2] * s
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                if i * i + j * j <= r * r:
                    x = int(round(cx + b1[0] * i + b2[0] * j))
                    y = int(round(cy + b1[1] * i + b2[1] * j))
                    z = int(round(cz + b1[2] * i + b2[2] * j))
                    d[(x, y, z)] = ci


def weather(d, x0, x1, y0, y1, z0, z1, c):
    """Sparse deterministic weathering speckle inside a box region."""
    ci = CI[c]
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                if (x, y, z) in d and (x * 73856093 ^ y * 19349663 ^ z * 83492791) % 13 == 0:
                    d[(x, y, z)] = ci

# ================================================================ PEDESTAL (static)
# Battered concrete tower: 4 stepped bands, 2-thick walls, hollow.
BANDS = [(0, 22, 36), (22, 44, 34), (44, 66, 32), (66, 88, 30)]


def band_walls(z0, z1, hw):
    # 4 walls, 2 thick; face planes at +/-hw
    box(pedestal, -hw, hw, hw - 2, hw, z0, z1, "concrete")      # +y
    box(pedestal, -hw, hw, -hw, -hw + 2, z0, z1, "concrete")    # -y
    box(pedestal, hw - 2, hw, -hw, hw, z0, z1, "concrete")      # +x
    box(pedestal, -hw, -hw + 2, -hw, hw, z0, z1, "concrete")    # -x
    # proud course lip at the band top
    box(pedestal, -hw - 1, hw + 1, hw - 1, hw + 1, z1 - 1, z1 + 1, "concrete_light")
    box(pedestal, -hw - 1, hw + 1, -hw - 1, -hw + 1, z1 - 1, z1 + 1, "concrete_light")
    box(pedestal, hw - 1, hw + 1, -hw, hw, z1 - 1, z1 + 1, "concrete_light")
    box(pedestal, -hw - 1, -hw + 1, -hw, hw, z1 - 1, z1 + 1, "concrete_light")


for z0, z1, hw in BANDS:
    band_walls(z0, z1, hw)

# transition collars: each narrower band seats on a perimeter ring at the wider
# band's footprint (also serve as interior floor plates)
def collar(z0, z1, hw):
    box(pedestal, -hw, hw, hw - 4, hw, z0, z1, "concrete")
    box(pedestal, -hw, hw, -hw, -hw + 4, z0, z1, "concrete")
    box(pedestal, hw - 4, hw, -hw, hw, z0, z1, "concrete")
    box(pedestal, -hw, -hw + 4, -hw, hw, z0, z1, "concrete")


collar(21, 24, 36)
collar(43, 46, 34)
collar(65, 68, 32)

# base plinth
box(pedestal, -38, 38, -38, 38, 0, 3, "concrete_dark")

# ---- ground-floor ops room (buried interior, revealed by damage)
box(pedestal, -34, 34, -34, 34, 0, 2, "concrete_dark")          # floor slab
box(pedestal, -34, 34, -34, 34, 18, 20, "concrete_dark")        # ceiling slab
for sx in (-1, 1):                                              # wall liners
    box(pedestal, 24 * sx - (1 if sx > 0 else 0), 24 * sx + (0 if sx > 0 else 1),
        -24, 24, 2, 18, "concrete")
box(pedestal, -24, 24, -24, -23, 2, 18, "concrete")
box(pedestal, -24, -3, 23, 24, 2, 18, "concrete")               # +y liner, door gap
box(pedestal, 3, 24, 23, 24, 2, 18, "concrete")
box(pedestal, -3, 3, 23, 24, 12, 18, "concrete")               # header over door
for lx in range(-20, 21, 8):                                   # ceiling light strips
    box(pedestal, lx, lx + 3, -2, 2, 17, 18, "white")
for rx in (-18, -6, 8):                                       # equipment racks
    box(pedestal, rx, rx + 8, -22, -18, 2, 12, "dark")
    box(pedestal, rx, rx + 8, -22, -18, 12, 13, "steel_dark")
box(pedestal, 12, 20, 8, 16, 2, 10, "dark")                   # console block
box(pedestal, 12, 20, 8, 9, 10, 14, "window")                 # console screen glow

# ---- upper equipment room
box(pedestal, -30, 30, -30, 30, 44, 46, "concrete_dark")
box(pedestal, -30, 30, -30, 30, 60, 62, "concrete_dark")
box(pedestal, -16, 16, -16, 16, 46, 60, "concrete")            # solid core w/ room carved
for x in range(-12, 13):
    for y in range(-12, 13):
        for z in range(48, 58):
            pedestal.pop((x, y, z), None)
box(pedestal, -12, 12, -12, 12, 47, 48, "steel_dark")          # floor plate
for vx in (-8, 0, 8):
    box(pedestal, vx, vx + 4, -12, -11, 48, 56, "dark")        # vent racks

# ---- door on +y face (band1 face at y=36) + steps
for x in range(-4, 5):
    for z in range(2, 15):
        for y in (34, 35, 36):
            pedestal[(x, y, z)] = CI["dark"]                   # recess
box(pedestal, -3, 4, 35, 36, 2, 13, "steel_dark")              # door slab
box(pedestal, -2, 3, 35, 36, 8, 11, "window")                 # door glazing
box(pedestal, 2, 3, 35, 36, 4, 6, "dark")                     # handle
for k in range(5):                                            # steps down +y
    box(pedestal, -5, 6, 37 + 2 * k, 39 + 2 * k, 0, 10 - 2 * k, "concrete_light")

# ---- slit windows on band3 (faces at +/-32), 3 per face
for wx in (-19, -3, 13):
    for y in (30, 31):
        for z in range(54, 59):
            pedestal[(wx, y, z)] = CI["window"]
            pedestal[(wx, -31, z)] = CI["window"]
            pedestal[(wx, -32, z)] = CI["window"]
for wz in range(54, 59):
    for wy in (-19, -3, 13):
        for x in (30, 31):
            pedestal[(x, wy, wz)] = CI["window"]
            pedestal[(-31, wy, wz)] = CI["window"]
            pedestal[(-32, wy, wz)] = CI["window"]

# ---- cable trunking down the +x face + junction boxes
box(pedestal, 36, 39, -10, -6, 0, 44, "dark")
box(pedestal, 34, 37, -10, -6, 44, 66, "dark")
box(pedestal, 36, 40, -12, -4, 20, 26, "steel_dark")
box(pedestal, 34, 38, -12, -4, 50, 56, "steel_dark")

# ---- ladder up the -y face, stepped per band to hug the batter
for z0, z1, hw in BANDS:
    for z in range(z0, z1):
        pedestal[(-2, -hw, z)] = CI["steel_dark"]
        pedestal[(2, -hw, z)] = CI["steel_dark"]
    for z in range(z0 + 2, z1, 3):
        for x in range(-2, 3):
            pedestal[(x, -hw, z)] = CI["steel_dark"]

# ---- rotation deck
box(pedestal, -32, 33, -32, 33, 88, 90, "concrete")            # deck slab
box(pedestal, -33, 34, -33, -32, 90, 91, "concrete_light")     # deck edge lip
box(pedestal, -33, 34, 32, 34, 90, 91, "concrete_light")       # (frame strips only:
box(pedestal, -33, -32, -33, 34, 90, 91, "concrete_light")     #  the rotating
box(pedestal, 32, 34, -33, 34, 90, 91, "concrete_light")       #  platform needs z90)
ring_z(pedestal, 0, 0, 32, 90, 92, "dark")                     # race ring (static gear)
# railing posts + top rail around the deck edge (kept below the yoke sweep)
for x in range(-31, 32, 8):
    for y in (-31, 31):
        box(pedestal, x, x + 1, y, y + 1, 91, 94, "steel_dark")
        box(pedestal, y, y + 1, x, x + 1, 91, 94, "steel_dark")
box(pedestal, -31, 32, -31, -30, 93, 94, "steel_dark")
box(pedestal, -31, 32, 31, 32, 93, 94, "steel_dark")
box(pedestal, -31, -30, -31, 32, 93, 94, "steel_dark")
box(pedestal, 31, 32, -31, 32, 93, 94, "steel_dark")

# ---- weathering: speckle + rust streaks under the deck lip (band4 faces)
weather(pedestal, -38, 38, -38, 38, 0, 88, "concrete_dark")
for rx, ry in [(-20, 29), (5, 29), (24, 28), (28, -14), (-28, 10), (12, -29)]:
    for z in range(70, 87):
        if (rx, ry, z) in pedestal and (rx * 31 + z * 17) % 3 == 0:
            pedestal[(rx, ry, z)] = CI["rust"]

# ================================================================ ARRAY (traverse about z at (0,0,90))
TILT = math.radians(TILT_DEG)
AX = (0.0, math.cos(TILT), math.sin(TILT))          # dish axis: forward + up
E1 = (1.0, 0.0, 0.0)
E2 = (0.0, -math.sin(TILT), math.cos(TILT))
C = (0.0, 8.0, 162.0)                              # dish vertex center
HW, HH, FOC = 104.0, 62.0, 85.0                    # half-width, half-height, focal length


def dish_point(u, v, w=0.0):
    ww = (u * u + v * v) / (4 * FOC) + w
    return (C[0] + u * E1[0] + v * E2[0] + ww * AX[0],
            C[1] + u * E1[1] + v * E2[1] + ww * AX[1],
            C[2] + u * E1[2] + v * E2[2] + ww * AX[2])


def dip(p):
    return (int(round(p[0])), int(round(p[1])), int(round(p[2])))


# ---- rotating platform (sits on the deck, inside the race ring)
cyl_z(array, 0, 0, 30, 90, 93, "steel_dark")
ring_z(array, 0, 0, 30, 93, 94, "steel")
for a in range(0, 360, 12):                                    # drive teeth under rim
    gx = int(round(28 * math.cos(math.radians(a))))
    gy = int(round(28 * math.sin(math.radians(a))))
    box(array, gx - 1, gx + 2, gy - 1, gy + 2, 90, 91, "dark")
box(array, 10, 22, -20, -10, 93, 101, "steel")                 # drive cabinet
box(array, 10, 22, -20, -10, 101, 102, "steel_dark")
for vx in range(12, 21, 3):
    box(array, vx, vx + 1, -20, -19, 95, 99, "dark")            # cabinet vents

# ---- yoke A-frame: feet on the platform -> trunnions at the dish flanks
TRUN = (92.0, 8.0, 162.0)
for s in (-1, 1):
    line3(array, (s * 24, 0, 90), (s * TRUN[0], TRUN[1], TRUN[2]), 4, "steel")
    # trunnion drum (axis along x), seated on the arm end
    if s > 0:
        x0t, x1t = 80, 91
    else:
        x0t, x1t = -90, -79
    for y in range(int(TRUN[1]) - 6, int(TRUN[1]) + 7):
        for z in range(int(TRUN[2]) - 6, int(TRUN[2]) + 7):
            if (y - TRUN[1]) ** 2 + (z - TRUN[2]) ** 2 <= 36:
                for x in range(x0t, x1t):
                    array[(x, y, z)] = CI["steel_dark"]
# elevation axle stubs: drums -> hub, tucked 3 vox behind the face vertex
# (y=8, z=158 clears the vertex at (0,8,162); ends meet the hub r=8)
box(array, 8, 91, 6, 10, 156, 160, "steel")
box(array, -90, -7, 6, 10, 156, 160, "steel")
# cross beam between the arms + equipment boxes riding it
line3(array, (-58, 4, 126), (58, 4, 126), 3, "steel_dark")
box(array, -14, -4, 0, 8, 126, 134, "steel")
box(array, 6, 16, 0, 8, 126, 133, "steel_dark")

# ---- reflector face: paraboloid shell, 2 thick along the axis
for u in range(-int(HW), int(HW) + 1):
    for v in range(-int(HH), int(HH) + 1):
        if (u / HW) ** 2 + (v / HH) ** 2 > 1:
            continue
        if u % 16 == 0 or v % 16 == 0:
            col = "reflector_dark"                              # panel seams
        else:
            col = "reflector"
        p = dip(dish_point(u, v, 0.0))
        q = dip(dish_point(u, v, 1.0))
        array[p] = CI[col]
        array[q] = CI[col]
        face_tags.add(p)
        face_tags.add(q)

# ---- rim tube around the dish edge
rim_pts = []
for adeg in range(0, 360, 2):
    a = math.radians(adeg)
    rim_pts.append(dip(dish_point(HW * math.cos(a), HH * math.sin(a), 0.0)))
for i in range(len(rim_pts)):
    line3(array, rim_pts[i], rim_pts[(i + 1) % len(rim_pts)], 3, "steel")

# ---- lattice backing: hub + radial spokes + ring trusses + diagonals
HUB = dish_point(0, 0, -6.0)


def rim_at(adeg):
    a = math.radians(adeg)
    return dish_point(HW * math.cos(a), HH * math.sin(a), -1.0)


cyl_axis(array, (HUB[0], HUB[1] - 6 * AX[1], HUB[2] - 6 * AX[2]), AX, 8, 12, "steel_dark")
box(array, -8, 9, -8, 9, 144, 158, "steel")                    # back equipment box (on hub)
for s in range(16):                                             # radial spokes
    rp = rim_at(s * 22.5)
    dvec = (rp[0] - HUB[0], rp[1] - HUB[1], rp[2] - HUB[2])
    l = math.sqrt(sum(c * c for c in dvec))
    sp = (HUB[0] + dvec[0] / l * 8, HUB[1] + dvec[1] / l * 8, HUB[2] + dvec[2] / l * 8)
    line3(array, sp, rp, 2, "steel")
for t in (0.35, 0.6, 0.85):                                     # ring trusses
    ring = []
    for adeg in range(0, 360, 4):
        rp = rim_at(adeg)
        hp = (HUB[0] + (rp[0] - HUB[0]) * t,
              HUB[1] + (rp[1] - HUB[1]) * t,
              HUB[2] + (rp[2] - HUB[2]) * t)
        ring.append(hp)
    for i in range(len(ring)):
        line3(array, ring[i], ring[(i + 1) % len(ring)], 2, "steel")
    if t < 0.8:                                                 # diagonals to next ring
        t2 = {0.35: 0.6, 0.6: 0.85}[t]
        for adeg in range(0, 360, 12):
            r1 = rim_at(adeg)
            r2 = rim_at(adeg + 12)
            p1 = (HUB[0] + (r1[0] - HUB[0]) * t, HUB[1] + (r1[1] - HUB[1]) * t,
                  HUB[2] + (r1[2] - HUB[2]) * t)
            p2 = (HUB[0] + (r2[0] - HUB[0]) * t2, HUB[1] + (r2[1] - HUB[1]) * t2,
                  HUB[2] + (r2[2] - HUB[2]) * t2)
            line3(array, p1, p2, 1, "steel_dark")

# ---- feed horn at the focal point + quadripod + cable
# (chunky canister per the painting: r=7 barrel, flared mouth, white tip band)
FEED = dish_point(0, 0, FOC)
cyl_axis(array, (FEED[0] - 10 * AX[0], FEED[1] - 10 * AX[1], FEED[2] - 10 * AX[2]),
         AX, 7, 20, "steel_dark")
cyl_axis(array, (FEED[0] - 3 * AX[0], FEED[1] - 3 * AX[1], FEED[2] - 3 * AX[2]),
         AX, 7, 6, "white")                                     # tip band
cyl_axis(array, (FEED[0] + 10 * AX[0], FEED[1] + 10 * AX[1], FEED[2] + 10 * AX[2]),
         AX, 9, 6, "steel_dark")                                # flared mouth
for adeg in (45, 135, 225, 315):                                # quadripod struts
    rp = rim_at(adeg)
    line3(array, rp, FEED, 3, "steel_dark")
# cable bundles: hub -> draped along the right yoke arm -> platform foot
# (two parallel 3-wide runs; the painting's thick cable bundles, not a scratch)
line3(array, (0, 4, 158), (28, 6, 104), 3, "dark")
line3(array, (28, 6, 104), (24, 3, 93), 3, "dark")
line3(array, (5, 4, 158), (33, 6, 104), 3, "dark")
line3(array, (33, 6, 104), (29, 3, 93), 3, "dark")

# ---- red obstruction light on the top rim (dark base + lens, not a debug cube)
top_rim = dip(dish_point(0, HH, 1.0))
box(array, top_rim[0] - 1, top_rim[0] + 2, top_rim[1] - 1, top_rim[1] + 2,
    top_rim[2], top_rim[2] + 1, "dark")
box(array, top_rim[0], top_rim[0] + 2, top_rim[1], top_rim[1] + 2,
    top_rim[2] + 1, top_rim[2] + 3, "red")

# ---------------------------------------------------------------- .vox writer (MagicaVoxel 150)
def write_vox(path, vox, PALETTE):
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    sx, sy, sz = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) + 1
    xoff, yoff = -min(xs), -min(ys)
    size_content = struct.pack("<iii", sx, sy, sz)
    xyzi = struct.pack("<i", len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("BBBB", x + xoff, y + yoff, z, ci)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in PALETTE)
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(PALETTE))
    main_children = chunk(b"SIZE", size_content) + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)
    with open(path, "wb") as f:
        f.write(b"VOX ")
        f.write(struct.pack("<i", 150))
        f.write(chunk(b"MAIN", b"", main_children))
    print(f"wrote {path} ({len(vox)} voxels)")


# ---------------------------------------------------------------- isometric preview render
def render_preview(path, vox, PALETTE, scale=2):
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    W2, H2, ZH = 0.8660254, 0.5, 1.0
    def proj(x, y, z):
        return ((x - y) * W2 * scale, ((x + y) * H2 - z * ZH) * scale)
    corners = [(min(xs), min(ys), min(zs)), (max(xs), min(ys), min(zs)),
               (min(xs), max(ys), min(zs)), (max(xs), max(ys), min(zs)),
               (min(xs), min(ys), max(zs)), (max(xs), max(ys), max(zs))]
    px = [proj(*c)[0] for c in corners]; py = [proj(*c)[1] for c in corners]
    ox, oy = -min(px) + 20 * scale, -min(py) + 20 * scale
    img = Image.new("RGB", (int(max(px) - min(px)) + 40 * scale, int(max(py) - min(py)) + 40 * scale),
                    (13, 20, 30))
    dr = ImageDraw.Draw(img)
    shades = {}
    for i, (_, (r, g, b)) in enumerate(PALETTE):
        shades[i + 1] = ((r, g, b),
                         (int(r * 0.78), int(g * 0.78), int(b * 0.78)),
                         (int(r * 0.60), int(g * 0.60), int(b * 0.60)))
    vset = set(vox.keys())
    surf = [p for p in vset
            if (p[0] + 1, p[1], p[2]) not in vset or (p[0], p[1] + 1, p[2]) not in vset
            or (p[0], p[1], p[2] + 1) not in vset]
    surf.sort(key=lambda p: (p[0] + p[1] + p[2], p[2]))
    for (x, y, z) in surf:
        top, left, right = shades[vox[(x, y, z)]]
        if (x, y, z + 1) not in vset:
            pts = [proj(x, y, z + 1), proj(x + 1, y, z + 1),
                   proj(x + 1, y + 1, z + 1), proj(x, y + 1, z + 1)]
            dr.polygon([(px_ + ox, py_ + oy) for px_, py_ in pts], fill=top)
        if (x, y + 1, z) not in vset:
            pts = [proj(x, y + 1, z), proj(x + 1, y + 1, z),
                   proj(x + 1, y + 1, z + 1), proj(x, y + 1, z + 1)]
            dr.polygon([(px_ + ox, py_ + oy) for px_, py_ in pts], fill=left)
        if (x + 1, y, z) not in vset:
            pts = [proj(x + 1, y, z), proj(x + 1, y + 1, z),
                   proj(x + 1, y + 1, z + 1), proj(x + 1, y, z + 1)]
            dr.polygon([(px_ + ox, py_ + oy) for px_, py_ in pts], fill=right)
    img.save(path)
    print(f"wrote {path} {img.size}")


# ---------------------------------------------------------------- top-down slice (dev check for buried interiors)
def render_slice(path, vox, PALETTE, z):
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]
    img = Image.new("RGB", ((max(xs) + 1) * 2, (max(ys) - min(ys) + 1) * 2), (13, 20, 30))
    px = img.load()
    yoff = -min(ys)
    for (x, y, zz), ci in vox.items():
        if zz == z:
            r, g, b = PALETTE[ci - 1][1]
            for dx in range(2):
                for dy in range(2):
                    px[x * 2 + dx, (y + yoff) * 2 + dy] = (r, g, b)
    img.save(path)
    print(f"wrote {path} {img.size}")


def heal_components(vox, no_bridge=None):
    """Add the minimal bridge voxels needed to make the part 6-connected:
    only bridge 26-neighbor pairs that lie in different components.
    If no_bridge is a set of tagged voxels, never bridge a tagged voxel to
    an untagged one (keeps the reflector face free of truss smear)."""
    from collections import deque
    total = 0
    for _ in range(8):
        comp = {}
        cid = 0
        for seed in vox:
            if seed in comp:
                continue
            cid += 1
            q = deque([seed])
            comp[seed] = cid
            while q:
                x, y, z = q.popleft()
                for nb in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                           (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                    if nb in vox and nb not in comp:
                        comp[nb] = cid
                        q.append(nb)
        if cid == 1:
            break
        s = set(vox)
        add = {}
        for (x, y, z) in s:
            c0 = comp[(x, y, z)]
            t0 = (x, y, z) in no_bridge if no_bridge else False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        if dx == 0 and dy == 0 and dz == 0:
                            continue
                        q = (x + dx, y + dy, z + dz)
                        if q not in s or comp[q] == c0:
                            continue
                        if no_bridge and t0 != (q in no_bridge):
                            continue
                        cx, cy, cz = x, y, z
                        for ax_i, d in ((0, dx), (1, dy), (2, dz)):
                            if d == 0:
                                continue
                            if ax_i == 0:
                                cx += d
                            elif ax_i == 1:
                                cy += d
                            else:
                                cz += d
                            if (cx, cy, cz) != q and (cx, cy, cz) not in s:
                                add[(cx, cy, cz)] = vox[(x, y, z)]
                            if (cx, cy, cz) == q:
                                break
        if not add:
            break
        vox.update(add)
        total += len(add)
    return total


def check_components(name, vox, must_touch_ground):
    from collections import deque
    vset = set(vox)
    seen = set()
    comps = 0
    floaters = 0
    for seed in vset:
        if seed in seen:
            continue
        comps += 1
        q = deque([seed]); seen.add(seed)
        touches = seed[2] == 0
        size = 0
        while q:
            x, y, z = q.popleft(); size += 1
            for nb in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                       (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if nb in vset and nb not in seen:
                    seen.add(nb); q.append(nb)
                    if nb[2] == 0:
                        touches = True
        if not touches:
            floaters += size
    print(f"{name}: {comps} component(s), {floaters} floater voxels ({len(vox)} total)")
    if must_touch_ground and floaters:
        print(f"  !! {name} has detached floaters")
    if not must_touch_ground and comps != 1:
        print(f"  !! {name} should be a single component (rides the pedestal)")


def check_rotation_clearance():
    """Rotate the array 90/180/270 deg about TRAVERSE_PIVOT and require zero
    voxel overlap with the static pedestal. Also report the lowest array
    voxel over the tower footprint."""
    px, py, pz = TRAVERSE_PIVOT
    pset = set(pedestal)
    for deg in (90, 180, 270):
        rad = math.radians(deg)
        cosr, sinr = round(math.cos(rad)), round(math.sin(rad))
        hit = 0
        for (x, y, z) in array:
            rx = px + (x - px) * cosr - (y - py) * sinr
            ry = py + (x - px) * sinr + (y - py) * cosr
            if (rx, ry, z) in pset:
                hit += 1
                if hit <= 5:
                    print(f"  collision at {deg} deg: array ({x},{y},{z})")
        print(f"traverse {deg} deg: {hit} colliding voxels")
    low = min(z for (x, y, z) in array if math.hypot(x - px, y - py) < 38)
    print(f"lowest array voxel over tower footprint (r<38): z={low} (railing top z=96)")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    print("heal pedestal: +", heal_components(pedestal), "bridge voxels")
    print("heal array: +", heal_components(array, face_tags), "bridge voxels")
    PARTS = {
        "radar_dish_pedestal_v1": (pedestal, True),
        "radar_dish_array_v1": (array, False),
    }
    for name, (d, grounded) in PARTS.items():
        write_vox(os.path.join(here, name + ".vox"), d, PALETTE)
        render_preview(os.path.join(here, name + "_preview.png"), d, PALETTE)
        check_components(name, d, grounded)
    assembled = dict(pedestal)
    assembled.update(array)
    write_vox(os.path.join(here, "radar_dish_assembled_v1.vox"), assembled, PALETTE)
    render_preview(os.path.join(here, "radar_dish_assembled_v1_preview.png"), assembled, PALETTE)
    render_slice(os.path.join(here, "radar_dish_ops_room_slice.png"), pedestal, PALETTE, 10)
    check_rotation_clearance()
    # palette audit
    used = set(pedestal.values()) | set(array.values())
    print("palette entries used:", len(used), "/", len(PALETTE))
