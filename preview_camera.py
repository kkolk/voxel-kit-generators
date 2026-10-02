"""Orthographic voxel preview with an explicit camera (position + look-at)
and a small 3-point light rig + per-voxel ambient occlusion.

Model stays on its design grid; only the preview is transformed.
"""
from PIL import Image, ImageDraw
import math


def render_camera(path, vox, PALETTE, cam_pos, look_at, up=(0, 0, 1),
                  scale=5, size=(1500, 1100), bg=(26, 34, 48)):
    def sub(a, b):
        return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

    def norm(a):
        l = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
        return (a[0] / l, a[1] / l, a[2] / l)

    def cross(a, b):
        return (a[1] * b[2] - a[2] * b[1],
                a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0])

    def dot(a, b):
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    fwd = norm(sub(look_at, cam_pos))
    right = norm(cross(fwd, up))
    upv = cross(right, fwd)

    # light rig, world space (model: x lateral, y forward, z up)
    KEY = norm((-0.45, 0.55, 0.75))    # key: upper-left-front
    FILL = norm((0.6, -0.25, 0.25))   # fill: right, weak
    RIM = norm((0.25, -0.65, 0.55))   # rim: behind-top, separates from bg
    AMBIENT = 0.38

    vset = set(vox.keys())
    shades = {i + 1: rgb for i, (_, rgb) in enumerate(PALETTE)}
    get = vset.__contains__

    # face ambient occlusion: for each exposed face, count solid voxels
    # surrounding the air cell just outside it -> crevices and slots shade
    # correctly while convex curves (fuselage sides) stay fully lit
    TANGENT = {
        (1, 0, 0): [(0, dy, dz) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
                    if (dy, dz) != (0, 0)],
        (-1, 0, 0): [(0, dy, dz) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
                     if (dy, dz) != (0, 0)],
        (0, 1, 0): [(dx, 0, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)
                    if (dx, dz) != (0, 0)],
        (0, -1, 0): [(dx, 0, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)
                     if (dx, dz) != (0, 0)],
        (0, 0, 1): [(dx, dy, 0) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                    if (dx, dy) != (0, 0)],
        (0, 0, -1): [(dx, dy, 0) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                     if (dx, dy) != (0, 0)],
    }

    F = [
        ((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
        ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
        ((0, 1, 0), [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)]),
        ((0, -1, 0), [(0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)]),
        ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
        ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]),
    ]

    cx, cy = size[0] / 2.0, size[1] / 2.0
    faces = []
    for (x, y, z) in vset:
        if (get((x + 1, y, z)) and get((x - 1, y, z)) and get((x, y + 1, z))
                and get((x, y - 1, z)) and get((x, y, z + 1)) and get((x, y, z - 1))):
            continue
        base = shades[vox[(x, y, z)]]
        for n, corners in F:
            if get((x + n[0], y + n[1], z + n[2])):
                continue
            if dot(n, fwd) >= -0.001:   # keep faces pointing at the camera
                continue
            ox, oy, oz = x + n[0], y + n[1], z + n[2]
            occ = sum(get((ox + tx, oy + ty, oz + tz))
                      for tx, ty, tz in TANGENT[n])
            ao = 1.0 - 0.08 * occ
            s = (AMBIENT
                 + 0.72 * max(0.0, dot(n, KEY))
                 + 0.28 * max(0.0, dot(n, FILL))
                 + 0.32 * max(0.0, dot(n, RIM))) * ao
            s = min(1.0, s)
            col = (min(255, int(base[0] * s)),
                   min(255, int(base[1] * s)),
                   min(255, int(base[2] * s)))
            pts = []
            dsum = 0.0
            for (ox, oy, oz) in corners:
                d = (x + ox - look_at[0], y + oy - look_at[1], z + oz - look_at[2])
                pts.append((dot(d, right) * scale + cx, -dot(d, upv) * scale + cy))
                dsum += dot(d, fwd)
            faces.append((dsum * 0.25, pts, col))

    faces.sort(key=lambda f: -f[0])  # far first (painter)
    img = Image.new("RGB", size, bg)
    dr = ImageDraw.Draw(img)
    for _, pts, col in faces:
        dr.polygon(pts, fill=col)
    img.save(path)
    print(f"wrote {path} {img.size} ({len(faces)} faces)")
