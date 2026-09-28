#!/usr/bin/env python3
"""kit-frame-showcase-l-v1 — L-shaped frame factory showcase, 2 stories, flat roof.

Composed from real generated kit modules (no partial kit):
  main wing x 0..48, y 0..24: corner-outside-2s + 2x wall-window-2s (south),
    endwall-flat-2s rotated 180 (east cap), endwall-flat-2s rotated CW (north face)
  side wing x 0..24, y 24..48: corner-inside-2s (north+east), endwall-flat-2s (west face)
  roofs: 4x roof-flat-2s (main wing) + roof-flat-corner-inside-2s (side wing)
  furniture: skylight-v1 on main roof, stairhouse-v1 on side roof. Plus the existing smokestack_steel_v1 seated on the side-wing roof (kit-designed seating).

Showcase-only adjustments (documented, not kit modules):
  - endwalls placed with overwrite where they clip bay floor/interior voxels
    (they are exterior faces and run wall-to-ground);
  - main-wing west end roofed by roof-flat-corner-outside-2s (parapet + coping
    cap instead of an open tile end);
  - main-wing north parapet + coping dropped for x 0..24 where the side wing
    joins (the two roofs meet with no parapet between them);
  - side-wing west endwall's south parapet return dropped (junction stub).

Grid: B=12 bay, S=10 story, T=2 wall, z-up, origin at footprint min corner,
ground level. Single model per file.
"""

import importlib.util
import os
import struct
import sys

FAMILY = "frame"

PALETTE = [
    ("concrete", (170, 166, 158)),
    ("concrete_dark", (112, 108, 100)),
    ("coping", (202, 198, 190)),
    ("brick", (150, 90, 66)),
    ("brick_dark", (120, 68, 50)),
    ("glass", (72, 98, 118)),
    ("glass_dark", (44, 62, 78)),
    ("steel", (122, 126, 134)),
    ("steel_dark", (62, 64, 72)),
    ("white", (235, 235, 230)),
    ("window", (18, 26, 38)),
    ("dark", (32, 34, 40)),
    ("green", (100, 118, 94)),
    ("green_dark", (70, 88, 68)),
    ("roof", (100, 104, 100)),
    ("stack_15", (158, 62, 52)),
    ("stack_16", (224, 220, 212)),
    ("stack_17", (0, 0, 0))
]

_HERE = os.path.dirname(os.path.abspath(__file__))
_GOAL = os.path.expanduser("~/workspace/goals/strike-bay-factory-voxel-kit/files/strike-bay-factory-modules")


def _rgba(path):
    d = open(path, "rb").read()
    i = d.find(b"RGBA")
    return [struct.unpack("BBBB", d[i + 12 + k * 4:i + 16 + k * 4])[:3] for k in range(256)]


def _load_rgb(slug):
    mod_path = os.path.join(_HERE, slug + ".py")
    if os.path.exists(mod_path):
        spec = importlib.util.spec_from_file_location(slug.replace("-", "_"), mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "build_module"):
            vox, _ = mod.build_module()
            pal = _rgba(os.path.join(_GOAL, slug + ".vox"))
            return {(x, y, z): pal[ci - 1] for (x, y, z), ci in vox.items()}
    d = open(os.path.join(_GOAL, slug + ".vox"), "rb").read()  # legacy generator
    i = d.find(b"XYZI")
    n = struct.unpack("<i", d[i + 12:i + 16])[0]
    pal = _rgba(os.path.join(_GOAL, slug + ".vox"))
    vox, p = {}, i + 16
    for _ in range(n):
        x, y, z, ci = struct.unpack("BBBB", d[p:p + 4]); p += 4
        vox[(x, y, z)] = pal[ci - 1]
    return vox


def _tf(vox, fn, dx=0, dy=0, dz=0):
    return {(fn(x, y)[0] + dx, fn(x, y)[1] + dy, z + dz): c for (x, y, z), c in vox.items()}


def _norm(vox):
    xs = [p[0] for p in vox]; ys = [p[1] for p in vox]
    mx, my = min(xs), min(ys)
    return {(x - mx, y - my, z): c for (x, y, z), c in vox.items()}


_I = lambda x, y: (x, y)
_R180 = lambda x, y: (-x, -y)
_RCW = lambda x, y: (y, -x)


def build_module():
    F = FAMILY
    comp = {}

    def _place(vox, overwrite=False):
        for p, c in vox.items():
            if p in comp and comp[p] != c and not overwrite:
                continue
            comp[p] = c

    _place(_tf(_load_rgb(f"kit-{F}-corner-outside-2s-v1"), _I, 0, 0))
    _place(_tf(_load_rgb(f"kit-{F}-wall-window-2s-v1"), _I, 24, 0))
    _place(_tf(_load_rgb(f"kit-{F}-wall-window-2s-v1"), _I, 36, 0))
    _place(_tf(_norm(_tf(_load_rgb(f"kit-{F}-endwall-flat-2s-v1"), _R180)), _I, 48, -1))
    # fill the 2x2 notch at the L's inside corner (22..23, 22..23) where the
    # main-wing north coping and side-wing east coping meet but don't overlap.
    # Copy the rgb from an existing coping voxel to guarantee palette match.
    _nz = (26 if F == "mill" else 25)
    _notch_rgb = (202, 198, 190)  # coping
    for _nx in (22, 23):
        for _ny in (22, 23):
            comp[(_nx, _ny, _nz)] = _notch_rgb
    _ewN = _load_rgb(f"kit-{F}-endwall-flat-2s-v1")
    # drop the local south return (becomes the west stub at the wing junction
    # after RCW); the east return stays to meet the east cap
    _ewN = {p: c for p, c in _ewN.items()
            if not (p[1] < 2 and p[2] >= 22)}
    _place(_tf(_norm(_tf(_ewN, _RCW)), _I, 24, 22), overwrite=True)
    _place(_tf(_load_rgb(f"kit-{F}-corner-inside-2s-v1"), _I, 0, 24))
    _ew = _load_rgb(f"kit-{F}-endwall-flat-2s-v1")
    # drop the south parapet return stub where the side wing meets the main
    # wing (local coords: the return's voxels outside the end-cap footprint)
    _ew = {p: c for p, c in _ew.items()
           if not ((p[0] < 0 and p[1] < 0) or (p[0] == 0 and p[1] < 2))
           or p[2] < 22}
    _place(_tf(_ew, _I, 2, 24), overwrite=True)
    # main-wing west end capped by the outside-corner roof (parapet + coping)
    _place(_tf(_load_rgb(f"kit-{F}-roof-flat-corner-outside-2s-v1"), _I, 0, 0))
    for dx in (12, 24, 36):
        _t = _tf(_load_rgb(f"kit-{F}-roof-flat-2s-v1"), _I, dx, 0)
        if dx == 12:
            # no parapet or coping where the side wing joins the main wing
            _t = {p: c for p, c in _t.items()
                  if not (12 <= p[0] < 24 and 22 <= p[1] < 26 and p[2] >= 22)}
        _place(_t)
    _place(_tf(_load_rgb(f"kit-{F}-roof-flat-corner-inside-2s-v1"), _I, 0, 24))
    _place(_tf(_load_rgb(f"kit-{F}-skylight-v1"), _I, 15, 9, 22))
    _place(_tf(_load_rgb(f"kit-{F}-stairhouse-v1"), _I, 12, 38, 22))
    if FAMILY == "frame":
        # existing catalog model, seats directly on a flat roof (kit-designed)
        _place(_tf(_load_rgb("smokestack_steel_v1"), _I, 5, 24, 22))
    have = {rgb: i + 1 for i, (_, rgb) in enumerate(PALETTE)}  # 1-based like CI()
    # actual bounds: x -1..50, y -1..48 (proud coping); z 0..30 mill, 0..96 frame (smokestack)
    fp = (-1, 51, -1, 49, 0, 31) if F == "mill" else (-1, 51, -1, 49, 0, 97)
    return {p: have[c] for p, c in comp.items()}, fp


if __name__ == "__main__":
    sys.path.insert(0, _HERE)
    import kit_contract as K
    vox, fp = build_module()
    K.floater_sweep(vox)
    out = os.path.join(_GOAL, f"kit-{FAMILY}-showcase-l-v1.vox")
    K.write_vox(out, vox, PALETTE)
    K.render_preview(out.replace(".vox", "_preview.png"), vox, PALETTE, scale=3)
    print(f"showcase {FAMILY}: {len(vox)} voxels")
