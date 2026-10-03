#!/usr/bin/env python3
"""Strike Bay — ZIL-157 Soviet 6x6 truck (v1).

TWELVE .vox files sharing one design frame (file coords == design coords,
origin at footprint min corner, ground z=0, x = width, y = length with y=0
at the front bumper, z up). VEHICLE forward = file -y (nose at y=0 bumper);
GUN rest pose = +y (barrels over the bed). The barrels are authored at
0 deg elevation pointing +y, matching the ZPU-2/ZSU file convention; on
the truck frame +y runs from the front bumper toward the tailgate, so at
rest traverse the AA gun faces rearward over the bed (classic gun-truck
pose). File-forward -y  ==>  vehicle left = +x, vehicle right = -x.

  zil157-chassis-v1.vox        static: ladder rails, cross members, 3 axles +
                               differentials, driveshafts, leaf springs, fuel
                               tank, exhaust, bumpers, tow hooks
  zil157-cab-v1.vox            hood + louvers, slat grille + guards, round
                               headlights, front fenders, split windshield,
                               doors, mirrors, roof, bench seat + steering
                               wheel, spare tire on carrier behind cab
  zil157-wheels-front-v1.vox   steerable pair: single tires, tread blocks,
                               hubs, kingpins
  zil157-wheels-rear-v1.vox    bogie: 4 dual-wheel positions, tread, hubs
  zil157-bed-flat-v1.vox       wooden stake bed: plank floor, 3-board sides,
                               headboard, tailgate, stake pockets, mudguards
  zil157-bed-covered-v1.vox    flatbed + 4 hoops + closed olive canvas cover
  zil157-bed-technical-v1.vox  flatbed + AA pedestal ring (lowered headboard /
                               tailgate / side boards so the gun sweep clears)
  zil157-bed-aa-turret-v1.vox  traversing cradle: turntable, cheeks, trunnion,
                               seat, sight, ammo boxes, handwheel
  zil157-bed-aa-barrels-v1.vox elevating twin barrels: receivers, collared
                               barrels, muzzle brakes (0 deg, pointing +y)
  zil157-assembled-flat-v1.vox      merged chassis+cab+wheels+bed-flat
  zil157-assembled-covered-v1.vox   merged chassis+cab+wheels+bed-covered
  zil157-assembled-technical-v1.vox merged chassis+cab+wheels+bed-technical
                               +aa-turret+aa-barrels

Scale: TRUCK_VOXEL = 0.09 m/voxel (ZSU convention). Measured from the
voxels: 78 long (y 0-77 incl. rear tow hitch) -> 7.02 m (real 6.93 m),
25 wide (bed x 0-24) -> 2.25 m (real 2.32 m), cab roof z=26 -> 2.34 m
(real 2.36 m), door glass bottom z=17 -> 1.53 m, wheel dia 1.20 m ->
13 vox, clearance 0.31 m -> diff bottom z=3.

Rig pivots (design/file coords):
  STEER_L = (3, 14, 6), STEER_R = (22, 14, 6)   z-axis (kingpins);
  spin = x-axis through (y=14, z=6) front, (y=49 / y=61, z=6) rear
  TRAVERSE_PIVOT  = (12, 55, 18)   z-axis; parent the aa-turret part here
  ELEVATION_PIVOT = (12, 55, 23)   x-axis; parent the aa-barrels part here,
                                  as a child of the traverse node
  Elevation limits: -5 deg .. +80 deg. A breech well is machined through
  the turntable (kept as an annulus), the pedestal and the bed floor along
  the breech swing (pivot (12,55,23); the breech drops ~10 vox below the
  pivot at +80 deg). Measured: 0 unintended hits -5..+90 deg; the
  documented +80 limit keeps margin for in-game rotation rounding.
  Traverse: recommend stops at +/-140 deg (0 hits through +/-145; the
  barrels clip the cab rear top corners at +/-150). 180 deg sweeps the
  barrels through the cab roof (roof z=26 > barrel plane z 22-24).

Reference: user's muddy 3/4 painting (weathered olive-drab, canvas bed,
spare behind cab, slat grille, headlight guards) + blueprint tech sheet.
"""
import math
import os
import random
import struct
from collections import deque
from PIL import Image, ImageDraw

random.seed(157)

TRUCK_VOXEL = 0.09  # m/voxel

PALETTE = [  # (name, rgb); color index = position + 1
    ("olive",        ( 99, 102,  71)),  # 1  Soviet protective green
    ("olive_dark",   ( 72,  75,  52)),  # 2  olive shadow / panel lines
    ("olive_light",  (118, 121,  86)),  # 3  sun-faded highlight
    ("rust",         (112,  72,  46)),  # 4  rust streaks
    ("rust_dark",    ( 78,  50,  34)),  # 5  deep rust
    ("tire",         ( 23,  23,  26)),  # 6  tire carcass
    ("tire_side",    ( 54,  54,  58)),  # 7  sidewall ring / tread blocks
    ("steel",        (122, 126, 134)),  # 8  bright hardware
    ("steel_dark",   ( 62,  64,  72)),  # 9  bumper, hubs, guards
    ("gunmetal",     ( 56,  58,  62)),  # 10 barrels, receivers
    ("gunmetal_dark",( 36,  38,  42)),  # 11 frame rails, muzzle brake
    ("dark",         ( 28,  30,  34)),  # 12 deep shadow, mudflaps
    ("wood",         (108,  94,  70)),  # 13 weathered bed planks
    ("wood_dark",    ( 76,  66,  50)),  # 14 plank gaps, sills
    ("canvas",       ( 97, 101,  72)),  # 15 faded olive canvas
    ("canvas_dark",  ( 70,  74,  52)),  # 16 canvas ribs / seat
    ("glass",        (120, 160, 180)),  # 17 windows, lenses
    ("white",        (222, 222, 216)),  # 18 stencil
    ("window",       (100, 132, 152)),  # 19 (interior_room contract)
    ("brass",        (168, 134,  72)),  # 20 ammo hint
    ("red",          (150,  44,  38)),  # 21 taillights
]
CI = {name: i + 1 for i, (name, _) in enumerate(PALETTE)}

TRAVERSE_PIVOT = (12, 55, 18)
ELEVATION_PIVOT = (12, 55, 23)
STEER_L = (22, 14, 6)   # +x = vehicle left (forward = file -y)
STEER_R = (3, 14, 6)

chassis = {}
cab = {}
wheels_front = {}
wheels_rear = {}
bed_flat = {}
bed_covered = {}
bed_technical = {}
aa_turret = {}
aa_barrels = {}


def B(d, x0, x1, y0, y1, z0, z1, c):
    """Inclusive box fill into dict d (all bounds inclusive)."""
    ci = CI[c]
    for x in range(int(x0), int(x1) + 1):
        for y in range(int(y0), int(y1) + 1):
            for z in range(int(z0), int(z1) + 1):
                d[(x, y, z)] = ci


def cyl_z(d, cx, cy, r, z0, z1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for y in range(cy - r, cy + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                for z in range(z0, z1 + 1):
                    d[(x, y, z)] = ci


def cyl_x(d, cy, cz, r, x0, x1, c):
    ci = CI[c]
    for y in range(cy - r, cy + r + 1):
        for z in range(cz - r, cz + r + 1):
            if (y - cy) ** 2 + (z - cz) ** 2 <= r * r:
                for x in range(x0, x1 + 1):
                    d[(x, y, z)] = ci


def cyl_y(d, cx, cz, r, y0, y1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            if (x - cx) ** 2 + (z - cz) ** 2 <= r * r:
                for y in range(y0, y1 + 1):
                    d[(x, y, z)] = ci


def ring_z(d, cx, cy, r, z0, z1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for y in range(cy - r, cy + r + 1):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if (r - 1) ** 2 < d2 <= r * r:
                for z in range(z0, z1 + 1):
                    d[(x, y, z)] = ci


def ring_x(d, cy, cz, r, x0, x1, c):
    ci = CI[c]
    for y in range(cy - r, cy + r + 1):
        for z in range(cz - r, cz + r + 1):
            d2 = (y - cy) ** 2 + (z - cz) ** 2
            if (r - 1) ** 2 < d2 <= r * r:
                for x in range(x0, x1 + 1):
                    d[(x, y, z)] = ci


def ring_y(d, cx, cz, r, y0, y1, c):
    ci = CI[c]
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            d2 = (x - cx) ** 2 + (z - cz) ** 2
            if (r - 1) ** 2 < d2 <= r * r:
                for y in range(y0, y1 + 1):
                    d[(x, y, z)] = ci


def streak(d, x, y, z_top, n):
    """Rust streak bleeding down: recolors existing face voxels only."""
    for i in range(n):
        p = (x, y, z_top - i)
        if p in d:
            d[p] = CI["rust"] if (i + x + y) % 3 else CI["rust_dark"]


def tread_ring(d, cy, cz, r, x0, x1, c, n=12):
    """Tread blocks around a wheel (axis = x)."""
    ci = CI[c]
    for i in range(n):
        a = 2 * math.pi * i / n
        yy = int(round(cy + (r - 0.5) * math.sin(a)))
        zz = int(round(cz + (r - 0.5) * math.cos(a)))
        for x in range(x0, x1 + 1):
            d[(x, yy, zz)] = ci


def tread_ring_y(d, cx, cz, r, y0, y1, c, n=12):
    """Tread blocks around a wheel whose axis is y (spare tire)."""
    ci = CI[c]
    for i in range(n):
        a = 2 * math.pi * i / n
        xx = int(round(cx + (r - 0.5) * math.sin(a)))
        zz = int(round(cz + (r - 0.5) * math.cos(a)))
        for y in range(y0, y1 + 1):
            d[(xx, y, zz)] = ci


# ================================================================ CHASSIS (static)
# ladder rails (z 9-11) + cross members
B(chassis, 7, 8, 2, 74, 9, 11, "gunmetal_dark")
B(chassis, 16, 17, 2, 74, 9, 11, "gunmetal_dark")
for cmy in (6, 16, 26, 36, 46, 56, 66, 73):
    B(chassis, 7, 17, cmy, cmy + 1, 9, 11, "gunmetal_dark")
# front bumper + tow hooks
B(chassis, 2, 23, 0, 1, 8, 10, "steel_dark")
B(chassis, 2, 23, 0, 1, 10, 10, "olive_dark")       # bumper top lip
B(chassis, 8, 8, 0, 1, 6, 8, "gunmetal_dark")       # tow hooks
B(chassis, 16, 16, 0, 1, 6, 8, "gunmetal_dark")
B(chassis, 8, 8, 0, 0, 5, 5, "steel_dark")          # hook tips
B(chassis, 16, 16, 0, 0, 5, 5, "steel_dark")
# rear light bar + taillights + rear hooks
B(chassis, 4, 20, 74, 75, 11, 13, "gunmetal_dark")
B(chassis, 5, 5, 74, 75, 12, 13, "red")
B(chassis, 19, 19, 74, 75, 12, 13, "red")
B(chassis, 8, 8, 75, 77, 8, 10, "gunmetal_dark")    # rear tow hooks
B(chassis, 16, 16, 75, 77, 8, 10, "gunmetal_dark")
# axles (center z=6; 13-dia wheels -> z 0-12) + differentials
B(chassis, 2, 22, 14, 14, 5, 7, "gunmetal")         # front axle
B(chassis, 11, 13, 12, 16, 3, 7, "olive_dark")      # front diff pumpkin
B(chassis, 11, 12, 12, 16, 3, 3, "gunmetal_dark")
for ay in (49, 61):                                 # bogie axles
    B(chassis, 1, 23, ay, ay, 5, 7, "gunmetal")
    B(chassis, 11, 13, ay - 2, ay + 2, 3, 7, "olive_dark")
    B(chassis, 11, 12, ay - 2, ay + 2, 3, 3, "gunmetal_dark")
# leaf spring packs above each axle
for sx0, sx1 in ((7, 9), (15, 17)):
    B(chassis, sx0, sx1, 8, 20, 7, 8, "steel_dark")     # front
    B(chassis, sx0, sx1, 10, 18, 8, 9, "steel_dark")
    B(chassis, sx0, sx1, 12, 16, 9, 10, "steel_dark")
    B(chassis, sx0, sx1, 43, 67, 7, 8, "steel_dark")    # bogie
    B(chassis, sx0, sx1, 45, 65, 8, 9, "steel_dark")
    B(chassis, sx0, sx1, 47, 63, 9, 10, "steel_dark")
    B(chassis, sx0, sx1, 54, 56, 7, 11, "gunmetal_dark")  # bogie pivot
# transfer case + driveshafts
B(chassis, 10, 13, 28, 32, 7, 10, "gunmetal_dark")
cyl_y(chassis, 12, 8, 1, 16, 28, "steel_dark")
cyl_y(chassis, 12, 8, 1, 32, 48, "steel_dark")
cyl_y(chassis, 12, 8, 1, 51, 60, "steel_dark")
# steering box (LEFT-hand drive: +x = left; box sits on the left rail with
# its mount plate flush on the rail top z=11, so the hood block (z>=12)
# clears it; the drag link was deleted, it fouled the tire sweep)
B(chassis, 17, 18, 14, 16, 8, 10, "olive_dark")
B(chassis, 17, 18, 14, 16, 11, 11, "gunmetal_dark")
# fuel tank, left side (+x, cylindrical)
cyl_y(chassis, 21, 8, 3, 28, 36, "olive")
cyl_y(chassis, 21, 8, 3, 28, 28, "olive_dark")
cyl_y(chassis, 21, 8, 3, 36, 36, "olive_dark")
B(chassis, 20, 22, 30, 31, 5, 11, "steel_dark")    # straps
B(chassis, 20, 22, 34, 35, 5, 11, "steel_dark")
B(chassis, 17, 18, 30, 32, 8, 10, "gunmetal_dark")  # support brackets
B(chassis, 17, 18, 33, 35, 8, 10, "gunmetal_dark")
cyl_z(chassis, 21, 32, 1, 11, 12, "dark")           # filler cap
streak(chassis, 18, 30, 10, 4)
streak(chassis, 24, 34, 10, 3)
# exhaust: muffler + pipe, right side (-x; inboard of the rear duals)
B(chassis, 5, 6, 40, 50, 6, 8, "gunmetal_dark")    # muffler
B(chassis, 5, 5, 21, 40, 7, 8, "gunmetal_dark")    # pipe forward
B(chassis, 6, 7, 20, 21, 8, 11, "gunmetal_dark")   # downpipe stub (clear of
# the front-tire sweep; the full downpipe fouled it at -30 deg lock)
B(chassis, 5, 5, 50, 72, 7, 8, "gunmetal_dark")    # tailpipe
B(chassis, 5, 5, 71, 72, 5, 6, "rust_dark")        # sooty tip
# sparse rust on rails / bumper
for (rx, ry) in ((7, 20), (17, 44), (8, 60), (16, 8)):
    streak(chassis, rx, ry, 10, 3)
streak(chassis, 12, 0, 9, 3)

# ================================================================ CAB (static)
# floor + rail pads (pad bottoms z=12 sit on rail tops z=11)
B(cab, 5, 20, 19, 35, 12, 13, "olive")
B(cab, 7, 8, 20, 34, 12, 13, "olive_dark")        # rail pads
B(cab, 16, 17, 20, 34, 12, 13, "olive_dark")
# hood (lowered: top z=18 so the split windscreen reads above it)
B(cab, 7, 18, 2, 19, 12, 17, "olive")             # hood block
B(cab, 7, 18, 2, 3, 12, 15, "olive")              # nose bevel (front lower)
B(cab, 8, 17, 3, 19, 17, 18, "olive")             # hood crown
B(cab, 8, 17, 3, 19, 18, 18, "olive_light")       # sun-faded top
for ly in (6, 8, 10, 12, 14):                     # side vent louvers
    B(cab, 7, 7, ly, ly, 13, 15, "dark")
    B(cab, 18, 18, ly, ly, 13, 15, "dark")
# (hood sides are plain olive — no stencil, per user direction)
# radiator shell + vertical-slat grille
B(cab, 8, 17, 2, 3, 12, 17, "olive")              # shell (bottom z=12 clears the rail tops z=11)
for gx in range(9, 17, 2):                        # vertical slats
    B(cab, gx, gx, 2, 3, 12, 16, "dark")
B(cab, 8, 17, 2, 3, 16, 17, "olive_dark")         # shell top
B(cab, 8, 17, 1, 1, 13, 13, "steel_dark")         # guard bars
B(cab, 8, 17, 1, 1, 17, 17, "steel_dark")
# round headlights in buckets + guards
for hx in (5, 20):
    cyl_y(cab, hx, 15, 2, 2, 4, "olive_dark")      # bucket
    cyl_y(cab, hx, 15, 1, 1, 1, "glass")           # lens
    for bx in (hx - 2, hx, hx + 2):                # guard bars
        B(cab, bx, bx, 1, 1, 13, 17, "steel_dark")
    streak(cab, hx - 2, 2, 14, 3)
# front fenders (plate clears the tire top z=12 by 1; see steering check)
for fx0, fx1 in ((1, 5), (20, 24)):
    B(cab, fx0, fx1, 7, 21, 13, 14, "olive")        # fender plate
    B(cab, fx0, fx1, 7, 21, 14, 14, "olive_light")  # faded top edge
    skx = fx0 if fx0 < 10 else fx1
    B(cab, skx, skx, 7, 23, 12, 13, "olive")        # shallow skirt lip (deep
    # skirts collide with the +/-30 deg tire sweep; the lip clears it)
    B(cab, fx0, fx1, 5, 6, 9, 13, "olive")          # front valance
    B(cab, fx0, fx1, 22, 23, 4, 11, "dark")         # front mudflap
# fender-to-hood fillers
B(cab, 6, 6, 7, 19, 12, 14, "olive")
B(cab, 19, 19, 7, 19, 12, 14, "olive")
# running boards
for bx0, bx1 in ((3, 5), (20, 22)):
    B(cab, bx0, bx1, 20, 34, 11, 12, "steel_dark")
    for ry in range(22, 34, 3):
        B(cab, bx0, bx1, ry, ry, 12, 12, "dark")
# lower stirrup steps (tops z=9 -> 0.81 m; hangers tie them to the boards;
# kept clear of the fuel tank (left, y 28+) and exhaust pipe (right, x=5))
B(cab, 2, 4, 24, 27, 8, 9, "steel_dark")          # right stirrup (-x = right)
B(cab, 2, 4, 24, 27, 10, 10, "steel_dark")        # right hangers
B(cab, 20, 22, 24, 27, 8, 9, "steel_dark")        # left stirrup (+x = left)
B(cab, 20, 22, 24, 27, 10, 10, "steel_dark")      # left hangers
# cab lower body / doors
B(cab, 5, 20, 19, 35, 13, 17, "olive")
for dx in (4, 21):                                # door skins
    B(cab, dx, dx, 24, 34, 13, 17, "olive")
    B(cab, dx, dx, 24, 24, 13, 17, "olive_dark")   # door seams
    B(cab, dx, dx, 34, 34, 13, 17, "olive_dark")
    B(cab, dx, dx, 28, 29, 15, 16, "steel_dark")   # handles
    streak(cab, dx, 28, 14, 3)
# cowl (widened to the cab sides so the mirror stalks attach) + cab back
B(cab, 4, 21, 19, 22, 17, 24, "olive")            # cowl
B(cab, 5, 20, 33, 35, 17, 24, "olive")            # cab back
B(cab, 10, 15, 35, 35, 18, 21, "glass")           # rear window
B(cab, 4, 21, 18, 19, 23, 24, "olive")            # header above windshield
B(cab, 12, 12, 18, 20, 17, 24, "olive")           # windshield center divider
for zi in range(17, 23):                          # split windshield, slight rake
    yy = 19 - (zi - 17) // 3
    B(cab, 6, 12, yy, yy, zi, zi, "glass")
    B(cab, 13, 19, yy, yy, zi, zi, "glass")
# side windows + frames: smaller glass (7 wide x 4 tall), deeper sill and
# pillars so the door reads mostly solid panel
for wx in (4, 21):
    B(cab, wx, wx, 26, 32, 18, 21, "glass")
    B(cab, wx, wx, 24, 34, 16, 17, "olive")       # sill
    B(cab, wx, wx, 24, 34, 22, 23, "olive")       # top rail
    B(cab, wx, wx, 24, 25, 16, 23, "olive")       # front pillar
    B(cab, wx, wx, 33, 34, 16, 23, "olive")       # rear pillar
# roof (top z=26 -> 2.34 m)
B(cab, 4, 20, 18, 36, 24, 26, "olive")
B(cab, 5, 19, 19, 35, 26, 26, "olive_light")      # faded roof skin
B(cab, 4, 20, 18, 18, 24, 25, "olive_dark")       # drip rails
B(cab, 4, 20, 36, 36, 24, 25, "olive_dark")
# mirrors on stalks
B(cab, 3, 3, 20, 20, 20, 23, "steel_dark")        # right stalk (-x = right)
B(cab, 2, 3, 19, 19, 22, 24, "olive_dark")        # right head
B(cab, 2, 2, 19, 19, 22, 24, "glass")             # right glass
B(cab, 22, 22, 20, 20, 20, 23, "steel_dark")      # left stalk (+x = left)
B(cab, 22, 23, 19, 19, 22, 24, "olive_dark")      # left head
B(cab, 23, 23, 19, 19, 22, 24, "glass")           # left glass
streak(cab, 3, 20, 21, 2)
streak(cab, 22, 20, 21, 2)
# bench seat + dash + steering wheel (seen through glass)
B(cab, 7, 18, 28, 31, 13, 14, "canvas_dark")      # cushion
B(cab, 7, 18, 31, 31, 14, 19, "canvas_dark")      # backrest
B(cab, 6, 19, 20, 20, 15, 17, "olive_dark")       # dash
B(cab, 16, 16, 21, 22, 15, 17, "gunmetal_dark")   # column (LEFT-hand drive: +x = left)
ring_y(cab, 16, 17, 2, 23, 23, "dark")            # steering wheel
B(cab, 15, 17, 23, 23, 16, 18, "dark")            # spokes
# spare tire on carrier behind cab (vertical, y 35-37)
cyl_y(cab, 12, 17, 6, 35, 37, "tire")
ring_y(cab, 12, 17, 6, 35, 35, "tire_side")
cyl_y(cab, 12, 17, 2, 35, 37, "steel_dark")
cyl_y(cab, 12, 17, 1, 35, 37, "olive_dark")
tread_ring_y(cab, 12, 17, 6, 35, 37, "tire_side", n=12)
B(cab, 10, 14, 34, 36, 8, 11, "steel_dark")       # carrier bracket

# ================================================================ WHEELS FRONT (steerable pair)
for sx in (3, 22):                                # kingpin x
    cyl_x(wheels_front, 14, 6, 6, sx - 1, sx + 1, "tire")
    ring_x(wheels_front, 14, 6, 6, sx - 1, sx - 1, "tire_side")  # sidewall rings
    ring_x(wheels_front, 14, 6, 6, sx + 1, sx + 1, "tire_side")
    tread_ring(wheels_front, 14, 6, 6, sx - 1, sx + 1, "tire_side")
    cyl_x(wheels_front, 14, 6, 2, sx - 1, sx + 1, "steel_dark")  # hub
    cyl_x(wheels_front, 14, 6, 1, sx - 1, sx + 1, "olive_dark")  # hub cap
    cyl_z(wheels_front, sx, 14, 1, 6, 10, "steel_dark")          # kingpin
    B(wheels_front, sx - 1, sx + 1, 13, 15, 9, 11, "gunmetal_dark")  # knuckle
# steer pivots: STEER_L=(22,14,6), STEER_R=(3,14,6) about z; spin about x-axis

# ================================================================ WHEELS REAR (bogie duals)
for ay in (49, 61):
    for xi0 in (1, 20):                           # dual pair: inner+outer
        cyl_x(wheels_rear, ay, 6, 6, xi0, xi0 + 1, "tire")        # inner
        cyl_x(wheels_rear, ay, 6, 6, xi0 + 2, xi0 + 3, "tire")    # outer
        ring_x(wheels_rear, ay, 6, 6, xi0 + 3, xi0 + 3, "tire_side")
        tread_ring(wheels_rear, ay, 6, 6, xi0, xi0 + 1, "tire_side")
        tread_ring(wheels_rear, ay, 6, 6, xi0 + 2, xi0 + 3, "tire_side")
        cyl_x(wheels_rear, ay, 6, 2, xi0 + 1, xi0 + 2, "steel_dark")  # hub
        cyl_x(wheels_rear, ay, 6, 1, xi0 + 3, xi0 + 3, "olive_dark")
# spin pivots (x-axis): (3,49,6),(22,49,6),(3,61,6),(22,61,6)
# 1-voxel parting cut at the bogie tangent plane so the two axles' duals
# stay separate running-gear components
wheels_rear = {p: c for p, c in wheels_rear.items() if p[1] != 55}

# ================================================================ BED BUILDER (flat / covered / technical)
def build_bed(d, technical=False):
    # sills seat on the rail tops (sill bottom z=12 on rail top z=11)
    B(d, 7, 8, 37, 74, 12, 13, "wood_dark")
    B(d, 16, 17, 37, 74, 12, 13, "wood_dark")
    # plank floor with gaps
    B(d, 4, 20, 37, 74, 13, 14, "wood")
    for gx in (7, 10, 13, 16, 19):
        B(d, gx, gx, 37, 74, 13, 14, "wood_dark")
    # 3-board sides + top rail (lowered on the technical for the gun sweep)
    side_top = 20 if technical else 22
    for bx in (4, 20):
        B(d, bx, bx, 37, 74, 14, 16, "wood")
        B(d, bx, bx, 37, 74, 17, 19, "wood")
        B(d, bx, bx, 37, 74, 20, side_top, "wood")
        B(d, bx, bx, 37, 74, 16, 16, "wood_dark")   # board seams
        B(d, bx, bx, 37, 74, 19, 19, "wood_dark")
        B(d, bx, bx, 37, 74, side_top, side_top, "wood_dark")  # top rail cap
    # headboard + tailgate (lowered on the technical so the gun sweep clears)
    hb_top = 18 if technical else 24
    tg_top = 18 if technical else 22
    B(d, 4, 20, 37, 37, 13, hb_top, "wood")         # headboard
    B(d, 4, 20, 37, 37, hb_top, hb_top, "wood_dark")
    B(d, 4, 20, 74, 74, 13, tg_top, "wood")        # tailgate
    B(d, 5, 5, 74, 74, 14, 16, "steel_dark")       # hinges
    B(d, 19, 19, 74, 74, 14, 16, "steel_dark")
    # stake pockets
    for px in (3, 21):
        for py in (42, 54, 67):
            B(d, px, px, py, py, 14, 20, "steel_dark")
            streak(d, px, py, 19, 3)
    # mudguards arched over the rear duals (plate clears tire top z=12)
    for mx0, mx1 in ((0, 5), (19, 24)):
        B(d, mx0, mx1, 41, 69, 13, 14, "olive")
        B(d, mx0, mx1, 41, 69, 14, 14, "olive_light")
        for ay in (49, 61):                         # arch skirt follows r=7
            for dy in range(-7, 8):
                ztop = 6 + int((49 - dy * dy) ** 0.5)
                sx = mx0 if mx0 < 10 else mx1
                for z in range(8, min(ztop, 13) + 1):
                    d[(sx, ay + dy, z)] = CI["olive"]
    # mudflaps behind the rear duals (shifted 1 vox rearward: the rearmost
    # tire reaches y=67, so the flap starts at y=68)
    B(d, 1, 4, 68, 70, 4, 12, "dark")
    B(d, 20, 23, 68, 70, 4, 12, "dark")
    # sparse rust from stake pockets
    streak(d, 4, 42, 19, 4)
    streak(d, 21, 67, 19, 3)


build_bed(bed_flat)

# ---- covered: flatbed + 4 hoops + closed canvas
build_bed(bed_covered)
for hy in (42, 51, 60, 69):                         # hoops from the bed floor
    B(bed_covered, 4, 4, hy, hy, 14, 28, "wood_dark")     # legs
    B(bed_covered, 20, 20, hy, hy, 14, 28, "wood_dark")
    B(bed_covered, 4, 20, hy, hy, 28, 28, "wood_dark")    # beam
    B(bed_covered, 6, 18, hy, hy, 29, 30, "wood_dark")    # apex z=30
# canvas SHELL, 2 voxels thick, draped over the 4-hoop profile; the
# interior stays hollow (the old solid fill buried ~44% of its voxels)
def _ctop(x):
    return 30 if 6 <= x <= 18 else 28
for _x in range(4, 21):                           # roof skin follows the hoops
    _t = _ctop(_x)
    B(bed_covered, _x, _x, 38, 73, _t - 1, _t, "canvas")
for _x0, _x1 in ((4, 5), (19, 20)):                # side drapes, 2 thick
    B(bed_covered, _x0, _x1, 38, 73, 16, 28, "canvas")
for _x in range(4, 21):                           # front face, 2 thick
    B(bed_covered, _x, _x, 38, 39, 16, _ctop(_x), "canvas")
B(bed_covered, 4, 20, 73, 74, 14, 28, "canvas")    # closed rear flap, 2 thick
B(bed_covered, 4, 20, 73, 74, 28, 28, "canvas_dark")  # flap top roll
for hy in (42, 51, 60, 69):                       # hoop rib shading, outer surface
    for _x in range(4, 21):
        _t = _ctop(_x)
        B(bed_covered, _x, _x, hy, hy, _t - 1, _t, "canvas_dark")
    B(bed_covered, 4, 5, hy, hy, 16, 28, "canvas_dark")
    B(bed_covered, 19, 20, hy, hy, 16, 28, "canvas_dark")
for tx in (6, 12, 18):                            # tie-downs on the flap
    B(bed_covered, tx, tx, 73, 74, 16, 24, "dark")

# ---- technical: flatbed + AA pedestal ring (static cargo unit)
build_bed(bed_technical, technical=True)
ring_z(bed_technical, 12, 55, 5, 14, 18, "olive_dark")   # pedestal ring
cyl_z(bed_technical, 12, 55, 4, 14, 15, "olive")          # pintle disc
ring_z(bed_technical, 12, 55, 5, 17, 18, "gunmetal_dark")  # traverse gear
cyl_z(bed_technical, 12, 55, 1, 14, 18, "steel")         # pintle
for (bx, by) in ((7, 55), (17, 55), (12, 50), (12, 60)):
    B(bed_technical, bx, bx, by, by, 18, 18, "steel_dark")  # bolts (flush)

# ================================================================ AA TURRET (traverse about (12,55) z-axis)
cyl_z(aa_turret, 12, 55, 6, 18, 20, "olive")        # turntable plate
ring_z(aa_turret, 12, 55, 6, 19, 20, "olive_dark")  # rim
B(aa_turret, 9, 15, 53, 57, 20, 22, "olive_dark")   # cradle crossbeam
B(aa_turret, 9, 10, 50, 60, 20, 27, "olive")        # cradle cheeks
B(aa_turret, 14, 15, 50, 60, 20, 27, "olive")
B(aa_turret, 9, 10, 50, 60, 27, 28, "olive_dark")   # cheek caps
B(aa_turret, 14, 15, 50, 60, 27, 28, "olive_dark")
cyl_x(aa_turret, 55, 23, 2, 7, 18, "gunmetal")      # trunnion
cyl_x(aa_turret, 55, 23, 1, 6, 6, "gunmetal_dark")  # trunnion end caps
cyl_x(aa_turret, 55, 23, 1, 19, 19, "gunmetal_dark")
# (cheek bolts deleted: the elevation sweep machines through (9/15, 59,
# 24-26) — the old bolts sat inside the barrel tubes; no bolt position on
# the cheek outer face clears the elevating tubes)
# gunner seat (traverses with the mount; kept at z>=19 and close to the
# pivot so the +/-90 deg sweep clears the bed sides and the pedestal)
B(aa_turret, 11, 12, 49, 50, 18, 21, "olive_dark")  # riser off the turntable
B(aa_turret, 11, 12, 44, 50, 21, 22, "olive_dark")  # support arm
B(aa_turret, 10, 14, 43, 46, 22, 23, "gunmetal")    # pan
B(aa_turret, 10, 14, 43, 43, 22, 28, "olive_dark")  # backrest
# AA reflector sight, left cheek
B(aa_turret, 8, 8, 53, 54, 23, 27, "steel_dark")    # sight post
ring_y(aa_turret, 8, 28, 2, 52, 53, "steel_dark")   # sight ring
B(aa_turret, 7, 9, 52, 53, 27, 29, "glass")        # reflector
# ammo boxes flanking (raised onto the turntable level so the traverse
# sweep clears the pedestal ring) + feed chutes
for (ax0, ax1, sx) in ((5, 8, 5), (16, 19, 19)):
    B(aa_turret, ax0, ax1, 50, 60, 21, 25, "olive")
    B(aa_turret, ax0, ax1, 50, 60, 26, 26, "olive_dark")  # lid
    B(aa_turret, sx, sx, 53, 56, 22, 23, "dark")          # stencil slot
B(aa_turret, 8, 8, 52, 56, 21, 23, "steel_dark")    # feed chutes
B(aa_turret, 16, 16, 52, 56, 21, 23, "steel_dark")
B(aa_turret, 8, 8, 52, 52, 23, 24, "brass")         # ammo hint
B(aa_turret, 16, 16, 52, 52, 23, 24, "brass")
# elevating handwheel, right cheek
cyl_x(aa_turret, 56, 22, 1, 16, 19, "gunmetal")
ring_x(aa_turret, 56, 22, 2, 19, 19, "steel_dark")
B(aa_turret, 19, 19, 55, 57, 20, 24, "steel_dark")  # spokes
B(aa_turret, 19, 19, 54, 58, 21, 23, "steel_dark")

# ================================================================ AA BARRELS (elevation about x-axis at (12,55,23))
for rx0 in (9, 14):                                 # twin receivers
    B(aa_barrels, rx0, rx0 + 1, 47, 57, 21, 25, "olive")
    B(aa_barrels, rx0, rx0 + 1, 49, 55, 25, 26, "olive_dark")  # top cover
    B(aa_barrels, rx0, rx0 + 1, 46, 46, 21, 25, "gunmetal_dark")  # buttplate
    B(aa_barrels, rx0, rx0, 45, 46, 22, 24, "dark")  # spade grip (points
    # rearward so the traverse sweep clears the bed sides)
    B(aa_barrels, rx0 + 2, rx0 + 2, 50, 51, 23, 24, "steel_dark")  # charger
    B(aa_barrels, rx0, rx0 + 1, 57, 85, 22, 24, "gunmetal")  # barrel
    for collar_y in (63, 71, 79):                   # barrel collars
        B(aa_barrels, rx0 - 1, rx0 + 2, collar_y, collar_y + 1, 21, 25,
          "gunmetal_dark")
    B(aa_barrels, rx0 - 1, rx0 + 2, 85, 86, 21, 25, "gunmetal_dark")  # brake root
    B(aa_barrels, rx0 - 1, rx0 + 2, 86, 88, 21, 25, "gunmetal_dark")  # brake flare
    B(aa_barrels, rx0, rx0 + 1, 87, 88, 22, 24, "dark")  # bore shadow
B(aa_barrels, 9, 15, 70, 71, 22, 24, "gunmetal_dark")  # barrel crossbar
B(aa_barrels, 11, 13, 55, 57, 20, 26, "gunmetal_dark")  # trunnion saddle
# barrels authored horizontal (0 deg), pointing +y; muzzle reaches y=88

# ================================================================ post-build clearance carves
# Fix 7a: chassis/cab must intersect ONLY at the intended mounting pads
# (pad bottoms z=12 sit ON rail tops z=11 — adjacent, never overlapping).
# The radiator shell bottom was raised to z=12 and the steering box moved to
# the left rail (top z=11) above; carve any remaining cab/chassis overlap
# (exhaust vs front mudflap, fuel tank vs running board, driveshaft vs
# spare-tire bracket, ...) out of the cab.
_ch_set = set(chassis)
_clear7a = [p for p in cab if p in _ch_set]
for p in _clear7a:
    del cab[p]

# Fix 1: breech well. The elevation sweep (-5..+90 deg about the x-axis at
# (12,55,23)) is machined out of the turret and the technical bed, keeping
# the trunnion solid (r<=2.5 about the elevation axis). The turntable stays
# an annulus so the cradle cheeks (which ride the trunnion axle) stay
# connected; the pedestal becomes a ring and the bed floor gets a slot.
# The gunner seat keeps its place — the sweep only nicks its front edge.
def rot_x(pts, cy, cz, deg):
    r = math.radians(deg)
    out = set()
    for (x, y, z) in pts:
        dy, dz = y - cy, z - cz
        out.add((x, round(cy + dy * math.cos(r) - dz * math.sin(r)),
                 round(cz + dy * math.sin(r) + dz * math.cos(r))))
    return out

_swept = set()
for _deg in range(-5, 91):
    _swept |= rot_x(set(aa_barrels), 55, 23, _deg)
_keep = {(x, y, z) for (x, y, z) in aa_turret
         if (y - 55) ** 2 + (z - 23) ** 2 <= 6.25 and 6 <= x <= 19}
_well = _swept - _keep
_well_turret = [p for p in aa_turret if p in _well]
_well_bed = [p for p in bed_technical if p in _well]
for p in _well_turret:
    del aa_turret[p]
for p in _well_bed:
    del bed_technical[p]
# The well machines the cheek middles where the receivers nest at rest; the
# right cheek cap's front (x 14-15, y 50-53, z 27-28) loses its seat. Bridge
# it sideways onto the right ammo-box lid (z=26) — the four voxels sit clear
# of the elevation sweep (verified: not in _swept).
B(aa_turret, 16, 16, 50, 53, 27, 27, "olive_dark")  # cheek-cap support ledge

# ================================================================ assembled merges
assembled_flat = dict(chassis)
assembled_flat.update(wheels_front)
assembled_flat.update(wheels_rear)
assembled_flat.update(cab)
assembled_flat.update(bed_flat)

assembled_covered = dict(chassis)
assembled_covered.update(wheels_front)
assembled_covered.update(wheels_rear)
assembled_covered.update(cab)
assembled_covered.update(bed_covered)

assembled_technical = dict(chassis)
assembled_technical.update(wheels_front)
assembled_technical.update(wheels_rear)
assembled_technical.update(cab)
assembled_technical.update(bed_technical)
assembled_technical.update(aa_turret)
assembled_technical.update(aa_barrels)

PARTS = {
    "zil157-chassis-v1": chassis,
    "zil157-cab-v1": cab,
    "zil157-wheels-front-v1": wheels_front,
    "zil157-wheels-rear-v1": wheels_rear,
    "zil157-bed-flat-v1": bed_flat,
    "zil157-bed-covered-v1": bed_covered,
    "zil157-bed-technical-v1": bed_technical,
    "zil157-bed-aa-turret-v1": aa_turret,
    "zil157-bed-aa-barrels-v1": aa_barrels,
    "zil157-assembled-flat-v1": assembled_flat,
    "zil157-assembled-covered-v1": assembled_covered,
    "zil157-assembled-technical-v1": assembled_technical,
}


# ------------------------------------------------- scale figure (preview only)
def build_soldier():
    """Blocky 25-voxel / 1.5 m infantryman, standing at the cab door."""
    s = {}
    def b(x0, x1, y0, y1, z0, z1, c):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    s[(x, y, z)] = CI[c]
    b(24, 26, 26, 29, 0, 1, "dark")        # boots
    b(24, 24, 26, 29, 2, 9, "olive_dark")  # legs
    b(26, 26, 26, 29, 2, 9, "olive_dark")
    b(24, 26, 26, 29, 10, 17, "olive_dark")  # torso
    b(23, 23, 26, 29, 11, 16, "olive_dark")  # arms
    b(27, 27, 26, 29, 11, 16, "olive_dark")
    b(24, 26, 26, 29, 18, 21, "olive_dark")  # head
    b(24, 26, 26, 29, 22, 23, "olive")       # cap
    b(25, 25, 26, 29, 24, 24, "dark")        # cap top
    return s


# ---------------------------------------------------------------- .vox writer (MagicaVoxel 150)
# Verbatim from the skill boilerplate, plus optional xoff/yoff so every rig
# part shares one design frame (file coords == design coords).
def write_vox(path, vox, PALETTE, xoff=None, yoff=None):
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


# ---------------------------------------------------------------- isometric preview render
def render_preview(path, vox, PALETTE, scale=3):
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


# ---------------------------------------------------------------- top-down slice (dev check)
def render_slice(path, vox, PALETTE, z):
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


# ---------------------------------------------------------------- .vox reader (validation)
def read_vox(path):
    data = open(path, "rb").read()
    i = data.find(b"XYZI")
    n = struct.unpack("<i", data[i + 12:i + 16])[0]
    j = data.find(b"RGBA")
    pal = [struct.unpack("BBBB", data[j + 8 + k * 4:j + 12 + k * 4])[:3]
           for k in range(256)]
    vox, off = {}, i + 16
    for _ in range(n):
        x, y, z, c = struct.unpack("BBBB", data[off:off + 4]); off += 4
        vox[(x, y, z)] = c
    return vox, pal


def components(d):
    """6-connected component sizes, largest first."""
    vset = set(d)
    seen = set()
    sizes = []
    for seed in vset:
        if seed in seen:
            continue
        q = deque([seed]); seen.add(seed); n = 0
        while q:
            x, y, z = q.popleft(); n += 1
            for nb in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                       (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if nb in vset and nb not in seen:
                    seen.add(nb); q.append(nb)
        sizes.append(n)
    return sorted(sizes, reverse=True)


def contact_count(a, b, za, zb):
    """Voxel positions where part a has z=za and part b has z=zb at same (x,y)."""
    bs = {(x, y) for (x, y, z) in b if z == zb}
    return sum(1 for (x, y, z) in a if z == za and (x, y) in bs)


def rotate_z(pts, cx, cy, deg):
    r = math.radians(deg)
    out = set()
    for (x, y, z) in pts:
        dx, dy = x - cx, y - cy
        out.add((round(cx + dx * math.cos(r) - dy * math.sin(r)),
                 round(cy + dx * math.sin(r) + dy * math.cos(r)), z))
    return out


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    soldier = build_soldier()

    for name, d in PARTS.items():
        write_vox(os.path.join(here, name + ".vox"), d, PALETTE, 0, 0)
        pv = dict(d)
        if name.startswith("zil157-assembled"):
            pv.update(soldier)
        render_preview(os.path.join(here, name + "_preview.png"), pv, PALETTE)

    print("\n== per-part stats ==")
    for name, d in PARTS.items():
        xs = [p[0] for p in d]; ys = [p[1] for p in d]; zs = [p[2] for p in d]
        comps = components(d)
        print(f"{name}: {len(d)} vox, "
              f"bbox {max(xs)-min(xs)+1}x{max(ys)-min(ys)+1}x{max(zs)+1}, "
              f"components={len(comps)} sizes={comps[:6]}")

    print("\n== clearance carves ==")
    print(f"Fix 7a: removed {len(_clear7a)} cab/chassis overlap voxels from cab; "
          f"{len(set(chassis) & set(cab))} remain")
    print(f"Fix 1: breech well machined {len(_well_turret)} turret + "
          f"{len(_well_bed)} bed-technical voxels")

    print("\n== interface contacts ==")
    print("cab pads z=12 on chassis rail tops z=11:",
          contact_count(cab, chassis, 12, 11))
    print("bed-flat sills z=12 on rail tops z=11:",
          contact_count(bed_flat, chassis, 12, 11))
    print("bed-technical sills z=12 on rail tops z=11:",
          contact_count(bed_technical, chassis, 12, 11))
    print("pedestal ring z=14 on bed floor top z=13:",
          contact_count(bed_technical, bed_technical, 14, 13))
    print("front wheels touch z=0:",
          sum(1 for p in wheels_front if p[2] == 0))
    print("rear wheels touch z=0:",
          sum(1 for p in wheels_rear if p[2] == 0))

    print("\n== steering sweep: front tire rotated +/-30 deg vs body ==")
    print("   (body = cab + chassis z>=8; axle/knuckle contact is intended)")
    body = set(cab) | {(x, y, z) for (x, y, z) in chassis if z >= 8}
    for sx, label in ((STEER_L[0], "L"), (STEER_R[0], "R")):
        tire = {(x, y, z) for (x, y, z) in wheels_front
                if abs(x - sx) <= 1 and 8 <= y <= 20}
        for deg in (30, -30):
            swept = rotate_z(tire, sx, 14, deg)
            hits = sorted(swept & body)
            print(f"wheel {label} {deg:+d} deg: {len(hits)} colliding voxels"
                  + (f" e.g. {hits[:4]}" if hits else ""))
            assert not hits, f"steering {label} {deg}"

    print("\n== AA traverse +-140 deg vs technical bed ==")
    # barrels at 0 deg vs technical bed (tailgate/headboard/sides)
    barrel = set(aa_barrels)
    tbed = set(bed_technical)
    print("barrels vs bed-technical at rest:", len(barrel & tbed))
    def traverse_hits(part, deg):
        m = rotate_z(part, 12, 55, deg)
        hits = [q for q in m if q in tbed]
        # intended: turntable bottom (z=18) riding the pedestal gear (r<=6)
        interface = [q for q in hits
                     if q[2] == 18 and (q[0] - 12) ** 2 + (q[1] - 55) ** 2 <= 36]
        return len(hits) - len(interface), len(interface)
    for deg in (140, -140):
        real, iface = traverse_hits(barrel, deg)
        print(f"barrels vs bed-technical at traverse {deg}: {real} "
              f"(+{iface} turntable/pedestal interface)")
        assert real == 0, f"barrel traverse {deg}"
        real, iface = traverse_hits(set(aa_turret), deg)
        print(f"turret vs bed-technical at traverse {deg}: {real} "
              f"(+{iface} turntable/pedestal interface)")
        assert real == 0, f"turret traverse {deg}"
    # elevation sweep -5..+90 deg: rotate barrels about the x-axis at
    # (12,55,23); the only permitted contact is the trunnion wrap
    print("\n== AA elevation sweep: -5..+90 deg vs mount + truck ==")
    truck = (set(bed_technical) | set(aa_turret) | set(chassis) | set(cab))
    for deg in range(-5, 91):
        hits = (rot_x(barrel, 55, 23, deg) & truck) - _keep
        assert not hits, f"elevation {deg}: {sorted(hits)[:6]}"
    print("0 unintended hits from -5 to +90 deg (trunnion wrap excluded)")
    first = None
    for deg in range(91, 131):
        hits = (rot_x(barrel, 55, 23, deg) & truck) - _keep
        if hits:
            first = (deg, sorted(hits)[:6])
            break
    print("first contact beyond +90 deg:", first)

    print("\n== scale checks (measured from the voxels) ==")
    ax = [p[0] for p in assembled_flat]; ay = [p[1] for p in assembled_flat]
    length = max(ay) - min(ay) + 1
    width = max(ax) - min(ax) + 1
    glass_bottom = min(p[2] for p in cab
                      if cab[p] == CI["glass"] and p[0] in (4, 21)
                      and 24 <= p[1] <= 34)   # door side windows (not headlight lenses)
    assert (length, width, glass_bottom) == (78, 25, 18), \
        (length, width, glass_bottom)
    print(f"cab roof z=26 -> {26 * TRUCK_VOXEL:.2f} m (real 2.36 m)")
    print(f"door window glass bottom z={glass_bottom} -> "
          f"{glass_bottom * TRUCK_VOXEL:.2f} m")
    print(f"overall length {length} vox (y 0-77 incl. rear tow hitch) -> "
          f"{length * TRUCK_VOXEL:.2f} m (real 6.93 m)")
    print(f"width {width} vox (bed x 0-24) -> {width * TRUCK_VOXEL:.2f} m "
          f"(real 2.32 m)")
    print(f"wheel dia 13 vox -> {13 * TRUCK_VOXEL:.2f} m (real 1.20 m)")
    print(f"diff bottom z=3 -> {3 * TRUCK_VOXEL:.2f} m (real clearance 0.31 m)")
    print(f"front axle->bogie center: 55-14=41 vox -> {41 * TRUCK_VOXEL:.2f} m (real 3.66 m)")
    print(f"bogie spacing 12 vox -> {12 * TRUCK_VOXEL:.2f} m (real 1.12 m)")

    print("\n== .vox color verification (changed/new colors) ==")
    for name in PARTS:
        vox, pal = read_vox(os.path.join(here, name + ".vox"))
        counts = {}
        for ci in vox.values():
            counts[ci] = counts.get(ci, 0) + 1
        named = {PALETTE[ci - 1][0]: n for ci, n in sorted(counts.items())}
        interesting = {k: v for k, v in named.items()
                       if k in ("white", "red", "brass", "rust", "rust_dark",
                                "glass", "canvas", "canvas_dark", "wood")}
        print(f"{name}: {interesting}")

    print("\npivots: STEER_L", STEER_L, "STEER_R", STEER_R,
          "TRAVERSE", TRAVERSE_PIVOT, "ELEVATION", ELEVATION_PIVOT)
