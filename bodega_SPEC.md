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
  footprint's min corner, no slab/yard. `FACTORY_VOXEL 0.13` m.
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

The tileset follows the factory kit's 10-voxel story module, so a story is
1.3 m at FACTORY_VOXEL 0.13 — the same proportional language as the kit and
the harbor set (kit mill loading door = 6/10 of a story; our arches = 6/10,
French doors 7/10, railings 3/10). Openings/railings are proportioned to
read true against the 1.5 m soldier the way the kit's own doors do; nothing
is built at concept-pixel size and nothing is dilated — every voxel is
authored detail.

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

## Palette (20 slots, literal PALETTE in the generator)

plaster (198,162,102) · plaster_dark (156,122,76) · teal (104,158,150) ·
teal_dark (68,110,104) · stone (172,164,148) · stone_dark (124,116,100) ·
wood (128,94,62) · wood_dark (86,62,40) · iron (56,58,64) ·
iron_dark (32,34,40) · glass (110,142,152) · glass_dark (38,54,68) ·
sack (178,154,110) · awn_a (140,190,182) · awn_b (238,232,218) ·
tinaco (40,40,46) · rust (150,88,52) · coping (208,202,192) ·
roof (102,104,100) · wood_floor (150,112,74)

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
| mural | flagship turquoise | teal kept | original canvas | deterministic coral-pink paint patches on exterior wall faces (hash-based 4×4 blotches, never on trim/glass/interiors); one large faded white 5-point star on the square building's south face (rasterized, hash-weathered, no lettering) |

All variants: 29,336 voxels per assembly (recolor-only — file diffs vs the
original show 0 added / 0 removed voxels), 0 floaters on every part and
assembly. Viewer ids: cement 296, brick 297, mural 298 (separate entries,
not replacements).
