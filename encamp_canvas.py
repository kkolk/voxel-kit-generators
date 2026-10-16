#!/usr/bin/env python3
"""encamp_canvas.py — shared primitives for the Strike Bay encampment CANVAS family.

Command tent, medical tent, field kitchen (and later siblings) import from
here instead of copying code. ADD new helpers; never change existing
signatures or voxel output (later generators depend on them).

Frame contract (binding for all users):
  - z-up, 1 voxel = 0.15 m.
  - origin at the pad footprint min corner, ground level = pad top (z=1).
  - front faces file -y (min y).

Colour contract: every helper takes explicit colour *names* and a CI dict
(name -> 1-based palette index). Defaults name the standard CANVAS palette
entries; a generator whose palette uses those names can rely on defaults,
otherwise pass explicit names.

Standard CANVAS palette names: dirt, dirt_dark, grass, grass_dark, timber,
timber_dark, canvas (olive), canvas_dark, canvas_light, sandbag, sandbag_dark,
plank, plank_dark, paper, lantern, lantern_glow, rope, metal_dark.
"""

from __future__ import annotations


def box(d, CI, x0, x1, y0, y1, z0, z1, color):
    """Inclusive-exclusive box fill. d: {(x,y,z): ci}."""
    ci = CI[color]
    for x in range(int(x0), int(x1)):
        for y in range(int(y0), int(y1)):
            for z in range(int(z0), int(z1)):
                d[(x, y, z)] = ci


def pole(d, CI, x, y, z0, z1, color="timber_dark"):
    """1x1 vertical post. inclusive-exclusive z."""
    box(d, CI, x, x + 1, y, y + 1, z0, z1, color)


def beam_x(d, CI, x0, x1, y, z, color="timber_dark"):
    """1x1 beam along x at (y, z)."""
    box(d, CI, x0, x1, y, y + 1, z, z + 1, color)


def beam_y(d, CI, x, y0, y1, z, color="timber_dark"):
    """1x1 beam along y at (x, z)."""
    box(d, CI, x, x + 1, y0, y1, z, z + 1, color)


def plank_floor(d, CI, x0, x1, y0, y1, z, base="plank", dark="plank_dark"):
    """Single-layer deck with alternating plank shading along x."""
    for x in range(x0, x1):
        for y in range(y0, y1):
            d[(x, y, z)] = CI[dark if (x // 3) % 2 else base]


def crate(d, CI, x, y, z, w=3, dpt=3, h=3, base="canvas_dark",
          dark=None, edge="timber_dark"):
    """Solid crate w x dpt x h at min corner (x,y,z) with corner posts,
    top/bottom rims and a dark band. dark defaults to base (no band)."""
    if dark is None:
        dark = base
    for xx in range(x, x + w):
        for yy in range(y, y + dpt):
            for zz in range(z, z + h):
                edge_col = (xx in (x, x + w - 1)) and (yy in (y, y + dpt - 1))
                if edge_col:
                    d[(xx, yy, zz)] = CI[edge]
                elif zz in (z, z + h - 1):
                    d[(xx, yy, zz)] = CI[edge]
                else:
                    d[(xx, yy, zz)] = CI[dark if zz == z + 1 else base]
    return (x, y, z), (x + w, y + dpt, z + h)


def crate_stack(d, CI, x, y, z, rng, n, w=4, dpt=4, h=3,
                bases=("canvas_dark", "canvas", "sandbag")):
    """Stack of n crates with random palette picks; bottom sits at z.
    Returns top z (exclusive)."""
    zz = z
    for i in range(n):
        base = bases[rng.randrange(len(bases))]
        crate(d, CI, x, y, zz, w=w, dpt=dpt, h=h, base=base)
        zz += h
    return zz


def dirt_pad(d, CI, rng, x0, x1, y0, y1,
             dirt="dirt", dirt_dark="dirt_dark",
             grass="grass", grass_dark="grass_dark"):
    """1-thick pad (z=0, top surface z=1): dirt field with speckles and a
    grass fringe: a ragged ring of grass around the dirt interior."""
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    rx, ry = (x1 - x0) / 2.0, (y1 - y0) / 2.0
    for x in range(x0, x1):
        for y in range(y0, y1):
            ex = (x + 0.5 - cx) / rx
            ey = (y + 0.5 - cy) / ry
            r = (ex * ex + ey * ey) ** 0.5
            t = rng.random()
            if r > 0.80:
                c = grass_dark if t < 0.4 else grass
            elif r > 0.62 and t < 0.55:
                c = grass if t < 0.3 else grass_dark
            else:
                c = dirt_dark if t < 0.22 else dirt
            d[(x, y, 0)] = CI[c]


def sandbag_row(d, CI, x0, x1, y, z, base="sandbag", dark="sandbag_dark"):
    """Single course of sandbags along x: 2-long rounded bags with dark seams."""
    x = x0
    while x < x1 - 1:
        d[(x, y, z)] = CI[base]
        d[(x + 1, y, z)] = CI[base]
        d[(min(x + 2, x1 - 1), y, z)] = CI[dark]
        x += 3
    if (x1 - 1) not in d or d.get((x1 - 1, y, z)) is None:
        d[(x1 - 1, y, z)] = CI[base]


def sandbag_wall(d, CI, x0, x1, y, z, courses=2,
                 base="sandbag", dark="sandbag_dark"):
    """Staggered sandbag wall, courses high."""
    for c in range(z, z + courses):
        sandbag_row(d, CI, x0 + (c % 2), x1 - (c % 2), y, c, base, dark)


def guy_rope(d, CI, x0, y0, z0, x1, y1, z1, color="rope"):
    """Rope line from (x0,y0,z0) to (x1,y1,z1) as a 6-connected path:
    float-interpolated samples welded with axis-unit steps, so no voxel
    is left floating on a diagonal."""
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    steps = max(abs(dx), abs(dy), abs(dz), 1)
    sx, sy, sz = dx / steps, dy / steps, dz / steps
    pts = []
    for i in range(steps + 1):
        p = (round(x0 + sx * i), round(y0 + sy * i), round(z0 + sz * i))
        if not pts or p != pts[-1]:
            pts.append(p)
    for a, b in zip(pts, pts[1:]):
        x, y, z = a
        d[(x, y, z)] = CI[color]
        while (x, y, z) != b:
            if x != b[0]:
                x += 1 if b[0] > x else -1
            elif y != b[1]:
                y += 1 if b[1] > y else -1
            else:
                z += 1 if b[2] > z else -1
            d[(x, y, z)] = CI[color]


def stake(d, CI, x, y, z_ground=1, color="timber", color_dark="timber_dark"):
    """Small angled stake: 3-voxel peg, one voxel at ground plus two
    leaning against the rope's pull (+y)."""
    d[(x, y, z_ground)] = CI[color]
    d[(x, y + 1, z_ground)] = CI[color_dark]
    d[(x, y + 1, z_ground + 1)] = CI[color]


def flag_pole(d, CI, x, y, z0, z1, color="timber_dark"):
    """Tall wooden flagpole from z0 to z1 (exclusive), with rope bands
    near the top and a lighter cap."""
    pole(d, CI, x, y, z0, z1, color)
    top = z1 - 1
    d[(x, y, top)] = CI["timber"]
    d[(x, y, top - 4)] = CI["rope"]
    d[(x, y, top - 8)] = CI["rope"]


def n_components(d):
    """Number of 6-connected components in dict d."""
    seen = set()
    n = 0
    for p in d:
        if p in seen:
            continue
        n += 1
        stack = [p]
        while stack:
            (x, y, z) = stack.pop()
            if (x, y, z) in seen:
                continue
            seen.add((x, y, z))
            for nb in ((x+1, y, z), (x-1, y, z), (x, y+1, z),
                       (x, y-1, z), (x, y, z+1), (x, y, z-1)):
                if nb in d and nb not in seen:
                    stack.append(nb)
    return n


def bbox(d):
    """((minx, miny, minz), (maxx, maxy, maxz)) inclusive."""
    xs = [p[0] for p in d]
    ys = [p[1] for p in d]
    zs = [p[2] for p in d]
    return ((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs)))


def ground_pad(d, CI, rng, x0, x1, y0, y1,
               dirt="dirt", dirt_dark="dirt_dark",
               grass="grass", grass_dark="grass_dark"):
    """1-thick irregular pad (z=0, surface z=1): a superellipse blob
    (n=3.2) clipped to the rect, dirt interior with a ragged grass
    fringe at the edge. Rough-edged, unlike the oval dirt_pad."""
    cx, cy = (x0 + x1 - 1) / 2.0, (y0 + y1 - 1) / 2.0
    rx, ry = (x1 - x0) / 2.0, (y1 - y0) / 2.0
    for x in range(x0, x1):
        for y in range(y0, y1):
            ex = (x - cx) / rx
            ey = (y - cy) / ry
            r = (abs(ex) ** 3.2 + abs(ey) ** 3.2) ** (1.0 / 3.2)
            jitter = 0.80 + rng.random() * 0.10
            if r > jitter:
                continue
            t = rng.random()
            if r > 0.74:
                c = grass_dark if t < 0.4 else grass
            elif r > 0.58 and t < 0.55:
                c = grass if t < 0.3 else grass_dark
            else:
                c = dirt_dark if t < 0.22 else dirt
            d[(x, y, 0)] = CI[c]


def dirt_patch_pad(d, CI, rng, x0, x1, y0, y1,
                   base="dirt", dark="dirt_dark", dark2="dirt_dark2",
                   light="dirt_light", grass="grass", grass_dark="grass_dark"):
    """1-thick patchy dirt pad (z=0, surface z=1): flat 4x4-ish colour
    patches (base + 2 darker + 1 lighter) with a grass-tuft fringe at a
    ragged superellipse edge. Not per-voxel speckle."""
    cx, cy = (x0 + x1 - 1) / 2.0, (y0 + y1 - 1) / 2.0
    rx, ry = (x1 - x0) / 2.0, (y1 - y0) / 2.0
    for x in range(x0, x1):
        for y in range(y0, y1):
            ex, ey = (x - cx) / rx, (y - cy) / ry
            r = (abs(ex) ** 4 + abs(ey) ** 4) ** 0.25
            if r > 0.93 + rng.random() * 0.06:
                continue
            t = rng.random()
            if r > 0.78:                     # grass-tuft fringe
                c = grass if t < 0.5 else grass_dark
            else:                            # flat colour patches
                h = ((x // 4) * 73856093 ^ (y // 4) * 19349663) % 100
                if h < 55:
                    c = base
                elif h < 70:
                    c = dark
                elif h < 82:
                    c = dark2
                else:
                    c = light
            d[(x, y, 0)] = CI[c]
