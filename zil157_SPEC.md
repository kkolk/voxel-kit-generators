# ZIL-157 Soviet 6x6 Truck — SPEC (v1)

Generator: `zil157_truck_v1.py` (standalone, stdlib + Pillow).
Work dir: `~/workspace/your_files/strike-bay-zil157/`

All numbers below are MEASURED from the regenerated voxels (2026-10-03,
7 reviewer fixes applied: breech well, traverse ±140°, frame-direction
disambiguation, shelled canvas, measured scale table, left-hand-drive
steering, part-separation clearance).

## Scale & frame

- **TRUCK_VOXEL = 0.09 m/voxel** (declared constant in the generator; ZSU convention).
- z-up voxel space, origin at footprint min corner, ground z=0.
- x = width (0–24), y = length with **y=0 at the front bumper** (0–77), z up.
- **VEHICLE forward = file −y (nose at y=0 bumper); GUN rest pose = +y
  (barrels over the bed).** File-forward −y ⇒ vehicle left = +x, vehicle
  right = −x. The barrels are authored at 0° elevation pointing +y, matching
  the ZPU-2/ZSU file convention; on the truck frame +y runs from the front
  bumper toward the tailgate, so at rest traverse the AA gun faces rearward
  over the bed (classic gun-truck pose).
- **All 12 rig parts are authored in ONE shared coordinate frame: file coords == design coords**
  (the `.vox` writer is called with xoff=0, yoff=0 for every part, so the game
  layers parts without recentering).
- **AA pairing: the `bed-aa-turret` / `bed-aa-barrels` parts pair ONLY with
  `bed-technical`.** The barrels pierce the flat bed's tall tailgate
  (4 voxels at (9,10,14,15, 74, 22)) and collide with the covered bed
  (24 barrel + 147 turret voxels) — the technical bed's lowered
  headboard/tailgate/side boards exist precisely for the gun sweep.

## Part table

| slug | contents | voxels | file dims (x·y·z) | components |
|---|---|---|---|---|
| zil157-chassis-v1 | ladder rails, 8 cross members, 3 axles + diffs, driveshafts, leaf springs, fuel tank (left), exhaust (right), bumpers, tow hooks, steering box (left) | 3,112 | 24×78×14 | 1 |
| zil157-cab-v1 | hood + louvers + "157" stencil (−x face), slat grille + guards, headlights, fenders, split windshield, doors, mirrors, roof, bench + left-hand steering wheel, spare tire + carrier | 7,038 | 24×37×27 | 1 |
| zil157-wheels-front-v1 | steerable pair: single tires, tread blocks, hubs, kingpins | 678 | 22×13×13 | 2 (one per wheel — genuine separate running gear) |
| zil157-wheels-rear-v1 | bogie: 4 dual-wheel positions, tread blocks, hubs | 1,792 | 23×25×13 | 4 (one per dual position) |
| zil157-bed-flat-v1 | wooden stake bed: plank floor, 3-board sides, headboard, tailgate, stake pockets, mudguards | 3,250 | 25×38×25 | 1 |
| zil157-bed-covered-v1 | flatbed + 4 hoops + closed olive canvas cover (2-vox shell, hollow) | 6,230 | 25×38×31 | 1 |
| zil157-bed-technical-v1 | flatbed + AA pedestal ring (lowered headboard/tailgate/side boards + breech well for the gun sweep) | 3,047 | 25×38×21 | 1 |
| zil157-bed-aa-turret-v1 | traversing cradle: turntable annulus, cheeks, trunnion, seat, sight, ammo boxes, handwheel | 1,018 | 15×19×31 | 1 |
| zil157-bed-aa-barrels-v1 | elevating twin barrels: receivers, collared barrels, muzzle brakes | 1,009 | 9×44×27 | 1 |
| zil157-assembled-flat-v1 | merged chassis+cab+wheels-front+wheels-rear+bed-flat | 15,681 | 25×78×27 | 1 |
| zil157-assembled-covered-v1 | merged chassis+cab+wheels+bed-covered | 18,661 | 25×78×31 | 1 |
| zil157-assembled-technical-v1 | merged chassis+cab+wheels+bed-technical+aa-turret+aa-barrels | 17,399 | 25×89×31 | 1 |

Palette (21 named entries; the viewer Assemblies sidebar derives from these):
olive, olive_dark, olive_light, rust, rust_dark, tire, tire_side, steel,
steel_dark, gunmetal, gunmetal_dark, dark, wood, wood_dark, canvas,
canvas_dark, glass, white, window, brass, red.

## Pivot table (.vox / design coords)

| pivot | coords | axis | notes |
|---|---|---|---|
| STEER_L | (22, 14, 6) | z (vertical kingpin) | left front wheel (+x = left) |
| STEER_R | (3, 14, 6) | z (vertical kingpin) | right front wheel |
| front spin | x-axis through (y=14, z=6) | x | per wheel, at its steer pivot |
| rear spin ×4 | (3,49,6), (22,49,6), (3,61,6), (22,61,6) | x | one per dual position per axle |
| TRAVERSE_PIVOT | (12, 55, 18) | z | parent aa-turret here; = turntable/pedestal-gear interface plane |
| ELEVATION_PIVOT | (12, 55, 23) | x | parent aa-barrels here as child of traverse node; = trunnion center |

- Barrels authored at 0° elevation, pointing **+y** (muzzle reaches y=88).
- Elevation limits: **−5° … +80°**. A breech well is machined through the
  turntable (kept as an annulus so the cradle stays connected), the pedestal
  and the bed floor along the breech swing — pivot (12,55,23), breech reaches
  y≈45–54 and drops ~10 vox below the pivot at +80°. Measured: **0
  unintended hits −5°…+90°** (trunnion wrap excluded); first contact at +93°
  (2 voxels, breech bottom vs bed-floor slot edge at (9,57,13),(14,57,13)).
  The documented +80° keeps margin for in-game rotation rounding.
- Traverse: **recommend stops at ±140°**. Measured 0 hits (barrels and
  turret) through ±145°; the barrels clip the cab rear top corners at ±150°
  (+150°: 7 voxels at (4,34–35,22–24),(5,36,24); −150°: 20 voxels at
  (19–21,31–36,21–24)). 180° traverse sweeps the barrels through the cab roof
  (roof z=26 > barrel plane z 22–24). Full 360° is geometrically possible but
  collides with the cab — game-side stops required.

## Scale-check numbers (TRUCK_VOXEL 0.09; measured from the voxels)

| check | model | real ZIL-157 |
|---|---|---|
| overall length 78 vox (y 0–77 incl. rear tow hitch) | 7.02 m | 6.93 m (Δ +0.09, the hitch) |
| width 25 vox (bed x 0–24) | 2.25 m | 2.32 m (Δ −0.07) |
| cab roof z=26 | 2.34 m | 2.36 m ✓ |
| door window glass bottom z=17 | 1.53 m | — (soldier 25 vox = 1.50 m; glass starts just above the soldier's head) |
| wheel diameter 13 vox | 1.17 m | 1.20 m ✓ |
| diff pumpkin bottom z=3 | 0.27 m | clearance 0.31 m ✓ |
| front axle → bogie center 41 vox | 3.69 m | 3.66 m ✓ |
| bogie axle spacing 12 vox | 1.08 m | 1.12 m ✓ |

(The generator computes length/width/glass-bottom from its vox dicts and
asserts 78/25/17.)

## Clearance validation (all numeric, from the generator's self-check)

- **chassis∩cab separation**: **0 intersecting voxels** (was 75 over z 7–14).
  The radiator shell bottom was raised to z=12, the steering box moved to the
  left rail (top z=11, flush), and the remaining overlaps were carved out of
  the cab: exhaust pipe vs front mudflap (4), fuel-tank top/straps/filler cap
  vs running board (20), driveshaft vs spare-tire carrier bracket (27).
  The intersection is now only the intended mounting pads (adjacent, z=12 on
  rail tops z=11 — 208 contact voxels, pads themselves 120/120 intact).
- **Steering sweep**: each front tire rotated ±30° about its kingpin
  (22,14)/(3,14): **0 colliding voxels** against cab + chassis (z≥8) on both
  wheels, both directions. (Axle/knuckle overlap is intended running-gear
  contact and excluded.)
- **Mudguards vs rear duals**: rear mudflaps shifted 1 voxel rearward
  (y 68–70; rearmost tire reaches y=67): **0 overlap** (was 8 voxels at
  (1–4/20–23, 67, 6)). Guard plate z 13–14, tire top z 12 → 1 voxel clear;
  arch skirts follow r=7 around each bogie axle; no steering on the bogie.
- **Spare tire vs cab/bed**: spare (y 35–37) shares only the mounting planes with
  the cab back (y=35) and headboard (y=37) — intended carrier contact, 0 deep overlap.
- **AA barrels at 0° vs bed**: 0 overlap (technical bed has lowered headboard z≤18,
  tailgate z≤18, side boards z≤20 for the gun sweep).
- **AA traverse ±140°**: barrels 0 collisions; turret 0 real collisions
  (+18/+20 voxels of intended turntable-bottom/pedestal-gear interface at z=18).
- **AA elevation sweep −5°…+90°** (1° steps, vs turret + technical bed +
  chassis + cab): **0 unintended hits** through the whole sweep (trunnion
  wrap excluded); first contact beyond at +93°. Documented game limit +80°.
- **Interface contacts**: cab pads z=12 on rail tops z=11: 208 voxels; bed sills
  z=12 on rail tops z=11: 152 voxels (flat and technical); pedestal ring z=14
  on bed floor top z=13: 848 voxels; front wheels 6 ground-touch voxels
  (tangent), rear duals 16.
- **Floater sweep**: every rig part is ONE 6-connected component, except the
  wheels parts which are one component per genuine running-gear unit
  (front: 2, rear: 4). Assembled unions: 1 component each. (The breech well
  briefly orphaned the right cheek cap's front; it is bridged sideways onto
  the right ammo-box lid with 4 sweep-clear voxels — turret back to 1.)

## Style notes

Weathered Soviet olive-drab: flat shading + olive_light sun-fade on upward faces,
olive_dark panel sensibility, sparse rust streaks bleeding down from bolts, handles,
headlight buckets, stake pockets and the fuel tank (recolor-only, no floaters).
Wooden bed in grey-brown weathered planks with dark plank gaps; faded-olive canvas
(2-voxel shell over the 4-hoop profile, hollow interior — 8.3% buried vs 44.5%
before) with hoop rib shading and tie-downs on the closed rear flap. Tires near-black with
lighter sidewall rings + tread blocks. Glass pale blue-grey. White "157" stencil on
the −x hood face — the truck's RIGHT side (file-forward −y ⇒ left = +x), matching
the reference painting's visible side (24 white voxels, verified legible in the
side ortho render). Steering wheel + column on the LEFT (+x) side: left-hand drive.
No star, per the reference painting.

## Files

- `zil157_truck_v1.py` — the generator (PALETTE + CI + B/cyl/ring helpers +
  verbatim skill-boilerplate `.vox` writer / isometric preview / slice renderer;
  the writer takes optional xoff/yoff so all parts share one frame; post-build
  clearance carves for Fix 7a (cab/chassis) and Fix 1 (breech well machined
  from the −5…+90° elevation sweep, trunnion kept solid)).
- `zil157-*.vox` + `zil157-*_preview.png` — 12 models + 12 previews.
- `zil157_pack.zip` — all 12 .vox + generator + 12 previews + SPEC.md (for the wiring issue).
- `reference/` — the two user-supplied references.

## NOT done (ship phase, separate)

Not uploaded to the Voxel Viewer, not committed to any repo, no Gitea issue filed —
per instructions the ship phase is separate.
