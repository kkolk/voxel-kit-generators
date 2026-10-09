#!/usr/bin/env python3
"""Strike Bay — twin-cannon ZSU variant, Gepard-style (kkolk/strike-bay#405).

A later ZSU: the zsu_aa_v2 hull and running gear (imported, same geometry)
under a twin-cannon turret — two outboard gun pods that elevate together,
a round tracking dish on the turret front, and a wide search antenna on a
mast at the rear that spins. Three-tone camo, no markings.

Rig parts, one design frame shared with zsu_aa_v2:

  zsu_twin_hull_v1    static: zsu_aa_v2 hull geometry, camo colours
  zsu2_tracks_v1      reused unchanged (written here too for convenience)
  zsu_twin_turret_v1  traverse about z at TRAVERSE_PIVOT
  zsu_twin_guns_v1    elevation about x at ELEVATION_PIVOT (child of turret):
                      both gun pods + barrels + cross shaft, authored at
                      0 deg pointing +y
  zsu_twin_radar_v1   spin about z at RADAR_PIVOT (child of turret)
  zsu_twin_aa_v1      assembled merge (browsing / reference)
"""
import os
import zsu_aa_v2 as base
from zsu_aa_v2 import PALETTE, CI, put, box, cyl_x, cyl_y, cyl_z, recolor

TRAVERSE_PIVOT = base.TRAVERSE_PIVOT           # (17, 42, 19)
ELEVATION_PIVOT = (17, 45, 30)
RADAR_PIVOT = (17, 32, 41)

TX0, TX1 = 7, 27          # turret body width (gun pods sit outboard)
TY0, TY1 = 30, 56
TZ0, TZ1 = TRAVERSE_PIVOT[2] + 2, TRAVERSE_PIVOT[2] + 21     # z 21..40


# ---------------------------------------------------------------- camo
def _hash(ix, iy, iz, seed):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 144665) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def _noise(x, y, z, cell, seed):
    fx, fy, fz = x / cell, y / cell, z / cell
    ix, iy, iz = int(fx // 1), int(fy // 1), int(fz // 1)
    tx, ty, tz = fx - ix, fy - iy, fz - iz
    tx, ty, tz = (t * t * (3 - 2 * t) for t in (tx, ty, tz))
    v = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (tx if dx else 1 - tx) * (ty if dy else 1 - ty) * (tz if dz else 1 - tz)
                v += w * _hash(ix + dx, iy + dy, iz + dz, seed)
    return v


def camo(d, black=0.654):
    """Three-tone blotches over the olive plate (trim and hardware keep
    their colours). World-frame noise, so the pattern runs across parts.
    `black` is the black-patch threshold (0.654 ~ 20%, 0.72 ~ 10%)."""
    plate = (CI["olive"], CI["olive_light"])
    for (x, y, z), c in list(d.items()):
        if c in plate:
            # thresholds measured for ~45% green / 35% brown / 20% black
            a = _noise(x, y, z * 1.1, 14.0, 1) * 0.85 + _noise(x, y, z, 6.0, 2) * 0.15
            b = _noise(x, y, z * 1.1, 11.9, 3) * 0.85 + _noise(x, y, z, 5.0, 4) * 0.15
            if b > black:
                d[(x, y, z)] = CI["camo_black"]
            elif a > 0.48:
                d[(x, y, z)] = CI["camo_brown"]
            else:
                d[(x, y, z)] = CI["camo_green"]
        elif c == CI["olive_dark"]:
            d[(x, y, z)] = CI["camo_black"] if _noise(x, y, z * 1.1, 11.9, 3) > black else CI["olive_dark"]
    return d


# ================================================================ TURRET
def turret():
    t = {}
    px, py, pz = TRAVERSE_PIVOT
    cyl_z(t, px, py, 10, pz, pz + 2, "olive_dark")            # basket / ring
    BEVEL, CORNER = 1, 2
    for z in range(TZ0, TZ1):
        inset = max(0, z - (TZ1 - 1 - BEVEL))
        # front glacis of the turret slopes back over the top third
        front = TY1 - max(0, (z - (TZ0 + 6)) // 2)
        x0, x1, y0, y1 = TX0 + inset, TX1 - inset, TY0 + inset, min(front, TY1 - inset)
        for x in range(x0, x1):
            for y in range(y0, y1):
                dx = min(x - x0, x1 - 1 - x); dy = min(y - y0, y1 - 1 - y)
                if dx + dy < CORNER:
                    continue
                c = "olive"
                if z == TZ0:
                    c = "olive_dark"
                elif inset and (dx == 0 or dy == 0):
                    c = "olive_light"
                put(t, x, y, z, c)
    # smoke dischargers: two 3-tube banks on the front corners
    yf = TY1 - max(0, (TZ1 - 3 - (TZ0 + 6)) // 2)          # sloped face at that height
    for x0 in (TX0 + 1, TX1 - 4):
        box(t, x0, x0 + 3, yf - 2, yf + 1, TZ1 - 3, TZ1 - 1, "olive_dark")
        for x in range(x0, x0 + 3):
            put(t, x, yf + 1, TZ1 - 2, "dark")
    # roof hatches + periscopes
    zr = TZ1
    for (hx, hy) in ((9, 42), (19, 42)):
        box(t, hx, hx + 6, hy, hy + 6, zr, zr + 1, "olive_dark")
        box(t, hx + 1, hx + 5, hy + 1, hy + 5, zr + 1, zr + 2, "olive_light")
    for x in (11, 22):
        put(t, x, 49, zr, "glass")
    # rear bustle with stowage rack
    box(t, TX0 + 1, TX1 - 1, TY0 - 5, TY0, TZ0 + 2, TZ1 - 3, "olive")
    box(t, TX0 + 1, TX1 - 1, TY0 - 5, TY0, TZ1 - 3, TZ1 - 2, "olive_light")
    box(t, TX0 + 1, TX1 - 1, TY0 - 6, TY0 - 5, TZ1 - 5, TZ1 - 4, "steel_dark")   # rack rail
    # side trunnion bosses where the gun pods' cross shaft passes
    ex, ey, ez = ELEVATION_PIVOT
    for x in (TX0 - 1, TX1):
        cyl_x(t, ey, ez, 3, x, x + 1, "olive_dark")
    # search-radar mast base (stays with the turret)
    rx, ry, rz = RADAR_PIVOT
    box(t, rx - 2, rx + 3, ry - 2, ry + 3, zr, rz, "olive_dark")
    return t


def radome():
    """Tracking radar: rounded dark-olive box proud of the turret's front-left,
    with a light lens panel. Added after camo so it keeps its own colours."""
    t = {}
    dz, dx = TZ0 + 11, TX0 + 4
    box(t, dx - 2, dx + 3, TY1 - 5, TY1 + 1, dz - 3, dz, "olive_dark")     # mount block
    for y in range(TY1, TY1 + 6):
        for x in range(dx - 5, dx + 5):
            for z in range(dz - 4, dz + 5):
                ex = abs(x - dx + 0.5) / 5.0; ez = abs(z - dz) / 4.5
                if ex ** 2 + ez ** 2 <= 1.15:
                    put(t, x, y, z, "olive_dark")
    box(t, dx - 2, dx + 2, TY1 + 6, TY1 + 7, dz - 1, dz + 3, "olive_light")  # lens panel
    put(t, dx - 1, TY1 + 7, dz, "glass")
    return t


# ================================================================ GUNS (both pods elevate together)
POD_X = ((1, 6), (28, 33))


def guns():
    g = {}
    ex, ey, ez = ELEVATION_PIVOT
    cyl_x(g, ey, ez, 1, 2, 32, "steel_dark")                      # cross shaft through the turret
    for (x0, x1) in POD_X:
        cx = (x0 + x1) // 2
        # armoured pod: chamfered box around the gun breech
        for z in range(ez - 6, ez + 4):
            for y in range(ey - 9, ey + 13):
                for x in range(x0, x1):
                    dy_front = ey + 12 - y
                    dz = min(z - (ez - 6), ez + 3 - z)
                    if dy_front + dz < 3:
                        continue                                   # nose chamfer
                    c = "olive"
                    if z == ez + 3:
                        c = "olive_light"
                    elif z == ez - 6:
                        c = "olive_dark"
                    put(g, x, y, z, c)
        box(g, x0, x1, ey - 10, ey - 9, ez - 5, ez + 3, "olive_dark")        # pod rear plate
        box(g, x0, x1, ey - 2, ey - 1, ez - 5, ez + 3, "olive_dark")         # access panel seam
        box(g, x0, x1, ey + 10, ey + 13, ez - 3, ez + 2, "gunmetal_dark")    # pod front face
        box(g, cx - 2, cx + 2, ey + 13, ey + 14, ez - 2, ez + 2, "dark")     # barrel collar ring
        put(g, cx, ey + 4, ez + 4, "steel_dark")                           # feed cover hinge
        put(g, cx - 1, ey + 4, ez + 4, "steel_dark")
        # barrel, recoil sleeve, muzzle brake
        box(g, cx - 1, cx + 1, ey + 12, ey + 16, ez - 1, ez + 1, "gunmetal_dark")   # sleeve
        box(g, cx - 1, cx + 1, ey + 16, ey + 31, ez - 1, ez + 1, "gunmetal")
        box(g, cx - 2, cx + 2, ey + 31, ey + 34, ez - 2, ez + 2, "gunmetal_dark")   # muzzle brake
        box(g, cx - 1, cx + 1, ey + 33, ey + 34, ez - 1, ez + 1, "dark")
        for z in (ez - 2, ez + 1):
            put(g, cx - 2, ey + 32, z, "dark"); put(g, cx + 1, ey + 32, z, "dark")
        # velocity radar box on top of each barrel's sleeve (hint)
        box(g, cx - 1, cx + 1, ey + 12, ey + 15, ez + 1, ez + 2, "olive_dark")
    return g


# ================================================================ RADAR (search, spins)
def radar():
    r = {}
    rx, ry, rz = RADAR_PIVOT
    cyl_z(r, rx, ry, 1, rz, rz + 3, "steel_dark")                   # mast
    box(r, rx - 2, rx + 3, ry - 1, ry + 2, rz + 3, rz + 4, "steel_dark")   # yoke
    for x in range(rx - 7, rx + 8):
        for z in range(rz + 4, rz + 12):
            if abs(x - rx) == 7 and z in (rz + 4, rz + 11):
                continue                                                  # rounded corners
            for y in range(ry - 2, ry + 1):
                put(r, x, y, z, "olive")                                  # antenna body
    box(r, rx - 6, rx + 7, ry + 1, ry + 2, rz + 5, rz + 11, "olive_dark")    # reflector face
    box(r, rx - 6, rx + 7, ry + 1, ry + 2, rz + 8, rz + 9, "gunmetal")
    box(r, rx - 7, rx + 8, ry - 2, ry + 1, rz + 11, rz + 12, "olive_light")
    return r


hull_v = camo(base.hull())
tracks_v = base.tracks()
turret_v = camo(turret(), black=0.72)
turret_v.update(radome())
guns_v = camo(guns())
radar_v = camo(radar())
assembled = {}
for part in (tracks_v, hull_v, turret_v, radar_v, guns_v):
    assembled.update(part)

PARTS = {
    "zsu_twin_hull_v1": hull_v,
    "zsu2_tracks_v1": tracks_v,
    "zsu_twin_turret_v1": turret_v,
    "zsu_twin_guns_v1": guns_v,
    "zsu_twin_radar_v1": radar_v,
    "zsu_twin_aa_v1": assembled,
}

if __name__ == "__main__":
    import sys
    if "--viewer-json" in sys.argv[1:]:
        import json
        print(json.dumps({"palette_names": [
            {"index": i + 1, "name": name} for i, (name, _) in enumerate(PALETTE)]}))
        raise SystemExit(0)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "zsu_twin")
    os.makedirs(out, exist_ok=True)
    # same frame offset as zsu_aa_v2 so shared parts composite exactly
    xoff = -min(p[0] for p in base.assembled); yoff = -min(p[1] for p in base.assembled)
    xoff = max(xoff, -min(p[0] for p in assembled)); yoff = max(yoff, -min(p[1] for p in assembled))
    print(f"frame offset ({xoff},{yoff}); file pivots: traverse "
          f"{(TRAVERSE_PIVOT[0]+xoff, TRAVERSE_PIVOT[1]+yoff, TRAVERSE_PIVOT[2])} elevation "
          f"{(ELEVATION_PIVOT[0]+xoff, ELEVATION_PIVOT[1]+yoff, ELEVATION_PIVOT[2])} radar "
          f"{(RADAR_PIVOT[0]+xoff, RADAR_PIVOT[1]+yoff, RADAR_PIVOT[2])}")
    for name, d in PARTS.items():
        base.write_vox(os.path.join(out, name + ".vox"), d, PALETTE, xoff, yoff)
        if name != "zsu_twin_aa_v1":
            print(f"  {name}: {base.components(d)} component(s)")
