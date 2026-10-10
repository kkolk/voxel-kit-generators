#!/usr/bin/env python3
"""Strike Bay — Osa II missile boat, v1 (replaces the patrol boat).

Reference: owner concept sheet "OSA II CLASS MISSILE BOAT" (grey hull, oxide
red deck with a red deck-edge trim, light-grey deckhouse, lattice mast with a
rotating radar, beige "Drum Tilt" radome aft of the mast, four P-15 launch
boxes two per side, a gun forward and a small fixed deckhouse aft).

SCALE  OSA_VOXEL = 0.1 m (hull, radar). The AK-630 turret and gun are on a
       2x fine grid, OSA_FINE = 0.05 m, so the gatling reads round.
       Hull ~18 m (owner: 0.6x the 28.7 m carrier), not the real 38.4 m.
       The launch boxes are stretched to ~6.2 m so the game's life-size P-15
       (5.85 m) fits inside them and slides out of the front.

Frame: z-up, x = across, y = fore-aft; forward (bow) = file -y (the ZIL /
CIWS convention). Port = low x, starboard = high x (looking forward, -y).

Parts (one 6-connected component each):
  osa-hull-v1    static: hull, deck, deckhouse, mast, radome, 4 launch
                 boxes, aft deckhouse, rails, ensign       (0.1 m)
  osa-radar-v1   spin: the mast-top radar about the vertical line
                 RADAR_SPIN (x, y)                         (0.1 m)
  osa-turret-v1  traverse: AK-630 turret about TURRET_AXIS (x, y) (0.05 m)
  osa-gun-v1     elevation: gatling + mantlet about GUN_PIVOT (y, z);
                 child of the turret                        (0.05 m)
  osa-assembled-v1  coarse merge for browsing (turret/gun downsampled)

Landmarks (file voxel cells, for agents without vision):
  FRONT  bow stem tip y=0, x 21..22, at deck height z~26. Forward = -y.
  BACK   flat transom y=179 (x 3..40). Ensign staff at (22, 177).
  UP     +z. Keel z=0 amidships; the forefoot rises to z~12 at the bow.
  WATERLINE z=10 (WATERLINE_Z): hull below it is the dark bottom colour.
         Sit the model so z=10 is at the sea surface.
  DECK   z=24 at the stern rising to z=27 at the bow (DECK_Z(y)).
  Hull parts (coarse cells):
         hull shell   x 0..43   y 0..179   z 0..27
         deckhouse    x 16..27  y 38..104  z 25..34; bridge x 16..27
                      y 34..62 to z 50 (sloped front), wings z 47
         mast         x 21..22  y 63..67   z 35..80
         radome       centre (21.5, 122, 55), r 6, on a pedestal z 41..49
         aft house    x 16..27  y 150..164 z 25..34 (fixed, no gun)
         launch boxes LAUNCHERS list: port/starboard x 9.5 / 33.5, r 5.5;
                      forward pair mouth y 48 -> rear y~107; aft pair mouth
                      y 118 -> rear y~177; mouths at z 39, front higher.
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
    ("hull",       (118, 123, 128)),  # 1 hull sides
    ("hull_light", (150, 155, 160)),  # 2 upper hull band, sheer strake
    ("bottom",     ( 52,  46,  44)),  # 3 below the waterline
    ("boot",       ( 30,  30,  32)),  # 4 boot-top stripe
    ("deck",       (152,  62,  48)),  # 5 oxide red deck
    ("deck_trim",  (196,  78,  58)),  # 6 deck-edge trim, rail tops
    ("house",      (170, 175, 180)),  # 7 deckhouse, superstructure
    ("house_dark", (128, 133, 138)),  # 8 shadowed faces, panel lines
    ("glass",      ( 34,  42,  54)),  # 9 bridge windows, portholes
    ("box",        (186, 190, 192)),  # 10 launch boxes
    ("box_band",   (142, 146, 150)),  # 11 box bands, supports
    ("radome",     (226, 214, 190)),  # 12 Drum Tilt radome
    ("steel",      ( 92,  96, 102)),  # 13 mast, gun, fittings
    ("dark",       ( 38,  40,  44)),  # 14 bores, hawse, vents
    ("flag_red",   (176,  44,  40)),  # 15 ensign
    ("flag_white", (232, 230, 224)),  # 16 ensign field, life rings
    ("ring",       (214, 110,  52)),  # 17 life rings (orange)
    ("deck_dark",  (124,  48,  38)),  # 18 plank seams, darker planks
    ("deck_light", (176,  80,  62)),  # 19 lighter planks
]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

L = 180               # hull length (y 0..179)
B = 44                # beam (x 0..43)
CX = 21.5             # centreline x (continuous)
WATERLINE_Z = 10


def DECK_Z(y):
    """Deck top row at station y: 24 at the stern, sheer up to 27 at the bow."""
    t = max(0.0, 1.0 - y / 90.0)
    return 24 + int(round(3 * t * t))


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
    # plan: sharp ogive bow over the first 64 rows, slight taper to the transom
    if y < 64:
        t = y / 64.0
        plan = 1.0 - (1.0 - t) ** 2.2
    elif y > 160:
        plan = 1.0 - 0.06 * (y - 160) / 19.0
    else:
        plan = 1.0
    # section: V below the waterline, slight flare above it
    if z < WATERLINE_Z:
        sec = 0.45 + 0.55 * (z / WATERLINE_Z)
    else:
        sec = 1.0 - 0.04 * (DECK_Z(y) - z) / max(1, DECK_Z(y) - WATERLINE_Z)
    return (B / 2.0) * plan * sec


def plank(x, y):
    """Deck planking: 0.2 m strips fore-aft, butt joints every 2.4 m staggered
    per strip, and a small per-plank colour shift (deterministic hash)."""
    strip = x // 2
    yy = y + 7 * strip
    if yy % 24 == 0:
        return "deck_dark"                           # butt joint
    h = (strip * 73856093 ^ (yy // 24) * 19349663) % 12
    if h in (0, 1):
        return "deck_light"
    if h == 2:
        return "deck_dark"
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
        elif z <= WATERLINE_Z + 1:
            c = "boot"
        elif z >= zt - 3:
            c = "hull_light"
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
            put(d, x, y, zt, "deck_trim")
            put(d, x, y, zt + 1, "deck_trim")
    for x in range(B):
        if (x, L - 1, DECK_Z(L - 1)) in solid:
            put(d, x, L - 1, DECK_Z(L - 1) + 1, "deck_trim")
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

def deckhouse(d):
    # long low deckhouse between the launch boxes
    box(d, 16, 27, 38, 104, 25, 34, "house")
    box(d, 16, 27, 38, 104, 34, 34, "house_dark")   # roof edge line
    # bridge block: wider and taller, forward face sloped back 1 per 2 rows
    for z in range(25, 51):
        y0 = 34 + max(0, z - 38) // 2
        box(d, 16, 27, y0, 62, z, z, "house")
    box(d, 15, 28, 37, 63, 50, 50, "house_dark")     # bridge roof, overhanging
    box(d, 16, 27, 36, 36, 43, 43, "house_dark")     # ledge under the windows
    box(d, 12, 31, 50, 56, 47, 47, "house_dark")     # bridge wings
    for x in (12, 31):
        for z in (48, 49):
            for y in range(50, 57):
                put(d, x, y, z, "steel")             # wing screens
    box(d, 16, 27, 63, 70, 35, 40, "house")          # step aft of the bridge (mast house)
    # bridge windows across the sloped front and down the sides
    for z in (44, 45):
        y0 = 34 + (z - 38) // 2
        for x in range(17, 27):
            put(d, x, y0, z, "glass" if x % 4 else "house_dark")
        for y in range(y0 + 1, 61):
            c = "glass" if (y - y0) % 4 else "house_dark"
            put(d, 16, y, z, c); put(d, 27, y, z, c)
    box(d, 18, 25, 50, 59, 51, 53, "house")          # chart house on the roof
    for x in range(19, 25, 2):
        put(d, x, 50, 52, "glass")
    # lower bridge-front portholes and a door each side
    for x in (18, 25):
        put(d, x, 34, 34, "glass"); put(d, x, 34, 35, "glass")
    for x in (16, 27):
        box(d, x, x, 52, 54, 44, 46, "house_dark")
    # deckhouse side doors and windows
    for y in (72, 88, 98):
        for x in (16, 27):
            box(d, x, x, y, y + 2, 26, 32, "house_dark")
    for y in range(68, 104, 7):
        for x in (16, 27):
            put(d, x, y, 31, "glass")
    # bridge roof: open-bridge screen + small director
    for x in range(16, 28):
        put(d, x, 41, 51, "house_dark")
    for y in range(41, 62):
        put(d, 16, y, 51, "house_dark"); put(d, 27, y, 51, "house_dark")
    disk_z(d, 21.5, 55.5, 2.6, 51, "steel")
    disk_z(d, 21.5, 55.5, 2.6, 52, "steel")
    box(d, 20, 23, 53, 54, 53, 54, "house_dark")
    # life rings on the bridge sides
    for x in (16, 27):
        box(d, x, x, 58, 59, 40, 41, "ring")
    # vents / lockers on the deckhouse roof behind the mast
    box(d, 18, 20, 74, 80, 35, 37, "house_dark")
    box(d, 23, 25, 74, 80, 35, 37, "house_dark")
    box(d, 18, 25, 88, 100, 35, 36, "house")


def mast(d):
    # lattice mast on the deckhouse roof just aft of the bridge
    for z in range(35, 81):
        put(d, 21, 65, z, "box_band"); put(d, 22, 65, z, "box_band")
        put(d, 21, 67, z, "box_band"); put(d, 22, 67, z, "box_band")
        if z % 4 == 0:
            put(d, 21, 66, z, "box_band"); put(d, 22, 66, z, "box_band")
    box(d, 19, 24, 63, 69, 35, 35, "box_band")          # mast foot on the roof
    for z in range(36, 51):                          # braces down to the bridge roof
        put(d, 21, 63, z, "box_band"); put(d, 22, 63, z, "box_band")
    for z in range(41, 61):                          # tripod legs from the mast house
        put(d, 19, 69, z, "box_band"); put(d, 24, 69, z, "box_band")
        put(d, 19, 70, z, "box_band"); put(d, 24, 70, z, "box_band")
    box(d, 19, 24, 66, 69, 60, 60, "box_band")          # legs tie into the mast
    box(d, 15, 28, 66, 66, 62, 62, "box_band")          # lower yard
    box(d, 18, 25, 63, 69, 52, 52, "house_dark")     # lower platform
    for x in range(18, 26):
        put(d, x, 63, 53, "box_band"); put(d, x, 69, 53, "box_band")
    box(d, 13, 30, 66, 66, 70, 70, "box_band")          # yardarm
    for x in (13, 30):
        put(d, x, 66, 69, "dark")                    # yardarm lamps
    box(d, 18, 25, 63, 69, 74, 74, "box_band")          # radar platform
    box(d, 20, 23, 64, 68, 75, 80, "box_band")          # radar pedestal
    # whip antennas off the bridge roof corners
    for (x, y) in ((16, 60), (27, 60)):
        for z in range(51, 64):
            put(d, x, y, z, "box_band")


RADAR_MOUNT = (21.5, 66.0, 81)     # top of the radar pedestal (hull cells)


def radome(d):
    cx, cy = 21.5, 122.0
    # pedestal from the deck up between the aft launch boxes
    for z in range(25, 50):
        disk_z(d, cx, cy, 3.6 if z < 41 else 5.0, z, "house" if z < 41 else "house_dark")
    box(d, 16, 27, 114, 130, 25, 36, "house")        # equipment house under it
    box(d, 16, 27, 114, 130, 36, 36, "house_dark")
    for x in range(16, 28):
        put(d, x, 114, 37, "steel"); put(d, x, 130, 37, "steel")
    for y in range(114, 131):
        put(d, 16, y, 37, "steel"); put(d, 27, y, 37, "steel")
    box(d, 20, 23, 114, 114, 26, 32, "house_dark")   # door, forward face
    disk_z(d, cx, cy, 8.0, 50, "steel")              # platform
    for z in range(51, 66):
        r = math.sqrt(max(0.0, 7.2 ** 2 - (z - 58.0) ** 2)) if z > 58 else 7.2
        disk_z(d, cx, cy, r, z, "radome")
    disk_z(d, cx, cy, 7.2, 53, "flag_white")         # seam band


def aft_house(d):
    # fixed deckhouse where the sheet's aft gun was (owner: no gun aft)
    box(d, 16, 27, 150, 164, 25, 34, "house")
    box(d, 16, 27, 150, 164, 34, 34, "house_dark")
    box(d, 18, 25, 152, 162, 35, 35, "house")        # roof step
    for x in range(16, 28):
        put(d, x, 164, 35, "steel")                  # roof rail
    box(d, 20, 23, 164, 164, 26, 31, "house_dark")   # aft door
    for z in range(35, 50):
        put(d, 26, 162, z, "steel")                  # whip antenna
    box(d, 19, 24, 155, 160, 36, 37, "house_dark")   # plinth
    for z in range(38, 44):
        disk_z(d, 21.5, 157.5, 4.2, z, "steel")       # director drum
    disk_z(d, 21.5, 157.5, 2.6, 44, "house_dark")
    box(d, 20, 23, 153, 153, 40, 41, "dark")         # director lens
    for x in range(18, 26):
        put(d, x, 150, 31, "glass")                  # window slit, forward face
    for x in (16, 27):
        box(d, x, x, 154, 156, 26, 31, "house_dark")
    # stern fittings: bollards, ensign staff + flag
    for x in (8, 35):
        box(d, x, x + 1, 172, 173, 25, 26, "steel")
    for z in range(25, 41):
        put(d, 22, 177, z, "steel")
    # flag flies aft from the staff (+y), red field with a white band
    for z in range(35, 41):
        for k in range(1, 3):
            put(d, 22, 177 + k, z, "flag_white" if z in (36, 37) else "flag_red")


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

BOX_R = 5.5           # outer radius (cells): 1.1 m dia
BOX_LEN = 60          # 6.0 m (the 5.85 m P-15 fits)
BOX_TILT = math.radians(12.0)
MISSILE_DIR = (0.0, -math.cos(BOX_TILT), math.sin(BOX_TILT))
# (x centre, front-mouth y, front-mouth axis z) per box
LAUNCHERS = [
    (9.5, 48.0, 39.0),    # port forward (beside the bridge)
    (33.5, 48.0, 39.0),   # starboard forward
    (9.5, 118.0, 39.0),   # port aft (~1.1 m gap behind the forward box)
    (33.5, 118.0, 39.0),  # starboard aft
]


def launch_box(d, cx, yf, zf):
    """A cylinder whose mouth centre is (cx, yf, zf), running aft (+y) and
    down at BOX_TILT for BOX_LEN cells."""
    ax = (0.0, math.cos(BOX_TILT), -math.sin(BOX_TILT))   # mouth -> rear
    yr = yf + BOX_LEN * ax[1]
    zr = zf + BOX_LEN * ax[2]
    ylo, yhi = int(yf) - 2, int(yr) + 2
    zlo, zhi = int(min(zf, zr) - BOX_R) - 2, int(max(zf, zr) + BOX_R) + 2
    for x in range(int(cx - BOX_R) - 1, int(cx + BOX_R) + 2):
        for y in range(ylo, yhi + 1):
            for z in range(zlo, zhi + 1):
                px, py, pz = x + 0.5 - cx, y + 0.5 - yf, z + 0.5 - zf
                t = py * ax[1] + pz * ax[2]
                if t < 0 or t > BOX_LEN:
                    continue
                rx = px
                rz = (pz - t * ax[2]) * math.cos(BOX_TILT) + 0.0
                ry = py - t * ax[1]
                r = math.sqrt(rx * rx + ry * ry + (pz - t * ax[2]) ** 2)
                if r > BOX_R:
                    continue
                end = t < 1.5 or t > BOX_LEN - 1.5
                if r < BOX_R - 1.6 and not end:
                    continue
                if t < 1.5:
                    c = "box_band" if r > BOX_R - 2.3 else "steel"
                elif t > BOX_LEN - 1.5:
                    c = "box_band"
                elif int(t) % 15 in (0, 1) or r > BOX_R - 0.35 and int(t) % 15 == 2:
                    c = "box_band"
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


def turret():
    d = {}
    # low cylinder with a chamfered top edge and a sloped front slot
    for z in range(0, 17):
        r = TURRET_R if z < 13 else TURRET_R - (z - 12) * 1.6
        disk_z(d, TX, TY, r, z, "house" if z % 6 else "house_dark")
    disk_z(d, TX, TY, TURRET_R + 0.8, 0, "steel")      # race ring
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
    box(d, 0, 15, 2, 3, 3, 5, "house")               # reflector bar
    box(d, 0, 15, 4, 4, 3, 5, "house_dark")          # back
    for x in range(0, 16, 3):
        put(d, x, 2, 4, "house_dark")                # feed slots
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
    "osa-hull-v1": hull_d,
    "osa-radar-v1": radar_d,
    "osa-turret-v1": turret_d,
    "osa-gun-v1": gun_d,
    "osa-assembled-v1": assembled,
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
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "osa2_v1")
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
