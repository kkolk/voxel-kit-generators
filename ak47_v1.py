"""Strike Bay ak-47 v1 — standalone AK-47 rifle as a separate kit module,
scaled to sit alongside infantry_green_v1 (26 voxels tall ~ 175 cm, so
1 voxel ~= 6.7 cm; a real AK-47 at ~88 cm => ~13 voxels long).

Lies horizontal along the x axis, barrel pointing +x, z up. Single
connected part — this is a prop model, not a rigged figure.

Side profile (z up, x along the gun):
  stock (wood)      x 0..3   butt plate at x 0, slightly taller
  receiver (steel)  x 3..6   2 tall, rear sight block on top at x 3
  pistol grip       x 4..5   angled down, wood
  trigger+guard     x 5..6   thin steel under the receiver
  banana mag        x 5..7   steel, stepping forward-down to z -2
  handguard (wood)  x 7..9   lower + upper, steel gas tube above at z 4
  barrel (steel)    x 10..12 thin, front sight post near the muzzle
  extras: charging handle on the side, muzzle nut (black accent)

Separate kit module — other generators untouched.
"""

# ---------------------------------------------------------------- palette
PALETTE = []  # (name, (r, g, b))


def P(name, rgb):
    PALETTE.append((name, tuple(int(v) for v in rgb)))
    return len(PALETTE)


WOOD = P("wood", (150, 100, 55))
WOOD_DARK = P("wood_dark", (110, 72, 38))
STEEL = P("steel", (78, 82, 92))
STEEL_DARK = P("steel_dark", (45, 47, 55))
ACCENT_BLACK = P("accent_black", (20, 20, 22))

# ---------------------------------------------------------------- geometry
vox = {}


def box(x0, x1, y0, y1, z0, z1, ci):
    """inclusive box, absolute coords."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                vox[(x, y, z)] = ci


def put(x, y, z, ci):
    vox[(x, y, z)] = ci


# --- stock (wood), butt plate at x 0 slightly taller/deeper
box(0, 0, 0, 0, 0, 3, WOOD_DARK)     # butt plate
box(1, 2, 0, 0, 1, 2, WOOD)         # stock body
box(1, 1, 0, 0, 0, 0, WOOD_DARK)    # heel shading at the butt

# --- receiver (steel), x 3..6, z 2..3
box(3, 6, 0, 0, 2, 3, STEEL)
box(3, 3, 0, 0, 4, 4, STEEL_DARK)   # rear sight block
box(4, 5, 1, 1, 3, 3, STEEL_DARK)   # charging handle on the side

# --- pistol grip (wood), angled down behind the trigger
box(4, 4, 0, 0, 0, 1, WOOD)
box(5, 5, 0, 0, 0, 0, WOOD_DARK)

# --- trigger + thin trigger guard
put(5, 0, 1, STEEL_DARK)            # trigger
box(5, 6, 0, 0, 1, 1, STEEL)        # guard bar (blends into receiver bottom)

# --- banana magazine (steel dark), stepping forward and down
box(5, 5, 0, 0, 0, 1, STEEL_DARK)   # mag lug under the receiver
box(6, 6, 0, 0, -1, 0, STEEL_DARK)
box(7, 7, 0, 0, -2, -1, STEEL_DARK)  # tip, ~4 below the receiver line

# --- wooden handguard + steel gas tube
box(7, 9, 0, 0, 1, 2, WOOD)         # lower handguard
box(7, 9, 0, 0, 3, 3, WOOD)         # upper handguard
box(7, 9, 0, 0, 4, 4, STEEL)        # gas tube
box(9, 9, 0, 0, 3, 4, STEEL_DARK)   # gas block at the front of the tube

# --- thin steel barrel, front sight, muzzle nut
box(10, 12, 0, 0, 2, 2, STEEL_DARK)  # barrel
box(11, 11, 0, 0, 2, 3, STEEL_DARK)  # front sight base
put(11, 0, 4, STEEL)                 # front sight post
box(12, 12, 0, 0, 2, 2, ACCENT_BLACK)  # muzzle nut


# ---------------------------------------------------------------- .vox writer — verbatim boilerplate
def write_vox(path, vox, PALETTE):
    import struct
    fmt_i = "<" + "i"
    fmt_ii = "<" + "ii"
    fmt_iii = "<" + "iii"

    def chunk(cid, content, children=b""):
        return cid + struct.pack(fmt_ii, len(content), len(children)) + content + children
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    sx, sy, sz = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) - min(zs) + 1
    xoff, yoff, zoff = -min(xs), -min(ys), -min(zs)
    size_content = struct.pack(fmt_iii, sx, sy, sz)
    xyzi = struct.pack(fmt_i, len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("BBBB", x + xoff, y + yoff, z + zoff, ci)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in PALETTE)
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(PALETTE))
    main_children = chunk(b"SIZE", size_content) + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)
    with open(path, "wb") as f:
        f.write(b"VOX ")
        f.write(struct.pack(fmt_i, 150))
        f.write(chunk(b"MAIN", b"", main_children))
    print(f"wrote {path} ({len(vox)} voxels)")


# ---------------------------------------------------------------- isometric preview — verbatim boilerplate
def render_preview(path, vox, PALETTE, scale=4):
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
    write_vox(os.path.join(here, "ak47_v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "ak47_v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "ak47_v1_slice_z2.png"), vox, PALETTE, 2)
