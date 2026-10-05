"""harbor-aduana-v1 — 1960s Havana customs warehouse.

48x36 footprint (4x3 bays), 2 stories, gable roof. Faded ochre plaster with
peel patches, three arched loading bays (center one open, doors slid aside),
blank painted sign band, rust streaks, corrugated repairs.
FACTORY_VOXEL 0.13. Hollow shell + buried interior room z 1..7.
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

W, D = 48, 36  # footprint

# ---- walls: plaster, T=2; y-faces run up to the eaves (z=22)
box(0, W, 0, 2, 0, 22, "plaster")      # front (y=0)
box(0, W, D - 2, D, 0, 22, "plaster")  # rear
box(0, 2, 0, D, 0, 22, "plaster")      # west
box(W - 2, W, 0, D, 0, 22, "plaster")  # east

# ---- concrete water table around the base
box(0, W, 0, 2, 0, 2, "concrete")
box(0, W, D - 2, D, 0, 2, "concrete")
box(0, 2, 0, D, 0, 2, "concrete")
box(W - 2, W, 0, D, 0, 2, "concrete")

# ---- three arched loading bays on the front (centers x=6,18,30)
def arch_opening(c):
    pts = set()
    for x in range(c - 4, c + 4):
        for z in range(2, 10):
            pts.add((x, z))
    for z, hw in ((10, 4), (11, 3), (12, 2), (13, 1)):
        for x in range(c - hw, c + hw):
            pts.add((x, z))
    return pts

for c in (6, 18, 30):
    op = arch_opening(c)
    for (x, z) in op:  # concrete surround (1 ring, face planes only)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                qx, qz = x + dx, z + dz
                if (qx, qz) not in op and 0 <= qx < W and 0 <= qz < 22:
                    for y in (0, 1):
                        if (qx, y, qz) in vox:
                            vox[(qx, y, qz)] = CI["concrete"]
    for (x, z) in op:  # carve through both wall planes
        vox.pop((x, 0, z), None)
        vox.pop((x, 1, z), None)

for c in (6, 30):  # closed bays: rusted sliding doors
    for (x, z) in arch_opening(c):
        col = "steel_dark"
        if x == c or z in (5, 9):
            col = "dark"                       # center seam + panel rails
        if rnd(x, z, 11) % 100 < 18:
            col = "rust"
        vox[(x, 0, z)] = CI[col]
        vox[(x, 1, z)] = CI[col]

for (x, z) in arch_opening(18):  # open bay: dark interior visible
    vox[(x, 0, z)] = CI["dark"]
    vox[(x, 1, z)] = CI["dark"]
box(10, 14, -1, 0, 2, 14, "steel_dark")  # slid-open door slabs (1 proud)
box(22, 26, -1, 0, 2, 14, "steel_dark")
box(8, 28, -1, 0, 14, 15, "steel_dark")  # slide rail above
for (x0, x1) in ((10, 14), (22, 26)):
    for x in range(x0, x1):
        for z in range(2, 14):
            if rnd(x, z, 21) % 100 < 15:
                vox[(x, -1, z)] = CI["rust"]

# ---- blank painted sign band (cream, z 14..19, letters weathered)
for x in range(W):
    for z in range(14, 20):
        if vox.get((x, 0, z)) == CI["plaster"]:
            vox[(x, 0, z)] = CI["cream"]

# (lettering removed 2026-10-04: cream band kept blank)

# ---- windows: steel_dark sash, grimy glass
def side_window(xa, y0, z0, glass_name):
    for y in range(y0, y0 + 4):
        for z in range(z0, z0 + 4):
            vox.pop((xa, y, z), None)
            vox.pop((xa + 1, y, z), None)
    for y in range(y0, y0 + 4):
        for z in range(z0, z0 + 4):
            edge = y in (y0, y0 + 3) or z in (z0, z0 + 3)
            col = "steel_dark" if edge else glass_name
            vox[(xa, y, z)] = CI[col]
            vox[(xa + 1, y, z)] = CI[col]
    box(xa, xa + 2, y0 - 1, y0 + 5, z0 - 1, z0, "concrete")  # sill
    for zz in range(z0 - 4, z0 - 1):  # rust weep under sill
        if vox.get((xa, y0 + 1, zz)) == CI["plaster"]:
            vox[(xa, y0 + 1, zz)] = CI["rust"]

def rear_window(x0, z0, glass_name):
    for x in range(x0, x0 + 4):
        for z in range(z0, z0 + 4):
            vox.pop((x, D - 2, z), None)
            vox.pop((x, D - 1, z), None)
    for x in range(x0, x0 + 4):
        for z in range(z0, z0 + 4):
            edge = x in (x0, x0 + 3) or z in (z0, z0 + 3)
            col = "steel_dark" if edge else glass_name
            vox[(x, D - 2, z)] = CI[col]
            vox[(x, D - 1, z)] = CI[col]
    box(x0 - 1, x0 + 5, D - 2, D, z0 - 1, z0, "concrete")
    for zz in range(z0 - 4, z0 - 1):
        if vox.get((x0 + 1, D - 1, zz)) == CI["plaster"]:
            vox[(x0 + 1, D - 1, zz)] = CI["rust"]

side_window(0, 7, 12, "glass")
side_window(0, 25, 12, "glass_dark")
side_window(W - 2, 7, 12, "glass_dark")
side_window(W - 2, 25, 12, "glass")
rear_window(6, 12, "glass")
rear_window(38, 12, "glass_dark")

# ---- personnel door on the rear
for x in range(22, 26):
    for z in range(0, 12):
        vox.pop((x, D - 2, z), None)
        vox.pop((x, D - 1, z), None)
        vox[(x, D - 2, z)] = CI["dark"]
        vox[(x, D - 1, z)] = CI["dark"]
box(21, 27, D - 2, D, 12, 13, "concrete")  # lintel
for z in range(0, 12):
    for x in (21, 26):
        if vox.get((x, D - 1, z)) == CI["plaster"]:
            vox[(x, D - 1, z)] = CI["concrete"]

# ---- corrugated patch repairs (steel_dark 3x4)
box(0, 1, 14, 17, 4, 8, "steel_dark")
box(0, 1, 20, 23, 10, 14, "steel_dark")
box(W - 1, W, 8, 11, 5, 9, "steel_dark")
box(12, 15, D - 1, D, 4, 8, "steel_dark")

# ---- plaster peel patches (blobs, denser near grade, plaster-only)
for i in range(70):
    face = rnd(i, 1, 2, 41) % 4
    w = 2 + rnd(i, 7, 8, 44) % 3
    h = 2 + rnd(i, 9, 10, 45) % 3
    if face == 0:
        x = 3 + rnd(i, 3, 4, 42) % (W - 6); z = 1 + rnd(i, 5, 6, 43) % 12
        for xx in range(x, min(x + w, W - 1)):
            for zz in range(z, min(z + h, 21)):
                if vox.get((xx, 0, zz)) == CI["plaster"]:
                    vox[(xx, 0, zz)] = CI["plaster_peel"]
    elif face == 1:
        x = 3 + rnd(i, 3, 4, 42) % (W - 6); z = 1 + rnd(i, 5, 6, 43) % 12
        for xx in range(x, min(x + w, W - 1)):
            for zz in range(z, min(z + h, 21)):
                if vox.get((xx, D - 1, zz)) == CI["plaster"]:
                    vox[(xx, D - 1, zz)] = CI["plaster_peel"]
    elif face == 2:
        y = 3 + rnd(i, 3, 4, 42) % (D - 6); z = 1 + rnd(i, 5, 6, 43) % 12
        for yy in range(y, min(y + w, D - 1)):
            for zz in range(z, min(z + h, 21)):
                if vox.get((0, yy, zz)) == CI["plaster"]:
                    vox[(0, yy, zz)] = CI["plaster_peel"]
    else:
        y = 3 + rnd(i, 3, 4, 42) % (D - 6); z = 1 + rnd(i, 5, 6, 43) % 12
        for yy in range(y, min(y + w, D - 1)):
            for zz in range(z, min(z + h, 21)):
                if vox.get((W - 1, yy, zz)) == CI["plaster"]:
                    vox[(W - 1, yy, zz)] = CI["plaster_peel"]

# ---- rust streaks under the eave lines (plaster-only)
for i in range(16):
    face = rnd(i, 21, 22, 51) % 4
    length = 3 + rnd(i, 25, 26, 53) % 4
    if face == 0:
        x = 2 + rnd(i, 23, 24, 52) % (W - 4)
        for zz in range(22 - length, 22):
            if vox.get((x, 0, zz)) == CI["plaster"]:
                vox[(x, 0, zz)] = CI["rust"]
    elif face == 1:
        x = 2 + rnd(i, 23, 24, 52) % (W - 4)
        for zz in range(22 - length, 22):
            if vox.get((x, D - 1, zz)) == CI["plaster"]:
                vox[(x, D - 1, zz)] = CI["rust"]
    elif face == 2:
        y = 2 + rnd(i, 23, 24, 52) % (D - 4)
        for zz in range(22 - length, 22):
            if vox.get((0, y, zz)) == CI["plaster"]:
                vox[(0, y, zz)] = CI["rust"]
    else:
        y = 2 + rnd(i, 23, 24, 52) % (D - 4)
        for zz in range(22 - length, 22):
            if vox.get((W - 1, y, zz)) == CI["plaster"]:
                vox[(W - 1, y, zz)] = CI["rust"]

# ---- gable roof: eaves z=22 at y=0/36(+1 overhang), ridge z=30 at y=18
def ztop(y):
    return 30 - round(abs(18 - y) * 8 / 18)

for x in range(W):
    for y in range(0, D + 1):
        zt = ztop(y)
        vox[(x, y, zt)] = CI["roof_grey"]
        vox[(x, y, zt - 1)] = CI["roof_grey"]
for x in (0, 1, W - 2, W - 1):  # gable triangles on the x faces
    for y in range(0, D + 1):
        zt = ztop(y)
        for z in range(22, zt):
            if (x, y, z) not in vox:
                vox[(x, y, z)] = CI["plaster"]
box(0, W, 17, 19, 31, 32, "concrete_dark")  # ridge roll

# ---- buried interior room z 1..7 (floor strips on grade, walls, ceiling)
box(14, 30, 12, 24, 0, 1, "steel_dark")
for x in range(14, 30):
    for z in range(1, 7):
        vox[(x, 12, z)] = CI["steel"]
        vox[(x, 23, z)] = CI["steel"]
for y in range(12, 24):
    for z in range(1, 7):
        vox[(14, y, z)] = CI["steel"]
        vox[(29, y, z)] = CI["steel"]
box(14, 30, 12, 24, 7, 8, "dark")
for x in range(16, 30, 4):  # panel seams
    for z in range(1, 7):
        vox[(x, 12, z)] = CI["steel_dark"]
        vox[(x, 23, z)] = CI["steel_dark"]

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
    write_vox("harbor-aduana-v1.vox", vox, PALETTE)
    render_preview("harbor-aduana-v1_preview.png", vox, PALETTE, scale=2)
    render_slice("harbor-aduana-v1_slice_z04.png", vox, PALETTE, 4)
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    print(f"harbor-aduana-v1: {len(vox)} voxels, "
          f"bounds {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}x{max(zs)+1}, "
          f"floating components: {floater_sweep()}")
