#!/usr/bin/env python3
"""Strike Bay factory kit — STEEL WATER TOWER (water_tower_v1).

Small-town riveted-steel water tower in the Cotter style: cylindrical
riveted tank with ellipsoidal dish bottom and rusty conical roof, faded
COTTER lettering on the camera face, circular balcony with railing at the
tank base, central riser pipe, four splayed legs with horizontal struts
and rod X-bracing on concrete footings, and access ladders from grade to
balcony to roof eave. Scaled to the factory kit (tank 24 dia, 84 tall).

Generates water_tower_v1.vox + preview/slice renders.
"""
import math
import random
random.seed(11)

PALETTE = [  # (name, rgb); color index = position + 1
    ("concrete",     (170, 166, 158)),  # 1  footings
    ("concrete_dark",(112, 108, 100)),  # 2  footing variation
    ("steel",        (122, 126, 134)),  # 3  railing
    ("steel_dark",   ( 62,  64,  72)),  # 4  bracing rods, ladders
    ("galv",         (172, 176, 182)),  # 5  tank wall, legs (weathered galvanized)
    ("galv_dark",    (138, 142, 148)),  # 6  course bands, seams, struts, ring girder
    ("rust",         (150,  96,  62)),  # 7  rust streaks and patches
    ("rust_dark",    (110,  68,  46)),  # 8  riser, heavy rust
    ("roof",         (140,  82,  60)),  # 9  conical roof (oxidized)
    ("dark",         ( 32,  34,  40)),  # 10 boilerplate
    ("letter",       (218, 216, 208)),  # 11 faded COTTER lettering
    ("white",        (235, 235, 230)),  # 12 boilerplate
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

vox = {}  # (x, y, z) -> color index (1-based)

TR = 12                    # tank radius
WALL_Z0, WALL_Z1 = 52, 72  # tank wall band
LEG_TOP_Z = 50

def leg_p(z):
    """Leg center offset at height z (splays 13 at grade -> 9 at the ring)."""
    return 13 - 4 * z / LEG_TOP_Z

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

def line(x0, y0, z0, x1, y1, z1, c):
    """1-voxel rod between two points."""
    ci = CI[c]
    n = int(max(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0), 1))
    for i in range(n + 1):
        t = i / n
        vox[(round(x0 + (x1 - x0) * t),
             round(y0 + (y1 - y0) * t),
             round(z0 + (z1 - z0) * t))] = ci

# ---------------------------------------------------------------- four splayed legs
for sx in (-1, 1):
    for sy in (-1, 1):
        for z in range(0, LEG_TOP_Z + 1):
            p = leg_p(z)
            cx, cy = round(sx * p), round(sy * p)
            for ox in (-1, 0):
                for oy in (-1, 0):
                    vox[(cx + ox, cy + oy, z)] = CI["galv"]

# ---------------------------------------------------------------- concrete footings
for sx in (-1, 1):
    for sy in (-1, 1):
        box(sx * 13 - 2, sx * 13 + 3, sy * 13 - 2, sy * 13 + 3, 0, 3, "concrete")

# ---------------------------------------------------------------- horizontal struts
for zl in (14, 28, 42):
    p = round(leg_p(zl))
    for s in (-1, 1):
        for x in range(-p, p + 1):                       # +/-y faces
            for z in (zl, zl + 1):
                vox[(x, s * p - 1, z)] = CI["galv_dark"]
                vox[(x, s * p, z)] = CI["galv_dark"]
        for y in range(-p, p + 1):                       # +/-x faces
            for z in (zl, zl + 1):
                vox[(s * p - 1, y, z)] = CI["galv_dark"]
                vox[(s * p, y, z)] = CI["galv_dark"]

# ---------------------------------------------------------------- rod X-bracing per face panel
for (za, zb) in ((2, 14), (14, 28), (28, 42), (42, 50)):
    pa, pb = leg_p(za), leg_p(zb)
    for s in (-1, 1):
        line(-pa, s * pa, za, pb, s * pb, zb, "steel_dark")
        line(pa, s * pa, za, -pb, s * pb, zb, "steel_dark")
        line(s * pa, -pa, za, s * pb, pb, zb, "steel_dark")
        line(s * pa, pa, za, s * pb, -pb, zb, "steel_dark")

# ---------------------------------------------------------------- base ring girder the legs bolt to
for dx in range(-14, 15):
    for dy in range(-14, 15):
        d2 = dx * dx + dy * dy
        if 121 <= d2 <= 196:                              # r 11..14
            for z in range(50, 53):
                vox[(dx, dy, z)] = CI["galv_dark"]

# ---------------------------------------------------------------- ellipsoidal dish bottom (shell)
for dx in range(-TR, TR + 1):
    for dy in range(-TR, TR + 1):
        r2 = dx * dx + dy * dy
        if r2 <= TR * TR:
            r = math.sqrt(r2)
            zb = 52 - round(8 * (1 - (r / TR) ** 2))
            for z in (zb - 1, zb, zb + 1):
                vox[(dx, dy, z)] = CI["galv"]

# ---------------------------------------------------------------- central riser pipe (through the dish)
cyl(0, 0, 2, 0, 49, "rust_dark")

# ---------------------------------------------------------------- tank wall
for dx in range(-13, 14):
    for dy in range(-13, 14):
        d2 = dx * dx + dy * dy
        if 132 <= d2 <= 156:                              # r 11.5..12.5
            for z in range(WALL_Z0, WALL_Z1):
                vox[(dx, dy, z)] = CI["galv"]

# ---------------------------------------------------------------- course bands (proud), seams, rivets
for z in (57, 62, 67):
    for dx in range(-13, 14):
        for dy in range(-13, 14):
            d2 = dx * dx + dy * dy
            if 144 <= d2 <= 172:                          # r 12..13.1
                vox[(dx, dy, z)] = CI["galv_dark"]
for a in range(12):                                       # vertical seams
    th = a * math.pi / 6
    for z in range(WALL_Z0, WALL_Z1):
        x = round(TR * math.cos(th)); y = round(TR * math.sin(th))
        if vox.get((x, y, z)) == CI["galv"]:
            vox[(x, y, z)] = CI["galv_dark"]
for z in (57, 62, 67):                                    # rivet dots on bands
    for k in range(30):
        th = k * 2 * math.pi / 30
        x = round(12.6 * math.cos(th)); y = round(12.6 * math.sin(th))
        if vox.get((x, y, z)) == CI["galv_dark"]:
            vox[(x, y, z)] = CI["steel_dark"]

# ---------------------------------------------------------------- faded COTTER lettering (camera face, +x/+y diagonal)
FONT = {
    "C": [".XX", "X..", "X..", "X..", ".XX"],
    "O": [".XX", "X.X", "X.X", "X.X", ".XX"],
    "T": ["XXX", ".X.", ".X.", ".X.", ".X."],
    "E": ["XXX", "X..", "XX.", "X..", "XXX"],
    "R": ["XX.", "X.X", "XX.", "X.X", "X.X"],
}
ac = math.pi / 4
for i, ch in enumerate("COTTER"):
    glyph = FONT[ch]
    ai = ac + (i - 2.5) * 0.3
    for px in range(3):
        a = ai + (px - 1) * (1.0 / TR)
        x = round(TR * math.cos(a)); y = round(TR * math.sin(a))
        for pz, row in enumerate(glyph):
            if row[px] == "X" and random.random() > 0.15:  # weather-faded
                z = 64 - pz
                for ox, oy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    if vox.get((x + ox, y + oy, z)) in (CI["galv"], CI["galv_dark"]):
                        vox[(x + ox, y + oy, z)] = CI["letter"]
                        break

# ---------------------------------------------------------------- rust streaks bleeding down from the balcony
for _ in range(28):
    th = random.random() * 2 * math.pi
    x = round(TR * math.cos(th)); y = round(TR * math.sin(th))
    for dz in range(random.randint(3, 6)):
        if vox.get((x, y, 51 - dz)) == CI["galv"]:
            vox[(x, y, 51 - dz)] = CI["rust"]

# ---------------------------------------------------------------- balcony: floor, brackets, railing
for dx in range(-16, 17):
    for dy in range(-16, 17):
        d2 = dx * dx + dy * dy
        if 169 <= d2 <= 256:                              # r 13..16
            for z in (52, 53):
                vox[(dx, dy, z)] = CI["steel_dark"]
for k in range(12):                                       # support brackets
    th = k * math.pi / 6
    line(round(11 * math.cos(th)), round(11 * math.sin(th)), 47,
         round(15 * math.cos(th)), round(15 * math.sin(th)), 52, "steel_dark")
# ---------------------------------------------------------------- eave fascia + conical roof + finial
for dx in range(-14, 15):
    for dy in range(-14, 15):
        d2 = dx * dx + dy * dy
        if 144 <= d2 <= 196:                              # r 12..14
            for z in (71, 72):
                vox[(dx, dy, z)] = CI["galv_dark"]
for z in range(72, 81):
    r = 13 * (80 - z) / 8
    for dx in range(-14, 15):
        for dy in range(-14, 15):
            d = math.sqrt(dx * dx + dy * dy)
            if z >= 78:
                if d <= r + 0.5:
                    vox[(dx, dy, z)] = CI["roof"]
            elif r - 2 < d <= r:
                vox[(dx, dy, z)] = CI["roof"]
cyl(0, 0, 1, 80, 84, "steel_dark")                        # finial rod
for dx in range(-2, 3):
    for dy in range(-2, 3):
        if dx * dx + dy * dy <= 4:                        # finial ball
            for z in (83, 84):
                vox[(dx, dy, z)] = CI["steel_dark"]

# ---------------------------------------------------------------- face ladder (+y), hugging the leg splay
for z in range(0, 53):
    yr = round(leg_p(z)) + 1
    vox[(-1, yr, z)] = CI["steel_dark"]
    vox[(1, yr, z)] = CI["steel_dark"]
    if z % 3 == 0:
        vox[(0, yr, z)] = CI["steel_dark"]
box(-2, 3, 10, 15, 52, 54, "steel_dark")                  # landing to the balcony

# ---------------------------------------------------------------- tank ladder: balcony to eave
for z in range(54, 73):
    vox[(-1, 13, z)] = CI["steel_dark"]
    vox[(1, 13, z)] = CI["steel_dark"]
    if z % 3 == 0:
        vox[(0, 13, z)] = CI["steel_dark"]

# ---------------------------------------------------------------- weathering
for (x, y, z), ci in list(vox.items()):
    r = random.random()
    if ci == CI["galv"] and r < 0.06:
        vox[(x, y, z)] = CI["rust"]
    elif ci == CI["galv_dark"] and r < 0.05:
        vox[(x, y, z)] = CI["rust"]
    elif ci == CI["roof"] and r < 0.08:
        vox[(x, y, z)] = CI["rust_dark"]
    elif ci == CI["rust_dark"] and r < 0.05:
        vox[(x, y, z)] = CI["rust"]
    elif ci == CI["concrete"] and r < 0.04:
        vox[(x, y, z)] = CI["concrete_dark"]


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
    write_vox(os.path.join(here, "water_tower_v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "water_tower_v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "water_tower_v1_slice_z25.png"), vox, PALETTE, 25)
    render_slice(os.path.join(here, "water_tower_v1_slice_z62.png"), vox, PALETTE, 62)
