#!/usr/bin/env python3
"""Strike Bay — Mk 15 Phalanx CIWS (Block 1B), v1 (#423, epic #417).

The carrier's point-defence gun: a western (US Navy) close-in weapon system.
Reference: Phalanx Mk 15 Block 1B photos (white radome "R2-D2" dome over an
X-braced gun cradle, 6-barrel M61 gatling below the radome's right half,
ammo drum slung under the cradle with the feed belt, FLIR/rangefinder pod
on the radome's right, boxy yoke arms on a turntable).

SCALE  CIWS_VOXEL = 0.05625 m (half the carrier's 0.1125 m: a 2x fine grid,
       so the gatling cluster and radome read round). ~2.3 m tall: stylised
       to the carrier's compressed scale, not the real 4.7 m.

Frame: z-up, x = across, y = fore-aft; forward (barrels) = file -y (the ZIL
convention). Authored at rest: barrels level, pointing -y.

Parts (one 6-connected component each):
  ciws-base-v1      static deck pedestal
  ciws-carriage-v1  traverse: turntable + yoke arms, about the vertical
                    line TRAVERSE_AXIS (x, y)
  ciws-cradle-v1    elevation: gun frame, ammo drum + belt, radome, FLIR,
                    about the x-parallel line ELEV_PIVOT (y, z)
  ciws-barrels-v1   spin: the gatling cluster, about the y-parallel line
                    SPIN_AXIS (x, z); child of the cradle
  ciws-assembled-v1 merge for browsing

Points (file coords, continuous):
  MUZZLE            centre of the muzzle face (tracer origin)

Landmarks (file voxel cells, for agents without vision):
  FRONT  muzzle face y=1 at (17.5, 1, 16.5): the barrels point -y.
  BACK   yoke/turntable rear y~36; radome back face y~34.
  UP     +z (radome top z=41). Gun + FLIR sit on +x (x 15..26), the
         radome centre on the traverse axis x=15.
  Parts  base      x 4..25   y 16..37  z 0..2    (deck footprint)
         carriage  x 2..27   y 17..36  z 3..20   (arms x 2..7 and 22..27)
         cradle    x 8..26   y 15..34  z 4..41   (radome z 20..41, drum
                   below the gun at z~8.6)
         barrels   x 15..19  y 1..15   z 14..18
  Links  carriage sits on base at z=3 about TRAVERSE_AXIS (15, 27);
         cradle hangs in the arms on ELEV_PIVOT (y 27, z 16.5);
         barrels spin in the cradle on SPIN_AXIS (x 17.5, z 16.5).
"""
import math
import os

CIWS_VOXEL = 0.05625

PALETTE = [
    ("haze",       (168, 173, 176)),  # 1 arms, frame (haze grey)
    ("haze_dark",  (132, 137, 141)),  # 2 panel lines, shadowed faces
    ("white",      (236, 238, 235)),  # 3 radome
    ("offwhite",   (206, 209, 206)),  # 4 radome bands, FLIR shade
    ("steel",      (118, 122, 127)),  # 5 turntable, trunnions, rungs
    ("deck",       ( 62,  65,  69)),  # 6 pedestal
    ("dark",       ( 40,  42,  46)),  # 7 mechanism inside the frame, belt
    ("gunmetal",   (118, 122, 126)),  # 8 barrels, clamps
    ("bore",       ( 14,  14,  16)),  # 9 muzzle bores
    ("lens",       ( 36,  44,  56)),  # 10 FLIR glass
    ("drum",       (150, 154, 157)),  # 11 ammo drum
    ("arm",        (146, 151, 154)),  # 12 yoke arm faces
    ("frame",      (188, 192, 194)),  # 13 cradle frame (lightest grey)  # 11 ammo drum
]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

CX = 15.0            # traverse axis x (voxels 0..29 symmetric about it)
CY = 16.0            # traverse axis y
TRAVERSE_AXIS = (CX, CY)
ELEV_PIVOT = (None, CY, 16.5)        # x-parallel line through y, z
GUN_X, GUN_Z = 17.5, 16.5            # gatling axis (continuous)
SPIN_AXIS = (GUN_X, None, GUN_Z)     # y-parallel line through x, z
MUZZLE_Y = -10                        # pre-shift muzzle row
SHIFT_Y = 11                          # whole model moved +y so the muzzle sits at y >= 0

FRAME = (9, 20, 6, 21, 13, 19)      # x0, x1, y0, y1, z0, z1 inclusive
ARM_L = (2, 7)                       # x ranges inclusive
ARM_R = (22, 27)
ARM_Y = (10, 21)
ARM_Z = (4, 20)
RADOME_CY = CY + 1.0
RADOME_R = 6.5
RADOME_Z = (20, 35)                  # cylinder rows; dome above
DOME_H = 6.0


def put(d, x, y, z, c):
    d[(x, y, z)] = CI[c]


def box(d, x0, x1, y0, y1, z0, z1, c):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                put(d, x, y, z, c)


def disk_z(d, cx, cy, r, z, c, r_in=None):
    """Horizontal disk (or ring when r_in is set) at row z."""
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            q = (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2
            if q <= r * r and (r_in is None or q > r_in * r_in):
                put(d, x, y, z, c)


def disk_y(d, cx, cz, r, y, c, r_in=None):
    """Disk in the x-z plane at row y."""
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            q = (x + 0.5 - cx) ** 2 + (z + 0.5 - cz) ** 2
            if q <= r * r and (r_in is None or q > r_in * r_in):
                put(d, x, y, z, c)


def line6(d, a, b, c):
    """6-connected voxel line from a to b (inclusive)."""
    x, y, z = a
    put(d, x, y, z, c)
    while (x, y, z) != tuple(b):
        dx, dy, dz = b[0] - x, b[1] - y, b[2] - z
        ax, ay, az = abs(dx), abs(dy), abs(dz)
        if ax >= ay and ax >= az:
            x += 1 if dx > 0 else -1
        elif ay >= az:
            y += 1 if dy > 0 else -1
        else:
            z += 1 if dz > 0 else -1
        put(d, x, y, z, c)


# --- base (static) -----------------------------------------------------------

def base():
    d = {}
    disk_z(d, CX, CY, 11.5, 0, "deck")
    disk_z(d, CX, CY, 11.5, 1, "deck")
    disk_z(d, CX, CY, 11.5, 1, "haze_dark", r_in=10.6)   # bolt ring
    disk_z(d, CX, CY, 10.5, 2, "steel")
    return d


# --- carriage (traverse) -----------------------------------------------------

def _arm(d, xa, xb, outer_sign):
    y0, y1 = ARM_Y
    z0, z1 = ARM_Z
    for z in range(z0, z1 + 1):
        # the outer face tapers in toward the turntable over the bottom rows
        cut = max(0, (z0 + 4 - z), (z - (z1 - 2)))
        lo, hi = (xa + cut, xb) if outer_sign < 0 else (xa, xb - cut)
        # front lower edge chamfered back
        yf = y0 + max(0, (z0 + 3 - z))
        for x in range(lo, hi + 1):
            for y in range(yf, y1 + 1):
                put(d, x, y, z, "haze" if z >= z1 - 2 else "arm")
    xo = xa if outer_sign < 0 else xb
    # three shallow hand-hold slots on the outer face
    xin = xo + 1 if outer_sign < 0 else xo - 1
    for hz in (8, 12, 16):
        for y in range(y0 + 4, y1 - 3):
            d.pop((xo, y, hz), None)          # recessed one voxel
            put(d, xin, y, hz, "dark")
    # top cap (darker) and the trunnion bearing boss on the inner face
    for x in range(xa, xb + 1):
        for y in range(y0, y1 + 1):
            if (x, y, z1) in d:
                put(d, x, y, z1, "haze")
    xi = xb if outer_sign < 0 else xa
    disk_x = lambda x: [put(d, x, y, z, "steel")
                        for y in range(int(CY) - 3, int(CY) + 3)
                        for z in range(14, 20)
                        if (y + 0.5 - CY) ** 2 + (z + 0.5 - ELEV_PIVOT[2]) ** 2 <= 7.5]
    disk_x(xi)


def carriage():
    d = {}
    disk_z(d, CX, CY, 10.0, 3, "haze_dark")
    disk_z(d, CX, CY, 9.0, 3, "steel")
    _arm(d, *ARM_L, outer_sign=-1)
    _arm(d, *ARM_R, outer_sign=+1)
    return d


# --- cradle (elevation) ------------------------------------------------------

def _frame(d):
    x0, x1, y0, y1, z0, z1 = FRAME
    # dark mechanism core, seen through the truss
    box(d, x0 + 1, x1 - 1, y0 + 1, y1 - 1, z0 + 1, z1 - 1, "bore")
    # bottom and top plates
    box(d, x0, x1, y0, y1, z0, z0, "frame")
    box(d, x0, x1, y0, y1, z1, z1, "frame")
    # vertical corner posts
    for x in (x0, x1):
        for y in (y0, y1):
            box(d, x, x, y, y, z0, z1, "frame")
    # side faces (x0, x1): an X brace either side of a centre post
    ym = (y0 + y1) // 2
    for x in (x0, x1):
        box(d, x, x, ym, ym, z0, z1, "frame")
        for (ya, yb) in ((y0, ym), (ym, y1)):
            line6(d, (x, ya, z0), (x, yb, z1), "frame")
            line6(d, (x, ya, z1), (x, yb, z0), "frame")
    # front and back faces: X braces
    for y in (y0, y1):
        for off in (0, 1):
            line6(d, (x0 + off, y, z0), (x1 - 1 + off, y, z1), "frame")
            line6(d, (x0 + off, y, z1), (x1 - 1 + off, y, z0), "frame")
    # gun housing: a ring boss round the gatling axis on the front face
    disk_y(d, GUN_X, GUN_Z, 3.1, y0, "frame")
    disk_y(d, GUN_X, GUN_Z, 3.1, y0 - 1, "steel")
    # bearing pads on the side faces, and trunnions out to the arms' bosses
    for x in (x0, x1):
        box(d, x, x, int(CY) - 2, int(CY) + 1, 15, 18, "steel")
    for x in (x0 - 1, x1 + 1):
        for y in (int(CY) - 1, int(CY)):
            for z in (16, 17):
                put(d, x, y, z, "steel")


def _drum(d):
    # ammo drum: axis along y, slung under the frame, with end caps and bands
    cx, cz, r = CX, 8.6, 4.6
    y0, y1 = FRAME[2], FRAME[3] - 1
    for y in range(y0, y1 + 1):
        c = "drum"
        if y in (y0 + 3, y1 - 3):
            c = "haze_dark"
        disk_y(d, cx, cz, r, y, c)
    # front cap: a pale hub inside a dark rim
    disk_y(d, cx, cz, r, y0, "haze_dark")
    disk_y(d, cx, cz, r - 0.6, y0, "white")
    disk_y(d, cx, cz, 1.3, y0, "steel")
    # the belt: one continuous dark band hugging the drum's lower half
    pts = []
    for k in range(0, 19):
        a = math.radians(190 + k * 8.9)
        pts.append((int(math.floor(cx + (r + 0.5) * math.cos(a))), int(math.floor(cz + (r + 0.5) * math.sin(a)))))
    for (ax_, az_), (bx_, bz_) in zip(pts, pts[1:]):
        for y in (y0, y0 + 1):
            line6(d, (ax_, y, max(4, az_)), (bx_, y, max(4, bz_)), "dark")


def _radome(d):
    z0, z1 = RADOME_Z
    for z in range(z0, z1 + 1):
        disk_z(d, CX, RADOME_CY, RADOME_R, z, "white")
    # bottom flange (proud) and the riveted band near the top
    disk_z(d, CX, RADOME_CY, RADOME_R + 0.7, z0, "deck")
    disk_z(d, CX, RADOME_CY, RADOME_R + 0.6, z1 - 1, "offwhite")
    # dome: an ellipsoid cap
    zt = z1 + 1
    for k in range(int(DOME_H) + 1):
        z = zt + k
        t = (k + 0.5) / (DOME_H + 0.5)
        rr = RADOME_R * max(0.0, 1.0 - t ** 2.6) ** (1 / 2.6)
        if rr >= 0.8:
            disk_z(d, CX, RADOME_CY, rr, z, "white")


def _flir(d):
    # bracket off the radome's right side
    xr = int(math.floor(CX + RADOME_R))          # radome's last voxel column
    for x in (xr, xr + 1, xr + 2):
        for y in range(13, int(RADOME_CY) + 1):
            for z in (24, 25):
                put(d, x, y, z, "steel")
    # FLIR pod: a small rounded drum, axis fore-aft, big dark lens in front
    lx, lz = xr + 3.5, 24.5
    for y in range(8, 14):
        disk_y(d, lx, lz, 2.0, y, "white")
    disk_y(d, lx, lz, 2.0, 8, "offwhite")
    disk_y(d, lx, lz, 1.6, 7, "lens")
    # steel strap down to the laser rangefinder, which sits ahead of the arm
    for y in (8, 9):
        put(d, xr + 3, y, 22, "steel")
    box(d, xr + 2, xr + 5, 5, 9, 20, 21, "offwhite")
    for x in (xr + 3, xr + 4):
        put(d, x, 4, 20, "dark"); put(d, x, 4, 21, "dark")


def cradle():
    d = {}
    _drum(d)
    _frame(d)
    _radome(d)
    _flir(d)
    return d


# --- barrels (spin) ----------------------------------------------------------

def barrels():
    """The M61 cluster: a 5-voxel round bundle with grooves between the six
    barrels, a breech collar at the frame, a mid clamp, and a muzzle face
    showing six bores round the spindle."""
    d = {}
    y_rear = FRAME[2] - 2
    bores = []
    for k in range(6):
        a = math.radians(30 + k * 60)
        bores.append((int(math.floor(GUN_X + 1.5 * math.cos(a))), int(math.floor(GUN_Z + 1.5 * math.sin(a)))))
    for y in range(MUZZLE_Y, y_rear + 1):
        disk_y(d, GUN_X, GUN_Z, 2.4, y, "gunmetal")
    # grooves between barrels along the run (not on clamps)
    mid = (MUZZLE_Y + y_rear) // 2
    for y in range(MUZZLE_Y + 3, y_rear - 1):
        if y in (mid, mid + 1):
            continue
        for k in range(6):
            a = math.radians(k * 60)
            put(d, int(math.floor(GUN_X + 2.0 * math.cos(a))), y, int(math.floor(GUN_Z + 2.0 * math.sin(a))), "dark")
    # clamps: muzzle (2 rows) and mid, proud; breech collar lighter
    for y in (MUZZLE_Y + 1, MUZZLE_Y + 2, mid, mid + 1):
        disk_y(d, GUN_X, GUN_Z, 2.9, y, "steel")
    disk_y(d, GUN_X, GUN_Z, 2.4, MUZZLE_Y, "steel")
    for y in (y_rear - 1, y_rear):
        disk_y(d, GUN_X, GUN_Z, 2.9, y, "steel")
    # muzzle face: six bores and the spindle
    for (bx, bz) in bores:
        put(d, bx, MUZZLE_Y, bz, "bore")
    put(d, int(math.floor(GUN_X)), MUZZLE_Y, int(math.floor(GUN_Z)), "dark")
    return d


def _shift(d):
    return {(x, y + SHIFT_Y, z): c for (x, y, z), c in d.items()}


base_d = _shift(base())
carriage_d = _shift(carriage())
cradle_d = _shift(cradle())
barrels_d = _shift(barrels())
TRAVERSE_AXIS = (CX, CY + SHIFT_Y)
ELEV_PIVOT = (None, CY + SHIFT_Y, ELEV_PIVOT[2])
MUZZLE = (GUN_X, MUZZLE_Y + SHIFT_Y, GUN_Z)

assembled = {}
for part in (base_d, carriage_d, cradle_d, barrels_d):
    assembled.update(part)

PARTS = {
    "ciws-base-v1": base_d,
    "ciws-carriage-v1": carriage_d,
    "ciws-cradle-v1": cradle_d,
    "ciws-barrels-v1": barrels_d,
    "ciws-assembled-v1": assembled,
}


def write_vox(path, vox, palette):
    import struct
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    assert min(p[0] for p in vox) >= 0 and min(p[1] for p in vox) >= 0 and min(p[2] for p in vox) >= 0
    sx = max(p[0] for p in vox) + 1; sy = max(p[1] for p in vox) + 1; sz = max(p[2] for p in vox) + 1
    xyzi = struct.pack("<i", len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("BBBB", x, y, z, ci)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for _, (r, g, b) in palette)
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - len(palette))
    main = chunk(b"SIZE", struct.pack("<iii", sx, sy, sz)) + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba)
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 150) + chunk(b"MAIN", b"", main))
    print(f"wrote {path} ({len(vox)} voxels, {sx}x{sy}x{sz})")


def components(vox):
    from collections import deque
    vset, seen, n = set(vox), set(), 0
    for s in vset:
        if s in seen:
            continue
        n += 1
        q = deque([s]); seen.add(s)
        while q:
            x, y, z = q.popleft()
            for nb in ((x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)):
                if nb in vset and nb not in seen:
                    seen.add(nb); q.append(nb)
    return n


if __name__ == "__main__":
    import sys
    if "--viewer-json" in sys.argv[1:]:
        import json
        print(json.dumps({"palette_names": [
            {"index": i + 1, "name": name} for i, (name, _) in enumerate(PALETTE)]}))
        raise SystemExit(0)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "ciws_v1")
    os.makedirs(out, exist_ok=True)
    for name, d in PARTS.items():
        write_vox(os.path.join(out, name + ".vox"), d, PALETTE)
        if "assembled" not in name:
            print(f"  {name}: {components(d)} component(s)")
    names = [n for n in PARTS if "assembled" not in n]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            both = set(PARTS[a]) & set(PARTS[b])
            if both:
                print(f"  OVERLAP {a} / {b}: {len(both)}")
    print("TRAVERSE_AXIS x,y", TRAVERSE_AXIS, "ELEV_PIVOT y,z", ELEV_PIVOT[1:], "SPIN_AXIS x,z", (SPIN_AXIS[0], SPIN_AXIS[2]), "MUZZLE", MUZZLE)
