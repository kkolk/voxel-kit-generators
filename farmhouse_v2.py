#!/usr/bin/env python3
"""Strike Bay farm line — FARMHOUSE (farmhouse_v2).

Turn-of-the-century American midwestern farmhouse at factory-kit scale
(~10 voxels per story): two-story white clapboard main block with stone
foundation, dark standing-seam gable roof, full-width front porch (wood
deck, white posts, shed roof with white ceiling), black shutters on the
front windows, brick chimney. No side ell — standalone main block variant.
Two buried interior rooms.

Generates farmhouse_v2.vox + preview/slice renders.
"""
import random
random.seed(42)

PALETTE = [  # (name, rgb); color index = position + 1
    ("stone",       (150, 145, 135)),  # 1  foundation, piers
    ("stone_dark",  (110, 105,  95)),  # 2  stone variation
    ("siding_white",(236, 232, 224)),  # 3  white clapboard
    ("siding_shade",(208, 204, 196)),  # 4  clapboard course shading
    ("trim",        (245, 242, 236)),  # 5  white trim, fascia, posts, ceiling
    ("roof_dark",   ( 74,  78,  86)),  # 6  dark standing-seam metal roof
    ("roof_seam",   ( 52,  56,  64)),  # 7  roof seams, ridge cap
    ("glass",       ( 70,  95, 115)),  # 8  window glass
    ("shutter",     ( 28,  30,  34)),  # 9  black shutters
    ("door",        ( 74,  62,  50)),  # 10 dark wood doors
    ("door_dark",   ( 48,  40,  32)),  # 11 door panels / edges
    ("wood",        (150, 116,  78)),  # 12 porch deck
    ("wood_dark",   (118,  90,  60)),  # 13 deck fascia, support piers
    ("brick",       (150,  90,  66)),  # 14 chimney stack
    ("brick_dark",  (120,  68,  50)),  # 15 chimney cap
    ("cream",       (228, 214, 180)),  # 16 side-ell siding
    ("cream_shade", (206, 192, 158)),  # 17 ell course shading
    ("steel",       (122, 126, 134)),  # 18 interiors
    ("steel_dark",  ( 62,  64,  72)),  # 19 interiors
    ("white",       (235, 235, 230)),  # 20 interiors
    ("window",      ( 18,  26,  38)),  # 21 interiors
    ("dark",        ( 30,  32,  38)),  # 22 interiors, loft fill
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

vox = {}  # (x, y, z) -> color index (1-based)

X0, X1 = 0, 20      # main block x 0..19 — 20 wide
Y0, Y1 = 0, 26      # main block y 0..25 — 26 long
CX = 9.5            # main ridge centerline

def box(x0, x1, y0, y1, z0, z1, c):
    """Inclusive-exclusive box fill."""
    ci = CI[c]
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                vox[(x, y, z)] = ci

def z_roof(u):
    """Main gable roofline: ridge 31 -> eave 24 @ u=10.5."""
    return 31.0 - u * (7.0 / 10.5)

def z_ell(v):
    """Ell gable roofline: ridge 22 -> eave 14.5 @ v=8."""
    return 22.0 - v * (7.5 / 8.0)

# ---------------------------------------------------------------- stone foundation, proud 1 voxel
box(X0 - 1, X1 + 1, Y0 - 1, Y1 + 1, 0, 5, "stone")

# ---------------------------------------------------------------- solid clapboard mass, z 5..24 (two stories)
box(X0, X1, Y0, Y1, 5, 25, "siding_white")

# ---------------------------------------------------------------- gable end walls follow the roofline
for yf in (Y0, Y1 - 1):
    for x in range(X0, X1):
        ztop = int(z_roof(abs(x - CX)))
        for z in range(24, ztop):
            vox[(x, yf, z)] = CI["siding_white"]

# ---------------------------------------------------------------- solid loft fill under the roof shell
for x in range(X0 + 2, X1 - 2):
    ztop = int(z_roof(abs(x - CX)))
    for y in range(Y0 + 1, Y1 - 1):
        for z in range(24, ztop):
            vox[(x, y, z)] = CI["dark"]

# ---------------------------------------------------------------- dark standing-seam gable roof, 2 thick, 1-voxel overhang
for x in range(X0 - 1, X1 + 1):
    u = abs(x - CX)
    if u > 10.5:
        continue
    zr = int(z_roof(u)) - 1
    for y in range(Y0 - 1, Y1 + 1):
        c = "roof_seam" if y % 3 == 0 else "roof_dark"
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
    zr = int(z_roof(10.5))
    for y in range(Y0 - 1, Y1 + 1):
        for z in (zr - 1, zr):
            if (x, y, z) in vox:
                vox[(x, y, z)] = CI["trim"]

# ---------------------------------------------------------------- ridge cap
box(9, 11, Y0 - 1, Y1 + 1, 31, 33, "roof_seam")

# ---------------------------------------------------------------- clapboard course striping on the four faces
for (x, y, z), c in list(vox.items()):
    if c == CI["siding_white"] and (x in (X0, X1 - 1) or y in (Y0, Y1 - 1)) and z % 2 == 0:
        vox[(x, y, z)] = CI["siding_shade"]

# ---------------------------------------------------------------- front porch: deck, support piers, step
box(20, 26, 2, 24, 5, 7, "wood")                       # deck floor, top z=6
for px in (21, 24):                                    # wood piers under deck
    for py in (2, 6, 10, 14, 18, 22):
        box(px, px + 1, py, py + 1, 0, 5, "wood_dark")
for y in range(2, 24):                                 # deck fascia boards
    for z in (5, 6):
        vox[(25, y, z)] = CI["wood_dark"]
for x in range(20, 26):
    for z in (5, 6):
        vox[(x, 2, z)] = CI["wood_dark"]
        vox[(x, 23, z)] = CI["wood_dark"]
box(26, 28, 10, 15, 0, 6, "wood")                      # step up to the deck

# ---------------------------------------------------------------- front porch: white posts
for py in (2, 6, 10, 14, 18, 22):
    box(24, 25, py, py + 1, 6, 14, "trim")             # posts, deck top to roof

# ---------------------------------------------------------------- front porch: shed roof + white ceiling
def porch_z(x):
    return 16 - (x - 19) // 2                          # 16 @ wall -> 13 @ x=26
for x in range(19, 27):
    rz = porch_z(x)
    for y in range(1, 25):
        c = "roof_seam" if y % 3 == 0 else "roof_dark"
        vox[(x, y, rz)] = CI[c]                        # roof surface
        vox[(x, y, rz - 1)] = CI["trim"]               # white ceiling
for y in range(1, 25):                                 # outer fascia
    for z in (12, 13):
        vox[(26, y, z)] = CI["trim"]
for y in (1, 24):                                      # side fascia
    for x in range(19, 27):
        rz = porch_z(x)
        for z in (rz - 1, rz):
            if (x, y, z) in vox:
                vox[(x, y, z)] = CI["trim"]

# ---------------------------------------------------------------- windows: front (with black shutters), back, gable ends
def front_window(yc, z0, z1, shutters=False):
    for y in range(yc - 2, yc + 3):                    # white trim frame
        for z in range(z0 - 1, z1 + 2):
            if y in (yc - 2, yc + 2) or z in (z0 - 1, z1 + 1):
                vox[(19, y, z)] = CI["trim"]
    for y in range(yc - 1, yc + 2):                   # glass + sash cross
        for z in range(z0, z1 + 1):
            vox.pop((19, y, z), None)
            mid = (y == yc) or (z == (z0 + z1) // 2)
            vox[(18, y, z)] = CI["trim"] if mid else CI["glass"]
    if shutters:                                       # black shutters
        for sy in (yc - 4, yc - 3, yc + 2, yc + 3):
            for z in range(z0, z1 + 2):
                vox[(20, sy, z)] = CI["shutter"]

def back_window(yc, z0, z1):
    for y in range(yc - 2, yc + 3):
        for z in range(z0 - 1, z1 + 2):
            if y in (yc - 2, yc + 2) or z in (z0 - 1, z1 + 1):
                vox[(0, y, z)] = CI["trim"]
    for y in range(yc - 1, yc + 2):
        for z in range(z0, z1 + 1):
            vox.pop((0, y, z), None)
            mid = (y == yc) or (z == (z0 + z1) // 2)
            vox[(1, y, z)] = CI["trim"] if mid else CI["glass"]

def gable_window(yf, yi, xc, z0, z1):
    for x in range(xc - 2, xc + 3):
        for z in range(z0 - 1, z1 + 2):
            if (x in (xc - 2, xc + 2) or z in (z0 - 1, z1 + 1)) and (x, yf, z) in vox:
                vox[(x, yf, z)] = CI["trim"]
    for x in range(xc - 1, xc + 2):
        for z in range(z0, z1 + 1):
            vox.pop((x, yf, z), None)
            mid = (x == xc) or (z == (z0 + z1) // 2)
            vox[(x, yi, z)] = CI["trim"] if mid else CI["glass"]

for yc in (5, 12, 19):
    front_window(yc, 18, 23, shutters=True)            # upstairs front, shuttered
for yc in (5, 19):
    front_window(yc, 7, 12, shutters=True)             # ground front flanks the door
for yc in (5, 12, 19):
    back_window(yc, 18, 23)
    back_window(yc, 7, 12)
for xc in (5, 14):
    gable_window(0, 1, xc, 7, 12)
    gable_window(0, 1, xc, 18, 23)
    gable_window(25, 24, xc, 18, 23)                   # y=25 ground hidden by the ell
gable_window(0, 1, 9, 26, 28)                          # gable peak windows
gable_window(25, 24, 9, 26, 28)

# ---------------------------------------------------------------- front door: full height to the ground, behind the porch
for x in (17, 18, 19, 20):                             # clear foundation in the doorway
    for y in range(10, 15):
        for z in range(0, 5):
            vox.pop((x, y, z), None)
for y in range(10, 15):                               # white trim frame, explicit to z=0
    for z in range(0, 15):
        if y in (10, 14) or z in (0, 14):
            vox[(19, y, z)] = CI["trim"]
for y in range(11, 14):                               # dark paneled leaf, inset 1
    for z in range(0, 14):
        vox.pop((19, y, z), None)
        panel = y in (11, 13) or z in (0, 13) or z in (6, 7)
        vox[(18, y, z)] = CI["door_dark"] if panel else CI["door"]

# ---------------------------------------------------------------- brick chimney near the ridge
box(9, 11, 6, 8, 26, 36, "brick")                     # stack, through the roof
box(8, 12, 5, 9, 36, 37, "brick_dark")                # wider cap course
box(9, 11, 6, 8, 37, 38, "dark")                      # flue


# ---------------------------------------------------------------- stone variation on foundation + piers
for (x, y, z), c in list(vox.items()):
    if c == CI["stone"] and random.random() < 0.30:
        vox[(x, y, z)] = CI["stone_dark"]

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
                   proj(x + 1, y + 1, z + 1), proj(x, y + 1, z + 1)]
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
    interior_room(3, 9, 3, 11, 6, 12, vox, CI)      # main ground floor, west
    interior_room(11, 17, 14, 22, 6, 12, vox, CI)   # main ground floor, east
    # user direction 2026-09-25: drop the lower 3 voxel layers, shift the rest to grade
    vox = {(x, y, z - 3): c for (x, y, z), c in vox.items() if z >= 3}
    write_vox(os.path.join(here, "farmhouse_v2.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "farmhouse_v2_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "farmhouse_v2_slice_z14.png"), vox, PALETTE, 14)
    render_slice(os.path.join(here, "farmhouse_v2_slice_z8.png"), vox, PALETTE, 8)
