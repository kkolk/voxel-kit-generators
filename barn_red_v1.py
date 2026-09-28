#!/usr/bin/env python3
"""Strike Bay farm line — CLASSIC RED BARN (barn_red_v1).

Turn-of-the-century American midwestern barn at factory-kit scale
(~10 voxels per story): rubble-stone foundation (proud 1 voxel), red
board-and-batten siding walls, gambrel roof in weathered galvanized gray
with seam lines, white eave fascia + gable rake trim, big weathered-gray
double sliding door with Z-bracing on the east eave side, white-trimmed
square windows, loft windows in both gable ends, louvered cupola on the
ridge. Three buried interior rooms (two ground floor, one hay loft).

Generates barn_red_v1.vox + preview/slice renders.
"""
import random
random.seed(21)

PALETTE = [  # (name, rgb); color index = position + 1
    ("stone",      (150, 145, 135)),  # 1  rubble-stone foundation
    ("stone_dark", (110, 105,  95)),  # 2  stone variation
    ("siding",     (150,  60,  48)),  # 3  barn-red boards
    ("siding_dark",(118,  44,  36)),  # 4  battens / weathering
    ("trim",       (232, 228, 220)),  # 5  white fascia, rake trim, frames
    ("roof_gray",  (168, 172, 176)),  # 6  weathered galvanized roof
    ("roof_seam",  (130, 134, 140)),  # 7  roof seams, ridge cap
    ("door_gray",  (120, 116, 110)),  # 8  weathered gray door leaves
    ("door_dark",  ( 88,  84,  80)),  # 9  door bracing, rail
    ("glass",      ( 70,  95, 115)),  # 10 window glass
    ("steel",      (122, 126, 134)),  # 11 interiors
    ("steel_dark", ( 62,  64,  72)),  # 12 interiors
    ("white",      (235, 235, 230)),  # 13 interiors
    ("window",     ( 18,  26,  38)),  # 14 interiors
    ("dark",       ( 30,  32,  38)),  # 15 interiors, loft fill
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

vox = {}  # (x, y, z) -> color index (1-based)

X0, X1 = 0, 26      # x 0..25 — 26 wide
Y0, Y1 = -18, 18    # y -18..17 — 36 long
CX = 12.5           # ridge centerline

def box(x0, x1, y0, y1, z0, z1, c):
    """Inclusive-exclusive box fill."""
    ci = CI[c]
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                vox[(x, y, z)] = ci

def z_roof(u):
    """Gambrel roofline: steep lower slope, shallow upper slope."""
    if u <= 5.5:
        return 31.0 - u * (4.25 / 5.5)       # ridge 31 -> break 26.75
    return 26.75 - (u - 5.5) * (8.75 / 8.0)  # break -> eave 18 @ u=13.5

# ---------------------------------------------------------------- stone foundation, proud 1 voxel
box(X0 - 1, X1 + 1, Y0 - 1, Y1 + 1, 0, 5, "stone")
for (x, y, z), ci in list(vox.items()):
    if ci == CI["stone"] and random.random() < 0.30:
        vox[(x, y, z)] = CI["stone_dark"]

# ---------------------------------------------------------------- solid siding mass, z 5..18
box(X0, X1, Y0, Y1, 5, 19, "siding")

# ---------------------------------------------------------------- gable end walls follow the roofline
for yf in (Y0, Y1 - 1):
    for x in range(X0, X1):
        ztop = int(z_roof(abs(x - CX)))
        for z in range(18, ztop):
            vox[(x, yf, z)] = CI["siding_dark" if x % 3 == 0 else "siding"]

# ---------------------------------------------------------------- solid loft fill under the roof shell
for x in range(X0 + 2, X1 - 2):
    ztop = int(z_roof(abs(x - CX)))
    for y in range(Y0 + 1, Y1 - 1):
        for z in range(18, ztop):
            vox[(x, y, z)] = CI["dark"]

# ---------------------------------------------------------------- gambrel roof shell, 2 thick, 1-voxel gable overhang
for x in range(X0 - 1, X1 + 1):
    u = abs(x - CX)
    if u > 13.5:
        continue
    zr = int(z_roof(u)) - 1
    for y in range(Y0 - 1, Y1 + 1):
        c = "roof_seam" if y % 3 == 0 else "roof_gray"
        vox[(x, y, zr)] = CI[c]
        vox[(x, y, zr + 1)] = CI[c]

# ---------------------------------------------------------------- white rake trim (gable ends) + eave fascia
for y in (Y0 - 1, Y0, Y1 - 1, Y1):
    for x in range(X0 - 1, X1 + 1):
        zr = int(z_roof(abs(x - CX)))
        for z in (zr - 1, zr):
            if (x, y, z) in vox:
                vox[(x, y, z)] = CI["trim"]
for x in (X0 - 1, X1):
    zr = int(z_roof(abs(x - CX)))
    for y in range(Y0 - 1, Y1 + 1):
        for z in (zr - 1, zr):
            if (x, y, z) in vox:
                vox[(x, y, z)] = CI["trim"]

# ---------------------------------------------------------------- ridge cap
box(12, 14, Y0 - 1, Y1 + 1, 31, 33, "roof_seam")

# ---------------------------------------------------------------- board-and-batten striping + white corner boards
for xf in (X0, X1 - 1):
    for y in range(Y0, Y1):
        if y % 3 == 0:
            for z in range(5, 19):
                vox[(xf, y, z)] = CI["siding_dark"]
for yf in (Y0, Y1 - 1):
    for x in range(X0, X1):
        if x % 3 == 0:
            for z in range(5, 19):
                vox[(x, yf, z)] = CI["siding_dark"]
for (cx, cy) in ((X0, Y0), (X0, Y1 - 1), (X1 - 1, Y0), (X1 - 1, Y1 - 1)):
    for z in range(5, 19):
        vox[(cx, cy, z)] = CI["trim"]

# ---------------------------------------------------------------- white-trimmed square windows, eave sides
def eave_window(xf, xi, yc):
    for y in range(yc - 2, yc + 3):
        for z in range(10, 15):
            if (y in (yc - 2, yc + 2) or z in (10, 14)) and (xf, y, z) in vox:
                vox[(xf, y, z)] = CI["trim"]
    for y in range(yc - 1, yc + 2):
        for z in range(11, 14):
            vox.pop((xf, y, z), None)
            vox[(xi, y, z)] = CI["glass"]

for yc in (-12, -4, 6):
    eave_window(0, 1, yc)
for yc in (-12, 12):
    eave_window(25, 24, yc)

# ---------------------------------------------------------------- door sills: clear the foundation slab in the door spans
for x in (24, 25, 26):                       # big sliding door path, east side
    for y in range(-6, 6):
        for z in range(0, 5):
            vox.pop((x, y, z), None)
for x in (-1, 0, 1):                         # personnel door path, west side
    for y in range(11, 16):
        for z in range(0, 5):
            vox.pop((x, y, z), None)

# ---------------------------------------------------------------- big double sliding door, east eave side (to the ground)
for y in range(-6, 6):                       # dark frame ring
    for z in range(0, 15):
        if (y in (-6, 5) or z in (0, 14)) and (25, y, z) in vox:
            vox[(25, y, z)] = CI["door_dark"]
for y in range(-5, 5):                       # leaves with Z-bracing
    for z in range(0, 14):
        vox.pop((25, y, z), None)
        ly = y + 5 if y < 0 else y            # 0..4 per leaf
        lz = z                               # 0..13
        brace = ly in (0, 4) or lz in (0, 13) or lz in (ly * 2, ly * 2 + 1)
        vox[(24, y, z)] = CI["door_dark" if brace else "door_gray"]
for y in range(-7, 7):                       # sliding rail above
    vox[(25, y, 14)] = CI["door_dark"]

# ---------------------------------------------------------------- personnel door, west eave side (to the ground)
for y in range(11, 16):                       # white trim frame, explicit so it reaches the ground
    for z in range(0, 11):
        if y in (11, 15) or z in (0, 10):
            vox[(0, y, z)] = CI["trim"]
for y in range(12, 15):
    for z in range(0, 10):
        vox.pop((0, y, z), None)
        edge = y in (12, 14) or z in (0, 9)
        vox[(1, y, z)] = CI["door_dark" if edge else "door_gray"]

# ---------------------------------------------------------------- gable windows (ground) + loft windows (in the peak)
def gable_window(yf, yi, zc):
    for x in range(10, 16):
        for z in range(zc - 1, zc + 3):
            if (x in (10, 15) or z in (zc - 1, zc + 2)) and (x, yf, z) in vox:
                vox[(x, yf, z)] = CI["trim"]
    for x in range(11, 15):
        for z in range(zc, zc + 2):
            vox.pop((x, yf, z), None)
            vox[(x, yi, z)] = CI["glass"]

gable_window(Y0, Y0 + 1, 11)        # south ground
gable_window(Y1 - 1, Y1 - 2, 11)    # north ground
gable_window(Y0, Y0 + 1, 26)        # south loft
gable_window(Y1 - 1, Y1 - 2, 26)    # north loft

# ---------------------------------------------------------------- louvered cupola on the ridge
for z in range(29, 32):                        # white base
    for x in range(11, 15):
        for y in range(-2, 2):
            if x in (11, 14) or y in (-2, 1):
                vox[(x, y, z)] = CI["trim"]
for z in (32, 33):                             # louvered band
    for x in range(11, 15):
        for y in range(-2, 2):
            if x in (11, 14) or y in (-2, 1):
                corner = x in (11, 14) and y in (-2, 1)
                vox[(x, y, z)] = CI["trim"] if corner else CI["dark"]
for x in range(11, 15):                        # top plate
    for y in range(-2, 2):
        if x in (11, 14) or y in (-2, 1):
            vox[(x, y, 34)] = CI["trim"]
box(11, 15, -2, 2, 35, 36, "roof_gray")        # cap slab
box(12, 14, -1, 1, 36, 37, "roof_gray")        # cap step
vox[(12, 0, 37)] = CI["roof_seam"]             # finial

# ---------------------------------------------------------------- weathering
for (x, y, z), ci in list(vox.items()):
    if ci == CI["siding"] and random.random() < 0.06:
        vox[(x, y, z)] = CI["siding_dark"]
    elif ci == CI["roof_gray"] and random.random() < 0.05:
        vox[(x, y, z)] = CI["roof_seam"]


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
    interior_room(4, 10, -2, 6, 6, 12, vox, CI)     # ground room, west
    interior_room(16, 22, 6, 14, 6, 12, vox, CI)    # ground room, east
    interior_room(9, 16, -10, 8, 20, 26, vox, CI)   # hay loft
    write_vox(os.path.join(here, "barn_red_v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "barn_red_v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "barn_red_v1_slice_z10.png"), vox, PALETTE, 10)
    render_slice(os.path.join(here, "barn_red_v1_slice_z24.png"), vox, PALETTE, 24)
