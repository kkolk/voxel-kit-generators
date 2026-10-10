# Bodega Corner — seaside-town tileset spec (v1, 2026-10-05)

First building of the Strike Bay rundown seaside town: a 4-story colonial
corner tenement with a ground-floor bodega behind an arched arcade.
Off the user's bodega-corner concept painting (ochre plaster, teal trim,
stone arcade, striped awning, tinacos + TV antennas on the roof).

**Revision 2026-10-05 (user-directed):** buried interior rooms removed —
interiors are wide open with real floor slabs (stone ground slab z 0..1,
wood-plank slabs at z 9/19/29/39..40); every window and glazed door is
inset 1 voxel (punched opening, 1-deep reveal).

## Grid contract (inherited from the factory kit)

- **B = 12** bay, **S = 10** story, **T = 2** wall, **z-up**, origin at the
  footprint's min corner, no slab/yard. **In game: 0.3 m per voxel**
  (Strike Bay `FactoryCompounds.KIT_VOXEL`), so a story is 3 m and a bay 3.6 m.
- Tileset unit = one **12×12 bay, one story tall** (z s..s+10). Canonical
  orientation faces **south** (exterior wall at y 0..2); the generator
  rotates bays CCW about the bay centre (S→E→N→W) when composing.
- **Seam rule (mill-style, strict):** wall ends meet flush at bay lines —
  no half-columns on plain faces. Nothing protrudes past x 0..12 / y 0..12
  **along the bay-run direction**. Outer corner columns (2×2) are written
  whole by the corner module; the two walls butt into the column (x 2..12 /
  y 2..12). The L's inside notch is closed by a dedicated 2×2 pier tile.
- **Protrusions along the wall-face normal are the design** (documented,
  never sideways): balcony slab 2, awning 3, sills/cornice/coping 1,
  awning brackets 1, sign band flush.
- **Interiors are wide open** (no buried rooms): a full stone ground slab
  at z 0..1, plus a wood-plank floor slab at the top voxel of every story
  band (z 9..10, 19..20, 29..30, 39..40) — each story's ceiling is the
  floor above; the top slab is the roof deck under the cornice. Slabs are
  inset 2 from walled faces and run full to bay lines on open faces, so
  neighbouring slabs meet without overlap.
- **Every window and glazed door is inset 1 voxel**: the opening is punched
  through the outer wall voxel and the glass/frame/shutters sit 1 deep —
  a real 1-deep plaster reveal, not a painted-on face. Sills stay proud 1
  (allowed trim); balcony railings stay proud as before.
- **No lettering on any voxel build** (mirror-text lesson, harbor 2026-10-04):
  the sign band is a blank teal board.

## Story rhythm (per story, base s)

- Ground (s=0): stone threshold/water table z 0..1 (proud 1); arcade piers
  z 1..8 (half-piers x 0..1 / 11..12 at bay edges so neighbours unite to a
  full 2-wide pier, full pier x 5..7 at centre); arch openings z 1..7
  (4 wide: x 1..5, 7..11) with stepped arch springs z 7..8; spandrel +
  **blank teal sign band** z 8..9 (front layer); stone entablature z 9..10.
- Upper (s=10,20,30): ochre plaster walls; openings z s+2..s+7; teal trim
  band z s+8..s+9 (front layer, both faces on corners); stone sills z s+1
  (proud 1); plaster_dark peel patches + rust streaks under sills.
- Top: corbelled coping cornice z 40..42 (proud 1); roof slab z 42..43
  (full bay); plaster parapet z 43..46; coping z 46..47 (proud 1).

## Scale note

**Corrected 2026-10-05 (strike-bay#296).** In game the bodega kit draws at
**0.3 m per voxel**, the factory kit's `KIT_VOXEL`: a 10-voxel story is
3 m, a 12-voxel bay 3.6 m, and the 4-story corner building stands ~14 m to
the coping. (The earlier wording here, FACTORY_VOXEL 0.13 and a 1.3 m
story, described a build shorter than the soldier; nothing in game uses
that scale.) Proportion new parts at 0.3 m: a door 7 voxels = 2.1 m, a rail
3 = 0.9 m, a bench seat 1 above the ground = 0.3–0.45 m. Every voxel is
authored detail; nothing is dilated.

## Lite interiors

Every part builder takes a lite option (`--lite` on the command line, or
`bodega_town_v1.part(name, variant, lite=True)`): slabs, walls and stairs
only, no shop dressing (counters, shelves, jars, sacks, barrels, crates,
workbenches, tables). Parts without dressing are unchanged by it. Lite part
files carry a `-lite` suffix. For towns: use lite for upper floors and
mid-block buildings.

Measured: the corner preview drops 29,336 → 28,634 voxels (−2.4%); a
dressed ground bay drops 50–120 voxels. The shell and slabs, not the
dressing, are most of the ~600 voxels per bay-story, so lite alone does
not make the town budget; fewer stories and low caps do more.

## Module catalog (18 parts, canonical orientation)

Ground (12×12×10, z 0..10):
| part | faces | notes |
|---|---|---|
| bodega-g-arcade | S | 2 arches, blank sign band, striped awning (3 proud) + iron brackets, shop interior: counter, shelf wall with jars, sacks, barrels, crates |
| bodega-g-arcade-corner | S+W | corner column whole; arcade both faces; awning on S face |
| bodega-g-shopfront | S | wide open shopfront (no arches), wood lintel, sign band, counter + shelves + sacks + barrels |
| bodega-g-stair | S | wood entry door + stone surround, barred transom, interior steps |
| bodega-g-plain | S | plaster, shuttered window, wood back door, crates + sacks |

Upper (12×12×10, z 0..10 local, placed at s=10/20/30):
| part | faces | notes |
|---|---|---|
| bodega-u-shutter | S | 2 closed-shutter windows (teal + slats), teal band, sills |
| bodega-u-balcony | S | French door + wrought-iron balcony (slab 2 proud, railing 3 tall, corbels), flanking narrow shutter windows |
| bodega-u-barred | S | 2 barred windows (glass_dark + iron bars) with folded-open teal shutters |
| bodega-u-corner | S+W | corner column whole (plaster), 1 shuttered window per face, teal bands |

Top:
| part | footprint | notes |
|---|---|---|
| bodega-top-cornice | 12×12×2 | S face, z 40..42, dentil course, proud 1 |
| bodega-top-cornice-corner | 12×12×2 | S+W |
| bodega-roof-parapet | 12×12×5 | S face; slab z 42..43 full bay, parapet z 43..46, coping z 46..47 |
| bodega-roof-parapet-corner | 12×12×5 | S+W |
| bodega-notch-pier | 2×2×10 | inside-corner pier, stone, per story |
| bodega-notch-pier-cap | 2×2×7 | z 40..47: cornice + parapet + coping for the notch |

Roof props (base z=0, seated on slab z=43):
| part | notes |
|---|---|
| bodega-prop-tinaco | black tank on 4 iron legs + lid + pipe + rust band |
| bodega-prop-antenna | TV antenna: iron mast + crossbars |
| bodega-prop-crates | wood crate cluster |

## Palette (38 slots, literal PALETTE in the generator)

plaster (198,162,102) · plaster_dark (156,122,76) · teal (104,158,150) ·
teal_dark (68,110,104) · stone (172,164,148) · stone_dark (124,116,100) ·
wood (128,94,62) · wood_dark (86,62,40) · iron (56,58,64) ·
iron_dark (32,34,40) · glass (110,142,152) · glass_dark (38,54,68) ·
sack (178,154,110) · awn_a (140,190,182) · awn_b (238,232,218) ·
tinaco (40,40,46) · rust (150,88,52) · coping (208,202,192) ·
roof (102,104,100) · wood_floor (150,112,74)
art_face (202,166,106) — slot 38, blank-art reserve (#308, §Boards):
near-plaster but exactly separable from plaster (198,162,102), so the
game routes it to the board material by colour while unassigned boards
read as plain wall. Skins remap it to their own near-wall reserve
(cement art_concrete, brick art_brick, mural art_turquoise); skin
extras now follow at 39+.

Town expansion (slots 21–37, appended so 1–20 never move; skins remap none
of them): tile (172,86,58) · tile_dark (128,62,44) · corr (150,152,148) ·
corr_dark (112,114,112) · pier (160,158,150) · pier_dark (112,110,104) ·
rubber (30,30,32) · bronze (110,92,60) · bronze_dark (78,64,44) ·
red (180,52,44) · water (70,130,150) · leaf (70,118,58) ·
leaf_dark (48,86,44) · trunk (120,100,76) · soil (88,66,48) ·
crane (204,160,52) · lamp (240,220,160). Skin extras follow at 39+.

## Preview assemblies (bodega-corner-v1.vox)

- **A — square:** 2×2 bays (24×24), 4 stories. Ground: 4× g-arcade-corner.
  Stories 1–3: 4× u-corner. Top: 4× cornice-corner + 4× parapet-corner.
  Props: 2 tinacos, 1 antenna, 1 crate cluster.
- **B — L:** 4×3 bays (48×36) minus the NE 2×2 quadrant = 8 bays, same
  height. Ground: arcade-corner / arcade / plain / stair / shopfront mix
  (shopfront faces the notch courtyard). Uppers: shutter / balcony / barred
  mix, varied per story. Notch closed by 4× notch-pier + 1 pier-cap.
  Buildings sit side by side with a ~12-voxel gap.

Viewer: exactly ONE entry, slug `bodega-corner-v1`
("Bodega Corner (tileset preview)"). Individual part .vox files live in
this work dir for inspection and gluing; they are not separate entries.

## Material variants (v2, 2026-10-05, user-directed)

Same 18-part geometry, same grid — new skins only. Implemented as a
`VARIANT` parameter in the generator (`bodega` | `cement` | `brick` |
`mural`; one run builds all four). Geometry builders always emit
canonical bodega-skin color names; each variant remaps a subset to
variant colors appended to the palette. File stems:
`bodega-corner-{variant}-v1.vox` (+ `_preview.png`, + stem-matched
`bodega-corner-{variant}-v1.py` so the viewer's static PALETTE parse
derives the right color names); parts `bodega-{variant}-<part>.vox`.

| variant | wall | trim | awning | extras |
|---|---|---|---|---|
| cement | bare concrete gray | weathered gray (no teal left) | gray / off-white | the quietest skin |
| brick | exposed red-brown brick | faded off-white painted trim | weathered canvas teal/cream | — |
| mural | flagship turquoise | teal kept | original canvas | deterministic coral-pink paint patches on exterior wall faces (hash-based 4×4 blotches, never on trim/glass/interiors). No voxel mural art: the wall is left open for texture murals painted on in game (strike-bay#308; the voxel star was removed 2026-10-05) |

All variants: 29,336 voxels per assembly (recolor-only — file diffs vs the
original show 0 added / 0 removed voxels), 0 floaters on every part and
assembly. Viewer ids: cement 296, brick 297, mural 298 (separate entries,
not replacements).

## Town expansion (v3, 2026-10-05, strike-bay#296)

`bodega_town_v1.py` adds 39 parts for port towns, on the same grid
contract and the same four skins (it imports this generator's palette,
skins and helpers). `part(name, variant, lite)` in that module builds any
bodega part, core or town: the entry point for prefab builders.

```
python3 bodega_town_v1.py [bodega|cement|brick|mural ...] [--lite] [--out DIR]
```

writes `bodega-{skin}-<part>[-lite].vox` + `_preview.png` per part and a
town preview `bodega-town-{skin}-v1[-lite].vox` + `_preview.png` (block of
1-story shops with low caps, a 2-story row house under a tile gable, a
civic portico + tower, a plaza of props, the harbor shed and a finger pier
with T-head, crane, bollards, fenders and steps). The iso preview shows the
north and east faces; canonical fronts face south.

Footprints are half-open voxel bounds in the part's local frame,
x0..x1 / y0..y1 / z0..z1 (negative y = proud of the south face). Voxel
counts are the full-interior bodega skin.

### Low caps (placed at the top of the walls: s = 10 or 20)

| part | bounds | vox | notes |
|---|---|---|---|
| cap-1s | 0..12 / −1..12 / 0..5 | 264 | coping course, roof slab z 1, parapet 2, coping; S face |
| cap-1s-corner | −1..12 / −1..12 / 0..5 | 370 | S+W |
| cap-2s | 0..12 / −1..12 / 0..7 | 324 | dentil cornice 2, slab z 2, parapet 3, coping |
| cap-2s-corner | −1..12 / −1..12 / 0..7 | 483 | S+W |

Roof deck top (where roof props and the civic tower sit): s + 2 for
cap-1s, s + 3 for cap-2s (s + 3 = 43 for the 4-story top, as before).

### Ground and upper bays (12×12×10, faces S)

| part | bounds | vox (lite) | notes |
|---|---|---|---|
| g-garage | 0..12 / −1..12 / 0..10 | 504 (447) | corrugated roll door 8 wide inset 1, lintel, blank sign band; workbench, oil drum, tyres |
| g-warehouse | 0..12 / −1..12 / 0..10 | 475 (441) | plank loading door 7×7 (2.1 m), barred high window (sill 1.5 m); crates, sacks |
| g-warehouse-corner | −1..12 / −1..12 / 0..10 | 685 (661) | S+W, stone corner column, high window per face |
| g-cafe | 0..12 / −4..12 / 0..10 | 611 (544) | piers + beam on the street line, awning, checker-floor loggia y 2..5, glazed front set back at y 5; tables and chairs |
| g-row-door | 0..12 / −2..12 / 0..10 | 534 (534) | narrow raised door, 2-step stoop proud 2, shuttered window, interior stair (kept lite) |
| u-loggia | 0..12 / 0..12 / 0..10 | 420 | recessed balcony 6 wide × 4 deep, iron balustrade on the wall line, French door |
| civic-portico | 0..12 / −2..12 / 0..10 | 710 (688) | raised floor z 0..2, 2 steps proud 2, 2 columns + half pilasters (pair at bay lines), cornice proud 1, back wall at y 6..8 with double door |

### Civic tower

| part | bounds | vox | notes |
|---|---|---|---|
| civic-tower | −1..13 / −1..13 / 0..38 | 1899 | 12×12 on the roof deck; 2 stories (windows, open belfry arches + bell), cornice proud 1 on all four sides, stepped tile pyramid z 21..27, flagpole + red flag to z 38 |

The tower's cornice overhangs the bay by 1 sideways; it stands above
every neighbour's roof, so nothing meets it.

### Gable roofs (placed at the top of the walls; ridge 6 above)

| part | bounds | vox | notes |
|---|---|---|---|
| roof-gable-1b-tile | 0..12 / −1..13 / 0..8 | 336 | one bay deep, 1:1 pitch, eaves proud 1 front and back, ridge cap |
| roof-gable-1b-corrugated | 0..12 / −1..13 / 0..7 | 312 | ribs across the slope, rust runs |
| roof-gable-2b-tile | 0..12 / −1..12 / 0..8 | 300 | half of a 2-bay-deep gable, 1:2 pitch, ridge at y 11; the far half is the same part at k=2 in the next bay |
| roof-gable-2b-corrugated | 0..12 / −1..12 / 0..7 | 288 | |
| gable-end-1b | 1..11 / −1..2 / 0..5 | 66 | triangle infill under a 1b roof, coping verge proud 1, attic vent |
| gable-end-2b-l | 0..9 / −1..2 / 0..5 | 59 | half triangle, ridge on the left seen from outside |
| gable-end-2b-r | 3..12 / −1..2 / 0..5 | 59 | ridge on the right |

Roofs are 2 voxels thick (each column [h−1, h]) so the steps share faces.
Roofs end flush at bay lines along the ridge (no sideways verge overhang);
place a gable end on the end bays, turned to face out (W: k=3, E: k=1).
Tile and corrugated keep their colours in every skin; gable ends are
plaster and take the skin.

### Plaza and street props (base z 0, own footprint)

| part | bounds | vox | notes |
|---|---|---|---|
| prop-monument | 0..8 / 0..8 / 0..17 | 231 | stepped plinth, bronze figure ~2.1 m, arm raised |
| prop-obelisk | 0..11 / 0..11 / 0..31 | 653 | tapering obelisk on a stepped base, red 5-point star on top (tip up) |
| prop-fountain | 0..14 / 0..14 / 0..9 | 417 | round basin, rim 2, water, centre column, bowl, spout |
| prop-bandstand | 0..16 / −2..16 / 0..17 | 1060 | octagonal platform with steps S, 8 iron posts, railing, stepped tile roof, finial |
| prop-bench | 0..6 / 0..2 / 0..3 | 22 | 1.8 m park bench |
| prop-lamp | 0..2 / 0..2 / 0..15 | 19 | 4.2 m lamp post, lantern |
| prop-palm | 0..9 / −2..7 / 0..18 | 116 | stone planter 5×5, leaning trunk, drooping fronds (overhang the planter) |
| prop-kiosk | −1..6 / −1..6 / 0..9 | 229 | 5×5 booth, serving window S, counter, overhanging roof |
| prop-pole | 0..7 / 0..1 / 0..28 | 42 | 8.4 m wood pole at x 3, crossarm + insulators |
| prop-bollard | 0..1 / 0..1 / 0..3 | 3 | street bollard |
| prop-trashcans | 0..5 / 0..2 / 0..4 | 30 | two bins |

### Pier set (pier concrete in every skin)

| part | bounds | vox | notes |
|---|---|---|---|
| pier-deck | 0..12 / −1..12 / 0..3 | 309 | 12×12 deck, 2 thick, kerb on the S edge with drain gaps, drip edge proud 1. A 12-wide finger = this part at k=1 and k=3 in the same bay |
| pier-deck-plain | 0..12 / 0..12 / 0..2 | 288 | no kerb, inner modules of a wide deck |
| pier-pile | 0..4 / 0..4 / 0..21 | 96 | 2×2 pile 20 tall (6 m) + 4×4 cap; deck sits on z 21. The game cuts it to the seabed |
| pier-head | 0..36 / −1..12 / 0..3 | 965 | T-head 36×12, berth face S, kerbs on the ends and on N except the finger join at x 12..24 |
| pier-bollard | 0..3 / 0..3 / 0..4 | 16 | mooring bollard |
| pier-fender | 0..4 / 0..3 / 0..8 | 18 | tyre ring on a chain; place at deck z − 5 with y −2 off the berth face so the hook lies over the kerb |
| pier-crane | 0..12 / −12..9 / 0..24 | 707 | travelling portal crane on rail bogies, cab, jib reaching 12 past S, hook |
| pier-steps | 0..8 / −3..0 / 0..8 | 108 | landing steps down a deck face; place at deck z − 6 |
| harbor-shed | −1..37 / −1..25 / 0..17 | 5654 (5490) | 3×2-bay gable warehouse assembled from g-warehouse(-corner), roof-gable-2b-corrugated and gable-end-2b-l/r (`build_shed`) |

The older harbor set (`harbor-*.py`) is not used by the town and was not
touched.

### Boards (blank billboards / murals, strike-bay#308)

Panel field is `art_face` (slot 38, per-skin near-plaster reserve): the
game routes it to the board material by exact colour, and unassigned it
reads as plain wall. Faces SOUTH, art on y = −1; all mounts reach local
z = 0 (floater-clean). Sizes are panel voxels (12×6 = 3.6×1.8 m,
24×8 = 7.2×2.4 m, 36×12 = 10.8×3.6 m at 0.3 m/voxel).

| part | bounds | vox | notes |
|---|---|---|---|
| board-wall-12x6 | −1..13 / −1..1 / 0..8 | 144 | wall-mounted, wood battens embed in wall |
| board-wall-24x8 | −1..25 / −1..1 / 0..10 | 300 | wall-mounted |
| board-wall-36x12 | −1..37 / −1..1 / 0..14 | 588 | wall-mounted |
| board-roof-12x6 | −1..13 / −1..2 / 0..12 | 142 | rooftop, iron A-frame on deck, panel z 5+ |
| board-roof-24x8 | −1..25 / −1..2 / 0..14 | 302 | rooftop |
| board-roof-36x12 | −1..37 / −1..2 / 0..18 | 586 | rooftop |
| board-free-12x6 | −1..13 / −1..1 / 0..9 | 154 | freestanding, wood posts + stone kicker + cap |
| board-free-24x8 | −1..25 / −1..1 / 0..11 | 330 | freestanding |
| board-free-36x12 | −1..37 / −1..1 / 0..15 | 634 | freestanding |
