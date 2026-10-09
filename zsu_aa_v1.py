#!/usr/bin/env python3
"""Strike Bay — SPAAG with a Gatling-style rotary cannon (v1).

Tracked chassis + traversing turret + Gatling gun pack,
with the Gun Dish radar on the turret roof.

Five rig parts sharing one design frame (file coords == design coords):

  zsu_hull_v1.vox    static: armored hull tub, glacis, engine deck, fenders,
                    turret ring, headlights, tow hooks
  zsu_tracks_v1.vox  running gear (ONE part for a motion shader): left/right
                    track runs, 6 road wheels per side, drive sprockets,
                    idlers, return rollers, tread links
  zsu_turret_v2.vox  traverse: turret body, roof, hatches, radar pedestal,
                    ammo boxes, turret basket (rotates about the vertical axis)
  zsu_radar_v1.vox   spin: the Gun Dish itself (dish + feed horn) on its own
                    pivot through the pedestal centre (yaws about the vertical
                    axis while the vehicle is active; the pedestal stays with
                    the turret so turret-without-dish + radar == the old v1)
  zsu_guns_v1.vox    elevation: Gatling rotary cannon — rotor housing +
                    6-barrel cluster on a trunnion mount (rotates about the
                    horizontal axis)
  zsu_aa_v1.vox      assembled merge of all five (browsing / reference)

Rig pivots (design coords, x right / y forward / z up):
  TRAVERSE_PIVOT  = (17, 40, 16)   z-axis; parent the turret part here
  ELEVATION_PIVOT = (17, 56, 23)   x-axis; parent the guns part here,
                                  as a child of the traverse node
  RADAR_PIVOT     = (17, 29, 28)   z-axis; parent the radar part here,
                                  as a child of the traverse node

Guns are authored horizontal (0 deg elevation, pointing +y) — the rigging
neutral. Tracks+wheels are a single part so a motion shader can scroll the
tread / spin the wheels as one.

Scale: TURRET_VOXEL 0.09 m/voxel. Hull ~6.5 m long, ~3 m wide — reads true
next to the 25-voxel (1.5 m) infantryman.
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
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

TRAVERSE_PIVOT = (17, 40, 16)
ELEVATION_PIVOT = (17, 56, 23)
RADAR_PIVOT = (17, 29, 28)   # spin axis (z) through the pedestal centre

hull = {}
tracks = {}
turret = {}
radar = {}
guns = {}

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

# ================================================================ HULL (static)
# lower tub
box(hull, 8, 26, 12, 66, 6, 12, "olive")
# upper hull sides
box(hull, 7, 27, 12, 66, 12, 16, "olive")
# glacis: stepped nose slope (front = +y)
box(hull, 8, 26, 66, 70, 6, 12, "olive")
box(hull, 9, 25, 70, 72, 6, 10, "olive")
box(hull, 10, 24, 70, 72, 10, 12, "olive_dark")  # nose cap
# rear plate
box(hull, 8, 26, 12, 14, 6, 14, "olive_dark")
# engine deck (rear) with grills
box(hull, 9, 25, 12, 28, 16, 18, "olive_dark")
for gx in (11, 15, 19, 23):
    box(hull, gx, gx + 2, 14, 26, 18, 19, "dark")  # grill slats
# exhaust
box(hull, 22, 25, 12, 16, 16, 18, "gunmetal_dark")
box(hull, 22, 25, 12, 14, 18, 19, "rust")
# armored top decks over the tracks (clear of the track top run / return rollers)
box(hull, 0, 8, 12, 68, 10, 13, "olive")
box(hull, 26, 34, 12, 68, 10, 13, "olive")
# armored side skirts covering the track top runs (static — hull part,
# so the motion-shader tracks part stays pure running gear)
box(hull, 0, 1, 12, 68, 3, 10, "olive")
box(hull, 33, 34, 12, 68, 3, 10, "olive")
for sy in range(14, 68, 12):                       # segmented panel seams
    box(hull, 0, 1, sy, sy + 1, 3, 10, "olive_dark")
    box(hull, 33, 34, sy, sy + 1, 3, 10, "olive_dark")
# stowage boxes on the armored track decks
box(hull, 2, 6, 20, 30, 13, 15, "olive")
box(hull, 28, 32, 20, 30, 13, 15, "olive")
box(hull, 2, 6, 44, 54, 13, 15, "olive_dark")
box(hull, 28, 32, 44, 54, 13, 15, "olive_dark")
# headlights (front track decks) + tow hooks
box(hull, 3, 5, 66, 68, 13, 14, "steel_dark")
box(hull, 29, 31, 66, 68, 13, 14, "steel_dark")
box(hull, 3, 5, 66, 68, 14, 15, "glass")
box(hull, 29, 31, 66, 68, 14, 15, "glass")
box(hull, 12, 14, 71, 73, 6, 8, "steel_dark")
box(hull, 20, 22, 71, 73, 6, 8, "steel_dark")
# turret ring: fixed race on the hull roof
cyl_z(hull, 17, 40, 8, 14, 16, "olive_dark")
ring_z(hull, 17, 40, 8, 15, 16, "gunmetal_dark")
box(hull, 9, 25, 30, 50, 14, 16, "olive")  # roof plate around the ring

# ================================================================ TRACKS (one part — motion shader)
for sx in (4, 30):  # track center x
    # track frame / side skirts inner
    box(tracks, sx - 3, sx + 3, 12, 68, 2, 9, "gunmetal_dark")
    # bottom run (ground contact)
    box(tracks, sx - 3, sx + 3, 12, 68, 0, 2, "dark")
    # top run
    box(tracks, sx - 3, sx + 3, 12, 68, 9, 10, "steel_dark")
    # tread links: alternating bright links every 3 voxels so motion reads
    for y in range(12, 68, 3):
        box(tracks, sx - 3, sx + 3, y, y + 1, 0, 10, "steel")
    # road wheels: 6 per side, tire + hub
    for wy in (18, 26, 34, 42, 50, 58):
        cyl_x(tracks, wy, 5, 4, sx - 3, sx + 3, "rubber")
        cyl_x(tracks, wy, 5, 2, sx - 3, sx + 3, "steel_dark")
        cyl_x(tracks, wy, 5, 1, sx - 3, sx + 3, "olive_dark")  # hub cap
    # drive sprocket (rear) + idler (front) with teeth hint
    cyl_x(tracks, 14, 5, 4, sx - 3, sx + 3, "gunmetal")
    cyl_x(tracks, 66, 5, 4, sx - 3, sx + 3, "gunmetal")
    for ty in range(2, 10):
        box(tracks, sx - 3, sx + 3, 13, 15, ty, ty + 1, "steel_dark")
        box(tracks, sx - 3, sx + 3, 65, 67, ty, ty + 1, "steel_dark")
    # return rollers
    for ry in (22, 36, 50):
        cyl_x(tracks, ry, 8, 1, sx - 2, sx + 2, "steel_dark")

# ================================================================ TURRET (traverse about (17,40) z-axis)
# Big boxy Shilka-style turret. Front = +y (mantlet faces the glacis).
cyl_z(turret, 17, 40, 8, 16, 18, "olive")          # turret basket / ring
box(turret, 3, 31, 28, 54, 18, 26, "olive")        # turret body — huge and boxy
box(turret, 8, 26, 54, 58, 18, 28, "olive")          # mantlet block (proud of the face)
box(turret, 10, 24, 57, 58, 20, 26, "olive_dark")    # mantlet front plate
cyl_x(turret, 56, 23, 4, 6, 28, "olive_dark")        # trunnion drum (static housing)
cyl_x(turret, 56, 23, 2, 4, 6, "gunmetal_dark")      # trunnion end caps
cyl_x(turret, 56, 23, 2, 28, 30, "gunmetal_dark")
for (mx, mz) in ((11, 20), (22, 20), (11, 25), (22, 25)):
    box(turret, mx, mx + 1, 57, 58, mz, mz + 1, "dark")  # mantlet bolts
box(turret, 4, 30, 29, 53, 26, 28, "olive_dark")   # roof plate
box(turret, 5, 29, 22, 28, 18, 25, "olive")        # rear bustle
# hatches
cyl_z(turret, 10, 38, 2, 28, 29, "olive_dark")
cyl_z(turret, 24, 38, 2, 28, 29, "olive_dark")
# periscopes along the front roof edge
for px in (7, 12, 22, 27):
    box(turret, px, px + 1, 50, 51, 28, 29, "glass")
# Gun Dish radar at the turret rear: the pedestal stays on the turret, the
# deployed dish facing +y spins on its own pivot (#404: RADAR_PIVOT, the
# pedestal centre, so the dish orbits the mast as it scans)
box(turret, 14, 20, 26, 32, 28, 33, "olive_dark")  # radar pedestal (stays)
cyl_y(radar, 17, 38, 5, 30, 32, "olive")           # dish face (spins)
cyl_y(radar, 17, 38, 5, 32, 33, "olive_dark")      # dish back (spins)
cyl_y(radar, 17, 38, 2, 29, 30, "steel_dark")      # feed horn (spins)
# ammo boxes on the turret flanks + feed chutes to the receivers
for (bx0, bx1) in ((0, 3), (31, 34)):
    box(turret, bx0, bx1, 34, 46, 19, 23, "olive")
    box(turret, bx0, bx1, 34, 46, 23, 24, "olive_dark")
    box(turret, bx0, bx1, 38, 42, 20, 21, "dark")
box(turret, 3, 5, 40, 42, 22, 24, "steel_dark")    # chutes
box(turret, 29, 31, 40, 42, 22, 24, "steel_dark")
box(turret, 3, 5, 40, 41, 24, 25, "brass")
box(turret, 29, 31, 40, 41, 24, 25, "brass")
# whip antenna on the rear bustle
cyl_z(turret, 24, 25, 1, 25, 36, "dark")

# ================================================================ GUNS (elevation about x-axis at (17,56,23))
# Gatling-style rotary cannon on an external trunnion mount: the gun sled and
# pivot shaft ride in the turret's mantlet drum; lengthened 6-barrel cluster.
box(guns, 13, 21, 32, 48, 20, 26, "olive")        # gun housing (extended fwd)
box(guns, 13, 21, 34, 46, 26, 27, "olive_dark")   # top cover
box(guns, 14, 20, 30, 32, 20, 26, "gunmetal_dark")# breech block
cyl_y(guns, 17, 23, 4, 30, 33, "gunmetal_dark")   # rotor drum (rear)
cyl_y(guns, 17, 23, 2, 28, 30, "steel_dark")      # drive motor
cyl_x(guns, 56, 23, 2, 7, 27, "steel_dark")       # pivot shaft through the drum
box(guns, 12, 22, 46, 55, 19, 27, "olive_dark")   # gun sled / cradle
box(guns, 12, 22, 50, 52, 27, 28, "olive_dark")   # cradle top strap
# 6 barrels in a circular cluster around the bore axis (17,23) — lengthened
for (bx, bz) in ((19, 23), (18, 25), (16, 25), (15, 23), (16, 21), (18, 21)):
    box(guns, bx, bx + 2, 44, 68, bz, bz + 2, "gunmetal")       # barrel
    box(guns, bx, bx + 2, 68, 70, bz, bz + 2, "gunmetal_dark")  # muzzle
    box(guns, bx + 1, bx + 2, 68, 70, bz + 1, bz + 2, "dark")   # bore shadow
# clamp discs holding the barrel cluster (ahead of the mantlet)
cyl_y(guns, 17, 23, 4, 60, 61, "gunmetal_dark")
cyl_y(guns, 17, 23, 4, 66, 67, "gunmetal_dark")
box(guns, 14, 20, 58, 60, 20, 26, "gunmetal_dark")# barrel collar ahead of mantlet

# ================================================================ assembled merge
assembled = dict(hull)
assembled.update(tracks)
assembled.update(turret)
assembled.update(radar)
assembled.update(guns)

PARTS = {
    "zsu_hull_v1": hull,
    "zsu_tracks_v1": tracks,
    "zsu_turret_v2": turret,
    "zsu_radar_v1": radar,
    "zsu_guns_v1": guns,
    "zsu_aa_v1": assembled,
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
    import sys
    if "--viewer-json" in sys.argv[1:]:
        # Palette labels for the voxel viewer's PATCH /api/models/{id}
        # (palette_names: [{index, name}]); the viewer also derives these
        # from the attached .py, this just makes the payload explicit.
        import json
        print(json.dumps({"palette_names": [
            {"index": i + 1, "name": name} for i, (name, _) in enumerate(PALETTE)]}))
        raise SystemExit(0)
    here = os.path.dirname(os.path.abspath(__file__))
    gx = min(p[0] for p in assembled); gy = min(p[1] for p in assembled)
    XOFF, YOFF = -gx, -gy
    print(f"frame offset: ({XOFF},{YOFF}); traverse pivot file coords: "
          f"({TRAVERSE_PIVOT[0]+XOFF},{TRAVERSE_PIVOT[1]+YOFF},{TRAVERSE_PIVOT[2]})")
    print(f"elevation pivot file coords: "
          f"({ELEVATION_PIVOT[0]+XOFF},{ELEVATION_PIVOT[1]+YOFF},{ELEVATION_PIVOT[2]})")
    print(f"radar pivot file coords: "
          f"({RADAR_PIVOT[0]+XOFF},{RADAR_PIVOT[1]+YOFF},{RADAR_PIVOT[2]})")
    for name, d in PARTS.items():
        write_vox(os.path.join(here, name + ".vox"), d, PALETTE, XOFF, YOFF)
        render_preview(os.path.join(here, name + "_preview.png"), d, PALETTE)
    floater_sweep(PARTS)
