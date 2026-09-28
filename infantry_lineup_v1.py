"""Strike Bay infantry lineup v1 — the four faction kits from the game's
soldier() (infantry section), composed front-facing, rifle up, legs
straight, pivot-welded exactly like the GDScript: every part authored
pivot-local in y, welded at its absolute pivot row. Four soldiers stand
side by side (olive / desert / tan / grey-teal / light-grey kits) so the
uniform variations read at a glance.

Scale: 30 voxels tall, boot sole (y=0) to cap top (y=29). Pivots:
hip 11, knee 6, neck 21, shoulder 20. The rifle rides on the soldier's
right (+x): muzzle voxel sits one past the barrel tip at local
(2, 19, 13), matching SOLDIER_MUZZLE.

GDScript notes honored: box() is inclusive on both ends (the 4-wide
asymmetric skull only works inclusive); Color.darkened(a) = v*(1-a);
Color.lightened(a) = v+(1-v)*a. WOOD/GUNMETAL/BLACK/BARREL are game
globals not present in the pasted section — values below are picks.

Separate kit module — other generators untouched.
"""

# ---------------------------------------------------------------- palette registry (named entries → Assemblies)
PALETTE = []  # (name, (r, g, b))


def P(name, rgb):
    PALETTE.append((name, tuple(int(v) for v in rgb)))
    return len(PALETTE)  # 1-based color index


def F(r, g, b):
    return (round(r * 255), round(g * 255), round(b * 255))


def dark(rgb, a):
    return tuple(round(v * (1 - a)) for v in rgb)


def light(rgb, a):
    return tuple(round(v + (255 - v) * a) for v in rgb)


WOOD = P("wood", F(0.48, 0.30, 0.15))
GUNMETAL = P("gunmetal", F(0.28, 0.29, 0.32))
BLACK = P("black", F(0.06, 0.06, 0.07))
BARREL = P("barrel", F(0.16, 0.16, 0.18))

# ---------------------------------------------------------------- the four reference kits (faction mod 4)
KITS = [
    dict(name="olive", cap=0, web=0,
         tunic=F(.34, .36, .20), trouser=F(.30, .32, .18), headgear=F(.33, .34, .19),
         webbing=F(.62, .55, .32), belt=F(.20, .18, .15), boots=F(.24, .16, .10),
         pack=F(.50, .43, .27), skin=F(.80, .66, .50), hair=F(.36, .22, .12),
         scarf=None, cuffs=None, gaiters=None, pouches=None),
    dict(name="desert", cap=0, web=3,
         tunic=F(.70, .59, .48), trouser=F(.52, .53, .31), headgear=F(.26, .27, .26),
         webbing=F(.52, .32, .15), belt=F(.20, .18, .15), boots=F(.24, .16, .10),
         pack=F(.42, .33, .22), skin=F(.80, .66, .50), hair=F(.36, .22, .12),
         scarf=F(.38, .37, .22), cuffs=F(.60, .45, .28),
         gaiters=F(.68, .63, .50), pouches=F(.72, .42, .17)),
    dict(name="teal", cap=2, web=2,
         tunic=F(.42, .48, .46), trouser=F(.36, .41, .40), headgear=F(.10, .10, .11),
         webbing=F(.16, .17, .18), belt=F(.09, .09, .10), boots=F(.09, .09, .10),
         pack=F(.27, .30, .29), skin=F(.85, .72, .60), hair=F(.36, .22, .12),
         scarf=None, cuffs=None, gaiters=None, pouches=None),
    dict(name="grey", cap=3, web=1,
         tunic=F(.70, .70, .76), trouser=F(.60, .61, .66), headgear=F(.55, .56, .58),
         webbing=F(.13, .13, .14), belt=F(.09, .09, .10), boots=F(.09, .09, .10),
         pack=F(.48, .47, .52), skin=F(.85, .72, .60), hair=F(.36, .22, .12),
         scarf=None, cuffs=None, gaiters=None, pouches=None),
]


def kit_colors(k):
    n = k["name"]
    c = {}
    for part in ("tunic", "trouser", "headgear", "webbing", "belt",
                 "boots", "pack", "skin", "hair"):
        c[part] = P(f"{n}_{part}", k[part])
    c["pack_dark"] = P(f"{n}_pack_dark", dark(k["pack"], 0.2))
    c["skin_shadow"] = P(f"{n}_skin_shadow", dark(k["skin"], 0.3))
    c["headgear_brim"] = P(f"{n}_headgear_brim", dark(k["headgear"], 0.25))
    c["headgear_visor"] = P(f"{n}_headgear_visor", dark(k["headgear"], 0.3))
    c["headgear_top"] = P(f"{n}_headgear_top", light(k["headgear"], 0.08))
    c["headgear_top_dark"] = P(f"{n}_headgear_top_dark", dark(k["headgear"], 0.15))
    if k["scarf"]:
        c["scarf"] = P(f"{n}_scarf", k["scarf"])
        c["scarf_knot"] = P(f"{n}_scarf_knot", light(k["scarf"], 0.3))
    if k["cuffs"]:
        c["cuffs"] = P(f"{n}_cuffs", k["cuffs"])
    if k["gaiters"]:
        c["gaiters"] = P(f"{n}_gaiters", k["gaiters"])
    if k["pouches"]:
        c["pouches"] = P(f"{n}_pouches", k["pouches"])
        c["pouches_dark"] = P(f"{n}_pouches_dark", dark(k["pouches"], 0.35))
    return c


# ---------------------------------------------------------------- rig pivots (absolute voxel rows)
HIP, KNEE, NECK, SHOULDER = 11, 6, 21, 20


def box(d, x0, x1, y0, y1, z0, z1, ci):  # inclusive, like VoxelData.box
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                d[(x, y, z)] = ci


def put(d, x, y, z, ci):
    d[(x, y, z)] = ci


def p_thigh(c, side):
    d = {}
    x0 = -2 if side < 0 else 1
    box(d, x0, x0 + 1, KNEE - HIP, -1, -1, 1, c["trouser"])
    return d, HIP


def p_shin(c, side):
    d = {}
    x0 = -2 if side < 0 else 1
    sole = -KNEE
    box(d, x0, x0 + 1, sole + 2, -1, -1, 1, c["trouser"])
    if "gaiters" in c:
        box(d, x0, x0 + 1, sole + 2, sole + 3, -1, 1, c["gaiters"])
    box(d, x0, x0 + 1, sole, sole + 1, -1, 2, c["boots"])  # toe juts forward
    return d, KNEE


def p_belt(c, k):
    d = {}
    box(d, -2, 2, 0, 0, -1, 1, c["belt"])
    if "pouches" in c:
        box(d, -2, 2, -1, -1, 2, 2, c["pouches_dark"])  # flap row lit, body darker
        box(d, -2, 2, 0, 0, 2, 2, c["pouches"])
        return d, HIP
    box(d, -1, 1, 0, 0, 2, 2, c["webbing"])      # buckle plate
    box(d, -2, -2, -1, 0, 2, 2, c["webbing"])    # hip pouches hang
    box(d, 2, 2, -1, 0, 2, 2, c["webbing"])      # off the buckle plate
    return d, HIP


def p_torso(c, k):
    d = {}
    box(d, -2, 2, 1, 9, -1, 1, c["tunic"])
    box(d, -3, 3, 8, 9, -1, 1, c["tunic"])          # shoulder row, one wider
    box(d, -1, 1, 2, 8, -3, -2, c["pack"])          # backpack, baked in
    box(d, -1, 1, 2, 2, -3, -1, c["pack_dark"])     # bottom flap
    if k["web"] == 1:                              # single bandolier
        for i in range(5):
            put(d, -2 + i, 9 - i * 2, 1, c["webbing"])
    elif k["web"] == 2:                            # none
        pass
    elif k["web"] == 3:                            # suspenders
        box(d, -1, -1, 1, 9, 1, 1, c["webbing"])
        box(d, 1, 1, 1, 9, 1, 1, c["webbing"])
    else:                                          # X cross
        for i in range(5):
            put(d, -2 + i, 9 - i * 2, 1, c["webbing"])
            put(d, 2 - i, 9 - i * 2, 1, c["webbing"])
    if "scarf" in c:
        box(d, -1, 1, 10, 10, -1, 1, c["scarf"])    # wrapped neck
        put(d, 0, 9, 1, c["scarf_knot"])            # knot at the throat
    else:
        box(d, -1, 1, 10, 10, 0, 0, c["skin"])      # neck
    return d, HIP


def p_head(c, k):
    d = {}
    box(d, -2, 1, 1, 6, -1, 1, c["skin"])
    box(d, -2, 1, 1, 1, 2, 2, c["skin"])                 # jaw juts forward, squared
    box(d, -2, 1, 1, 1, 1, 1, c["skin_shadow"])          # jawline shadow
    box(d, -2, -2, 3, 5, -1, 0, c["hair"])               # temples / sideburns
    box(d, 1, 1, 3, 5, -1, 0, c["hair"])
    box(d, -2, 1, 3, 5, -1, -1, c["hair"])               # back of the head
    if k["cap"] == 1:                                   # wide campaign brim
        box(d, -5, 5, 6, 6, -5, 5, c["headgear"])
        box(d, -2, 2, 7, 8, -2, 2, c["headgear"])
        box(d, -2, 2, 8, 8, -2, 2, c["headgear_top_dark"])
    elif k["cap"] == 2:                                 # peaked cap
        box(d, -3, 3, 6, 6, -3, 3, c["headgear"])
        box(d, -2, 2, 7, 7, -2, 2, c["headgear"])
        box(d, -1, 1, 8, 8, -1, 1, c["headgear"])
        box(d, -1, 1, 6, 6, 4, 4, c["headgear_visor"])
    elif k["cap"] == 3:                                 # kepi
        box(d, -3, 3, 6, 6, -3, 3, c["headgear"])
        box(d, -2, 2, 7, 7, -2, 2, c["headgear"])
        box(d, -1, 1, 8, 8, -1, 1, c["headgear_top_dark"])
        box(d, -1, 1, 6, 6, 4, 4, c["headgear_visor"])
    else:                                               # steel helmet, low over the brow
        box(d, -3, 2, 5, 7, -2, 2, c["headgear"])
        box(d, -3, 2, 5, 5, 3, 3, c["headgear_brim"])    # front brim lip
        box(d, -2, 1, 8, 8, -1, 1, c["headgear_top"])    # flat top catches light
    return d, NECK


def p_arms(c, k):
    d = {}
    # left arm: shoulder across the body to the trigger grip (follows the gun right)
    box(d, -3, -2, -2, 0, -1, 1, c["tunic"])
    box(d, -2, 1, -2, -1, 1, 4, c["tunic"])
    if "cuffs" in c:
        box(d, 0, 1, -2, -1, 2, 3, c["cuffs"])
    box(d, 1, 2, -1, -1, 3, 4, c["skin"])          # trigger hand
    # right arm: one voxel toward the soldier's right, reaching further forward
    box(d, 3, 4, -2, 0, -1, 1, c["tunic"])
    box(d, 2, 3, -2, -1, 1, 7, c["tunic"])
    if "cuffs" in c:
        box(d, 2, 3, -2, -2, 5, 5, c["cuffs"])
        put(d, 3, -1, 5, c["cuffs"])
    box(d, 2, 3, -1, -1, 6, 7, c["skin"])          # support hand on the handguard
    # rifle: shifted right with the arm and lengthened; AK banana magazine
    box(d, 2, 2, -1, 0, 0, 2, WOOD)                # stock
    box(d, 2, 2, -1, 0, 2, 5, GUNMETAL)            # receiver
    box(d, 2, 2, -2, -2, 3, 4, BLACK)              # banana mag: top step,
    box(d, 2, 2, -3, -3, 4, 5, BLACK)              # curving forward-down,
    box(d, 2, 2, -4, -4, 5, 6, BLACK)              # mag tip
    box(d, 2, 2, -1, 0, 5, 8, WOOD)                # handguard
    box(d, 2, 2, -1, -1, 8, 12, BARREL)            # barrel
    put(d, 2, 0, 12, GUNMETAL)                     # front sight post
    return d, SHOULDER


# ---------------------------------------------------------------- compose: weld parts at pivots, line up the four kits
vox = {}
for i, k in enumerate(KITS):
    c = kit_colors(k)
    parts = [p_thigh(c, -1), p_thigh(c, 1), p_shin(c, -1), p_shin(c, 1),
             p_belt(c, k), p_torso(c, k), p_head(c, k), p_arms(c, k)]
    xo = int((i - 1.5) * 14)
    for d, py in parts:
        for (x, y, z), ci in d.items():
            # game (x=right, y=up, z=front) -> vox (x=right, y=depth, z=up):
            # the viewer and every other model in this kit are z-up.
            vox[(x + xo, z + 3, y + py)] = ci


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
    write_vox(os.path.join(here, "infantry_lineup_v1.vox"), vox, PALETTE)
    render_preview(os.path.join(here, "infantry_lineup_v1_preview.png"), vox, PALETTE)
    render_slice(os.path.join(here, "infantry_lineup_v1_slice_z15.png"), vox, PALETTE, 15)
