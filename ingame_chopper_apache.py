#!/usr/bin/env python3
"""Body v3: redesigned rocket pods + tapered tail cone + engines inboard.

v2 rocket pods (more detail, slightly larger) -- kept.
v3 changes (2026-09-29):
  - engine exhausts moved inboard one voxel (x +-6 -> +-5)
  - rear fuselage tapered into the tail boom: the blunt cabin end is
    replaced by a 10-voxel tail cone (w 5->2.5, y 0..10 -> 4..8) flowing
    into the boom
Also removed the vestigial floating canopy-frame crossbar. Then the
standard shorten + 4x upscale, and rebuilds the no-rotor assembly with
the current (v6) canopy -- upload body (230) and assembly (239) every time.
"""
import os
import sys
import math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ingame_chopper_v1 as g
from ingame_chopper_canopy_v6 import build_canopy

# New darker-than-everything olive for the main body. "olive" (the lighter
# drab) is replaced by it; "olive_dark" stays exactly as-is. Appended to the
# shared palette so existing color indices are untouched.
if "olive_deep" not in g.CI:
    g.PALETTE.append(("olive_deep", (g.c8(0.21), g.c8(0.22), g.c8(0.12))))
    g.CI["olive_deep"] = len(g.PALETTE)
# near-black for the pod mouth checkerboard: two tones of black with the
# pure black, much less contrast than the old steel_dark
if "soft_black" not in g.CI:
    g.PALETTE.append(("soft_black", (g.c8(0.17), g.c8(0.18), g.c8(0.21))))
    g.CI["soft_black"] = len(g.PALETTE)
PALETTE = g.PALETTE  # so the viewer parses the new palette name
OLIVE = g.CI["olive"]
OLIVE_DEEP = g.CI["olive_deep"]

S = 4

def build_body4():
    d = g.chopper_body()

    # ---- rear rework: taper the tail cone into the boom, engines inboard --
    # delete everything aft of game z=-8, then rebuild
    for p in [p for p in d.d if p[2] < -8]:
        d.remove(p)
    # tapered tail cone (was a blunt cabin end at z=-10)
    for z in range(-9, -19, -1):
        t = float(-9 - z) / 9.0
        w = max(g.roundi(g.lerpf(5.0, 2.5, t)), 1)
        ylo = g.roundi(g.lerpf(0.0, 4.0, t))
        yhi = g.roundi(g.lerpf(10.0, 8.0, t))
        g._fuselage_slice(d, z, w, ylo, yhi, "olive")
    # tail boom continues from the taper
    for z in range(-18, -37, -1):
        t = float(-18 - z) / 18.0
        r = g.lerpf(2.5, 1.5, t)
        cy = g.roundi(g.lerpf(6.0, 5.0, t))
        d.cylinder(2, (0, cy), r, z, z, "olive")
    d.box((0, 8, -36), (0, 9, -16), "olive_dark")  # boom spine stripe
    # engine nacelles: larger v2-style side engines (outboard, r=2.5)
    for x in (-5, 5):
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                for z in range(-12, 5):
                    d.remove((x + dx, 9 + dy, z))
    for sx in (-1, 1):
        x = sx * 6
        d.cylinder(2, (x, 8), 2.5, -6, 8, "olive")      # main nacelle (green)
        d.cylinder(2, (x, 8), 2.7, 8, 9, "olive_dark")  # intake lip
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                d.remove((x + dx, 8 + dy, 9))
                d.add((x + dx, 8 + dy, 8), "black")     # intake mouth
        d.cylinder(2, (x, 8), 2.0, -8, -6, "dark")     # exhaust taper
        d.cylinder(2, (x, 8), 1.2, -9, -8, "black")    # exhaust mouth
        d.cylinder(2, (x, 8), 2.6, 2, 2, "gunmetal")   # panel line
        # fairings: close the gaps where the round nacelle meets the boxy
        # fuselage, and bridge the engine to the tapering tail at the rear
        # (shifted 2 voxels inboard per user)
        d.box((sx * 3, 6, -6), (sx * 4, 10, 8), "olive")   # side saddle
        d.box((sx * 2, 6, -10), (sx * 4, 9, -6), "olive") # rear bridge
    # engine deck (its z=-9 slice was deleted)
    d.box((-4, 11, -9), (4, 12, 5), "olive_dark")
    d.box((-3, 13, -8), (3, 13, 3), "olive_dark")
    # panel lines (their z -10..-9 segments were deleted)
    d.box((-5, 3, -8), (5, 3, 12), "olive_dark")
    d.box((0, 1, -8), (0, 2, 12), "olive_dark")
    # stabilizer + fin + ventral + tail-rotor gearbox (re-add)
    # stabilizer moved forward 3 (was z -30..-27) to clear the tail rotor
    d.box((-7, 5, -27), (7, 5, -24), "olive_dark")
    d.box((-7, 5, -27), (-7, 6, -24), "olive")
    d.box((7, 5, -27), (7, 6, -24), "olive")
    d.box((0, 5, -37), (0, 13, -33), "olive_dark")
    d.box((0, 13, -38), (0, 13, -32), "olive")
    d.box((0, 0, -37), (0, 4, -35), "olive_dark")
    d.box((0, g.CHOPPER_TAIL_ROTOR[1] - 1, g.CHOPPER_TAIL_ROTOR[2] - 1),
          (g.CHOPPER_TAIL_ROTOR[0] - 1, g.CHOPPER_TAIL_ROTOR[1] + 1,
           g.CHOPPER_TAIL_ROTOR[2] + 1), "gunmetal")

    # ---- stronger rotor mast + mast-mounted sensor pod -------------------
    # remove the old thin mast (cylinder at (0,2), y 13..19)
    for y in range(13, 20):
        for dx in range(-3, 3):
            for dz in range(-3, 3):
                d.remove((dx, y, 2 + dz))
    # wide pylon base on the engine deck, dark shaft up through the rotor
    # plane, sensor ball above the blades
    d.cylinder(1, (0, 2), 2.8, 12, 15, "olive_deep")
    d.cylinder(1, (0, 2), 1.8, 15, 24, "dark")
    d.cylinder(1, (0, 2), 2.3, 19, 20, "gunmetal")    # collar at rotor plane
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            for dz in range(-2, 3):
                if dx * dx + dy * dy + dz * dz <= 5:
                    d.add((dx, 24 + dy, 2 + dz), "dark")  # sensor ball
    d.add((0, 24, 5), "black")
    d.add((1, 24, 5), "black")                        # front windows

    # ---- nose: bulbous ship-bow front --------------------------------------
    # delete the old nose (game z > 12)
    for p in [p for p in d.d if p[2] > 12]:
        d.remove(p)
    # full body to z=19, then a rounded bulbous cap (ship's bow, not a taper)
    # the deck slopes down off the canopy windshield to the blunt front
    for z in range(13, 20):
        g._fuselage_slice(d, z, 5, 0, 9, "olive_deep")
    for z in range(20, 25):
        t = float(z - 19) / 5.0
        s = math.sqrt(max(1.0 - t * t, 0.0))  # rounded, not linear
        w = max(g.roundi(2.5 + 2.5 * s), 1)
        yhi = g.roundi(9.0 - 2.5 * (1.0 - s))  # deck slopes down forward
        ylo = g.roundi(0.0 + 3.0 * (1.0 - s))  # keel rises
        g._fuselage_slice(d, z, w, ylo, yhi, "olive_deep")
    # static sensor hint at the blunt front (not rigged)
    for y in (4, 5):
        if (0, y, 24) in d.d:
            d.d[(0, y, 24)] = g.CI["black"]
        d.add((0, y, 25), "black")
    for x in (-2, 2):
        for y in (4, 5):
            if (x, y, 23) not in d.d:
                d.add((x, y, 23), "gunmetal")

    # ---- rocket pod swap (unchanged v2 design) ----------------------------

    # remove the old pods (exact voxels, via a temp VD)
    old = g.VD()
    for x in (-11, 11):
        old.cylinder(2, (x, 3), 2.0, -6, 7, "olive_dark")
        old.cylinder(2, (x, 3), 1.2, 7, 8, "dark")
        old.cylinder(2, (x, 3), 0.6, 8, 8, "deck_line")
        old.cylinder(2, (x, 3), 1.6, -7, -6, "black")
    for p in old.d:
        d.remove(p)

    # remove the vestigial floating canopy-frame crossbar (old canopy frame
    # bar at game (x -2..2, y 8, z 12) -- disconnected, and it would show
    # through the new glasshouse)
    for x in range(-2, 3):
        d.remove((x, 8, 12))

    # new detailed pods: larger diameter (r=3.5, one more row), inset faces
    # front AND rear (mirrored). At y=3 (one voxel down per user).
    for x in (-11, 11):
        d.cylinder(2, (x, 3), 3.5, -5, 5, "olive_dark")   # main tube
        d.cylinder(2, (x, 3), 3.7, -2, -1, "gunmetal")    # band 1
        d.cylinder(2, (x, 3), 3.7, 2, 3, "gunmetal")     # band 2
        d.cylinder(2, (x, 3), 3.5, -7, -5, "olive_dark")  # rear cap
        d.cylinder(2, (x, 3), 3.5, 5, 7, "olive_dark")    # front nose
        # inset 7-tube faces, front (z=7) and rear (z=-7) mirrored
        for zf, zd in ((7, 6), (-7, -6)):
            for dx in (-1, 0, 1):                         # hollow 3x3
                for dy in (-1, 0, 1):
                    d.remove((x + dx, 3 + dy, zf))
            for dx in range(-4, 5):                        # gunmetal rim
                for dy in range(-4, 5):
                    if 9.0 < dx * dx + dy * dy <= 12.5:
                        p = (x + dx, 3 + dy, zf)
                        if p in d.d:
                            d.add(p, "gunmetal")
            for dx in (-1, 0, 1):                         # dark recess floor
                for dy in (-1, 0, 1):
                    d.add((x + dx, 3 + dy, zd), "dark")
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1),  # 7 tubes
                           (0, -1), (1, 1), (-1, -1)):
                cn = "black" if (dx + dy) % 2 == 0 else "soft_black"
                d.add((x + dx, 3 + dy, zd), cn)

    # repaint stub wings (old pod tops overlapped the wing bottom row)
    for x in range(-15, 16):
        ax = abs(x)
        z_lo = -3 if ax < 7 else -2
        z_hi = 4 if ax < 7 else 3
        d.box((x, 5, z_lo), (x, 7 if ax < 9 else 6, z_hi), "olive")
    d.box((-15, 7, -1), (15, 7, 1), "olive_dark")

    # swap the lighter olive drab for the new darker olive (olive_dark kept)
    # -- after all geometry (incl. wing repaint) is in, before remap
    d.d = {p: (OLIVE_DEEP if ci == OLIVE else ci) for p, ci in d.d.items()}

    # stub wings were repainted above; olive swap happens before remap
    vox1 = g.remap(d.d, (0, 0, 0))
    CUT_LO, CUT_HI = -22, -20
    short1 = {}
    for (x, y, z), ci in vox1.items():
        if CUT_LO <= y < CUT_HI:
            continue
        if y < CUT_LO:
            y += (CUT_HI - CUT_LO)
        short1[(x, y, z)] = ci

    out = {}
    for (x, y, z), ci in short1.items():
        bx, by, bz = x * S, y * S, z * S
        for dx in range(S):
            for dy in range(S):
                for dz in range(S):
                    out[(bx + dx, by + dy, bz + dz)] = ci
    return out

def build_assembly(body4, canopy4):
    parts1 = {}
    for name, vd, offset in g.PART_DEFS:
        parts1[name] = g.remap(vd.d, offset)
    asm = dict(body4)
    asm.update(canopy4)
    try:
        from ingame_chopper_gun_4barrel import build_gun4
        asm.update(build_gun4())  # 4-barrel chin gun (id 232)
    except ImportError:
        out = {}
        for (x, y, z), ci in parts1["ingame-chopper-gun-v1"].items():
            bx, by, bz = x * S, y * S, z * S
            for dx in range(S):
                for dy in range(S):
                    for dz in range(S):
                        out[(bx + dx, by + dy, bz + dz)] = ci
        asm.update(out)
    tr = {}
    for (x, y, z), ci in parts1["ingame-chopper-tailrotor-v1"].items():
        bx, by, bz = x * S, (y + 2) * S, z * S
        for dx in range(S):
            for dy in range(S):
                for dz in range(S):
                    tr[(bx + dx, by + dy, bz + dz)] = ci
    asm.update(tr)
    return asm

if __name__ == "__main__":
    body4 = build_body4()
    xs = [p[0] for p in body4]; ys = [p[1] for p in body4]; zs = [p[2] for p in body4]
    bd = (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) + 1)
    print(f"body v2: {len(body4)} vox, dims={bd}")
    print("body floaters:", len(g.floater_sweep(body4)))
    vpath = os.path.join(HERE, "ingame-chopper-4x-apache-body-v1.vox")
    ppath = os.path.join(HERE, "ingame-chopper-4x-apache-body-v1_preview.png")
    g.write_vox(vpath, body4)
    g.render_preview(ppath, body4, scale=1)

    canopy4 = build_canopy()
    asm4 = build_assembly(body4, canopy4)
    ax = [p[0] for p in asm4]; ay = [p[1] for p in asm4]; az = [p[2] for p in asm4]
    ad = (max(ax) - min(ax) + 1, max(ay) - min(ay) + 1, max(az) + 1)
    print(f"assembly: {len(asm4)} vox, dims={ad}")
    assert all(x <= 255 for x in ad)
    apath = os.path.join(HERE, "ingame-chopper-4x-apache-assembled-no-rotor-v1.vox")
    aprev = os.path.join(HERE, "ingame-chopper-4x-apache-assembled-no-rotor-v1_preview.png")
    g.write_vox(apath, asm4)
    g.render_preview(aprev, asm4, scale=1)
    print("done")
