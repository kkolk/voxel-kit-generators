#!/usr/bin/env python3
"""Strike Bay factory kit — STEEL SMOKESTACK (smokestack_steel_v1).

Variant of smokestack_v1: straighter steel stack in the buildings' light
grey, with visible plate-course seams, the same red/white aviation bands (caged access ladder removed 2026-09-28). No base — the shaft rises straight
from the ground to compose against other kit buildings.
Separate kit module — other kit files untouched.

Generates smokestack_steel_v1.vox + preview/slice renders.
"""

PALETTE = [  # (name, rgb); color index = position + 1
    ("concrete",     (170, 166, 158)),  # 1  base block + steel shaft
    ("concrete_dark",(112, 108, 100)),  # 2  footing, cap, plate seams
    ("coping",       (202, 198, 190)),  # 3  boilerplate
    ("brick",        (150,  90,  66)),  # 4  boilerplate
    ("brick_dark",   (120,  68,  50)),  # 5  boilerplate
    ("glass",        ( 72,  98, 118)),  # 6  boilerplate
    ("glass_dark",   ( 44,  62,  78)),  # 7  boilerplate
    ("steel",        (122, 126, 134)),  # 8  boilerplate
    ("steel_dark",   ( 62,  64,  72)),  # 9  door frame, ladder, rod
    ("white",        (235, 235, 230)),  # 10 boilerplate
    ("window",       ( 18,  26,  38)),  # 11 boilerplate
    ("dark",         ( 32,  34,  40)),  # 12 door leaf, flue opening
    ("green",        (100, 118,  94)),  # 13 boilerplate
    ("green_dark",   ( 70,  88,  68)),  # 14 boilerplate
    ("roof",         (100, 104, 100)),  # 15 boilerplate
    ("band_red",     (158,  62,  52)),  # 16 stack bands
    ("band_white",   (224, 220, 212)),  # 17 stack bands
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

vox = {}  # (x, y, z) -> color index (1-based)

CX, CY = 15, 0          # stack center; footprint x 10..24, y -5..5
Z0, Z1 = 0, 71          # shaft z range (exclusive top)
R0, R1 = 5.0, 4.5       # nearly straight steel shaft

def box(x0, x1, y0, y1, z0, z1, c):
    """Inclusive-exclusive box fill."""
    ci = CI[c]
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                vox[(x, y, z)] = ci

def disc(cx, cy, r, z, c):
    """Filled 1-tall disc."""
    ci = CI[c]
    ri = int(r + 0.5)
    for dx in range(-ri, ri + 1):
        for dy in range(-ri, ri + 1):
            if dx * dx + dy * dy <= r * r:
                vox[(cx + dx, cy + dy, z)] = ci

def radius_at(z):
    return R0 - (z - Z0) * (R0 - R1) / (Z1 - Z0)

# ---------------------------------------------------------------- steel shaft
BANDS = {61: "band_red", 62: "band_red",
         63: "band_white", 64: "band_white",
         65: "band_red", 66: "band_red"}
SEAMS = set(range(5, 61, 8))                 # plate-course seams
for z in range(Z0, Z1):
    c = BANDS.get(z, "concrete_dark" if z in SEAMS else "concrete")
    disc(CX, CY, radius_at(z), z, c)

# ---------------------------------------------------------------- top rim + flue opening + lightning rod
r = radius_at(Z1 - 1)
for dx in range(-6, 7):
    for dy in range(-6, 7):
        d2 = dx * dx + dy * dy
        if d2 <= r * r:
            vox[(CX + dx, CY + dy, Z1)] = (CI["concrete_dark"] if d2 >= (r - 1.2) ** 2
                                           else CI["dark"])
box(19, 20, 0, 1, Z1 - 2, Z1 + 4, "steel_dark")   # lightning rod on the rim


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
    write_vox(os.path.join(here, "smokestack_steel_v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "smokestack_steel_v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "smokestack_steel_v1_slice_z10.png"), vox, PALETTE, 10)
    render_slice(os.path.join(here, "smokestack_steel_v1_slice_z40.png"), vox, PALETTE, 40)
