#!/usr/bin/env python3
"""Strike Bay factory kit — SMALL BRICK FLAT-ROOF BLOCK (factory_brick_flat_v1).

Square-footprint (30x30) sibling of the early-20th-century brick mill
(factory_brick_v1): load-bearing brick walls with two bands of tall
steel-sash windows, concrete lintels/sills and water table, corbelled brick
cornice, and a flat grey concrete roof with a raised brick parapet edge
and concrete coping. Freight door on the west end, personnel door on the east end.
Two buried interior rooms for damage reveals.

Generates factory_brick_flat_v1.vox + preview/slice renders.
"""
import random
random.seed(7)

PALETTE = [  # (name, rgb); color index = position + 1
    ("concrete",     (170, 166, 158)),  # 1  water table, lintels, sills
    ("concrete_dark",(112, 108, 100)),  # 2  concrete variation
    ("coping",       (202, 198, 190)),  # 3  boilerplate
    ("brick",        (150,  90,  66)),  # 4  walls
    ("brick_dark",   (120,  68,  50)),  # 5  brick variation
    ("glass",        ( 72,  98, 118)),  # 6  window glass
    ("glass_dark",   ( 44,  62,  78)),  # 7  boilerplate
    ("steel",        (122, 126, 134)),  # 8  interiors
    ("steel_dark",   ( 62,  64,  72)),  # 9  sash, door frames
    ("white",        (235, 235, 230)),  # 10 interiors
    ("window",       ( 18,  26,  38)),  # 11 interiors
    ("dark",         ( 32,  34,  40)),  # 12 door leaf, oculus
    ("green",        (100, 118,  94)),  # 13 boilerplate
    ("green_dark",   ( 70,  88,  68)),  # 14 freight door
    ("roof",         (100, 104, 100)),  # 15 boilerplate
    ("band_red",     (158,  62,  52)),  # 16 boilerplate
    ("band_white",   (224, 220, 212)),  # 17 boilerplate
    ("patina",       ( 96, 142, 118)),  # 18 patinated copper roof
    ("patina_dark",  ( 66, 104,  88)),  # 19 seams, ridge, variation
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

vox = {}  # (x, y, z) -> color index (1-based)

L, Y = 30, 15            # x 0..29, y -15..15: square footprint
WALL_TOP = 20           # brick walls z 0..20
SPRING = 22             # flat roof base

def box(x0, x1, y0, y1, z0, z1, c):
    """Inclusive-exclusive box fill."""
    ci = CI[c]
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                vox[(x, y, z)] = ci

# ---------------------------------------------------------------- solid brick mass + water table + cornice
box(0, L, -Y, Y + 1, 0, WALL_TOP, "brick")
box(-1, L + 1, -Y - 1, Y + 2, 0, 2, "concrete")      # water table, proud 1
box(-1, L + 1, -Y - 1, Y + 2, WALL_TOP, SPRING, "brick")  # corbelled cornice, proud 1

# ---------------------------------------------------------------- flat grey roof + brick parapet
box(0, L, -Y, Y + 1, SPRING, SPRING + 2, "concrete")    # roof slab
box(0, L, -Y, -Y + 1, SPRING + 2, SPRING + 7, "brick")  # raised parapet, long sides
box(0, L, Y, Y + 1, SPRING + 2, SPRING + 7, "brick")
box(0, 1, -Y, Y + 1, SPRING + 2, SPRING + 7, "brick")   # parapet, ends
box(L - 1, L, -Y, Y + 1, SPRING + 2, SPRING + 7, "brick")
box(-1, L + 1, -Y - 1, Y + 2, SPRING + 7, SPRING + 8, "concrete")  # coping

# ---------------------------------------------------------------- tall steel-sash windows, concrete lintels + sills
def long_windows(z0, z1):
    zmid = (z0 + z1) // 2
    for s in (-1, 1):
        yf, yg = s * Y, s * (Y - 1)
        for bx in range(0, L, 10):
            x0, x1 = bx + 3, bx + 9
            mull = set(range(x0, x1, 2))
            for x in range(x0, x1):
                for z in range(z0, z1 + 1):
                    vox.pop((x, yf, z), None)
                    ci = "steel_dark" if (x in mull or z == zmid) else "glass"
                    vox[(x, yg, z)] = CI[ci]
            for x in range(x0 - 1, x1 + 1):
                vox[(x, yf, z1 + 1)] = CI["concrete"]   # lintel
                vox[(x, yf, z0 - 1)] = CI["concrete"]   # sill

def end_windows(fx, ix, z0, z1, skip_middle=False):
    zmid = (z0 + z1) // 2
    bays = [(-12, -7), (-3, 2), (7, 12)]
    if skip_middle:
        bays = [bays[0], bays[-1]]
    for (y0, y1) in bays:
        mull = set(range(y0, y1 + 1, 2))
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                vox.pop((fx, y, z), None)
                ci = "steel_dark" if (y in mull or z == zmid) else "glass"
                vox[(ix, y, z)] = CI[ci]
        for y in range(y0 - 1, y1 + 2):
            vox[(fx, y, z1 + 1)] = CI["concrete"]
            vox[(fx, y, z0 - 1)] = CI["concrete"]

long_windows(2, 8)
long_windows(12, 18)
end_windows(0, 1, 2, 8, skip_middle=True)    # west ground: freight door takes the middle
end_windows(0, 1, 12, 18)
end_windows(L - 1, L - 2, 2, 8)
end_windows(L - 1, L - 2, 12, 18)

# ---------------------------------------------------------------- freight door (west) + personnel door (east)
for y in range(-6, 7):                                # freight door surround
    for z in range(1, 10):
        if y in (-6, 6) or z in (1, 9):
            vox[(0, y, z)] = CI["concrete"]
for y in range(-5, 6):
    for z in range(2, 9):
        vox.pop((0, y, z), None)
        ci = "steel_dark" if (z % 3 == 2 or y % 3 == 0) else "green_dark"
        vox[(1, y, z)] = CI[ci]

for y in range(-2, 3):                                # personnel door, east end
    for z in range(2, 9):
        if y in (-2, 2) or z in (2, 8):
            vox[(L - 1, y, z)] = CI["steel_dark"]
for y in range(-1, 2):
    for z in range(2, 8):
        vox.pop((L - 1, y, z), None)
        vox[(L - 2, y, z)] = CI["dark"]

# ---------------------------------------------------------------- subtle weathering
for (x, y, z), ci in list(vox.items()):
    if ci == CI["brick"] and random.random() < 0.06:
        vox[(x, y, z)] = CI["brick_dark"]
    elif ci == CI["concrete"] and random.random() < 0.04:
        vox[(x, y, z)] = CI["concrete_dark"]
    elif ci == CI["patina"] and random.random() < 0.06:
        vox[(x, y, z)] = CI["patina_dark"]


# ---------------------------------------------------------------- buried interiors — verbatim kit pattern
def interior_room(x0, x1, y0, y1, z0, z1, vox, CI):
    """Carve a grey-metal room with bulkhead doors on port/starboard walls.

    Bounds are inclusive-exclusive. The one-voxel shell around the box must
    be fully solid or the room is skipped (no hull breach). Palette must
    define: steel, steel_dark, dark, white, window.
    """
    shells = []
    for x in range(x0 - 1, x1 + 1):
        for y in range(y0 - 1, y1 + 1):
            shells += [(x, y, z0 - 1), (x, y, z1)]
    for x in (x0 - 1, x1):
        for y in range(y0 - 1, y1 + 1):
            for z in range(z0, z1):
                shells.append((x, y, z))
    for y in (y0 - 1, y1):
        for x in range(x0, x1):
            for z in range(z0, z1):
                shells.append((x, y, z))
    for p in shells:
        if p not in vox:
            print(f"interior_room({x0},{x1},{y0},{y1},{z0},{z1}) skipped: shell breach at {p}")
            return
    for x in range(x0, x1):                       # carve the cavity
        for y in range(y0, y1):
            for z in range(z0, z1):
                vox.pop((x, y, z), None)
    for x in range(x0, x1):                       # floor / ceiling
        for y in range(y0, y1):
            vox[(x, y, z0 - 1)] = CI["steel_dark"]
            vox[(x, y, z1)] = CI["dark"]
    for z in range(z0, z1):                       # walls
        for y in range(y0, y1):
            vox[(x0 - 1, y, z)] = CI["steel"]
            vox[(x1, y, z)] = CI["steel"]
        for x in range(x0, x1):
            vox[(x, y0 - 1, z)] = CI["steel"]
            vox[(x, y1, z)] = CI["steel"]
    for wx in range(x0 + 2, x1 - 1, 4):           # wall panel seams
        for z in range(z0, z1):
            vox[(wx, y0 - 1, z)] = CI["steel_dark"]
            vox[(wx, y1, z)] = CI["steel_dark"]
    for fx in range(x0, x1, 4):                   # floor plate seams
        for y in range(y0, y1):
            vox[(fx, y, z0 - 1)] = CI["dark"]
    for lx in range(x0 + 2, x1 - 2):              # ceiling light strips
        vox[(lx, y0 + 2, z1 - 1)] = CI["white"]
        vox[(lx, y1 - 3, z1 - 1)] = CI["white"]
    cx = (x0 + x1) // 2                           # bulkhead doors, port/starboard
    for dy in (y0, y1 - 1):
        for dx in range(-2, 3):
            for dz in range(0, 7):
                vox[(cx + dx, dy, z0 + dz)] = CI["steel_dark"]   # frame
        for dx in range(-1, 2):
            for dz in range(1, 6):
                vox[(cx + dx, dy, z0 + dz)] = CI["steel"]        # slab
        for dx in range(0, 2):
            for dz in range(4, 6):
                vox[(cx + dx, dy, z0 + dz)] = CI["window"]       # porthole
        vox[(cx + 1, dy, z0 + 2)] = CI["dark"]     # handle hints
        vox[(cx + 1, dy, z0 + 3)] = CI["dark"]


# ---------------------------------------------------------------- .vox writer (MagicaVoxel 150) — verbatim boilerplate
def write_vox(path, vox, PALETTE):
    import struct
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


# ---------------------------------------------------------------- isometric preview — verbatim boilerplate
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


# ---------------------------------------------------------------- top-down slice — verbatim boilerplate
def render_slice(path, vox, PALETTE, z):
    from PIL import Image
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


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    interior_room(4, 14, -9, -1, 4, 10, vox, CI)
    interior_room(16, 26, -9, -1, 4, 10, vox, CI)
    write_vox(os.path.join(here, "factory_brick_flat_v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "factory_brick_flat_v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "factory_brick_flat_v1_slice_z5.png"), vox, PALETTE, 5)
    render_slice(os.path.join(here, "factory_brick_flat_v1_slice_z25.png"), vox, PALETTE, 25)
