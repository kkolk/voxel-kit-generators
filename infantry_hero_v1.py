"""Strike Bay infantry hero v1 — chunky hero soldier inspired by the
reference render, on the same rig as the lineup: 30 voxels tall, pivots
hip 11 / knee 6 / neck 21 / shoulder 20, 8 pivot-local parts (gun lives
in the arms piece so it aims with the arms). Chunky read: 11-wide
shoulders, 9-wide boxy helmet, 3-wide limbs, big rucksack, tac vest
with pouches, knee pads, simple stern eyes. The rifle is carried
horizontally across the chest, pointing to the figure's right; the
right arm is THE SLOPED ARM — thick voxel steps down-left to the
handguard, the left hand grips under the trigger.

Separate kit module — other generators untouched.
"""

# ---------------------------------------------------------------- palette
PALETTE = []  # (name, (r, g, b))


def P(name, rgb):
    PALETTE.append((name, tuple(int(v) for v in rgb)))
    return len(PALETTE)


def F(r, g, b):
    return (round(r * 255), round(g * 255), round(b * 255))


def dark(rgb, a):
    return tuple(round(v * (1 - a)) for v in rgb)


def light(rgb, a):
    return tuple(round(v + (255 - v) * a) for v in rgb)


HELMET = P("helmet", F(0.50, 0.50, 0.30))
HELMET_TOP = P("helmet_top", light(F(0.50, 0.50, 0.30), 0.10))
HELMET_BRIM = P("helmet_brim", dark(F(0.50, 0.50, 0.30), 0.20))
TUNIC = P("tunic", F(0.42, 0.42, 0.24))
TROUSER = P("trouser", F(0.44, 0.43, 0.26))
VEST = P("vest", F(0.36, 0.36, 0.21))
POUCH = P("pouch", F(0.60, 0.53, 0.33))
BELT = P("belt", F(0.22, 0.20, 0.14))
BOOTS = P("boots", F(0.52, 0.36, 0.20))
BOOT_DARK = P("boot_dark", dark(F(0.52, 0.36, 0.20), 0.30))
KNEEPAD = P("kneepad", F(0.28, 0.29, 0.16))
SKIN = P("skin", F(0.87, 0.69, 0.52))
SKIN_SHADOW = P("skin_shadow", dark(F(0.87, 0.69, 0.52), 0.25))
EYES = P("eyes", F(0.16, 0.13, 0.10))
PACK = P("pack", F(0.45, 0.44, 0.27))
PACK_DARK = P("pack_dark", dark(F(0.45, 0.44, 0.27), 0.25))
GUNMETAL = P("gunmetal", F(0.30, 0.30, 0.32))
GUN_DARK = P("gun_dark", F(0.18, 0.18, 0.20))
BLACK = P("black", F(0.08, 0.08, 0.09))

# ---------------------------------------------------------------- rig pivots (absolute voxel rows, game y-up)
HIP, KNEE, NECK, SHOULDER = 11, 6, 21, 20


def box(d, x0, x1, y0, y1, z0, z1, ci):  # inclusive, pivot-local y
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                d[(x, y, z)] = ci


def B(d, x0, x1, ay0, ay1, z0, z1, ci, piv):
    """box with ABSOLUTE y (converted to pivot-local)."""
    box(d, x0, x1, ay0 - piv, ay1 - piv, z0, z1, ci)


def put(d, x, ay, z, ci, piv):
    d[(x, ay - piv, z)] = ci


def p_thigh(side):
    d = {}
    x0, x1 = (-4, -2) if side < 0 else (2, 4)
    B(d, x0, x1, 6, 10, -2, 1, TROUSER, HIP)
    return d, HIP


def p_shin(side):
    d = {}
    x0, x1 = (-4, -2) if side < 0 else (2, 4)
    B(d, x0, x1, 3, 5, -2, 1, TROUSER, KNEE)
    B(d, x0, x1, 4, 5, 2, 2, KNEEPAD, KNEE)      # knee pads
    B(d, x0, x1, 0, 2, -2, 2, BOOTS, KNEE)       # chunky boots, toe forward
    B(d, x0, x1, 0, 0, -2, 2, BOOT_DARK, KNEE)   # sole shadow
    return d, KNEE


def p_belt():
    d = {}
    B(d, -4, 4, 11, 11, -2, 2, BELT, HIP)
    B(d, -3, 3, 10, 11, 3, 3, POUCH, HIP)        # belt pouches, front
    B(d, -1, 1, 11, 11, 3, 3, POUCH, HIP)
    return d, HIP


def p_torso():
    d = {}
    B(d, -4, 4, 12, 20, -2, 2, TUNIC, HIP)
    B(d, -5, 5, 19, 20, -2, 2, TUNIC, HIP)       # shoulder row, wider
    B(d, -3, 3, 14, 18, 3, 3, VEST, HIP)         # tac vest front panel
    for px in (-3, -1, 1, 3):                     # vest pouches
        B(d, px, px, 15, 17, 4, 4, POUCH, HIP)
    # rucksack, baked in — tall, peeks over the shoulders
    B(d, -3, 3, 13, 19, -5, -3, PACK, HIP)
    B(d, -3, 3, 19, 22, -5, -3, PACK, HIP)       # top roll
    B(d, -3, 3, 13, 13, -5, -3, PACK_DARK, HIP)  # bottom flap
    B(d, -2, 2, 14, 18, -3, -3, PACK_DARK, HIP)  # back panel detail
    # shoulder straps, front
    B(d, -4, -3, 14, 19, 3, 3, PACK_DARK, HIP)
    B(d, 3, 4, 14, 19, 3, 3, PACK_DARK, HIP)
    B(d, -1, 1, 21, 21, -1, 1, SKIN_SHADOW, HIP)  # neck shadow
    return d, HIP


def p_head():
    d = {}
    B(d, -3, 3, 21, 26, -1, 2, SKIN, NECK)
    B(d, -3, 3, 21, 22, 3, 3, SKIN, NECK)        # squared jutting jaw
    B(d, -3, 3, 21, 21, 2, 2, SKIN_SHADOW, NECK)  # jawline shadow
    # stern angled eyes
    B(d, -2, -2, 24, 24, 2, 2, EYES, NECK)
    B(d, -1, -1, 23, 23, 2, 2, EYES, NECK)
    B(d, 2, 2, 24, 24, 2, 2, EYES, NECK)
    B(d, 1, 1, 23, 23, 2, 2, EYES, NECK)
    put(d, 0, 23, 3, SKIN_SHADOW, NECK)          # nose hint
    # big boxy helmet, low over the brow
    B(d, -4, 4, 24, 28, -2, 3, HELMET, NECK)
    B(d, -4, 4, 24, 24, 4, 4, HELMET_BRIM, NECK)  # front brim lip
    B(d, -3, 3, 29, 29, -1, 2, HELMET_TOP, NECK)  # flat top catches light
    return d, NECK


def p_arms():
    d = {}
    # left arm: shoulder down, forearm forward, hand under the trigger
    B(d, -5, -3, 17, 19, -1, 1, TUNIC, SHOULDER)
    B(d, -5, -3, 16, 18, 1, 3, TUNIC, SHOULDER)
    B(d, -4, -2, 16, 17, 3, 5, TUNIC, SHOULDER)
    B(d, -3, -2, 16, 17, 5, 6, SKIN, SHOULDER)   # trigger hand, under receiver
    # right arm: THE SLOPED ARM — thick steps down-left across the body
    B(d, 3, 5, 17, 19, -1, 1, TUNIC, SHOULDER)   # upper arm at the shoulder
    B(d, 2, 4, 16, 18, 1, 3, TUNIC, SHOULDER)    # slope step 1
    B(d, 1, 3, 16, 17, 3, 5, TUNIC, SHOULDER)    # slope step 2
    B(d, 0, 2, 16, 16, 5, 6, TUNIC, SHOULDER)    # slope step 3
    B(d, 0, 1, 16, 17, 5, 6, SKIN, SHOULDER)     # support hand, under handguard
    # rifle, horizontal across the chest, pointing to the figure's right
    B(d, -5, -3, 17, 18, 5, 6, GUN_DARK, SHOULDER)   # stock
    B(d, -3, -1, 17, 18, 5, 6, GUNMETAL, SHOULDER)   # receiver
    B(d, -2, -2, 15, 16, 5, 6, BLACK, SHOULDER)      # magazine
    put(d, -2, 18, 5, GUN_DARK, SHOULDER)             # rear sight
    B(d, 0, 2, 17, 18, 5, 6, GUN_DARK, SHOULDER)     # handguard
    B(d, 3, 8, 17, 17, 5, 6, GUNMETAL, SHOULDER)      # barrel
    put(d, 7, 18, 5, GUNMETAL, SHOULDER)              # front sight post
    return d, SHOULDER


# ---------------------------------------------------------------- compose (game y-up -> vox z-up)
vox = {}
for d, py in [p_thigh(-1), p_thigh(1), p_shin(-1), p_shin(1),
              p_belt(), p_torso(), p_head(), p_arms()]:
    for (x, y, z), ci in d.items():
        vox[(x, z + 5, y + py)] = ci  # z + 5: rucksack sits at z=-5

# ---------------------------------------------------------------- .vox writer — verbatim boilerplate
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
    write_vox(os.path.join(here, "infantry_hero_v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "infantry_hero_v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "infantry_hero_v1_slice_z15.png"), vox, PALETTE, 15)
