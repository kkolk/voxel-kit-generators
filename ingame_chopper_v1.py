#!/usr/bin/env python3
"""In-game Strike Bay chopper, ported 1:1 from the game repo.

Source: kkolk/strike-bay @ 2c24644
  scripts/voxel/voxel_shapes.gd  (chopper_body, chopper_canopy, chopper_gun,
                                   rotor, tail_rotor, _fuselage_slice)
  scripts/voxel/voxel_data.gd    (box/shell/cylinder/add/remove semantics)
  scripts/entities/player_chopper.gd (_build_visuals part placement)

Game coords: x right, y up, z forward (nose +Z). CHOPPER_VOXEL = 0.05 m.
Remapped to vox z-up: vox = (x, z_game, y_game + 3) so the skids sit at z=0.

Parts mirror the game's rig: body, canopy (translucent in game), rotor
(spins about the mast), tail_rotor (spins about X), gun (yaws at the chin
mount), plus an assembled reference.
"""
import math
import struct
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette
# GDScript Color(r,g,b) 0..1 -> 0..255, half away from zero (Godot roundi)
def c8(v):
    return int(v * 255.0 + 0.5)

PALETTE = [
    ("olive",        (c8(0.46), c8(0.47), c8(0.28))),
    ("olive_dark",   (c8(0.34), c8(0.35), c8(0.20))),
    ("olive_light",  (c8(0.56), c8(0.57), c8(0.36))),
    ("gunmetal",     (c8(0.30), c8(0.31), c8(0.34))),
    ("dark",         (c8(0.22), c8(0.23), c8(0.27))),
    ("cockpit",      (c8(0.12), c8(0.12), c8(0.14))),
    ("canopy_glass", (c8(0.55), c8(0.80), c8(0.95))),
    ("steel_dark",   (c8(0.42), c8(0.44), c8(0.48))),
    ("deck_line",    (c8(0.90), c8(0.85), c8(0.30))),
    ("black",        (c8(0.10), c8(0.10), c8(0.12))),
    ("rotor_blade",  (c8(0.07), c8(0.07), c8(0.08))),
    ("rotor_tip",    (c8(0.34), c8(0.34), c8(0.37))),
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

# ------------------------------------------------------- VoxelData port
def roundi(x):  # Godot roundi: half away from zero (all inputs here are >= 0)
    return int(math.floor(x + 0.5))

def lerpf(a, b, t):
    return a + (b - a) * t

class VD:
    def __init__(self):
        self.d = {}
    def add(self, p, cn):
        self.d[p] = CI[cn]
    def remove(self, p):
        self.d.pop(p, None)
    def box(self, f, t, cn):
        for x in range(min(f[0], t[0]), max(f[0], t[0]) + 1):
            for y in range(min(f[1], t[1]), max(f[1], t[1]) + 1):
                for z in range(min(f[2], t[2]), max(f[2], t[2]) + 1):
                    self.add((x, y, z), cn)
    def shell(self, f, t, cn, thick=1):
        lo = (min(f[0], t[0]), min(f[1], t[1]), min(f[2], t[2]))
        hi = (max(f[0], t[0]), max(f[1], t[1]), max(f[2], t[2]))
        for x in range(lo[0], hi[0] + 1):
            for y in range(lo[1], hi[1] + 1):
                for z in range(lo[2], hi[2] + 1):
                    if (x - lo[0] < thick or hi[0] - x < thick
                            or y - lo[1] < thick or hi[1] - y < thick
                            or z - lo[2] < thick or hi[2] - z < thick):
                        self.add((x, y, z), cn)
    def cylinder(self, axis, center, radius, a, b, cn):
        r2 = radius * radius
        lo, hi = min(a, b), max(a, b)
        ri = math.ceil(radius)
        for u in range(center[0] - ri, center[0] + ri + 1):
            for v in range(center[1] - ri, center[1] + ri + 1):
                du = float(u - center[0])
                dv = float(v - center[1])
                if du * du + dv * dv > r2 + 0.25:
                    continue
                for tt in range(lo, hi + 1):
                    if axis == 0:
                        self.add((tt, u, v), cn)
                    elif axis == 1:
                        self.add((u, tt, v), cn)
                    else:
                        self.add((u, v, tt), cn)

# ------------------------------------------------- chopper model ports
CHOPPER_ROTOR_Y = 20
CHOPPER_GUN_MOUNT = (0, 0, 11)
CHOPPER_TAIL_ROTOR = (2, 6, -33)

def _fuselage_slice(d, z, w, ylo, yhi, cn):
    for x in range(-w, w + 1):
        for y in range(ylo, yhi + 1):
            corner = abs(x) == w and (y == ylo or y == yhi)
            if corner and w > 1 and yhi - ylo > 1:
                continue
            d.add((x, y, z), cn)

def chopper_body():
    d = VD()
    for z in range(-10, 13):  # main cabin
        _fuselage_slice(d, z, 5, 0, 10, "olive")
    for z in range(13, 25):  # nose taper
        t = float(z - 12) / 12.0
        w = max(roundi(lerpf(5.0, 1.0, t)), 1)
        ylo = roundi(lerpf(0.0, 4.0, t * t))
        yhi = roundi(lerpf(9.0, 5.0, t))
        _fuselage_slice(d, z, w, ylo, yhi, "olive")
    for z in range(6, 19):  # cockpit well carve
        for x in range(-4, 5):
            for y in range(7, 12):
                d.remove((x, y, z))
    d.box((-4, 6, 6), (4, 6, 18), "cockpit")
    for z in range(13, 19):
        t = float(z - 12) / 12.0
        w = max(roundi(lerpf(5.0, 1.0, t)), 1)
        for x in range(-4, 5):
            if abs(x) > w:
                d.remove((x, 6, z))
    # canopy frame
    d.box((-4, 7, 6), (4, 11, 6), "dark")
    d.box((-4, 7, 6), (-4, 7, 18), "dark")
    d.box((4, 7, 6), (4, 7, 18), "dark")
    d.box((-2, 8, 12), (2, 8, 12), "dark")
    d.box((-3, 8, 18), (3, 8, 18), "dark")
    d.box((-1, 7, 18), (1, 8, 19), "dark")
    # engine deck + intake
    d.box((-4, 11, -9), (4, 12, 5), "olive_dark")
    d.box((-3, 13, -8), (3, 13, 3), "olive_dark")
    d.cylinder(1, (0, -1), 2.6, 13, 14, "dark")
    d.cylinder(1, (0, -1), 1.6, 14, 14, "gunmetal")
    d.box((0, 14, -1), (0, 14, -1), "dark")
    # panel lines
    d.box((-5, 10, -8), (5, 10, -8), "olive_dark")
    d.box((-5, 3, -10), (5, 3, 12), "olive_dark")
    d.box((0, 1, -10), (0, 2, 12), "olive_dark")
    # doors
    for x in (-5, 5):
        d.box((x, 4, -6), (x, 8, 2), "olive_light")
        d.box((x, 4, -6), (x, 8, -6), "olive_dark")
        d.box((x, 4, 2), (x, 8, 2), "olive_dark")
    # exhaust pods
    for x in (-6, 6):
        d.cylinder(2, (x, 9), 1.8, -12, -6, "gunmetal")
        d.cylinder(2, (x, 9), 1.0, -13, -12, "black")
    # stub wings
    for x in range(-15, 16):
        ax = abs(x)
        z_lo = -3 if ax < 7 else -2
        z_hi = 4 if ax < 7 else 3
        d.box((x, 5, z_lo), (x, 7 if ax < 9 else 6, z_hi), "olive")
    d.box((-15, 7, -1), (15, 7, 1), "olive_dark")
    # rocket pods
    for x in (-11, 11):
        d.cylinder(2, (x, 3), 2.0, -6, 7, "olive_dark")
        d.cylinder(2, (x, 3), 1.2, 7, 8, "dark")
        d.cylinder(2, (x, 3), 0.6, 8, 8, "deck_line")
        d.cylinder(2, (x, 3), 1.6, -7, -6, "black")
    # wingtip cannons
    for x in (-16, 16):
        d.cylinder(2, (x, 6), 1.2, -3, 3, "gunmetal")
        d.cylinder(2, (x, 6), 0.6, 3, 9, "dark")
        d.box((x, 6, 9), (x, 6, 10), "deck_line")
    # rotor mast
    d.cylinder(1, (0, 2), 1.6, 13, CHOPPER_ROTOR_Y - 1, "dark")
    d.cylinder(1, (0, 2), 2.4, CHOPPER_ROTOR_Y - 2, CHOPPER_ROTOR_Y - 2, "gunmetal")
    # tail boom
    for z in range(-11, -37, -1):
        t = float(-11 - z) / 25.0
        r = lerpf(3.0, 1.5, t)
        cy = roundi(lerpf(6.0, 5.0, t))
        d.cylinder(2, (0, cy), r, z, z, "olive")
    d.box((0, 8, -36), (0, 9, -12), "olive_dark")
    # stabilizer + fin
    d.box((-7, 5, -30), (7, 5, -27), "olive_dark")
    d.box((-7, 5, -30), (-7, 6, -27), "olive")
    d.box((7, 5, -30), (7, 6, -27), "olive")
    d.box((0, 5, -37), (0, 13, -33), "olive_dark")
    d.box((0, 13, -38), (0, 13, -32), "olive")
    d.box((0, 0, -37), (0, 4, -35), "olive_dark")
    # tail rotor gearbox
    d.box((0, CHOPPER_TAIL_ROTOR[1] - 1, CHOPPER_TAIL_ROTOR[2] - 1),
          (CHOPPER_TAIL_ROTOR[0] - 1, CHOPPER_TAIL_ROTOR[1] + 1, CHOPPER_TAIL_ROTOR[2] + 1),
          "gunmetal")
    # skids
    for x in (-6, 6):
        d.box((x, -3, -8), (x, -2, 12), "dark")
        d.box((x, -2, 12), (x, 0, 14), "dark")
        d.box((x, -1, -5), (x, 1, -4), "steel_dark")
        d.box((x, -1, 6), (x, 1, 7), "steel_dark")
    d.box((-6, 0, -5), (6, 0, -4), "steel_dark")
    d.box((-6, 0, 6), (6, 0, 7), "steel_dark")
    return d

def chopper_canopy():
    d = VD()
    d.shell((-4, 8, 7), (4, 11, 12), "canopy_glass")
    for z in range(12, 19):
        t = float(z - 12) / 6.0
        top = roundi(lerpf(10.0, 8.0, t))
        w = 4 if z < 16 else 3
        for x in range(-w, w + 1):
            d.add((x, top, z), "canopy_glass")
            for y in range(8, top):
                if abs(x) == w:
                    d.add((x, y, z), "canopy_glass")
    for z in range(6, 19):
        for x in range(-4, 5):
            d.remove((x, 7, z))
    for x in range(-4, 5):
        for y in range(7, 12):
            d.remove((x, y, 6))
    return d

def chopper_gun():
    d = VD()
    d.cylinder(1, (0, 0), 2.2, -2, 0, "dark")
    d.box((-2, -4, -2), (2, -2, 3), "gunmetal")
    d.cylinder(2, (0, -3), 1.6, 3, 5, "dark")
    for off in [(-1, -2), (1, -2), (0, -4), (-1, -4), (1, -4), (0, -2)]:
        d.cylinder(2, off, 0.4, 5, 14, "black")
    d.cylinder(2, (0, -3), 1.7, 9, 9, "gunmetal")
    d.cylinder(2, (0, -3), 1.7, 14, 14, "gunmetal")
    return d

def rotor():
    d = VD()
    span = 34
    d.box((-span, 0, -1), (span, 0, 1), "rotor_blade")
    d.box((-1, 0, -span), (1, 0, span), "rotor_blade")
    d.box((-span, 0, -1), (-span + 4, 0, 1), "rotor_tip")
    d.box((span - 4, 0, -1), (span, 0, 1), "rotor_tip")
    d.box((-1, 0, -span), (1, 0, -span + 4), "rotor_tip")
    d.box((-1, 0, span - 4), (1, 0, span), "rotor_tip")
    d.cylinder(1, (0, 0), 2.6, 0, 1, "gunmetal")
    d.cylinder(1, (0, 0), 1.2, 2, 2, "dark")
    return d

def tail_rotor():
    d = VD()
    d.box((0, -6, 0), (0, 6, 0), "rotor_blade")
    d.box((0, 0, -6), (0, 0, 6), "rotor_blade")
    d.box((0, -6, 0), (0, -5, 0), "rotor_tip")
    d.box((0, 5, 0), (0, 6, 0), "rotor_tip")
    d.box((0, 0, -6), (0, 0, -5), "rotor_tip")
    d.box((0, 0, 5), (0, 0, 6), "rotor_tip")
    d.box((0, -1, -1), (0, 1, 1), "gunmetal")
    return d

# ------------------------------------------------- assembly + remap
# Part placement exactly as player_chopper.gd _build_visuals (model units,
# before the skid lift): rotor at y=CHOPPER_ROTOR_Y, z=+2; tail rotor and gun
# at their constant pivots.
PART_DEFS = [
    ("ingame-chopper-body-v1",      chopper_body(),   (0, 0, 0)),
    ("ingame-chopper-canopy-v1",    chopper_canopy(), (0, 0, 0)),
    ("ingame-chopper-rotor-v1",     rotor(),          (0, CHOPPER_ROTOR_Y, 2)),
    ("ingame-chopper-tailrotor-v1", tail_rotor(),     CHOPPER_TAIL_ROTOR),
    ("ingame-chopper-gun-v1",       chopper_gun(),    CHOPPER_GUN_MOUNT),
]

ZOFF = 4  # game y=-4 (gun bottom, hangs 1 below the skid line, as in the game) -> vox z=0

def remap(game_dict, offset):
    ox, oy, oz = offset
    out = {}
    for (x, y, z), ci in game_dict.items():
        out[(x + ox, z + oz, y + oy + ZOFF)] = ci
    return out

# ---------------------------------------------------------------- .vox writer (MagicaVoxel 150)
def write_vox(path, vox):
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    assert min(zs) >= 0, "negative z in vox"
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
    print(f"wrote {path} ({len(vox)} voxels) dims=({sx},{sy},{sz}) xoff={xoff} yoff={yoff}")
    return (xoff, yoff)

# ---------------------------------------------------------------- isometric preview render
def render_preview(path, vox, scale=2):
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

def floater_sweep(vox):
    vset = set(vox.keys())
    seen = set()
    comp = []
    stack = [next(iter(vset))]
    while stack:
        p = stack.pop()
        if p in seen:
            continue
        seen.add(p)
        comp.append(p)
        x, y, z = p
        for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                  (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
            if q in vset and q not in seen:
                stack.append(q)
    if len(seen) != len(vset):
        return sorted(vset - seen)
    return []

if __name__ == "__main__":
    import json
    parts = {}
    for name, vd, offset in PART_DEFS:
        parts[name] = remap(vd.d, offset)
    # assembled reference: union of all parts
    asm = {}
    for v in parts.values():
        asm.update(v)
    parts["ingame-chopper-assembled-v1"] = asm

    pivots_game = {
        "rotor": (0, CHOPPER_ROTOR_Y, 2),   # spins about game Y -> vox Z
        "tailrotor": CHOPPER_TAIL_ROTOR,    # spins about game X -> vox X
        "gun": CHOPPER_GUN_MOUNT,           # yaws about game Y -> vox Z
    }
    file_pivots = {}
    for name, vox in parts.items():
        vpath = os.path.join(HERE, name + ".vox")
        ppath = os.path.join(HERE, name + "_preview.png")
        xoff, yoff = write_vox(vpath, vox)
        render_preview(ppath, vox)
        stray = floater_sweep(vox)
        print(f"  floaters: {len(stray)}" + (f" e.g. {stray[:5]}" if stray else ""))
        xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
        print(f"  game-frame bounds x[{min(xs)+0},{max(xs)}] file dims vox "
              f"({max(xs)-min(xs)+1},{max(ys)-min(ys)+1},{max(zs)+1})")
    # pivots in .vox file coords per part
    asm_vox = parts["ingame-chopper-assembled-v1"]
    xs = [p[0] for p in asm_vox]; ys = [p[1] for p in asm_vox]
    xoff, yoff = -min(xs), -min(ys)
    for k, (gx, gy, gz) in pivots_game.items():
        vx, vy, vz = gx + xoff, gz + yoff, gy + ZOFF
        file_pivots[k] = {"game": [gx, gy, gz], "file": [vx, vy, vz]}
    # per-part file pivots: each moving part is authored around its own hub
    # (local origin); the pivot in the part file = remap(offset) + file offset
    part_keys = {"ingame-chopper-rotor-v1": "rotor",
                 "ingame-chopper-tailrotor-v1": "tailrotor",
                 "ingame-chopper-gun-v1": "gun"}
    for name, vd, offset in PART_DEFS:
        if name not in part_keys:
            continue
        vox = parts[name]
        xs = [p[0] for p in vox]; ys = [p[1] for p in vox]
        xo, yo = -min(xs), -min(ys)
        ox, oy, oz = offset
        file_pivots[name + ":" + part_keys[name]] = [ox + xo, oz + yo, oy + ZOFF]
    with open(os.path.join(HERE, "ingame_chopper_pivots.json"), "w") as f:
        json.dump(file_pivots, f, indent=2)
    print("pivots:", json.dumps(file_pivots))
