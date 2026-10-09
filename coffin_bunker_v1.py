#!/usr/bin/env python3
"""Strike Bay — P-15 coffin-bunker kit, v1 (#420, epic #417).

A modular hardened missile battery dug into a jungle hillside: a straight
row of identical BAYS (one launch tube, one pair of hexagonal blast doors,
one missile per volley) closed off by two END CAPS that taper the earth
mound to the ground, plus a lattice radar mast on a concrete pad.

Concepts: p15-coffin-bunker-voxel-concept (dark grey concrete, hexagonal
outward-swinging doors, sandbag revetments, jungle mound) and the CGM-13B
Mace shelters reference (hex portals, chamfered hex aprons).

SCALE  BUNKER_VOXEL = 0.15 m (the game's PROP_VOXEL: trees, bushes, rocks
       match it). Bay pitch 48 voxels = 7.2 m; door recess 5.1 m wide,
       opening 4.2 x 3.9 m.

Frame: z-up, ground z=0. The row runs along x; the doors face file -y
(the bunker's "forward", like the vehicles). Module origin = min corner.

Parts (per module, local coords):
  coffin-bay-core-v1     INVULNERABLE concrete: facade with hex portal,
                         wing walls, tube, roof, apron, launch cradle.
                         Dark (not black) inside, lit ribs.
  coffin-bay-door-l-v1   left leaf, authored CLOSED. Opens outward (toward
                         -y): rotate -90 deg about z through DOOR_HINGE_L.
  coffin-bay-door-r-v1   right leaf, mirror: +90 deg about DOOR_HINGE_R.
  coffin-bay-mound-a-v1  voxel_health earth slice over/around one bay:
  coffin-bay-mound-b-v1  sandbags, grass, bushes, rocks; a/b differ only
                         in vegetation so a row doesn't repeat.
  coffin-cap-l-v1        voxel_health earth tapering the mound to the
  coffin-cap-r-v1        ground (L at x<0, R after the last bay).
  coffin-radar-pad-v1    INVULNERABLE concrete pad + equipment box (cap R).
  coffin-radar-mast-v1   static open lattice tower on the pad.
  coffin-radar-antenna-v1  spins about z through RADAR_SPIN.

Points (module-local, continuous; printed at the bottom):
  MISSILE_SEAT / MISSILE_DIR  nose tip + axis of the seated missile
  OPENING   hex opening polygon (x, z) in the plane y = OPEN_Y: the
            trench-shot entry plane; TUBE_BOX the interior behind it.

Landmarks (module-local voxel cells, for agents without vision):
  FRONT  doors face -y: the door leaves sit at y 24..29, the facade/apron
         y 0..28; the trench-shot plane is y=28, hex (10,2) (38,2) (38,15)
         (28,25) (20,25) (10,15) in (x, z).
  BACK   tube runs back to y=86 (TUBE_BOX (8,28,2)-(40,86,31)); the mound
         ends at y~113.
  UP     +z; ground z=0; mound top z~44.
  Seat   missile nose tip (24, 29, 13.6), axis (0, -0.990, 0.139): 8 deg up,
         out through the doors.
  Parts  core     x 4..43   y 0..91   z 0..45   (invulnerable)
         door-l   x 7..23   y 24..29  z 2..29   hinge (7, 26), opens -90 about z
         door-r   x 24..40  y 24..29  z 2..29   hinge (41, 26), opens +90
         mound    x 0..47   y 7..113  z 0..44   (voxel_health)
         cap-l/r  x 0..29   y 7..114  z 0..45   (cap-l placed at x=-30;
                  cap-r right after the last bay)
         radar pad x 8..21 y 56..70 z 0..39; mast z 33..69; antenna
                  z 68..90, spins about z through (15, 64) (cap-local)
  Links  bays tile along x every 48 cells (BAY pitch).
"""
import math
import os

BUNKER_VOXEL = 0.15

PALETTE = [
    ("concrete",       (108, 110, 112)),  # 1
    ("concrete_dark",  ( 82,  84,  88)),  # 2
    ("concrete_light", (132, 133, 132)),  # 3
    ("stain",          ( 94,  92,  84)),  # 4 rain/rust streaks
    ("inner_1",        ( 66,  68,  72)),  # 5 tube interior, by depth
    ("inner_2",        ( 52,  54,  58)),  # 6
    ("inner_3",        ( 32,  34,  38)),  # 7
    ("steel",          (112, 116, 122)),  # 8
    ("steel_dark",     ( 66,  70,  76)),  # 9
    ("door",           ( 96, 116, 142)),  # 10 door steel (lighter than concrete)
    ("door_dark",      ( 68,  84, 106)),  # 11
    ("rivet",          (168, 170, 172)),  # 12
    ("dirt",           (122,  88,  56)),  # 13
    ("dirt_dark",      ( 94,  68,  44)),  # 14
    ("grass",          ( 92, 116,  54)),  # 15
    ("grass_dark",     ( 68,  92,  42)),  # 16
    ("leaf",           ( 64, 116,  48)),  # 17
    ("leaf_dark",      ( 40,  82,  34)),  # 18
    ("leaf_light",     (108, 148,  62)),  # 19
    ("sand",           (176, 150, 104)),  # 20 sandbags
    ("sand_dark",      (136, 114,  78)),  # 21 bag seams
    ("moss",           ( 84, 104,  56)),  # 22 moss on concrete
    ("lamp",           (230, 210, 130)),  # 23
    ("yellow",         (206, 170,  52)),  # 24 hazard / warhead band
    ("olive",          ( 92,  98,  62)),  # 25 missile (preview only)
    ("radome",         (172, 174, 142)),  # 26 missile nose (preview only)
    ("rock",           (112, 108,  98)),  # 27
    ("rock_dark",      ( 84,  80,  72)),  # 28
    ("rib",            (104, 106, 110)),  # 29 lit tube ribs
    ("dirt_light",     (146, 110,  72)),  # 30 path, dry earth
    ("door_light",     (164, 176, 190)),  # 31 door hatch / edge caps
    ("beacon",         (220,  52,  40)),  # 32 mast warning light
    ("roof",           (124, 126, 126)),  # 33 roof slab (cleaner, lighter)
    ("rib_light",      (128, 130, 134)),  # 34 nearest tube ribs
]
CI = {n: i + 1 for i, (n, _) in enumerate(PALETTE)}

# ---------------------------------------------------------------- module grid
BAY_W = 48                 # module pitch along x
CX = 24                    # centre line (between voxels 23 and 24)
CORE_X = (4, 44)           # concrete block incl. facade
FACADE_Y = 26              # facade face (apron in front)
REC_D = 2                  # door recess depth
OPEN_Y = FACADE_Y + REC_D  # opening plane (the trench-shot entry plane)
TUBE_Y = (36, 86)
BACK_Y = 92
ROOF_Z = (32, 40)
SILL_Z = 2                 # apron top = door sill
REC = (17, 17, 30)         # recess half-width, side top, top
OPN = (14, 15, 25)         # opening half-width, side top, top
WING_Y0 = 10               # wing walls run from here to the facade
CAP_W = 30
MOUND_TOP = 42


def put(d, x, y, z, c):
    d[(x, y, z)] = CI[c]


def box(d, x0, x1, y0, y1, z0, z1, c):
    for x in range(x0, x1):
        for y in range(y0, y1):
            for z in range(z0, z1):
                put(d, x, y, z, c)


def h3(x, y, z=0, s=0):
    """Deterministic hash in [0, 1)."""
    n = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ (s * 2654435761)
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


def hex_hw(z, spec):
    """Half-width of a hex portal at row z (None outside)."""
    hw, side_top, top = spec
    if z < SILL_Z or z >= top:
        return None
    if z < side_top:
        return hw
    return hw - (z - side_top + 1)


def in_hex(x, z, spec, grow=0.0):
    hw = hex_hw(z, spec)
    return hw is not None and abs(x + 0.5 - CX) < hw + grow


def concrete_tone(x, y, z, base="concrete"):
    """Weathering in 3-voxel blotches plus vertical rain streaks."""
    r = h3(x // 3, y // 3, z // 3, 7)
    if h3(x, y // 5, 0, 9) < 0.05 and z > 8:
        return "stain"
    if r < 0.12:
        return "concrete_dark"
    if r > 0.92:
        return "concrete_light"
    return base


RAIL_DEG = 8.0     # gentle in the tube; the flight climbs steeply


def rail_z(y):
    return max(3, int(round(10 - (y - OPEN_Y - 1) * math.tan(math.radians(RAIL_DEG)))))


def wing_top(y):
    """Stepped buttress: three tiers rising to the roof."""
    t = (y - WING_Y0) / (FACADE_Y - WING_Y0)
    return (12, 22, 32, ROOF_Z[1])[min(3, int(t * 4))]


# ================================================================ BAY CORE
def bay_core():
    d = {}
    x0, x1 = CORE_X
    # --- apron: chamfered hex pad (Mace), one front ramp row, joint grooves
    for y in range(0, FACADE_Y):
        hw = min(20, 12 + y * 0.9)
        for x in range(CX - 20, CX + 20):
            if abs(x + 0.5 - CX) > hw:
                continue
            top = SILL_Z if y >= 2 else 1
            for z in range(0, top):
                c = "concrete_light"
                if z == top - 1 and (y % 8 == 7 or abs(x + 0.5 - CX) > hw - 1):
                    c = "concrete"
                if z == top - 1 and y == FACADE_Y - 4 and abs(x + 0.5 - CX) < hw - 1:
                    c = "inner_2"                                    # drain strip
                put(d, x, y, z, c)
    for x in range(CX - REC[0], CX + REC[0]):                       # hazard stripe at the lip
        put(d, x, FACADE_Y - 1, SILL_Z - 1, "yellow" if ((x - CX) // 2) % 2 == 0 else "concrete_dark")
    # --- wing walls retaining the earth, top stepping down to the apron
    for (wa, wb) in ((x0, x0 + 3), (x1 - 3, x1)):
        for y in range(WING_Y0, FACADE_Y):
            for z in range(0, wing_top(y)):
                for x in range(wa, wb):
                    put(d, x, y, z, concrete_tone(x, y, z))
            for x in range(wa, wb):
                put(d, x, y, wing_top(y) - 1, "concrete_light")       # coping
        for x in range(wa, wb):
            for z in range(0, wing_top(WING_Y0)):
                put(d, x, WING_Y0, z, "concrete_dark")                  # end face
    # --- solid block: facade, sides, back, roof (tube carved below)
    for x in range(x0, x1):
        for y in range(FACADE_Y, BACK_Y):
            for z in range(0, ROOF_Z[1]):
                if y < OPEN_Y and in_hex(x, z, REC):
                    continue                                             # door recess
                if OPEN_Y <= y < TUBE_Y[0] and in_hex(x, z, OPN):
                    continue                                             # throat
                if TUBE_Y[0] <= y < TUBE_Y[1] and x0 + 4 <= x < x1 - 4 and SILL_Z <= z < ROOF_Z[0] - 1:
                    # vault: chamfered top corners echo the hex
                    if (z - (ROOF_Z[0] - 8)) < (min(x - x0 - 4, x1 - 5 - x) + 1) or z < ROOF_Z[0] - 8:
                        continue
                put(d, x, y, z, concrete_tone(x, y, z))
    # --- recess walls + throat + tube skin: dark, by depth, with lit ribs
    def tone(y):
        if y < OPEN_Y + 6:
            return "inner_1"
        if y < TUBE_Y[0] + 14:
            return "inner_2"
        return "inner_3"
    for (x, y, z) in list(d):
        if y < FACADE_Y:
            continue
        exposed = False
        for nb in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
            if nb not in d and nb[1] >= OPEN_Y and FACADE_Y <= nb[1] < TUBE_Y[1] and 0 <= nb[2] < ROOF_Z[0] and x0 < nb[0] < x1 - 1:
                exposed = True
        if exposed:
            c = tone(y)
            if y >= TUBE_Y[0] and (y - TUBE_Y[0]) % 10 == 4:
                c = "rib_light" if y < TUBE_Y[0] + 20 else "rib"
            if y in (OPEN_Y + 2, OPEN_Y + 3, OPEN_Y + 9):
                c = "rib_light"
            put(d, x, y, z, c)
    # floor of the throat/tube
    for y in range(OPEN_Y, TUBE_Y[1]):
        for x in range(x0 + 4, x1 - 4):
            for z in range(0, SILL_Z):
                put(d, x, y, z, tone(y))
    # recess cut faces: concrete_dark so the hex portal reads
    for (x, y, z) in list(d):
        if FACADE_Y <= y < OPEN_Y and (in_hex(x, z, REC, grow=1.0) or in_hex(x, z - 1, REC)) and not in_hex(x, z, REC):
            put(d, x, y, z, "concrete_dark")
    # --- proud chamfered frame around the recess (2 wide)
    for z in range(0, REC[2] + 2):
        for x in range(x0, x1):
            if (in_hex(x, z, REC, grow=2.0) or in_hex(x, z - 2, REC) or in_hex(x, z - 1, REC, grow=1.0)) and not in_hex(x, z, REC):
                put(d, x, FACADE_Y - 1, z, "concrete_light")
    # --- stepped cornice over the facade
    box(d, x0, x1, FACADE_Y - 2, FACADE_Y, ROOF_Z[1] - 3, ROOF_Z[1], "concrete")
    box(d, x0, x1, FACADE_Y - 3, FACADE_Y - 2, ROOF_Z[1] - 2, ROOF_Z[1], "concrete")
    for x in range(x0, x1):
        put(d, x, FACADE_Y - 3, ROOF_Z[1] - 2, "concrete_dark")          # drip shadow
        put(d, x, FACADE_Y - 2, ROOF_Z[1] - 3, "concrete_dark")
        put(d, x, FACADE_Y - 3, ROOF_Z[1] - 1, "concrete_light")
    # bay plate on the cornice: light panel, blocky numeral-like strokes
    box(d, CX - 4, CX + 4, FACADE_Y - 4, FACADE_Y - 3, ROOF_Z[1] - 3, ROOF_Z[1], "concrete_light")
    for (x, z) in ((CX - 2, ROOF_Z[1] - 2), (CX - 1, ROOF_Z[1] - 2), (CX - 1, ROOF_Z[1] - 3), (CX + 1, ROOF_Z[1] - 1), (CX + 1, ROOF_Z[1] - 2), (CX + 1, ROOF_Z[1] - 3), (CX + 2, ROOF_Z[1] - 2)):
        put(d, x, FACADE_Y - 4, z, "concrete_dark")
    # form-tie dots on the facade face (paint, no relief)
    for x in range(x0, x1):
        for z in range(0, ROOF_Z[1] - 3):
            p = (x, FACADE_Y, z)
            if p in d and not in_hex(x, z, REC, grow=2.5) and d[p] != CI["concrete_light"]:
                if x % 6 == 1 and z % 6 == 4:
                    put(d, x, FACADE_Y, z, "concrete_dark")
    # lamps over the portal on steel brackets, conduit down the left pier
    for xa in (CX - 9, CX + 8):
        put(d, xa, FACADE_Y - 1, REC[2] + 2, "steel_dark")
        put(d, xa, FACADE_Y - 2, REC[2] + 2, "steel_dark")
        put(d, xa, FACADE_Y - 2, REC[2] + 1, "lamp")
    for z in range(4, ROOF_Z[1] - 3):
        put(d, x0 + 1, FACADE_Y - 1, z, "steel_dark")
    box(d, x0, x0 + 3, FACADE_Y - 2, FACADE_Y, 9, 13, "steel_dark")      # junction box
    put(d, x0 + 1, FACADE_Y - 2, 11, "steel")
    # door hinge brackets on the frame, two per side
    for xa in (CX - REC[0] - 2, CX + REC[0]):
        for zb in (5, 14):
            box(d, xa, xa + 2, FACADE_Y - 2, FACADE_Y - 1, zb, zb + 3, "steel_dark")
            put(d, xa, FACADE_Y - 2, zb + 1, "rivet"); put(d, xa + 1, FACADE_Y - 2, zb + 1, "rivet")
    # --- roof: edge lip, louvred vent block, two hatches, conduit, moss
    for x in range(x0, x1):
        for y in range(FACADE_Y - 3, BACK_Y):
            if x in (x0, x1 - 1) or y == BACK_Y - 1:
                put(d, x, y, ROOF_Z[1], "concrete_dark")
    for x in range(x0, x1):
        put(d, x, FACADE_Y - 3, ROOF_Z[1], "concrete_dark")                     # front lip
    for x in range(CX - 10, CX + 10):
        for y in range(FACADE_Y + 14, FACADE_Y + 30):
            if (x, y, ROOF_Z[1] - 1) in d:
                edge = x in (CX - 10, CX + 9) or y in (FACADE_Y + 14, FACADE_Y + 29)
                if edge:
                    d[(x, y, ROOF_Z[1] - 1)] = CI["concrete_dark"]
                else:
                    del d[(x, y, ROOF_Z[1] - 1)]
                    put(d, x, y, ROOF_Z[1] - 2, "concrete")                     # recessed panel
    for sx in (x0 + 4, x1 - 7):
        box(d, sx, sx + 3, FACADE_Y + 2, FACADE_Y + 5, ROOF_Z[1], ROOF_Z[1] + 5, "steel_dark")   # vent stacks
        box(d, sx - 1, sx + 4, FACADE_Y + 1, FACADE_Y + 6, ROOF_Z[1] + 5, ROOF_Z[1] + 6, "steel")
        put(d, sx + 1, FACADE_Y + 3, ROOF_Z[1] + 5, "inner_3")
    box(d, CX - 7, CX + 7, 58, 70, ROOF_Z[1], ROOF_Z[1] + 4, "concrete")
    box(d, CX - 7, CX + 7, 58, 70, ROOF_Z[1] + 4, ROOF_Z[1] + 5, "rivet")
    for x in range(CX - 6, CX + 6, 2):
        box(d, x, x + 1, 57, 58, ROOF_Z[1] + 1, ROOF_Z[1] + 4, "steel_dark")
        box(d, x, x + 1, 70, 71, ROOF_Z[1] + 1, ROOF_Z[1] + 4, "steel_dark")
    for y in range(59, 70, 2):
        box(d, CX - 8, CX - 7, y, y + 1, ROOF_Z[1] + 1, ROOF_Z[1] + 4, "steel_dark")
        box(d, CX + 7, CX + 8, y, y + 1, ROOF_Z[1] + 1, ROOF_Z[1] + 4, "steel_dark")
    for (hx, hy) in ((CX - 12, 30), (CX + 8, 44)):
        box(d, hx, hx + 5, hy, hy + 5, ROOF_Z[1], ROOF_Z[1] + 1, "steel_dark")
        box(d, hx + 1, hx + 4, hy + 1, hy + 4, ROOF_Z[1], ROOF_Z[1] + 1, "steel")
        put(d, hx + 2, hy, ROOF_Z[1] + 1, "steel_dark")                    # handle
    box(d, x1 - 6, x1 - 4, 22, 58, ROOF_Z[1], ROOF_Z[1] + 1, "steel_dark")
    for x in range(x0 + 1, x1 - 1):
        for y in range(FACADE_Y - 1, BACK_Y - 1):
            top = (x, y, ROOF_Z[1] - 1)
            if top in d:
                d[top] = CI["concrete" if (y - FACADE_Y) % 12 == 11 else "roof"]     # slab + seams
            edge = min(x - x0, x1 - 1 - x) < 3 or y > BACK_Y - 6
            if edge and (x, y, ROOF_Z[1]) not in d and h3(x // 3, y // 3, 0, 3) < 0.35 and h3(x, y, 1, 3) < 0.75:
                put(d, x, y, ROOF_Z[1], "moss")
    for y in range(OPEN_Y - 4, TUBE_Y[1]):
        put(d, CX - 1, y, SILL_Z - 1, "steel"); put(d, CX, y, SILL_Z - 1, "steel")
    box(d, CX - 5, CX + 5, OPEN_Y + 8, OPEN_Y + 14, SILL_Z, SILL_Z + 3, "steel_dark")   # cradle base
    # --- launch cradle: twin steel beams on posts, rising RAIL_DEG forward
    for y in range(OPEN_Y + 1, TUBE_Y[1] - 10):
        zt = rail_z(y)
        for x in (CX - 4, CX + 3):
            for z in range(SILL_Z, zt + 1):
                if z >= zt - 1 or y % 4 == 0:
                    put(d, x, y, z, "rivet" if z == zt else "steel_dark")
        if y % 8 == 0:
            for x in range(CX - 4, CX + 4):
                put(d, x, y, zt - 1, "steel_dark")
    return d


MISSILE_DIR = (0.0, -math.cos(math.radians(RAIL_DEG)), math.sin(math.radians(RAIL_DEG)))
MISSILE_SEAT = (CX, OPEN_Y + 1.0, rail_z(OPEN_Y + 1) + 3.6)
OPENING = [(CX - OPN[0], SILL_Z), (CX + OPN[0], SILL_Z), (CX + OPN[0], OPN[1]),
           (CX + OPN[0] - (OPN[2] - OPN[1]), OPN[2]), (CX - OPN[0] + (OPN[2] - OPN[1]), OPN[2]),
           (CX - OPN[0], OPN[1])]
TUBE_BOX = ((CORE_X[0] + 4, OPEN_Y, SILL_Z), (CORE_X[1] - 4, TUBE_Y[1], ROOF_Z[0] - 1))


# ================================================================ DOORS
DOOR_T = 3
DOOR_Y0 = FACADE_Y - 1              # door face sits 1 proud of the facade
DOOR_HINGE_L = (CX - REC[0], FACADE_Y)
DOOR_HINGE_R = (CX + REC[0], FACADE_Y)


def door_l():
    """Left leaf, closed: half the recess hex. Thick rim, centre hatch,
    stiffeners, rivets, locking boss and hinge knuckles."""
    d = {}
    for z in range(SILL_Z, REC[2]):
        hw = hex_hw(z, REC)
        for x in range(CX - REC[0], CX):
            if abs(x + 0.5 - CX) >= hw:
                continue
            rim = (x <= CX - REC[0] + 1 or x == CX - 1 or z <= SILL_Z + 1 or abs(x + 0.5 - CX) >= hw - 2 or z >= REC[2] - 2)
            for y in range(DOOR_Y0 + 1, DOOR_Y0 + 1 + DOOR_T):
                put(d, x, y, z, "door_dark" if y > DOOR_Y0 + 1 else "door")
            if rim:
                put(d, x, DOOR_Y0, z, "door")                            # raised rim
    for (x, y, z) in list(d):
        if y == DOOR_Y0 + 1 and ((x - 1, y, z) not in d or (x, y, z + 1) not in d and z >= REC[2] - 3):
            put(d, x, DOOR_Y0 + DOOR_T, z, "inner_3")                     # dark back edge
    # centre hatch: raised panel with a dark outline and a handle
    hx0, hx1, hz0, hz1 = CX - 12, CX - 4, 7, 17
    box(d, hx0, hx1, DOOR_Y0, DOOR_Y0 + 1, hz0, hz1, "door")
    for x in range(hx0, hx1):
        put(d, x, DOOR_Y0, hz0, "door_dark"); put(d, x, DOOR_Y0, hz1 - 1, "door_dark")
    for z in range(hz0, hz1):
        put(d, hx0, DOOR_Y0, z, "door_dark"); put(d, hx1 - 1, DOOR_Y0, z, "door_dark")
    box(d, hx1 - 3, hx1 - 2, DOOR_Y0 - 1, DOOR_Y0, 11, 13, "steel_dark")   # handle
    # horizontal stiffeners above/below the hatch
    for z in (4, 20):
        for x in range(CX - REC[0] + 2, CX - 1):
            if hex_hw(z, REC) and abs(x + 0.5 - CX) < hex_hw(z, REC) - 2:
                put(d, x, DOOR_Y0, z, "door_dark")
    for (x, z) in ((hx0 + 1, hz0 + 1), (hx1 - 2, hz0 + 1), (hx0 + 1, hz1 - 2), (hx1 - 2, hz1 - 2)):
        put(d, x, DOOR_Y0 - 1, z, "rivet")
    # hazard chevron band low on the leaf, light hatch face
    for x in range(CX - REC[0] + 2, CX - 1):
        for z in (SILL_Z + 2, SILL_Z + 3):
            put(d, x, DOOR_Y0, z, "yellow" if (x + z) % 4 < 2 else "inner_3")
    box(d, hx0 + 1, hx1 - 1, DOOR_Y0, DOOR_Y0 + 1, hz0 + 1, hz1 - 1, "door_light")
    # light edge caps on the meeting edge and top chamfer (read edge-on when open)
    for z in range(SILL_Z, REC[2]):
        for y in range(DOOR_Y0 + 1, DOOR_Y0 + 1 + DOOR_T):
            put(d, CX - 1, y, z, "door_light")
        hw = hex_hw(z, REC)
        xe = int(CX - hw)
        if z >= REC[1]:
            for y in range(DOOR_Y0, DOOR_Y0 + 1 + DOOR_T):
                put(d, xe, y, z, "rivet")
                put(d, xe + 1, y, z, "rivet")
    # back face: bright steel X brace + door ram lug (faces the opening when open)
    yb = DOOR_Y0 + DOOR_T + 1
    for i in range(0, REC[0] - 3):
        for (x, z) in ((CX - REC[0] + 2 + i, SILL_Z + 2 + int(i * 1.2)), (CX - REC[0] + 2 + i, REC[1] - 1 - int(i * 0.8))):
            if (x, yb - 1, z) in d:
                put(d, x, yb, z, "steel")
    box(d, CX - 6, CX - 3, yb, yb + 1, 11, 14, "steel_dark")
    # locking boss at the meeting edge, hinge knuckles on the outer edge
    box(d, CX - 2, CX, DOOR_Y0 - 1, DOOR_Y0, 10, 15, "steel")
    for zb in (4, 13):
        box(d, CX - REC[0], CX - REC[0] + 2, DOOR_Y0 - 1, DOOR_Y0 + 1 + DOOR_T, zb, zb + 4, "rivet")
    return d


def door_r():
    return {(2 * CX - 1 - x, y, z): c for (x, y, z), c in door_l().items()}


def swing(door, hinge, ang):
    """Preview: rotate a leaf about its z hinge by ang degrees."""
    hx, hy = hinge
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    out = {}
    for (x, y, z), c in door.items():
        for ox in (0.25, 0.75):
            for oy in (0.25, 0.75):
                dx, dy = x + ox - hx, y + oy - hy
                out[(int(math.floor(hx + dx * ca - dy * sa)), int(math.floor(hy + dx * sa + dy * ca)), z)] = c
    return out


# ================================================================ MOUND
def flank_height(y):
    if y < WING_Y0:
        return 0
    if y < FACADE_Y:
        return min(wing_top(y) - 1, 10 + (y - WING_Y0) * 2.0)
    if y < BACK_Y:
        return min(MOUND_TOP, ROOF_Z[1] + 1 + (y - FACADE_Y) * 0.1)
    return max(0.0, MOUND_TOP - (y - BACK_Y) * 2.0)


def core_height(y):
    if y < 72:
        return 0
    if y < BACK_Y:
        return ROOF_Z[1] + min(MOUND_TOP - ROOF_Z[1], 1 + (y - 72) * 0.15)
    return max(0.0, MOUND_TOP - (y - BACK_Y) * 2.0)


def mound_h(x, y):
    in_core = CORE_X[0] <= x < CORE_X[1]
    h = core_height(y) if in_core else flank_height(y)
    if h <= 0:
        return 0
    n = h3(x // 3, y // 3, 0, 11)
    return int(h + (n - 0.5) * 2.0)


def sandbags(d, x0, x1, y0, y1, z0, z1, axis="x"):
    """Stacked bags, staggered every row; bag = 4 long, 2 tall."""
    for z in range(z0, z1):
        row = (z - z0) // 2
        for x in range(x0, x1):
            for y in range(y0, y1):
                u = (x if axis == "x" else y) + (2 if row % 2 else 0)
                seam = u % 4 == 0
                put(d, x, y, z, "sand_dark" if seam else "sand")


def boulder(d, x, y, h, r, seed):
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            for dz in range(-1, r + 1):
                if dx * dx + dy * dy + (dz * 1.4) ** 2 <= r * r + 0.5:
                    put(d, x + dx, y + dy, h + dz, "rock_dark" if h3(x + dx, y + dy, dz, seed) < 0.35 else "rock")


def vegetate(d, hmap, seed, density=0.009, width=None):
    """Distinct jungle bushes + boulders on the surface."""
    for (x, y), h in sorted(hmap.items()):
        if h <= 3:
            continue
        if width is not None and not (3 <= x < width - 3):
            continue
        r = h3(x, y, 0, seed)
        if r < density:
            size = 2 + int(h3(x, y, 1, seed) * 2.5) + (2 if h3(x, y, 5, seed) < 0.25 else 0)
            tall = 1.0 + h3(x, y, 2, seed) * 0.8
            for dx in range(-size, size + 1):
                for dy in range(-size, size + 1):
                    for dz in range(0, int(size * tall) + 3):
                        q = dx * dx + dy * dy + ((dz - 1) / tall) ** 2
                        if q <= size * size + 0.5 and h3(x + dx, y + dy, dz, seed + 2) > 0.12:
                            if width is not None and not (0 <= x + dx < width):
                                continue
                            k = h3(x + dx, y + dy, dz, seed + 1)
                            shade = dz / (size * tall + 1)
                            c = "leaf_light" if (k > 0.75 and shade > 0.5) else ("leaf_dark" if k < 0.3 or shade < 0.25 else "leaf")
                            d[(x + dx, y + dy, h + dz)] = CI[c]
        elif r < density + 0.004:
            boulder(d, x, y, h, 1 + int(h3(x, y, 3, seed) * 2), seed)


def mound_fill(d, hfun, x0, x1, y1, skip=None):
    hmap = {}
    for x in range(x0, x1):
        for y in range(0, y1):
            h = hfun(x, y)
            if h <= 0:
                continue
            zb = 0
            if skip and skip(x, y):
                zb = ROOF_Z[1] + 1 if y < BACK_Y else 0
                if h <= zb:
                    continue
            steep = hfun(x, y - 1) < h - 3 or hfun(x - 1, y) < h - 3 or hfun(x + 1, y) < h - 3
            patch = h3(x // 5, y // 5, 0, 17)
            for z in range(zb, h):
                if z == h - 1:
                    if steep:
                        c = "grass_dark" if h3(x // 2, y // 2, z // 2, 4) < 0.3 else ("dirt" if h3(x // 3, y, z // 3, 6) > 0.4 else "dirt_light")
                    elif patch < 0.12:
                        c = "dirt"
                    elif patch < 0.45:
                        c = "grass_dark"
                    else:
                        c = "grass"
                elif z >= h - 4 and not steep:
                    c = "grass_dark" if z == h - 2 else "dirt_dark"
                else:
                    q = h3(x // 3, y // 3, z // 3, 19)
                    c = "dirt_light" if q < 0.2 else ("dirt" if q < 0.6 else "dirt_dark")
                    if q > 0.95:
                        c = "rock"
                put(d, x, y, z, c)
            hmap[(x, y)] = h
    return hmap


def keep_largest(d):
    from collections import deque
    vs, seen, best = set(d), set(), []
    for st in vs:
        if st in seen:
            continue
        q = deque([st]); seen.add(st); comp = [st]
        while q:
            x, y, z = q.popleft()
            for nb in ((x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)):
                if nb in vs and nb not in seen:
                    seen.add(nb); q.append(nb); comp.append(nb)
        if len(comp) > len(best):
            best = comp
    return {p: d[p] for p in best}


def in_core_footprint(x, y):
    return CORE_X[0] <= x < CORE_X[1] and WING_Y0 <= y < BACK_Y


CORE = bay_core()


def bay_mound(seed):
    d = {}
    hmap = mound_fill(d, mound_h, 0, BAY_W, 116, skip=in_core_footprint)
    # sandbag revetment across the flank toes, in front of the wing walls
    sandbags(d, 0, CORE_X[0], WING_Y0 - 3, WING_Y0 + 2, 0, 6)
    sandbags(d, CORE_X[1], BAY_W, WING_Y0 - 3, WING_Y0 + 2, 0, 6)
    vegetate(d, {k: v for k, v in hmap.items() if k[1] > FACADE_Y + 30 and not (CORE_X[0] - 1 <= k[0] <= CORE_X[1] and k[1] < BACK_Y)}, seed, width=BAY_W)
    for p in list(d):
        if p in CORE:
            del d[p]
    return keep_largest(d)


# ================================================================ END CAPS
def cap_h(x, y):
    """Right cap, local x=0 at the join with the last bay."""
    base = flank_height(y) if y >= FACADE_Y else (wing_top(y) - 1 if y >= WING_Y0 else 0)
    taper = (CAP_W - x) * 1.6 - 2
    h = min(base, taper)
    if h <= 0:
        return 0
    n = h3(x // 3, y // 3, 0, 13)
    return int(h + (n - 0.5) * 2.0)


PAD_XY = (15, 64)                    # on cap R, local
PAD_TOP = 32


def cap_r(seed=21):
    d = {}
    hmap = mound_fill(d, cap_h, 0, CAP_W, 120)
    # sandbag wall continues across the cap front, stepping down outward
    for x in range(0, CAP_W - 6):
        top = max(2, 8 - (x // 7) * 2)
        sandbags(d, x, x + 1, WING_Y0 - 3, WING_Y0 + 2, 0, top)
    # footpath from the front up to the radar pad
    for t in range(0, 60):
        x = int(CAP_W - 8 - t * 0.12)
        y = WING_Y0 + 2 + t
        if y >= PAD_XY[1] - 6:
            break
        for dx in (0, 1, 2):
            h = hmap.get((x + dx, y))
            if h:
                put(d, x + dx, y, h - 1, "dirt_light")
    vegetate(d, {k: v for k, v in hmap.items() if k[1] > FACADE_Y + 20 and (abs(k[0] - PAD_XY[0]) > 8 or abs(k[1] - PAD_XY[1]) > 8)}, seed, density=0.012, width=CAP_W)
    return keep_largest(d)


def cap_l(seed=23):
    d = {}
    hmap = mound_fill(d, cap_h, 0, CAP_W, 120)
    for x in range(0, CAP_W - 6):
        top = max(2, 8 - (x // 7) * 2)
        sandbags(d, x, x + 1, WING_Y0 - 3, WING_Y0 + 2, 0, top)
    vegetate(d, {k: v for k, v in hmap.items() if k[1] > FACADE_Y + 20}, seed, density=0.012, width=CAP_W)
    d = keep_largest(d)
    return {(CAP_W - 1 - x, y, z): c for (x, y, z), c in d.items()}


# ================================================================ RADAR
def radar_pad():
    """Concrete pad flush with the mound + equipment cabinet beside the tower."""
    d = {}
    px, py = PAD_XY
    for x in range(px - 7, px + 7):
        for y in range(py - 7, py + 7):
            for z in range(0, PAD_TOP + 1):
                put(d, x, y, z, concrete_tone(x, y, z))
            put(d, x, y, PAD_TOP, "concrete_dark" if x in (px - 7, px + 6) or y in (py - 7, py + 6) else "concrete_light")
    box(d, px - 6, px - 2, py - 7, py - 3, PAD_TOP + 1, PAD_TOP + 7, "concrete_light")  # cabinet
    box(d, px - 6, px - 2, py - 7, py - 3, PAD_TOP + 7, PAD_TOP + 8, "steel")
    put(d, px - 5, py - 7, PAD_TOP + 4, "lamp")
    box(d, px - 5, px - 3, py - 8, py - 7, PAD_TOP + 2, PAD_TOP + 6, "steel_dark")  # cabinet door
    return d


MAST_H = 34


def line6(d, a, b, c):
    """6-connected voxel line from a to b (steps one axis at a time)."""
    x, y, z = a
    put(d, x, y, z, c)
    n = max(abs(b[0] - a[0]), abs(b[1] - a[1]), abs(b[2] - a[2]), 1)
    for i in range(1, n + 1):
        t = i / n
        tx = round(a[0] + (b[0] - a[0]) * t); ty = round(a[1] + (b[1] - a[1]) * t); tz = round(a[2] + (b[2] - a[2]) * t)
        while (x, y, z) != (tx, ty, tz):
            if x != tx:
                x += 1 if tx > x else -1
            elif y != ty:
                y += 1 if ty > y else -1
            else:
                z += 1 if tz > z else -1
            put(d, x, y, z, c)


def radar_mast():
    """Open 4-leg lattice tower: thin legs, zigzag bracing, top deck, ladder."""
    d = {}
    px, py = PAD_XY
    z0 = PAD_TOP + 1
    zt = z0 + MAST_H

    def leg(sx, sy, z):
        t = (z - z0) / MAST_H
        hw = 6.5 - 4.5 * t
        return (int(round(px + sx * hw)) - (1 if sx < 0 else 0), int(round(py + sy * hw)) - (1 if sy < 0 else 0), z)
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for (sx, sy) in corners:
        line6(d, leg(sx, sy, z0), leg(sx, sy, zt), "rivet")
        a = leg(sx, sy, z0); b = leg(sx, sy, zt)
        line6(d, (a[0] - sx, a[1], a[2]), (b[0] - sx, b[1], b[2]), "rivet")     # 2-thick legs
    levels = list(range(z0, zt + 1, 9))
    if levels[-1] != zt:
        levels.append(zt)
    for i, z in enumerate(levels):
        for k in range(4):
            line6(d, leg(*corners[k], z), leg(*corners[(k + 1) % 4], z), "steel")
        if i + 1 < len(levels):
            z2 = levels[i + 1]
            for k in range(4):
                c1, c2 = corners[k], corners[(k + 1) % 4]
                if (i + k) % 2:
                    line6(d, leg(*c1, z), leg(*c2, z2), "steel")
                else:
                    line6(d, leg(*c2, z), leg(*c1, z2), "steel")
    box(d, px - 3, px + 3, py - 3, py + 3, zt, zt + 1, "steel_dark")          # deck
    for x in range(px - 3, px + 3):
        for y in range(py - 3, py + 3):
            if x in (px - 3, px + 2) or y in (py - 3, py + 2):
                put(d, x, y, zt + 2, "steel")
    for (x, y) in ((px - 3, py - 3), (px + 2, py - 3), (px - 3, py + 2), (px + 2, py + 2)):
        put(d, x, y, zt + 1, "steel")
    # ladder up the front face
    for z in range(z0, zt):
        fy = leg(-1, -1, z)[1]
        ly = fy - 1
        put(d, px - 1, ly, z, "steel"); put(d, px + 1, ly, z, "steel")
        if z % 2 == 0:
            put(d, px, ly, z, "steel")
            line6(d, (px - 1, ly, z), (px - 1, fy, z), "steel")
    return keep_largest(d)


RADAR_SPIN = PAD_XY                   # z axis through (x, y) at the mast top
ANT_W, ANT_H, ANT_TILT = 30, 16, 15.0


def radar_antenna():
    """Large open-mesh search antenna: frame, 4-voxel mesh, centre hub,
    yoke and pedestal, tilted back ANT_TILT deg."""
    d = {}
    px, py = PAD_XY
    zt = PAD_TOP + 1 + MAST_H + 1
    box(d, px - 1, px + 1, py - 1, py + 1, zt, zt + 3, "steel_dark")          # pedestal
    box(d, px - 4, px + 4, py - 1, py + 1, zt + 3, zt + 4, "steel_dark")      # yoke
    for x in (px - 4, px + 3):
        box(d, x, x + 1, py - 1, py + 1, zt + 4, zt + 7, "steel_dark")
    zc = zt + 6 + ANT_H / 2
    t = math.tan(math.radians(ANT_TILT))
    for zi in range(0, ANT_H):
        z = zt + 6 + zi
        yo = int(round((z - zc) * t))                                            # lean back
        yp = int(round((z - 1 - zc) * t))
        for xi in range(0, ANT_W):
            x = px - ANT_W // 2 + xi
            frame = xi in (0, ANT_W - 1) or zi in (0, ANT_H - 1)
            mesh = xi % 4 == 0 or zi % 4 == 0
            if frame or mesh:
                c = "door_light" if frame else "steel"
                put(d, x, py - 2 + yo, z, c)
                if zi > 0 and yp != yo:
                    put(d, x, py - 2 + yp, z, c)
    box(d, px - 2, px + 2, py - 2, py + 1, int(zc) - 2, int(zc) + 2, "steel_dark")    # hub
    for z in range(zt + 4, zt + 6 + ANT_H):
        put(d, px - 1, py - 1, z, "steel_dark"); put(d, px, py - 1, z, "steel_dark")   # spine
    box(d, px - 1, px + 1, py - 6, py - 2, int(zc) - 1, int(zc) + 1, "steel")      # feed horn arm
    for x in range(px - ANT_W // 2, px + ANT_W // 2):
        put(d, x, py - 2 + int(round((zt + 6 + ANT_H - 1 - zc) * t)), zt + 6 + ANT_H - 1, "door_light")
    put(d, px - 1, py - 1, zt + 6 + ANT_H, "beacon"); put(d, px, py - 1, zt + 6 + ANT_H, "beacon")
    return keep_largest(d)


# ================================================================ PREVIEW MISSILE
def preview_missile():
    """The real P-15 (stowed wings), downsampled 0.045 -> 0.15 m and seated
    on the cradle (preview only; the game places the 0.045 m model)."""
    import importlib.util, contextlib, io
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("p15", os.path.join(here, "p15_termit_v1.py"))
    m = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    names = {i + 1: n for i, (n, _) in enumerate(m.PALETTE)}
    remap = {"olive": "olive", "olive_dark": "olive", "olive_light": "olive", "yellow": "yellow",
             "radome": "radome", "gunmetal": "steel_dark", "dark": "inner_3", "booster": "olive",
             "booster_dark": "olive", "steel": "steel", "red": "olive"}
    k = m.MISSILE_VOXEL / BUNKER_VOXEL
    a = math.radians(RAIL_DEG)
    sx, sy, sz = MISSILE_SEAT
    votes = {}
    for (x, y, z), c in m.assembled_stowed.items():
        lx, ly, lz = (x + 0.5 - m.AX) * k, (y + 0.5) * k, (z + 0.5 - m.AZ) * k
        wy = sy + ly * math.cos(a) + lz * math.sin(a)
        wz = sz - ly * math.sin(a) + lz * math.cos(a)
        key = (int(math.floor(sx + lx)), int(math.floor(wy)), int(math.floor(wz)))
        votes.setdefault(key, {}).setdefault(names[c], 0)
        votes[key][names[c]] += 1
    out = {}
    for key, v in votes.items():
        if sum(v.values()) >= 6:
            out[key] = CI[remap[max(v, key=v.get)]]
    return out


# ================================================================ ASSEMBLE
door_l_v = door_l()
door_r_v = door_r()
mound_a_v = bay_mound(31)
mound_b_v = bay_mound(47)
cap_r_v = cap_r()
cap_l_v = cap_l()
pad_v = radar_pad()
mast_v = radar_mast()
antenna_v = radar_antenna()
missile_v = preview_missile()


def shift(d, ox):
    return {(x + ox, y, z): c for (x, y, z), c in d.items()}


def row(n, open_=False):
    out = {}
    out.update(cap_l_v)
    for i in range(n):
        ox = CAP_W + i * BAY_W
        out.update(shift(mound_a_v if i % 2 == 0 else mound_b_v, ox))
        out.update(shift(CORE, ox))
        if open_:
            out.update(shift(swing(door_l_v, DOOR_HINGE_L, -90), ox))
            out.update(shift(swing(door_r_v, DOOR_HINGE_R, 90), ox))
            out.update(shift(missile_v, ox))
        else:
            out.update(shift(door_l_v, ox))
            out.update(shift(door_r_v, ox))
    ox = CAP_W + n * BAY_W
    for p in (cap_r_v, pad_v, mast_v, antenna_v):
        out.update(shift(p, ox))
    return out


row1_open = row(1, open_=True)
row1 = row(1)
row2 = row(2)
row3_open = row(3, open_=True)
row3 = row(3)

PARTS = {
    "coffin-bay-core-v1": CORE,
    "coffin-bay-door-l-v1": door_l_v,
    "coffin-bay-door-r-v1": door_r_v,
    "coffin-bay-mound-a-v1": mound_a_v,
    "coffin-bay-mound-b-v1": mound_b_v,
    "coffin-cap-l-v1": cap_l_v,
    "coffin-cap-r-v1": cap_r_v,
    "coffin-radar-pad-v1": pad_v,
    "coffin-radar-mast-v1": mast_v,
    "coffin-radar-antenna-v1": antenna_v,
    "coffin-assembled-row2-v1": row2,
    "coffin-assembled-row1-open-v1": row1_open,
}


def write_vox(path, vox, palette):
    import struct
    def chunk(cid, content, children=b""):
        return cid + struct.pack("<ii", len(content), len(children)) + content + children
    assert min(p[0] for p in vox) >= 0 and min(p[1] for p in vox) >= 0 and min(p[2] for p in vox) >= 0, path
    sx = max(p[0] for p in vox) + 1; sy = max(p[1] for p in vox) + 1; sz = max(p[2] for p in vox) + 1
    assert max(sx, sy, sz) <= 256, (path, sx, sy, sz)
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
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "coffin_v1")
    os.makedirs(out, exist_ok=True)
    for name, d in PARTS.items():
        write_vox(os.path.join(out, name + ".vox"), d, PALETTE)
        if "assembled" not in name:
            print(f"  {name}: {components(d)} component(s)")
    print("MISSILE_SEAT", MISSILE_SEAT, "MISSILE_DIR", MISSILE_DIR, "RAIL_DEG", RAIL_DEG)
    print("OPENING (plane y=%d)" % OPEN_Y, OPENING, "TUBE_BOX", TUBE_BOX)
    print("DOOR_HINGE_L", DOOR_HINGE_L, "(open -90)", "DOOR_HINGE_R", DOOR_HINGE_R, "(open +90)")
    print("RADAR_SPIN", RADAR_SPIN, "PAD_TOP", PAD_TOP, "MAST_H", MAST_H)
