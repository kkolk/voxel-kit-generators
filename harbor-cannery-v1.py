"""harbor-cannery-v1 — 1960s Havana fish cannery.

48x24 footprint (4x2 bays), single tall story, sawtooth roof with glazed
faces, faded fish logo, exterior steel stair to a roof catwalk,
brick chimney, wall pipes. FACTORY_VOXEL 0.13.
Hollow shell + buried interior room z 1..7.
"""
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

CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}
vox = {}

def box(x0, x1, y0, y1, z0, z1, name):
    ci = CI[name]
    for x in range(x0, x1):
        for y in range(y0, y1):
            for z in range(z0, z1):
                vox[(x, y, z)] = ci

def rnd(*args):
    h = 2166136261
    for a in args:
        h = ((h ^ (int(a) & 0xffffffff)) * 16777619) & 0xffffffff
    h ^= h >> 13
    h = (h * 0x5bd1e995) & 0xffffffff
    h ^= h >> 15
    return h

W, D, H = 48, 24, 14  # footprint, wall top

# ---- walls: whitewashed brick gone gray (concrete), T=2
box(0, W, 0, 2, 0, H, "concrete")      # south (y=0)
box(0, W, D - 2, D, 0, H, "concrete")  # north
box(0, 2, 0, D, 0, H, "concrete")      # west
box(W - 2, W, 0, D, 0, H, "concrete")  # east

# ---- grime near grade
for x in range(W):
    for z in range(0, 3):
        for y in (0, 1, D - 2, D - 1):
            if rnd(x, y, z, 61) % 100 < 35:
                vox[(x, y, z)] = CI["concrete_dark"]
for y in range(D):
    for z in range(0, 3):
        for x in (0, 1, W - 2, W - 1):
            if rnd(x, y, z, 62) % 100 < 35:
                vox[(x, y, z)] = CI["concrete_dark"]

# ---- south windows: steel sash, ~40% broken, one boarded
for idx, c in enumerate((4, 20, 28, 44)):
    x0, x1 = c - 2, c + 2
    for x in range(x0, x1):
        for z in range(6, 11):
            vox.pop((x, 0, z), None)
            vox.pop((x, 1, z), None)
    boarded = (idx == 2)
    broken = (idx * 7 + 3) % 10 < 4
    for x in range(x0, x1):
        for z in range(6, 11):
            edge = x in (x0, x1 - 1) or z in (6, 10)
            if boarded:
                col = "wood_dark" if z in (7, 9) else "wood"
            elif edge:
                col = "steel_dark"
            else:
                col = "glass_dark" if broken else "glass"
            vox[(x, 0, z)] = CI[col]
            vox[(x, 1, z)] = CI[col]
    box(x0 - 1, x1 + 1, 0, 2, 5, 6, "concrete")  # sill
    for zz in range(2, 5):  # rust weep under sill
        if vox.get((c, 0, zz)) == CI["concrete"]:
            vox[(c, 0, zz)] = CI["rust"]

# ---- rusted loading doors (south)
for (dx0, dx1) in ((9, 15), (33, 39)):
    for x in range(dx0, dx1):
        for z in range(2, 10):
            vox.pop((x, 0, z), None)
            vox.pop((x, 1, z), None)
    for x in range(dx0, dx1):
        for z in range(2, 10):
            col = "steel_dark"
            if z in (4, 7):
                col = "dark"
            if rnd(x, z, 71) % 100 < 22:
                col = "rust"
            vox[(x, 0, z)] = CI[col]
            vox[(x, 1, z)] = CI[col]
    box(dx0 - 1, dx1 + 1, 0, 2, 10, 11, "concrete")  # lintel
    box(dx0 - 1, dx1 + 1, 0, 2, 1, 2, "concrete")    # threshold
    for z in range(1, 11):  # side trim (recolor wall face)
        for x in (dx0 - 1, dx1):
            for y in (0, 1):
                if vox.get((x, y, z)) not in (CI["steel_dark"], CI["dark"],
                                              CI["rust"]):
                    vox[(x, y, z)] = CI["concrete"]

# ---- personnel door (south)
for x in range(22, 26):
    for z in range(0, 12):
        vox.pop((x, 0, z), None)
        vox.pop((x, 1, z), None)
        vox[(x, 0, z)] = CI["dark"]
        vox[(x, 1, z)] = CI["dark"]
box(21, 27, 0, 2, 12, 13, "concrete")  # lintel

# ---- wall pipes (steel_dark verticals on the faces)
for z in range(0, H):
    vox[(8, 0, z)] = CI["steel_dark"]
    vox[(40, 0, z)] = CI["steel_dark"]
    vox[(40, D - 1, z)] = CI["steel_dark"]

# ---- big PESCA sign on the north face (y=23 plane): fish + letters
def paint_fish(x0, yf, z0):
    for dx in range(9):  # body ellipse
        for dy in range(-2, 3):
            if (dx - 4) ** 2 / 16 + dy ** 2 / 6 <= 1:
                if rnd(x0 + dx, z0 + 2 + dy, 82) % 12 == 0:
                    continue
                vox[(x0 + dx, yf, z0 + 2 + dy)] = CI["sign_blue"]
    for t in range(4):  # tail triangle
        for dy in range(-t, t + 1):
            if rnd(x0 + 9 + t, z0 + 2 + dy, 83) % 12 == 0:
                continue
            vox[(x0 + 9 + t, yf, z0 + 2 + dy)] = CI["sign_blue"]
    vox[(x0 + 2, yf, z0 + 3)] = CI["dark"]  # eye

paint_fish(4, D - 1, 6)
# (PESCA lettering removed 2026-10-04: fish logo kept)

# ---- small high windows on the north face (flank the sign)
for x0 in (2, 42):
    for x in range(x0, x0 + 3):
        for z in range(10, 13):
            vox.pop((x, D - 2, z), None)
            vox.pop((x, D - 1, z), None)
    for x in range(x0, x0 + 3):
        for z in range(10, 13):
            edge = x in (x0, x0 + 2) or z in (10, 12)
            col = "steel_dark" if edge else "glass_dark"
            vox[(x, D - 2, z)] = CI[col]
            vox[(x, D - 1, z)] = CI[col]

# ---- sawtooth roof: 3 teeth, 16 wide each
# slopes first, then glazed faces overwrite the top edge cleanly
for i in range(3):
    xg = 16 * i
    for x in range(xg, xg + 16):
        zt = 22 - ((x - xg) * 8) // 16
        for y in range(0, D):
            vox[(x, y, zt)] = CI["roof_grey"]
            vox[(x, y, zt - 1)] = CI["roof_grey"]

for i in range(3):
    xg = 16 * i
    for y in (0, 6, 12, 18, 23):  # mullions
        for z in range(H, 23):
            vox[(xg, y, z)] = CI["steel_dark"]
    for z in (H, 22):  # head + sill rails
        for y in range(0, D):
            vox[(xg, y, z)] = CI["steel_dark"]
    for y in range(0, D):  # glass between mullions
        if y in (0, 6, 12, 18, 23):
            continue
        for z in range(H + 1, 22):
            vox[(xg, y, z)] = CI["glass"]

# ---- end-wall profile fill on the y faces (skip glazed x planes)
for x in range(0, W):
    if x % 16 == 0:
        continue
    zt = 22 - ((x % 16) * 8) // 16
    for y in (0, 1, D - 2, D - 1):
        for z in range(H, zt + 1):
            if (x, y, z) not in vox:
                vox[(x, y, z)] = CI["concrete"]

# ---- louvered vents on each slope
for i in range(3):
    x0 = 16 * i + 6
    for x in range(x0, x0 + 4):
        zt = 22 - ((x - 16 * i) * 8) // 16
        for y in range(10, 14):
            vox[(x, y, zt)] = CI["steel_dark"]
            vox[(x, y, zt + 1)] = CI["steel_dark"]
    for x in range(x0, x0 + 4):
        zt = 22 - ((x - 16 * i) * 8) // 16
        for y in (10, 13):
            vox[(x, y, zt + 1)] = CI["steel"]

# ---- brick chimney through the east slope + cap
box(40, 44, 18, 22, H, 24, "brick")
box(40, 44, 18, 22, 24, 25, "concrete_dark")
for z in (17, 21):
    for x in range(40, 44):
        vox[(x, 18, z)] = CI["brick_dark"]
        vox[(x, 21, z)] = CI["brick_dark"]

# ---- exterior steel stair (east face, 1 proud) to roof catwalk
for i in range(14):
    box(48, 49, 2 + i, 3 + i, 0, i + 1, "steel")
    box(48, 49, 2 + i, 3 + i, i + 1, i + 4, "iron")  # handrail post
box(48, 49, 2, 24, 14, 15, "steel")      # catwalk deck (1 proud of east face)
for y in range(2, 24, 3):
    box(48, 49, y, y + 1, 15, 18, "iron")  # railing posts
box(48, 49, 2, 24, 17, 18, "iron")       # top rail

# ---- whitewash peel patches (concrete-only)
for i in range(50):
    face = rnd(i, 91, 92, 93) % 4
    w = 2 + rnd(i, 94, 95, 96) % 3
    h = 2 + rnd(i, 97, 98, 99) % 3
    if face == 0:
        x = 2 + rnd(i, 101, 102, 103) % (W - 4); z = 3 + rnd(i, 104, 105, 106) % 8
        for xx in range(x, min(x + w, W - 1)):
            for zz in range(z, min(z + h, H - 1)):
                if vox.get((xx, 0, zz)) == CI["concrete"]:
                    vox[(xx, 0, zz)] = CI["plaster_peel"]
    elif face == 1:
        x = 2 + rnd(i, 101, 102, 103) % (W - 4); z = 3 + rnd(i, 104, 105, 106) % 8
        for xx in range(x, min(x + w, W - 1)):
            for zz in range(z, min(z + h, H - 1)):
                if vox.get((xx, D - 1, zz)) == CI["concrete"]:
                    vox[(xx, D - 1, zz)] = CI["plaster_peel"]
    elif face == 2:
        y = 2 + rnd(i, 101, 102, 103) % (D - 4); z = 3 + rnd(i, 104, 105, 106) % 8
        for yy in range(y, min(y + w, D - 1)):
            for zz in range(z, min(z + h, H - 1)):
                if vox.get((0, yy, zz)) == CI["concrete"]:
                    vox[(0, yy, zz)] = CI["plaster_peel"]
    else:
        y = 2 + rnd(i, 101, 102, 103) % (D - 4); z = 3 + rnd(i, 104, 105, 106) % 8
        for yy in range(y, min(y + w, D - 1)):
            for zz in range(z, min(z + h, H - 1)):
                if vox.get((W - 1, yy, zz)) == CI["concrete"]:
                    vox[(W - 1, yy, zz)] = CI["plaster_peel"]

# ---- buried interior room z 1..7
box(14, 30, 8, 18, 0, 1, "steel_dark")
for x in range(14, 30):
    for z in range(1, 7):
        vox[(x, 8, z)] = CI["steel"]
        vox[(x, 17, z)] = CI["steel"]
for y in range(8, 18):
    for z in range(1, 7):
        vox[(14, y, z)] = CI["steel"]
        vox[(29, y, z)] = CI["steel"]
box(14, 30, 8, 18, 7, 8, "dark")
for x in range(16, 30, 4):
    for z in range(1, 7):
        vox[(x, 8, z)] = CI["steel_dark"]
        vox[(x, 17, z)] = CI["steel_dark"]

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
                   proj(x + 1, y + 1, z + 1), proj(x + 1, y, z + 1)]
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

def floater_sweep():
    pts = set(vox.keys())
    base = min(p[2] for p in pts)
    seen = set()
    bad = 0
    for p in pts:
        if p in seen:
            continue
        stack = [p]
        seen.add(p)
        touches = False
        while stack:
            q = stack.pop()
            if q[2] == base:
                touches = True
            x, y, z = q
            for r in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                      (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if r in pts and r not in seen:
                    seen.add(r)
                    stack.append(r)
        if not touches:
            bad += 1
    return bad

if __name__ == "__main__":
    write_vox("harbor-cannery-v1.vox", vox, PALETTE)
    render_preview("harbor-cannery-v1_preview.png", vox, PALETTE, scale=2)
    render_slice("harbor-cannery-v1_slice_z04.png", vox, PALETTE, 4)
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    print(f"harbor-cannery-v1: {len(vox)} voxels, "
          f"bounds {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}x{max(zs)+1}, "
          f"floating components: {floater_sweep()}")
