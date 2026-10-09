#!/usr/bin/env python3
"""Strike Bay — ZSU v2: Shilka-style SPAAG with four auto-cannons
(kkolk/strike-bay#407).

Same vehicle class and rig contract as zsu_aa_v1 (the Gatling ZSU, kept for
later use), redrawn toward the owner's ZSU-23-4 concept sheet: open running
gear (6 road wheels a side, no skirts), a low flat-sided hull with fenders
and stowage, a huge flat boxy turret, four cooled cannons in two stacked
pairs, and a box radar on a mast at the turret rear. No markings.

Rig parts, one design frame (file coords == design coords + frame offset):

  zsu2_hull_v1    static: hull, fenders, glacis, decks, turret race
  zsu2_tracks_v1  running gear as ONE part (tread-scroll motion shader)
  zsu2_turret_v1  traverse about z at TRAVERSE_PIVOT
  zsu2_guns_v1    elevation about x at ELEVATION_PIVOT (child of turret);
                  authored at 0 deg, barrels pointing +y
  zsu2_radar_v1   spin about z at RADAR_PIVOT (child of turret)
  zsu2_aa_v1      assembled merge (browsing / reference)

hull() and tracks() are importable: zsu_twin_aa_v1 (#405) reuses them.

Frame: x right, y forward, z up. TURRET_VOXEL 0.09 m/voxel.
"""
import os

PALETTE = [
    ("olive",         ( 92, 104,  62)),  # 1  protective green
    ("olive_dark",    ( 66,  76,  45)),  # 2  shadowed plate, seams
    ("gunmetal",      ( 58,  60,  64)),  # 3  barrels, cradle
    ("gunmetal_dark", ( 38,  40,  44)),  # 4  muzzles, track frame
    ("steel",         (118, 122, 128)),  # 5  bright track links, hardware
    ("steel_dark",    ( 70,  72,  78)),  # 6  hubs, hinges
    ("dark",          ( 26,  28,  30)),  # 7  bores, grilles, deep shadow
    ("rubber",        ( 30,  31,  33)),  # 8  road-wheel tyres
    ("olive_light",   (112, 124,  78)),  # 9  lit edges, hatch lids
    ("glass",         (120, 160, 180)),  # 10 periscopes, lights
    ("rust",          ( 98,  66,  44)),  # 11 exhaust stain
    ("lamp",          (214, 196, 120)),  # 12 headlight lens
    # three-tone camo, used only by the twin-AA variant (zsu_twin_aa_v1)
    ("camo_green",    ( 74,  94,  52)),  # 13
    ("camo_brown",    ( 98,  80,  54)),  # 14
    ("camo_black",    ( 50,  52,  44)),  # 15
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

TRAVERSE_PIVOT = (17, 42, 19)
ELEVATION_PIVOT = (17, 61, 25)
RADAR_PIVOT = (17, 27, 35)

HULL_Y0, HULL_Y1 = 10, 76        # hull body (rear plate .. nose)
DECK_Z = 19                      # hull roof height (top face at z=19)


# ---------------------------------------------------------------- primitives
def put(d, x, y, z, c):
    d[(x, y, z)] = CI[c] if isinstance(c, str) else c


def box(d, x0, x1, y0, y1, z0, z1, c):
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                put(d, x, y, z, c)


def cyl_x(d, cy, cz, r, x0, x1, c, r_in=-1.0):
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for z in range(int(cz - r - 1), int(cz + r + 2)):
            d2 = (y - cy) ** 2 + (z - cz) ** 2
            if r_in * r_in < d2 <= r * r + 0.5 or (r_in < 0 and d2 <= r * r + 0.5):
                for x in range(x0, x1):
                    put(d, x, y, z, c)


def cyl_y(d, cx, cz, r, y0, y1, c):
    for x in range(int(cx - r - 1), int(cx + r + 2)):
        for z in range(int(cz - r - 1), int(cz + r + 2)):
            if (x - cx) ** 2 + (z - cz) ** 2 <= r * r + 0.5:
                for y in range(y0, y1):
                    put(d, x, y, z, c)


def cyl_z(d, cx, cy, r, z0, z1, c):
    for x in range(int(cx - r - 1), int(cx + r + 2)):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.5:
                for z in range(z0, z1):
                    put(d, x, y, z, c)


def ring_z(d, cx, cy, r, z0, z1, c):
    for x in range(int(cx - r - 1), int(cx + r + 2)):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if (r - 1) ** 2 < d2 <= r * r + 0.5:
                for z in range(z0, z1):
                    put(d, x, y, z, c)


def recolor(d, pred, c):
    for p in list(d):
        if pred(*p):
            d[p] = CI[c]


# ================================================================ TRACKS
WHEEL_Y = (20, 29, 38, 47, 56, 65)
WHEEL_Z, WHEEL_R = 6, 5
SPROCKET = (12, 8)   # (y, z) rear drive
IDLER = (73, 7)      # (y, z) front idler


def tracks():
    t = {}
    for (x0, x1, outer) in ((0, 7, 0), (27, 34, 33)):
        # road wheels: tyre, dished rim, hub with bolt ring
        for wy in WHEEL_Y:
            cyl_x(t, wy, WHEEL_Z, WHEEL_R, x0 + 1, x1 - 1, "rubber")
            cyl_x(t, wy, WHEEL_Z, WHEEL_R - 1, x0 + 1, x1 - 1, "olive_dark")
            cyl_x(t, wy, WHEEL_Z, 2, outer, outer + 1, "olive")
            cyl_x(t, wy, WHEEL_Z, 1, outer, outer + 1, "steel_dark")
            for (dy, dz) in ((3, 0), (-3, 0), (0, 3), (0, -3)):
                put(t, outer, wy + dy, WHEEL_Z + dz, "dark")   # lightening holes
            # wheel faces stay recessed against the outer link plane
            cyl_x(t, wy, WHEEL_Z, WHEEL_R, outer, outer + 1, "rubber", r_in=WHEEL_R - 1)
            cyl_x(t, wy, WHEEL_Z, WHEEL_R - 1, outer, outer + 1, "olive_dark", r_in=2)
            for (dy, dz) in ((3, 0), (-3, 0), (0, 3), (0, -3)):
                put(t, outer, wy + dy, WHEEL_Z + dz, "dark")
        # drive sprocket (rear) with teeth, idler (front)
        sy, sz = SPROCKET
        cyl_x(t, sy, sz, 4, x0 + 1, x1 - 1, "gunmetal")
        cyl_x(t, sy, sz, 2, outer, outer + 1, "steel_dark")
        for (dy, dz) in ((4, 0), (-4, 0), (0, 4), (0, -4), (3, 3), (-3, 3), (3, -3), (-3, -3)):
            put(t, outer, sy + dy, sz + dz, "steel")
        iy, iz = IDLER
        cyl_x(t, iy, iz, 4, x0 + 1, x1 - 1, "olive_dark")
        cyl_x(t, iy, iz, 2, outer, outer + 1, "steel_dark")
        # the track band: bottom run, top run on the wheel tops, wraps
        band = set()
        for y in range(SPROCKET[0], IDLER[0] + 1):
            band.add((y, 0)); band.add((y, 1))           # ground run
        for y in range(SPROCKET[0], IDLER[0] + 1):
            zt = WHEEL_Z + WHEEL_R + (1 if y < WHEEL_Y[0] - 3 or y > WHEEL_Y[-1] + 3 else 0)
            zt = max(zt, WHEEL_Z + WHEEL_R)
            band.add((y, zt)); band.add((y, zt + 1))     # top run
        for (cy, cz) in (SPROCKET, IDLER):
            for y in range(cy - 7, cy + 8):
                for z in range(0, 14):
                    d2 = (y - cy) ** 2 + (z - cz) ** 2
                    rear = y <= cy if (cy, cz) == SPROCKET else y >= cy
                    if rear and 4.5 ** 2 < d2 <= 6.3 ** 2:
                        band.add((y, z))
        for (y, z) in band:
            link = "steel" if (y + z) % 3 == 0 else "gunmetal_dark"
            for x in range(x0, x1):
                c = link
                if z <= 1 and x in (x0, x1 - 1):
                    c = "dark"                           # pad edges
                put(t, x, y, z, c)
        # guide horns down the middle of the top run
        for y in range(WHEEL_Y[0] - 4, WHEEL_Y[-1] + 5, 3):
            put(t, (x0 + x1) // 2, y, WHEEL_Z + WHEEL_R + 2, "steel_dark")
    return t


# ================================================================ HULL
def hull():
    h = {}
    # lower hull between the tracks
    box(h, 7, 27, HULL_Y0, HULL_Y1 - 4, 3, 13, "olive_dark")
    # upper hull / sponsons over the tracks
    box(h, 1, 33, HULL_Y0, HULL_Y1 - 13, 13, DECK_Z, "olive")
    # fenders: thin shelf over the tracks, a touch longer than the hull
    box(h, 0, 34, HULL_Y0 - 2, HULL_Y1 + 1, 13, 14, "olive_dark")
    box(h, 0, 1, HULL_Y0 - 2, HULL_Y1 + 1, 12, 13, "olive_dark")      # fender lip
    box(h, 33, 34, HULL_Y0 - 2, HULL_Y1 + 1, 12, 13, "olive_dark")
    # glacis: upper plate slopes from the deck down to the nose
    for y in range(HULL_Y1 - 13, HULL_Y1 + 1):
        ztop = DECK_Z - (y - (HULL_Y1 - 13)) * 5 // 13
        box(h, 1, 33, y, y + 1, 13, max(ztop, 14), "olive")
        if y >= HULL_Y1 - 6:
            box(h, 7, 27, y, y + 1, 4 + (y - (HULL_Y1 - 6)) // 2, 13, "olive_dark")  # lower glacis
    recolor(h, lambda x, y, z: y == HULL_Y1 and 13 <= z, "olive_light")       # nose edge
    # deck seam lines
    for y in (HULL_Y0 + 17, 60):
        box(h, 2, 32, y, y + 1, DECK_Z - 1, DECK_Z, "olive_dark")
    # driver's hatch + vision blocks (front left)
    for y in range(64, 69):
        zt = DECK_Z - (y - (HULL_Y1 - 13)) * 5 // 13
        box(h, 6, 13, y, y + 1, zt, zt + 1, "olive_light")
    for px in (7, 9, 11):
        put(h, px, 69, DECK_Z - 2, "glass")
    # headlight clusters at both front corners, on the fender
    for x0 in (1, 29):
        box(h, x0, x0 + 4, 71, 74, 14, 16, "steel_dark")
        put(h, x0 + 1, 74, 15, "lamp"); put(h, x0 + 2, 74, 15, "lamp")
        put(h, x0 + 1, 74, 14, "steel_dark")
        box(h, x0, x0 + 4, 70, 71, 14, 17, "olive_dark")                     # guard
    # tow hooks + nose towing eyes
    for x in (10, 23):
        box(h, x, x + 2, HULL_Y1 - 3, HULL_Y1, 3, 5, "steel_dark")
    # turret race on the roof
    cyl_z(h, TRAVERSE_PIVOT[0], TRAVERSE_PIVOT[1], 11, DECK_Z - 1, DECK_Z, "olive_dark")
    ring_z(h, TRAVERSE_PIVOT[0], TRAVERSE_PIVOT[1], 11, DECK_Z - 1, DECK_Z, "gunmetal_dark")
    # engine deck (rear): two louvred grille panels + centre access plate
    for (gx0, gx1) in ((3, 15), (19, 31)):
        box(h, gx0, gx1, HULL_Y0 + 2, HULL_Y0 + 15, DECK_Z, DECK_Z + 1, "olive_dark")
        for y in range(HULL_Y0 + 3, HULL_Y0 + 14, 2):
            box(h, gx0 + 1, gx1 - 1, y, y + 1, DECK_Z, DECK_Z + 1, "dark")
    box(h, 15, 19, HULL_Y0 + 3, HULL_Y0 + 14, DECK_Z, DECK_Z + 1, "olive_light")
    # rear plate: exhausts, tail lights, spare-track rack
    box(h, 1, 33, HULL_Y0 - 1, HULL_Y0, 6, DECK_Z, "olive_dark")
    for x0 in (5, 25):
        box(h, x0, x0 + 4, HULL_Y0 - 3, HULL_Y0 - 1, 13, 16, "gunmetal_dark")   # exhaust box
        box(h, x0 + 1, x0 + 3, HULL_Y0 - 3, HULL_Y0 - 2, 14, 15, "dark")
        put(h, x0 + 1, HULL_Y0 - 3, 16, "rust"); put(h, x0 + 2, HULL_Y0 - 3, 16, "rust")
    for x in (2, 31):
        put(h, x, HULL_Y0 - 2, 17, "rust"); put(h, x, HULL_Y0 - 1, 17, "rust")  # tail lights
    for x in range(11, 23, 3):
        box(h, x, x + 2, HULL_Y0 - 2, HULL_Y0 - 1, 7, 12, "steel_dark")        # spare links
    # sponson sides: stowage boxes and panel seams over the fenders
    for side_x, out_x in ((1, 0), (32, 33)):
        bx0 = out_x - 1 if out_x == 0 else out_x
        for (y0, y1) in ((14, 24), (26, 34), (40, 47), (50, 60)):
            box(h, bx0, bx0 + 2, y0, y1, 14, 18, "olive")
            box(h, bx0, bx0 + 2, y0, y1, 18, 19, "olive_light")
            box(h, bx0, bx0 + 2, y0, y0 + 1, 14, 18, "olive_dark")              # end shadow
            lx = bx0 if out_x == 0 else bx0 + 1
            put(h, lx, (y0 + y1) // 2, 16, "steel_dark")                         # latch
        for y in (36, 48):
            box(h, side_x, side_x + 1, y, y + 1, 13, DECK_Z, "olive_dark")
        # fuel drum at the rear of the fender
        cyl_y(h, out_x + (2 if out_x == 0 else -2), 16, 2, HULL_Y0 - 2, HULL_Y0 + 8, "olive_dark")
    # grab rails along the deck edge
    # lit top edge of the sponsons
    recolor(h, lambda x, y, z: z == DECK_Z - 1 and x in (1, 32) and HULL_Y0 <= y < HULL_Y1 - 6
            and h.get((x, y, z)) == CI["olive"], "olive_light")
    return h


# ================================================================ TURRET
def turret():
    t = {}
    px, py, pz = TRAVERSE_PIVOT
    cyl_z(t, px, py, 10, pz, pz + 2, "olive_dark")              # basket / ring
    TY0, TY1, TZ0, TZ1 = 22, 58, pz + 2, pz + 14               # body z 21..33, rear over the engine deck
    CORNER, BEVEL = 2, 2       # plan-corner cut; roof-edge 45 deg bevel layers
    for z in range(TZ0, TZ1):
        inset = max(0, z - (TZ1 - 1 - BEVEL))
        x0, x1, y0, y1 = 2 + inset, 32 - inset, TY0 + inset, TY1 - inset
        for x in range(x0, x1):
            for y in range(y0, y1):
                dx = min(x - x0, x1 - 1 - x); dy = min(y - y0, y1 - 1 - y)
                if dx + dy < CORNER - inset // 2:
                    continue
                edge = dx == 0 or dy == 0 or dx + dy == CORNER - inset // 2
                c = "olive"
                if edge and inset:
                    c = "olive_light"            # lit bevel
                elif z == TZ0:
                    c = "olive_dark"             # skirt shadow line
                put(t, x, y, z, c)
    # cheeks flank the gun slot and reach forward with a sloped face
    for (x0, x1) in ((3, 9), (25, 31)):
        for y in range(TY1, TY1 + 4):
            ztop = TZ1 - 2 - BEVEL - (y - TY1 + 1) * 2
            box(t, x0, x1, y, y + 1, TZ0, max(ztop, TZ0 + 2), "olive")
        box(t, x0, x1, TY1 + 3, TY1 + 4, TZ0, TZ0 + 2, "olive_dark")
    # gun slot: dark recess between the cheeks behind the cradle
    box(t, 9, 25, TY1 - 1, TY1, TZ0 + 1, TZ1 - 2 - BEVEL, "dark")
    # rear bustle (stowage) and its lid
    box(t, 4, 30, TY0 - 3, TY0, TZ0 + 1, TZ1 - 2, "olive")
    box(t, 4, 30, TY0 - 3, TY0, TZ1 - 2, TZ1 - 1, "olive_light")
    for x in (9, 17, 25):
        box(t, x, x + 1, TY0 - 3, TY0 - 2, TZ0 + 2, TZ1 - 3, "olive_dark")
    # side access doors and vision blocks
    for (sx, ox) in ((2, 1), (31, 32)):
        box(t, ox, ox + 1, 33, 41, TZ0 + 1, TZ1 - 2, "olive")
        box(t, ox, ox + 1, 33, 41, TZ1 - 2, TZ1 - 1, "olive_light")
        put(t, ox, 34, TZ0 + 4, "steel_dark"); put(t, ox, 39, TZ0 + 4, "steel_dark")  # hinges
        box(t, ox, ox + 1, 45, 53, TZ0 + 2, TZ1 - 3, "olive_dark")                # ammo hatch
        box(t, ox, ox + 1, 24, 30, TZ0 + 2, TZ1 - 3, "olive_dark")                # rear stowage door
        put(t, ox, 49, TZ1 - 3, "glass")
        for y in (44, 54):
            box(t, sx, sx + 1, y, y + 1, TZ0, TZ1 - 1, "olive_dark")              # weld seam
    # roof: commander cupola, gunner hatch, periscopes, vents
    zr = TZ1                                                     # on the flat roof top
    for hx in (7, 21):                                           # commander + gunner hatches
        box(t, hx, hx + 7, 41, 48, zr, zr + 1, "olive_dark")
        box(t, hx + 1, hx + 6, 42, 47, zr + 1, zr + 2, "olive_light")
        put(t, hx + 1, 46, zr + 2, "steel_dark")
    for x in (13, 20):
        put(t, x, TY1 - BEVEL - 1, zr, "glass")                    # front sight pair
    box(t, 12, 22, 50, 53, zr, zr + 1, "olive_dark")                            # vent housing
    for x in (13, 15, 17, 19, 21):
        put(t, x, 51, zr + 1, "dark")
    # radar mast pedestal (stays with the turret)
    rx, ry, rz = RADAR_PIVOT
    box(t, rx - 3, rx + 4, ry - 3, ry + 4, zr, rz, "olive_dark")
    cyl_z(t, rx, ry, 2, rz - 1, rz, "gunmetal_dark")
    # whip antennas
    return t


# ================================================================ RADAR (spins about z)
def radar():
    r = {}
    rx, ry, rz = RADAR_PIVOT
    cyl_z(r, rx, ry, 1, rz, rz + 1, "steel_dark")                 # mast
    box(r, rx - 8, rx + 9, ry - 2, ry + 2, rz + 1, rz + 8, "olive")    # antenna housing
    box(r, rx - 7, rx + 8, ry + 2, ry + 3, rz + 2, rz + 7, "olive_dark")  # front radome face
    for z in range(rz + 3, rz + 7, 2):
        box(r, rx - 6, rx + 7, ry + 2, ry + 3, z, z + 1, "gunmetal")      # face ribs
    box(r, rx - 8, rx + 9, ry - 2, ry + 2, rz + 8, rz + 9, "olive_light")  # top cap
    for x in (rx - 5, rx, rx + 5):
        box(r, x, x + 1, ry - 3, ry - 2, rz + 3, rz + 7, "olive_dark")    # back ribs
    return r


# ================================================================ GUNS (elevate about x)
GUN_SLOTS = ((12, 22), (12, 27), (20, 22), (20, 27))   # (x, z) lower-left of each 2x2 barrel


def guns():
    g = {}
    ex, ey, ez = ELEVATION_PIVOT
    cyl_x(g, ey, ez, 2, 7, 28, "steel_dark")                     # trunnion shaft
    box(g, 9, 25, ey - 4, ey + 3, 20, 31, "olive")               # cradle / mantlet block
    box(g, 10, 24, ey + 3, ey + 4, 20, 31, "olive_dark")         # mantlet face
    for (bx, bz) in GUN_SLOTS:
        box(g, bx - 1, bx + 3, ey + 3, ey + 12, bz - 1, bz + 3, "gunmetal")     # cooling jacket
        for y in range(ey + 4, ey + 12, 3):
            box(g, bx - 1, bx + 3, y, y + 1, bz - 1, bz + 3, "gunmetal_dark")   # jacket bands
        box(g, bx, bx + 2, ey + 12, ey + 18, bz, bz + 2, "gunmetal")            # barrel
        box(g, bx - 1, bx + 3, ey + 18, ey + 21, bz - 1, bz + 3, "gunmetal_dark")  # flash hider
        box(g, bx, bx + 2, ey + 20, ey + 21, bz, bz + 2, "dark")                # bore
        put(g, bx - 1, ey + 19, bz + 1, "dark"); put(g, bx + 2, ey + 19, bz + 1, "dark")  # slots
    # ammo feed chutes from the cradle sides
    for x in (8, 25):
        box(g, x, x + 1, ey - 3, ey + 2, 22, 29, "steel_dark")
    return g


hull_v = hull()
tracks_v = tracks()
turret_v = turret()
radar_v = radar()
guns_v = guns()
assembled = {}
for part in (tracks_v, hull_v, turret_v, radar_v, guns_v):
    assembled.update(part)

PARTS = {
    "zsu2_hull_v1": hull_v,
    "zsu2_tracks_v1": tracks_v,
    "zsu2_turret_v1": turret_v,
    "zsu2_radar_v1": radar_v,
    "zsu2_guns_v1": guns_v,
    "zsu2_aa_v1": assembled,
}


# ---------------------------------------------------------------- .vox writer (MagicaVoxel 150)
def write_vox(path, vox, palette, xoff, yoff):
    import struct
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    sx = max(p[0] for p in vox) + xoff + 1
    sy = max(p[1] for p in vox) + yoff + 1
    sz = max(p[2] for p in vox) + 1
    xyzi = struct.pack("<i", len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("BBBB", x + xoff, y + yoff, z, ci)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in palette)
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(palette))
    main = chunk(b"SIZE", struct.pack("<iii", sx, sy, sz)) + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 150) + chunk(b"MAIN", b"", main))
    print(f"wrote {path} ({len(vox)} voxels)")


def components(vox):
    """Count 6-connected components (rig parts must be one each)."""
    from collections import deque
    vset, seen, n = set(vox), set(), 0
    for s in vset:
        if s in seen:
            continue
        n += 1
        q = deque([s]); seen.add(s)
        while q:
            x, y, z = q.popleft()
            for nb in ((x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)):
                if nb in vset and nb not in seen:
                    seen.add(nb); q.append(nb)
    return n


if __name__ == "__main__":
    import sys
    if "--viewer-json" in sys.argv[1:]:
        import json
        print(json.dumps({"palette_names": [
            {"index": i + 1, "name": name} for i, (name, _) in enumerate(PALETTE)]}))
        raise SystemExit(0)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "zsu2")
    os.makedirs(out, exist_ok=True)
    xoff = -min(p[0] for p in assembled); yoff = -min(p[1] for p in assembled)
    print(f"frame offset ({xoff},{yoff}); file pivots: traverse "
          f"{(TRAVERSE_PIVOT[0]+xoff, TRAVERSE_PIVOT[1]+yoff, TRAVERSE_PIVOT[2])} elevation "
          f"{(ELEVATION_PIVOT[0]+xoff, ELEVATION_PIVOT[1]+yoff, ELEVATION_PIVOT[2])} radar "
          f"{(RADAR_PIVOT[0]+xoff, RADAR_PIVOT[1]+yoff, RADAR_PIVOT[2])}")
    for name, d in PARTS.items():
        write_vox(os.path.join(out, name + ".vox"), d, PALETTE, xoff, yoff)
        if name != "zsu2_aa_v1":
            print(f"  {name}: {components(d)} component(s)")
