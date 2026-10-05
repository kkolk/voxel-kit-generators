"""harbor-trash-cans-v1 — trash can cluster.

Three galvanized cans (steel body, steel_dark bands): two upright
(one lid ajar with a raised edge + handle), one tipped on its side with
an open dark mouth and its lid off beside it. Rust patches, dark litter
on grade. Every part touches grade or the main mass (floater sweep).
z-up, at grade. FACTORY_VOXEL 0.13.
"""

import struct
import random
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
vox = {}

rng = random.Random(11)


def box(x0, x1, y0, y1, z0, z1, c):
    ci = CI[c]
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                vox[(x, y, z)] = ci


def rust_speckle(x0, x1, y0, y1, z0, z1, p):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                if vox.get((x, y, z)) == CI["steel"] and rng.random() < p:
                    vox[(x, y, z)] = CI["rust"]


def build():
    # can A: upright, lid ajar (shifted +x, one edge lifted) + handle
    box(0, 3, 0, 3, 0, 6, "steel")
    box(0, 3, 0, 3, 2, 2, "steel_dark")
    box(0, 3, 0, 3, 5, 5, "steel_dark")
    box(1, 4, 0, 3, 7, 7, "steel_dark")   # lid shifted, overhangs +x
    box(4, 4, 0, 3, 8, 8, "steel_dark")   # raised edge
    vox[(2, 1, 8)] = CI["steel_dark"]     # handle
    vox[(2, 2, 8)] = CI["steel_dark"]
    # can B: upright, lid on properly + handle
    box(5, 8, 0, 3, 0, 6, "steel")
    box(5, 8, 0, 3, 2, 2, "steel_dark")
    box(5, 8, 0, 3, 5, 5, "steel_dark")
    box(5, 8, 0, 3, 7, 7, "steel_dark")
    vox[(6, 1, 8)] = CI["steel_dark"]
    vox[(6, 2, 8)] = CI["steel_dark"]
    # can C: tipped on its side, axis along x (7 long)
    box(1, 7, 4, 7, 0, 3, "steel")
    box(2, 2, 4, 7, 0, 3, "steel_dark")   # rings
    box(5, 5, 4, 7, 0, 3, "steel_dark")
    box(1, 1, 4, 7, 0, 3, "steel_dark")   # closed end
    for y in range(4, 8):                 # dark open mouth at x=7
        for z in range(0, 4):
            if y in (4, 7) or z in (0, 3):
                if vox.get((7, y, z)) == CI["steel"]:
                    vox[(7, y, z)] = CI["steel_dark"]  # rim
            else:
                vox[(7, y, z)] = CI["dark"]           # interior
    box(8, 8, 4, 7, 0, 3, "steel_dark")   # lid off, standing beside the can
    # rust patches, denser near grade
    rust_speckle(0, 3, 0, 3, 0, 2, 0.25)
    rust_speckle(0, 3, 0, 3, 3, 6, 0.08)
    rust_speckle(5, 8, 0, 3, 0, 2, 0.25)
    rust_speckle(5, 8, 0, 3, 3, 6, 0.08)
    rust_speckle(1, 7, 4, 7, 0, 1, 0.2)
    # litter on grade
    for (x, y) in ((0, 5), (9, 2), (3, 6), (8, 6), (9, 5)):
        vox[(x, y, 0)] = CI["dark"]


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


if __name__ == "__main__":
    build()
    write_vox("harbor-trash-cans-v1.vox", vox, PALETTE)
    render_preview("harbor-trash-cans-v1_preview.png", vox, PALETTE, scale=4)
