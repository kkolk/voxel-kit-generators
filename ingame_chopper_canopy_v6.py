#!/usr/bin/env python3
"""Canopy v6: 9 flat panels with sloped sides and a raked windshield.

v4 was fully axis-aligned (boxy but slab-sided). v5 keeps the 9-panel
division and gunmetal frames, but each panel is now a single flat plane:
  - side windows slope inward going up (tumblehome), one clean plane
  - windshield rakes back going up, one clean plane
  - roof stays flat (2 panels: the bar above the rear pilot seat was removed,
    merging rear+mid roof), rear window stays vertical

Built as a tapered solid -> 2-thick 3D shell (6-direction depth-2 erosion,
which keeps sloped faces connected) -> frames recolored to gunmetal,
leaving 8 separate glass panels. All in the 4x frame. Also rebuilds the
no-rotor assembly (id 239) so it stays in sync -- upload both every time.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ingame_chopper_v1 as g

S = 4

def hw(z):
    """Half-width of the canopy at height z (sloped sides)."""
    return 17 - (z - 48) * 0.25 if z <= 68 else 12.0

def yf(z):
    """Front y of the canopy at height z (raked windshield, shallower)."""
    if z <= 50:
        return 74
    if z <= 68:
        return 74 - (z - 50) * 0.28
    return 69

def build_canopy():
    pal_idx = {name: i + 1 for i, (name, _) in enumerate(g.PALETTE)}
    glass, metal = pal_idx["canopy_glass"], pal_idx["gunmetal"]

    solid = set()
    for z in range(48, 71):
        rhw, ryf = int(round(hw(z))), int(round(yf(z)))
        for x in range(-rhw, rhw + 1):
            for y in range(30, ryf + 1):
                solid.add((x, y, z))

    # 2-thick 3D shell via erosion (keeps sloped faces connected)
    D6 = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    vox = {}
    for p in solid:
        interior = True
        for dx, dy, dz in D6:
            for d in (1, 2):
                if (p[0]+dx*d, p[1]+dy*d, p[2]+dz*d) not in solid:
                    interior = False
                    break
            if not interior:
                break
        if not interior:
            vox[p] = glass

    def frame(p):
        rhw = int(round(hw(p[2])))
        ryf = int(round(yf(p[2])))
        x, y, z = p
        if z <= 49:
            return True  # base perimeter
        is_roof = z >= 68
        is_front = y >= ryf - 1
        is_rear = y <= 31
        if is_front and not is_roof:
            return abs(x) >= rhw - 2 or z >= 66      # windshield surround
        if is_roof:
            return (53 <= y <= 55                       # roof cross frame
                    # (the 41..43 bar above the rear pilot seat was removed)
                    or y >= 64 or y <= 33            # roof front/back edges
                    or abs(x) >= rhw - 2)            # roof rails
        if is_rear:
            return abs(x) >= rhw - 2 or z >= 66      # rear surround
        # side walls
        return (53 <= y <= 55        # side mid-post
                or z >= 66          # roof rail (side top edge)
                or y <= 33          # side rear edge
                or y >= ryf - 3)    # side front edge (meets windshield)

    for p in list(vox):
        if frame(p):
            vox[p] = metal

    # verify 9 separate glass panels
    panels, seen = [], set()
    for p, ci in vox.items():
        if ci != glass or p in seen:
            continue
        stack, reg = [p], []
        while stack:
            q = stack.pop()
            if q in seen:
                continue
            seen.add(q)
            reg.append(q)
            x, y, z = q
            for d in D6:
                r = (x+d[0], y+d[1], z+d[2])
                if vox.get(r) == glass and r not in seen:
                    stack.append(r)
        panels.append(reg)
    print(f"glass regions: {len(panels)} (want 8)")
    for i, reg in enumerate(sorted(panels, key=len, reverse=True)):
        xs = [p[0] for p in reg]; ys = [p[1] for p in reg]; zs = [p[2] for p in reg]
        print(f"  panel {i+1}: {len(reg)} vox "
              f"x {min(xs)}..{max(xs)} y {min(ys)}..{max(ys)} z {min(zs)}..{max(zs)}")
    return vox

def upscale(vox):
    out = {}
    for (x, y, z), ci in vox.items():
        bx, by, bz = x * S, y * S, z * S
        for dx in range(S):
            for dy in range(S):
                for dz in range(S):
                    out[(bx + dx, by + dy, bz + dz)] = ci
    return out

def build_assembly(canopy4):
    parts1 = {}
    for name, vd, offset in g.PART_DEFS:
        parts1[name] = g.remap(vd.d, offset)
    CUT_LO, CUT_HI = -22, -20
    short1 = {}
    for (x, y, z), ci in parts1["ingame-chopper-body-v1"].items():
        if CUT_LO <= y < CUT_HI:
            continue
        if y < CUT_LO:
            y += (CUT_HI - CUT_LO)
        short1[(x, y, z)] = ci
    asm = dict(upscale(short1))
    asm.update(canopy4)
    asm.update(upscale(parts1["ingame-chopper-gun-v1"]))
    tr = {(x, y + 2, z): ci for (x, y, z), ci in
          parts1["ingame-chopper-tailrotor-v1"].items()}
    asm.update(upscale(tr))
    return asm

if __name__ == "__main__":
    canopy4 = build_canopy()
    xs = [p[0] for p in canopy4]; ys = [p[1] for p in canopy4]; zs = [p[2] for p in canopy4]
    print(f"canopy v5: {len(canopy4)} vox, "
          f"dims=({max(xs)-min(xs)+1},{max(ys)-min(ys)+1},{max(zs)+1})")
    print("canopy floaters:", len(g.floater_sweep(canopy4)))

    parts1 = {}
    for name, vd, offset in g.PART_DEFS:
        parts1[name] = g.remap(vd.d, offset)
    body1 = parts1["ingame-chopper-body-v1"]
    base = [(x//4, y//4, z//4) for (x, y, z) in canopy4 if z < 52]
    supported = sum(1 for (x, y, z) in base
                    if any((x+dx, y+dy, z-dz) in body1
                           for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                           for dz in (1, 2, 3)))
    print(f"base support: {supported}/{len(base)}")

    vpath = os.path.join(HERE, "ingame-chopper-4x-canopy-v1.vox")
    ppath = os.path.join(HERE, "ingame-chopper-4x-canopy-v1_preview.png")
    g.write_vox(vpath, canopy4)
    g.render_preview(ppath, canopy4, scale=2)

    asm4 = build_assembly(canopy4)
    ax = [p[0] for p in asm4]; ay = [p[1] for p in asm4]; az = [p[2] for p in asm4]
    ad = (max(ax) - min(ax) + 1, max(ay) - min(ay) + 1, max(az) + 1)
    print(f"assembly: {len(asm4)} vox, dims={ad}")
    assert all(d <= 255 for d in ad)
    apath = os.path.join(HERE, "ingame-chopper-4x-assembled-no-rotor-v1.vox")
    aprev = os.path.join(HERE, "ingame-chopper-4x-assembled-no-rotor-v1_preview.png")
    g.write_vox(apath, asm4)
    g.render_preview(aprev, asm4, scale=1)
    print("done")
