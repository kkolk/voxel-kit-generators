#!/usr/bin/env python3
"""Strike Bay BODEGA CORNER — seaside-town tileset v1 (2026-10-05).

First building of the rundown communist-Caribbean seaside town: a 4-story
colonial corner tenement with a ground-floor bodega behind an arched arcade.
Off the user's bodega-corner concept painting (ochre plaster, teal trim,
stone arcade, striped awning, tinacos + TV antennas on the roof).

FACTORY-KIT METHOD, town content:
  B = 12 bay, S = 10 story, T = 2 wall, z-up, origin at footprint min corner,
  no slab/yard. In game 0.3 m per voxel (3 m story, 3.6 m bay; see the
  spec's scale note). Tileset unit = one 12x12 bay, one story
  tall (z s..s+10). Canonical orientation faces SOUTH (wall at y 0..2); the
  assembler rotates bays CCW about the bay centre (S->E->N->W).
  Seam rule (mill-style, strict): wall ends meet flush at bay lines; nothing
  protrudes along the bay-run direction. Outer corner columns (2x2) are
  written whole by the corner module; the L's inside notch is closed by a
  dedicated 2x2 pier tile. Protrusions along the wall-face normal are the
  design (balcony slab 2, awning 3, sills/cornice/coping 1) — never sideways.
  Interiors are WIDE OPEN (no buried rooms): a full stone ground slab at
  z 0..1 and a wood-plank floor slab at the top voxel of every story band
  (z 9..10, 19..20, 29..30, 39..40 — each story's ceiling is the floor
  above; the top slab is the roof deck under the cornice). Slabs are inset
  2 from walled faces and run full to bay lines on open faces, so neighbours
  meet without overlap. Every window and glazed door is inset 1 voxel: the
  opening is punched through the outer wall voxel and the glass/frame/
  shutters sit 1 deep, a real 1-deep reveal, not a painted-on face.
  NO LETTERING anywhere (mirror-text lesson): the sign band is blank.

PARTS (18): 5 ground + 4 upper + 2 cornice + 2 parapet + 2 notch pier +
3 roof props. Each is written as its own .vox (work dir, for inspection and
gluing). The preview .vox (bodega-corner-v1.vox) holds TWO assemblies:
  A: square 2x2 bays (24x24), 4 stories + cornice + parapet + roof clutter.
  B: L, 4x3 bays (48x36) minus the NE 2x2 quadrant = 8 bays, same height.
     The shopfront bay faces the notch courtyard; the notch is closed by
     the pier tile stack. Gap between buildings ~12 voxels.
"""

PALETTE = [
    ("plaster",      (198, 162, 102)),  # 1  ochre weathered plaster
    ("plaster_dark", (156, 122,  76)),  # 2  exposed / shadow plaster
    ("teal",         (104, 158, 150)),  # 3  trim bands, shutters, sign band
    ("teal_dark",    ( 68, 110, 104)),  # 4  shutter slats
    ("stone",        (172, 164, 148)),  # 5  columns, arcade, sills
    ("stone_dark",   (124, 116, 100)),  # 6  floor strips
    ("wood",         (128,  94,  62)),  # 7  counter, shelves, crates, doors
    ("wood_dark",    ( 86,  62,  40)),  # 8
    ("iron",         ( 56,  58,  64)),  # 9  railings, antenna, brackets
    ("iron_dark",    ( 32,  34,  40)),  # 10
    ("glass",        (110, 142, 152)),  # 11 jars
    ("glass_dark",   ( 38,  54,  68)),  # 12 window dark
    ("sack",         (178, 154, 110)),  # 13 burlap sacks
    ("awn_a",        (140, 190, 182)),  # 14 awning stripe (teal)
    ("awn_b",        (238, 232, 218)),  # 15 awning stripe (cream)
    ("tinaco",       ( 40,  40,  46)),  # 16 black water tanks
    ("rust",         (150,  88,  52)),  # 17 weathering streaks
    ("coping",       (208, 202, 192)),  # 18 cornice / parapet coping
    ("roof",         (102, 104, 100)),  # 19 roof slab grey
    ("wood_floor",   (150, 112,  74)),  # 20 upper floor planks
    # town expansion (bodega_town_v1.py), appended so slots 1-20 never move
    ("tile",         (172,  86,  58)),  # 21 terracotta roof tile
    ("tile_dark",    (128,  62,  44)),  # 22 tile course shadow, ridge
    ("corr",         (150, 152, 148)),  # 23 corrugated sheet (galvanized)
    ("corr_dark",    (112, 114, 112)),  # 24 corrugation trough
    ("pier",         (160, 158, 150)),  # 25 pier concrete
    ("pier_dark",    (112, 110, 104)),  # 26 pier kerb / wet concrete
    ("rubber",       ( 30,  30,  32)),  # 27 tyre fenders
    ("bronze",       (110,  92,  60)),  # 28 statue
    ("bronze_dark",  ( 78,  64,  44)),  # 29
    ("red",          (180,  52,  44)),  # 30 star, flag
    ("water",        ( 70, 130, 150)),  # 31 fountain water
    ("leaf",         ( 70, 118,  58)),  # 32 palm fronds
    ("leaf_dark",    ( 48,  86,  44)),  # 33
    ("trunk",        (120, 100,  76)),  # 34 palm trunk
    ("soil",         ( 88,  66,  48)),  # 35 planter soil
    ("crane",        (204, 160,  52)),  # 36 crane yellow
    ("lamp",         (240, 220, 160)),  # 37 lamp glass
    ("art_face",     (202, 166, 106)),  # 38 blank-art reserve (#308): near-plaster,
                                        # exactly separable from plaster (198,162,102).
                                        # Unassigned it renders as wall plaster (note 1);
                                        # the game routes it to the board material by colour.
]

C = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}


# ---------------------------------------------------------------- material variants
# Geometry builders always emit canonical (bodega-skin) color names; each
# variant remaps a subset to variant colors appended to the palette. The
# "mural" skin additionally gets painted pink patches per part. Mural art
# itself is not voxels: the game paints it onto open wall with a texture
# (kkolk/strike-bay#308). New skins only — geometry
# untouched.

VARIANT_EXTRA = {
    "cement": [
        ("concrete",       (170, 169, 161)),  # 39 drab bare concrete
        ("concrete_dark",  (131, 130, 122)),  # 40
        ("trim_gray",      (146, 145, 137)),  # 41 weathered gray trim
        ("trim_gray_dark", (106, 105,  97)),  # 42
        ("awn_gray",       (148, 146, 138)),  # 43 faded awning stripe
        ("awn_offwhite",   (210, 206, 196)),  # 44
        ("art_concrete",   (174, 173, 165)),  # 45 blank-art reserve, near-concrete
    ],
    "brick": [
        ("brick",           (150,  88,  64)),  # 39 exposed red-brown brick
        ("brick_dark",      (112,  62,  46)),  # 40 mortar shadow
        ("trim_white",      (219, 213, 199)),  # 41 faded off-white painted trim
        ("trim_white_dark", (171, 165, 151)),  # 42
        ("awn_faded_teal",  (120, 150, 144)),  # 43 sun-bleached canvas
        ("awn_faded_cream", (213, 203, 183)),  # 44
        ("art_brick",       (154,  92,  68)),  # 45 blank-art reserve, near-brick
    ],
    "mural": [
        ("turquoise",      (126, 198, 190)),  # 39 flagship turquoise plaster
        ("patch_concrete", (158, 148, 134)),  # 40 exposed concrete under paint
        ("patch_pink",     (234, 174, 172)),  # 41 faded coral-pink paint patches
        ("art_turquoise",  (130, 202, 194)),  # 42 blank-art reserve, near-turquoise
    ],
}

VARIANT_REMAP = {
    "cement": {"plaster": "concrete", "plaster_dark": "concrete_dark",
               "teal": "trim_gray", "teal_dark": "trim_gray_dark",
               "awn_a": "awn_gray", "awn_b": "awn_offwhite", "art_face": "art_concrete"},
    "brick": {"plaster": "brick", "plaster_dark": "brick_dark",
              "teal": "trim_white", "teal_dark": "trim_white_dark",
              "awn_a": "awn_faded_teal", "awn_b": "awn_faded_cream", "art_face": "art_brick"},
    "mural": {"plaster": "turquoise", "plaster_dark": "patch_concrete",
              "art_face": "art_turquoise"},
}

VARIANTS = ("bodega", "cement", "brick", "mural")


def variant_palette(name):
    """Full (name, rgb) palette for a variant: base + variant extras."""
    if name == "bodega":
        return list(PALETTE)
    return list(PALETTE) + list(VARIANT_EXTRA[name])


def variant_index(name):
    """(palette, name->index, canonical-index->variant-index remap)."""
    pal = variant_palette(name)
    idx = {n: i + 1 for i, (n, _) in enumerate(pal)}
    base = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}
    rmap = {base[c]: idx[v] for c, v in VARIANT_REMAP.get(name, {}).items()}
    return pal, idx, rmap


def apply_variant(part, variant):
    """Remap a canonical part dict to variant color indices."""
    if variant == "bodega":
        return dict(part)
    _, _, rmap = variant_index(variant)
    return {(x, y, z): rmap.get(ci, ci) for (x, y, z), ci in part.items()}


def _hash2(a, b, salt=0):
    """Deterministic 0..99 hash for weathering/patch decisions."""
    h = (a * 73856093) ^ (b * 19349663) ^ (salt * 83492791)
    return (h & 0x7fffffff) % 100


def mural_patches(part, vidx):
    """Deterministic faded coral-pink paint patches on exterior wall faces
    (mural skin only). Recolors turquoise wall voxels on the outer face
    layers (y==0 south, x==0 west) in 4x4-voxel blotches. Trim, glass,
    stone, shutters and interiors are never turquoise, so never touched."""
    tq = vidx["turquoise"]
    pink = vidx["patch_pink"]
    out = {}
    for (x, y, z), ci in part.items():
        if ci == tq and (y == 0 or x == 0):
            if _hash2(x // 4, z // 4, salt=7) < 42:
                out[(x, y, z)] = pink
                continue
        out[(x, y, z)] = ci
    return out


# ---------------------------------------------------------------- builders
def box(d, x0, x1, y0, y1, z0, z1, ci):
    """Inclusive-exclusive box fill. ci is a 1-based color index."""
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                d[(x, y, z)] = ci


def B(vox, x0, x1, y0, y1, z0, z1, name):
    box(vox, x0, x1, y0, y1, z0, z1, C[name])


def rot(vox, k):
    """Rotate k*90 deg CCW about the bay centre (5.5,5.5). S->E->N->W.
    Voxel-exact: (i,j) -> (11-j, i) for the 12x12 bay."""
    for _ in range(k % 4):
        vox = {(11 - y, x, z): ci for (x, y, z), ci in vox.items()}
    return vox


def place(world, part, bx, by, bz, k=0, ox=0, oy=0):
    """Place a part: rotate k*90 CCW, then translate to bay (bx,by) + z + offset."""
    p = rot(part, k)
    for (x, y, z), ci in p.items():
        world[(x + bx * 12 + ox, y + by * 12 + oy, z + bz)] = ci


# ---------------------------------------------------------------- validation
def floater_sweep(vox):
    """6-connectivity components; return those NOT touching min-z."""
    if not vox:
        return []
    base = min(z for _, _, z in vox)
    seen = set()
    bad = []
    for seed in vox:
        if seed in seen:
            continue
        comp = set()
        stack = [seed]
        seen.add(seed)
        touches = False
        while stack:
            p = stack.pop()
            comp.add(p)
            if p[2] == base:
                touches = True
            x, y, z = p
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                      (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in vox and q not in seen:
                    seen.add(q)
                    stack.append(q)
        if not touches:
            bad.append(comp)
    total = sum(len(c) for c in bad)
    print(f"floater_sweep: base z={base}, {len(bad)} bad components "
          f"({total} voxels)")
    return bad


# ---------------------------------------------------------------- .vox writer
def write_vox(path, vox, palette):
    import struct
    fmt_i = "<i"
    fmt_ii = "<ii"
    fmt_iii = "<iii"

    def chunk(cid, content, children=b""):
        return cid + struct.pack(fmt_ii, len(content), len(children)) + content + children

    xs = [p[0] for p in vox]
    ys = [p[1] for p in vox]
    zs = [p[2] for p in vox]
    sx, sy, sz = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) + 1
    xoff, yoff = -min(xs), -min(ys)
    size_content = struct.pack(fmt_iii, sx, sy, sz)
    xyzi = struct.pack(fmt_i, len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("BBBB", x + xoff, y + yoff, z, ci)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in palette)
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(palette))
    main_children = chunk(b"SIZE", size_content) + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)
    with open(path, "wb") as f:
        f.write(b"VOX ")
        f.write(struct.pack(fmt_i, 150))
        f.write(chunk(b"MAIN", b"", main_children))
    print(f"wrote {path} ({len(vox)} voxels)")


# ---------------------------------------------------------------- previews
def render_preview(path, vox, palette, scale=2):
    from PIL import Image, ImageDraw
    xs = [p[0] for p in vox]
    ys = [p[1] for p in vox]
    zs = [p[2] for p in vox]
    W2, H2, ZH = 0.8660254, 0.5, 1.0

    def proj(x, y, z):
        return ((x - y) * W2 * scale, ((x + y) * H2 - z * ZH) * scale)

    corners = [(min(xs), min(ys), min(zs)), (max(xs), min(ys), min(zs)),
               (min(xs), max(ys), min(zs)), (max(xs), max(ys), min(zs)),
               (min(xs), min(ys), max(zs)), (max(xs), max(ys), max(zs))]
    px = [proj(*c)[0] for c in corners]
    py = [proj(*c)[1] for c in corners]
    ox, oy = -min(px) + 20 * scale, -min(py) + 20 * scale
    img = Image.new("RGB", (int(max(px) - min(px)) + 40 * scale, int(max(py) - min(py)) + 40 * scale),
                    (13, 20, 30))
    dr = ImageDraw.Draw(img)
    shades = {}
    for i, (_, (r, g, b)) in enumerate(palette):
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
                   proj(x + 1, y, z + 1), proj(x, y + 1, z + 1)]
            dr.polygon([(px_ + ox, py_ + oy) for px_, py_ in pts], fill=right)
    img.save(path)
    print(f"wrote {path} {img.size}")


def render_slice(path, vox, palette, z):
    from PIL import Image
    xs = [p[0] for p in vox]
    ys = [p[1] for p in vox]
    img = Image.new("RGB", ((max(xs) - min(xs) + 1) * 2, (max(ys) - min(ys) + 1) * 2), (13, 20, 30))
    px = img.load()
    xoff, yoff = -min(xs), -min(ys)
    for (x, y, zz), ci in vox.items():
        if zz == z:
            r, g, b = palette[ci - 1][1]
            for dx in range(2):
                for dy in range(2):
                    px[(x + xoff) * 2 + dx, (y + yoff) * 2 + dy] = (r, g, b)
    img.save(path)
    print(f"wrote {path} {img.size}")


# ---------------------------------------------------------------- shared bits
def cut(vox, x0, x1, y0, y1, z0, z1):
    """Punch an opening: delete voxels in the inclusive-exclusive box."""
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                vox.pop((x, y, z), None)


def ground_slab(vox):
    """Full-bay ground slab, z 0..1, stone."""
    B(vox, 0, 12, 0, 12, 0, 1, "stone_dark")


def story_slab(vox, south=True, west=False):
    """Upper floor slab at local z 9..10 (this story's ceiling = the floor
    above), wood plank. Inset 2 from walled faces; runs full to bay lines on
    open faces so neighbouring slabs meet without overlap."""
    B(vox, 2 if west else 0, 12, 2 if south else 0, 12, 9, 10, "wood_floor")


def peel(vox, patches):
    """Deterministic plaster_dark peel patches on the front face (y 0..1)."""
    for (x, z0, w, h) in patches:
        B(vox, x, x + w, 0, 1, z0, z0 + h, "plaster_dark")


def rust_streak(vox, x, z_top, length):
    B(vox, x, x + 1, 0, 1, z_top - length, z_top, "rust")


def awning(vox, x0=1, x1=11):
    """Torn striped awning, 3 proud of the face. z local 6..8."""
    B(vox, 2, 3, -1, 0, 7, 8, "iron")
    B(vox, 9, 10, -1, 0, 7, 8, "iron")
    i = 0
    for x in range(x0, x1, 2):
        col = "awn_a" if (i % 2 == 0) else "awn_b"
        B(vox, x, min(x + 2, x1), -2, 0, 7, 8, col)
        if (x + i) % 4 != 0:  # torn outer edge (shares z with inner strip)
            B(vox, x, min(x + 2, x1), -4, -2, 6, 8, col)
        i += 1


def sign_band(vox, x0=0, x1=12):
    """BLANK teal sign band, front layer, z 8..9. No lettering, ever."""
    B(vox, x0, x1, 0, 1, 8, 9, "teal")


def shelf_unit(vox, x0, x1, y0=9):
    """Freestanding shelf unit, 2 deep, with jars."""
    B(vox, x0, x1, y0 + 1, y0 + 2, 0, 6, "wood_dark")  # back panel
    for sz in (1, 3, 5):
        B(vox, x0, x1, y0, y0 + 2, sz, sz + 1, "wood")
        for jx in range(x0, x1):
            if (jx + sz) % 3 != 0:
                B(vox, jx, jx + 1, y0, y0 + 1, sz + 1, sz + 2,
                  "glass" if (jx % 2) else "glass_dark")


def barrel(vox, x0, y0):
    B(vox, x0, x0 + 2, y0, y0 + 2, 0, 1, "wood")
    B(vox, x0, x0 + 2, y0, y0 + 2, 1, 2, "wood_dark")
    B(vox, x0, x0 + 2, y0, y0 + 2, 2, 3, "wood")


def shutter_window(vox, x0, x1, s, sill=True):
    """Shuttered window inset 1 voxel: the opening is punched through the
    outer wall voxel (y 0..1) and the shutters sit 1 deep (y 1..2), giving a
    1-deep plaster reveal instead of a painted-on face. z s+2..s+7."""
    cut(vox, x0, x1, 0, 1, s + 2, s + 7)
    B(vox, x0, x1, 1, 2, s + 2, s + 7, "teal")
    B(vox, x0, x1, 1, 2, s + 4, s + 5, "teal_dark")  # slat line
    if sill:
        B(vox, x0 - 1, x1 + 1, -1, 2, s + 1, s + 2, "stone")


def band(vox, s, x0=0, x1=12):
    """Teal trim band, front layer, z s+8..s+9."""
    B(vox, x0, x1, 0, 1, s + 8, s + 9, "teal")


# ---------------------------------------------------------------- ground story (local z 0..10)
def g_arcade(lite=False):
    """Arcade bay, faces S. 2 arches, blank sign band, awning, shop interior."""
    v = {}
    ground_slab(v)
    story_slab(v)
    B(v, 0, 12, -1, 2, 0, 1, "stone")          # threshold, proud 1
    for px0, px1 in ((0, 1), (5, 7), (11, 12)):  # piers (half at bay edges)
        B(v, px0, px1, 0, 2, 1, 8, "stone")
    for ax in (1, 7):                           # stepped arch springs
        B(v, ax, ax + 1, 0, 2, 7, 8, "stone")
        B(v, ax + 3, ax + 4, 0, 2, 7, 8, "stone")
    B(v, 0, 12, 1, 2, 8, 9, "stone")            # spandrel
    sign_band(v)                                 # BLANK teal band
    B(v, 0, 12, 0, 2, 9, 10, "stone")           # entablature
    awning(v)
    peel(v, [(8, 9, 2, 1)])
    if lite:
        return v
    # shop interior (room at 6..10, 2..6)
    B(v, 1, 5, 9, 11, 0, 3, "wood")             # counter
    B(v, 1, 5, 9, 11, 3, 4, "wood_dark")
    shelf_unit(v, 1, 4)                          # shelves + jars
    B(v, 1, 3, 6, 8, 0, 2, "sack")              # sacks
    B(v, 1, 2, 6, 7, 2, 3, "sack")
    barrel(v, 3, 4)                              # barrel
    B(v, 4, 6, 2, 4, 0, 2, "wood")              # crates
    return v


def g_arcade_corner(lite=False):
    """Arcade corner, faces S+W. Corner column whole; awning on S face."""
    v = {}
    ground_slab(v)
    story_slab(v, south=True, west=True)
    B(v, -1, 2, -1, 2, 0, 1, "stone")          # corner base, proud both faces
    B(v, 0, 2, 0, 2, 1, 10, "stone")           # corner column whole
    B(v, 0, 2, 0, 2, 8, 9, "coping")           # capital course
    # south arcade (column replaces west half-pier)
    B(v, 2, 12, -1, 2, 0, 1, "stone")
    for px0, px1 in ((5, 7), (11, 12)):
        B(v, px0, px1, 0, 2, 1, 8, "stone")
    for ax in (2, 7):
        B(v, ax, ax + 1, 0, 2, 7, 8, "stone")
        B(v, ax + 2, ax + 3, 0, 2, 7, 8, "stone")
    B(v, 2, 12, 1, 2, 8, 9, "stone")
    B(v, 2, 12, 0, 1, 8, 9, "teal")            # BLANK sign band
    B(v, 2, 12, 0, 2, 9, 10, "stone")
    awning(v, 3, 11)
    # west arcade (mirror)
    B(v, -1, 2, 2, 12, 0, 1, "stone")
    for py0, py1 in ((5, 7), (11, 12)):
        B(v, 0, 2, py0, py1, 1, 8, "stone")
    for ay in (2, 7):
        B(v, 0, 2, ay, ay + 1, 7, 8, "stone")
        B(v, 0, 2, ay + 2, ay + 3, 7, 8, "stone")
    B(v, 1, 2, 2, 12, 8, 9, "stone")
    B(v, 0, 1, 2, 12, 8, 9, "teal")            # BLANK sign band
    B(v, 0, 2, 2, 12, 9, 10, "stone")
    if lite:
        return v
    # interior
    B(v, 3, 7, 9, 11, 0, 3, "wood")            # counter
    B(v, 3, 7, 9, 11, 3, 4, "wood_dark")
    shelf_unit(v, 8, 11)
    B(v, 3, 5, 6, 8, 0, 2, "sack")
    B(v, 8, 10, 7, 9, 0, 2, "sack")
    barrel(v, 3, 3)
    return v


def g_shopfront(lite=False):
    """Open shopfront bay, faces S. Wide opening, wood lintel, sign band."""
    v = {}
    ground_slab(v)
    story_slab(v)
    B(v, 0, 12, -1, 2, 0, 1, "stone")
    B(v, 0, 2, 0, 2, 1, 9, "stone")            # side piers
    B(v, 10, 12, 0, 2, 1, 9, "stone")
    B(v, 2, 10, 0, 2, 7, 8, "wood_dark")       # lintel
    B(v, 0, 12, 1, 2, 8, 9, "stone")
    sign_band(v)                                 # BLANK
    B(v, 0, 12, 0, 2, 9, 10, "stone")
    awning(v)
    if lite:
        return v
    # interior
    B(v, 2, 6, 9, 11, 0, 3, "wood")            # counter
    B(v, 2, 6, 9, 11, 3, 4, "wood_dark")
    shelf_unit(v, 7, 11)
    B(v, 2, 4, 6, 8, 0, 2, "sack")
    barrel(v, 8, 6)
    B(v, 4, 6, 3, 5, 0, 2, "wood")              # crates
    return v


def g_stair(lite=False):
    """Entry bay to upper floors, faces S. Wood door, barred transom, steps.
    Lite keeps the steps (lite strips shop dressing, never stairs)."""
    v = {}
    ground_slab(v)
    story_slab(v)
    B(v, 0, 12, -1, 2, 0, 1, "stone")
    B(v, 0, 12, 0, 2, 0, 10, "plaster")
    B(v, 2, 3, 0, 2, 1, 8, "stone")            # door surround
    B(v, 7, 8, 0, 2, 1, 8, "stone")
    B(v, 2, 8, 0, 2, 7, 8, "stone")
    cut(v, 3, 7, 0, 1, 1, 7)                   # punch outer voxel
    B(v, 3, 7, 1, 2, 1, 7, "wood")             # door leaf, 1 deep
    B(v, 3, 7, 1, 2, 2, 3, "wood_dark")        # panels
    B(v, 3, 7, 1, 2, 5, 6, "wood_dark")
    B(v, 6, 7, 1, 2, 3, 4, "iron_dark")        # handle
    # barred transom window, inset 1
    cut(v, 8, 11, 0, 1, 4, 6)
    B(v, 8, 11, 1, 2, 4, 6, "glass_dark")
    B(v, 9, 10, 1, 2, 4, 6, "iron")
    B(v, 8, 11, 1, 2, 5, 6, "iron")
    B(v, 8, 12, -1, 2, 3, 4, "stone")          # sill
    # interior steps up (each lands on the last)
    B(v, 2, 6, 8, 10, 0, 1, "wood")
    B(v, 2, 6, 7, 9, 1, 2, "wood")
    B(v, 2, 6, 6, 8, 2, 3, "wood")
    peel(v, [(9, 8, 2, 1)])
    return v


def g_plain(lite=False):
    """Plain back/side bay, faces S. Shuttered window + wood back door."""
    v = {}
    ground_slab(v)
    story_slab(v)
    B(v, 0, 12, -1, 2, 0, 1, "stone")
    B(v, 0, 12, 0, 2, 0, 10, "plaster")
    cut(v, 4, 7, 0, 1, 3, 6)                   # punch outer voxel
    B(v, 4, 7, 1, 2, 3, 6, "teal")             # closed shutters, 1 deep
    B(v, 4, 7, 1, 2, 4, 5, "teal_dark")
    B(v, 3, 8, -1, 2, 2, 3, "stone")           # sill
    cut(v, 8, 10, 0, 1, 1, 5)
    B(v, 8, 10, 1, 2, 1, 5, "wood")            # back door, 1 deep
    B(v, 8, 10, 1, 2, 2, 3, "wood_dark")
    B(v, 7, 11, 0, 2, 5, 6, "stone")           # lintel
    peel(v, [(1, 6, 2, 2), (9, 7, 2, 1)])
    rust_streak(v, 4, 2, 2)
    if not lite:
        B(v, 2, 4, 8, 10, 0, 2, "wood")        # crates
        B(v, 8, 10, 8, 10, 0, 2, "sack")       # sacks
    return v


# ---------------------------------------------------------------- upper stories (local z 0..10, placed at s)
def u_shutter():
    """Shutter bay, faces S. 2 closed-shutter windows + teal band."""
    v = {}
    story_slab(v)
    B(v, 0, 12, 0, 2, 0, 10, "plaster")
    shutter_window(v, 2, 5, 0)
    shutter_window(v, 7, 10, 0)
    B(v, 5, 6, 0, 1, 5, 8, "rust")  # streak under the band
    band(v, 0)
    peel(v, [(0, 2, 2, 2), (10, 5, 2, 1)])
    return v


def u_balcony():
    """Balcony bay, faces S. French door + wrought-iron balcony."""
    v = {}
    story_slab(v)
    B(v, 0, 12, 0, 2, 0, 10, "plaster")
    cut(v, 4, 8, 0, 1, 0, 7)                   # punch outer voxel
    B(v, 4, 8, 1, 2, 0, 7, "teal")             # French door frame, 1 deep
    B(v, 5, 7, 1, 2, 1, 6, "glass_dark")       # glazing
    B(v, 5, 7, 1, 2, 3, 4, "teal")             # mid bar
    B(v, 3, 10, -1, 2, 0, 1, "stone")          # door sill
    B(v, 3, 10, -2, 0, -1, 0, "stone")         # balcony slab (2 proud)
    for px in (3, 5, 7, 9):                    # railing posts, even 2-splits
        B(v, px, px + 1, -2, -1, 0, 3, "iron")
    B(v, 3, 10, -2, -1, 2, 3, "iron")          # top rail
    # (mid rail removed per viewer diff #1, 2026-10-05 — user cut it in edit mode)
    B(v, 3, 4, -2, 0, 2, 3, "iron")           # side rails
    B(v, 9, 10, -2, 0, 2, 3, "iron")
    B(v, 3, 4, -1, 0, -3, -1, "stone")        # corbels
    B(v, 9, 10, -1, 0, -3, -1, "stone")
    shutter_window(v, 1, 3, 0)                 # flanking windows
    shutter_window(v, 9, 11, 0)
    B(v, 3, 4, 0, 1, 5, 8, "rust")  # streak under the band
    band(v, 0)
    peel(v, [(0, 6, 1, 1)])
    return v


def u_barred():
    """Barred-window bay, faces S. Iron bars + folded-open shutters."""
    v = {}
    story_slab(v)
    B(v, 0, 12, 0, 2, 0, 10, "plaster")
    for x0 in (2, 7):
        cut(v, x0, x0 + 3, 0, 1, 2, 7)            # punch outer voxel
        B(v, x0, x0 + 3, 1, 2, 2, 7, "glass_dark")  # glazing, 1 deep
        B(v, x0 + 1, x0 + 2, 1, 2, 2, 7, "iron")   # bars
        B(v, x0, x0 + 3, 1, 2, 4, 5, "iron")
        B(v, x0 - 2, x0, 0, 1, 2, 7, "teal")       # folded-open shutter
        B(v, x0 - 2, x0, 0, 1, 4, 5, "teal_dark")   # (surface-mounted on face)
        B(v, x0 - 1, x0 + 4, -1, 2, 1, 2, "stone")  # sill
    B(v, 6, 7, 0, 1, 5, 8, "rust")  # streak under the band
    B(v, 10, 12, 0, 1, 2, 7, "teal")           # right shutter, 2nd window
    B(v, 10, 12, 0, 1, 4, 5, "teal_dark")
    band(v, 0)
    peel(v, [(5, 1, 2, 2)])
    return v


def u_corner():
    """Upper corner, faces S+W. Corner column whole, shuttered windows."""
    v = {}
    story_slab(v, south=True, west=True)
    B(v, 0, 2, 0, 2, 0, 10, "plaster")        # corner column whole
    B(v, 2, 12, 0, 2, 0, 10, "plaster")       # south wall
    B(v, 0, 2, 2, 12, 0, 10, "plaster")       # west wall
    shutter_window(v, 6, 9, 0)                 # south window
    cut(v, 0, 1, 6, 9, 2, 7)                  # west opening, punch outer voxel
    B(v, 1, 2, 6, 9, 2, 7, "teal")            # west shutters, 1 deep
    B(v, 1, 2, 6, 9, 4, 5, "teal_dark")
    B(v, -1, 2, 5, 10, 1, 2, "stone")         # west sill
    B(v, 4, 5, 0, 1, 5, 8, "rust")  # streak under the band
    band(v, 0, 2, 12)                          # south band
    B(v, 0, 1, 2, 12, 8, 9, "teal")           # west band
    peel(v, [(3, 2, 2, 1)])
    return v


# ---------------------------------------------------------------- top (cornice local z 0..2 @40; parapet local z 0..5 @42)
def top_cornice():
    v = {}
    B(v, 0, 12, -1, 2, 0, 1, "coping")
    for x in range(0, 12, 4):                  # dentil course
        B(v, x, x + 2, -1, 2, 1, 2, "coping")
        B(v, x + 2, x + 4, -1, 2, 1, 2, "stone_dark")
    return v


def top_cornice_corner():
    v = {}
    B(v, -1, 2, -1, 2, 0, 2, "coping")        # corner block
    B(v, 2, 12, -1, 2, 0, 1, "coping")
    for x in range(2, 12, 4):
        B(v, x, x + 2, -1, 2, 1, 2, "coping")
        B(v, x + 2, min(x + 4, 12), -1, 2, 1, 2, "stone_dark")
    B(v, -1, 2, 2, 12, 0, 1, "coping")
    for y in range(2, 12, 4):
        B(v, -1, 2, y, y + 2, 1, 2, "coping")
        B(v, -1, 2, y + 2, min(y + 4, 12), 1, 2, "stone_dark")
    return v


def roof_parapet():
    v = {}
    B(v, 0, 12, 0, 12, 0, 1, "roof")          # slab, full bay
    B(v, 0, 12, 0, 2, 1, 4, "plaster")        # parapet
    B(v, 0, 12, -1, 2, 4, 5, "coping")        # coping, proud 1
    return v


def roof_parapet_corner():
    v = {}
    B(v, 0, 12, 0, 12, 0, 1, "roof")
    B(v, 0, 2, 0, 2, 1, 4, "plaster")
    B(v, 2, 12, 0, 2, 1, 4, "plaster")
    B(v, 0, 2, 2, 12, 1, 4, "plaster")
    B(v, -1, 2, -1, 2, 4, 5, "coping")
    B(v, 2, 12, -1, 2, 4, 5, "coping")
    B(v, -1, 2, 2, 12, 4, 5, "coping")
    return v


def notch_pier():
    """2x2 inside-corner pier for the L notch. One story."""
    v = {}
    B(v, 0, 2, 0, 2, 0, 1, "stone_dark")
    B(v, 0, 2, 0, 2, 1, 9, "stone")
    B(v, 0, 2, 0, 2, 9, 10, "coping")
    return v


def notch_pier_cap():
    """Notch pier top termination, local z 0..7 @ bz=40."""
    v = {}
    B(v, 0, 2, 0, 2, 0, 2, "coping")
    B(v, 0, 2, 0, 2, 2, 3, "roof")
    B(v, 0, 2, 0, 2, 3, 6, "plaster")
    B(v, 0, 2, 0, 2, 6, 7, "coping")
    return v


# ---------------------------------------------------------------- roof props (base z=0)
def prop_tinaco():
    v = {}
    for lx in (0, 4):
        for ly in (0, 4):
            B(v, lx, lx + 1, ly, ly + 1, 0, 2, "iron")
    B(v, 2, 3, 2, 3, 0, 2, "iron_dark")       # downpipe
    B(v, 0, 5, 0, 5, 2, 6, "tinaco")          # tank
    B(v, 1, 2, 0, 1, 2, 6, "rust")            # rust streak
    B(v, 0, 5, 0, 5, 6, 7, "tinaco")          # lid
    return v


def prop_antenna():
    v = {}
    B(v, 2, 3, 0, 1, 0, 9, "iron")            # mast
    B(v, 0, 5, 0, 1, 7, 8, "iron")            # crossbars
    B(v, 1, 4, 0, 1, 8, 9, "iron")
    B(v, 2, 3, 0, 1, 9, 10, "iron_dark")      # tip
    return v


def prop_crates():
    v = {}
    B(v, 0, 2, 0, 2, 0, 2, "wood")
    B(v, 2, 4, 0, 2, 0, 2, "wood")
    B(v, 1, 3, 0, 2, 2, 4, "wood")
    B(v, 0, 2, 0, 1, 0, 2, "wood_dark")       # batten hints
    B(v, 2, 4, 1, 2, 0, 2, "wood_dark")
    return v


# ---------------------------------------------------------------- assemblies
def build_square(w, ox, oy):
    """2x2 bays (24x24), 4 stories + cornice + parapet + roof clutter."""
    gc = PARTS["bodega-g-arcade-corner"]
    uc = PARTS["bodega-u-corner"]
    cc = PARTS["bodega-top-cornice-corner"]
    pc = PARTS["bodega-roof-parapet-corner"]
    place(w, gc, 0, 0, 0, 0, ox, oy)
    place(w, gc, 1, 0, 0, 1, ox, oy)
    place(w, gc, 1, 1, 0, 2, ox, oy)
    place(w, gc, 0, 1, 0, 3, ox, oy)
    for s in (10, 20, 30):
        place(w, uc, 0, 0, s, 0, ox, oy)
        place(w, uc, 1, 0, s, 1, ox, oy)
        place(w, uc, 1, 1, s, 2, ox, oy)
        place(w, uc, 0, 1, s, 3, ox, oy)
    for (bx, by, k) in ((0, 0, 0), (1, 0, 1), (1, 1, 2), (0, 1, 3)):
        place(w, cc, bx, by, 40, k, ox, oy)
        place(w, pc, bx, by, 42, k, ox, oy)
    place(w, PARTS["bodega-prop-tinaco"], 0, 0, 43, 0, ox + 4, oy + 5)
    place(w, PARTS["bodega-prop-tinaco"], 0, 0, 43, 0, ox + 15, oy + 14)
    place(w, PARTS["bodega-prop-antenna"], 0, 0, 43, 0, ox + 17, oy + 4)
    place(w, PARTS["bodega-prop-crates"], 0, 0, 43, 0, ox + 5, oy + 16)


def build_L(w, ox, oy):
    """4x3 bays minus NE 2x2 quadrant = 8 bays, same height. Notch at local
    x 24..48, y 12..36; shopfront faces the notch courtyard."""
    P = PARTS
    G = [(0, 0, "bodega-g-arcade-corner", 0),
         (1, 0, "bodega-g-arcade", 0),
         (2, 0, "bodega-g-plain", 2),
         (3, 0, "bodega-g-arcade-corner", 2),
         (0, 1, "bodega-g-stair", 3),
         (1, 1, "bodega-g-shopfront", 1),
         (0, 2, "bodega-g-arcade-corner", 3),
         (1, 2, "bodega-g-arcade-corner", 2)]
    U1 = [(0, 0, "bodega-u-corner", 0), (1, 0, "bodega-u-balcony", 0),
          (2, 0, "bodega-u-shutter", 2), (3, 0, "bodega-u-corner", 2),
          (0, 1, "bodega-u-shutter", 3), (1, 1, "bodega-u-barred", 1),
          (0, 2, "bodega-u-corner", 3), (1, 2, "bodega-u-corner", 2)]
    U2 = [(0, 0, "bodega-u-corner", 0), (1, 0, "bodega-u-shutter", 0),
          (2, 0, "bodega-u-barred", 2), (3, 0, "bodega-u-corner", 2),
          (0, 1, "bodega-u-balcony", 3), (1, 1, "bodega-u-shutter", 1),
          (0, 2, "bodega-u-corner", 3), (1, 2, "bodega-u-corner", 2)]
    U3 = [(0, 0, "bodega-u-corner", 0), (1, 0, "bodega-u-barred", 0),
          (2, 0, "bodega-u-shutter", 2), (3, 0, "bodega-u-corner", 2),
          (0, 1, "bodega-u-shutter", 3), (1, 1, "bodega-u-balcony", 1),
          (0, 2, "bodega-u-corner", 3), (1, 2, "bodega-u-corner", 2)]
    for bx, by, name, k in G:
        place(w, P[name], bx, by, 0, k, ox, oy)
    for s, U in ((10, U1), (20, U2), (30, U3)):
        for bx, by, name, k in U:
            place(w, P[name], bx, by, s, k, ox, oy)
    for bx, by, name, k in U3:  # top follows the top-story face plan
        if "corner" in name:
            place(w, P["bodega-top-cornice-corner"], bx, by, 40, k, ox, oy)
            place(w, P["bodega-roof-parapet-corner"], bx, by, 42, k, ox, oy)
        else:
            place(w, P["bodega-top-cornice"], bx, by, 40, k, ox, oy)
            place(w, P["bodega-roof-parapet"], bx, by, 42, k, ox, oy)
    for s in (0, 10, 20, 30):  # notch pier stack at local (22,10)
        place(w, P["bodega-notch-pier"], 0, 0, s, 0, ox + 22, oy + 10)
    place(w, P["bodega-notch-pier-cap"], 0, 0, 40, 0, ox + 22, oy + 10)
    place(w, P["bodega-prop-tinaco"], 0, 0, 43, 0, ox + 8, oy + 6)
    place(w, P["bodega-prop-antenna"], 0, 0, 43, 0, ox + 30, oy + 4)
    place(w, P["bodega-prop-crates"], 0, 0, 43, 0, ox + 6, oy + 26)
    place(w, P["bodega-prop-tinaco"], 0, 0, 43, 0, ox + 14, oy + 20)


def variant_py_source(variant):
    """Generator source with the PALETTE literal swapped for the variant
    palette, so the viewer's static PALETTE parse derives the right color
    names. Saved as bodega-corner-{variant}-v1.py for the upload zip."""
    import re
    src = open(__file__).read()
    pal = variant_palette(variant)
    lines = ["PALETTE = ["]
    for n, (r, g, b) in pal:
        lines.append(f'    ("{n}",'.ljust(22) + f"({r}, {g}, {b})),")
    lines.append("]")
    new, n = re.subn(r"^PALETTE = \[.*?\n\]", "\n".join(lines),
                      src, count=1, flags=re.S | re.M)
    assert n == 1, "PALETTE literal not found for variant .py"
    return new


def component_count(vox):
    """Number of 6-connected components."""
    seen = set()
    n = 0
    for seed in vox:
        if seed in seen:
            continue
        n += 1
        stack = [seed]
        seen.add(seed)
        while stack:
            x, y, z = stack.pop()
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                      (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in vox and q not in seen:
                    seen.add(q)
                    stack.append(q)
    return n


# ---------------------------------------------------------------- part builders
BUILDERS = [
    ("bodega-g-arcade", g_arcade),
    ("bodega-g-arcade-corner", g_arcade_corner),
    ("bodega-g-shopfront", g_shopfront),
    ("bodega-g-stair", g_stair),
    ("bodega-g-plain", g_plain),
    ("bodega-u-shutter", u_shutter),
    ("bodega-u-balcony", u_balcony),
    ("bodega-u-barred", u_barred),
    ("bodega-u-corner", u_corner),
    ("bodega-top-cornice", top_cornice),
    ("bodega-top-cornice-corner", top_cornice_corner),
    ("bodega-roof-parapet", roof_parapet),
    ("bodega-roof-parapet-corner", roof_parapet_corner),
    ("bodega-notch-pier", notch_pier),
    ("bodega-notch-pier-cap", notch_pier_cap),
    ("bodega-prop-tinaco", prop_tinaco),
    ("bodega-prop-antenna", prop_antenna),
    ("bodega-prop-crates", prop_crates),
]


# Ground parts with shop dressing take lite=True: slabs, walls and stairs
# only (towns have hundreds of bay-stories; full dressing is ~600 vox per
# bay-story). Every other part has no dressing, so lite is a no-op for it.
LITE_BUILDERS = {"bodega-g-arcade", "bodega-g-arcade-corner",
                 "bodega-g-shopfront", "bodega-g-stair", "bodega-g-plain"}


def make_part(fn, variant, vidx, lite=False, takes_lite=False):
    """One part in a skin: build canonical, (lite), remap, mural patches."""
    v = apply_variant(fn(lite=lite) if takes_lite else fn(), variant)
    if variant == "mural":
        v = mural_patches(v, vidx)
    return v


def write_part(out, fname, v, pal, preview=False):
    """Part .vox (+ optional preview .png). Part files are inspection/gluing
    aids: shift below-base protrusions (balcony slab/corbels) so z starts at
    0; assemblers use the unshifted local frames."""
    import os
    mz = min(z for _, _, z in v)
    wv = {(x, y, z - mz): ci for (x, y, z), ci in v.items()} if mz < 0 else v
    write_vox(os.path.join(out, fname + ".vox"), wv, pal)
    if preview:
        render_preview(os.path.join(out, fname + "_preview.png"), wv, pal,
                       scale=8)


def build_variant(HERE, variant, lite=False, out=None):
    """Build one material variant: 18 part .vox files + the two-assembly
    preview .vox/.png + a stem-matched variant .py for the upload zip.
    lite: lite interiors, files suffixed -lite."""
    import os
    global PARTS
    out = out or HERE
    pal, vidx, _ = variant_index(variant)
    sfx = "-lite" if lite else ""
    stem = ("bodega-corner-v1" if variant == "bodega"
            else f"bodega-corner-{variant}-v1") + sfx
    pstem = "bodega" if variant == "bodega" else f"bodega-{variant}"

    PARTS = {}
    for name, fn in BUILDERS:
        v = make_part(fn, variant, vidx, lite, name in LITE_BUILDERS)
        bad = floater_sweep(v)
        assert not bad, f"{variant}/{name}: {len(bad)} bad components"
        PARTS[name] = v
        write_part(out, f"{pstem}-{name[7:]}{sfx}", v, pal)
        print(f"part {variant}/{name}{sfx}: {len(v)} vox")

    world = {}
    build_square(world, 0, 0)
    build_L(world, 40, 0)
    bad = floater_sweep(world)
    assert not bad, f"{variant}: floaters in assembly"
    xs = [p[0] for p in world]
    ys = [p[1] for p in world]
    zs = [p[2] for p in world]
    print(f"assembly {variant} footprint x {min(xs)}..{max(xs)} "
          f"y {min(ys)}..{max(ys)} z {min(zs)}..{max(zs)}")
    print(f"assembly {variant} total {len(world)} voxels")
    write_vox(os.path.join(out, stem + ".vox"), world, pal)
    render_preview(os.path.join(out, stem + "_preview.png"),
                   world, pal, scale=6)
    for z in (5, 9, 15, 41, 44):
        render_slice(os.path.join(out, f"{stem}_slice_z{z:02d}.png"),
                     world, pal, z)
    # stem-matched generator copy for the upload zip (variant PALETTE, so the
    # viewer's static parse derives the right color names)
    with open(os.path.join(out, stem + ".py"), "w") as f:
        f.write(variant_py_source(variant))
    print(f"variant {variant}: {len(world)} voxels")


def parse_args(argv):
    """[variant ...] [--lite] [--out DIR]; no variant = all four."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("variants", nargs="*", metavar="variant",
                    help=" | ".join(VARIANTS))
    ap.add_argument("--lite", action="store_true",
                    help="lite interiors (slabs + stairs), files suffixed -lite")
    ap.add_argument("--out", help="output dir (default: this script's dir)")
    a = ap.parse_args(argv)
    for v in a.variants:
        if v not in VARIANTS:
            ap.error(f"unknown variant {v!r}")
    a.variants = a.variants or list(VARIANTS)
    return a


if __name__ == "__main__":
    import os
    import sys
    HERE = os.path.dirname(os.path.abspath(__file__))
    args = parse_args(sys.argv[1:])
    if args.out:
        os.makedirs(args.out, exist_ok=True)
    for variant in args.variants:
        print(f"=== variant: {variant}{' (lite)' if args.lite else ''} ===")
        build_variant(HERE, variant, args.lite, args.out)
