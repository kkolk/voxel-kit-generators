"""Strike Bay infantry green v2 — narrowed T-pose soldier.

v2 (2026-09-24): one column of voxels removed from each side, from the eye
level (z 19) all the way down to the feet (z 0), to slim the silhouette.
Applied per part so details survive:
- thighs/shins/boots: outer leg column dropped (±4 -> ±3); shin taper
  kept as a 2-wide step (±2) so the leg still tapers toward the boot
- belt: hips ±4 -> ±3, belt ±5 -> ±4 (still sticks out past the hips by 1);
  hip satchels go 2-wide -> 1-wide at ±5; shoulder straps untouched at ±5
- torso: jacket ±4 -> ±3, shoulder row ±5 -> ±4, epaulettes ride the new
  shoulder edge, collar/pocket flaps shifted in to keep their inset
- face: skin/jaw narrowed ±3 -> ±2 for rows 17..19 (forehead rows 20..22
  stay as-is, hidden inside the helmet); eyes, nose, helmet untouched
- arms: hands go 2-wide -> 1-wide so the silhouette still loses one column
  per side at arm height; upper arms keep their v1 span so the sleeve
  welds at the elbow joint (±9); elbow joints and rig pivots are untouched
- helmet: one column shaved off each side and one row shorter
  (7 wide, rows 20..23); model is now 25 tall

Rig pivots unchanged from v1:
HIP=9, KNEE=5, NECK=17, SHOULDER=16 (absolute voxel rows);
ELBOW_R=+9, ELBOW_L=-9 (absolute x). Forearms are elbow-pivot-local in x.
Head is the infantry_hero_v1 head assembly, transplanted unscaled
(9 rows, pivot-local above NECK) — model is 25 tall after the helmet
shrink. Boot soles and belt buckle are gunmetal grey.

Separate kit module — other generators untouched.
"""

# ---------------------------------------------------------------- palette
PALETTE = []  # (name, (r, g, b))


def P(name, rgb):
    PALETTE.append((name, tuple(int(v) for v in rgb)))
    return len(PALETTE)


JACKET = P("jacket", (60, 68, 36))
JACKET_DARK = P("jacket_dark", (45, 52, 28))
TROUSER = P("trouser", (55, 62, 34))
EPAULETTE = P("epaulette", (130, 128, 66))
POCKET = P("pocket", (130, 128, 66))
BELT = P("belt", (25, 25, 28))
BOOTS = P("boots", (22, 22, 25))
GUNMETAL = P("gunmetal", (105, 108, 115))
SKIN = P("skin", (222, 158, 112))
SKIN_SHADOW = P("skin_shadow", (170, 110, 85))
COLLAR = P("collar", (28, 28, 30))
POUCH_CHARCOAL = P("pouch_charcoal", (48, 48, 52))
POUCH_LEATHER = P("pouch_leather", (124, 74, 40))
# head assembly transplanted from infantry_hero_v1, unscaled
HERO_SKIN = P("hero_skin", (222, 176, 133))
HERO_SKIN_SHADOW = P("hero_skin_shadow", (166, 132, 100))
HERO_EYES = P("hero_eyes", (41, 33, 26))
HELMET = P("helmet", (128, 128, 76))
HELMET_TOP = P("helmet_top", (141, 141, 94))
HELMET_BRIM = P("helmet_brim", (102, 102, 61))

# ---------------------------------------------------------------- rig pivots
# HIP/KNEE/NECK/SHOULDER: absolute voxel rows (pivot-local z).
# ELBOW_R/ELBOW_L: absolute x of the elbow joint (forearm parts are
# elbow-pivot-local in x; z stays shoulder-pivot-local).
HIP, KNEE, NECK, SHOULDER = 9, 5, 17, 16
ELBOW_R, ELBOW_L = 9, -9


def box(d, x0, x1, y0, y1, z0, z1, ci):  # inclusive, pivot-local y
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                d[(x, y, z)] = ci


def B(d, x0, x1, ay0, ay1, z0, z1, ci, piv):
    """box with ABSOLUTE z row (converted to pivot-local)."""
    box(d, x0, x1, z0, z1, ay0 - piv, ay1 - piv, ci)


def put(d, x, az, y, ci, piv):
    d[(x, y, az - piv)] = ci


def p_thigh(side):
    d = {}
    x0, x1 = (-3, -1) if side < 0 else (1, 3)   # v2: narrowed
    B(d, x0, x1, 5, 8, -2, 2, TROUSER, HIP)   # thighs touch at center
    return d, 0, HIP


def p_shin(side):
    d = {}
    if side < 0:
        B(d, -3, -1, 4, 4, -2, 2, TROUSER, KNEE)  # ankle, 6 wide
        B(d, -2, -1, 3, 3, -2, 2, TROUSER, KNEE)  # taper to 4 wide
        B(d, -3, -1, 0, 2, -2, 2, BOOTS, KNEE)    # chunky boot
        B(d, -3, -1, 0, 0, -2, 2, GUNMETAL, KNEE)  # gunmetal sole
    else:
        B(d, 1, 3, 4, 4, -2, 2, TROUSER, KNEE)
        B(d, 1, 2, 3, 3, -2, 2, TROUSER, KNEE)
        B(d, 1, 3, 0, 2, -2, 2, BOOTS, KNEE)
        B(d, 1, 3, 0, 0, -2, 2, GUNMETAL, KNEE)
    return d, 0, KNEE


def p_belt():
    d = {}
    B(d, -3, 3, 9, 9, -2, 2, TROUSER, HIP)      # hips
    B(d, -4, 4, 10, 11, -2, 2, BELT, HIP)      # belt, sticks out past hips
    B(d, -1, 1, 10, 11, 3, 3, GUNMETAL, HIP)     # buckle block, front
    # hip satchels + shoulder straps (bags touch the hip side)
    B(d, -5, -5, 9, 11, -2, 1, POUCH_LEATHER, HIP)   # leather, his right hip
    B(d, -5, -5, 12, 14, -2, -2, POUCH_LEATHER, HIP)  # leather strap, up the side
    B(d, 5, 5, 8, 11, -2, 1, POUCH_CHARCOAL, HIP)       # charcoal, his left hip
    B(d, 5, 5, 12, 14, -2, -2, POUCH_CHARCOAL, HIP)      # charcoal strap, up the side
    return d, 0, HIP


def p_torso():
    d = {}
    B(d, -3, 3, 12, 16, -2, 2, JACKET, HIP)    # jacket
    B(d, -4, 4, 17, 17, -2, 2, JACKET, HIP)    # shoulder row, wider
    B(d, -4, -3, 17, 17, -2, 2, EPAULETTE, HIP)  # shoulder boards
    B(d, 3, 4, 17, 17, -2, 2, EPAULETTE, HIP)
    B(d, -2, 2, 17, 17, 0, 2, COLLAR, HIP)    # black collar, front of neck
    B(d, -1, 1, 17, 17, -2, -1, COLLAR, HIP)   # collar, back of neck
    # chest pocket flaps, proud of the jacket front
    B(d, -2, -1, 14, 15, 3, 3, POCKET, HIP)
    B(d, 1, 2, 14, 15, 3, 3, POCKET, HIP)
    B(d, -1, 1, 12, 16, -2, -2, JACKET_DARK, HIP)  # center back shading
    return d, 0, HIP


def p_head():
    # hero head transplanted from infantry_hero_v1, unscaled — pivot-local
    # above NECK (absolute rows 17..25). v2 narrows the visible face
    # (rows 17..19) one column per side; forehead rows 20..22 are hidden
    # inside the helmet and stay as-is. Helmet untouched.
    d = {}
    B(d, -2, 2, 17, 19, -1, 2, HERO_SKIN, NECK)
    B(d, -3, 3, 20, 22, -1, 2, HERO_SKIN, NECK)      # hidden under helmet
    B(d, -2, 2, 17, 18, 3, 3, HERO_SKIN, NECK)        # squared jutting jaw
    B(d, -2, 2, 17, 17, 2, 2, HERO_SKIN_SHADOW, NECK)  # jawline shadow
    # stern angled eyes (inner ends lower)
    B(d, -2, -2, 20, 20, 2, 2, HERO_EYES, NECK)
    B(d, -1, -1, 19, 19, 2, 2, HERO_EYES, NECK)
    B(d, 2, 2, 20, 20, 2, 2, HERO_EYES, NECK)
    B(d, 1, 1, 19, 19, 2, 2, HERO_EYES, NECK)
    put(d, 0, 19, 3, HERO_SKIN_SHADOW, NECK)          # nose hint
    # big boxy helmet, low over the brow — v2 revision 2026-09-24: one
    # column shaved off each side and one row shorter (now 7 wide, z 20..23)
    B(d, -3, 3, 20, 23, -2, 3, HELMET, NECK)
    B(d, -3, 3, 20, 20, 4, 4, HELMET_BRIM, NECK)    # front brim lip
    B(d, -2, 2, 24, 24, -1, 2, HELMET_TOP, NECK)    # flat top catches light
    return d, 0, NECK


def p_upper_arm(side):
    # T-pose, shoulder-pivot-local: from the shoulder out to the elbow joint
    d = {}
    if side < 0:
        B(d, -8, -4, 14, 16, -1, 1, JACKET, SHOULDER)   # welds into shoulder row
    else:
        B(d, 4, 8, 14, 16, -1, 1, JACKET, SHOULDER)
    return d, 0, SHOULDER


def p_forearm(side):
    # elbow-pivot-local in x (z stays shoulder-pivot-local). The forearm's
    # first column sits ON the elbow pivot x, so the rig can rotate the arm
    # around (ELBOW_x, y=0, row 15) with the joint voxel intact.
    d = {}
    if side < 0:
        B(d, -3, 0, 14, 16, -1, 1, JACKET, SHOULDER)    # world x -12..-9
        B(d, -4, -4, 15, 16, -1, 1, SKIN, SHOULDER)     # hand, world x -13
        B(d, -4, -4, 15, 15, -1, 1, SKIN_SHADOW, SHOULDER)
        return d, ELBOW_L, SHOULDER
    else:
        B(d, 0, 3, 14, 16, -1, 1, JACKET, SHOULDER)     # world x 9..12
        B(d, 4, 4, 15, 16, -1, 1, SKIN, SHOULDER)       # hand, world x 13
        B(d, 4, 4, 15, 15, -1, 1, SKIN_SHADOW, SHOULDER)
        return d, ELBOW_R, SHOULDER


# ---------------------------------------------------------------- compose (game coords -> vox z-up)
vox = {}
for d, px, pz in [p_thigh(-1), p_thigh(1), p_shin(-1), p_shin(1),
                  p_belt(), p_torso(), p_head(),
                  p_upper_arm(-1), p_upper_arm(1),
                  p_forearm(-1), p_forearm(1)]:
    for (x, y, z), ci in d.items():
        vox[(x + px, y, z + pz)] = ci

# ---------------------------------------------------------------- .vox writer — verbatim boilerplate
def write_vox(path, vox, PALETTE):
    import struct
    fmt_i = "<" + "i"
    fmt_ii = "<" + "ii"
    fmt_iii = "<" + "iii"
    def chunk(cid, content, children=b""):
        return cid + struct.pack(fmt_ii, len(content), len(children)) + content + children
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    sx, sy, sz = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) + 1
    xoff, yoff = -min(xs), -min(ys)
    size_content = struct.pack(fmt_iii, sx, sy, sz)
    xyzi = struct.pack(fmt_i, len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("BBBB", x + xoff, y + yoff, z, ci)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in PALETTE)
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(PALETTE))
    main_children = chunk(b"SIZE", size_content) + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)
    with open(path, "wb") as f:
        f.write(b"VOX ")
        f.write(struct.pack(fmt_i, 150))
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
    write_vox(os.path.join(here, "infantry_green_v2.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "infantry_green_v2_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "infantry_green_v2_slice_z15.png"), vox, PALETTE, 15)
