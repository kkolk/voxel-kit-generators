"""harbor-capitania-v1 — port authority office, 1960s run-down Havana harbor.

24 x 24 (2 x 2 bays), 2 stories, wall top z=20. Corner watchtower 12x12
rising to z=29 with arched openings + pyramid cap + railed walkway, red tile
gable roof with missing tiles, tall barred windows with open shutters,
heavy wood double door with stone steps, wrought-iron front balcony,
flagpole with red flag, CAPITANIA sign band (two-line stack on the rear
face — 9 glyphs cannot fit the 24-vox front in the 3x5 font).
Hollow shell + buried interior room z 1..7.
FACTORY_VOXEL 0.13. z-up, origin at footprint min corner, at grade.
"""

import random
import struct
from PIL import Image, ImageDraw

PALETTE = [
    ("concrete",      (170, 166, 158)),  # water table, sills, lintels, dock
    ("concrete_dark", (112, 108, 100)),
    ("coping",        (202, 198, 190)),  # parapet coping
    ("plaster",       (196, 164, 120)),  # aduana faded ochre plaster
    ("plaster_peel",  (150, 140, 128)),  # peeled plaster / bare render patches
    ("plaster_turq",  (110, 168, 158)),  # tenement faded turquoise
    ("plaster_pink",  (198, 140, 128)),  # tenement faded pink
    ("brick",         (150,  90,  66)),  # chimney, patches
    ("brick_dark",    (120,  68,  50)),
    ("glass",         ( 72,  98, 118)),  # window glass
    ("glass_dark",    ( 44,  62,  78)),  # broken/boarded panes
    ("steel",         (122, 126, 134)),
    ("steel_dark",    ( 62,  64,  72)),  # sash, patches, corrugated repairs
    ("white",         (235, 235, 230)),
    ("window",        ( 18,  26,  38)),  # dark glass / sign backboards
    ("dark",          ( 32,  34,  40)),  # door leaves, tires, litter
    ("wood",          (125,  92,  62)),  # shutters, sign boards, doors
    ("wood_dark",     ( 90,  66,  44)),
    ("rust",          (142,  82,  50)),  # streaks under sills/roofline
    ("roof_grey",     (100, 104, 100)),  # weathered roof slabs
    ("roof_red",      (150,  70,  58)),  # capitania tile roof
    ("iron",          ( 70,  74,  82)),  # railings, window bars
    ("neon_pink",     (255,  80, 160)),  # bar sign tubes
    ("neon_cyan",     ( 80, 230, 255)),  # bar sign tubes / border
    ("neon_yellow",   (255, 220,  90)),  # bar sign tubes
    ("pump_red",      (180,  50,  45)),  # gas pump body, flag
    ("cream",         (232, 220, 190)),  # pump panels, sign boards, letters
    ("sign_blue",     ( 50,  90, 150)),  # PESCA logo
    ("tinaco",        ( 40,  42,  48)),  # black rooftop water tanks
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

FONT_3X5 = {
 "A": [".#.","#.#","###","#.#","#.#"],
 "B": ["##.","#.#","##.","#.#","##."],
 "C": [".##","#..","#..","#..",".##"],
 "D": ["##.","#.#","#.#","#.#","##."],
 "E": ["###","#..","##.","#..","###"],
 "F": ["###","#..","##.","#..","#.."],
 "G": [".##","#..","#.#","#.#",".##"],
 "H": ["#.#","#.#","###","#.#","#.#"],
 "I": ["###",".#.",".#.",".#.","###"],
 "L": ["#..","#..","#..","#..","###"],
 "M": ["#.#","###","###","#.#","#.#"],
 "N": ["#.#","##.","##.","#.#","#.#"],
 "O": [".#.","#.#","#.#","#.#",".#."],
 "P": ["##.","#.#","##.","#..","#.."],
 "Q": [".#.","#.#","#.#","##.",".##"],
 "R": ["##.","#.#","##.","#.#","#.#"],
 "S": [".##","#..",".#.","..#","##."],
 "T": ["###",".#.",".#.",".#.",".#."],
 "U": ["#.#","#.#","#.#","#.#","###"],
 " ": ["...","...","...","...","..."],
}

vox = {}
R = random.Random(20261005)

W = 24  # footprint 24 x 24


def box(x0, x1, y0, y1, z0, z1, c):
    ci = CI[c]
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                vox[(x, y, z)] = ci


def carve(x0, x1, y0, y1, z0, z1):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                vox.pop((x, y, z), None)


plaster_like = {CI["plaster"], CI["plaster_turq"], CI["plaster_pink"]}


def peel_patch(face, fixed, u0, u1, v0, v1, n):
    for _ in range(n):
        w = R.randint(2, 4)
        h = R.randint(2, 3)
        u = R.randint(u0, u1 - w)
        v = R.randint(v0, v1 - h)
        for du in range(w):
            for dv in range(h):
                p = (u + du, fixed, v + dv) if face == "y" else (fixed, u + du, v + dv)
                if vox.get(p) in plaster_like:
                    vox[p] = CI["plaster_peel"]


def draw_text_y(fixed_y, x0, z_top, text, fg="dark"):
    for ch in text:
        g = FONT_3X5.get(ch, FONT_3X5[" "])
        for r in range(5):
            for c in range(3):
                if g[r][c] == "#":
                    vox[(x0 + c, fixed_y, z_top - r)] = CI[fg]
        x0 += 4


def window(face, a0, a1, z0, z1):
    """Tall barred window: glass_dark, iron bar grid, open wood shutters
    flat on the wall (proud 1), proud concrete sill, rust streak below."""
    if face == "fn":      # front, wall y 0..1
        carve(a0, a1, 0, 1, z0, z1)
        F = lambda u, z: (u, 0, z)
        P = lambda u, z: (u, -1, z)
    elif face == "fs":    # rear, wall y 22..23
        carve(a0, a1, 22, 23, z0, z1)
        F = lambda u, z: (u, 23, z)
        P = lambda u, z: (u, 24, z)
    elif face == "fw":    # west, wall x 0..1
        carve(0, 1, a0, a1, z0, z1)
        F = lambda u, z: (0, u, z)
        P = lambda u, z: (-1, u, z)
    elif face == "fe":    # east, wall x 22..23
        carve(22, 23, a0, a1, z0, z1)
        F = lambda u, z: (23, u, z)
        P = lambda u, z: (24, u, z)
    for u in range(a0, a1 + 1):
        for z in range(z0, z1 + 1):
            vox[F(u, z)] = CI["glass_dark"]
    for u in range(a0, a1 + 1, 2):
        for z in range(z0, z1 + 1):
            vox[F(u, z)] = CI["iron"]
    for z in (z0, (z0 + z1) // 2, z1):
        for u in range(a0, a1 + 1):
            vox[F(u, z)] = CI["iron"]
    for u in range(a0 - 2, a0):
        for z in range(z0, z1 + 1):
            vox[P(u, z)] = CI["wood"]
    for u in range(a1 + 1, a1 + 3):
        for z in range(z0, z1 + 1):
            vox[P(u, z)] = CI["wood"]
    for u in range(a0 - 1, a1 + 2):
        vox[P(u, z0 - 1)] = CI["concrete"]
    for k in range(R.randint(3, 5)):
        p = F((a0 + a1) // 2, z0 - 2 - k)
        if vox.get(p) in plaster_like:
            vox[p] = CI["rust"]


# ---------------------------------------------------------------- main block walls (T=2, z 0..20)
box(0, 23, 0, 1, 0, 20, "plaster")
box(0, 23, 22, 23, 0, 20, "plaster")
box(0, 1, 0, 23, 0, 20, "plaster")
box(22, 23, 0, 23, 0, 20, "plaster")

# heavy peeling
peel_patch("y", 0, 0, 23, 3, 19, 34)
peel_patch("y", 23, 0, 23, 3, 19, 34)
peel_patch("x", 0, 0, 23, 3, 19, 30)
peel_patch("x", 23, 0, 23, 3, 19, 30)

# concrete water table
for (x, y, z), ci in list(vox.items()):
    if z <= 1 and ci in plaster_like and (x in (0, 23) or y in (0, 23)):
        vox[(x, y, z)] = CI["concrete"]

# ---------------------------------------------------------------- door, windows
carve(9, 14, 0, 1, 0, 9)
box(9, 14, 0, 1, 0, 9, "wood_dark")          # heavy double door, closed
box(8, 8, 0, 1, 0, 10, "concrete")          # surround
box(15, 15, 0, 1, 0, 10, "concrete")
box(8, 15, 0, 1, 10, 10, "concrete")        # lintel
box(7, 16, -1, 1, 0, 0, "concrete")         # steps (proud 1)
box(8, 15, 0, 1, 0, 1, "concrete")

window("fn", 2, 5, 2, 9)
window("fn", 18, 21, 2, 9)
window("fn", 2, 5, 11, 18)
window("fn", 18, 21, 11, 18)
window("fs", 2, 5, 2, 9)
window("fs", 18, 21, 2, 9)
window("fw", 4, 7, 2, 9)
window("fw", 16, 19, 2, 9)
window("fw", 4, 7, 11, 18)
window("fw", 10, 13, 11, 18)
window("fw", 16, 19, 11, 18)
window("fe", 4, 7, 2, 9)
window("fe", 4, 7, 11, 18)

# ---------------------------------------------------------------- front balcony (upper)
carve(10, 13, 0, 1, 10, 17)
box(10, 13, 0, 0, 10, 17, "glass_dark")     # balcony door
box(8, 15, -1, 1, 10, 10, "concrete")       # slab, proud 1
box(8, 15, 0, 0, 9, 9, "iron")              # corbel strip
for px in (8, 11, 15):
    box(px, px, -1, -1, 11, 13, "iron")
for px, py in ((8, 1), (15, 1)):
    box(px, px, py, py, 11, 13, "iron")
box(8, 15, -1, -1, 13, 13, "iron")
box(8, 8, -1, 1, 13, 13, "iron")
box(15, 15, -1, 1, 13, 13, "iron")

# ---------------------------------------------------------------- sign band (rear): CAPITANIA as two-line stack
box(0, 23, 24, 24, 9, 21, "cream")
# (lettering removed 2026-10-04: cream band kept blank)

# ---------------------------------------------------------------- gable roof (ridge along x at y=12)
def roof_z(y):
    return 22 + round(5 * (12 - abs(y - 12)) / 12)

for y in range(0, 25):
    zt = roof_z(y)
    x1 = 11 if y >= 12 else 23   # tower occupies x 12..23, y 12..23
    box(0, x1, y, y, zt - 1, zt, "roof_red")
box(0, 23, -1, -1, 21, 22, "roof_red")   # eave overhangs, proud 1
box(0, 23, 24, 24, 21, 22, "roof_red")
for x in (0, 1):
    for y in range(0, 25):
        zt = roof_z(y)
        if zt - 2 >= 21:
            box(x, x, y, y, 21, zt - 2, "plaster")
for x in (22, 23):
    for y in range(0, 12):
        zt = roof_z(y)
        if zt - 2 >= 21:
            box(x, x, y, y, 21, zt - 2, "plaster")
box(0, 11, 11, 13, 28, 28, "roof_red")   # ridge roll
for px, py in ((4, 3), (5, 3), (4, 4), (5, 4), (4, 5), (5, 5),
               (14, 5), (15, 5), (14, 6), (15, 6),
               (20, 2), (21, 2), (20, 3)):
    zt = roof_z(py)
    if (px, py, zt) in vox:
        vox[(px, py, zt)] = CI["roof_grey"]   # missing tiles

# ---------------------------------------------------------------- corner watchtower (x 12..23, y 12..23, z 0..29)
box(12, 23, 12, 13, 0, 29, "plaster")
box(12, 23, 22, 23, 0, 29, "plaster")
box(12, 13, 12, 23, 0, 29, "plaster")
box(22, 23, 12, 23, 0, 29, "plaster")
peel_patch("y", 23, 12, 23, 3, 27, 14)
peel_patch("x", 23, 12, 23, 3, 27, 14)
peel_patch("y", 12, 12, 23, 3, 27, 10)
peel_patch("x", 12, 12, 23, 3, 27, 10)
for (x, y, z), ci in list(vox.items()):
    if z <= 1 and ci in plaster_like and (x == 23 or y == 23) and x >= 12 and y >= 12:
        vox[(x, y, z)] = CI["concrete"]

# arched openings on all four tower faces, z 24..27
for face in ("s", "n", "w", "e"):
    if face == "s":
        carve(16, 19, 12, 13, 24, 26); carve(17, 18, 12, 13, 27, 27)
        box(16, 19, 12, 13, 24, 26, "glass_dark"); box(17, 18, 12, 13, 27, 27, "glass_dark")
        box(15, 20, 12, 12, 23, 23, "concrete")
    elif face == "n":
        carve(16, 19, 22, 23, 24, 26); carve(17, 18, 22, 23, 27, 27)
        box(16, 19, 22, 23, 24, 26, "glass_dark"); box(17, 18, 22, 23, 27, 27, "glass_dark")
        box(15, 20, 23, 23, 23, 23, "concrete")
    elif face == "w":
        carve(12, 13, 16, 19, 24, 26); carve(12, 13, 17, 18, 27, 27)
        box(12, 13, 16, 19, 24, 26, "glass_dark"); box(12, 13, 17, 18, 27, 27, "glass_dark")
        box(12, 12, 15, 20, 23, 23, "concrete")
    elif face == "e":
        carve(22, 23, 16, 19, 24, 26); carve(22, 23, 17, 18, 27, 27)
        box(22, 23, 16, 19, 24, 26, "glass_dark"); box(22, 23, 17, 18, 27, 27, "glass_dark")
        box(23, 23, 15, 20, 23, 23, "concrete")

# pyramid cap + railed walkway around its base
box(13, 22, 13, 22, 30, 30, "roof_red")
box(14, 21, 14, 21, 31, 31, "roof_red")
box(15, 20, 15, 20, 32, 32, "roof_red")
box(16, 19, 16, 19, 33, 33, "roof_red")
for px, py in ((12, 12), (17, 12), (23, 12), (12, 17), (23, 17),
               (12, 23), (17, 23), (23, 23)):
    box(px, px, py, py, 30, 32, "iron")
box(12, 23, 12, 12, 32, 32, "iron")
box(12, 23, 23, 23, 32, 32, "iron")
box(12, 12, 12, 23, 32, 32, "iron")
box(23, 23, 12, 23, 32, 32, "iron")

# flagpole + red flag
box(18, 18, 18, 18, 30, 40, "steel_dark")
for x in range(19, 25):
    for z in range(36, 40):
        vox[(x, 18, z)] = CI["pump_red"]
        if x >= 22:  # wave step, 2-thick so the fly end stays 6-connected
            vox[(x, 19, z)] = CI["pump_red"]

# ---------------------------------------------------------------- buried interior room
box(2, 9, 2, 9, 0, 8, "concrete")


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


# ---------------------------------------------------------------- .vox writer (MagicaVoxel 150)
def write_vox(path, vox, PALETTE):
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


# ---------------------------------------------------------------- isometric preview render
def render_preview(path, vox, PALETTE, scale=2):
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
            dr.polygon([(px_ + ox, py_ + oy) for px_, py_ in pts], fill=left)
        if (x + 1, y, z) not in vset:
            pts = [proj(x + 1, y, z), proj(x + 1, y + 1, z),
                   proj(x + 1, y + 1, z + 1), proj(x, y, z + 1)]
            dr.polygon([(px_ + ox, py_ + oy) for px_, py_ in pts], fill=right)
    img.save(path)
    print(f"wrote {path} {img.size}")


# ---------------------------------------------------------------- top-down slice (dev check for buried interiors)
def render_slice(path, vox, PALETTE, z):
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


def floater_sweep(vox):
    pts = set(vox.keys())
    seen = set()
    bad = []
    while pts:
        seed = pts.pop()
        stack = [seed]
        seen.add(seed)
        comp = [seed]
        touches = seed[2] == 0
        while stack:
            x, y, z = stack.pop()
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                      (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in pts and q not in seen:
                    seen.add(q)
                    pts.discard(q)
                    stack.append(q)
                    comp.append(q)
                    if q[2] == 0:
                        touches = True
        if not touches:
            bad.append(comp)
    return bad


if __name__ == "__main__":
    interior_room(3, 9, 3, 9, 1, 7, vox, CI)

    bad = floater_sweep(vox)
    print(f"floater_sweep: {len(bad)} floating component(s)")
    for comp in bad[:5]:
        print(f"  {len(comp)} vox, e.g. {comp[:8]}")

    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    print(f"footprint {(max(xs) - min(xs) + 1)}x{(max(ys) - min(ys) + 1)}x{(max(zs) + 1)}"
          f" (x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)}, z {min(zs)}..{max(zs)})")

    write_vox("harbor-capitania-v1.vox", vox, PALETTE)
    render_preview("harbor-capitania-v1_preview.png", vox, PALETTE)
    render_slice("harbor-capitania-v1_slice_z04.png", vox, PALETTE, 4)
