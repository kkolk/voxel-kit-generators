# Strike Bay HARBOR BUILDINGS — build spec (v1, 2026-10-04)

1960s run-down Havana harbor set: industrial, tin-pot dictatorship, NOT a resort.
Sits beside the modular factory kit in harbor areas on the islands.

## Grid + scale contract (matches the factory kit)

- `B = 12` bay, `S = 10` story, `T = 2` wall thickness. Every building
  footprint is a whole number of bays; story heights are multiples of 10.
- `FACTORY_VOXEL = 0.13` m/voxel — same class constant as the factory kit
  and farm buildings. The 25-voxel / 1.5 m infantryman is the scale anchor:
  personnel doors ~16 vox tall (2.08 m), window sills ~z 10-12, railings ~z 8.
- z-up, origin at the footprint's min corner, at ground level. No ground
  slab, no yard — the game draws those.
- Hollow shells with a buried interior room at z 1..7 for damage reveals
  (buildings only, not props). Room walls stand on floor strips so the
  floater sweep passes.
- Trim may extend 1 voxel past the footprint ALONG THE WALL-FACE NORMAL
  only (balcony rails, cornices, sign boards) — never along a tiling axis.
- Every generator MUST contain a literal `PALETTE = [...]` assignment
  (copy the list below verbatim into the file). The viewer server statically
  parses the generator; an imported name does NOT derive assemblies.
- Copy the `.vox` writer + isometric preview renderer from
  `~/workspace/skills/making-voxel-game-assets/references/boilerplate.py`
  verbatim. Generator `<slug>.py` writes `<slug>.vox` + `<slug>_preview.png`
  and prints the voxel count.
- Validation before reporting done: `floater_sweep` (6-connectivity, every
  component touches base z), read the preview PNG at full size yourself,
  render a top-down slice through the buried room to confirm it is sealed.
- Work dir: `~/workspace/your_files/strike-bay-harbor-buildings/`
  (concepts in `concepts/`). Do NOT upload to the viewer — the parent
  handles shipping.

## Shared palette (literal in every generator)

```python
PALETTE = [
    ("concrete",      (170, 166, 158)),  # water table, sills, lintels, dock
    ("concrete_dark", (112, 108, 100)),
    ("coping",        (202, 198, 190)),  # parapet coping
    ("plaster",       (196, 164, 120)),  # aduana faded ochre plaster
    ("plaster_peel",  (150, 140, 128)),  # peeled plaster / bare render patches
    ("plaster_turq",  (110, 168, 158)),  # tenement faded turquoise
    ("plaster_pink",  (198, 140, 128)),  # tenement faded pink
    ("brick",         (150,  90,  66)),  # chimney, patches
    ("brick_dark",    (120,  68,  50)),
    ("glass",         ( 72,  98, 118)),  # window glass
    ("glass_dark",    ( 44,  62,  78)),  # broken/boarded panes
    ("steel",         (122, 126, 134)),
    ("steel_dark",    ( 62,  64,  72)),  # sash, patches, corrugated repairs
    ("white",         (235, 235, 230)),
    ("window",        ( 18,  26,  38)),  # dark glass / sign backboards
    ("dark",          ( 32,  34,  40)),  # door leaves, tires, litter
    ("wood",          (125,  92,  62)),  # shutters, sign boards, doors
    ("wood_dark",     ( 90,  66,  44)),
    ("rust",          (142,  82,  50)),  # streaks under sills/roofline
    ("roof_grey",     (100, 104, 100)),  # weathered roof slabs
    ("roof_red",      (150,  70,  58)),  # capitania tile roof
    ("iron",          ( 70,  74,  82)),  # railings, window bars
    ("neon_pink",     (255,  80, 160)),  # bar sign tubes
    ("neon_cyan",     ( 80, 230, 255)),  # bar sign tubes / border
    ("neon_yellow",   (255, 220,  90)),  # bar sign tubes
    ("pump_red",      (180,  50,  45)),  # gas pump body, flag
    ("cream",         (232, 220, 190)),  # pump panels, sign boards, letters
    ("sign_blue",     ( 50,  90, 150)),  # PESCA logo
    ("tinaco",        ( 40,  42,  48)),  # black rooftop water tanks
]
```

## 3x5 block font (for painted / neon signs)

Rows top-to-bottom, `#` = foreground voxel. Letters are 3 wide, 5 tall,
1 voxel deep, with 1 voxel spacing between letters.

```python
FONT_3X5 = {
 "A": [".#.","#.#","###","#.#","#.#"],
 "B": ["##.","#.#","##.","#.#","##."],
 "C": [".##","#..","#..","#..",".##"],
 "D": ["##.","#.#","#.#","#.#","##."],
 "E": ["###","#..","##.","#..","###"],
 "F": ["###","#..","##.","#..","#.."],
 "G": [".##","#..","#.#","#.#",".##"],
 "H": ["#.#","#.#","###","#.#","#.#"],
 "I": ["###",".#.",".#.",".#.","###"],
 "L": ["#..","#..","#..","#..","###"],
 "M": ["#.#","###","###","#.#","#.#"],
 "N": ["#.#","##.","##.","#.#","#.#"],
 "O": [".#.","#.#","#.#","#.#",".#."],
 "P": ["##.","#.#","##.","#..","#.."],
 "Q": [".#.","#.#","#.#","##.",".##"],
 "R": ["##.","#.#","##.","#.#","#.#"],
 "S": [".##","#..",".#.","..#","##."],
 "T": ["###",".#.",".#.",".#.",".#."],
 "U": ["#.#","#.#","#.#","#.#","###"],
 " ": ["...","...","...","...","..."],
}
```

Needed words: ADUANA, PESCA, BAR, LA, ESQUINA, CAPITANIA (no accents in
voxel type — use plain capitals).

## Buildings

### 1. harbor-aduana-v1 — customs warehouse
- Footprint 48 x 36 (4 x 3 bays), 2 stories, wall top H = 20.
- Gable roof: eaves at z 22 on the y = 0 / y = 36 faces, ridge along x at
  y = 18, ridge z = 30 (rise 8 over half-span 18). roof_grey planes 2 thick,
  ridge roll, rust streaks along the eave line.
- Walls: plaster (faded ochre) with irregular plaster_peel patches
  (peeling paint revealing render) — patches 2-5 vox, denser near grade.
- Front (y = 0 face): three arched loading bays, one per 12-vox bay at
  x 12..24, 24..36, 36..48? Better: bays centred in three of the four
  12-wide bays (x 0..12, 12..24, 24..36), each opening 8 wide (x c-4..c+4),
  z 2..12, with a round arch top (stepped). Rusted steel_dark sliding doors,
  one bay with doors open (door slabs slid to the sides, dark interior
  visible). Concrete surround + water table.
- Painted sign band above the arches: cream band z 14..19 across the front,
  "ADUANA" in dark 3x5 letters, letters weathered (a few voxels knocked out).
- Upper story: small grimy windows (glass / glass_dark), steel_dark sash.
- Corrugated patch repairs: steel_dark rectangles 3x4 on walls.
- Rust streaks: 1-wide rust strips running down 3-6 vox under sills/eaves.
- Side/rear: one personnel door, small high windows.
- Buried interior room z 1..7.

### 2. harbor-tenement-v1 — dockworkers' tenement block
- Footprint 36 x 24 (3 x 2 bays), 3 stories, wall top H = 30.
- Flat roof: slab z 30..32 roof_grey, plaster parapet z 32..35, coping
  z 35..36. Rooftop: two tinaco black water tanks on wood stands + one
  crooked iron TV antenna. A few dark litter voxels.
- Ground floor (z 0..10): street arcade — recessed loggia y 0..4 behind
  square plaster columns at each bay line (x = 0, 12, 24, 36), round arches
  spanning between columns at z 6..10 (stepped arch). Dark shop doorways
  in the recessed wall, one with a striped awning (white/pump_red stripes,
  sloped, proud 1 over the arcade).
- Upper floors: alternating plaster_turq / plaster_pink per bay with
  plaster_peel patches. Each bay: tall shuttered window (wood shutters,
  one open one closed), iron balcony with iron railing (proud 1, z floor+8
  rail height ~3), some balconies with a tinaco? No — keep balconies empty
  except railing + one with a wood crate.
- Window bars: iron 1-vox grid over ground-floor windows.
- Faded mural: on the x = 0 side wall, a cream band with dark 3x5 text
  "PATRIA O MUERTE" (weathered). Keep it small: one line, z 14..19.
- Rust stains under every sill.
- Buried interior room z 1..7.

### 3. harbor-cannery-v1 — fish cannery
- Footprint 48 x 24 (4 x 2 bays), single tall story, wall top H = 14.
- Sawtooth roof: 3 teeth along x (each 16 wide), vertical glazed faces
  (glass with steel_dark mullions) facing -x? Classic sawtooth: vertical
  face on one side, slope on the other. Teeth: vertical glass face at the
  west side of each 16-vox tooth (x = 0, 16, 32), sloped roof_grey plane
  rising eastward to z 22. Louvered vent (steel_dark slats) on each slope.
- Walls: whitewashed brick gone gray — concrete base with plaster_peel
  patches and grime streaks near grade.
- Long side (y = 0): rows of steel-sash windows, ~40% glass_dark
  (broken/boarded), one boarded with wood planks.
- Big faded sign on the y = 24 wall: sign_blue fish silhouette (simple
  pixel fish ~14 x 6) + cream "PESCA" 3x5 letters beside it, weathered.
- Rusted loading doors (steel_dark + rust patches), one personnel door.
- Exterior steel stair (steel/steel_dark) on the x = 48 end climbing to a
  roof walkway with iron railing.
- Wall pipes (steel_dark verticals) + short brick chimney (brick,
  z 14..24, concrete_dark cap).
- Buried interior room z 1..7.

### 4. harbor-capitania-v1 — port authority office
- Footprint 24 x 24 (2 x 2 bays), 2 stories, wall top H = 20.
- Corner watchtower: 12 x 12 at the (x 12..24, y 12..24) corner, rising to
  z = 30, with arched openings (glass_dark) on each face at z 24..28 and a
  shallow pyramid cap (roof_red) z 30..34. Iron railing around the cap base.
- Main block: red tile gable roof (roof_red planes, ridge along x at
  y = 12, eaves z 22, ridge z 27), ridge roll, a few missing tiles
  (roof_grey patches).
- Walls: cream plaster (use `white` dimmed? No — add nothing; use plaster
  with heavy plaster_peel, reads as aged cream). Tall barred windows: wood
  shutters + iron bar grid. Stone (concrete) steps up to a heavy wood_dark
  double door on the y = 0 face.
- Painted sign band: "CAPITANIA" in dark 3x5 on a cream band above the door.
- Wrought-iron balcony (iron railing, proud 1) on the upper front.
- Flagpole (steel_dark, z 30..40) on the tower cap with a pump_red flag
  (6 x 4, slight wave steps).
- Buried interior room z 1..7.

## Color props (small, at grade, same 0.13 scale)

### 5. harbor-neon-bar-v1 — pole-mounted neon bar sign
- Footprint ~12 x 4. Steel_dark pole z 0..22 (2.86 m). Sign cabinet at top:
  10 x 2 x 7 (x 1..11, z 22..29), window (dark) faces.
- Neon tubes 1 voxel proud of both faces: "BAR" in neon_pink 3x5 letters,
  neon_cyan border rectangle around the cabinet face, two neon_yellow
  underline bars. Small steel_dark mounting arms.
- Concrete footing block z 0..2.

### 6. harbor-bar-sign-v1 — painted cantina board sign
- Two wood posts (z 0..14) holding a cream board 14 x 1 x 6 (z 8..14):
  "BAR" big + "LA ESQUINA" small below, dark letters, weathered.
  Small striped awning (white/pump_red) mounted below the board.
- Freestanding, placeable in front of any building.

### 7. harbor-gas-pump-v1 — 1960s gas pump
- Footprint 6 x 5. Concrete island base z 0..1.
- Body: pump_red lower z 1..8, cream upper z 8..12, rounded top (stepped in
  1 voxel per side at z 12..13). White glass globe (z 13..15) with a
  neon_yellow band.
- Face: dark dial window + white needle marks, steel_dark side panels.
- Hose: dark voxels curving down one side into a steel_dark nozzle boot.
- A few rust voxels at the base.

### 8. harbor-trash-cans-v1 — trash can cluster
- Footprint ~10 x 8. Three galvanized cans (steel body, steel_dark bands):
  two upright (4 x 4, z 0..7) with lids (one lid ajar, rotated), one tipped
  on its side (axis along x, 7 long) with the lid off beside it.
- Rust patches on all cans, a few dark litter voxels scattered.
- All parts must pass the floater sweep (litter touches grade or a can).

## Reporting
Each builder reports: slug, voxel count, footprint WxDxH, preview path,
and any issue found + fixed during validation.
