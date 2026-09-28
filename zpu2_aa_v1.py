#!/usr/bin/env python3
"""Strike Bay — Soviet ZPU-2 style twin 14.5mm AA gun (v1).

Built for rigging: the generator emits FOUR .vox files that share one
design frame (file coords == design coords, global min at 0,0,0):

  zpu2_base_v1.vox     static: pedestal, outrigger arms, screw jacks, tow bar
  zpu2_turret_v1.vox   traverse: cradle cheeks, seat, AA sight, ammo boxes,
                      handwheels (rotates about the vertical traverse axis)
  zpu2_barrels_v1.vox  elevation: twin KPV receivers + barrels + muzzle brakes
                      (rotates about the horizontal elevation axis)
  zpu2_aa_v1.vox       assembled merge of the three (browsing / reference)

Rig pivots (in .vox file coords, x right / y forward / z up):
  TRAVERSE_PIVOT  = (16, 16, 8)    z-axis; parent the turret part here
  ELEVATION_PIVOT = (16, 16, 16)   x-axis; parent the barrels part here,
                                  as a child of the traverse node

The barrels are authored horizontal (0 deg elevation, pointing +y) so the
rest pose is the rigging neutral. Ammo boxes, seat and sight traverse with
the cradle, as on the real mount.

Scale: 1 voxel ~= 7 cm against the 25-tall infantry (infantry_green_v2).
A standing infantryman is composited into the assembled preview for scale.

Reference: twin-KPV ZPU-2 in deployed firing position (screw jacks down,
tow arms as outriggers), olive drab with gunmetal barrels.
"""
import random
random.seed(3)

PALETTE = [  # (name, rgb); color index = position + 1
    ("olive",        ( 99, 102,  71)),  # 1  Soviet protective green
    ("olive_dark",   ( 72,  75,  52)),  # 2  olive shadow / lids
    ("gunmetal",     ( 56,  58,  62)),  # 3  barrels, receiver furniture
    ("gunmetal_dark",( 36,  38,  42)),  # 4  muzzle brake, collars, feet
    ("steel",        (122, 126, 134)),  # 5  jack screws, bright hardware
    ("steel_dark",   ( 62,  64,  72)),  # 6  handwheels, sight ring, chutes
    ("dark",         ( 28,  30,  34)),  # 7  grips, bore, deep shadow
    ("brass",        (168, 134,  72)),  # 8  ammo hint in feed chutes
    ("glass",        (120, 160, 180)),  # 9  sight reflector
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

TRAVERSE_PIVOT = (16, 16, 8)
ELEVATION_PIVOT = (16, 16, 16)

base = {}
turret = {}
barrels = {}

def box(d, x0, x1, y0, y1, z0, z1, c):
    """Inclusive-exclusive box fill into dict d."""
    ci = CI[c]
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                d[(x, y, z)] = ci

def cyl_z(d, cx, cy, r, z0, z1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for y in range(cy - r, cy + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                for z in range(z0, z1):
                    d[(x, y, z)] = ci

def cyl_x(d, cy, cz, r, x0, x1, c):
    ci = CI[c]
    for y in range(cy - r, cy + r + 1):
        for z in range(cz - r, cz + r + 1):
            if (y - cy) ** 2 + (z - cz) ** 2 <= r * r:
                for x in range(x0, x1):
                    d[(x, y, z)] = ci

def cyl_y(d, cx, cz, r, y0, y1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            if (x - cx) ** 2 + (z - cz) ** 2 <= r * r:
                for y in range(y0, y1):
                    d[(x, y, z)] = ci

def ring_z(d, cx, cy, r, z0, z1, c):
    """Flat ring in the xy-plane (traverse wheels, tow eye)."""
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for y in range(cy - r, cy + r + 1):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if (r - 1) ** 2 < d2 <= r * r:
                for z in range(z0, z1):
                    d[(x, y, z)] = ci

def ring_x(d, cy, cz, r, x0, x1, c):
    """Ring in the yz-plane (elevating handwheel, faces +-x)."""
    ci = CI[c]
    for y in range(cy - r, cy + r + 1):
        for z in range(cz - r, cz + r + 1):
            d2 = (y - cy) ** 2 + (z - cz) ** 2
            if (r - 1) ** 2 < d2 <= r * r:
                for x in range(x0, x1):
                    d[(x, y, z)] = ci

def ring_y(d, cx, cz, r, y0, y1, c):
    """Ring in the xz-plane (AA sight ring, faces +-y)."""
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            d2 = (x - cx) ** 2 + (z - cz) ** 2
            if (r - 1) ** 2 < d2 <= r * r:
                for y in range(y0, y1):
                    d[(x, y, z)] = ci

# ================================================================ BASE (static)
# pedestal
box(base, 13, 19, 13, 19, 0, 4, "olive")
box(base, 14, 18, 14, 18, 4, 7, "olive")
cyl_z(base, 16, 16, 5, 7, 8, "olive_dark")          # pintle cap disc
ring_z(base, 16, 16, 5, 7, 8, "gunmetal_dark")     # traverse ring gear (rim of the disc)
# outrigger arms (side pair)
box(base, 0, 13, 15, 17, 3, 5, "olive")
box(base, 19, 32, 15, 17, 3, 5, "olive")
box(base, 13, 19, 15, 17, 3, 5, "olive_dark")      # center saddle
# tow bar (front) + rear leg
box(base, 14, 18, 18, 34, 3, 5, "olive")           # bar runs under the whole tow eye
box(base, 15, 17, 1, 13, 3, 5, "olive")
ring_z(base, 16, 32, 2, 4, 5, "steel_dark")        # tow eye
# screw jacks: steel screw + dark disc foot
for (jx, jy) in ((3, 16), (28, 16), (16, 28), (16, 3)):
    cyl_z(base, jx, jy, 1, 1, 6, "steel")
    cyl_z(base, jx, jy, 2, 5, 6, "steel_dark")     # collar
    cyl_z(base, jx, jy, 3, 0, 1, "gunmetal_dark")  # foot disc
# traverse handwheel on a post, right of the pedestal
box(base, 20, 22, 15, 17, 3, 6, "olive_dark")
ring_z(base, 21, 16, 2, 6, 7, "steel_dark")
box(base, 21, 22, 14, 18, 6, 7, "steel_dark")      # spokes
box(base, 19, 23, 16, 17, 6, 7, "steel_dark")
cyl_z(base, 21, 16, 1, 3, 7, "gunmetal")

# ================================================================ TURRET (traverse about (16,16) z-axis)
cyl_z(turret, 16, 16, 6, 8, 9, "olive_dark")       # turntable plate
box(turret, 12, 20, 14, 18, 9, 11, "olive")        # crossbeam
box(turret, 12, 14, 13, 19, 9, 16, "olive")        # cradle cheeks
box(turret, 18, 20, 13, 19, 9, 16, "olive")
box(turret, 12, 14, 13, 19, 14, 16, "olive_dark")  # cheek caps
box(turret, 18, 20, 13, 19, 14, 16, "olive_dark")
cyl_x(turret, 16, 16, 2, 10, 22, "gunmetal")       # trunnion
cyl_x(turret, 16, 16, 1, 9, 23, "gunmetal_dark")   # trunnion pins
# gunner seat (traverses with the mount) — one connected assembly
box(turret, 14, 18, 9, 12, 6, 9, "olive_dark")     # support arm: plate -> pan
box(turret, 15, 17, 7, 9, 3, 6, "olive_dark")      # post
box(turret, 13, 19, 6, 11, 6, 7, "gunmetal")       # pan
box(turret, 13, 19, 5, 6, 6, 12, "olive_dark")     # backrest
box(turret, 12, 20, 5, 9, 2, 3, "olive_dark")      # footrest
# AA reflector sight, left cheek (solid disc + glass; a 1-voxel ring breaks up)
box(turret, 9, 11, 15, 17, 16, 20, "olive_dark")   # sight post
cyl_y(turret, 10, 21, 2, 15, 17, "steel_dark")     # sight disc
box(turret, 9, 11, 15, 17, 20, 22, "glass")        # reflector
# ammo boxes with lids + feed chutes to the receivers
for (bx0, bx1, s) in ((5, 10, -1), (22, 27, 1)):
    box(turret, bx0, bx1, 11, 19, 10, 15, "olive")
    box(turret, bx0, bx1, 11, 19, 15, 16, "olive_dark")   # lid
    box(turret, bx0, bx1, 13, 17, 12, 13, "dark")         # stencil slot
    cx0 = bx1 if s < 0 else bx0 - 2
    box(turret, cx0, cx0 + 2, 14, 16, 15, 16, "steel_dark")  # feed chute
    box(turret, cx0, cx0 + 2, 14, 15, 16, 17, "brass")       # ammo hint
# elevating handwheel, right cheek
cyl_x(turret, 16, 12, 1, 20, 23, "gunmetal")       # axle
ring_x(turret, 16, 12, 2, 21, 23, "steel_dark")
box(turret, 21, 23, 15, 17, 10, 14, "steel_dark")  # spokes
box(turret, 21, 23, 14, 18, 11, 13, "steel_dark")

# ================================================================ BARRELS (elevation about x-axis at (16,16,16))
for cx in (13, 19):
    box(barrels, cx - 1, cx + 2, 10, 20, 14, 18, "olive")        # receiver
    box(barrels, cx - 1, cx + 2, 12, 18, 18, 19, "olive_dark")   # top cover
    box(barrels, cx - 1, cx + 2, 9, 10, 14, 18, "gunmetal_dark") # buttplate
    box(barrels, cx, cx + 1, 10, 11, 11, 14, "dark")             # pistol grip
    box(barrels, cx + 1, cx + 3, 12, 14, 16, 17, "steel_dark")   # charging handle
    box(barrels, cx, cx + 2, 20, 38, 15, 17, "gunmetal")         # barrel
    for collar_y in (24, 29, 34):                                # barrel collars
        box(barrels, cx - 1, cx + 2, collar_y, collar_y + 1, 14, 18, "gunmetal_dark")
    box(barrels, cx - 1, cx + 2, 38, 40, 14, 18, "gunmetal_dark") # muzzle brake root
    box(barrels, cx - 1, cx + 3, 40, 42, 14, 18, "gunmetal_dark") # brake flare
    box(barrels, cx, cx + 2, 40, 42, 15, 17, "dark")              # bore shadow
box(barrels, 11, 21, 26, 27, 15, 17, "gunmetal_dark")             # barrel crossbar

# ================================================================ assembled merge
assembled = dict(base)
assembled.update(turret)
assembled.update(barrels)   # barrels win at the trunnion overlap

PARTS = {
    "zpu2_base_v1": base,
    "zpu2_turret_v1": turret,
    "zpu2_barrels_v1": barrels,
    "zpu2_aa_v1": assembled,
}


# ---------------------------------------------------------------- .vox writer (MagicaVoxel 150)
def write_vox(path, vox, PALETTE, xoff=None, yoff=None):
    import struct
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    if xoff is None:
        xoff, yoff = -min(xs), -min(ys)
    sx, sy, sz = max(xs) + xoff + 1, max(ys) + yoff + 1, max(zs) + 1
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


# ---------------------------------------------------------------- isometric preview
def render_preview(path, vox, PALETTE, scale=3):
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


# ---------------------------------------------------------------- top-down slice
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


# ---------------------------------------------------------------- .vox reader (for the scale figure)
def read_vox(path):
    import struct
    data = open(path, "rb").read()
    i = data.find(b"XYZI")
    n = struct.unpack("<i", data[i + 12:i + 16])[0]   # numVoxels: first content word
    j = data.find(b"RGBA")
    pal = [struct.unpack("BBBB", data[j + 8 + k * 4:j + 12 + k * 4])[:3] for k in range(256)]
    vox, off = {}, i + 16
    for _ in range(n):
        x, y, z, c = struct.unpack("BBBB", data[off:off + 4]); off += 4
        vox[(x, y, z)] = pal[c - 1]
    return vox


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))

    # shared frame: every part uses the assembled bbox offsets, so pivots
    # map 1:1 across all four files
    gx = min(p[0] for p in assembled); gy = min(p[1] for p in assembled)
    XOFF, YOFF = -gx, -gy
    print(f"frame offset: ({XOFF},{YOFF}); traverse pivot file coords: "
          f"({TRAVERSE_PIVOT[0]+XOFF},{TRAVERSE_PIVOT[1]+YOFF},{TRAVERSE_PIVOT[2]})")
    print(f"elevation pivot file coords: "
          f"({ELEVATION_PIVOT[0]+XOFF},{ELEVATION_PIVOT[1]+YOFF},{ELEVATION_PIVOT[2]})")

    for name, d in PARTS.items():
        write_vox(os.path.join(here, name + ".vox"), d, PALETTE, XOFF, YOFF)
        render_preview(os.path.join(here, name + "_preview.png"), d, PALETTE)

    # manned figure: seat a posed infantry_green_v2 in the gunner seat.
    # The soldier is authored in a T-pose; bend hips/knees/shoulders in voxel
    # space: thighs rotate +90 deg about x at the hip, shins translate with
    # the knee, arms swing forward toward the handwheel/sight.
    import math
    sold = read_vox(os.path.join(here, "infantry_green_v2.vox"))
    sold = {p: c for p, c in sold.items() if p[0] <= 30}  # drop stray voxel
    HIP = (13, 3, 10)
    T = (3, 5, -2)                       # hip -> seat: (13,3,10) -> (16,8,8)
    LEGXS = {10, 11, 12, 14, 15, 16}

    def _rz(dx, dy, deg):
        r = math.radians(deg)
        return (dx * math.cos(r) - dy * math.sin(r),
                dx * math.sin(r) + dy * math.cos(r))

    def _rx(dy, dz, deg):
        r = math.radians(deg)
        return (dy * math.cos(r) - dz * math.sin(r),
                dy * math.sin(r) + dz * math.cos(r))

    def _pose_arm(x, y, z, side):
        px, py, pz = (17, 2, 15) if side > 0 else (9, 2, 15)
        dx, dy, dz = x - px, y - py, z - pz
        dx, dy = _rz(dx, dy, 65 * side)   # swing forward toward the controls
        dy, dz = _rx(dy, dz, -12)         # slight droop
        return (px + dx + T[0], py + dy + T[1], pz + dz + T[2])

    posed = {}
    for (x, y, z), rgb in sold.items():
        if z in (14, 15, 16) and y in (1, 2, 3) and (x < 9 or x > 17):
            nx, ny, nz = _pose_arm(x, y, z, +1 if x > 17 else -1)
            posed[(round(nx), round(ny), round(nz))] = rgb
        elif z >= 10 or x not in LEGXS:
            posed[(x + T[0], y + T[1], z + T[2])] = rgb          # torso/head
        elif z >= 5:
            dx, dy, dz = x - HIP[0], y - HIP[1], z - HIP[2]     # thigh -> fwd
            posed[(round(HIP[0] + dx + T[0]), round(HIP[1] - dz + T[1]),
                   round(HIP[2] + dy + T[2]))] = rgb
        else:
            posed[(x + T[0], y + T[1] + 10, z + T[2] + 3)] = rgb  # shin w/knee
    # assembled preview: bare gun (this .vox carries no figure)
    render_preview(os.path.join(here, "zpu2_aa_v1_preview.png"), assembled, PALETTE)

    # manned variant: bake the posed gunner into its own .vox so the viewer
    # shows him in 3D, not just in a thumbnail.
    manpal = list(PALETTE)
    rgb2ci = {}
    manned = dict(assembled)
    for (x, y, z), rgb in posed.items():
        if rgb not in rgb2ci:
            rgb2ci[rgb] = len(manpal) + 1
            manpal.append((f"soldier_{len(manpal)}", rgb))
        manned[(x, y, z)] = rgb2ci[rgb]
    print(f"manned: {len(manned)} voxels")
    write_vox(os.path.join(here, "zpu2_aa_manned_v1.vox"), manned, manpal)
    render_preview(os.path.join(here, "zpu2_aa_manned_v1_preview.png"),
                   manned, manpal)

    render_slice(os.path.join(here, "zpu2_aa_v1_slice_z5.png"), assembled, PALETTE, 5)
    render_slice(os.path.join(here, "zpu2_aa_v1_slice_z16.png"), assembled, PALETTE, 16)
