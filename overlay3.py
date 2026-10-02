"""Manual-landmark overlay: exact voxel silhouettes over the new concept sheet.
Similarity transform per view from two point correspondences (nose<->tail).
"""
import numpy as np
from PIL import Image
import overlay_check as oc

REF = oc.REF

# full-image landmarks (x, y), measured from zoomed crops
LANDMARKS = {
    # view: (concept_nose, concept_tail, vox_nose_2d, vox_tail_2d, plane)
    "top":  ((648, 350), (25, 340), (0, 110), (0, -110), "xy"),
    # side: 2d coords are (y_vox, z_vox); concept x right, y down
    "side": ((498, 545), (975, 543), (110, 0), (-110, 0), "yz"),
}

def similarity(p1, p2, q1, q2):
    """Return (scale, angle, tx, ty) mapping p->q: q = s*R(a)*p + t."""
    p1, p2, q1, q2 = map(np.array, (p1, p2, q1, q2), [float]*4)
    dp, dq = p2 - p1, q2 - q1
    s = np.linalg.norm(dq) / np.linalg.norm(dp)
    a = np.arctan2(dq[1], dq[0]) - np.arctan2(dp[1], dp[0])
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    t = q1 - s * R @ p1
    return s, a, t, R

def render_mask(vmask_vox2d, s, a, R, t, out_shape):
    """vmask_vox2d: dict with 'pts' (N,2) voxel coords and implicit mask via projection.
    Simpler: take binary mask array + its voxel-coordinate grid, warp by transform."""
    pts = vmask_vox2d["pts"]          # (N,2) voxel coords
    q = s * (R @ pts.T).T + t         # (N,2) pixel coords
    h, w = out_shape
    img = np.zeros((h, w), bool)
    qi = np.round(q).astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < w) & (qi[:, 1] >= 0) & (qi[:, 1] < h)
    img[qi[ok, 1], qi[ok, 0]] = True
    return img

def main():
    ref = Image.open(REF).convert("RGB")
    full = np.array(ref)
    vox = oc.load_vox("out/gunfighter-merged-v1.vox")

    projs = {}
    for (x, y, z) in vox:
        projs.setdefault("top", []).append((x, y))
        projs.setdefault("side", []).append((y, z))
    for k in projs:
        projs[k] = {"pts": np.array(projs[k], float)}

    for view, (cn, ct, vn, vt, plane) in LANDMARKS.items():
        s, a, t, R = similarity(vn, vt, cn, ct)
        print(f"{view}: scale={s:.3f}px/vox angle={np.degrees(a):.2f}deg")
        m = render_mask(projs[view], s, a, R, t, full.shape[:2])
        rgb = (full * 0.55).astype(np.uint8)
        rgb[m] = (0, 220, 255)
        Image.fromarray(rgb).save(f"out/overlay3_{view}.png")

    # FRONT: align by intake center, scale from span
    front = dict(tip_L=(645, 225), tip_R=(1015, 225), intake_c=(825, 250))
    span_px = front["tip_R"][0] - front["tip_L"][0]
    s = span_px / 160.0
    pts = np.array([(x, z) for (x, y, z) in vox], float)  # (x_vox, z_vox)
    cx, cy = front["intake_c"]
    q = np.stack([cx + pts[:, 0] * s, cy - pts[:, 1] * s], -1)
    h, w = full.shape[:2]
    img = np.zeros((h, w), bool)
    qi = np.round(q).astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < w) & (qi[:, 1] >= 0) & (qi[:, 1] < h)
    img[qi[ok, 1], qi[ok, 0]] = True
    rgb = (full * 0.55).astype(np.uint8)
    rgb[img] = (0, 220, 255)
    Image.fromarray(rgb).save("out/overlay3_front.png")
    print(f"front: scale={s:.3f}px/vox (from span)")

if __name__ == "__main__":
    main()
