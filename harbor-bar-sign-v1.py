"""harbor-bar-sign-v1 — painted cantina board sign.

Freestanding wood-post sign: cream board with dark 3x5 "BAR" over
"LA ESQUINA" (weathered), wood_dark edge trim, striped white/pump_red
awning below the board on wood posts. z-up, at grade. FACTORY_VOXEL 0.13.

Note: the board is 40 wide (not 14) — "LA ESQUINA" needs 39 voxels at
3x5 and cannot fit the spec's 14-wide board at any legible size.
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

FONT_3X5 = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "B": ["##.", "#.#", "##.", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "N": ["#.#", "##.", "##.", "#.#", "#.#"],
    "Q": [".#.", "#.#", "#.#", "##.", ".##"],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": [".##", "#..", ".#.", "..#", "##."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"],
    " ": ["...", "...", "...", "...", "..."],
}

rng = random.Random(20261004)


def box(x0, x1, y0, y1, z0, z1, c):
    ci = CI[c]
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                vox[(x, y, z)] = ci


def text(s, x0, z_top, y, c, spacing=1):
    """3x5 letters, rows top-to-bottom mapping to z_top downward, 1 deep at y."""
    ci = CI[c]
    x = x0
    for ch in s:
        for r, row in enumerate(FONT_3X5[ch]):
            z = z_top - r
            for dx, bit in enumerate(row):
                if bit == "#":
                    vox[(x + dx, y, z)] = ci
        x += 3 + spacing


def build():
    # posts (drawn first; board overwrites the overlap behind it)
    box(3, 4, 0, 1, 0, 19, "wood")
    box(35, 36, 0, 1, 0, 19, "wood")
    # cream board x 0..39, y=1, z 8..19
    box(0, 39, 1, 1, 8, 19, "cream")
    # wood_dark edge trim on both faces (top rail + side stiles)
    for y in (0, 2):
        for x in range(0, 40):
            vox[(x, y, 19)] = CI["wood_dark"]
        for z in range(8, 20):
            vox[(0, y, z)] = CI["wood_dark"]
            vox[(39, y, z)] = CI["wood_dark"]
    # lettering on both faces
    for y in (0, 2):
        text("BAR", 14, 18, y, "dark")               # rows z 14..18
        text("LA ESQUINA", 5, 12, y, "dark", spacing=0)  # rows z 8..12, x 5..34
    # weathering: knocked-out letter voxels + worn cream speckle
    for p, ci in list(vox.items()):
        if ci == CI["dark"] and rng.random() < 0.07:
            del vox[p]
        elif ci == CI["cream"] and rng.random() < 0.05:
            vox[p] = CI["wood"]
    # striped awning below the board: stepped slope from the board face
    for i, y in enumerate((0, -1, -2, -3)):
        ztop = 8 - i
        for x in range(6, 34):
            c = "white" if ((x - 6) // 2) % 2 == 0 else "pump_red"
            vox[(x, y, ztop)] = CI[c]
            vox[(x, y, ztop - 1)] = CI[c]  # riser keeps 6-connectivity
    for x in range(6, 34):  # valance
        c = "white" if ((x - 6) // 2) % 2 == 0 else "pump_red"
        vox[(x, -3, 2)] = CI[c]
        vox[(x, -3, 3)] = CI[c]
    box(6, 6, -3, -3, 0, 2, "wood_dark")   # awning support poles
    box(33, 33, -3, -3, 0, 2, "wood_dark")


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
    write_vox("harbor-bar-sign-v1.vox", vox, PALETTE)
    render_preview("harbor-bar-sign-v1_preview.png", vox, PALETTE, scale=2)
