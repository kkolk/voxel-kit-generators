"""harbor-tenement-v1 — dockworkers' tenement block, 1960s run-down Havana harbor.

36 x 24 (3 x 2 bays), 3 stories, wall top z=29. Ground-floor street arcade
with stepped arches, recessed shop doorways (one striped awning), upper floors
in faded turquoise / pink plaster with peeling patches, shuttered windows,
iron balconies, rooftop tinacos + crooked TV antenna, PATRIA O MUERTE mural
on the rear wall. Hollow shell + buried interior room z 1..7.
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
R = random.Random(20261004)

W, D = 36, 24
BAYS = [(0, 11), (12, 23), (24, 35)]
BAY_COLORS = ["plaster_turq", "plaster_pink", "plaster_turq"]
CENTERS = [6, 18, 30]
FLOORS = [10, 20]  # balcony slab level of the two upper stories


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
    """Scatter n plaster_peel patches on a wall face (u along wall, v = z)."""
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


def rust_streak(face, fixed, u, z_top, length):
    for k in range(length):
        p = (u, fixed, z_top - k) if face == "y" else (fixed, u, z_top - k)
        if vox.get(p) in plaster_like or vox.get(p) == CI["plaster_peel"]:
            vox[p] = CI["rust"]


def draw_text_y(fixed_y, x0, z_top, text, fg="dark"):
    """3x5 text on a y=fixed plane, reading along +x, rows downward from z_top."""
    for ch in text:
        g = FONT_3X5.get(ch, FONT_3X5[" "])
        for r in range(5):
            for c in range(3):
                if g[r][c] == "#":
                    vox[(x0 + c, fixed_y, z_top - r)] = CI[fg]
        x0 += 4


# ---------------------------------------------------------------- walls: ground floor
# side + rear ground walls (T=2)
box(0, 1, 0, 23, 0, 9, "plaster")
box(34, 35, 0, 23, 0, 9, "plaster")
box(0, 35, 22, 23, 0, 9, "plaster")
# arcade columns at bay lines (front, y 0..1)
for c in (0, 12, 24, 36):
    box(max(0, c - 1), min(35, c + 1), 0, 1, 0, 9, "plaster")
# stepped arch fill between columns (y 0..1, z 7..9)
for a0, a1 in ((2, 10), (14, 22), (26, 33)):
    for z in (7, 8, 9):
        inset = z - 6
        box(a0, a0 + inset - 1, 0, 1, z, z, "plaster")
        box(a1 - inset + 1, a1, 0, 1, z, z, "plaster")
# recessed loggia wall + ceiling
box(0, 35, 4, 5, 0, 9, "plaster")
box(0, 35, 2, 5, 10, 10, "plaster")

# ---------------------------------------------------------------- walls: upper floors (per-bay color)
for (bx0, bx1), col in zip(BAYS, BAY_COLORS):
    box(bx0, bx1, 0, 1, 10, 29, col)    # front
    box(bx0, bx1, 22, 23, 10, 29, col)  # rear
box(0, 1, 0, 11, 10, 29, "plaster_turq")   # west upper
box(0, 1, 12, 23, 10, 29, "plaster_pink")
box(34, 35, 0, 11, 10, 29, "plaster_turq")  # east upper
box(34, 35, 12, 23, 10, 29, "plaster_pink")

# ---------------------------------------------------------------- peeling paint + water table
peel_patch("y", 0, 0, 35, 12, 27, 42)
peel_patch("y", 23, 0, 35, 12, 27, 42)
peel_patch("x", 0, 0, 23, 3, 27, 26)
peel_patch("x", 35, 0, 23, 3, 27, 26)
peel_patch("y", 0, 0, 35, 2, 8, 18)   # ground floor, denser near grade
peel_patch("y", 23, 0, 35, 2, 8, 18)
peel_patch("x", 0, 0, 23, 2, 8, 12)
peel_patch("x", 35, 0, 23, 2, 8, 12)

for (x, y, z), ci in list(vox.items()):
    if z <= 1 and ci in plaster_like and (x in (0, 35) or y in (0, 23)):
        vox[(x, y, z)] = CI["concrete"]

# ---------------------------------------------------------------- openings: recessed shopfronts
for ci, c in enumerate(CENTERS):
    # dark shop doorway
    carve(c - 2, c + 1, 4, 5, 0, 7)
    box(c - 2, c + 1, 4, 5, 0, 7, "dark")
    # barred window beside it (face y=4)
    wx0, wx1 = c + 3, c + 5
    carve(wx0, wx1, 4, 5, 3, 7)
    box(wx0, wx1, 4, 4, 3, 7, "glass_dark")
    for bx in range(wx0, wx1 + 1, 2):  # iron bar grid on the face
        box(bx, bx, 4, 4, 3, 7, "iron")
    box(wx0, wx1, 4, 4, 5, 5, "iron")
    box(wx0, wx1, 4, 4, 3, 3, "concrete")  # sill

# rear ground windows + rear door
for c in CENTERS:
    carve(c - 2, c, 22, 23, 3, 7)
    box(c - 2, c, 23, 23, 3, 7, "glass_dark")
    for bx in range(c - 2, c + 1, 2):
        box(bx, bx, 23, 23, 3, 7, "iron")
    box(c - 2, c, 23, 23, 5, 5, "iron")
carve(16, 19, 22, 23, 0, 7)
box(16, 19, 22, 23, 0, 7, "dark")

# side ground windows (barred)
for sx in (0, 35):
    for wy0 in (5, 16):
        carve(sx, sx, wy0, wy0 + 2, 2, 8)
        box(sx, sx, wy0, wy0 + 2, 2, 8, "glass_dark")
        for wy in range(wy0, wy0 + 3, 2):
            box(sx, sx, wy, wy, 2, 8, "iron")
        box(sx, sx, wy0, wy0 + 2, 5, 5, "iron")

# ---------------------------------------------------------------- upper windows + balcony doors + shutters
for c in CENTERS:
    for b in FLOORS:
        # balcony door (glass_dark)
        carve(c - 1, c + 2, 0, 1, b, b + 7)
        box(c - 1, c + 2, 0, 0, b, b + 7, "glass_dark")
        # flanking shuttered windows
        for wx0, wx1 in ((c - 5, c - 3), (c + 3, c + 5)):
            z0, z1 = b + 2, b + 8
            carve(wx0, wx1, 0, 1, z0, z1)
            box(wx0, wx1, 0, 0, z0, z1, "glass_dark")
            # left shutter closed over window, right shutter open flat on wall
            box(wx0, wx0 + 1, -1, -1, z0, z1, "wood")
            ox0 = wx1 + 1
            if ox0 + 1 > 35:
                ox0 = wx0 - 2
            box(ox0, ox0 + 1, -1, -1, z0, z1, "wood")
            box(wx0 - 1, wx1 + 1, -1, -1, z0 - 1, z0 - 1, "concrete")  # proud sill
            rust_streak("y", 0, wx0 + 1, z0 - 2, R.randint(3, 5))

# side upper windows (barred)
for sx in (0, 35):
    for b in FLOORS:
        carve(sx, sx, 10, 12, b + 2, b + 8)
        box(sx, sx, 10, 12, b + 2, b + 8, "glass_dark")
        for wy in range(10, 13, 2):
            box(sx, sx, wy, wy, b + 2, b + 8, "iron")
        box(sx, sx, 10, 12, b + 5, b + 5, "iron")
        rust_streak("x", sx, 11, b + 1, R.randint(3, 5))

# ---------------------------------------------------------------- balconies (iron, proud 1)
for bi, c in enumerate(CENTERS):
    for b in FLOORS:
        box(c - 3, c + 2, -1, 1, b, b, "concrete")       # slab
        box(c - 3, c + 2, 0, 0, b - 1, b - 1, "iron")    # corbel strip
        for px in (c - 3, c, c + 2):                     # front posts
            box(px, px, -1, -1, b + 1, b + 3, "iron")
        for px, py in ((c - 3, 1), (c + 2, 1)):          # back corner posts
            box(px, px, py, py, b + 1, b + 3, "iron")
        box(c - 3, c + 2, -1, -1, b + 3, b + 3, "iron")  # front rail
        box(c - 3, c - 3, -1, 1, b + 3, b + 3, "iron")   # side rails
        box(c + 2, c + 2, -1, 1, b + 3, b + 3, "iron")
        if bi == 1 and b == 10:                          # crate on one balcony
            box(c - 1, c, -1, 0, b + 1, b + 2, "wood")

# ---------------------------------------------------------------- striped awning over bay-2 shop doorway
for x in range(14, 23):
    col = "white" if ((x - 14) // 2) % 2 == 0 else "pump_red"
    box(x, x, 3, 4, 8, 9, col)
    box(x, x, 1, 2, 6, 7, col)
box(14, 14, 1, 1, 0, 6, "iron")
box(22, 22, 1, 1, 0, 6, "iron")

# ---------------------------------------------------------------- roof, parapet, coping
box(0, 35, 0, 23, 30, 31, "roof_grey")
box(0, 0, 0, 23, 32, 34, "plaster")
box(35, 35, 0, 23, 32, 34, "plaster")
box(0, 35, 0, 0, 32, 34, "plaster")
box(0, 35, 23, 23, 32, 34, "plaster")
box(0, 0, 0, 23, 35, 35, "coping")
box(35, 35, 0, 23, 35, 35, "coping")
box(0, 35, 0, 0, 35, 35, "coping")
box(0, 35, 23, 23, 35, 35, "coping")

# two tinaco water tanks on wood stands
for tx0, ty0 in ((6, 16), (26, 5)):
    for lx, ly in ((tx0, ty0), (tx0 + 3, ty0), (tx0, ty0 + 3), (tx0 + 3, ty0 + 3)):
        box(lx, lx, ly, ly, 32, 33, "wood")
    box(tx0, tx0 + 3, ty0, ty0 + 3, 34, 37, "tinaco")
    box(tx0, tx0 + 3, ty0, ty0 + 3, 38, 38, "tinaco")

# crooked iron TV antenna (elbow voxel keeps the bend 6-connected)
box(30, 30, 18, 18, 32, 37, "iron")
box(31, 31, 18, 18, 37, 37, "iron")
box(31, 31, 18, 18, 38, 42, "iron")
box(28, 32, 18, 18, 39, 39, "iron")
box(31, 31, 16, 20, 41, 41, "iron")

# litter on the roof
for _ in range(6):
    vox[(R.randint(2, 33), R.randint(2, 21), 32)] = CI["dark"]

# ---------------------------------------------------------------- mural: PATRIA O MUERTE on the rear wall
box(1, 34, 24, 24, 11, 23, "cream")  # proud sign band
draw_text_y(24, 6, 22, "PATRIA")
draw_text_y(24, 2, 16, "O MUERTE")
for (x, y, z), ci in list(vox.items()):  # weather the letters
    if y == 24 and ci == CI["dark"] and 11 <= z <= 23 and R.random() < 0.07:
        vox[(x, y, z)] = CI["cream"]

# ---------------------------------------------------------------- buried interior room
box(4, 32, 6, 18, 0, 8, "concrete")


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
                   proj(x + 1, y + 1, z + 1), proj(x, y + 1, z + 1)]
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
    interior_room(5, 32, 7, 18, 1, 7, vox, CI)

    bad = floater_sweep(vox)
    print(f"floater_sweep: {len(bad)} floating component(s)")
    for comp in bad[:5]:
        print(f"  {len(comp)} vox, e.g. {comp[:8]}")

    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    print(f"footprint {(max(xs) - min(xs) + 1)}x{(max(ys) - min(ys) + 1)}x{(max(zs) + 1)}"
          f" (x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)}, z {min(zs)}..{max(zs)})")

    write_vox("harbor-tenement-v1.vox", vox, PALETTE)
    render_preview("harbor-tenement-v1_preview.png", vox, PALETTE)
    render_slice("harbor-tenement-v1_slice_z04.png", vox, PALETTE, 4)
