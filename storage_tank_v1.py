#!/usr/bin/env python3
"""Strike Bay factory kit — LARGE AGED INDUSTRIAL STORAGE TANK (storage_tank_v1).

Placeable tank-farm module in the kit's mid-century industrial language:
tall olive-drab riveted steel shell with course bands, domed roof carrying
pipe stubs with valve caps and a pipe frame, bolted manhole hatch and small
ports on the shell, caged access ladder, discharge piping with a red valve
wheel, a ground pipe run on posts, and heavy aging — rust streaks, chipped
paint, grime at the base. Separate kit module — other generators untouched.

Generates storage_tank_v1.vox + preview/slice renders.
"""
import math
import random
random.seed(7)

PALETTE = [  # (name, rgb); color index = position + 1
    ("concrete",     (170, 166, 158)),  # 1  pipe supports, posts
    ("concrete_dark",(112, 108, 100)),  # 2  ring footing
    ("shell",        (112, 116,  90)),  # 3  aged olive-drab tank steel
    ("shell_dark",   ( 92,  96,  72)),  # 4  course bands, seams, roof
    ("shell_darker", ( 74,  78,  58)),  # 5  hatch plate, shadowed steel
    ("grime",        ( 58,  58,  48)),  # 6  base grime band
    ("rust",         (122,  72,  44)),  # 7  rust streaks / patches
    ("rust_dark",    ( 92,  54,  34)),  # 8  deep rust
    ("steel_dark",   ( 62,  64,  72)),  # 9  pipes, ladder, railing
    ("white",        (235, 235, 230)),  # 10 boilerplate
    ("window",       ( 18,  26,  38)),  # 11 boilerplate
    ("dark",         ( 32,  34,  40)),  # 12 void floor
    ("red",          (150,  52,  40)),  # 13 valve wheel, port caps
    ("blue",         ( 52,  90, 150)),  # 14 valve caps
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

vox = {}  # (x, y, z) -> color index (1-based)

CX, CY = 24, 0          # tank center; footprint x 0..48, y -18..18
R = 11                 # shell radius

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

def disc(cx, cy, r, z, c):
    """One-voxel-thick horizontal disc."""
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for y in range(cy - r, cy + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                vox[(x, y, z)] = ci

# ---------------------------------------------------------------- ring footing + shell
cyl(CX, CY, R + 1, 0, 2, "concrete_dark")     # low ring footing, part of the tank
cyl(CX, CY, R, 2, 38, "shell")
for (x, y, z), ci in list(vox.items()):        # course bands: full wall rings
    # (interior is hollowed later, so d2 > 81 selects the whole 2-thick wall;
    # a d2 >= R*R-2 test only catches ~4 voxels per layer and paints dashes)
    if ci == CI["shell"] and z in (8, 14, 20, 26, 32):
        if (x - CX) ** 2 + (y - CY) ** 2 > 9 * 9:
            vox[(x, y, z)] = CI["shell_dark"]
for a in range(10):                            # vertical plate seams
    th = a * math.pi / 5 + 0.1
    for z in range(2, 38):
        x = CX + round((R - 0.4) * math.cos(th)); y = CY + round((R - 0.4) * math.sin(th))
        if vox.get((x, y, z)) == CI["shell"]:
            vox[(x, y, z)] = CI["shell_dark"]

# ---------------------------------------------------------------- hollow interior (dark void for damage reveals)
for dx in range(-9, 10):
    for dy in range(-9, 10):
        if dx * dx + dy * dy <= 9 * 9:
            for z in range(3, 36):
                vox.pop((CX + dx, CY + dy, z), None)
            vox[(CX + dx, CY + dy, 2)] = CI["dark"]

# ---------------------------------------------------------------- domed roof
cyl(CX, CY, R, 38, 39, "shell_dark")
cyl(CX, CY, 9, 39, 40, "shell_dark")
cyl(CX, CY, 6, 40, 41, "shell_dark")
cyl(CX, CY, 3, 41, 42, "shell_dark")
for dx in range(-R - 1, R + 2):                # roof-edge gutter rim
    for dy in range(-R - 1, R + 2):
        d2 = dx * dx + dy * dy
        if R * R <= d2 <= (R + 1.5) ** 2:
            vox[(CX + dx, CY + dy, 38)] = CI["shell_darker"]

# ---------------------------------------------------------------- roof fittings
cyl(CX, CY, 1, 42, 44, "steel_dark")          # central vent stub
disc(CX, CY, 2, 44, "dark")                   # vent cap
for sx, sy in ((-4, 3), (4, 3)):              # pipe stubs with valve caps
    cyl(CX + sx, CY + sy, 1, 41, 45, "steel_dark")
    disc(CX + sx, CY + sy, 1, 45, "blue")
py = CY - 5                                    # roof pipe frame (like the photo)
box(CX - 6, CX + 7, py, py + 1, 44, 46, "steel_dark")
for px in (CX - 6, CX, CX + 6):
    box(px, px + 1, py, py + 1, 41, 44, "steel_dark")

# ---------------------------------------------------------------- caged access ladder (camera-facing, +x side)
LX = CX + R + 2
box(LX, LX + 1, -1, 0, 2, 42, "steel_dark")
box(LX, LX + 1, 1, 2, 2, 42, "steel_dark")
for z in range(6, 42, 8):                         # standoff brackets tying the rails to the shell
    box(LX - 3, LX + 1, -1, 0, z, z + 1, "steel_dark")
    box(LX - 3, LX + 1, 1, 2, z, z + 1, "steel_dark")
for z in range(3, 40, 2):
    box(LX, LX + 1, -1, 2, z, z + 1, "steel_dark")
for z in range(8, 40, 4):
    for dx in range(0, 3):
        for dy in range(-2, 3):
            d2 = dx * dx + dy * dy
            if 2 <= d2 <= 6:                      # d2=2 bridges the hoop tips to the rails
                vox[(LX + dx, dy, z)] = CI["steel_dark"]

# ---------------------------------------------------------------- bolted manhole hatch (camera-facing)
MZ, MR = 7, 3
for dy in range(-MR, MR + 1):
    for dz in range(-MR, MR + 1):
        if dy * dy + dz * dz <= MR * MR:
            vox[(CX + R, dy, MZ + dz)] = CI["shell_darker"]
for k in range(12):                           # bolt ring
    th = k * 2 * math.pi / 12
    by = round((MR + 1) * math.cos(th)); bz = round((MR + 1) * math.sin(th))
    vox[(CX + R, by, MZ + bz)] = CI["steel_dark"]
box(CX + R - 2, CX + R + 2, 5, 8, 6, 8, "white")   # stencil tag plate, sunk into the shell
for (x, y, z), ci in list(vox.items()):
    if ci == CI["white"] and random.random() < 0.4:
        vox[(x, y, z)] = CI["shell_dark"]

# ---------------------------------------------------------------- small base ports (camera-facing)
box(CX + R - 2, CX + R + 1, -7, -5, 2, 4, "red")    # base ports, sunk into the shell
box(CX + R - 2, CX + R + 1, 5, 7, 2, 4, "blue")

# ---------------------------------------------------------------- discharge piping with valve wheel (camera-facing)
box(CX + R, CX + R + 8, -1, 1, 2, 4, "steel_dark")
box(CX + R + 3, CX + R + 5, -1, 1, 1, 2, "concrete")    # pipe support
for fx in (CX + R + 2, CX + R + 6):                    # flange rings
    for dy in range(-1, 2):
        for dz in range(2, 5):
            if abs(dy) + abs(dz - 3) == 2:
                vox[(fx, dy, dz)] = CI["shell_darker"]
for dx in range(-2, 3):                               # red valve wheel
    for dy in range(-2, 3):
        if 3 <= dx * dx + dy * dy <= 5:
            vox[(CX + R + 7 + dx, dy, 5)] = CI["red"]
for s in range(-2, 3):                                # wheel spokes → hub sits on the stem
    vox[(CX + R + 7 + s, 0, 5)] = CI["red"]
    vox[(CX + R + 7, s, 5)] = CI["red"]
box(CX + R + 7, CX + R + 8, -1, 2, 4, 5, "steel_dark")

# ---------------------------------------------------------------- ground pipe run on posts (foreground, like the photo)
GY = CY + 14
box(CX - 6, CX + 14, GY, GY + 1, 1, 3, "steel_dark")
for px in (CX - 4, CX + 2, CX + 8, CX + 12):
    box(px, px + 1, GY, GY + 1, 0, 1, "concrete")

# ---------------------------------------------------------------- aging: rust streaks, chips, grime
def streak(x, y, z0, z1):
    for z in range(z0, z1):
        if random.random() < 0.7 and (x, y, z) in vox:
            vox[(x, y, z)] = CI["rust_dark"] if random.random() < 0.4 else CI["rust"]

for a in range(10):                                   # streaks below seams / roof rim
    th = a * math.pi / 5 + 0.1
    x = CX + round((R - 0.4) * math.cos(th)); y = CY + round((R - 0.4) * math.sin(th))
    streak(x, y, 30, 37)
for dy in (-MR - 1, MR + 1):                          # streaks under the manhole
    streak(CX + R, dy, 2, MZ - MR)
streak(CX + R, 0, 2, 6)                               # streak under discharge
for (x, y, z), ci in list(vox.items()):               # chipped paint / grime
    shell = (ci == CI["shell"] or ci == CI["shell_dark"])
    if shell:
        if z < 6 and random.random() < 0.18:
            vox[(x, y, z)] = CI["grime"]
        elif random.random() < 0.07:
            vox[(x, y, z)] = CI["rust"]
        elif random.random() < 0.03:
            vox[(x, y, z)] = CI["shell_darker"]


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
    write_vox(os.path.join(here, "storage_tank_v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "storage_tank_v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "storage_tank_v1_slice_z20.png"), vox, PALETTE, 20)
    render_slice(os.path.join(here, "storage_tank_v1_slice_z41.png"), vox, PALETTE, 41)
