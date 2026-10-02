"""Landmark-based overlay: exact voxel silhouettes over the new concept sheet.
Measures landmarks via scanlines, derives scale+offset per view, composites.
"""
import numpy as np
from PIL import Image
import overlay_check as oc

REF = oc.REF

def bright_runs(row, thr=95):
    """Return (start,end) runs where row > thr."""
    m = row > thr
    runs = []
    i = 0
    n = len(m)
    while i < n:
        if m[i]:
            j = i
            while j < n and m[j]:
                j += 1
            runs.append((i, j - 1))
            i = j
        else:
            i += 1
    return runs

def measure_top(g):
    h, w = g.shape
    best = None
    for y in range(280, 400):
        for (a, b) in bright_runs(g[y], 95):
            if best is None or (b - a) > (best[2] - best[1]):
                best = (y, a, b)
    y_c, tail_x, nose_x = best
    top_y, bot_y, top_x, bot_x = h, -1, 0, 0
    for x in range(180, 320):
        col = g[:, x]
        ys = np.nonzero(col > 95)[0]
        if len(ys):
            if ys.min() < top_y:
                top_y, top_x = int(ys.min()), x
            if ys.max() > bot_y:
                bot_y, bot_x = int(ys.max()), x
    return dict(y_c=y_c, nose_x=nose_x, tail_x=tail_x,
                tip_top=(top_x, top_y), tip_bot=(bot_x, bot_y))

def measure_side(g):
    h, w = g.shape
    best = None
    for y in range(80, 240):
        for (a, b) in bright_runs(g[y], 95):
            if best is None or (b - a) > (best[2] - best[1]):
                best = (y, a, b)
    y_c, nose_x, tail_x = best  # nose at left
    # fin tip: topmost bright in the fin's x-range (label sits left of it)
    fin_y, fin_x = h, 0
    for x in range(330, w):
        ys = np.nonzero(g[:, x] > 95)[0]
        if len(ys) and ys.min() < fin_y:
            fin_y, fin_x = int(ys.min()), x
    # lowest point mid-body (pod/gear)
    low_y, low_x = -1, 0
    for x in range(int(w * 0.25), int(w * 0.75)):
        ys = np.nonzero(g[:, x] > 95)[0]
        if len(ys) and ys.max() > low_y:
            low_y, low_x = int(ys.max()), x
    return dict(y_c=y_c, nose_x=nose_x, tail_x=tail_x,
                fin_tip=(fin_x, fin_y), lowest=(low_x, low_y))

def main():
    ref = Image.open(REF).convert("L")
    w, h = ref.size
    vox = oc.load_vox("out/gunfighter-merged-v1.vox")
    vm = oc.voxel_masks(vox)

    # ---- TOP ----
    top = np.array(ref.crop((0, 20, 640, 660)))
    m = measure_top(top)
    print("TOP landmarks:", m)
    length_px = m["nose_x"] - m["tail_x"]
    scale = length_px / 220.0
    vmask = vm["top"]  # [Y(-x), X(y)]
    vh, vw = vmask.shape  # 161 x 221
    vimg = Image.fromarray((vmask * 255).astype(np.uint8)).resize(
        (int(round(vw * scale)), int(round(vh * scale))), Image.NEAREST)
    v = np.array(vimg) > 128
    ch, cw = top.shape
    base = (top * 0.55).astype(np.uint8)
    rgb = np.stack([base, base, base], -1)
    # voxel (x_vox,y_vox): X_img = nose_x - scale*(110 - y_vox); Y_img = y_c - scale*x_vox
    # v array: row = (80 - x_vox)*scale, col = (y_vox+110)*scale
    oy = int(round(m["y_c"] - 80 * scale))
    ox = int(round(m["nose_x"] - 220 * scale))
    yy, xx = np.nonzero(v)
    gy, gx = yy + oy, xx + ox
    ok = (gy >= 0) & (gy < ch) & (gx >= 0) & (gx < cw)
    rgb[gy[ok], gx[ok]] = (0, 220, 255)
    Image.fromarray(rgb).save("out/overlay2_top.png")
    print(f"top: len_px={length_px} scale={scale:.3f}")

    # ---- SIDE ----
    side = np.array(ref.crop((555, 400, 1024, 665)))
    s = measure_side(side)
    print("SIDE landmarks:", s)
    slen = s["tail_x"] - s["nose_x"]
    sscale = slen / 220.0
    smask = vm["side"]  # [z, -y]: row=(z+15), col=(110-y)
    sh, sw = smask.shape
    simg = Image.fromarray((smask * 255).astype(np.uint8)).resize(
        (int(round(sw * sscale)), int(round(sh * sscale))), Image.NEAREST)
    sv = np.array(simg) > 128
    ch, cw = side.shape
    base = (side * 0.55).astype(np.uint8)
    srgb = np.stack([base, base, base], -1)
    # X_img = nose_x + scale*(110 - y_vox); col=(110-y)*s -> X = nose_x + col*s
    # Y_img = y_c - scale*z_vox; row=(z+15)*s -> z = row/s - 15 -> Y = y_c - (row - 15*s)
    oy = int(round(s["y_c"] + 15 * sscale))
    ox = int(round(s["nose_x"]))
    yy, xx = np.nonzero(sv)
    gy, gx = yy + oy, xx + ox
    ok = (gy >= 0) & (gy < ch) & (gx >= 0) & (gx < cw)
    srgb[gy[ok], gx[ok]] = (0, 220, 255)
    Image.fromarray(srgb).save("out/overlay2_side.png")
    print(f"side: len_px={slen} scale={sscale:.3f}")

main()
