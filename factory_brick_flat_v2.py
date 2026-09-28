#!/usr/bin/env python3
"""Strike Bay factory kit — BRICK FLAT BLOCK in the small-hall style (v2).

Same 30x30 footprint and flat roof as factory_brick_flat_v1, but restyled
in the mid-century industrial language of factory_small_v1:

  - exposed reinforced-concrete frame on a regular bay grid (3-wide columns,
    proud 1, on both long facades; beam bands at z 9-11 and 19-21)
  - brick infill, single band of multi-pane steel-sash windows (recessed 1)
  - flat roof: concrete slab + raised concrete parapet with coping, nothing
    on it (no brick parapet, no cornice)
  - ground floor: green loading doors (front + rear), dark personnel doors,
    one large 2-story garage door on the east end
  - concrete plinth, proud 1
  - 2 buried interior rooms (boilerplate interior_room) for future voxel damage
"""
import random
random.seed(11)

PALETTE = [  # (name, rgb); color index = position + 1  (same as factory_small_v1)
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
    ("green",        (100, 118,  94)),  # 13 muted green (doors, tank)
    ("green_dark",   ( 70,  88,  68)),  # 14 dark green accent
    ("roof",         (100, 104, 100)),  # 15 flat roof slab
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

vox = {}  # (x, y, z) -> color index (1-based)

L, Y = 30, 15            # x 0..29, y -15..15: same footprint as factory_brick_flat_v1
TOP = 20                # roof slab top (same story height as factory_small_v1)

def box(x0, x1, y0, y1, z0, z1, c):
    """Inclusive-exclusive box fill."""
    ci = CI[c]
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                vox[(x, y, z)] = ci

# ---------------------------------------------------------------- solid mass + plinth
box(0, L, -Y, Y + 1, 0, TOP + 1, "brick")
box(-1, L + 1, -Y - 1, Y + 2, 0, 2, "concrete")      # plinth, proud 1 all around

# ---------------------------------------------------------------- concrete frame (factory_small_v1 language)
COLS = [4, 14, 24]                                  # column lines (3 wide), 10-voxel bays
for c in COLS:                                      # facade columns, proud 1
    box(c, c + 3, 14, 17, 2, TOP + 1, "concrete")
    box(c, c + 3, -17, -14, 2, TOP + 1, "concrete")
for z0, z1 in ((9, 11), (19, 21)):                  # beam bands: sill / header
    box(0, L, 14, 17, z0, z1, "concrete")
    box(0, L, -17, -14, z0, z1, "concrete")
    box(-1, 1, -Y, Y + 1, z0, z1, "concrete")       # end walls
    box(L - 1, L + 1, -Y, Y + 1, z0, z1, "concrete")
for cy in (-9, 9):                                  # end-wall pilasters
    box(-1, 1, cy - 1, cy + 2, 2, TOP + 1, "concrete")
    box(L - 1, L + 1, cy - 1, cy + 2, 2, TOP + 1, "concrete")

OPENINGS = [(c + 3, COLS[i + 1]) for i, c in enumerate(COLS[:-1])]  # [(7,14),(17,24)]

# ---------------------------------------------------------------- window band (recessed 1 behind facade)
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
    for (fx, ix) in ((0, 1), (L - 1, L - 2)):
        segs = ((-12, -7), (-3, 2), (7, 12))
        if fx == L - 1:
            segs = (segs[0], segs[-1])   # garage-door end: keep the door bay clear
        for (y0, y1) in segs:
            mull = set(range(y0, y1 + 1, 2))
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    vox.pop((fx, y, z), None)
                    ci = "steel_dark" if (y in mull or z == zmid) else "glass"
                    vox[(ix, y, z)] = CI[ci]

facade_windows(11, 18)   # single window band
end_windows(11, 18)

# ---------------------------------------------------------------- ground floor
def loading_door(x0, x1, s):
    """6-wide green loading door with transom, on the s*Y facade."""
    dx0, dx1 = x0, x0 + 6
    yf, yg = s * Y, s * (Y - 1)
    for x in range(dx0 - 1, dx1 + 1):                 # concrete surround
        for z in range(1, 9):
            if x in (dx0 - 1, dx1) or z in (1, 8):
                vox[(x, yf, z)] = CI["concrete"]
    for x in range(dx0, dx1):
        for z in range(2, 8):
            vox.pop((x, yf, z), None)
            if z == 7:
                vox[(x, yg, z)] = CI["glass"]         # transom
            elif x == (dx0 + dx1) // 2:
                vox[(x, yg, z)] = CI["steel_dark"]    # center post
            else:
                vox[(x, yg, z)] = CI["green"]

ax0, ax1 = OPENINGS[0]   # (7, 14)
bx0, bx1 = OPENINGS[1]   # (17, 24)

loading_door(ax0, ax1, -1)   # front loading door, bay A
loading_door(ax0, ax1, 1)    # rear loading door, bay A

dx0, dx1 = bx0 + 1, min(bx0 + 4, bx1)                # front personnel door, bay B
for x in range(dx0 - 1, dx1 + 1):
    for z in range(2, 8):
        if x in (dx0 - 1, dx1) or z == 7:
            vox[(x, -Y, z)] = CI["steel_dark"]
for x in range(dx0, dx1):
    for z in range(2, 7):
        vox.pop((x, -Y, z), None)
        vox[(x, -(Y - 1), z)] = CI["dark"]

for x in range(bx0 + 1, bx0 + 5):                    # small rear windows, bay B
    for z in range(5, 8):
        vox.pop((x, Y, z), None)
        vox[(x, Y - 1, z)] = CI["glass"] if x != bx0 + 3 else CI["steel_dark"]

for y in range(-3, 4):                               # dark framed personnel door, west end
    for z in range(2, 9):
        if y in (-3, 3) or z in (2, 8):
            vox[(0, y, z)] = CI["steel_dark"]        # frame
for y in range(-2, 3):
    for z in range(2, 8):
        vox.pop((0, y, z), None)
        vox[(1, y, z)] = CI["dark"]                  # door leaf, recessed

gy0, gy1 = -8, 9                                     # large garage door, east narrow end
for y in range(gy0 - 1, gy1 + 1):                    # concrete surround
    for z in range(1, 20):
        if y in (gy0 - 1, gy1) or z in (1, 19):
            vox[(L - 1, y, z)] = CI["concrete"]
for y in range(gy0, gy1):                            # one continuous door leaf
    for z in range(2, 19):
        vox.pop((L - 1, y, z), None)
        vox.pop((L, y, z), None)                    # clear proud pilaster/beam layer
        ci = "dark" if z % 3 == 2 else "steel_dark"   # panel lines
        vox[(L - 2, y, z)] = CI[ci]

# ---------------------------------------------------------------- flat roof: slab + concrete parapet with coping, nothing else
for x in range(0, L):
    for y in range(-Y, Y + 1):
        vox[(x, y, TOP)] = CI["roof"]
for x in range(0, L):                               # parapet, 2 thick
    for yy in (14, 15, -15, -14):
        box(x, x + 1, yy, yy + 1, 21, 23, "concrete")
for y in range(-14, 15):
    box(0, 2, y, y + 1, 21, 23, "concrete")
    box(L - 2, L, y, y + 1, 21, 23, "concrete")
for x in range(0, L):                               # coping
    for yy in (14, 15, -15, -14):
        vox[(x, yy, 23)] = CI["coping"]
for y in range(-14, 15):
    vox[(0, y, 23)] = CI["coping"]; vox[(1, y, 23)] = CI["coping"]
    vox[(L - 2, y, 23)] = CI["coping"]; vox[(L - 1, y, 23)] = CI["coping"]

# ---------------------------------------------------------------- subtle weathering
for (x, y, z), ci in list(vox.items()):
    surf = abs(y) >= Y - 1 or x <= 0 or x >= L - 1 or z >= 21
    if not surf:
        continue
    if ci == CI["brick"] and random.random() < 0.06:
        vox[(x, y, z)] = CI["brick_dark"]
    elif ci == CI["concrete"] and random.random() < 0.04:
        vox[(x, y, z)] = CI["concrete_dark"]


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
    write_vox(os.path.join(here, "factory_brick_flat_v2.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "factory_brick_flat_v2_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "factory_brick_flat_v2_slice_z5.png"), vox, PALETTE, 5)
    render_slice(os.path.join(here, "factory_brick_flat_v2_slice_z14.png"), vox, PALETTE, 14)
    render_slice(os.path.join(here, "factory_brick_flat_v2_slice_z22.png"), vox, PALETTE, 22)
