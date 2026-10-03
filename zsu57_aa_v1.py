#!/usr/bin/env python3
"""Strike Bay — ZSU-57-2 style turret with a single long-barrel cannon for the
existing ZSU motorized base (v3 — the AA gunner ROTATES WITH the pintle MG).

Drop-in replacement turret + gun parts for the zsu_hull_v1 / zsu_tracks_v1 base,
grounded in the late-1950s / 1960s Soviet look: big rounded cast turret, single
long-barrel cannon painted hull olive with a muzzle brake and fume extractor,
canvas mantlet cover.

Authored DIRECTLY in the on-disk .vox coordinate frame of zsu_hull_v1.vox and
zsu_tracks_v1.vox (no frame offset — verified against the shipped files: ring
seat centroid (17,30) at z=16, elevation shaft axis (17,45..46,23)), so the new
parts composite exactly with the existing base.

  zsu57_turret_v1.vox  traverse: turret basket, stepped cast turret body,
                       mantlet housing with elevation slot + trunnion drum,
                       ventilator dome, hatches, periscopes, stowage boxes,
                       SHORTENED whip antenna, LEFT hatch OPEN with coaming
                       ring + static traverse RACE ring + lid folded flat to
                       port  (rotates about the vertical axis)
  zsu57_pintle_v1.vox pintle traverse: toothed traverse ring riding in the
                       race, yoke fork arms, AND the gunner torso (waist-up
                       infantryman in SSh-40 helmet, hands ON the MG spade
                       grips) — the whole assembly rotates together, like a
                       commander's AA ring  (rotates about the z-axis at
                       PINTLE_PIVOT, child of the traverse node)
  zsu57_mg_v1.vox     MG elevation: DShK-style 12.7mm — spade grips, receiver,
                       barrel shroud, long barrel, muzzle brake, front/rear
                       sights, ammo box  (rotates about the x-axis at
                       MG_PIVOT, child of the pintle node)
  zsu57_guns_v1.vox    elevation: pivot shaft, cradle, breech, canvas mantlet
                       cover, single long-barrel olive cannon with muzzle
                       brake and fume extractor, gunner
                       sight  (rotates about the horizontal axis)

Rig pivots (file coords, x right / y forward / z up):
  TRAVERSE_PIVOT  = (17, 30, 16)   z-axis; parent the turret part here
  ELEVATION_PIVOT = (17, 46, 23)   x-axis; parent the guns part here,
                                  as a child of the traverse node
  PINTLE_PIVOT    = (9, 28, 33)    z-axis; parent the pintle part here,
                                  as a child of the traverse node.
                                  NOTE: v2 used (9, 34, 33) with a STATIC
                                  torso. A rotating torso at the hatch
                                  (9,28) orbits at r~6 about (9,34) and
                                  collides with the ventilator dome at 71/72
                                  traverse angles (verified numerically) —
                                  so v3 moves the pivot to the hatch center.
                                  The gunner now swings with the gun, like
                                  the user's reference photo.
  MG_PIVOT        = (9, 35, 39)    x-axis; parent the MG part here,
                                  as a child of the pintle node

Verified articulation (voxel sweep tests, file coords):
  Pintle traverse: full 360 deg about z at PINTLE_PIVOT — zero collisions
                   with the turret (hatch lid, coaming, race, ventilator
                   dome, periscopes, antenna) and with the main gun at
                   elevations -10..+60 deg. Torso sweep max r ~4.3 (helmet
                   brim) clears the dome vertically (dome top z33).
  MG elevation: -40 deg .. +80 deg about x at MG_PIVOT — zero new
                   collisions vs the turret at any angle; vs the pintle only
                   2-4 voxels per angle inside the cradle/fork-arm bearing
                   (by-design seating, same character as the 0-deg baseline)
                   plus a 2-voxel graze of the receiver against the gunner's
                   forearms at +20..+40 deg (reads as the gun braced against
                   him). Suggested game clamp approx -10 .. +70 deg. Hands
                   stay on the grips at 0 deg; slight separation at extreme
                   elevation is expected.
  Main gun (-10 .. +60 deg about ELEVATION_PIVOT) vs pintle+MG: zero
                   collisions at 0 deg pintle traverse.

Guns are authored horizontal (0 deg elevation, pointing +y) — the rigging
neutral. Turret underside clears the hull top (deck top z=17/18) with the same
1-voxel convention as the shipped turret part; the basket (r8) seats on the
ring race (hull top z=15 in the ring area).

Scale: TURRET_VOXEL 0.09 m/voxel, same as the base.
"""
import os

PALETTE = [
    ("olive",        ( 99, 102,  71)),  # 1  Soviet protective green
    ("olive_dark",   ( 72,  75,  52)),  # 2  olive shadow
    ("gunmetal",     ( 56,  58,  62)),  # 3  barrels, receiver furniture
    ("gunmetal_dark",( 36,  38,  42)),  # 4  muzzle brake, track frame
    ("steel",        (122, 126, 134)),  # 5  bright hardware, tread links
    ("steel_dark",   ( 62,  64,  72)),  # 6  wheels hubs, chutes
    ("dark",         ( 28,  30,  34)),  # 7  track pads, bore, deep shadow
    ("rubber",       ( 22,  22,  24)),  # 8  road-wheel tires
    ("brass",        (168, 134,  72)),  # 9  ammo hint
    ("glass",        (120, 160, 180)),  # 10 periscopes / sight
    ("rust",         (110,  70,  45)),  # 11 exhaust stain
    ("canvas",       (134, 124,  98)),  # 12 mantlet dust cover (khaki-tan)
    ("jacket",       ( 60,  68,  36)),  # 13 gunner uniform (infantry palette)
    ("jacket_dark",  ( 45,  52,  28)),  # 14 uniform shadow
    ("skin",         (222, 158, 112)),  # 15 gunner skin (infantry palette)
    ("skin_shadow",  (170, 110,  85)),  # 16 skin shadow
    ("helmet",       (128, 128,  76)),  # 17 SSh-40 helmet (infantry palette)
    ("helmet_brim",  (102, 102,  61)),  # 18 helmet brim shadow
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

TRAVERSE_PIVOT = (17, 30, 16)
ELEVATION_PIVOT = (17, 46, 23)
PINTLE_PIVOT = (9, 28, 33)
MG_PIVOT = (9, 35, 39)

turret = {}
guns = {}
pintle = {}
mg = {}

def box(d, x0, x1, y0, y1, z0, z1, c):
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

def cyl_x(d, cy, cz, r, x0, x1, c):
    ci = CI[c]
    for y in range(cy - r, cy + r + 1):
        for z in range(cz - r, cz + r + 1):
            if (y - cy) ** 2 + (z - cz) ** 2 <= r * r:
                for x in range(x0, x1):
                    d[(x, y, z)] = ci

def cyl_y(d, cx, cz, r, y0, y1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            if (x - cx) ** 2 + (z - cz) ** 2 <= r * r:
                for y in range(y0, y1):
                    d[(x, y, z)] = ci

def ring_z(d, cx, cy, r, z0, z1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for y in range(cy - r, cy + r + 1):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if (r - 1) ** 2 < d2 <= r * r:
                for z in range(z0, z1):
                    d[(x, y, z)] = ci

# ================================================================ TURRET (traverse about (17,30) z-axis)
# Big rounded cast ZSU-57-2 turret. Front = +y (guns face the glacis).
cyl_z(turret, 17, 30, 8, 16, 18, "olive")        # turret basket — seats on the ring race
ring_z(turret, 17, 30, 9, 16, 17, "olive_dark")  # race shadow collar
# cast body: stacked cylinders with dark parting seams (stepped cast look)
cyl_z(turret, 17, 30, 14, 18, 22, "olive")      # lower band
cyl_z(turret, 17, 30, 15, 22, 27, "olive")      # main band (widest)
ring_z(turret, 17, 30, 15, 22, 23, "olive_dark") # cast parting seam
cyl_z(turret, 17, 30, 14, 27, 28, "olive")      # shoulder taper
ring_z(turret, 17, 30, 14, 27, 28, "olive_dark") # cast parting seam
cyl_z(turret, 17, 30, 13, 28, 29, "olive_dark")  # roof plate
# mantlet housing (static): lower + brow leave an elevation slot (x 12..22, z 21..27)
box(turret, 8, 26, 40, 48, 19, 21, "olive")       # mantlet lower
box(turret, 8, 26, 40, 48, 27, 29, "olive")       # mantlet brow
box(turret, 8, 12, 40, 48, 19, 29, "olive")       # cheeks
box(turret, 22, 26, 40, 48, 19, 29, "olive")      # cheeks
box(turret, 10, 12, 48, 49, 21, 27, "olive_dark")  # mantlet front plate (split —
box(turret, 22, 24, 48, 49, 21, 27, "olive_dark")  #  leaves the gun slot open)
cyl_x(turret, 46, 23, 3, 10, 24, "olive_dark")     # trunnion drum (static housing)
cyl_x(turret, 46, 23, 2, 8, 10, "gunmetal_dark")   # drum end caps
cyl_x(turret, 46, 23, 2, 24, 26, "gunmetal_dark")
# roof: central ventilator dome with bolt ring (the concept's big round hatch)
cyl_z(turret, 17, 30, 6, 29, 30, "olive_dark")    # ventilator base ring
cyl_z(turret, 17, 30, 5, 30, 32, "olive")         # dome
cyl_z(turret, 17, 30, 3, 32, 33, "olive_dark")    # dome cap
for (bx, by) in ((24, 30), (10, 30), (17, 37), (17, 23),
                 (22, 35), (12, 25), (22, 25), (12, 35)):
    box(turret, bx, bx + 1, by, by + 1, 29, 30, "steel_dark")  # dome bolts
# right hatch (closed, unchanged)
box(turret, 22, 27, 26, 31, 29, 30, "olive_dark")
box(turret, 24, 25, 28, 29, 30, 31, "steel_dark")   # hatch handle
# LEFT hatch: OPEN for the AA gunner — one tall coaming/race ring (r4-5)
# the pintle's toothed traverse ring rides on, lid hinged open flat to port.
# The gunner torso now lives in the PINTLE part (rotates with the gun).
# Left hatch chosen over the right: clear of the main-gun breech/cradle
# (x12..22) and the gunner sight, with the pintle ring around it on open roof.
ring_z(turret, 9, 28, 5, 29, 33, "olive_dark")      # coaming + static race
box(turret, 1, 7, 26, 31, 29, 30, "olive")         # lid, hinged open flat to port
box(turret, 6, 7, 26, 31, 29, 31, "olive_dark")    # hinge
# periscopes around the roof edge
for (px, py) in ((9, 36), (25, 36), (9, 24), (25, 24), (17, 41), (17, 19)):
    box(turret, px, px + 1, py, py + 1, 28, 29, "olive_dark")
    box(turret, px, px + 1, py, py + 1, 29, 30, "glass")
# roof panel seams radiating from the dome
box(turret, 17, 18, 36, 42, 29, 30, "dark")
box(turret, 17, 18, 18, 24, 29, 30, "dark")
box(turret, 6, 11, 29, 30, 29, 30, "dark")
box(turret, 23, 28, 29, 30, 29, 30, "dark")
# stowage boxes on the turret flanks
for (sx0, sx1) in ((1, 4), (30, 33)):
    box(turret, sx0, sx1, 24, 36, 20, 24, "olive")
    box(turret, sx0, sx1, 24, 36, 24, 25, "olive_dark")  # lid
    box(turret, sx0, sx1, 29, 31, 21, 23, "dark")        # latch shadow
# rear stowage boxes
for (rx0, rx1) in ((6, 10), (24, 28)):
    box(turret, rx0, rx1, 15, 20, 20, 24, "olive")
    box(turret, rx0, rx1, 15, 20, 24, 25, "olive_dark")
# whip antenna on the rear-left roof — SHORTENED (top z34) so the traversing
# MG barrel (bottom z36) sweeps over it through a full 360 deg pintle traverse
box(turret, 9, 11, 20, 22, 29, 30, "olive_dark")
cyl_z(turret, 10, 21, 1, 30, 34, "dark")
# lifting eyes
for (ex, ey) in ((7, 36), (27, 36), (7, 24), (27, 24)):
    box(turret, ex, ex + 1, ey, ey + 1, 29, 30, "steel_dark")

# ================================================================ GUNS (elevation about x-axis at (17,46,23))
# Twin S-68 57mm cannons, authored horizontal (0 deg, pointing +y).
cyl_x(guns, 46, 23, 2, 8, 26, "steel_dark")      # pivot shaft — ends register
                                                        # in the drum caps; middle rides
                                                        # buried in the cradle/cover
box(guns, 11, 23, 40, 48, 21, 26, "olive_dark")  # cradle / sled
box(guns, 12, 22, 34, 42, 21, 25, "gunmetal")    # breech block
box(guns, 12, 22, 36, 44, 25, 26, "olive_dark")  # receiver top cover
# canvas mantlet cover (draped over the slot)
box(guns, 10, 24, 44, 48, 21, 26, "canvas")      # cover body
box(guns, 9, 25, 45, 48, 20, 21, "canvas")       # drape skirt
box(guns, 16, 18, 44, 48, 21, 26, "olive_dark")   # center fold shadow
# single long-barrel cannon on the bore axis (17,23) — painted hull olive per user direction
cyl_y(guns, 17, 23, 2, 44, 62, "olive")          # barrel jacket
cyl_y(guns, 17, 23, 3, 62, 70, "olive")          # fume-extractor bulge
cyl_y(guns, 17, 23, 3, 63, 64, "olive_dark")     # extractor band
cyl_y(guns, 17, 23, 3, 68, 69, "olive_dark")     # extractor band
cyl_y(guns, 17, 23, 2, 70, 88, "olive")          # long tube
cyl_y(guns, 17, 23, 2, 87, 88, "steel_dark")     # brake lock ring
cyl_y(guns, 17, 23, 3, 88, 94, "olive")          # muzzle brake
cyl_y(guns, 17, 23, 3, 90, 91, "dark")           # baffle groove
cyl_y(guns, 17, 23, 2, 93, 94, "dark")           # bore
# gunner sight riding on the canvas cover (moves with the guns)
box(guns, 11, 13, 45, 47, 26, 31, "gunmetal_dark")
box(guns, 11, 13, 47, 48, 29, 31, "glass")

# ================================================================ PINTLE (traverse about z at PINTLE_PIVOT)
# AA MG pintle mount: the gunner STANDS in the open hatch and rotates WITH
# the gun, like a classic commander's AA ring (user's reference photo).
# A toothed traverse ring rides in the static race around the hatch coaming;
# yoke fork arms rise outboard of the gunner to the MG trunnion at (9,35,39).
# The gunner torso (waist-up infantryman, SSh-40 helmet, hands ON the spade
# grips at 0 deg elevation) is part of this assembly — torso, ring, yoke and
# gun all swing together. Authored facing +y (0 deg).
# PINTLE_PIVOT = (9, 28, 33): the hatch center. The torso sweeps a tight
# circle (max r ~4.3 at the helmet brim, z38+) that clears the ventilator
# dome vertically (dome top z33); the narrowed waist (r<=1.5, z29-32) clears
# the dome's base ring and the static hatch lid folded to port.
ring_z(pintle, 9, 28, 5, 33, 34, "steel_dark")     # traverse ring (rotating)
for (tx, ty) in ((14, 28), (4, 28), (9, 33), (9, 23),
                 (12, 32), (6, 24), (12, 24), (6, 32)):
    box(pintle, tx, tx + 1, ty, ty + 1, 33, 34, "steel_dark")  # ring teeth
for (bx, by) in ((13, 28), (5, 28), (9, 32), (9, 24)):
    box(pintle, bx, bx + 1, by, by + 1, 33, 34, "steel_dark")  # ring bridges
                                                        # (6-connect the cardinals)
# yoke fork arms: rise outboard of the gunner to the trunnion. Lower segments
# merge with the gunner's chest sides — one rigid rotating assembly.
box(pintle, 7, 8, 28, 34, 33, 37, "gunmetal_dark")  # fork arm L lower
box(pintle, 10, 11, 28, 34, 33, 37, "gunmetal_dark")# fork arm R lower
box(pintle, 7, 8, 32, 36, 37, 41, "gunmetal_dark")  # fork arm L upper
box(pintle, 10, 11, 32, 36, 37, 41, "gunmetal_dark")# fork arm R upper
cyl_x(pintle, 35, 39, 1, 7, 11, "steel_dark")       # trunnion caps
# gunner torso — upright, posed with hands on the MG spade grips.
# Colors copied from the infantry_green_v2 palette; ~0.9 m waist-up at 0.09.
box(pintle, 8, 10, 27, 29, 30, 33, "jacket")       # waist (inside the coaming,
                                                        #  raised clear of the roof seam)
box(pintle, 7, 11, 26, 30, 32, 35, "jacket")       # chest
box(pintle, 8, 10, 29, 30, 32, 34, "dark")         # webbing strap
box(pintle, 7, 8, 29, 30, 33, 34, "jacket_dark")   # ammo pouch
box(pintle, 6, 12, 26, 30, 35, 36, "jacket")       # shoulders
box(pintle, 8, 9, 29, 33, 35, 38, "jacket")        # arms reaching forward-up,
box(pintle, 9, 10, 29, 33, 35, 38, "jacket")       #  inboard of the fork arms
box(pintle, 8, 10, 31, 33, 38, 39, "skin")         # hands ON the spade grips
box(pintle, 7, 11, 26, 30, 36, 38, "skin")         # head
box(pintle, 6, 12, 25, 31, 38, 39, "helmet_brim")  # SSh-40 brim
box(pintle, 7, 11, 26, 30, 39, 40, "helmet")       # SSh-40 dome

# ================================================================ MG (elevation about x at MG_PIVOT)
# DShK-style 12.7mm heavy MG, ~1.8 m overall. Authored horizontal (0 deg
# elevation, pointing +y) — the rigging neutral. The gunner's hands (in the
# pintle part) grip the spade grips at 0 deg and swing WITH the gun.
box(mg, 8, 10, 31, 33, 37, 39, "dark")             # spade grips (inboard of the
                                                        #  fork arms so they swing clear)
box(mg, 8, 10, 31, 33, 37, 40, "gunmetal_dark")   # butt
box(mg, 7, 11, 33, 39, 38, 40, "gunmetal")        # receiver
box(mg, 7, 11, 34, 38, 40, 41, "gunmetal_dark")   # top cover
box(mg, 8, 10, 32, 33, 40, 42, "gunmetal_dark")   # rear sight
cyl_y(mg, 9, 39, 1, 39, 42, "gunmetal_dark")       # barrel shroud
box(mg, 8, 10, 42, 43, 38, 40, "gunmetal_dark")    # shroud ring
cyl_y(mg, 9, 39, 1, 43, 48, "gunmetal")            # barrel
box(mg, 7, 11, 48, 51, 38, 40, "gunmetal_dark")    # DShK muzzle brake
box(mg, 8, 10, 49, 50, 38, 40, "dark")             # brake slots
cyl_y(mg, 9, 39, 1, 50, 51, "dark")                # bore
box(mg, 8, 10, 45, 46, 40, 42, "gunmetal_dark")    # front sight
box(mg, 11, 13, 34, 37, 38, 40, "olive_dark")      # ammo box (right side)
box(mg, 11, 13, 34, 37, 40, 41, "olive")           # box lid
box(mg, 11, 12, 35, 36, 40, 41, "brass")           # belt hint

PARTS = {
    "zsu57_turret_v1": turret,
    "zsu57_guns_v1": guns,
    "zsu57_pintle_v1": pintle,
    "zsu57_mg_v1": mg,
}

# ---------------------------------------------------------------- .vox writer (MagicaVoxel 150)
def write_vox(path, vox, PALETTE, xoff=None, yoff=None):
    import struct
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    if xoff is None:
        xoff, yoff = -min(xs), -min(ys)
    sx, sy, sz = max(xs) + xoff + 1, max(ys) + yoff + 1, max(zs) + 1
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

def read_vox(path):
    import struct
    data = open(path, "rb").read()
    i = data.find(b"XYZI")
    n = struct.unpack("<i", data[i + 12:i + 16])[0]
    vox = {}
    for k in range(n):
        x, y, z, c = struct.unpack("BBBB", data[i + 16 + 4 * k:i + 20 + 4 * k])
        vox[(x, y, z)] = c
    return vox

# ---------------------------------------------------------------- isometric preview
def render_preview(path, vox, PALETTE, scale=3):
    from PIL import Image, ImageDraw
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
            dr.polygon([(px_ + ox, py_ + oy) for px_, py_ in pts], fill=right)
        if (x + 1, y, z) not in vset:
            pts = [proj(x + 1, y, z), proj(x + 1, y + 1, z),
                   proj(x + 1, y + 1, z + 1), proj(x + 1, y, z + 1)]
            dr.polygon([(px_ + ox, py_ + oy) for px_, py_ in pts], fill=right)
    img.save(path)
    print(f"wrote {path} {img.size}")

def floater_sweep(parts):
    """6-connected components; report components not touching z=0."""
    from collections import deque
    for name, vox in parts.items():
        vset = set(vox)
        seen = set()
        floaters = 0
        for seed in vset:
            if seed in seen:
                continue
            q = deque([seed]); seen.add(seed); comp = [seed]
            touches_ground = seed[2] == 0
            while q:
                x, y, z = q.popleft()
                for nb in ((x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)):
                    if nb in vset and nb not in seen:
                        seen.add(nb); q.append(nb); comp.append(nb)
                        if nb[2] == 0:
                            touches_ground = True
            if not touches_ground:
                floaters += len(comp)
        print(f"{name}: {floaters} floater voxels ({len(vox)} total)")

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    basedir = os.path.expanduser("~/workspace/goals/strike-bay-factory-voxel-kit/files/strike-bay-factory-modules")
    for name, d in PARTS.items():
        write_vox(os.path.join(here, name + ".vox"), d, PALETTE, 0, 0)
        render_preview(os.path.join(here, name + "_preview.png"), d, PALETTE)
    floater_sweep(PARTS)
    # assembled composites with the existing base (render-only)
    hull = read_vox(os.path.join(basedir, "zsu_hull_v1.vox"))
    tracks = read_vox(os.path.join(basedir, "zsu_tracks_v1.vox"))
    on_base = dict(hull); on_base.update(tracks); on_base.update(turret)
    render_preview(os.path.join(here, "zsu57_on_base_preview.png"), on_base, PALETTE)
    full = dict(on_base); full.update(guns)
    render_preview(os.path.join(here, "zsu57_single_gun_full_preview.png"), full, PALETTE)
    # full vehicle with the pintle MG mount
    mount = dict(full); mount.update(pintle); mount.update(mg)
    render_preview(os.path.join(here, "zsu57_mg_mount_full_preview.png"), mount, PALETTE)
    # close-up of the hatch / gunner / MG area (cutaway crop of the turret top)
    region = {p: c for p, c in mount.items()
              if 0 <= p[0] < 24 and 12 <= p[1] < 50 and p[2] >= 26}
    render_preview(os.path.join(here, "zsu57_mg_mount_closeup.png"), region, PALETTE, scale=6)
