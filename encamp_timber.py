#!/usr/bin/env python3
"""encamp_timber.py — shared primitives for the Strike Bay encampment TIMBER family.

Supply shack, vehicle garage, comms tower (and later siblings) import from
here instead of copying code. ADD new helpers; never change existing
signatures or voxel output (later generators depend on them).

Frame contract (binding for all users):
  - z-up, 1 voxel = 0.15 m.
  - origin at the pad footprint min corner, ground level = pad top (z=1).
  - front faces file -y (min y).

Colour contract: every helper takes explicit colour *names* and a CI dict
(name -> 1-based palette index). Defaults name the standard TIMBER palette
entries; a generator whose palette uses those names can rely on defaults,
otherwise pass explicit names.

Standard TIMBER palette names: dirt, dirt_dark, grass, grass_dark, timber,
timber_dark, canvas (olive), canvas_dark, sandbag, sandbag_dark, plank,
plank_dark, roof_grey, roof_dark, metal_dark, rope.
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
        c = dark if (x % 2 == 0) else base
        for y in range(y0, y1):
            d[(x, y, z)] = CI[c]


def steps_front(d, CI, x0, x1, y_edge, z_top, n, base="plank", dark="timber_dark"):
    """Staircase descending toward -y from deck edge y_edge (deck top z_top).

    n treads, each 1 deep and 1 lower than the last. Treads are 2 thick so
    each step face reads solid. Returns the lowest tread footprint
    (y_min) for landmark use.
    """
    for i in range(n):
        zt = z_top - 1 - i
        y = y_edge - 1 - i
        box(d, CI, x0, x1, y, y_edge - i, zt - 1, zt + 1, base)
        box(d, CI, x0, x1, y, y + 1, zt - 1, zt + 1, dark)  # nosing
    return y_edge - n


def crate(d, CI, x, y, z, w=3, dpt=3, h=3, base="canvas",
          dark=None, edge="timber_dark"):
    """Solid crate w x dpt x h at min corner (x,y,z) with corner posts,
    top rim and horizontal plank shading. dark defaults to base shading
    done via edge on alternate layers.
    """
    box(d, CI, x, x + w, y, y + dpt, z, z + h, base)
    if dark is not None:
        for zz in range(z, z + h, 2):
            for xx in range(x, x + w):
                d[(xx, y, zz)] = CI[dark]
                d[(xx, y + dpt - 1, zz)] = CI[dark]
    for zz in range(z, z + h):  # corner posts
        for xx in (x, x + w - 1):
            for yy in (y, y + dpt - 1):
                d[(xx, yy, zz)] = CI[edge]
    for xx in range(x, x + w):  # top rim
        for yy in range(y, y + dpt):
            if xx in (x, x + w - 1) or yy in (y, y + dpt - 1):
                d[(xx, yy, z + h - 1)] = CI[edge]


def dirt_pad(d, CI, rng, x0, x1, y0, y1,
             dirt="dirt", dirt_dark="dirt_dark",
             grass="grass", grass_dark="grass_dark"):
    """1-thick pad (z=0, top surface z=1): dirt field with speckles and a
    1-wide irregular grass border. Corners get a jagged bite so the pad
    reads hand-placed, not stamped.
    """
    import math
    for x in range(x0, x1):
        for y in range(y0, y1):
            edge = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
            if edge == 0 and rng.random() < 0.35:
                continue  # bitten edge
            if edge <= 0:
                c = grass_dark if rng.random() < 0.5 else grass
            elif edge == 1 and rng.random() < 0.55:
                c = grass if rng.random() < 0.7 else grass_dark
            else:
                r = rng.random()
                c = dirt_dark if r < 0.18 else dirt
            d[(x, y, 0)] = CI[c]


def sandbag_row(d, CI, x0, x1, y, z, base="sandbag", dark="sandbag_dark"):
    """Single course of sandbags along x: 2-long rounded bags with dark seams."""
    for x in range(x0, x1, 2):
        box(d, CI, x, min(x + 2, x1), y, y + 1, z, z + 1, base)
        d[(min(x + 1, x1 - 1), y, z)] = CI[dark]


def sandbag_wall(d, CI, x0, x1, y, z, courses=2,
                 base="sandbag", dark="sandbag_dark"):
    """Staggered sandbag wall, courses high."""
    for c in range(courses):
        off = c % 2
        for x in range(x0 + off, x1, 2):
            box(d, CI, x, min(x + 2, x1), y, y + 1, z + c, z + c + 1, base)
        for x in range(x0, x1, 3):
            d[(x, y, z + c)] = CI[dark]


def camo_net(d, CI, rng, x0, x1, y0, y1, ztop,
             c1="canvas", c2="canvas_dark", c3="dirt_dark", sag=1):
    """Mottled camo-netting sheet over rect: height sags toward the middle
    by up to `sag` voxels. ztop(x, y) gives the frame height; the sheet
    hangs at/below it. Deterministic under rng.
    """
    cx, cy = (x0 + x1 - 1) / 2.0, (y0 + y1 - 1) / 2.0
    hx, hy = max((x1 - x0) / 2.0, 1.0), max((y1 - y0) / 2.0, 1.0)
    for x in range(x0, x1):
        for y in range(y0, y1):
            sag_here = sag - int(sag * min(1.0, ((x - cx) / hx) ** 2 + ((y - cy) / hy) ** 2))
            z = ztop(x, y) - sag_here
            r = rng.random()
            c = c1 if r < 0.45 else (c2 if r < 0.8 else c3)
            d[(x, y, z)] = CI[c]


def n_components(d):
    """Number of 6-connected components in dict d."""
    seen = set()
    n = 0
    for p in d:
        if p in seen:
            continue
        n += 1
        stack = [p]
        seen.add(p)
        while stack:
            x, y, z = stack.pop()
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                      (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in d and q not in seen:
                    seen.add(q)
                    stack.append(q)
    return n


def bbox(d):
    """((minx, miny, minz), (maxx, maxy, maxz)) inclusive."""
    xs = [p[0] for p in d]
    ys = [p[1] for p in d]
    zs = [p[2] for p in d]
    return ((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs)))

def hero_crate(d, CI, x, y, z, w, dp, h, trio):
    """Bright hero crate w x dp x h at min corner (x,y,z). trio is a
    (base, dark, lite) triple of palette names: flat base faces, 1-voxel
    dark base band, light lid layer, dark vertical corner edges.
    Min sensible size 4x3x3."""
    base, dark, lite = trio
    box(d, CI, x, x + w, y, y + dp, z, z + h, base)
    for xx in range(x, x + w):                       # dark base band
        for yy in range(y, y + dp):
            if xx in (x, x + w - 1) or yy in (y, y + dp - 1):
                d[(xx, yy, z)] = CI[dark]
    for xx in range(x, x + w):                       # light lid
        for yy in range(y, y + dp):
            d[(xx, yy, z + h - 1)] = CI[lite]
    for zz in range(z, z + h):                       # dark corner edges
        for xx in (x, x + w - 1):
            for yy in (y, y + dp - 1):
                d[(xx, yy, zz)] = CI[dark]


def shaded_wall(d, CI, x0, x1, y0, y1, z0, z1, base="timber", seam="timber_dark",
                every=3):
    """Timber/plank wall with a dark seam course every `every` layers."""
    for z in range(z0, z1):
        c = seam if (z - z0) % every == every - 1 else base
        box(d, CI, x0, x1, y0, y1, z, z + 1, c)


def knee(d, CI, x, y, z, dx, dy, n, color="timber"):
    """Diagonal knee brace: staircase of n steps from (x,y,z) toward
    (dx,dy,+1). Each step also fills the voxel below its tread so the
    brace is one 6-connected component (pure diagonals only touch at
    corners). Pass dx/dy in {-1, 0, 1} with exactly one nonzero."""
    for i in range(n):
        d[(x + dx * i, y + dy * i, z + i)] = CI[color]
        if i > 0:
            d[(x + dx * i, y + dy * i, z + i - 1)] = CI[color]

def read_vox(path):
    """Read a MagicaVoxel .vox file (stdlib only). Returns
    (vox {(x,y,z): ci0}, palette [(r,g,b) x 256], (sx,sy,sz)) where ci0
    is the 0-based index into palette. Preview compositing helper."""
    import struct
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"VOX ", path
    off = 8
    assert data[off:off + 4] == b"MAIN", path
    import struct as _s
    _clen, _chlen = _s.unpack("<ii", data[off + 4:off + 12])
    off += 12 + _clen
    end = off + _chlen
    size = None
    xyzi = None
    rgba = None
    while off < end:
        cid = data[off:off + 4]
        clen, chlen = _s.unpack("<ii", data[off + 4:off + 12])
        content = data[off + 12:off + 12 + clen]
        if cid == b"SIZE":
            size = _s.unpack("<iii", content)
        elif cid == b"XYZI":
            n = _s.unpack("<i", content[:4])[0]
            xyzi = _s.unpack("<" + "BBBB" * n, content[4:4 + 4 * n])
        elif cid == b"RGBA":
            rgba = [tuple(content[i:i + 3]) for i in range(0, 256 * 4, 4)]
        off += 12 + clen + chlen
    vox = {}
    for i in range(0, len(xyzi), 4):
        x, y, z, ci = xyzi[i:i + 4]
        vox[(x, y, z)] = ci - 1
    return vox, rgba, size


def resample(d, s):
    """Nearest-neighbour scale of {(x,y,z): v} by factor s. Returns a new
    dict; several source voxels may land on one target (last wins).
    Preview compositing helper (e.g. s = 0.09 / 0.15 to drop a 0.09 m
    vehicle into a 0.15 m scene)."""
    import math
    out = {}
    for (x, y, z), v in d.items():
        out[(math.floor(x * s), math.floor(y * s),
             math.floor(z * s))] = v
    return out
