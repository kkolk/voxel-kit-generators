#!/usr/bin/env python3
"""Strike Bay MODULAR FACTORY KIT — shared grid contract (v1, 2026-09-28).

Every kit generator imports this module. The numbers below are THE contract;
they are identical for the mill and frame families and are repeated in each
generator's docstring.

GRID
  B = 12   bay width (voxels).  Every module footprint is a whole number of bays.
  S = 10   story height (voxels).
  T = 2    wall thickness (voxels), fixed for both families.
  DEPTH = 24  standard wing depth = 2 bays.  Wall bays are 12 (x) by 24 (y).

ORIGIN / PLACEMENT
  Origin at the footprint's min corner, at ground level, z-up.
  No ground slab, no yard — the game draws those.
  Footprints are half-open boxes [x0,x1) x [y0,y1) x [z0,z1).  A module writes
  ONLY voxels inside its own footprint (one exception: outer corner columns,
  completed whole by the corner/endwall piece — nothing else occupies them).

SEAM RULE (no gaps, no double walls)
  Bay lines sit at multiples of B.  A wall module spanning x in [x0, x0+12)
  writes half-columns (1 voxel wide) at x0..x0+1 and x0+11..x0+12 on each
  walled face; the neighbour writes the complementary half, so the union is
  one full 2-wide column centred on the bay line.  Mill (load-bearing brick)
  has no pilasters: plain wall ends just meet, complementary, no overlap.
  Horizontal trim/belt courses live inside the story band that owns them:
  nothing structural protrudes past z = 10*n except the documented top
  termination (cornice / beam / parapet / roof).
  TRIM PROUDNESS: water tables, cornices, column/beams and copings may extend
  1 voxel beyond the footprint ALONG THE WALL-FACE NORMAL only (never along
  the bay-run direction, where modules tile).  E.g. a 12x24 wall bay may use
  y in [-1, 25) but x stays in [0, 12).

STORY RHYTHM — MILL ("mill": early brick, load-bearing walls)
  Per story, story base s = 10*k:
    z s+0..s+2 : concrete water table, proud 1 (ground story only)
    z s+1      : concrete sill under the window band (x 2..10 of the bay)
    z s+2..s+8 : window glass band (6 wide, x 3..9); steel_dark sash/mullions
    z s+9      : concrete lintel (x 2..10)
  Wall top H = 10*n: corbelled brick cornice z H..H+2, proud 1.
  Flat roof (roof-flat tile): slab z H+2..H+3 (roof grey); brick parapet
    z H+3..H+6; concrete coping z H+6..H+7, proud 1.
  Gable roof (roof-gable-bay, mill only): eave z H+2 at y=0/24, ridge z H+8
    at y=12 (slope 0.5, like factory_brick_v1's RISE=16 over half-span 32);
    patina planes 2 thick; ridge roll; one raised seam rib at the bay's
    west (x0) edge so tiled bays read as standing seams.
  Ridge monitor (mill only): walls y 8..10 / 14..16, z H+2..H+13, louvered
    upper half; own gable cap, ridge along x at z H+15.
  Doors (ground story; upper stories of door bays get windows):
    loading : opening x 2..10, leaf z 2..8 green + transom, concrete surround
    personnel: opening x 4..8, leaf z 2..7 dark, steel_dark surround
    garage  : opening x 1..11, leaf z 2..H-1 green_dark, panel lines

STORY RHYTHM — FRAME ("frame": mid-century concrete frame, brick infill)
  Per story, story base s = 10*k:
    z s+0..s+2 : concrete plinth, proud 1 (ground story only)
    columns    : 2 wide, centred on bay lines (half-columns per seam rule),
                 z s+2..s+10 ground / s..s+10 upper, proud 1, concrete
    z s+2..s+8 : brick infill + glass ribbon, recessed 1 behind facade;
                 steel_dark mullions every 3; concrete sill z s+2..s+3
    z s..s+2   : brick spandrel under the sill on upper stories (s>0) —
                 solid wall below the window band, no between-story gap
    z s+8..s+10: concrete header beam band, proud 1 (top story: wall top)
  Flat roof (roof-flat tile): slab z H..H+2 (roof grey); concrete parapet
    z H+2..H+5; coping z H+5..H+6, proud 1.
  Doors (ground story; upper stories of door bays get window ribbons):
    loading : 6 wide (x 3..9), leaf z 2..8 green + glass transom z 7
    personnel: 3 wide, leaf z 2..6 dark, steel_dark frame
    garage  : 8 wide (x 2..10), leaf z 2..H-1, dark/steel_dark panels

HOLLOW SHELLS
  Shells are hollow: walls + roof + floor edge only.  Floor edge = perimeter
  strip T wide, z 0..1, plus strips under interior-room walls.
  Buried interior room for damage reveals: sealed room INSIDE the hollow
  shell at z 1..7 (family-styled walls; mill = dark brick, frame = concrete
  + steel), walls stand on the floor strips so the floater sweep passes.
  (Rooms sit above grade because the .vox writer keeps z unshifted; they
  read as buried once the outer wall is breached.)

ROOF TILES
  roof-flat: 12x12 tile, pure slab + parapet on the WEST (-x) and SOUTH (-y)
  edges only (half-convention): tiling N x M tiles yields one continuous
  parapet ring with no doubles; end bays get their end parapet from the
  endwall piece.  Corners tile 2x2; the corner wall piece carries no parapet.

FAMILIES
  mill : MILL_PALETTE (19 slots).  Never mix with frame in one building.
  frame: FRAME_PALETTE (15 slots). Never mix with mill in one building.
  lot  : LOT_PALETTE (18 slots), family-neutral (walls, fences, tank/tower
         rig parts).  Rig parts are identified by palette slot (see below).

RIG PARTS (water tower / fuel tank — infantry #118 style contract)
  Each part is its own .vox, authored in ONE shared design frame
  (footprint documented in the part's docstring; file x/y are min-normalised
  by the writer, z is kept).  The part's identity is its palette slot:
    water tower: wt_leg_steel (each leg separately), wt_brace_steel,
                 wood (balcony), wt_tank_steel (shell), wt_roof_steel (roof)
    fuel tank:   ft_shell (shell), ft_roof (roof), ft_ladder_steel (ladder),
                 ft_pipe (manifold)
  The game reassembles parts by frame coordinates and breaks them apart
  (tank explodes, tower legs buckle) by part identity.

VALIDATION (every generator runs these before shipping)
  - floater_sweep: every 6-connected component must touch the module's base
    plane (min z of the model).  No hovering attachments.
  - voxel count reported; preview PNG read at full size by the author.
  - slice render through any changed/joined region for seam checks.
"""

B, S, T, DEPTH = 12, 10, 2, 24

# ---------------------------------------------------------------- palettes
# (name, rgb); color index = position + 1.  Every module in a family uses
# this exact list, in this order.
#
# VIEWER RULE: each generator MUST contain a literal `PALETTE = [...]`
# assignment (copy the list into the file).  The viewer server statically
# parses the generator to derive palette_names + assemblies; an imported
# name (PALETTE = MILL_PALETTE) does NOT derive (assemblies stay null).

MILL_PALETTE = [
    ("concrete",      (170, 166, 158)),  # 1  water table, lintels, sills
    ("concrete_dark", (112, 108, 100)),  # 2
    ("coping",        (202, 198, 190)),  # 3  parapet coping
    ("brick",         (150,  90,  66)),  # 4  walls
    ("brick_dark",    (120,  68,  50)),  # 5
    ("glass",         ( 72,  98, 118)),  # 6  window glass
    ("glass_dark",    ( 44,  62,  78)),  # 7
    ("steel",         (122, 126, 134)),  # 8
    ("steel_dark",    ( 62,  64,  72)),  # 9  sash, louvers, frames
    ("white",         (235, 235, 230)),  # 10
    ("window",        ( 18,  26,  38)),  # 11 dark glass
    ("dark",          ( 32,  34,  40)),  # 12 door leaves
    ("green",         (100, 118,  94)),  # 13 doors
    ("green_dark",    ( 70,  88,  68)),  # 14
    ("roof",          (100, 104, 100)),  # 15 flat slab grey
    ("band_red",      (158,  62,  52)),  # 16 stack bands
    ("band_white",    (224, 220, 212)),  # 17 stack bands
    ("patina",        ( 96, 142, 118)),  # 18 gable roof copper
    ("patina_dark",   ( 66, 104,  88)),  # 19 seams, ridge
]

FRAME_PALETTE = [
    ("concrete",      (170, 166, 158)),  # 1  frame, beams, plinth
    ("concrete_dark", (112, 108, 100)),  # 2
    ("coping",        (202, 198, 190)),  # 3  parapet coping
    ("brick",         (150,  90,  66)),  # 4  infill
    ("brick_dark",    (120,  68,  50)),  # 5
    ("glass",         ( 72,  98, 118)),  # 6  window ribbon
    ("glass_dark",    ( 44,  62,  78)),  # 7
    ("steel",         (122, 126, 134)),  # 8
    ("steel_dark",    ( 62,  64,  72)),  # 9  mullions, frames
    ("white",         (235, 235, 230)),  # 10
    ("window",        ( 18,  26,  38)),  # 11 dark glass
    ("dark",          ( 32,  34,  40)),  # 12 door leaves
    ("green",         (100, 118,  94)),  # 13 doors
    ("green_dark",    ( 70,  88,  68)),  # 14
    ("roof",          (100, 104, 100)),  # 15 flat slab grey
]

LOT_PALETTE = [
    ("stone",         (148, 142, 130)),  # 1  wall stone
    ("stone_dark",    (110, 104,  94)),  # 2
    ("capstone",      (200, 196, 188)),  # 3  wall caps, pillar caps
    ("iron",          ( 70,  74,  82)),  # 4  fence posts/rails
    ("iron_dark",     ( 38,  40,  46)),  # 5
    ("mesh",          (105, 110, 120)),  # 6  chain-link
    ("wood",          (125,  92,  62)),  # 7  balcony deck, gate boards
    ("wood_dark",     ( 90,  66,  44)),  # 8
    ("concrete",      (170, 166, 158)),  # 9  footings, dock/platform
    ("wt_leg_steel",  (120, 124, 132)),  # 10 RIG: water tower legs
    ("wt_brace_steel",( 96, 100, 108)),  # 11 RIG: water tower bracing
    ("wt_tank_steel", (158, 162, 170)),  # 12 RIG: water tower tank shell
    ("wt_roof_steel", (110, 114, 122)),  # 13 RIG: water tower roof
    ("ft_shell",      (108, 122, 100)),  # 14 RIG: fuel tank shell (sage)
    ("ft_roof",       ( 90,  94,  90)),  # 15 RIG: fuel tank roof
    ("ft_ladder_steel",( 80,  84,  90)),  # 16 RIG: fuel tank ladder
    ("ft_pipe",       (110, 114, 120)),  # 17 RIG: fuel tank manifold
    ("rust",          (142,  82,  50)),  # 18 weathering
]

FAMILY_PALETTE = {"mill": MILL_PALETTE, "frame": FRAME_PALETTE, "lot": LOT_PALETTE}


# ---------------------------------------------------------------- builders
def box(d, x0, x1, y0, y1, z0, z1, ci):
    """Inclusive-exclusive box fill. ci is a 1-based color index."""
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                d[(x, y, z)] = ci


def CI(palette):
    return {name: i + 1 for i, (name, _) in enumerate(palette)}


# ---------------------------------------------------------------- validation
def floater_sweep(vox):
    """6-connectivity components; return those NOT touching min-z.

    Prints a summary; returns the list of bad components (each a set).
    """
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


# ---------------------------------------------------------------- .vox writer (single model per file)
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


# ---------------------------------------------------------------- isometric preview (boilerplate)
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


def mill_window(vox, C, axis, face, outward, s, a0, a1):
    """Improved mill window (2026-09-28): glass inset 1 voxel, concrete sill
    + lintel proud 1 voxel (no jambs), 1-voxel iron perimeter frame + one
    horizontal mid bar (no vertical bar).

    axis: 'y' = wall runs along x (face normal is y);
          'x' = wall runs along y (face normal is x).
    face: outer face coordinate (the brick layer the window cuts through).
    outward: -1 or +1, direction from wall interior toward exterior.
    s: story base z. Glass spans z s+2..s+7.
    a0, a1: window span along the wall (a1 exclusive).
    """
    sash = C["steel_dark"]
    inset = face - outward   # glass layer, 1 in from face
    proud = face + outward   # sill/lintel layer, 1 out from face
    z0, z1 = s + 2, s + 8    # glass z range (end exclusive)
    # clear outer brick, set inset glass
    for a in range(a0, a1):
        for z in range(z0, z1):
            if axis == "y":
                vox.pop((a, face, z), None)
                vox[(a, inset, z)] = C["glass"]
            else:
                vox.pop((face, a, z), None)
                vox[(inset, a, z)] = C["glass"]
    # iron perimeter frame + horizontal mid bar (no vertical)
    for a in range(a0, a1):
        for zz in (z0, z1 - 1, s + 4):
            if axis == "y":
                vox[(a, inset, zz)] = sash
            else:
                vox[(inset, a, zz)] = sash
    for z in range(z0, z1):
        if axis == "y":
            vox[(a0, inset, z)] = sash
            vox[(a1 - 1, inset, z)] = sash
        else:
            vox[(inset, a0, z)] = sash
            vox[(inset, a1 - 1, z)] = sash
    # concrete sill + lintel, proud of face
    for a in range(a0 - 1, a1 + 1):
        if axis == "y":
            vox[(a, proud, s + 1)] = C["concrete"]
            vox[(a, proud, s + 8)] = C["concrete"]
        else:
            vox[(proud, a, s + 1)] = C["concrete"]
            vox[(proud, a, s + 8)] = C["concrete"]
