# Voxel Kit Generators

Parametric Python generators for the Strike Bay modular factory voxel kit.
Each script builds one `.vox` model (z-up) plus preview/slice renders.

This repo holds the **generators only** — it is separate from the
[voxel-viewer](https://git.frostbyte.us/Muse/voxel-viewer) repo, which serves
the rendered models.

## Layout

- `kit-mill-*.py` — early-brick mill family modules (walls, corners, endwalls,
  roofs, steps, dock, flue duct, L showcase)
- `kit-frame-*.py` — mid-century concrete-frame family modules
- `kit-lot-*.py` — family-neutral lot pieces
- `kit_contract.py` — shared grid contract (B=12 bay, S=10 story, T=2 wall),
  palettes, `.vox` writer, preview renderer, floater sweep
- `smokestack_v1.py`, `smokestack_steel_v1.py` — standalone smokestacks
- `farmhouse_v1.py`, `farmhouse_v2.py`, `barn_red_v1.py` — farm buildings
- `zpu2_*.py`, `infantry_*.py`, `ak47-v1.py` — rig/game assets
- `water_tower_v1.py`, `storage_tank_*.py`, `fuel_tank_v1.py` — tanks

## Usage

```bash
python3 kit-mill-wall-window-2s-v1.py   # writes .vox + _preview.png + _slice.png
```

## Grid contract

See `kit_contract.py` and `KIT_SPEC.md` (in the factory-modules working dir):
origin at footprint min corner, ground level, z-up, no slab/yard. One `.vox`
per module — the viewer parser reads a single model per file.

**Material families never mix inside one building:**
mill = early brick, frame = mid-century concrete + brick infill.
