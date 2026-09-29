#!/usr/bin/env python3
"""Ortho multi-view z-buffer renderer for .vox (x lateral, y forward, z up).

usage: render_views.py out.png a.vox [b.vox ...]   (files merged)
Renders side / front / top / 3-quarter views in one sheet.
"""
import struct
import sys
import math
import os
import numpy as np
from PIL import Image

def read_vox(path):
    b = open(path, "rb").read()
    pos = 8
    xyzi = None
    pal = None
    def walk(pos, end):
        nonlocal xyzi, pal
        while pos < end:
            cid, n, m = struct.unpack_from("<4sii", b, pos)
            data = pos + 12
            if cid == b"XYZI":
                cnt = struct.unpack_from("<i", b, data)[0]
                xyzi = np.frombuffer(b, dtype=np.uint8, count=cnt * 4, offset=data + 4).reshape(cnt, 4)
            elif cid == b"RGBA":
                pal = np.frombuffer(b, dtype=np.uint8, count=1024, offset=data).reshape(256, 4)
            if cid == b"MAIN":
                walk(data + n, data + n + m)
            pos = data + n + m
    walk(pos, len(b))
    return xyzi, pal

def render(pts, cols, yaw, pitch, scale, light=(0.4, -0.5, 0.75)):
    """pts Nx3 float (x,y,z); yaw about z, pitch tilt. returns RGB image."""
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
    # rotate about z
    x1 = x * cy - y * sy
    y1 = x * sy + y * cy
    # tilt: camera looks along +y1 after pitch; screen u = x1, v = z*cp + y1*sp
    u = x1
    v = z * cp - y1 * sp
    d = y1 * cp + z * sp  # depth, smaller = closer
    u = (u - u.min()) * scale
    v = (v.max() - v) * scale
    W, H = int(u.max()) + int(scale) + 6, int(v.max()) + int(scale) + 6
    zb = np.full((H, W), 1e9)
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (28, 46, 74)
    order = np.argsort(-d)  # far first, near overwrites
    k = max(int(math.ceil(scale)), 1)
    ui = u.astype(int) + 3
    vi = v.astype(int) + 3
    for i in order:
        img[vi[i]:vi[i] + k, ui[i]:ui[i] + k] = cols[i]
    return img

def shade(vset_arr, cols):
    """simple ambient occlusion-ish: darken voxels by empty-neighbour count facing away."""
    return cols

def main():
    out = sys.argv[1]
    allp, allc = [], []
    for f in sys.argv[2:]:
        xyzi, pal = read_vox(f)
        hide = [int(v) for v in os.environ.get('HIDE', '').split(',') if v]
        if hide:
            xyzi = xyzi[~np.isin(xyzi[:, 3], hide)]
        allp.append(xyzi[:, :3].astype(float))
        allc.append(pal[xyzi[:, 3].astype(int) - 1][:, :3])
    pts = np.concatenate(allp)
    cols = np.concatenate(allc).astype(float)
    # centre x
    pts[:, 0] -= (pts[:, 0].min() + pts[:, 0].max()) / 2
    # face shading: per voxel brightness from occupancy of neighbours (top-lit)
    occ = {tuple(p) for p in pts.astype(int)}
    br = np.ones(len(pts))
    for i, p in enumerate(pts.astype(int)):
        t = tuple(p)
        if (t[0], t[1], t[2] + 1) in occ:
            br[i] -= 0.22
        if (t[0], t[1] + 1, t[2]) in occ:
            br[i] -= 0.10
        if (t[0] + 1, t[1], t[2]) in occ and (t[0] - 1, t[1], t[2]) in occ:
            br[i] -= 0.05
    cols = np.clip(cols * br[:, None], 0, 255).astype(np.uint8)
    views = [
        ("side", math.radians(90), 0.0),     # looking from +x side (nose left/right)
        ("front", math.radians(180), 0.0),
        ("top", math.radians(90), math.radians(-89)),
        ("3q", math.radians(140), math.radians(-25)),
        ("3q-rear", math.radians(40), math.radians(-25)),
    ]

    scale = float(os.environ.get('SCALE','2.2'))
    imgs = [render(pts, cols, yaw, pitch, scale) for _, yaw, pitch in views]
    H = max(i.shape[0] for i in imgs)
    W = sum(i.shape[1] for i in imgs[:3]) + 20
    # layout: row1 side | row2 front, top, 3q
    row1 = [imgs[0], imgs[3], imgs[4]]
    row2 = [imgs[1], imgs[2]]
    def hcat(ims):
        h = max(i.shape[0] for i in ims)
        w = sum(i.shape[1] for i in ims) + 8 * len(ims)
        c = np.zeros((h, w, 3), np.uint8); c[:] = (28, 46, 74)
        x = 0
        for i in ims:
            c[:i.shape[0], x:x + i.shape[1]] = i; x += i.shape[1] + 8
        return c
    r1, r2 = hcat(row1), hcat(row2)
    w = max(r1.shape[1], r2.shape[1])
    sheet = np.zeros((r1.shape[0] + r2.shape[0] + 8, w, 3), np.uint8); sheet[:] = (28, 46, 74)
    sheet[:r1.shape[0], :r1.shape[1]] = r1
    sheet[r1.shape[0] + 8:, :r2.shape[1]] = r2
    Image.fromarray(sheet).save(out)
    print(out, sheet.shape)

main()
