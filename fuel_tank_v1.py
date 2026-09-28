#!/usr/bin/env python3
"""Strike Bay factory kit — LARGE FUEL STORAGE TANK (fuel_tank_v1).

Placeable tank-farm module in the kit's mid-century industrial language:
light sage-green riveted steel shell with course bands, shallow conical
roof, vertical access ladder with safety hoops, roof-edge railing, and a
pipe manifold with valve wheel. The tank sits straight on the ground —
no pad, no berm. Separate kit module — factory_*.py / warehouse_v1.py untouched.

Generates fuel_tank_v1.vox + preview/slice renders.
"""
import math
import random
random.seed(42)

PALETTE = [  # (name, rgb); color index = position + 1
    ("concrete",     (170, 166, 158)),  # 1  pad, pipe supports
    ("concrete_dark",(112, 108, 100)),  # 2  containment berm, foundation ring
    ("coping",       (202, 198, 190)),  # 3  boilerplate
    ("brick",        (150,  90,  66)),  # 4  boilerplate
    ("brick_dark",   (120,  68,  50)),  # 5  boilerplate
    ("glass",        ( 72,  98, 118)),  # 6  boilerplate
    ("glass_dark",   ( 44,  62,  78)),  # 7  boilerplate
    ("steel",        (122, 126, 134)),  # 8  boilerplate
    ("steel_dark",   ( 62,  64,  72)),  # 9  stairs, pipes, railings, vent
    ("white",        (235, 235, 230)),  # 10 boilerplate
    ("window",       ( 18,  26,  38)),  # 11 boilerplate
    ("dark",         ( 32,  34,  40)),  # 12 tank void floor, valve wheel, vent cap
    ("green",        (100, 118,  94)),  # 13 boilerplate
    ("green_dark",   ( 70,  88,  68)),  # 14 boilerplate
    ("roof",         (100, 104, 100)),  # 15 boilerplate
    ("tank_shell",   (168, 176, 164)),  # 16 pale sage-green tank steel
    ("tank_dark",    (138, 146, 134)),  # 17 course bands, roof
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

vox = {}  # (x, y, z) -> color index (1-based)

CX, CY = 21, 0          # tank center; footprint x 0..42, y -21..21
R = 16                 # shell radius

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

# (no pad or berm — the tank sits straight on the ground)

# ---------------------------------------------------------------- shell
cyl(CX, CY, R, 0, 18, "tank_shell")
for dx in range(-R, R + 1):                             # foundation ring
    for dy in range(-R, R + 1):
        d2 = dx * dx + dy * dy
        if 15 * 15 <= d2 <= 17 * 17:
            vox[(CX + dx, CY + dy, 0)] = CI["concrete_dark"]
for (x, y, z), ci in list(vox.items()):                 # course bands
    if ci == CI["tank_shell"] and z in (3, 7, 11, 15):
        if (x - CX) ** 2 + (y - CY) ** 2 >= 240:
            vox[(x, y, z)] = CI["tank_dark"]
for a in range(8):                                      # vertical seams
    th = a * math.pi / 4
    for z in range(0, 18):
        x = CX + round(15.7 * math.cos(th)); y = CY + round(15.7 * math.sin(th))
        if vox.get((x, y, z)) == CI["tank_shell"]:
            vox[(x, y, z)] = CI["tank_dark"]

# ---------------------------------------------------------------- hollow interior (dark void for damage reveals)
for dx in range(-14, 15):
    for dy in range(-14, 15):
        if dx * dx + dy * dy <= 14 * 14:
            for z in range(1, 16):
                vox.pop((CX + dx, CY + dy, z), None)
            vox[(CX + dx, CY + dy, 0)] = CI["dark"]

# ---------------------------------------------------------------- shallow conical roof
cyl(CX, CY, 15, 18, 19, "tank_dark")
cyl(CX, CY, 12, 19, 20, "tank_dark")
cyl(CX, CY, 8, 20, 21, "tank_dark")
cyl(CX, CY, 4, 21, 22, "tank_dark")
for dx in range(-17, 18):                               # roof-edge gutter rim
    for dy in range(-17, 18):
        d2 = dx * dx + dy * dy
        if 240 <= d2 <= 272:
            vox[(CX + dx, CY + dy, 18)] = CI["steel_dark"]
cyl(CX, CY, 2, 22, 24, "steel_dark")                    # roof vent
for dx in range(-3, 4):
    for dy in range(-3, 4):
        if dx * dx + dy * dy <= 8:
            vox[(CX + dx, CY + dy, 24)] = CI["dark"]

# ---------------------------------------------------------------- vertical access ladder with safety hoops
LX = CX + R + 2                                            # ladder x, proud of the shell
box(LX, LX + 1, -1, 0, 0, 20, "steel_dark")                # rails (extend past roof edge)
box(LX, LX + 1, 1, 2, 0, 20, "steel_dark")
for z in range(1, 18, 2):                                  # rungs
    box(LX, LX + 1, -1, 2, z, z + 1, "steel_dark")
for z in range(4, 18, 4):                                  # safety hoops
    for dx in range(0, 3):
        for dy in range(-2, 3):
            d2 = dx * dx + dy * dy
            if 3 <= d2 <= 6:
                vox[(LX + dx, dy, z)] = CI["steel_dark"]

# ---------------------------------------------------------------- roof-edge railing
for k in range(30):
    if k == 0:                                             # gap at the ladder
        continue
    th = k * 2 * math.pi / 30
    xi = CX + round(15 * math.cos(th)); yi = CY + round(15 * math.sin(th))
    box(xi, xi + 1, yi, yi + 1, 18, 21, "steel_dark")
for dx in range(-16, 17):
    for dy in range(-16, 17):
        d2 = dx * dx + dy * dy
        if 210 <= d2 <= 240:
            if abs(dx - 15) < 2 and abs(dy) < 3:            # rail gap at ladder
                continue
            vox[(CX + dx, CY + dy, 21)] = CI["steel_dark"]

# ---------------------------------------------------------------- pipe manifold with valve wheel
cyl(33, 12, 1, 0, 6, "steel_dark")                       # pipe A
box(28, 34, 11, 13, 4, 6, "steel_dark")                  # A into the shell
box(30, 32, 11, 13, 0, 4, "concrete")                    # A support
cyl(34, 13, 1, 0, 8, "steel_dark")                       # pipe B
box(28, 35, 12, 14, 6, 8, "steel_dark")                  # B into the shell
for dx in range(-2, 3):                                  # valve wheel on B
    for dy in range(-2, 3):
        if 3 <= dx * dx + dy * dy <= 5:
            vox[(34 + dx, 13 + dy, 9)] = CI["dark"]

# ---------------------------------------------------------------- subtle weathering
for (x, y, z), ci in list(vox.items()):
    if ci == CI["tank_shell"] and random.random() < 0.05:
        vox[(x, y, z)] = CI["tank_dark"]
    elif ci == CI["tank_dark"] and z < 18 and random.random() < 0.03:
        vox[(x, y, z)] = CI["tank_shell"]


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
    write_vox(os.path.join(here, "fuel_tank_v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "fuel_tank_v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "fuel_tank_v1_slice_z8.png"), vox, PALETTE, 8)
    render_slice(os.path.join(here, "fuel_tank_v1_slice_z19.png"), vox, PALETTE, 19)
