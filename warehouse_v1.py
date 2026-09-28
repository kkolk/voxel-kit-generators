#!/usr/bin/env python3
"""Strike Bay factory kit — WAREHOUSE HALL (warehouse_v1).

Long, low warehouse in the same mid-century industrial language as the
factory halls: exposed concrete frame, brick infill, high strip-window
ribbon, four large dock doors on the long side, near-clean roof with a
single row of vents. Separate kit module — factory_*.py files untouched.

Generates warehouse_v1.vox + preview/slice renders.
"""
import random
random.seed(42)

PALETTE = [  # (name, rgb); color index = position + 1
    ("concrete",     (170, 166, 158)),  # 1  aged concrete frame / beams
    ("concrete_dark",(112, 108, 100)),  # 2  weathered concrete
    ("coping",       (202, 198, 190)),  # 3  parapet coping stones
    ("brick",        (150,  90,  66)),  # 4  weathered brick infill
    ("brick_dark",   (120,  68,  50)),  # 5  brick variation
    ("glass",        ( 72,  98, 118)),  # 6  blue-gray window glass
    ("glass_dark",   ( 44,  62,  78)),  # 7  glass variation
    ("steel",        (122, 126, 134)),  # 8  interior wall panels (boilerplate)
    ("steel_dark",   ( 62,  64,  72)),  # 9  mullions, frames, vents
    ("white",        (235, 235, 230)),  # 10 boilerplate ceiling lights
    ("window",       ( 18,  26,  38)),  # 11 dark glass / portholes
    ("dark",         ( 32,  34,  40)),  # 12 dark detail / hatch
    ("green",        (100, 118,  94)),  # 13 muted green (doors)
    ("green_dark",   ( 70,  88,  68)),  # 14 dark green accent
    ("roof",         (100, 104, 100)),  # 15 flat roof slab
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

vox = {}  # (x, y, z) -> color index (1-based)

L, Y = 120, 30          # x 0..119, y -30..30, wall face planes at |y|=30, x=0/119
TOP = 21                # roof slab top

def box(x0, x1, y0, y1, z0, z1, c):
    """Inclusive-exclusive box fill."""
    ci = CI[c]
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                vox[(x, y, z)] = ci

def cyl(cx, cy, r, z0, z1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for y in range(cy - r, cy + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                for z in range(z0, z1):
                    vox[(x, y, z)] = ci

# ---------------------------------------------------------------- solid mass + plinth
box(0, 120, -Y, Y + 1, 0, TOP + 1, "brick")
box(-1, 121, -31, 32, 0, 2, "concrete")          # plinth, proud 1 all around

# ---------------------------------------------------------------- concrete frame
COLS = [4, 16, 28, 40, 52, 64, 76, 88, 100, 112]  # column lines (3 wide)
for c in COLS:                                    # facade columns, proud 1
    box(c, c + 3, 29, 32, 2, TOP + 1, "concrete")
    box(c, c + 3, -32, -29, 2, TOP + 1, "concrete")
for z0, z1 in ((12, 14), (19, 21)):               # beam bands
    box(0, 120, 29, 32, z0, z1, "concrete")
    box(0, 120, -32, -29, z0, z1, "concrete")
    box(-1, 1, -Y, Y + 1, z0, z1, "concrete")     # end walls
    box(119, 121, -Y, Y + 1, z0, z1, "concrete")
for cy in (-24, -12, 12, 24):                     # end-wall pilasters
    box(-1, 1, cy - 1, cy + 2, 2, TOP + 1, "concrete")
    box(119, 121, cy - 1, cy + 2, 2, TOP + 1, "concrete")

OPENINGS = [(c + 3, COLS[i + 1]) for i, c in enumerate(COLS[:-1])]

# ---------------------------------------------------------------- high strip windows (recessed 1 behind facade)
def facade_windows(z0, z1):
    zmid = (z0 + z1) // 2
    for (x0, x1) in OPENINGS:
        mull = set(range(x0, x1, 3))
        for x in range(x0, x1):
            for z in range(z0, z1 + 1):
                for s in (-1, 1):
                    vox.pop((x, s * Y, z), None)
                    ci = "steel_dark" if (x in mull or z == zmid) else "glass"
                    vox[(x, s * (Y - 1), z)] = CI[ci]

def end_windows(z0, z1):
    zmid = (z0 + z1) // 2
    for (fx, ix) in ((0, 1), (119, 118)):
        for (y0, y1) in ((-22, -14), (-10, 10), (14, 22)):
            for y in range(y0, y1 + 1):
                mull = (y - y0) % 3 == 0
                for z in range(z0, z1 + 1):
                    vox.pop((fx, y, z), None)
                    ci = "steel_dark" if (mull or z == zmid) else "glass"
                    vox[(ix, y, z)] = CI[ci]

facade_windows(14, 19)   # clerestory ribbon
end_windows(14, 19)

# ---------------------------------------------------------------- ground floor: dock doors + personnel door (front)
for oi in (1, 3, 5, 7):                           # four large dock doors
    x0, x1 = OPENINGS[oi]
    for x in range(x0 - 1, x1 + 1):               # concrete surround
        for z in range(1, 13):
            if x in (x0 - 1, x1) or z in (1, 12):
                vox[(x, -Y, z)] = CI["concrete"]
    for x in range(x0, x1):                       # one continuous door leaf
        for z in range(2, 12):
            for yy in (-32, -31, -30):
                vox.pop((x, yy, z), None)        # clear all facade layers
            ci = "dark" if z % 3 == 2 else "steel_dark"   # panel lines
            vox[(x, -(Y - 1), z)] = CI[ci]

for oi in (0,):                                   # personnel door
    x0, x1 = OPENINGS[oi]
    dx0, dx1 = x0 + 2, x0 + 6
    for x in range(dx0 - 1, dx1 + 1):
        for z in range(2, 8):
            if x in (dx0 - 1, dx1) or z == 7:
                vox[(x, -Y, z)] = CI["steel_dark"]
    for x in range(dx0, dx1):
        for z in range(2, 7):
            vox.pop((x, -Y, z), None)
            vox[(x, -(Y - 1), z)] = CI["dark"]

for oi in (2, 4, 6, 8):                           # small high rear windows
    x0, _ = OPENINGS[oi]
    for x in range(x0 + 2, x0 + 7):
        for z in range(8, 11):
            vox.pop((x, Y, z), None)
            vox[(x, Y - 1, z)] = CI["glass"] if x != x0 + 4 else CI["steel_dark"]

# ---------------------------------------------------------------- flat roof: slab, parapet, one vent row
for x in range(0, 120):
    for y in range(-Y, Y + 1):
        vox[(x, y, TOP)] = CI["roof"]
for x in range(0, 120):                               # parapet, 2 thick + coping
    for yy in (29, 30, -30, -29):
        box(x, x + 1, yy, yy + 1, 22, 24, "concrete")
for y in range(-29, 30):
    box(0, 2, y, y + 1, 22, 24, "concrete")
    box(118, 120, y, y + 1, 22, 24, "concrete")
for x in range(0, 120):
    for yy in (29, 30, -30, -29):
        vox[(x, yy, 24)] = CI["coping"]
for y in range(-29, 30):
    vox[(0, y, 24)] = CI["coping"]; vox[(1, y, 24)] = CI["coping"]
    vox[(118, y, 24)] = CI["coping"]; vox[(119, y, 24)] = CI["coping"]

for vx in (30, 50, 70, 90):                           # roof vents, single row
    cyl(vx, 0, 1, 21, 25, "steel_dark")
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx * dx + dy * dy <= 4:
                vox[(vx + dx, dy, 25)] = CI["dark"]

# ---------------------------------------------------------------- subtle weathering
for (x, y, z), ci in list(vox.items()):
    surf = abs(y) >= 29 or x <= 0 or x >= 119 or z >= 22
    if not surf:
        continue
    if ci == CI["brick"] and random.random() < 0.06:
        vox[(x, y, z)] = CI["brick_dark"]
    elif ci == CI["concrete"] and random.random() < 0.04:
        vox[(x, y, z)] = CI["concrete_dark"]

# (buried interiors run in __main__, after all geometry is built)


# ---------------------------------------------------------------- buried interiors
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
def render_preview(path, vox, PALETTE, scale=2):
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
    # buried interiors (future voxel damage reveals real rooms)
    interior_room(20, 32, -12, 12, 6, 12, vox, CI)
    interior_room(88, 100, -12, 12, 6, 12, vox, CI)
    write_vox(os.path.join(here, "warehouse_v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "warehouse_v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "warehouse_v1_slice_z16.png"), vox, PALETTE, 16)
    render_slice(os.path.join(here, "warehouse_v1_slice_z22.png"), vox, PALETTE, 22)
