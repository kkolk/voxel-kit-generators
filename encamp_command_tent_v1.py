#!/usr/bin/env python3
"""encamp_command_tent_v1.py — Strike Bay encampment CANVAS family: Command Tent.

Gitea kkolk/strike-bay #667. Concept:
.claude/workspace/encampment/command-tent-concept.png

RENDER NOTE: the open front faces file -y. Render the contact sheet WITH
--nose-neg-y (it flips x so the FRONT-LEFT panel shows the -y face);
gameview.py flips internally.

LANDMARK MAP (file coords; z-up, 1 voxel = 0.15 m, origin at the pad
footprint min corner, ground level = pad top z=1, front faces file -y):

  FRAME: +x right when viewed from the front, +y toward the rear,
         +z up. FRONT is -y (the open long side, wall plane y=6).
         LEFT is -x. DOOR_POINT y=3 < tent front y=6.

  PAD:      patchy dirt pad (#7a5a3a base, two darker + one lighter
            tone, flat 4x4 patches) with a grass-tuft fringe: x 2..50,
            y 2..32, z=0 (ground surface z=1). Worn packed dirt inside
            the tent and on the door path.
  TENT:     house-shaped ridge tent: vertical panelled walls z 1..8
            (~1.2 m) on both long sides and both gables; roof pitch
            above the eaves (eave z=8, ridge z=18). The BACK slope is
            full canvas (y 17..28, 2-voxel overhang past the rear
            wall); the FRONT slope is propped open as an AWNING: a
            canvas sheet at z 7..9 running ~1.2 m forward from the
            eave line (y 1..5) on two thin poles at (17, 2) and
            (43, 2), guyed to the front stakes — so the game camera
            (yaw 0) looks into the tent. Canvas: flat panels running
            eave-to-ridge (vertical strips 4-6 wide, three olive tones
            #5f6b3a / #6b7842 / #545f33), 1-voxel dark seams, dark hem
            band at the wall bottoms, large darker camo patches
            (#454f2a). Ridge pole along x at y=16, z 18..19, ends
            poking past the gables.
  FRONT:    the -y long side is open on its right two-thirds (x>=16,
            z 4..8 clear). Left third (x 5..15) closed canvas with a
            paper notice inside. Opening framed by full-height dark
            posts at (15, 6) and (44, 6). Rolled-up wall: 2x2 canvas
            tube (y 6, z 2..3) with dark tie straps at x 22/33.
  DOOR_POINT (24, 3, 1): on the worn dirt in front of the open section.
  INTERIOR (all under the open front — visible at game yaw 0): map
            table (x 15..26, y 7..10, top z=6, light wood) with pale
            paper map; folding chair behind it (x 19..21, y 11..13,
            seat z=4); two lanterns, 2x2x3 with bright #f2c84b cores,
            hung from the awning edge at (22, 6) and (36, 6), bodies
            z 4..7; crate stacks at the right wall (x 39..43) and a
            loose crate by the table. Lighter packed-dirt floor. Rear
            (lean): desk + plain sign plate + shelf with a slate
            radio box (light dots) against the rear wall.
  CRATES:   solid boxes: olive #5a6b2f sides, lighter #7a8b45 tops,
            tan #a8763a lid bands, 1-voxel darker rim on the vertical
            edges only. Front-left stack 5x4 (2 high) at (4..8, 3..6),
            front-right stack 4x3 (2 high) at (45..48, 3..5), three
            spilling from the opening.
  FLAGPOLE: front-right corner, (45, 8), pole z=1..27 (4.05 m, ~1.5x
            the 18-voxel ridge), rope bands near the top. FLAG_PIVOT
            (45, 8, 25): the flag part hangs from there — a 7x5 olive
            flag with a 2-voxel-thick pale-yellow V chevron, flying
            toward +x (right).
  GUY ROPES: eave corners to stakes at the pad corners (3,3) (3,31)
            (49,3) (49,31), plus the two awning guys.

  PARTS:
    body  — everything static. One 6-connected component.
    flag  — the olive chevron flag; own part so it can sway later.
            Pivot FLAG_PIVOT = (45, 8, 25) in file coords.

Printed by the generator: FOOTPRINT, HEIGHT, DOOR_POINT (y < tent front
y, proving the opening is at low y), FLAG_PIVOT, per-part counts and
component counts.
"""

import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from encamp_canvas import (box, pole, beam_x, guy_rope, stake, flag_pole,
                           dirt_patch_pad, n_components, bbox)

# ---------------------------------------------------------------- palette
PALETTE = []  # (name, (r, g, b))


def P(name, rgb):
    PALETTE.append((name, tuple(int(v) for v in rgb)))
    return len(PALETTE)


DIRT = P("dirt", (122, 90, 58))             # #7a5a3a pad base
DIRT_DARK = P("dirt_dark", (104, 76, 48))
DIRT_DARK2 = P("dirt_dark2", (94, 68, 42))
DIRT_LIGHT = P("dirt_light", (140, 106, 70))
DIRT_PACKED = P("dirt_packed", (110, 82, 54))    # #6e5236 interior floor
DIRT_PATCH = P("dirt_patch", (94, 67, 42))       # #5e432a floor blobs
GRASS = P("grass", (110, 128, 70))
GRASS_DARK = P("grass_dark", (86, 102, 54))
TIMBER = P("timber", (176, 140, 92))
TIMBER_DARK = P("timber_dark", (120, 88, 52))
POST_DARK = P("post_dark", (84, 60, 34))    # opening posts, dark wood
CANVAS = P("canvas", (95, 107, 58))         # #5f6b3a
CANVAS_B = P("canvas_b", (107, 120, 66))    # #6b7842
CANVAS_C = P("canvas_c", (84, 95, 51))      # #545f33
CANVAS_SEAM = P("canvas_seam", (62, 70, 38))
CANVAS_HEM = P("canvas_hem", (52, 59, 32))
CANVAS_PATCH = P("canvas_patch", (69, 79, 42))   # #454f2a
CANVAS_ROLL = P("canvas_roll", (78, 88, 48))    # darker than roof panels
CRATE_OLIVE = P("crate_olive", (90, 107, 47))    # #5a6b2f sides
CRATE_SLATE = P("crate_slate", (74, 80, 88))     # #4a5058
CRATE_TOP = P("crate_top", (122, 139, 69))       # #7a8b45 tops
CRATE_LID = P("crate_lid", (168, 118, 58))       # #a8763a lid band
CRATE_DARK = P("crate_dark", (58, 66, 32))       # vertical-edge rim
PAPER = P("paper", (226, 219, 192))
LANTERN = P("lantern", (96, 80, 44))
LANTERN_GLOW = P("lantern_glow", (242, 200, 75))  # #f2c84b core
ROPE = P("rope", (82, 68, 48))
FLAG_OLIVE = P("flag_olive", (104, 116, 60))
FLAG_CHEVRON = P("flag_chevron", (228, 196, 84))

CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

# ---------------------------------------------------------------- landmarks
DOOR_POINT = (24, 3, 1)
FLAG_PIVOT = (45, 8, 25)
FLAGPOLE = (45, 8)
POLE_TOP = 27            # ~1.5x the 18-voxel ridge: 4.05 m pole

# tent geometry
TX0, TX1 = 5, 46         # walls' x span (exclusive)
TY0, TY1 = 6, 27         # walls' y span (exclusive); FRONT wall plane y=TY0
EAVE_Z = 8               # vertical walls z 1..7, eaves at z8
RIDGE_Z = 15             # ridge z at y=17
MIDY = 17                # ridge line y (rater cross-section)
FRONT_OPEN_X = 16        # front wall closed left of this x
AWN_Y0 = 0               # awning tip 4 voxels past the front eave (y4)
AWNING_TIP_Z = 6         # awning outer edge height (shallow pitch)

FOOTPRINT = (53, 35)     # pad x 2..50, y 2..32 (7.2 x 4.6 m)
HEIGHT = POLE_TOP

# panel strips across x (panels run eave-to-ridge): width, tone name
_STRIPS = [(5, "canvas"), (4, "canvas_b"), (6, "canvas_c"), (5, "canvas"),
           (4, "canvas_b"), (5, "canvas_c"), (6, "canvas"), (4, "canvas_b"),
           (5, "canvas"), (5, "canvas_c")]


def _panel(x):
    """Flat panel tone for column x: 1-voxel dark seam on each strip's
    first column. Deterministic, no per-voxel noise."""
    acc = TX0 - 2
    for w, tone in _STRIPS:
        if acc <= x < acc + w:
            return "canvas_seam" if x == acc else tone
        acc += w
    return "canvas"


def _roof_z(y):
    """Straight slopes: ridge z15 at y=17, reaching the eave z8 AT the
    wall planes (y=6 front, y=26 rear); the 2-voxel overhang rows keep
    falling past them."""
    if abs(y - MIDY) <= 10:
        return RIDGE_Z - int(round(abs(y - MIDY) * 7 / 10.0))
    return max(EAVE_Z - (abs(y - MIDY) - 10), 5)   # overhang drop-off


def _gable_top(y):
    """Gable canvas top at y: house shape — walls to EAVE_Z everywhere,
    pitched triangle above (same unified pitch as the roof)."""
    return max(_roof_z(y), EAVE_Z)


def _walls(d):
    """Vertical panelled walls on both long sides (closed sections) with
    hem bands; the front's right two-thirds stays open."""
    for x in range(TX0, TX1):
        for y in (TY0, TY1 - 1):
            if y == TY0 and x >= FRONT_OPEN_X:
                continue  # open front
            for wz in range(1, EAVE_Z):
                d[(x, y, wz)] = (CI["canvas_hem"] if wz <= 2
                                 else CI[_panel(x)])


def _roof(d):
    """Both roof slopes, ridge to both eaves (y 4..30), 1 past the gables
    in x. Camo patches on both slopes."""
    for x in range(TX0 - 1, TX1 + 1):
        for y in range(4, 31):
            z = _roof_z(y)
            if y < MIDY and z <= 11:
                continue                # rolled-up front: slope cut at z11
            d[(x, y, z)] = CI[_panel(x)]
    for (x0, x1, y0, y1) in ((8, 18, 18, 22), (24, 34, 20, 24), (30, 40, 9, 13)):
        for x in range(x0, x1):
            for y in range(y0, y1):
                if (x in (x0, x1 - 1) or y in (y0, y1 - 1)) and (x + y) % 3 == 0:
                    continue
                z = _roof_z(y)
                if (x, y, z) in d:
                    d[(x, y, z)] = CI["canvas_patch"]


def _gables(d):
    """House-shaped panelled gables at both short ends: vertical wall to
    the eaves, pitched triangle above, hem band at the bottom."""
    for x in (TX0, TX1 - 1):
        for y in range(TY0, TY1):
            top = _gable_top(y)
            for wz in range(1, top):
                d[(x, y, wz)] = (CI["canvas_hem"] if wz <= 2
                                 else CI[_panel(x)])


def _awning(d):
    """Propped front roof panel: canvas sheet z 7..9 from the eave line
    forward (y 1..5) on two thin poles, guyed to the front stakes. The
    area behind it (y 6..15) stays open to the sky so the game camera
    looks into the tent."""
    # front eave beam ties the roof to the wall tops
    beam_x(d, CI, FRONT_OPEN_X - 1, TX1, TY0, EAVE_Z, "timber_dark")
    # rolled canvas tube along the cut edge (y 11..12, z 11..12)
    for x in range(TX0 - 1, TX1 + 1):
        for (yy, zz) in ((12, 11), (12, 12), (11, 11), (11, 12)):
            d[(x, yy, zz)] = CI["canvas_roll"]
        if x % 8 == 4:                          # tie straps
            for (yy, zz) in ((12, 11), (12, 12), (11, 11), (11, 12)):
                d[(x, yy, zz)] = CI["canvas_seam"]



def _frame(d):
    """Ridge pole (ends poke past the gables), rear eave beam, corner
    posts, full-height dark opening posts."""
    beam_x(d, CI, TX0 - 1, TX1 + 1, MIDY, RIDGE_Z, "timber_dark")
    d[(TX0 - 1, MIDY, RIDGE_Z + 1)] = CI["timber_dark"]
    d[(TX1, MIDY, RIDGE_Z + 1)] = CI["timber_dark"]
    beam_x(d, CI, TX0, TX1, TY1 - 1, EAVE_Z, "timber_dark")
    # rear eave row at z8 ties the wall tops (z7) to the roof slope
    beam_x(d, CI, TX0 - 1, TX1 + 1, TY1 - 1, EAVE_Z, "timber_dark")
    for x in (TX0, TX1 - 1):
        for y in (TY0, TY1 - 1):
            pole(d, CI, x, y, 1, EAVE_Z, "timber_dark")
    # opening posts: dark wood, full height to the rolled cut (z12)
    pole(d, CI, FRONT_OPEN_X - 1, TY0, 1, 12, "post_dark")
    pole(d, CI, TX1 - 2, TY0, 1, 12, "post_dark")


def _crate(d, x, y, z, w, dpt, h, tone):
    """Solid crate: tone sides, lighter top, tan lid band under the top,
    1-voxel darker rim on the vertical edges only."""
    for xx in range(x, x + w):
        for yy in range(y, y + dpt):
            for zz in range(z, z + h):
                vrim = (xx in (x, x + w - 1) or yy in (y, y + dpt - 1))
                if zz == z + h - 1:
                    d[(xx, yy, zz)] = CI["crate_top"]
                elif zz == z + h - 2:
                    d[(xx, yy, zz)] = CI["crate_lid"]
                elif vrim:
                    d[(xx, yy, zz)] = CI["crate_dark"]
                else:
                    d[(xx, yy, zz)] = CI[tone]


def _stack(d, x, y, tones, sizes):
    zz = 1
    for tone, (w, dpt, h) in zip(tones, sizes):
        _crate(d, x, y, zz, w, dpt, h, tone)
        zz += h


def _interior(d):
    """Everything under the open front — table, chair, lanterns, crates —
    plus the lean rear desk/shelf/radio."""
    # packed-dirt floor inside the tent, a few blob-sized darker patches
    for x in range(TX0 + 1, TX1 - 1):
        for y in range(TY0 + 1, TY1 - 1):
            d[(x, y, 0)] = CI["dirt_packed"]
    for (bx, by) in ((9, 20), (24, 12), (34, 22), (28, 9), (38, 17)):
        for dx in range(3):
            for dy in range(2):
                if (bx + dx, by + dy, 0) in d:
                    d[(bx + dx, by + dy, 0)] = CI["dirt_patch"]
    # map table just inside the mouth (y 7..10, open sky above: visible)
    box(d, CI, 15, 27, 7, 11, 6, 7, "timber")
    for zz in range(1, 6):
        for (lx, ly) in ((16, 8), (25, 8), (16, 10), (25, 10)):
            d[(lx, ly, zz)] = CI["timber_dark"]
    box(d, CI, 17, 25, 7, 10, 7, 8, "paper")
    # folding chair behind the table
    box(d, CI, 19, 22, 11, 13, 4, 5, "timber_dark")
    for zz in range(1, 4):
        d[(19, 12, zz)] = CI["timber_dark"]
        d[(21, 12, zz)] = CI["timber_dark"]
    # two lanterns, 2x2x3 with bright cores, hung from the awning's
    # front beam just inside the mouth (y 6; nothing above them)
    for lx in (22, 36):
        d[(lx, TY0, EAVE_Z)] = CI["rope"]
        d[(lx, TY0, EAVE_Z - 1)] = CI["rope"]
        for zz in range(EAVE_Z - 4, EAVE_Z - 1):     # 2x2x3 body
            for xx in (lx, lx + 1):
                d[(xx, TY0, zz)] = CI["lantern"]
        d[(lx, TY0, EAVE_Z - 5)] = CI["lantern_glow"]
        d[(lx + 1, TY0, EAVE_Z - 5)] = CI["lantern_glow"]
    # crates: one loose by the table, stacks at the right wall
    _crate(d, 29, 7, 1, 3, 3, 3, "crate_olive")
    _stack(d, 40, 8, ["crate_olive", "crate_slate"], [(4, 4, 3), (4, 4, 3)])
    _crate(d, 40, 14, 1, 3, 4, 3, "crate_olive")
    _stack(d, 39, 19, ["crate_olive", "crate_slate"], [(3, 3, 3), (3, 3, 3)])
    # back wall: 2-high row of olive/slate crates along y=24
    row_tones = ["crate_olive", "crate_slate", "crate_olive", "crate_olive",
                 "crate_slate", "crate_olive", "crate_slate", "crate_olive"]
    cx = TX0 + 2
    for tone in row_tones:
        _crate(d, cx, 23, 1, 4, 3, 3, tone)
        _crate(d, cx, 23, 4, 4, 3, 3, "crate_olive" if tone == "crate_slate" else "crate_slate")
        cx += 4
    # map board on an easel, left of the desk: light panel + dark map lines
    pole(d, CI, 27, 23, 1, 4, "timber_dark")
    pole(d, CI, 30, 23, 1, 4, "timber_dark")
    box(d, CI, 26, 31, 23, 24, 4, 7, "paper")
    for lx in (27, 28, 29):
        d[(lx, 24, 6)] = CI["timber_dark"]
        d[(lx, 24, 5)] = CI["timber_dark"] if lx == 28 else CI["paper"]
    # second folding chair at the table (opposite side)
    box(d, CI, 19, 22, 7, 9, 4, 5, "timber_dark")
    for zz in range(1, 4):
        d[(19, 8, zz)] = CI["timber_dark"]
        d[(21, 8, zz)] = CI["timber_dark"]
    # rear (lean): desk + plain sign + shelf with a slate radio
    box(d, CI, 30, 39, 23, 26, 5, 7, "timber")
    for zz in range(1, 5):
        for yy in (23, 25):
            for xx in (30, 38):
                d[(xx, yy, zz)] = CI["timber_dark"]
    box(d, CI, 33, 37, 25, 26, 9, 12, "timber_dark")  # sign: plain plate
    box(d, CI, 8, 13, 24, 26, 5, 6, "timber_dark")
    box(d, CI, 30, 34, 24, 25, 7, 9, "crate_slate")
    d[(31, 24, 8)] = CI["lantern_glow"]
    d[(33, 24, 8)] = CI["lantern_glow"]
    # paper notice on the inner face of the closed front-left wall
    box(d, CI, 7, 10, 7, 8, 4, 6, "paper")


def build_body(rng):
    d = {}
    dirt_patch_pad(d, CI, rng, 2, 51, 0, 34,
                   base="dirt", dark="dirt_dark", dark2="dirt_dark2",
                   light="dirt_light", grass="grass", grass_dark="grass_dark")
    # trodden path from the door point into the tent
    for y in range(2, TY0 + 5):
        for x in range(22, 27):
            if rng.random() < 0.7:
                d[(x, y, 0)] = CI["dirt_packed"]
    _frame(d)
    _walls(d)
    _gables(d)
    _roof(d)
    _awning(d)
    # rolled-up front wall: 2-high tube on the wall plane + tie straps
    for x in range(FRONT_OPEN_X, TX1 - 2):
        d[(x, TY0, 2)] = CI["canvas_roll"]
        d[(x, TY0, 3)] = CI["canvas_roll"]
    for sx in (22, 33):
        d[(sx, TY0, 2)] = CI["canvas_seam"]
        d[(sx, TY0, 3)] = CI["canvas_seam"]
    _interior(d)
    # front corner crate stacks + spill (olive-dominant, light tops)
    _stack(d, 4, 3, ["crate_olive", "crate_olive"],
           [(5, 4, 4), (5, 4, 3)])
    _stack(d, 45, 3, ["crate_olive", "crate_slate"],
           [(4, 3, 3), (4, 3, 3)])
    _crate(d, 20, 1, 1, 4, 3, 3, "crate_olive")
    _crate(d, 21, 1, 4, 3, 3, 3, "crate_olive")
    _crate(d, 31, 2, 1, 3, 3, 3, "crate_olive")
    # guy ropes: eave corners to stakes at the pad corners
    for (ex, ey, sx, sy) in ((TX0, TY0, 3, 3), (TX0, TY1 - 1, 3, 31),
                             (TX1 - 1, TY0, 49, 3), (TX1 - 1, TY1 - 1, 49, 31)):
        guy_rope(d, CI, ex, ey, EAVE_Z, sx, sy, 1)
        stake(d, CI, sx, sy)
    # supports always land on the pad, whatever the jitter drew
    for (sx, sy) in (FLAGPOLE, (3, 3), (49, 3), (3, 31), (49, 31)):
        if (sx, sy, 0) not in d:
            d[(sx, sy, 0)] = CI["dirt"]
    # flagpole at the front-right corner
    flag_pole(d, CI, FLAGPOLE[0], FLAGPOLE[1], 1, HEIGHT)
    # pad stays one piece: drop isolated specks
    ground = [(x, y) for (x, y, z) in d if z == 0]
    gset = set(ground)
    for (x, y) in ground:
        nbs = ((x+1, y) in gset, (x-1, y) in gset,
               (x, y+1) in gset, (x, y-1) in gset)
        if not any(nbs):
            del d[(x, y, 0)]
    return d


def build_flag():
    """7x5 olive flag with a 2-voxel-thick pale-yellow V chevron, hanging
    from FLAG_PIVOT, flying toward +x (right). Own part so it can sway."""
    f = {}
    x0, y0, z0 = FLAG_PIVOT
    for i in range(7):
        for zz in range(5):
            for yy in (0, 1):
                f[(x0 + 1 + i, y0 + yy, z0 - zz)] = CI["flag_olive"]
    for i in range(3):
        zc = z0 - 2 + i
        for yy in (0, 1):
            f[(x0 + 3 + i, y0 + yy, zc)] = CI["flag_chevron"]
            f[(x0 + 7 - i, y0 + yy, zc)] = CI["flag_chevron"]
    return f


def main():
    rng = random.Random(667)
    body = build_body(rng)
    flag = build_flag()
    parts = {"body": body, "flag": flag}
    assembled = dict(body)
    assembled.update(flag)

    print(f"FOOTPRINT={FOOTPRINT} voxels ({FOOTPRINT[0]*0.15:.2f} x "
          f"{FOOTPRINT[1]*0.15:.2f} m), HEIGHT={HEIGHT} ({HEIGHT*0.15:.2f} m)")
    print(f"OPENING: wall plane y={TY0} (file -y front); open span "
          f"x {FRONT_OPEN_X}..{TX1 - 1}, z 4..{EAVE_Z}")
    print(f"DOOR_POINT={DOOR_POINT} (y={DOOR_POINT[1]} < front y={TY0}: "
          f"opening at LOW y)  FLAG_PIVOT={FLAG_PIVOT}")
    total = 0
    for name, part in parts.items():
        n = len(part)
        total += n
        comps = n_components(part)
        bb = bbox(part)
        print(f"  {name}: {n} voxels, {comps} component(s), bbox "
              f"{bb[0]}..{bb[1]}")
    print(f"total solid voxels: {total}")
    return parts, assembled


_parts, assembled = main()
body = _parts["body"]
flag = _parts["flag"]

if __name__ == "__main__":
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(outdir, exist_ok=True)
