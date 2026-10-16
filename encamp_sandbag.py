#!/usr/bin/env python3
"""SANDBAG-family shared primitives (lite) for Strike Bay encampment set
pieces: watch post (#671), then the ammo dump and fortified checkpoint.

Every helper fills a caller-owned dict {(x, y, z): color_index} — z-up,
authored at 0.15 m per voxel (a 1.5 m soldier = 10 voxels). Colors are
passed as palette indices from the generator's own named palette, so a
generator never inherits colours it did not choose. Helpers are pure:
no module state, and deterministic given the rng the caller passes in.

Family-owned module: add, don't break — the later SANDBAG pieces (and
only those) import from here.
"""


def bag(d, x, y, z0, length, ci, ci_shade, axis="x"):
    """One sandbag: 4 long x 2 across x 2 tall (`length` overrides the run
    direction size). Rounded: the 4 top-edge corner voxels are dropped and
    the bottom course is ci_shade (self-shadow), so each bag reads as an
    individual pillow, not a plank."""
    for i in range(length):
        for j in range(2):
            px, py = (x + i, y + j) if axis == "x" else (x + j, y + i)
            d[(px, py, z0)] = ci_shade
            end = i in (0, length - 1)
            if not (end and j in (0, 1)):        # rounded top corners
                d[(px, py, z0 + 1)] = ci

def _side_bags(span, stagger):
    """(start, length) positions of 4-long bags with a 1-voxel gap between
    neighbours, covering 0..span-1; offset by `stagger` for a running bond.
    A bag that would overhang the span is trimmed, and a tail shorter than
    2 merges back into the previous bag."""
    out = []
    a = -(stagger % 5)
    while a < span:
        b = min(a + 4, span)
        a0 = max(a, 0)
        if b - a0 >= 2:
            out.append((a0, b - a0))
        elif out and b > a0:
            s0, _ = out[-1]
            out[-1] = (s0, span - s0)
        a += 5
    return out


def parapet_ring(d, x0, y0, x1, y1, z0, courses, ci, ci_shade, ci_dark=None,
                 ci_seam=None, gaps=(), from_course=0):
    """Individual-sandbag parapet around the rectangle (x0..x1, y0..y1):
    4x2x2 bags in a running bond, `courses` x 2 tall, corners interlocked
    (S/N full-length on even courses, W/E on odd). If `ci_seam` is given,
    a 1-voxel darker seam is drawn BETWEEN neighbouring bags and between
    courses (the ring stays continuous — no see-through gaps); without it
    the 1-voxel bond gaps are left as air. `gaps` are ((side, a0, a1), ..)
    spans left open — 's' the y0 face, 'n' y1 (spans in x), 'w' x0, 'e'
    x1 (spans in y) — honoured from `from_course` up. Every ~7th bag takes
    ci_dark for weathered variety."""
    for course in range(courses):
        z = z0 + 2 * course
        stag = (course * 2) % 5
        even = course % 2 == 0
        sx0, sx1 = (x0, x1) if even else (x0 + 2, x1 - 2)
        sy0, sy1 = (y0, y1) if not even else (y0 + 2, y1 - 2)
        sides = (("s", sx0, sx1, y0, "x"),
                 ("n", sx0, sx1, y1 - 1, "x"),
                 ("w", sy0, sy1, x0, "y"),
                 ("e", sy0, sy1, x1 - 1, "y"))
        for side, a0, a1, fix, ax in sides:
            gapped = [g for g in gaps if g[0] == side] if course >= from_course else []
            runs = _side_bags(a1 - a0 + 1, stag)
            for ri, (s, ln) in enumerate(runs):
                bs, be = a0 + s, a0 + s + ln - 1
                if any(g[1] <= be and g[2] >= bs for g in gapped):
                    continue
                varied = ci_dark is not None and (course * 13 + a0 + s) % 7 == 0
                tone = ci_dark if varied else (ci if ri % 2 else ci_shade)
                # courses >= 1 sit on a ci_seam bottom row: the pillow
                # self-shadow doubles as the 1-voxel seam between courses
                under = ci_seam if (ci_seam is not None and course > 0) else ci_shade
                bag(d, bs if ax == "x" else fix, bs if ax == "y" else fix,
                    z, ln, tone, under, axis=ax)
            if ci_seam is None:
                continue
            for a in range(a0, a1 + 1):       # mortar: fills the 1-voxel
                if any(g[1] <= a <= g[2] for g in gapped):   # bond gaps with
                    continue                    # ci_seam, bag faces win
                for f in (fix, fix + 1):
                    for zc in (z, z + 1):
                        p = (a, f, zc) if ax == "x" else (f, a, zc)
                        d.setdefault(p, ci_seam)


def crate_stack(d, x0, y0, ci):
    """Five hero crates: four 4x3x3 in a 2x2 grid (8x6 footprint) plus one
    4x3x3 topper centred on top. Sides alternate olive/slate (checker
    across the grid), top face #7a8b45 with a 1-voxel #a8763a band on the
    top edge only."""
    olive, slate, top, band = ci["crate_olive"], ci["crate_slate"], ci["crate_top"], ci["crate_band"]
    for gx in (0, 4):
        for gy in (0, 3):
            base = olive if (gx + gy) % 4 == 0 else slate
            crate(d, x0 + gx, y0 + gy, 1, 4, 3, 3, base, base, ci_lid=None)
            for i in range(4):                  # top face + edge band
                for j in range(3):
                    p = (x0 + gx + i, y0 + gy + j, 3)
                    d[p] = band if i in (0, 3) and j in (0, 2) else top
    crate(d, x0 + 2, y0 + 1, 4, 4, 3, 3, slate, slate, ci_lid=None)   # topper
    for i in range(4):
        for j in range(3):
            p = (x0 + 2 + i, y0 + 1 + j, 6)
            d[p] = band if i in (0, 3) and j in (0, 2) else top

def crate(d, x, y, z0, w, dep, h, ci, ci_frame, ci_lid=None):
    """Timber crate, solid: frame boards on the bottom and the four corner
    posts, plain panels between, and (optionally) a lighter lid band on the
    top course."""
    for i in range(w):
        for j in range(dep):
            for k in range(h):
                if k == 0 or (i in (0, w - 1) and j in (0, dep - 1)):
                    c = ci_frame
                elif k == h - 1 and ci_lid is not None:
                    c = ci_lid
                else:
                    c = ci
                d[(x + i, y + j, z0 + k)] = c


def ammo_can(d, x, y, z0, ci, ci_lid):
    """Small 3x2x2 ammunition can: body in ci, a lighter lid strip and a
    1-voxel handle lug on top."""
    for i in range(3):
        for j in range(2):
            for k in range(2):
                d[(x + i, y + j, z0 + k)] = ci_lid if k == 1 else ci
    d[(x + 1, y, z0 + 2)] = ci_lid


def dirt_pad(d, x0, y0, x1, y1, ci_dirt, ci_dirt_dark, ci_grass, ci_grass_dark,
             rng, fringe=3):
    """One-voxel ground pad at z=0: dirt interior with dark speckle, a
    noisy grass fringe `fringe` voxels wide, and a nibbled outer edge."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            de = min(x - x0, x1 - x, y - y0, y1 - y)
            r = rng.random()
            if de >= fringe:
                c = ci_dirt_dark if r < 0.14 else ci_dirt
            elif de >= 1:
                c = (ci_grass_dark if r < 0.35
                     else ci_grass if r < 0.85 else ci_dirt)
            else:
                if r > 0.92:
                    continue                # nibbled outer edge
                c = ci_grass_dark if r < 0.5 else ci_grass
            d[(x, y, 0)] = c


def bag_pile(d, x, y, n, ci, ci_shade, ci_dark=None):
    """A low pile of `n` sandbags at ground level: bags 4x2x2 laid along x
    with a 1-voxel gap; the 3rd bag on stacks on the 1st, so it never
    floats."""
    for i in range(n):
        if i < 2:
            bag(d, x + i * 5, y, 1, 4, ci, ci_shade)
        else:                                   # stacked on bag (i - 2)
            varied = ci_dark is not None and (x + i) % 3 == 0
            bag(d, x + (i - 2) * 5 + 1, y, 3, 3, ci_dark if varied else ci,
                ci_shade)


def grass_tuft(d, x, y, ci, ci_dark, rng):
    """A 2-3 sprig tuft standing on the pad at z=1..2."""
    for dx, dy in ((0, 0), (1, 0), (0, 1)):
        if rng.random() < 0.8:
            d[(x + dx, y + dy, 1)] = ci if rng.random() < 0.7 else ci_dark
            if rng.random() < 0.4:
                d[(x + dx, y + dy, 2)] = ci_dark


def flagpole(d, x, y, z0, z1, ci, ci_cap):
    """1x1 pole from z0 to z1-1 with a cap voxel at z1 (2x2 poles read as
    trunks at game scale)."""
    for z in range(z0, z1):
        d[(x, y, z)] = ci
    d[(x, y, z1)] = ci_cap


def flag_chevron(d, x, y, z_bot, w, h, ci_bg, ci_mark):
    """Rectangular flag `w` wide (x) by `h` tall (z), one voxel thick in y,
    flying -x away from a pole whose near face is at x+1. Solid ci_bg cloth
    with one bold chevron in ci_mark: a V of 2-thick voxels, apex at the
    free end, no other pattern."""
    ha = h // 2
    for i in range(w):
        cx = x - i                          # i=0 hangs at the pole
        arm = (w - 1 - i) // 2
        for j in range(h):
            mark = j in (ha - arm, ha + arm)
            d[(cx, y, z_bot + j)] = ci_mark if mark else ci_bg
