#!/usr/bin/env python3
"""Strike Bay — Osa II missile boat, v2 (closer to the new concept sheet).

v2 vs v1 (see osa3/gaps.md): raked stem + bow flare, stronger sheer, tall
black boot-top, stepped bridge with square windows, solid tapered mast with
a planar-array radar, chamfered-box (not tube) launchers, bigger radome on a
stepped square tower, lower aft house + open quarterdeck with a big ensign,
boxy fore turret, smoother oxide deck with brighter trim, round life rings,
orange lockers. Round 2 (judge scores): horizontal strake shading on the
flare, linear evenly-spaced sheer, hull flares from the boot band, radar
panel at 70%, bridge one row taller and full-width, no stern props.
Contracts unchanged from v1: part split, voxel scales, ~18 m hull, box tilt
12° (MISSILE_DIR), WATERLINE_Z, bow = -y. Round 3 (owner: shrink boxes):
launch boxes resized to the halved P-15 — length 34, bore 5.4/R 6.5,
centres outboard at x 8.0/35.0, mouths y 48/118 z 39; MISSILE_SEATS moved
with the mouths.

Reference: owner concept sheet "OSA II CLASS MISSILE BOAT" (grey hull, oxide
red deck with a bright red deck-edge trim, light-grey stepped deckhouse,
solid mast with a rotating planar radar, beige "Drum Tilt" radome aft of the
mast, four P-15 launch boxes two per side, a gun forward, open aft deck).

SCALE  OSA_VOXEL = 0.1 m (hull, radar). The AK-630 turret and gun are on a
       2x fine grid, OSA_FINE = 0.05 m, so the gatling reads round.
       Hull ~18 m (owner: 0.6x the 28.7 m carrier), not the real 38.4 m.
       The launch boxes are stretched to ~6.2 m so the game's life-size P-15
       (5.85 m) fits inside them and slides out of the front.

Frame: z-up, x = across, y = fore-aft; forward (bow) = file -y (the ZIL /
CIWS convention). Port = low x, starboard = high x (looking forward, -y).

Parts (one 6-connected component each):
  osa-hull-v2    static: hull, deck, deckhouse, mast, radome, 4 launch
                 boxes, aft deckhouse, rails, ensign       (0.1 m)
  osa-radar-v2   spin: the mast-top radar about the vertical line
                 RADAR_SPIN (x, y)                         (0.1 m)
  osa-turret-v2  traverse: AK-630 turret about TURRET_AXIS (x, y) (0.05 m)
  osa-gun-v2     elevation: gatling + mantlet about GUN_PIVOT (y, z);
                 child of the turret                        (0.05 m)
  osa-assembled-v2  coarse merge for browsing (turret/gun downsampled)

Landmarks (file voxel cells, for agents without vision):
  FRONT  bow stem tip y=0, x 21..22, at deck height z~29. Forward = -y.
  BACK   flat transom y=179 (x 3..40). Ensign staff at (22, 177).
  UP     +z. Keel z=0 amidships; the forefoot rises toward the stem and
         the stem rakes back below the waterline.
  WATERLINE z=10 (WATERLINE_Z): hull below it is the dark bottom colour,
         boot-top z 10..12. Sit the model so z=10 is at the sea surface.
  DECK   z=24 at the stern rising linearly to z=29 at the bow (DECK_Z(y);
         1-cell steps evenly spaced every 30 stations).
  Hull parts (coarse cells):
         hull shell   x 0..43   y 0..179   z 0..29 (flare from boot band up)
         deckhouse    x 16..27  y 38..104  z 25..34; bridge x 16..27
                      y 35..63 to z 47 (stepped, flat front), wings z 45
         mast         solid pylon x 20..23, y 63..68, z 35..80
         radome       centre (21.5, 122, 59), r 9, on a stepped tower z 25..50
         launch boxes LAUNCHERS list: port/starboard x 8.0 / 35.0, outer
                      half 6.5 (bore 5.4), length 34 along the 12° axis;
                      forward pair mouth y 48 -> rear y~81; aft pair mouth
                      y 118 -> rear y~151; mouths at z 39, front higher.
  Links  turret sits on the hull's GUN_RING top z=TURRET_DECK_Z at hull
         cell TURRET_MOUNT (x, y); radar sits on the mast top at hull cell
         RADAR_MOUNT (x, y, z).
  Points MISSILE_SEATS: hull cells of the nose-tip position inside each
         box mouth (P-15 nose goes here, tail toward the box rear);
         MISSILE_DIR: unit fire direction in file coords (forward-up, 12°).
         MUZZLE (fine turret-file cells): the gatling muzzle centre.
"""
import math
import os

OSA_VOXEL = 0.1
OSA_FINE = 0.05

PALETTE = [
    ("hull",       (132, 138, 144)),  # 1 hull sides
    ("hull_light", (158, 163, 168)),  # 2 sheer strake under the trim
    ("bottom",     ( 62,  50,  44)),  # 3 below the waterline (dark brown)
    ("boot",       ( 24,  24,  26)),  # 4 boot-top band
    ("deck",       (166,  64,  46)),  # 5 oxide red deck
    ("deck_trim",  (224,  84,  52)),  # 6 deck-edge trim, rail tops
    ("house",      (176, 180, 184)),  # 7 deckhouse, superstructure
    ("house_dark", (130, 135, 140)),  # 8 shadowed faces, panel lines
    ("glass",      ( 30,  38,  50)),  # 9 bridge windows, portholes
    ("box",        (190, 193, 196)),  # 10 launch boxes
    ("box_band",   (142, 146, 150)),  # 11 box bands, supports
    ("radome",     (228, 216, 192)),  # 12 Drum Tilt radome
    ("steel",      ( 92,  96, 102)),  # 13 mast, gun, fittings
    ("dark",       ( 34,  36,  40)),  # 14 bores, hawse, vents
    ("flag_red",   (190,  44,  38)),  # 15 ensign
    ("flag_white", (236, 233, 226)),  # 16 ensign field, life rings
    ("ring",       (224, 108,  44)),  # 17 life rings / orange lockers
    ("deck_dark",  (138,  54,  42)),  # 18 plank seams
    ("deck_light", (176,  80,  62)),  # 19 (kept for palette stability)
    ("bronze",     (150, 110,  62)),  # 20 props / rudders
]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

L = 180               # hull length (y 0..179)
B = 44                # beam (x 0..43)
CX = 21.5             # centreline x (continuous)
WATERLINE_Z = 10


def DECK_Z(y):
    """Deck top row at station y: 24 aft rising to 29 at the bow, LINEAR
    sheer (round 2): the five 1-cell steps land at y=15/45/75/105/135 —
    evenly spaced every 30 stations — so the deck line and red trim read
    as one smooth curve with no clustered jump (the v2 quadratic
    clustered its first step 7 stations off the stem)."""
    t = max(0.0, 1.0 - y / 150.0)
    return 24 + int(round(5 * t))


def put(d, x, y, z, c):
    d[(x, y, z)] = CI[c]


def box(d, x0, x1, y0, y1, z0, z1, c):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                put(d, x, y, z, c)


def disk_z(d, cx, cy, r, z, c, r_in=None):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            q = (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2
            if q <= r * r and (r_in is None or q > r_in * r_in):
                put(d, x, y, z, c)


def disk_y(d, cx, cz, r, y, c, r_in=None):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            q = (x + 0.5 - cx) ** 2 + (z + 0.5 - cz) ** 2
            if q <= r * r and (r_in is None or q > r_in * r_in):
                put(d, x, y, z, c)


# --- hull ---------------------------------------------------------------------

def half_beam(y, z):
    """Hull half-width (continuous, from CX) at station y and row z."""
    # plan: full bow shoulders (low exponent), slight taper to the transom
    if y < 64:
        t = y / 64.0
        plan = 1.0 - (1.0 - t) ** 1.55
    elif y > 160:
        plan = 1.0 - 0.06 * (y - 160) / 19.0
    else:
        plan = 1.0
    # section: V below the waterline; above the boot band the whole hull
    # flares continuously to the deck edge (round 2), the bow hardest
    if z < WATERLINE_Z:
        sec = 0.42 + 0.48 * (z / WATERLINE_Z)
        if y < 64:
            sec *= 0.82 + 0.18 * (y / 64.0)
    else:
        zt = DECK_Z(y)
        frac = (z - WATERLINE_Z) / max(1, zt - WATERLINE_Z)
        sec = 0.90 + 0.14 * frac
        if y < 80:
            sec += 0.03 * frac * (1.0 - y / 80.0)
    return (B / 2.0) * plan * sec


def stem_min_y(z):
    """Raked stem: the lowest bow stations start aft of y=0."""
    if z >= 20:
        return 0
    return int(round((20 - z) * 0.75))


def plank(x, y):
    """Deck finish: smooth oxide red, faint butt seams every 2.4 m only —
    the concept deck has no per-plank hash (v1 read speckled)."""
    strip = x // 2
    yy = y + 7 * strip
    if yy % 24 == 0:
        return "deck_dark"                           # butt joint
    return "deck"


def keel_z(y):
    """Bottom row at station y: the forefoot rises toward the stem."""
    return int(round(max(0.0, 12.0 * (1.0 - y / 46.0))))


def hull():
    d = {}
    solid = set()
    for y in range(L):
        z0, zt = keel_z(y), DECK_Z(y)
        for z in range(z0, zt + 1):
            if y < stem_min_y(z):
                continue
            hb = half_beam(y, z)
            if y == 0:
                hb = max(hb, 0.6)
            for x in range(B):
                if abs(x + 0.5 - CX) <= hb:
                    solid.add((x, y, z))
    for (x, y, z) in solid:
        # keep a 2-voxel shell (the loader culls the enclosed rest)
        inner = all(((x + dx, y + dy, z + dz) in solid)
                    for dx in (-2, 0, 2) for dy in (-2, 0, 2) for dz in (-2, 0, 2))
        if inner:
            continue
        zt = DECK_Z(y)
        if z == zt:
            c = plank(x, y)
        elif z < WATERLINE_Z:
            c = "bottom"
        elif z <= WATERLINE_Z + 2:
            c = "boot"
        elif z >= zt - 1:
            c = "hull_light"
        elif (z - WATERLINE_Z) % 4 == 1:
            # horizontal strake line (round 2): the flare is shaded by ROW,
            # so the eye reads strakes, not the per-column zebra the bow
            # staircase otherwise prints on the flare
            c = "house_dark"
        else:
            c = "hull"
        put(d, x, y, z, c)
    # deck-edge trim: the outermost deck cells + a low bulwark lip
    for y in range(L):
        zt = DECK_Z(y)
        xs = [x for x in range(B) if (x, y, zt) in solid]
        if not xs:
            continue
        for x in (xs[0], xs[-1]):
            put(d, x, y, zt, "deck_trim")   # single trim line (no bulwark lip: sheer stays smooth)
    for x in range(B):
        if (x, L - 1, DECK_Z(L - 1)) in solid:
            put(d, x, L - 1, DECK_Z(L - 1), "deck_trim")
    # hawse pipes (dark) both bows
    for x in (int(CX - half_beam(12, 20)) , int(CX + half_beam(12, 20))):
        put(d, x, 12, 20, "dark"); put(d, x, 13, 20, "dark")
    # portholes along the hull under the deckhouse
    for y in range(44, 104, 9):
        for side in (0, 1):
            hb = half_beam(y, 18)
            x = int(math.floor(CX - hb + 0.5)) if side == 0 else int(math.floor(CX + hb - 0.5))
            put(d, x, y, 18, "glass")
    return d, solid


def rails(d, solid):
    """Stanchions + a continuous top rail along both deck edges, bow to stern.
    The rail steps in x (bow taper) and z (sheer) stay 6-connected."""
    prev = None
    for y in range(4, L - 1):
        zt = DECK_Z(y)
        xs = [x for x in range(B) if (x, y, zt) in solid]
        if len(xs) < 6:
            continue
        cur = (xs[0], xs[-1], zt + 3)
        for side, x in enumerate(cur[:2]):
            if y % 6 == 0:
                put(d, x, y, zt + 2, "steel")
            put(d, x, y, zt + 3, "steel")
            if prev is not None:
                px, pz = prev[side], prev[2]
                for xx in range(min(px, x), max(px, x) + 1):
                    put(d, xx, y, pz, "steel")
                for zz in range(min(pz, zt + 3), max(pz, zt + 3) + 1):
                    put(d, x, y, zz, "steel")
        if prev is None:
            for x in cur[:2]:
                put(d, x, y, zt + 2, "steel")
        prev = cur


# --- superstructure -------------------------------------------------------------

def life_ring(d, x, y, z):
    """Round orange life ring on a vertical side face at cell x (3x3 torus)."""
    for dy in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dy == 0 and dz == 0:
                continue
            put(d, x, y + dy, z + dz, "ring")


def deckhouse(d):
    # long low deckhouse between the launch boxes (step 1)
    box(d, 16, 27, 38, 104, 25, 33, "house")
    box(d, 16, 27, 38, 104, 34, 34, "house_dark")   # roof edge line
    # bridge block (step 2): full deckhouse width + one row taller than
    # round 1 (roof z47) so it reads as the dominant forward block, while
    # still sitting low against the boxes' z44.5 tops
    box(d, 16, 27, 36, 62, 34, 47, "house")
    box(d, 15, 28, 35, 63, 47, 47, "house_dark")     # bridge roof, overhanging
    box(d, 13, 30, 50, 56, 45, 45, "house_dark")     # bridge wings
    for x in (13, 30):
        for z in (46, 47):
            for y in range(50, 57):
                put(d, x, y, z, "steel")             # wing screens
    box(d, 17, 26, 63, 70, 35, 40, "house")          # step aft of the bridge (mast house)
    # bridge windows: separate square panes across the flat front + sides
    for x in (18, 20, 22, 24, 25):
        box(d, x, x, 36, 36, 42, 43, "glass")
    for y in (42, 47, 52, 57):
        box(d, 16, 16, y, y, 42, 43, "glass"); box(d, 27, 27, y, y, 42, 43, "glass")
    box(d, 16, 27, 36, 36, 38, 38, "house_dark")     # ledge under the windows
    # chart house (step 3) on the bridge roof + orange director on top
    box(d, 19, 24, 48, 58, 48, 50, "house")
    for x in (20, 22):
        put(d, x, 48, 49, "glass")
    box(d, 20, 23, 52, 55, 51, 52, "ring")           # orange director housing
    box(d, 21, 22, 53, 54, 53, 53, "dark")           # director optics
    # lower bridge-front portholes and a door each side
    for x in (19, 24):
        put(d, x, 36, 35, "glass"); put(d, x, 36, 36, "glass")
    for x in (16, 27):
        box(d, x, x, 52, 54, 40, 42, "house_dark")
    # deckhouse side doors and windows
    for y in (72, 88, 98):
        for x in (16, 27):
            box(d, x, x, y, y + 2, 26, 32, "house_dark")
    for y in range(68, 104, 7):
        for x in (16, 27):
            put(d, x, y, 31, "glass")
    # round life rings on the bridge + deckhouse sides (concept: orange)
    for x in (16, 27):
        life_ring(d, x, 59, 40)
    for x in (16, 27):
        life_ring(d, x, 82, 30)
    # vents / lockers on the deckhouse roof behind the mast
    box(d, 18, 20, 74, 80, 35, 37, "house_dark")
    box(d, 23, 25, 74, 80, 35, 37, "house_dark")
    box(d, 18, 25, 88, 100, 35, 36, "house")


def mast(d):
    # solid tapered pylon mast on the mast house aft of the bridge
    # (concept: a pylon with platforms, not v1's open lattice)
    for z in range(35, 81):
        t = (z - 35) / 45.0
        hx = 2 if t < 0.45 else 1          # x half-extent taper
        hy0, hy1 = (63, 68) if t < 0.45 else (64, 67)
        box(d, 22 - hx, 21 + hx, hy0, hy1, z, z, "house" if z % 9 else "house_dark")
    box(d, 19, 24, 63, 69, 35, 35, "box_band")          # mast foot on the roof
    # platforms + cross-trees with side equipment boxes
    box(d, 18, 25, 63, 69, 52, 52, "house_dark")     # lower platform
    box(d, 15, 28, 66, 66, 62, 62, "box_band")          # lower yard
    box(d, 17, 19, 64, 68, 63, 65, "house")          # yard equipment boxes
    box(d, 24, 26, 64, 68, 63, 65, "house")
    box(d, 13, 30, 66, 66, 70, 70, "box_band")          # upper yardarm
    for x in (13, 30):
        put(d, x, 66, 69, "dark")                    # yardarm lamps
    box(d, 18, 25, 63, 69, 74, 74, "box_band")          # radar platform
    box(d, 20, 23, 64, 68, 75, 80, "box_band")          # radar pedestal
    # whip antennas off the bridge roof corners + mast head
    for (x, y) in ((17, 60), (26, 60)):
        for z in range(47, 62):
            put(d, x, y, z, "box_band")
    for z in range(74, 86):
        put(d, 18, 69, z, "box_band")                # masthead whip, clear of the radar

RADAR_MOUNT = (21.5, 66.0, 81)     # top of the radar pedestal (hull cells)


def radome(d):
    cx, cy = 21.5, 122.0
    # stepped square tower between the aft launch boxes (concept), not
    # v1's round cylinder pedestal
    box(d, 16, 27, 114, 130, 25, 36, "house")        # equipment house (tier 1)
    box(d, 16, 27, 114, 130, 36, 36, "house_dark")
    box(d, 17, 26, 115, 129, 37, 44, "house")        # tier 2
    box(d, 18, 25, 117, 127, 45, 49, "house")        # tier 3
    for x in range(16, 28):
        put(d, x, 114, 37, "steel"); put(d, x, 130, 37, "steel")
    for y in range(114, 131):
        put(d, 16, y, 37, "steel"); put(d, 27, y, 37, "steel")
    box(d, 20, 23, 114, 114, 26, 32, "house_dark")   # door, forward face
    box(d, 17, 18, 120, 124, 38, 39, "ring")         # orange base details
    box(d, 25, 26, 120, 124, 38, 39, "ring")
    disk_z(d, cx, cy, 8.6, 50, "steel")              # platform
    # bigger faceted dome: r9 (v1 r7.2), centre z58
    for z in range(51, 68):
        r = math.sqrt(max(0.0, 9.0 ** 2 - (z - 59.0) ** 2)) if z > 59 else 9.0
        disk_z(d, cx, cy, r, z, "radome")
    disk_z(d, cx, cy, 9.0, 54, "flag_white")         # seam band


def aft_house(d):
    # low fixed deckhouse aft (owner: no gun aft), quarterdeck left open
    box(d, 17, 26, 150, 164, 25, 30, "house")
    box(d, 17, 26, 150, 164, 30, 30, "house_dark")
    box(d, 19, 24, 152, 162, 31, 32, "house")        # roof step
    box(d, 20, 23, 164, 164, 26, 29, "house_dark")   # aft door
    box(d, 20, 23, 155, 160, 33, 34, "house_dark")   # plinth
    for z in range(35, 40):
        disk_z(d, 21.5, 157.5, 3.6, z, "steel")       # director drum
    for z in range(33, 46):
        put(d, 23, 158, z, "steel")                  # whip antenna (on the plinth)
    for x in range(19, 25):
        put(d, x, 150, 28, "glass")                  # window slit, forward face
    for x in (17, 26):
        box(d, x, x, 154, 156, 26, 29, "house_dark")
    life_ring(d, 17, 158, 28); life_ring(d, 26, 158, 28)
    # open quarterdeck clutter: orange + grey lockers (concept 45° rear)
    box(d, 6, 10, 168, 172, 25, 27, "ring")
    box(d, 33, 37, 168, 172, 25, 27, "house_dark")
    box(d, 18, 25, 170, 174, 25, 26, "house_dark")
    # stern fittings: bollards, ensign staff + big ensign
    for x in (8, 35):
        box(d, x, x + 1, 172, 173, 25, 26, "steel")
    for z in range(25, 43):
        put(d, 22, 177, z, "steel")
    # ensign flies aft from the staff (+y): white field, red band + cross
    for z in range(34, 43):
        for k in range(1, 3):
            c = "flag_white"
            if z in (34, 35):
                c = "flag_red"                       # red foot band
            if z == 38 or (k == 1 and z in (37, 39)):
                c = "flag_red"                       # cross / star block
            put(d, 22, 177 + k, z, c)

def gun_ring(d):
    # the AK-630's low barbette on the foredeck
    for z in range(DECK_Z(26) + 1, TURRET_DECK_Z):
        disk_z(d, TURRET_MOUNT[0], TURRET_MOUNT[1], 7.4, z, "house_dark")
    # bow fittings: bollards, a small locker, jack staff
    for x in (13, 29):
        box(d, x, x + 1, 14, 15, DECK_Z(14) + 1, DECK_Z(14) + 2, "steel")
    box(d, 19, 24, 8, 10, DECK_Z(8) + 1, DECK_Z(8) + 2, "house_dark")
    for z in range(DECK_Z(3) + 1, DECK_Z(3) + 9):
        put(d, 21, 3, z, "steel")
    # orange foredeck lockers flanking the turret (concept 45° front)
    box(d, 8, 11, 32, 36, DECK_Z(34) + 1, DECK_Z(34) + 3, "ring")
    box(d, 32, 35, 32, 36, DECK_Z(34) + 1, DECK_Z(34) + 3, "ring")
    # anchor winch and chain runs to both hawses
    box(d, 17, 26, 13, 18, DECK_Z(14) + 1, DECK_Z(14) + 4, "house")
    box(d, 17, 26, 15, 16, DECK_Z(14) + 2, DECK_Z(14) + 3, "house_dark")
    box(d, 20, 23, 12, 13, DECK_Z(12) + 1, DECK_Z(12) + 1, "dark")
    for y in range(12, 15):
        for x in (15, 16, 27, 28):
            put(d, x, y, DECK_Z(y) + 1, "dark")
    # centreline clutter: mushroom vents, hatches, life rings, a davit
    for (x, y) in ((19, 108), (24, 108), (21, 111)):
        for z in range(25, 28):
            put(d, x, y, z, "steel")
        box(d, x - 1, x + 1, y - 1, y + 1, 28, 28, "house_dark")
    box(d, 18, 25, 136, 142, 25, 26, "house_dark")   # hatch
    box(d, 19, 24, 168, 171, 25, 25, "house_dark")   # hatch
    for (x, y) in ((17, 146), (26, 146)):
        box(d, x, x, y, y + 1, 25, 26, "ring")
    for z in range(25, 33):
        put(d, 27, 133, z, "steel")                  # davit post
    box(d, 27, 27, 133, 137, 33, 33, "steel")        # davit arm


TURRET_MOUNT = (21.5, 26.0)        # hull cells (x, y): turret centre on the foredeck
TURRET_DECK_Z = 30                 # hull cell row the turret's floor sits on (top of the barbette)


# --- launch boxes ---------------------------------------------------------------

BOX_R = 6.5           # outer half-extent (cells): bore 5.4 + ~1 cell wall
BOX_LEN = 34          # 3.4 m along the axis (round 3: sized to the halved P-15)
BOX_TILT = math.radians(12.0)
MISSILE_DIR = (0.0, -math.cos(BOX_TILT), math.sin(BOX_TILT))
# (x centre, front-mouth y, front-mouth axis z) per box. Round 3: centres
# moved outboard (9.5->8.0 / 33.5->35.0) so a red deck strip shows between
# each box and the house (x16..27) and between box and deck edge.
LAUNCHERS = [
    (8.0, 48.0, 39.0),    # port forward (beside the bridge)
    (35.0, 48.0, 39.0),   # starboard forward
    (8.0, 118.0, 39.0),   # port aft
    (35.0, 118.0, 39.0),  # starboard aft
]


def launch_box(d, cx, yf, zf):
    """A chamfered-box launcher whose mouth centre is (cx, yf, zf), running
    aft (+y) and down at BOX_TILT for BOX_LEN cells. Cross-section is a
    superellipse (|u|^4+|v|^4 <= R^4): flat sides, chamfered corners.
    Round 3 sizing (halved P-15, P15_VOXEL 0.0225): missile 3.03 m long
    (nose y0 to booster nozzle y134, fine cells), folded cross-section
    10.4 x 9.7 hull cells (tailplanes x10..55, fin to z46, booster to z3,
    fine cells x0.225) -> bore half 5.4, outer R 6.5 (~1 cell wall),
    length 34 = missile + ~0.3 m. Top at z~45.5, below the bridge roof."""
    ax = (0.0, math.cos(BOX_TILT), -math.sin(BOX_TILT))   # mouth -> rear
    yr = yf + BOX_LEN * ax[1]
    zr = zf + BOX_LEN * ax[2]
    ylo, yhi = int(yf) - 2, int(yr) + 2
    zlo, zhi = int(min(zf, zr) - BOX_R) - 2, int(max(zf, zr) + BOX_R) + 2
    rin = BOX_R - 1.1
    for x in range(int(cx - BOX_R) - 1, int(cx + BOX_R) + 2):
        for y in range(ylo, yhi + 1):
            for z in range(zlo, zhi + 1):
                px, py, pz = x + 0.5 - cx, y + 0.5 - yf, z + 0.5 - zf
                t = py * ax[1] + pz * ax[2]
                if t < 0 or t > BOX_LEN:
                    continue
                # cross-section coords: u across, v along the axis-perp in yz
                u = px
                v = py * math.sin(BOX_TILT) + pz * math.cos(BOX_TILT)
                q = (abs(u) / BOX_R) ** 4 + (abs(v) / BOX_R) ** 4
                if q > 1.0:
                    continue
                qi = (abs(u) / rin) ** 4 + (abs(v) / rin) ** 4
                end = t < 1.5 or t > BOX_LEN - 1.5
                if qi <= 1.0 and not end:
                    continue                     # hollow bore for the P-15
                if t < 1.5:
                    c = "dark" if q <= 0.10 else "box_band"   # small dark bore inset, steel rim
                elif t > BOX_LEN - 1.5:
                    c = "box_band"               # rear cap
                elif int(t) % 15 == 0:
                    c = "box_band"               # segmented panel bands
                else:
                    c = "box"
                put(d, x, y, z, c)
    # two supports from the box underside to the deck
    for tt in (10.0, BOX_LEN - 10.0):
        sy = yf + tt * ax[1]
        sz_top = zf + tt * ax[2] - BOX_R + 1
        zd = DECK_Z(int(sy))
        for z in range(zd + 1, int(sz_top) + 2):
            for xx in range(int(cx - BOX_R) + 1, int(cx + BOX_R)):
                for yy in range(int(sy) - 1, int(sy) + 3):
                    if (xx, yy, z) not in d:
                        put(d, xx, yy, z, "box_band" if z > zd + 1 else "house_dark")
    return (cx, yf + 1.0 * ax[1], zf + 1.0 * ax[2])


# --- AK-630 (fine grid, 0.05 m) -------------------------------------------------
# Turret file: centre at (TX, TY), floor z=0; barrels forward (-y).
TX, TY = 15.0, 16.0
TURRET_R = 13.5
TURRET_AXIS = (TX, TY)
GUN_PIVOT = (None, 10.0, 11.5)     # x-parallel line (y, z), fine cells
GUN_X, GUN_Z = 15.0, 11.5
MUZZLE_Y = -26
SHIFT_FINE = 28                    # everything +y so the muzzle sits at y >= 0


def _sq_disk(d, cx, cy, r, z, c):
    """Chamfered-square layer (superellipse) centred (cx, cy)."""
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            q = (abs(x + 0.5 - cx) / r) ** 4 + (abs(y + 0.5 - cy) / r) ** 4
            if q <= 1.0:
                put(d, x, y, z, c)


def turret():
    d = {}
    # boxy chamfered housing with flat faces (concept), chamfered top edge
    for z in range(0, 17):
        r = TURRET_R if z < 13 else TURRET_R - (z - 12) * 1.6
        _sq_disk(d, TX, TY, r, z, "house" if z % 6 else "house_dark")
    _sq_disk(d, TX, TY, TURRET_R + 0.8, 0, "steel")      # race ring
    # gun slot: clear a channel in the front for the mantlet
    for (x, y, z) in list(d):
        if 11 <= x <= 19 and y <= TY - 4 and 6 <= z <= 16:
            del d[(x, y, z)]
    # slot cheeks (darker) so the opening reads
    for z in range(6, 15):
        for y in range(int(TY - TURRET_R), int(TY - 4)):
            for x in (10, 20):
                if (x, y, z) in d:
                    put(d, x, y, z, "house_dark")
    # sight box on the left, vents on top
    box(d, 3, 6, 10, 16, 13, 16, "house_dark")
    box(d, 13, 17, 20, 24, 17, 17, "house_dark")
    return d


def gun():
    d = {}
    # mantlet: block that fills the slot and pivots on GUN_PIVOT
    box(d, 11, 19, 3, 12, 7, 16, "steel")
    box(d, 12, 18, 2, 2, 8, 15, "house_dark")
    # gatling: cooling jacket with a flared muzzle brake
    for y in range(MUZZLE_Y, 3):
        disk_y(d, GUN_X + 0.5, GUN_Z + 0.5, 3.0, y, "steel")
    for y in range(MUZZLE_Y, MUZZLE_Y + 4):
        disk_y(d, GUN_X + 0.5, GUN_Z + 0.5, 3.8, y, "steel")
    for y in range(MUZZLE_Y + 9, 3, 7):
        disk_y(d, GUN_X + 0.5, GUN_Z + 0.5, 3.4, y, "house_dark")
    disk_y(d, GUN_X + 0.5, GUN_Z + 0.5, 2.2, MUZZLE_Y, "dark")
    put(d, int(GUN_X), MUZZLE_Y, int(GUN_Z), "steel")
    return d


def _shift_fine(dd):
    return {(x, y + SHIFT_FINE, z): c for (x, y, z), c in dd.items()}


# --- radar (spin, coarse) --------------------------------------------------------
# Radar file: spin axis at (RX, RY), base z=0. Antenna bar across x.
RX, RY = 8.0, 3.0

def radar():
    d = {}
    disk_z(d, RX, RY, 1.6, 0, "steel")
    for z in range(1, 3):
        put(d, 7, 3, z, "steel"); put(d, 8, 3, z, "steel")
    # planar array at ~70% of round 1 (round 2): 10 wide x 7 tall panel
    box(d, 3, 12, 2, 3, 3, 9, "house")               # panel
    box(d, 3, 12, 4, 4, 3, 9, "house_dark")          # back
    for x in range(4, 12, 3):
        for z in range(4, 9, 3):
            put(d, x, 2, z, "house_dark"); put(d, x + 1, 2, z, "house_dark")   # grid cells
    box(d, 7, 8, 3, 4, 1, 3, "steel")                # mount neck
    box(d, 2, 2, 2, 3, 5, 6, "house")                # side boxes on the panel ends
    box(d, 13, 13, 2, 3, 5, 6, "house")
    return d


RADAR_SPIN = (RX, RY)


# --- build ------------------------------------------------------------------------

hull_d, _solid = hull()
rails(hull_d, _solid)
deckhouse(hull_d)
mast(hull_d)
radome(hull_d)
aft_house(hull_d)
gun_ring(hull_d)
MISSILE_SEATS = [launch_box(hull_d, *lz) for lz in LAUNCHERS]

turret_d = _shift_fine(turret())
gun_d = _shift_fine(gun())
TURRET_AXIS = (TX, TY + SHIFT_FINE)
GUN_PIVOT = (None, GUN_PIVOT[1] + SHIFT_FINE, GUN_PIVOT[2])
MUZZLE = (GUN_X + 0.5, MUZZLE_Y + SHIFT_FINE, GUN_Z + 0.5)
radar_d = radar()
ak630_view = {**turret_d, **gun_d}   # fine-grid gun view (not exported)


def _place_fine(dd, mount_xy, floor_z):
    """Downsample a fine part 2:1 onto hull cells for the assembled view."""
    out = {}
    for (x, y, z), c in dd.items():
        hx = int(math.floor(mount_xy[0] + (x + 0.5 - TURRET_AXIS[0]) / 2.0))
        hy = int(math.floor(mount_xy[1] + (y + 0.5 - TURRET_AXIS[1]) / 2.0))
        hz = floor_z + z // 2
        out[(hx, hy, hz)] = c
    return out


assembled = dict(hull_d)
assembled.update(_place_fine(turret_d, TURRET_MOUNT, TURRET_DECK_Z))
assembled.update(_place_fine(gun_d, TURRET_MOUNT, TURRET_DECK_Z))
for (x, y, z), c in radar_d.items():
    assembled[(int(math.floor(RADAR_MOUNT[0] - RX + x + 0.5)), int(math.floor(RADAR_MOUNT[1] - RY + y + 0.5)), RADAR_MOUNT[2] + z)] = c

PARTS = {
    "osa-hull-v2": hull_d,
    "osa-radar-v2": radar_d,
    "osa-turret-v2": turret_d,
    "osa-gun-v2": gun_d,
    "osa-assembled-v2": assembled,
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
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "osa2_v2")
    os.makedirs(out, exist_ok=True)
    for name, dd in PARTS.items():
        write_vox(os.path.join(out, name + ".vox"), dd, PALETTE)
        if "assembled" not in name:
            print(f"  {name}: {components(dd)} component(s)")
    both = set(turret_d) & set(gun_d)
    if both:
        print(f"  OVERLAP turret / gun: {len(both)}")
    print("TURRET_MOUNT (hull x,y)", TURRET_MOUNT, "TURRET_DECK_Z", TURRET_DECK_Z)
    print("TURRET_AXIS (fine x,y)", TURRET_AXIS, "GUN_PIVOT (fine y,z)", GUN_PIVOT[1:], "MUZZLE (fine)", MUZZLE)
    print("RADAR_MOUNT (hull x,y,z)", RADAR_MOUNT, "RADAR_SPIN (radar x,y)", RADAR_SPIN)
    print("WATERLINE_Z", WATERLINE_Z, "MISSILE_DIR", tuple(round(v, 3) for v in MISSILE_DIR))
    for i, s in enumerate(MISSILE_SEATS):
        print(f"MISSILE_SEAT {i}", tuple(round(v, 2) for v in s))
