#!/usr/bin/env python3
"""ASSEMBLY PROOF (not for upload): merge each rig family in its shared frame,
sweep the union for floaters vs z=0, render a combined preview, and report
part-to-part contact checks (legs<->bracing, balcony<->legs, shell<->balcony,
roof<->shell, ladder/manifold<->shell).
"""
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit_contract import LOT_PALETTE, floater_sweep, render_preview

HERE = os.path.dirname(os.path.abspath(__file__))


def load(slug):
    spec = importlib.util.spec_from_file_location(
        slug.replace("-", "_"), os.path.join(HERE, slug + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def contact(a, b):
    """True if any voxel of a is 6-adjacent to (or overlapping) b."""
    bs = set(b)
    for (x, y, z) in a:
        if (x, y, z) in bs:
            return True
        for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                  (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
            if q in bs:
                return True
    return False


def prove(name, slugs, png, checks):
    parts = {}
    union = {}
    for s in slugs:
        vox, _ = load(s).build_module()
        parts[s] = vox
        union.update(vox)   # shared frame; overlaps only where designed
    print(f"--- {name}: {len(union)} voxels in union")
    bad = floater_sweep(union)
    assert not bad, f"{name}: union has floaters!"
    for an, bn in checks:
        ok = contact(parts[an], parts[bn])
        print(f"contact {an.split('-')[-2:]} <-> {bn.split('-')[-2:]}: "
              f"{'OK' if ok else 'MISSING'}")
        assert ok, f"{name}: {an} does not touch {bn}"
    render_preview(os.path.join(HERE, png), union, LOT_PALETTE, scale=3)
    # zoomed slices through the joint zones
    from kit_contract import render_slice
    return union


WT = ["kit-lot-watertower-leg-fl-v1", "kit-lot-watertower-leg-fr-v1",
      "kit-lot-watertower-leg-rl-v1", "kit-lot-watertower-leg-rr-v1",
      "kit-lot-watertower-bracing-v1", "kit-lot-watertower-balcony-v1",
      "kit-lot-watertower-shell-v1", "kit-lot-watertower-roof-v1"]
prove("water tower", WT, "kit-lot-watertower-assembled_check.png", [
    ("kit-lot-watertower-bracing-v1", "kit-lot-watertower-leg-fl-v1"),
    ("kit-lot-watertower-bracing-v1", "kit-lot-watertower-leg-rr-v1"),
    ("kit-lot-watertower-balcony-v1", "kit-lot-watertower-leg-fl-v1"),
    ("kit-lot-watertower-shell-v1", "kit-lot-watertower-balcony-v1"),
    ("kit-lot-watertower-roof-v1", "kit-lot-watertower-shell-v1"),
])

FT = ["kit-lot-fueltank-shell-v1", "kit-lot-fueltank-roof-v1",
      "kit-lot-fueltank-ladder-v1", "kit-lot-fueltank-manifold-v1"]
prove("fuel tank", FT, "kit-lot-fueltank-assembled_check.png", [
    ("kit-lot-fueltank-roof-v1", "kit-lot-fueltank-shell-v1"),
    ("kit-lot-fueltank-ladder-v1", "kit-lot-fueltank-shell-v1"),
    ("kit-lot-fueltank-manifold-v1", "kit-lot-fueltank-shell-v1"),
])
print("ASSEMBLY PROOF PASSED")
