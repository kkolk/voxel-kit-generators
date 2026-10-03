#!/usr/bin/env python3
"""Strike Bay — T-55 style turret for the ZSU motorized base (v1).

Two rig parts sharing the ZSU design frame (FILE coords == shipped .vox
coords; ground truth taken from the shipped zsu_*_v1.vox files, NOT the
stale zsu_aa_v1.py on disk):

  t55_turret_v1.vox  traverse: low cast dome, mantlet cheeks, loader hatch,
                     commander cupola, snorkel box, antenna
                     (rotates about the vertical axis)
  t55_gun_v1.vox     elevation: single 100mm D-10T style barrel, fume
                     extractor, double-baffle muzzle brake, pivot shaft,
                     mantlet collar, breech (rotates about horizontal axis)

Rig pivots (file coords, x right / y forward / z up) — verified against
the shipped .vox files (turret basket centroid, gun pivot shaft):
  TRAVERSE_PIVOT  = (17, 30, 16)   z-axis; parent the turret part here
  ELEVATION_PIVOT = (17, 46, 23)   x-axis; parent the guns part here,
                                  as a child of the traverse node

Gun authored horizontal (0 deg elevation, pointing +y) — the rigging neutral.
Barrel overhang past the hull nose at 0 deg is correct for the type.

Scale: TURRET_VOXEL 0.09 m/voxel.
"""
import os
import struct
from collections import deque, Counter

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

TRAVERSE_PIVOT = (17, 30, 16)
ELEVATION_PIVOT = (17, 46, 23)

turret = {}
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

# ================================================================ TURRET (traverse about (17,30) z-axis)
# Low cast T-55 dome. Front = +y (gun faces the glacis).
cyl_z(turret, 17, 30, 8, 16, 18, "olive")          # turret basket / ring seat
# cast dome — stepped cylinders, squat profile
for (z0, z1, r) in ((18, 20, 11), (20, 22, 10), (22, 24, 9),
                    (24, 26, 7), (26, 28, 5), (28, 29, 3)):
    cyl_z(turret, 17, 30, r, z0, z1, "olive")
# rear bustle with stowage
box(turret, 11, 23, 19, 26, 18, 25, "olive")
box(turret, 11, 23, 19, 26, 25, 26, "olive_dark")  # bustle lid seam
# mantlet cheeks flanking the barrel channel (channel x 15..19 stays open
# for the gun part's collar/breech; cheeks raised 1 vox so a 180 traverse
# clears the engine-deck grills)
box(turret, 11, 15, 38, 48, 20, 28, "olive")       # left cheek
box(turret, 19, 23, 38, 48, 20, 28, "olive")       # right cheek
box(turret, 11, 15, 47, 49, 21, 27, "olive_dark")   # cheek front plates
box(turret, 19, 23, 47, 49, 21, 27, "olive_dark")
box(turret, 11, 23, 42, 46, 28, 30, "olive")       # top strap over the barrel
# periscopes on the strap
for px in (13, 16, 21):
    box(turret, px, px + 1, 43, 44, 30, 31, "glass")
# loader's hatch (left of the gun)
cyl_z(turret, 11, 31, 2, 25, 27, "olive_dark")
box(turret, 10, 12, 30, 31, 27, 28, "steel_dark")  # hatch handle
# commander's cupola (right of the gun)
cyl_z(turret, 23, 31, 3, 24, 29, "olive")
cyl_z(turret, 23, 31, 3, 29, 30, "olive_dark")     # hatch lid
box(turret, 22, 24, 30, 31, 30, 31, "steel_dark")  # lid handle
for (px, py) in ((20, 31), (26, 31), (23, 28), (23, 34)):
    box(turret, px, px + 1, py, py + 1, 29, 30, "glass")  # cupola periscopes
# snorkel stowage box on the rear roof (T-55 signature)
box(turret, 13, 21, 21, 28, 27, 30, "olive_dark")
box(turret, 13, 14, 21, 28, 30, 31, "dark")        # straps
box(turret, 20, 21, 21, 28, 30, 31, "dark")
# whip antenna, turret rear roof
cyl_z(turret, 13, 26, 1, 26, 36, "dark")

# cast texture: stipple the exposed olive faces with olive_dark
def cast_texture(d):
    vset = set(d)
    for p in list(vset):
        if d[p] != CI["olive"]:
            continue
        x, y, z = p
        if ((x + 1, y, z) not in vset or (x, y + 1, z) not in vset
                or (x, y, z + 1) not in vset):
            if (x * 7 + y * 11 + z * 13) % 9 < 2:
                d[p] = CI["olive_dark"]
cast_texture(turret)

# ================================================================ GUN (elevation about x-axis at (17,46,23))
# 100mm D-10T style: authored horizontal, pointing +y (rigging neutral).
cyl_x(guns, 46, 23, 2, 12, 22, "steel_dark")       # pivot shaft on the axis
box(guns, 14, 20, 43, 49, 20, 26, "olive")         # mantlet collar
box(guns, 14, 20, 48, 50, 21, 25, "olive_dark")    # collar front plate
box(guns, 15, 19, 40, 46, 21, 25, "gunmetal_dark") # breech in the channel
cyl_y(guns, 17, 23, 2, 48, 62, "gunmetal")         # barrel base
cyl_y(guns, 17, 23, 2, 62, 74, "gunmetal")         # barrel mid
cyl_y(guns, 17, 23, 3, 74, 80, "gunmetal")         # fume extractor
cyl_y(guns, 17, 23, 3, 74, 75, "gunmetal_dark")    # extractor bands
cyl_y(guns, 17, 23, 3, 79, 80, "gunmetal_dark")
cyl_y(guns, 17, 23, 2, 80, 98, "gunmetal")         # barrel tip section
cyl_y(guns, 17, 23, 3, 98, 104, "gunmetal_dark")   # double-baffle muzzle brake
cyl_y(guns, 17, 23, 3, 100, 101, "dark")           # baffle groove
box(guns, 16, 18, 103, 104, 22, 24, "dark")        # bore shadow on the face

# ---------------------------------------------------------------- .vox reader (for compositing the shipped base)
def read_vox(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"VOX "
    vox = {}
    def parse(pos, end):
        while pos < end:
            cid = data[pos:pos + 4]
            clen, chlen = struct.unpack("<ii", data[pos + 4:pos + 12])
            cstart = pos + 12
            if cid == b"XYZI":
                content = data[cstart:cstart + clen]
                n = struct.unpack("<i", content[:4])[0]
                for i in range(n):
                    x, y, z, c = struct.unpack("BBBB", content[4 + 4 * i:8 + 4 * i])
                    vox[(x, y, z)] = c
            parse(cstart + clen, cstart + clen + chlen)
            pos = cstart + clen + chlen
    parse(8, len(data))
    return vox

# ---------------------------------------------------------------- .vox writer (MagicaVoxel 150)
def write_vox(path, vox, PALETTE, xoff=0, yoff=0):
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
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

def components(vox):
    """6-connected components of a voxel dict."""
    vset = set(vox)
    seen = set()
    comps = []
    for seed in vset:
        if seed in seen:
            continue
        q = deque([seed]); seen.add(seed); comp = 0
        while q:
            x, y, z = q.popleft(); comp += 1
            for nb in ((x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)):
                if nb in vset and nb not in seen:
                    seen.add(nb); q.append(nb)
        comps.append(comp)
    return sorted(comps, reverse=True)

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    base = os.path.expanduser("~/workspace/goals/strike-bay-factory-voxel-kit/files/strike-bay-factory-modules")
    hull = read_vox(os.path.join(base, "zsu_hull_v1.vox"))
    tracks = read_vox(os.path.join(base, "zsu_tracks_v1.vox"))
    print(f"base: hull {len(hull)} vox, tracks {len(tracks)} vox")

    assembled = dict(hull)
    assembled.update(tracks)
    assembled.update(turret)
    assembled.update(guns)

    PARTS = {
        "t55_turret_v1": turret,
        "t55_gun_v1": guns,
        "t55_assembled_v1": assembled,
    }
    print(f"traverse pivot file coords: {TRAVERSE_PIVOT}")
    print(f"elevation pivot file coords: {ELEVATION_PIVOT}")
    for name, d in PARTS.items():
        write_vox(os.path.join(here, name + ".vox"), d, PALETTE)
        render_preview(os.path.join(here, name + "_preview.png"), d, PALETTE)

    # ---- validation ----
    for name, d in PARTS.items():
        comps = components(d)
        print(f"{name}: {len(d)} vox, {len(comps)} component(s), largest={comps[0]}")
    # per-color counts (confirm every intended color landed)
    inv = {v: k for k, v in CI.items()}
    for name, d in (("t55_turret_v1", turret), ("t55_gun_v1", guns)):
        c = Counter(d.values())
        print(f"{name} colors:", {inv[i]: n for i, n in sorted(c.items())})
    # turret/gun overlap report (gun wins the merge; same-color overlaps are invisible)
    overlap = set(turret) & set(guns)
    diff = [(p, inv[turret[p]], inv[guns[p]]) for p in overlap if turret[p] != guns[p]]
    print(f"turret/gun overlap: {len(overlap)} voxels, {len(diff)} with differing colors")
    for p, a, b in sorted(diff)[:10]:
        print(f"  {p}: turret={a} gun={b}")
    # ring seat contact: turret basket bottom (z=16) vs hull top (z<=16) at the ring
    basket = [(x, y) for (x, y, z) in turret if z == 16]
    contact = sum(1 for (x, y) in basket if (x, y, 15) in hull or (x, y, 16) in hull)
    print(f"basket voxels at z=16: {len(basket)}, seated on hull: {contact}")
