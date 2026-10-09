#!/usr/bin/env python3
"""Strike Bay — P-15 Termit cruise missile, v1 (#419, epic #417).

Owner blueprint (zil157-p15-mobile-launcher-blueprint, missile details
panel) wins over the generated concepts: olive drab body, yellow warhead
band, rounded nose, folding mid-wings, solid booster slung under the tail.

SCALE  MISSILE_VOXEL = 0.045 m (the ZIL wheels' fine grid: 2x the truck's
       0.09 m), so a 0.76 m body is 17 voxels across and reads round.
       Length ~5.8 m (129 voxels).

Frame: z-up, x = span, y = length with the nose tip at y=0; missile
forward = file -y (the ZIL convention). Body axis (continuous) at
x = AX, z = AZ.

Parts:
  p15-body-v1      static: nose, warhead band, fuselage, tail fin,
                   tailplanes, sustainer nozzle
  p15-wing-r-v1    folds about the hinge line (y axis) at WING_HINGE_R:
                   authored deployed (flat); stowed = rotate up ~90 deg
  p15-wing-l-v1    mirror, hinge WING_HINGE_L
  p15-booster-v1   static on the body until burnout, then drops away
                   (cosmetic); nozzle exit point BOOSTER_NOZZLE
  p15-assembled-v1 merge for browsing

Points (file coords, continuous):
  SUSTAINER_NOZZLE  centre of the main nozzle exit (flame / trail origin)
  BOOSTER_NOZZLE    centre of the booster nozzle exit (launch plume)

Landmarks (file voxel cells, for agents without vision):
  FRONT  nose tip = the single voxel (33, 0, 22); slices widen 1 -> 101
         voxels by y=10, full body (~235) from y~20.
  BACK   tail / sustainer nozzle ring y 125..129 (z 16..28); nozzle exit
         (33.5, 130, 22.5). Top tail fin y 110..123, z >= 40.
  UP     +z (top fin side). RIGHT wing = +x (x 42..65), LEFT = -x (x 1..24).
  Parts  body     x 10..55  y 0..129   z 14..46
         wing-r   x 42..65  y 40..83   z 21..23  (hinge x=42, z=22.5)
         wing-l   x 1..24   y 40..83   z 21..23  (hinge x=25, z=22.5)
         booster  x 24..42  y 88..132  z 3..14   (under the tail; exit
                  (33.5, 134, 7.7))
  Game   load_model_aligned cell = (cx-1-fx, fz, fy-cy) with frame (34, 67)
         puts the nose at model-local z = -3.0 m and the tail at +2.84 m:
         prove "nose leads" with model.to_global(nose) vs velocity.
"""
import math
import os

MISSILE_VOXEL = 0.045

PALETTE = [
    ("olive",        ( 92,  98,  62)),  # 1 body
    ("olive_dark",   ( 66,  71,  45)),  # 2 panel lines, underside
    ("olive_light",  (114, 120,  80)),  # 3 sun-side top
    ("yellow",       (206, 170,  52)),  # 4 warhead band
    ("radome",       (122, 126,  92)),  # 5 nose radome (lighter, worn)
    ("gunmetal",     ( 58,  60,  64)),  # 6 nozzle
    ("dark",         ( 22,  23,  26)),  # 7 nozzle throat
    ("booster",      ( 98, 102,  78)),  # 8 booster casing
    ("booster_dark", ( 80,  84,  64)),  # 9 booster bands
    ("steel",        (118, 122, 128)),  # 10 pylons, hinges
    ("red",          (150,  44,  38)),  # 11 nozzle-cover lip
]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

AX = 33.5          # body axis x (continuous)
AZ = 22.5          # body axis z
R = 8.5            # body radius (0.76 m)
NOSE_LEN = 26      # tangent-ogive length (~1.5 D)
BODY_END = 116     # cylinder ends; boat-tail to the nozzle
TAIL_END = 125
NOZZLE_END = 130
WING_Z = 21        # wing plane voxel rows WING_Z .. WING_Z+2 (3 thick)
WING_ROOT_X = 42   # first wing voxel column, right side (body surface)
WING_SPAN = 24     # per side (~1.4 D)
WING_HINGE_R = (WING_ROOT_X, None, WING_Z + 1.5)   # y-axis line through x, z
WING_HINGE_L = (2 * AX - WING_ROOT_X, None, WING_Z + 1.5)
BOOSTER_AZ = 9.5
BOOSTER_R = 5.0
SUSTAINER_NOZZLE = (AX, NOZZLE_END, AZ)
BOOSTER_NOZZLE = (AX, 134.0, BOOSTER_AZ - 1.8)
_RHO = (R * R + NOSE_LEN * NOSE_LEN) / (2 * R)


def put(d, x, y, z, c):
    d[(x, y, z)] = CI[c]


def radius_at(y):
    """Body radius at station y (voxel row centre y + 0.5)."""
    t = y + 0.5
    if t < NOSE_LEN:
        return max(0.8, math.sqrt(max(0.0, _RHO * _RHO - (NOSE_LEN - t) ** 2)) + R - _RHO)
    if t < BODY_END:
        return R
    if t < TAIL_END:
        u = (t - BODY_END) / (TAIL_END - BODY_END)
        return R - u * 3.0
    return None


def body_color(y, x, z):
    t = y + 0.5
    up = (z + 0.5 - AZ) / R
    if t < 19:
        return "radome"
    if 19 <= y < 23:
        return "yellow"
    if y in (46, 76, 104):
        return "olive_dark"                       # section joints
    if up > 0.2:
        return "olive_light"
    if up < -0.75:
        return "olive_dark"
    return "olive"


def body():
    d = {}
    for y in range(0, TAIL_END):
        r = radius_at(y)
        for x in range(int(AX - R - 1), int(AX + R + 2)):
            for z in range(int(AZ - R - 1), int(AZ + R + 2)):
                if math.hypot(x + 0.5 - AX, z + 0.5 - AZ) <= r:
                    put(d, x, y, z, body_color(y, x, z))
    # sustainer nozzle: gunmetal bell, dark throat
    for y in range(TAIL_END, NOZZLE_END):
        for x in range(int(AX - 7), int(AX + 8)):
            for z in range(int(AZ - 7), int(AZ + 8)):
                rr = math.hypot(x + 0.5 - AX, z + 0.5 - AZ)
                ro = 4.5 + 0.5 * (y - TAIL_END)
                if rr <= ro:
                    put(d, x, y, z, "dark" if rr < ro - 1.3 else "gunmetal")
    xs = (int(AX),)
    top = int(AZ + R)
    # vertical fin: swept trapezoid (~50 deg), clipped tip, ~1 D tall,
    # 3 voxels thick at the root tapering to 1
    FH = 16
    for k in range(0, FH):
        z = top + k
        y0 = 98 + int(round(k * 1.3))
        y1 = 124 - int(k * 0.1)
        fx = (int(AX) - 1, int(AX), int(AX) + 1) if k < 6 else xs
        for y in range(y0, y1):
            for x in fx:
                c = "olive_light"
                if y == y1 - 1:
                    c = "olive_dark"
                if y >= y1 - 5 and k > 2:
                    c = "olive_dark" if y == y1 - 5 else c       # rudder line
                put(d, x, y, z, c)
    # dorsal fillet blending the fin into the spine
    for y in range(84, 99):
        h = int((y - 84) * 0.25)
        for z in range(top, top + h + 1):
            for x in xs:
                put(d, x, y, z, "olive_light")
    # access hatches on the upper flanks (1-voxel outline, no relief)
    for (ya, yb) in ((54, 62),):
        for (x, y, z), c in list(d.items()):
            if not (ya <= y <= yb):
                continue
            up = (z + 0.5 - AZ) / R
            side = (x + 0.5 - AX) / R
            if 0.35 <= up <= 0.75 and abs(side) > 0.45 and math.hypot(x + 0.5 - AX, z + 0.5 - AZ) > R - 1.2:
                d[(x, y, z)] = CI["olive"]          # hatch panel, one shade down
    # tailplanes: swept, mid-height
    for side in (1, -1):
        for k in range(0, 15):
            x = int(AX + R - 0.5 + k) if side > 0 else int(AX - R - 0.5) - k
            y0 = 104 + int(round(k * 1.0))
            y1 = 124 - int(k * 0.2)
            for y in range(y0, y1):
                for z in (int(AZ) - 1, int(AZ)):
                    c = "olive_light" if z == int(AZ) else "olive_dark"
                    if y == y1 - 1 or k == 14:
                        c = "olive_dark"
                    put(d, x, y, z, c)
    # wing-root hinge pads (darker) on both sides
    for x in (int(AX + R), int(AX - R) - 1):
        for y in range(38, 86):
            for z in range(WING_Z - 1, WING_Z + 4):
                put(d, x, y, z, "olive_dark")
    return d


def wing_r():
    """Right wing, deployed: big swept cropped delta, 3 voxels thick."""
    d = {}
    for k in range(0, WING_SPAN):
        x = WING_ROOT_X + k
        le = 40 + int(round(k * 1.2))       # strong leading-edge sweep
        te = 84 - int(round(k * 0.12))
        for y in range(le, te):
            for z in range(WING_Z, WING_Z + 3):
                if k > WING_SPAN * 0.6 and z == WING_Z + 2 and y < le + 1:
                    continue
                c = "olive_light" if z == WING_Z + 2 else ("olive" if z == WING_Z + 1 else "olive_dark")
                if y >= te - 6 and k > 3:
                    c = "olive_dark" if y == te - 6 else c            # aileron line
                if k == WING_SPAN - 1:
                    c = "olive_dark"
                if k == 0:
                    c = "steel"                                       # hinge
                put(d, x, y, z, c)
    return d


def wing_l():
    return {(int(2 * AX) - 1 - x, y, z): c for (x, y, z), c in wing_r().items()}


def booster():
    """Solid booster tucked under the tail: cone nose, strap, one nozzle."""
    d = {}
    for y in range(88, 126):
        t = y + 0.5
        r = BOOSTER_R if t >= 96 else BOOSTER_R * max(0.25, (t - 88) / 8.0)
        for x in range(int(AX - 7), int(AX + 8)):
            for z in range(0, 16):
                if math.hypot(x + 0.5 - AX, z + 0.5 - BOOSTER_AZ) <= r:
                    c = "booster"
                    if y in (100, 101, 120, 121):
                        c = "gunmetal"                       # straps
                    elif z + 0.5 < BOOSTER_AZ - 3.5:
                        c = "booster_dark"
                    put(d, x, y, z, c)
    # fairing between booster and belly, ramping in from the booster nose
    for y in range(88, 96):
        w = 1 + (y - 88) // 3
        for x in range(int(AX) - w, int(AX) + w + 1):
            for z in range(int(BOOSTER_AZ) + 1, 15):
                put(d, x, y, z, "booster")
    for y in range(96, 124):
        for x in range(int(AX) - 3, int(AX) + 4):
            for z in range(int(BOOSTER_AZ + BOOSTER_R) - 2, 15):
                put(d, x, y, z, "booster")
    # single nozzle canted slightly down
    for i, y in enumerate(range(126, 133)):
        cz = BOOSTER_AZ - 0.25 * i
        ro = 3.2 + 0.35 * i
        for x in range(int(AX - 6), int(AX + 7)):
            for z in range(0, 16):
                rr = math.hypot(x + 0.5 - AX, z + 0.5 - cz)
                if rr <= ro:
                    put(d, x, y, z, "dark" if rr < ro - 1.2 and i > 1 else "gunmetal")
    # small stabilising fins on the booster tail
    for s in (1, -1):
        for k in range(0, 5):
            x = int(AX + BOOSTER_R - 0.5 + k) if s > 0 else int(AX - BOOSTER_R - 0.5) - k
            for y in range(116 + k, 126):
                for z in (int(BOOSTER_AZ) - 1, int(BOOSTER_AZ)):
                    put(d, x, y, z, "booster_dark")
    return d


body_v = body()
wing_r_v = wing_r()
wing_l_v = wing_l()
booster_v = booster()
assembled = {}
for p in (booster_v, body_v, wing_r_v, wing_l_v):
    assembled.update(p)

# stowed preview: wings folded up 90 deg about their hinge lines
def _fold(w, hx, sign):
    """Fold up about the hinge, a constant 15 deg lean in over the spine;
    face colours flattened (no dark edge voxels on the stowed faces)."""
    out = {}
    sa, ca = math.sin(math.radians(15)), math.cos(math.radians(15))
    for (x, y, z), c in w.items():
        k = abs(x - hx)
        t = z - WING_Z                      # 0..2 thickness
        for f in (0.25, 0.75):
            kk = k + f
            nx = hx + 0.5 - sign * kk * sa + sign * (t - 1)
            nz = WING_Z + 3 + kk * ca
            col = c if c in (CI["steel"],) else (CI["olive_light"] if t == 2 else CI["olive"])
            if k >= WING_SPAN - 2:
                col = CI["olive_dark"]          # tip seam: two wings, not one plate
            out[(int(math.floor(nx)), y, int(math.floor(nz)))] = col
    return out


assembled_stowed = {}
for p in (booster_v, body_v):
    assembled_stowed.update(p)
assembled_stowed.update(_fold(wing_r_v, WING_ROOT_X, 1))
assembled_stowed.update(_fold(wing_l_v, int(2 * AX) - 1 - WING_ROOT_X, -1))

PARTS = {
    "p15-body-v1": body_v,
    "p15-wing-r-v1": wing_r_v,
    "p15-wing-l-v1": wing_l_v,
    "p15-booster-v1": booster_v,
    "p15-assembled-v1": assembled,
    "p15-assembled-stowed-v1": assembled_stowed,
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
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "p15_v1")
    os.makedirs(out, exist_ok=True)
    for name, d in PARTS.items():
        write_vox(os.path.join(out, name + ".vox"), d, PALETTE)
        if "assembled" not in name:
            print(f"  {name}: {components(d)} component(s)")
    print("SUSTAINER_NOZZLE", SUSTAINER_NOZZLE, "BOOSTER_NOZZLE", BOOSTER_NOZZLE)
    print("WING_HINGE_R x,z", WING_HINGE_R[0], WING_HINGE_R[2], "WING_HINGE_L x,z", WING_HINGE_L[0], WING_HINGE_L[2])
