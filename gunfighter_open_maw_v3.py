#!/usr/bin/env python3
"""
gunfighter_v3.py — Strike Bay "Open Maw" gunfighter, fresh re-authoring.

v3 addresses the v1/v2 "thin dart" read: the concept is a CHUBBY fighter.
Measured from the concept sheet:
  - intake diameter / span ~ 0.22 (v2: 0.12)  -> fuselage r_max 19 (was 11)
  - fuselage depth / length ~ 0.15 (v2: 0.10)
  - span / length ~ 0.94 (v2: 0.82)           -> span +-104 (was +-90)
  - dorsal hump + deep belly (not a straight tube)

Budget: up to 250k voxels, spent on genuine geometry (shell fuselage,
thicker wings, detailed pods, control-surface panel lines), never filler.
Panel lines and tonal variation in shades of grey (palette discipline:
grey + red on the airframe; functional colors only for canopy/pilot/
barrels/nozzle/bore).

Nine destructible parts, one shared frame. x lateral, y forward (nose +y),
z up. FIGHTER_VOXEL 0.075 m -> 221 vox = 16.6 m (MiG-21-to-human).
"""
import math
import os
import struct
import json

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette
# idx0 unused. Greys + red on the airframe; functional colors elsewhere.
PALETTE = [
    None,
    ("airframe",     (178, 184, 190)),   # 1 main light grey
    ("airframe_mid", (138, 144, 150)),   # 2 tonal panel grey
    ("panel",        ( 88,  93,  99)),   # 3 panel lines (dark grey)
    ("red",          (198,  32,  32)),   # 4 markings
    ("groove",       ( 58,  60,  64)),   # 5 deep grooves/vents
    ("blade",        (205, 210, 216)),   # 6 intake splitter (light)
    ("gunmetal",     ( 48,  50,  54)),   # 7 barrels
    ("bore",         ( 16,  16,  18)),   # 8 intake duct interior (near-black)
    ("canopy",       ( 38,  58,  78)),   # 9 glass (functional)
    ("pilot",        ( 74,  84,  62)),   # 10 pilot (functional)
    ("helmet",       (210, 210, 208)),   # 11 helmet (functional)
    ("steel",        (118, 123, 129)),   # 12 nozzle
    ("steel_dark",   ( 78,  83,  89)),   # 13 nozzle dark
    ("airframe_lt",  (160, 165, 170)),   # 14 light tonal step (wings)
]
A, AM, P, R, G, B, M, O, C, PI, H, S, SD, AL = range(1, 15)

parts = {n: {} for n in (
    "core", "canopy", "pilot",
    "wing_l", "wing_r", "guns_l", "guns_r", "fin", "stabilator")}


def box(d, x0, x1, y0, y1, z0, z1, c):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                d[(x, y, z)] = c


# ---------------------------------------------------------------- fuselage
def fuselage_r(y):
    """Outer radius profile. Nose (intake) at y=110, tail tip at y=-110."""
    if y >= 95:
        return 19.0
    if y >= 60:
        return 19.0 + (y - 60) / 35.0 * 3.0      # 19 -> 22
    if y >= -55:
        return 22.0
    if y >= -90:
        return 22.0 - (-55 - y) / 35.0 * 7.0     # 22 -> 15
    return 15.0 - (-90 - y) / 20.0 * 6.0          # 15 -> 9


core = parts["core"]
SHELL_INNER = 0.86   # normalized inner radius -> ~2.5 vox shell at r=19

for y in range(-110, 111):
    r = fuselage_r(y)
    rx, rz = r * 0.96, r * 1.06
    ir = int(math.ceil(rx)) + 1
    iz = int(math.ceil(rz)) + 1
    for x in range(-ir, ir + 1):
        for z in range(-iz, iz + 1):
            d = math.hypot(x / rx, z / rz)
            if d <= 1.0 and d >= SHELL_INNER:
                # tonal panels: alternate slightly darker bands along the body
                c = A
                if (y // 18) % 2 == 1:
                    c = AM
                # panel rings every 18 vox
                if y % 18 == 0:
                    c = P
                # longitudinal panel lines: top + keel only (sides deleted)
                ang = math.degrees(math.atan2(z, x)) % 360
                if min(abs(ang - 90), abs(ang - 270)) < 4:
                    if y % 18 != 0:
                        c = P
                core[(x, y, z)] = c

# dorsal hump: raised spine y 15..85 (solid airframe, ring lines only)
for y in range(15, 86):
    r = fuselage_r(y)
    h = 4.5 * math.sin(math.pi * (y - 15) / 70.0)
    hw = int(r * 0.55)
    for x in range(-hw, hw + 1):
        for dz in range(0, int(h) + 1):
            z = int(r * 1.06) + dz - 1
            if abs(x) < hw * (1 - dz / (h + 1)):
                c = A
                if y % 18 == 0:
                    c = P
                core[(x, y, z)] = c

# intake lip: red outer ring + steel inner ring at the maw (y 107..110)
for y in range(107, 111):
    r = fuselage_r(y)
    for x in range(-20, 21):
        for z in range(-21, 22):
            d = math.hypot(x / (r * 0.96), z / (r * 1.06))
            if 0.97 <= d <= 1.12:
                core[(x, y, z)] = R
            elif 0.86 <= d < 0.97:
                core[(x, y, z)] = S

# intake duct: dark backstop disc deep in the maw (overlaps the shell)
for x in range(-19, 20):
    for z in range(-20, 21):
        if math.hypot(x / 18.5, z / 20.0) <= 1.0:
            core[(x, 84, z)] = O

# splitter blade: full-height divider, bonded to duct walls + backstop
# (solid light grey, no striping)
for y in range(84, 109):
    for z in range(-20, 21):
        for x in (-1, 0, 1):
            core[(x, y, z)] = B

# gun vents: dark slots flanking the nose (gunfighter identity)
for sx in (-1, 1):
    for i in range(6):
        y = 96 - i * 2
        for z in range(2, 8):
            x = sx * (int(fuselage_r(y) * 0.96) - 1)
            if (x, y, z) in core:
                core[(x, y, z)] = G

# red nose band (behind the lip) + red tail band: full rings
for y in list(range(100, 104)) + list(range(-72, -66)):
    r = fuselage_r(y)
    for x in range(-20, 21):
        for z in range(-21, 22):
            d = math.hypot(x / (r * 0.96), z / (r * 1.06))
            if 0.86 <= d <= 1.0:
                core[(x, y, z)] = R

# tail nozzle: steel petals + dark interior
for y in range(-110, -94):
    t = (y + 110) / 16.0  # 0 at tip -> 1 forward
    r = 8.0 + t * 5.0
    for x in range(-14, 15):
        for z in range(-14, 15):
            d = math.hypot(x, z)
            if r - 2.5 <= d <= r:
                core[(x, y, z)] = S if (x + z) % 2 == 0 else SD
            elif d < r - 2.5:
                core[(x, y, z)] = O
# nozzle cap ring
for x in range(-11, 12):
    for z in range(-11, 12):
        d = math.hypot(x, z)
        if 8.0 <= d <= 10.5:
            core[(x, -110, z)] = SD

# ventral strake under the tail
for y in range(-105, -70):
    h = int(6 * (1 - abs(y + 87) / 20.0))
    for z in range(-int(fuselage_r(y) * 1.06) - h, -int(fuselage_r(y) * 1.06) + 1):
        core[(0, y, z)] = A
        core[(1 if y % 2 else -1, y, z)] = A

# twin canted blade antennae on the aft spine (embedded in the shell)
for sx in (-1, 1):
    for i in range(9):
        y = -58 - i
        z0 = int(fuselage_r(y) * 1.06) - 1
        for k in range(6 - i // 2):
            core[(sx * (2 + i // 2), y, z0 + k)] = A

# pitot tube on the intake lip (embedded, extends forward)
for y in range(107, 117):
    core[(12, y, -16)] = M
    core[(13, y, -16)] = M

# ---------------------------------------------------------------- canopy + pilot
canopy = parts["canopy"]
pilot = parts["pilot"]
# teardrop canopy y 52..86, framed: grey frame + dark glass
for y in range(52, 87):
    t = (y - 52) / 34.0
    w = 7.5 * math.sin(math.pi * min(1.0, 0.15 + t * 0.85)) + 1.5
    h = 8.0 * math.sin(math.pi * min(1.0, 0.12 + t * 0.88)) + 1.0
    zbase = int(fuselage_r(y) * 1.06) - 1
    for x in range(-int(w) - 1, int(w) + 2):
        for dz in range(0, int(h) + 2):
            z = zbase + dz
            edge = abs(x) > w - 1.2 or dz > h - 1.0 or dz < 1.0
            if (x / (w + 1)) ** 2 + (dz / (h + 1)) ** 2 <= 1.0:
                canopy[(x, y, z)] = A if edge else C
    # canopy frame ribs every 7 vox
    if y % 7 == 0:
        for x in range(-int(w), int(w) + 1):
            for dz in range(0, int(h) + 1):
                z = zbase + dz
                if (x / w) ** 2 + (dz / h) ** 2 <= 1.0 and abs(x) > w - 2.2:
                    canopy[(x, y, z)] = A
# pilot: seat + torso + helmet (mostly hidden, separate part)
for y in range(60, 74):
    for x in range(-3, 4):
        for z in range(8, 15):
            if abs(x) <= 3 - abs(y - 67) // 4:
                pilot[(x, y, z)] = PI
for x in range(-2, 3):
    for z in range(14, 18):
        if x * x + (z - 15) ** 2 <= 5:
            pilot[(0 + x, 66, z)] = H

# ---------------------------------------------------------------- wings
def build_wing(side, pname):
    w = parts[pname]
    # planform: |x| 8..104, swept, dogtooth, tapered thickness
    for ix in range(8, 105):
        t = (ix - 8) / 96.0
        le = 38 - t * 78.0
        chord = 72 - t * 48.0
        thick = 6 - int(t * 3)          # 6 at root -> 3 at tip
        z0 = 8 - thick // 2
        le_fwd = 10 if 52 <= ix <= 60 else 0   # dogtooth kink
        for iy in range(int(le - chord), int(le + le_fwd) + 1):
            for iz in range(z0, z0 + thick):
                # airfoil-ish: round the slab edges
                edge = (iz == z0 or iz == z0 + thick - 1)
                inset = 1 if edge else 0
                if iy < int(le - chord) + inset and t > 0.05:
                    continue
                c = A
                # light tonal chord bands (subtle, not zebra)
                if ((iy // 14) % 2) == 1:
                    c = AL
                # spanwise panel lines only (chordwise set deleted)
                if ix % 16 == 0:
                    c = P
                w[(side * ix, iy, iz)] = c
    # red wing patches (top surface, 72-80% span): proper patches, not dots
    for mx in range(72, 84):
        for my in range(-32, -22):
            for iz in range(5, 14):
                if (side * mx, my, iz) in w and (side * mx, my, iz + 1) not in w:
                    w[(side * mx, my, iz)] = R
    # flap/aileron hinge lines (dark, top surface)
    for ix in range(14, 100):
        t = (ix - 8) / 96.0
        le = 38 - t * 78.0
        chord = 72 - t * 48.0
        hy = int(le - chord * 0.72)
        for iz in range(5, 14):
            if (side * ix, hy, iz) in w and (side * ix, hy, iz + 1) not in w:
                w[(side * ix, hy, iz)] = P
            if (side * ix, hy + 1, iz) in w and (side * ix, hy + 1, iz + 1) not in w:
                w[(side * ix, hy + 1, iz)] = P
    # wing fences: 2 thin vertical plates per wing (rooted in the slab)
    for fx in (45, 70):
        t = (fx - 8) / 96.0
        le = 38 - t * 78.0
        chord = 72 - t * 48.0
        thick = 6 - int(t * 3)
        ztop = 8 - thick // 2 + thick - 1
        for iy in range(int(le - chord * 0.8), int(le - chord * 0.25)):
            for iz in range(ztop - 1, ztop + 5):
                w[(side * fx, iy, iz)] = A
                w[(side * fx + side, iy, iz)] = AM
    # rounded tip cap (1 vox proud, stays in frame)
    tx = side * 104
    for ox in (0, side):
        for ty in range(-58, -52):
            for tz in (10, 11):
                w[(tx + ox, ty, tz)] = A


build_wing(-1, "wing_l")
build_wing(1, "wing_r")

# ---------------------------------------------------------------- fin
fin = parts["fin"]
for iz in range(2, 48):
    t = (iz - 2) / 45.0
    le = -50 - t * 36
    chord = 60 - t * 42
    if iz < 12:
        le += 12 - iz                     # dorsal fillet blending to spine
    thick = 3 if iz < 30 else 2
    for iy in range(int(le - chord), int(le) + 1):
        for dx in range(-thick // 2, thick // 2 + 1):
            c = A
            if ((iy // 14) % 2) == 1:
                c = AM
            if iz % 12 == 0:
                c = P
            # rudder hinge line (aft 30%)
            if iy < le - chord * 0.70:
                c = P if (iz % 3 == 0) else AM
            # red leading edge
            if iy >= int(le) - 2 and iz < 34:
                c = R
            fin[(dx, iy, iz)] = c
# red fin base band
for iz in range(2, 12):
    for iy in range(-100, -88):
        for dx in (-1, 0, 1):
            if (dx, iy, iz) in fin:
                fin[(dx, iy, iz)] = R

# ---------------------------------------------------------------- stabilators
st = parts["stabilator"]
for side in (-1, 1):
    for ix in range(4, 46):
        t = (ix - 4) / 41.0
        le = -64 - t * 24
        chord = 36 - t * 18
        for iy in range(int(le - chord), int(le) + 1):
            for iz in (-2, -1, 0, 1):
                c = A
                if ((iy // 12) % 2) == 1:
                    c = AM
                if ix % 12 == 0 or (iy - int(le - chord)) % 14 == 0:
                    c = P
                if iy < le - chord * 0.65:   # elevator
                    c = P if iz in (-2, 1) else AM
                st[(side * ix, iy, iz)] = c
# red tips
for side in (-1, 1):
    for ix in range(42, 46):
        for iy in range(-108, -100):
            for iz in (-2, -1, 0, 1):
                if (side * ix, iy, iz) in st:
                    st[(side * ix, iy, iz)] = R
# center section joining the two halves
for x in range(-4, 5):
    for y in range(-100, -64):
        for z in (-2, -1, 0, 1):
            st[(x, y, z)] = A if (y % 12 != 0) else P

# ---------------------------------------------------------------- guns: pods + canon clusters
for side, pname in ((-1, "guns_l"), (1, "guns_r")):
    g = parts[pname]
    cx = side * 30
    px0, px1 = (cx - 5, cx + 5) if side > 0 else (cx - 5, cx + 5)
    # weapon pod: chunky body y -38..6
    for x in range(px0, px1 + 1):
        for y in range(-38, 7):
            for z in range(-10, 2):
                # rounded cross-section
                if ((x - cx) / 6.0) ** 2 + ((z + 4) / 7.0) ** 2 <= 1.0:
                    c = A
                    if (y // 10) % 2 == 1:
                        c = AM
                    if y % 10 == 0:
                        c = P
                    g[(x, y, z)] = c
    # tapered blunt nose
    for y in range(7, 14):
        ins = (y - 7)
        for x in range(px0 + ins, px1 - ins + 1):
            for z in range(-10 + ins, 2 - ins // 2):
                if ((x - cx) / 6.0) ** 2 + ((z + 4) / 7.0) ** 2 <= 1.0:
                    g[(x, y, z)] = A
    # gunmetal nose plate + 3x2 muzzle grid
    for x in range(px0 + 3, px1 - 2):
        for z in range(-7, -1):
            g[(x, 13, z)] = M
    for dx in (-2, 0, 2):
        for mz in (-6, -3):
            g[(cx + dx, 13, mz)] = O
            g[(cx + dx, 13, mz + 1)] = O
    # side cooling grilles
    for y in range(-34, 4, 4):
        for z in range(-8, -2):
            g[(px1 if side > 0 else px0, y, z)] = G
    # gunmetal tail plate
    for x in range(px0, px1 + 1):
        for z in range(-9, 1):
            if ((x - cx) / 6.0) ** 2 + ((z + 4) / 7.0) ** 2 <= 1.0:
                g[(x, -38, z)] = M
    # pylon: pod -> wing (with lightening panel lines)
    for x in range(px0 + 1, px1):
        for y in range(-30, -6):
            for z in range(1, 9):
                c = AM if (y % 8 == 0) else A
                g[(x, y, z)] = c
    # outboard canon cluster: hanger + 3 barrels at |x| 58..68
    mx0, mx1 = (58, 68) if side > 0 else (-68, -58)
    for x in range(mx0, mx1 + 1):
        for y in range(-14, -4):
            for z in range(4, 9):
                g[(x, y, z)] = A
    for bx in (60, 63, 66):
        x = side * bx
        for dx in (0, 1):
            xx = x + (dx if side > 0 else -dx)
            for dz in (4, 5, 6):
                for y in range(-12, 10):
                    g[(xx, y, dz)] = M
                g[(xx, 10, dz)] = O
                # barrel clamp rings
                if y in (-4, 2):
                    pass
        for y in (-4, 2):
            for dz in (4, 5, 6):
                g[(x, y, dz)] = SD
                g[(x + (1 if side > 0 else -1), y, dz)] = SD
    # muzzle blast fairing
    for bx in (60, 63, 66):
        x = side * bx
        for dz in (4, 5, 6):
            g[(x, 11, dz)] = SD
    # spar buried in the wing slab
    sx0, sx1 = (30, 62) if side > 0 else (-62, -30)
    for x in range(sx0, sx1 + 1):
        for y in range(-18, -4):
            for z in range(8, 13):
                g[(x, y, z)] = A

# ---------------------------------------------------------------- frame / pivots / write
FRAME_SIZE = (211, 231, 76)      # x [-105,105], y [-110,120], z [-25,50]
FRAME_OFF = (105, 110, 25)
VOXEL_M = 0.075

PIVOTS = {
    "core": (0, 0, 0),
    "canopy": (0, 70, 20),
    "pilot": (0, 66, 12),
    "wing_l": (-20, 0, 10),
    "wing_r": (20, 0, 10),
    "guns_l": (-30, -14, -4),
    "guns_r": (30, -14, -4),
    "fin": (0, -72, 14),
    "stabilator": (0, -92, 0),
}


def write_vox_frame(path, vox):
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children

    sx, sy, sz = FRAME_SIZE
    ox, oy, oz = FRAME_OFF
    for (x, y, z) in vox:
        assert 0 <= x + ox < sx and 0 <= y + oy < sy and 0 <= z + oz < sz, (x, y, z)
    xyzi = struct.pack("<i", len(vox))
    for (x, y, z), ci in vox.items():
        xyzi += struct.pack("BBBB", x + ox, y + oy, z + oz, ci)
    rgba = b"".join(struct.pack("BBBB", r, g, b, 255) for e in PALETTE if e for _, (r, g, b) in [e])
    rgba += struct.pack("BBBB", 0, 0, 0, 0) * (256 - (len(PALETTE) - 1))
    main_children = (chunk(b"SIZE", struct.pack("<iii", sx, sy, sz))
                     + chunk(b"XYZI", xyzi) + chunk(b"RGBA", rgba))
    with open(path, "wb") as f:
        f.write(b"VOX ")
        f.write(struct.pack("<i", 150))
        f.write(chunk(b"MAIN", b"", main_children))
    print(f"wrote {path} ({len(vox)} voxels)")


def bbox_of(vox):
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
    return [min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)]


def main():
    from preview_camera import render_camera
    manifest_parts = []
    merged = {}
    for name, vox in parts.items():
        path = os.path.join(OUT, f"gunfighter-{name}-v3.vox")
        write_vox_frame(path, vox)
        manifest_parts.append({
            "name": name,
            "file": os.path.basename(path),
            "pivot": list(PIVOTS[name]),
            "voxels": len(vox),
            "bbox_design": bbox_of(vox),
        })
        merged.update(vox)
    mpath = os.path.join(OUT, "gunfighter-merged-v3.vox")
    write_vox_frame(mpath, merged)
    manifest = {
        "model": "gunfighter-open-maw-v3",
        "frame": {"x": "lateral (port -x)", "y": "forward (nose +y)",
                  "z": "up, z=0 through intake-lip plane",
                  "size": list(FRAME_SIZE), "offset": list(FRAME_OFF),
                  "voxel_m": VOXEL_M,
                  "length_m": round(FRAME_SIZE[1] * VOXEL_M, 2),
                  "span_m": round(211 * VOXEL_M, 2)},
        "parts": manifest_parts + [{
            "name": "merged", "file": os.path.basename(mpath),
            "pivot": [0, 0, 0], "voxels": len(merged),
            "bbox_design": bbox_of(merged)}],
    }
    jpath = os.path.join(OUT, "pivot_manifest_v3.json")
    with open(jpath, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"wrote {jpath}")

    pal = [p for p in PALETTE if p]
    render_camera(os.path.join(OUT, "preview_hero_v3.png"), merged, pal,
                  cam_pos=(-95, 215, 85), look_at=(0, 5, 4), scale=5)
    render_camera(os.path.join(OUT, "preview_side_v3.png"), merged, pal,
                  cam_pos=(-270, 5, 4), look_at=(0, 5, 4), scale=4)
    render_camera(os.path.join(OUT, "preview_top_v3.png"), merged, pal,
                  cam_pos=(0, 5, 290), look_at=(0, 5, 4), up=(0, 1, 0), scale=4)
    render_camera(os.path.join(OUT, "preview_nose_v3.png"), merged, pal,
                  cam_pos=(-45, 240, 30), look_at=(0, 95, 0), scale=7,
                  size=(1000, 1000))
    render_camera(os.path.join(OUT, "preview_front_v3.png"), merged, pal,
                  cam_pos=(0, 270, 20), look_at=(0, 0, 0), scale=5,
                  size=(1500, 1100))


if __name__ == "__main__":
    main()
