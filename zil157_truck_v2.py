#!/usr/bin/env python3
"""Strike Bay — ZIL-157 6x6 truck, v2 (owner concept sheet, 2026-10-09).

v2 redraws v1 toward the owner's ZIL-157 concept: long crowned hood over a
tall slat grille, big flowing front wings with fender-mounted headlights,
rounded cab with a split windscreen, upright spare behind the cab, an
olive slatted stake bed, single wide tyres on all six wheels, and high
ground clearance. No markings.

TWO VOXEL SCALES
  body parts  TRUCK_VOXEL = 0.09 m   (chassis, cab, beds, AA parts)
  wheel parts WHEEL_VOXEL = 0.045 m  (wheels front/rear, spare): half-size
              voxels so a 1.1 m tyre is 25 voxels across and reads round.
  Wheel parts are authored in the SAME frame at 2x resolution:
  fine = 2 * coarse (a coarse voxel (x,y,z) spans fine [2x, 2x+2) ...).

Frame (as v1): z-up, ground z=0, x = width, y = length with the front
bumper at y=0; vehicle forward = file -y. Body x [0,25), centre x=12.5.

Parts:
  zil157-chassis-v2        static: ladder frame, axles, springs, bumper,
                           tow hooks, fuel tank, battery box, exhaust
  zil157-cab-v2            static: hood, grille, wings + headlights, cab,
                           running boards, mirrors
  zil157-bed-flat-v2       static cargo unit (variants follow)
  zil157-wheels-front-v2   FINE. Steer about z through each wheel centre,
                           spin about x. Centres (fine, continuous):
                           (7, 27, 12.5) and (43, 27, 12.5)
  zil157-wheels-rear-v2    FINE. Spin about x. Centres (7|43, 105|129, 12.5)
  zil157-spare-v2          FINE, static: upright spare behind the cab
  zil157-assembled-flat-v2 FINE merge (body upsampled 2x) for browsing
"""
import math
import os

TRUCK_VOXEL = 0.09
WHEEL_VOXEL = 0.045

PALETTE = [  # v1 palette, same indices
    ("olive",        ( 99, 102,  71)),  # 1
    ("olive_dark",   ( 72,  75,  52)),  # 2
    ("olive_light",  (118, 121,  86)),  # 3
    ("rust",         (112,  72,  46)),  # 4
    ("rust_dark",    ( 78,  50,  34)),  # 5
    ("tire",         ( 30,  30,  33)),  # 6
    ("tire_side",    ( 52,  52,  56)),  # 7
    ("steel",        (122, 126, 134)),  # 8
    ("steel_dark",   ( 62,  64,  72)),  # 9
    ("gunmetal",     ( 56,  58,  62)),  # 10
    ("gunmetal_dark",( 36,  38,  42)),  # 11
    ("dark",         ( 24,  26,  30)),  # 12
    ("wood",         (108,  94,  70)),  # 13
    ("wood_dark",    ( 76,  66,  50)),  # 14
    ("canvas",       (170, 146,  96)),  # 15 desert-tan canvas (owner: yellowy tan)
    ("canvas_dark",  (128, 106,  68)),  # 16 hoop ridges, ropes, flap seams
    ("glass",        (120, 160, 180)),  # 17
    ("white",        (222, 222, 216)),  # 18
    ("window",       (100, 132, 152)),  # 19
    ("brass",        (168, 134,  72)),  # 20
    ("red",          (150,  44,  38)),  # 21
    ("canvas_light", (196, 176, 122)),  # 22 sun-faded canvas roof
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

# wheel geometry (coarse continuous units; fine = x2)
WHEEL_X = (3.5, 21.5)
FRONT_Y = 13.5
REAR_Y = (52.0, 65.0)
WHEEL_Z = 6.25
WHEEL_R = 6.25
TYRE_W = 4.0            # 0.36 m


# ---------------------------------------------------------------- primitives
def put(d, x, y, z, c):
    d[(x, y, z)] = CI[c]


def box(d, x0, x1, y0, y1, z0, z1, c):
    for x in range(x0, x1):
        for y in range(y0, y1):
            for z in range(z0, z1):
                put(d, x, y, z, c)


def mirror_x(d, width=25):
    """Copy every voxel to its mirror across the centre line."""
    for (x, y, z), c in list(d.items()):
        d[(width - 1 - x, y, z)] = c


def cyl(d, axis, c0, c1, r, lo, hi, c, r_in=-1.0):
    """Cylinder along `axis` ('x'|'y'|'z'); (c0,c1) is the continuous centre
    in the other two axes (in order), lo..hi the voxel range along axis."""
    for a in range(int(c0 - r - 1), int(c0 + r + 2)):
        for b in range(int(c1 - r - 1), int(c1 + r + 2)):
            d2 = (a + 0.5 - c0) ** 2 + (b + 0.5 - c1) ** 2
            if d2 <= r * r and (r_in < 0 or d2 > r_in * r_in):
                for t in range(lo, hi):
                    p = {"x": (t, a, b), "y": (a, t, b), "z": (a, b, t)}[axis]
                    d[p] = CI[c]


# ================================================================ CHASSIS (coarse)
def chassis():
    h = {}
    # ladder frame rails + cross members
    for x0 in (8, 15):
        box(h, x0, x0 + 2, 1, 77, 9, 11, "gunmetal_dark")
    for y in (2, 12, 22, 36, 47, 58, 70, 75):
        box(h, 10, 15, y, y + 1, 9, 10, "gunmetal_dark")
    # front bumper + tow hooks
    box(h, 0, 25, 0, 2, 7, 10, "olive_dark")
    box(h, 0, 25, 0, 1, 9, 10, "olive")
    for x0 in (0, 23):
        box(h, x0, x0 + 2, 0, 2, 6, 10, "gunmetal_dark")                  # end caps
    for x in (6, 17):
        box(h, x, x + 2, 0, 1, 5, 7, "steel_dark")
    # axles, diffs, springs
    for ay in (13, 52, 64):
        box(h, 3, 22, ay, ay + 1, 6, 7, "gunmetal")
        box(h, 10, 15, ay - 1, ay + 2, 4, 8, "gunmetal_dark")       # diff housing
        for x0 in (8, 15):
            box(h, x0, x0 + 2, ay - 5, ay + 6, 8, 9, "steel_dark")   # leaf spring
            box(h, x0, x0 + 2, ay, ay + 1, 7, 8, "steel_dark")        # U-bolt block
    box(h, 11, 14, 14, 52, 7, 8, "steel_dark")                      # driveshaft
    box(h, 10, 15, 30, 36, 6, 9, "gunmetal_dark")                   # transfer case
    # fuel tank (left = +x side) and battery box (right)
    box(h, 18, 23, 36, 46, 6, 10, "olive")                          # fuel tank
    box(h, 18, 23, 36, 46, 9, 10, "olive_light")
    for y in (38, 43):
        box(h, 18, 23, y, y + 1, 6, 10, "olive_dark")                # straps
    box(h, 17, 18, 38, 44, 8, 10, "steel_dark")                     # bracket to the rail
    box(h, 1, 5, 37, 45, 6, 10, "olive_dark")
    box(h, 5, 8, 39, 42, 8, 9, "steel_dark")
    # exhaust along the right rail
    box(h, 6, 7, 20, 46, 8, 9, "gunmetal_dark")
    put(h, 6, 46, 8, "rust")
    for y in (24, 40):
        box(h, 6, 8, y, y + 1, 9, 10, "steel_dark")                  # exhaust hangers
    box(h, 5, 8, 41, 42, 9, 10, "steel_dark")                       # battery box hanger
    # rear: cross bar, tail lights, mudflaps, tow hitch
    box(h, 1, 24, 75, 77, 10, 11, "olive_dark")
    for x0 in (1, 21):
        box(h, x0, x0 + 3, 76, 77, 11, 12, "red")
    for x0 in (1, 19):
        box(h, x0, x0 + 5, 72, 73, 3, 11, "dark")                    # mudflaps
    box(h, 5, 8, 72, 73, 10, 11, "steel_dark")                      # flap hangers
    box(h, 17, 19, 72, 73, 10, 11, "steel_dark")
    box(h, 11, 14, 77, 78, 8, 11, "steel_dark")                     # pintle hitch
    return h


# ================================================================ CAB + FRONT (coarse)
def _wing_top(y):
    """Profile of the front wing's upper edge along y (z)."""
    if y < 4:
        return None
    if y < 9:
        return (12, 14, 15, 16, 16)[y - 4]
    if y < 18:
        return 16
    if y < 24:
        return 16 - (y - 18)
    return None


def cab():
    c = {}
    # --- grille: tall vertical slats in a frame
    box(c, 7, 18, 2, 3, 8, 21, "olive")
    for x in range(8, 17):
        box(c, x, x + 1, 2, 3, 9, 20, "dark" if x % 2 == 0 else "olive_dark")
    box(c, 7, 18, 2, 3, 20, 21, "olive_light")
    box(c, 7, 8, 2, 3, 8, 21, "olive_light"); box(c, 17, 18, 2, 3, 8, 21, "olive_light")   # surround
    # --- hood: crowned, slight forward droop, side louvres
    for y in range(3, 20):
        top = 20 if y == 3 else 21
        box(c, 7, 18, y, y + 1, 9, top, "olive")
        box(c, 8, 17, y, y + 1, top, top + 1, "olive_light")          # crown
    box(c, 12, 13, 4, 20, 21, 22, "olive_dark")                       # centre seam
    for y in range(9, 18, 2):
        box(c, 7, 8, y, y + 1, 15, 19, "olive_dark")                   # louvres
        box(c, 17, 18, y, y + 1, 15, 19, "olive_dark")
    # --- front wings (built on the right, mirrored): solid wing above the
    # wheel arc, flowing down to the running board
    wing = {}
    for y in range(3, 25):
        top = _wing_top(y)
        if top is None:
            continue
        for z in range(7, top + 1):
            dyz = math.hypot(y + 0.5 - FRONT_Y, z + 0.5 - WHEEL_Z)
            if dyz < WHEEL_R + 0.9:
                continue                                              # wheel arch
            for x in range(1, 7):
                col = "olive"
                if z == top:
                    col = "olive_light"
                elif dyz < WHEEL_R + 1.9:
                    col = "olive_dark" if x in (1, 6) else "olive"    # arch lip
                put(wing, x, y, z, col)
    # headlight pod on the wing nose, lens forward
    cyl(wing, "y", 5.0, 15.0, 2.0, 4, 7, "olive_dark")
    cyl(wing, "y", 5.0, 15.0, 1.5, 3, 4, "white")
    put(wing, 4, 3, 15, "glass"); put(wing, 5, 3, 14, "glass")
    # sidelight + blackout lamp on the wing top
    box(wing, 3, 5, 9, 10, 17, 18, "steel_dark")
    mirror_x(wing)
    c.update(wing)
    # --- running boards and stirrup steps
    for x0 in (0, 22):
        box(c, x0, x0 + 3, 23, 34, 9, 10, "olive_dark")
        box(c, x0, x0 + 3, 26, 30, 6, 7, "steel_dark")                 # lower step
        box(c, x0 + (0 if x0 == 0 else 2), x0 + (1 if x0 == 0 else 3), 26, 27, 7, 9, "steel_dark")
    # --- cab body
    box(c, 1, 24, 20, 35, 10, 18, "olive")                             # lower body
    box(c, 1, 24, 20, 21, 17, 18, "olive_light")                       # cowl lip
    box(c, 1, 24, 21, 35, 18, 24, "olive")                             # window band
    # windscreen: two panes split by a centre post, set into the front
    box(c, 1, 24, 20, 21, 18, 24, "olive")
    box(c, 3, 12, 20, 21, 18, 24, "glass")
    box(c, 13, 22, 20, 21, 18, 24, "glass")
    box(c, 2, 23, 20, 21, 24, 25, "olive")                             # header
    box(c, 2, 23, 19, 20, 24, 25, "olive_dark")                        # visor lip
    # side door windows + door seams + handles
    for x in (1, 23):
        box(c, x, x + 1, 23, 30, 19, 23, "glass")
        box(c, x, x + 1, 22, 23, 11, 22, "olive_dark")                  # door front seam
        box(c, x, x + 1, 31, 32, 11, 22, "olive_dark")                  # door rear seam
        put(c, x, 29, 16, "steel")                                      # handle
    # rear window
    box(c, 8, 17, 34, 35, 19, 22, "glass")
    # roof: rounded edges (two inset layers)
    box(c, 1, 24, 21, 35, 24, 25, "olive")
    box(c, 2, 23, 21, 34, 25, 26, "olive_light")
    box(c, 4, 21, 22, 33, 26, 27, "olive")
    # mirrors on arms ahead of the doors
    for (x, ax) in ((0, 1), (24, 23)):
        box(c, x, x + 1, 19, 21, 19, 23, "steel_dark")
        put(c, ax, 20, 20, "steel_dark"); put(c, ax, 21, 20, "steel_dark")
    return c


# ================================================================ BEDS (coarse)
BED_Y0, BED_Y1 = 39, 77


def bed_base(d, side_top=20, head_top=24, tail_top=20):
    y0, y1 = BED_Y0, BED_Y1
    for x0 in (8, 15):
        box(d, x0, x0 + 2, y0, y1, 11, 13, "olive_dark")               # sub-sills on the rails
    for y in range(y0 + 2, y1, 6):
        box(d, 0, 25, y, y + 1, 12, 13, "olive_dark")                   # cross bearers
    box(d, 0, 25, y0, y1, 13, 14, "olive")                              # floor
    # sides: three boards with open gaps between, on stakes
    boards = [(14, 16), (17, side_top)]
    for x in (0, 24):
        for (z0, z1) in boards:
            if z1 > z0:
                box(d, x, x + 1, y0, y1, z0, z1, "olive")
                box(d, x, x + 1, y0, y1, z1 - 1, z1, "olive_light")
        for y in range(y0, y1, 9):
            box(d, x, x + 1, y, y + 1, 12, side_top, "olive_dark")       # stakes
        box(d, x, x + 1, y1 - 1, y1, 12, side_top, "olive_dark")
    # headboard with a cab-guard rack
    box(d, 0, 25, y0, y0 + 1, 14, head_top - 3, "olive")
    for x in range(1, 25, 3):
        box(d, x, x + 1, y0, y0 + 1, head_top - 3, head_top, "olive_dark")
    box(d, 0, 25, y0, y0 + 1, head_top - 1, head_top, "olive_dark")
    # tailgate: boards + hinge blocks + chains
    for (z0, z1) in boards:
        if z1 > z0 and z1 <= tail_top:
            box(d, 1, 24, y1 - 1, y1, z0, z1, "olive")
            box(d, 1, 24, y1 - 1, y1, z1 - 1, z1, "olive_light")
    for x in (4, 12, 20):
        box(d, x, x + 1, y1 - 1, y1, 13, 15, "steel_dark")               # hinges
    for x in (1, 23):
        put(d, x, y1 - 1, tail_top - 1, "steel")                          # latch
    # rear wheel fenders: flat plates under the bed over each bogie pair
    for x0 in (0, 19):
        box(d, x0, x0 + 6, 45, 72, 12, 13, "olive_dark")
    return d


def bed_flat():
    return bed_base({})


TENT_SIDE_TOP, TENT_TOP, TENT_R = 25, 30, 4.5


def _tent_inside(x, z):
    """True inside the tent cross-section (vertical sides, rounded
    shoulders, flat roof), x in [0,25), z from the bed rail up."""
    if z >= TENT_TOP or x < 0 or x >= 25:
        return False
    xi = min(x + 0.5, 25 - (x + 0.5))            # distance from the nearer side
    zt = TENT_TOP - (z + 0.5)                    # distance below the roof
    if xi >= TENT_R or zt >= TENT_R:
        return True
    return math.hypot(TENT_R - xi, TENT_R - zt) <= TENT_R


def bed_covered():
    d = bed_base({})
    y0, y1 = BED_Y0, BED_Y1
    # canvas shell over the bed: 1 voxel thick, front and rear closed
    for x in range(0, 25):
        for z in range(18, TENT_TOP):
            if not _tent_inside(x, z):
                continue
            edge = not (_tent_inside(x - 1, z) and _tent_inside(x + 1, z) and _tent_inside(x, z + 1))
            for y in range(y0, y1):
                end = y in (y0, y1 - 1)
                if edge or end:
                    d[(x, y, z)] = CI["canvas"]
    # hoop ridges at the stakes, a darker band over the roof and sides
    for y in range(y0, y1, 9):
        for x in range(0, 25):
            for z in range(18, TENT_TOP):
                if (x, y, z) in d and d[(x, y, z)] == CI["canvas"] and y not in (y0, y1 - 1):
                    d[(x, y, z)] = CI["canvas_dark"]
    # lighter roof panel (sun-faded) and a ridge seam
    for (x, y, z), c in list(d.items()):
        if z == TENT_TOP - 1 and c == CI["canvas"] and 6 <= x <= 18:
            d[(x, y, z)] = CI["canvas_light"]
    # tie-down rope along the bottom edge and lashing points
    for x in (0, 24):
        for y in range(y0, y1):
            d[(x, y, 20)] = CI["canvas_dark"]
        for y in range(y0 + 4, y1, 6):
            d[(x, y, 19)] = CI["wood_dark"]
    # rear flap: centre split + roll at the top, ropes
    for z in range(20, TENT_TOP - 2):
        d[(12, y1 - 1, z)] = CI["canvas_dark"]
    for x in range(3, 22):
        d[(x, y1, TENT_TOP - 4)] = CI["canvas_dark"]                       # rolled flap
    for x in (6, 18):
        for z in range(21, TENT_TOP - 4):
            d[(x, y1, z)] = CI["wood_dark"]                                 # straps
    return d


# ================================================================ TECHNICAL (coarse)
# Pivots, coarse continuous coords (x centre line 12.5):
AA_LIFT = 3                         # mount raised on its pedestal (authored at +0, lifted)
AA_TRAVERSE = (12.5, 58.0, 17.0 + AA_LIFT)    # about z; turntable seat plane
AA_ELEVATION = (12.5, 58.0, 23.0 + AA_LIFT)   # about x; on the bore line, child of traverse


def _lift(d):
    return {(x, y, z + AA_LIFT): c for (x, y, z), c in d.items()}


def bed_technical():
    """Stake bed with low sides/headboard/tailgate for the gun sweep, a
    pedestal for the AA mount, and ammo crates lashed by the headboard."""
    d = bed_base({}, side_top=17, head_top=20, tail_top=17)
    cx, cy, _ = AA_TRAVERSE
    cyl(d, "z", cx, cy, 3.2, 14, 17 + AA_LIFT, "gunmetal_dark")        # pedestal
    cyl(d, "z", cx, cy, 6.0, 14, 15, "olive_light", r_in=5.0)          # traverse ring on the floor
    cyl(d, "z", cx, cy, 4.2, 14, 15, "olive_dark")                     # base plate
    cyl(d, "z", cx, cy, 4.2, 15, 16, "gunmetal_dark")                  # flared collar
    for (x0, x1) in ((1, 5), (20, 24)):                                 # ammo crates, 2 a side
        for (y0, y1) in ((42, 46), (68, 72)):
            box(d, x0, x1, y0, y1, 14, 18, "olive")
            box(d, x0, x1, y0, y1, 18, 19, "olive_light")
            box(d, x0, x1, y0 + 1, y0 + 2, 14, 18, "olive_dark")
            put(d, x0 + 1, y0, 16, "steel_dark")
    return d


def aa_turret():
    """Traversing cradle: turntable, cheeks, gunner seat, sight, ammo boxes."""
    t = {}
    cx, cy, cz = AA_TRAVERSE
    ez = AA_ELEVATION[2] - AA_LIFT                                     # authored unlifted
    cyl(t, "z", cx, cy, 5.0, 17, 18, "olive")                          # turntable
    cyl(t, "z", cx, cy, 5.0, 17, 18, "olive_dark", r_in=4.0)           # rim
    box(t, 9, 16, 56, 60, 18, 20, "gunmetal")                           # cradle crossbeam
    for x in (9, 15):
        box(t, x, x + 1, 53, 63, 18, 26, "gunmetal")                     # cheeks
        box(t, x, x + 1, 53, 63, 26, 27, "steel_dark")
    cyl(t, "x", cy, ez, 1.2, 8, 17, "gunmetal")                         # trunnion
    # gunner seat behind the guns (toward the cab when at rest)
    box(t, 12, 13, 51, 54, 18, 20, "olive_dark")
    box(t, 12, 13, 48, 51, 19, 20, "olive_dark")                        # seat arm
    box(t, 10, 15, 48, 51, 20, 21, "gunmetal")                          # pan
    box(t, 10, 15, 47, 48, 20, 25, "olive_dark")                        # backrest
    # reflector sight on the left cheek
    box(t, 8, 9, 56, 57, 22, 27, "steel_dark")
    box(t, 7, 9, 55, 57, 27, 29, "steel")                               # sight ring block
    # ammo boxes outboard of the cheeks + feed chutes
    for (x0, x1, chute) in ((5, 8, 8), (17, 20, 16)):
        box(t, x0, x1, 53, 61, 19, 23, "olive")
        box(t, x0, x1, 53, 61, 23, 24, "olive_dark")
        box(t, chute, chute + 1, 55, 58, 20, 22, "steel_dark")
        put(t, chute, 55, 22, "brass")
    for x0 in (5, 17):
        box(t, x0, x0 + 3, 57, 58, 18, 19, "olive_dark")                 # box mounts
    # elevating handwheel on the right cheek
    cyl(t, "x", 59.5, 20.5, 1.6, 16, 17, "steel_dark")
    return t


def aa_barrels():
    """Twin KPV barrels, ONE part, elevate about x at AA_ELEVATION; authored
    level pointing +y (over the bed / tail at rest)."""
    b = {}
    _, ey, ez = AA_ELEVATION
    for rx in (10, 13):                                                  # receivers (2 wide each)
        box(b, rx, rx + 2, 50, 62, 21, 25, "olive")
        box(b, rx, rx + 2, 52, 60, 25, 26, "olive_dark")                 # top cover
        box(b, rx, rx + 2, 49, 50, 21, 25, "gunmetal_dark")              # buttplate
        box(b, rx, rx + 2, 47, 49, 22, 24, "dark")                       # spade grips
        box(b, rx, rx + 2, 62, 63, 21, 25, "steel")                      # breech ring
        box(b, rx, rx + 2, 63, 76, 22, 24, "gunmetal")                   # barrel
        for y in (67, 72):
            box(b, rx, rx + 2, y, y + 1, 21, 25, "gunmetal_dark")         # collars
        box(b, rx, rx + 2, 76, 79, 21, 25, "gunmetal_dark")              # flash hider
        box(b, rx, rx + 2, 78, 79, 22, 24, "dark")                       # bore
    box(b, 12, 13, 70, 71, 22, 24, "gunmetal_dark")                      # barrel crossbar
    box(b, 12, 13, 62, 63, 22, 24, "gunmetal_dark")
    box(b, 12, 13, 56, 60, 21, 25, "gunmetal_dark")                      # trunnion saddle
    return b


# ================================================================ WHEELS (fine, 2x)
def wheel(d, xc, yc, zc, outboard):
    """One wheel in fine voxels. (xc,yc,zc) continuous centre; outboard =
    +1 when the outer face is +x, -1 when it is -x."""
    R = WHEEL_R * 2                 # 12.5
    W = TYRE_W * 2                  # 8
    x0, x1 = int(round(xc - W / 2)), int(round(xc + W / 2))
    lugs = 22
    for y in range(int(yc - R - 1), int(yc + R + 2)):
        for z in range(int(zc - R - 1), int(zc + R + 2)):
            dy, dz = y + 0.5 - yc, z + 0.5 - zc
            r = math.hypot(dy, dz)
            if r > R:
                continue
            ang = math.atan2(dz, dy) % (2 * math.pi)
            k = int(ang / (2 * math.pi) * lugs)
            for x in range(x0, x1):
                side = 0 if (x - xc) * outboard < 0 else 1                # inner / outer half
                face = x == (x1 - 1 if outboard > 0 else x0)              # outer face column
                inner = x == (x0 if outboard > 0 else x1 - 1)
                if r > R - 1.2:
                    if (k + side) % 2 == 0:
                        put(d, x, y, z, "tire")                          # lug (staggered)
                    continue                                              # groove = gap
                if r > R - 3.6:
                    put(d, x, y, z, "tire_side" if (face or inner) else "tire")
                    continue
                # rim and hub, recessed on the outer face
                if face:
                    continue
                if r > R - 4.6:
                    put(d, x, y, z, "olive_dark")                         # rim lip
                elif r > 3.2:
                    put(d, x, y, z, "olive")                              # dished disc
                else:
                    put(d, x, y, z, "steel_dark")                         # hub
    # hub cap boss and 8 lug nuts on the outer face (one step in)
    fx = (x1 - 2) if outboard > 0 else (x0 + 1)
    for i in range(8):
        a = i * math.pi / 4
        put(d, fx + (1 if outboard > 0 else -1), int(yc + 4.6 * math.cos(a)), int(zc + 4.6 * math.sin(a)), "steel")
    cyl(d, "x", yc, zc, 2.2, min(fx, fx + outboard * 2), max(fx, fx + outboard * 2) + 1, "olive_dark")
    cyl(d, "x", yc, zc, 1.0, fx + outboard * 2 if outboard > 0 else fx - 2, (fx + outboard * 2 if outboard > 0 else fx - 2) + 1, "steel")
    # tyre inflation fitting (ZIL central inflation) on the hub
    put(d, fx + outboard, int(yc), int(zc + 2.6), "steel_dark")


def wheels_front():
    d = {}
    wheel(d, WHEEL_X[0] * 2, FRONT_Y * 2, WHEEL_Z * 2, -1)
    wheel(d, WHEEL_X[1] * 2, FRONT_Y * 2, WHEEL_Z * 2, +1)
    return d


def wheels_rear():
    d = {}
    for yc in REAR_Y:
        wheel(d, WHEEL_X[0] * 2, yc * 2, WHEEL_Z * 2, -1)
        wheel(d, WHEEL_X[1] * 2, yc * 2, WHEEL_Z * 2, +1)
    return d


def spare():
    """Upright spare behind the cab (axis along y), right of centre."""
    d = {}
    xc, yc, zc = 35.0, 73.0, 34.0
    R = WHEEL_R * 2
    for x in range(int(xc - R - 1), int(xc + R + 2)):
        for z in range(int(zc - R - 1), int(zc + R + 2)):
            r = math.hypot(x + 0.5 - xc, z + 0.5 - zc)
            if r > R:
                continue
            for y in range(int(yc - 4), int(yc + 4)):
                col = "tire" if r > R - 3.6 else ("olive" if r > 3.2 else "steel_dark")
                if r > R - 1.2 and (int(math.atan2(z + 0.5 - zc, x + 0.5 - xc) * 22 / (2 * math.pi)) % 2):
                    continue
                d[(x, y, z)] = CI[col]
    # carrier bracket down to the frame
    for z in range(20, int(zc - 3)):
        for y in (70, 71):
            d[(34, y, z)] = CI["steel_dark"]; d[(35, y, z)] = CI["steel_dark"]
    return d


# ================================================================ assemble
chassis_v = chassis()
cab_v = cab()
bed_flat_v = bed_flat()
bed_covered_v = bed_covered()
bed_technical_v = bed_technical()
aa_turret_v = _lift(aa_turret())
aa_barrels_v = _lift(aa_barrels())
wheels_front_v = wheels_front()
wheels_rear_v = wheels_rear()
spare_v = spare()


def upsample(d):
    out = {}
    for (x, y, z), c in d.items():
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    out[(2 * x + dx, 2 * y + dy, 2 * z + dz)] = c
    return out


def assemble(*coarse, fine=()):
    out = {}
    for d in coarse:
        out.update(upsample(d))
    for d in fine:
        out.update(d)
    return out


assembled_flat = assemble(chassis_v, cab_v, bed_flat_v,
                          fine=(wheels_front_v, wheels_rear_v, spare_v))
assembled_covered = assemble(chassis_v, cab_v, bed_covered_v,
                             fine=(wheels_front_v, wheels_rear_v, spare_v))
assembled_technical = assemble(chassis_v, cab_v, bed_technical_v, aa_turret_v, aa_barrels_v,
                               fine=(wheels_front_v, wheels_rear_v, spare_v))

PARTS = {
    "zil157-chassis-v2": chassis_v,
    "zil157-cab-v2": cab_v,
    "zil157-bed-flat-v2": bed_flat_v,
    "zil157-bed-covered-v2": bed_covered_v,
    "zil157-bed-technical-v2": bed_technical_v,
    "zil157-bed-aa-turret-v2": aa_turret_v,
    "zil157-bed-aa-barrels-v2": aa_barrels_v,
    "zil157-wheels-front-v2": wheels_front_v,
    "zil157-wheels-rear-v2": wheels_rear_v,
    "zil157-spare-v2": spare_v,
    "zil157-assembled-flat-v2": assembled_flat,
    "zil157-assembled-covered-v2": assembled_covered,
    "zil157-assembled-technical-v2": assembled_technical,
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
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "zil157_v2")
    os.makedirs(out, exist_ok=True)
    for name, d in PARTS.items():
        write_vox(os.path.join(out, name + ".vox"), d, PALETTE)
        if "assembled" not in name:
            print(f"  {name}: {components(d)} component(s)")
