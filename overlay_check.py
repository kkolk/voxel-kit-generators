"""Overlay voxel-model silhouettes onto the concept sheet for shape parity.
Usage: python3 overlay_check.py  -> writes out/overlay_{top,front,side}.png + prints IoU.
"""
import struct
import numpy as np
from PIL import Image
from scipy import ndimage

OUT = "out"
REF = "/home/hatch/workspace/user/media_library/image/49/4983aa4d914930345d368b5192067df59c3dbcd01589be1fa9ffd3681760ebcd.jpg"

# ---------------- concept masks ----------------
def concept_mask(path):
    im = np.array(Image.open(path).convert("L"))
    fg = im > 105
    lab, n = ndimage.label(fg)
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    biggest = 1 + int(np.argmax(sizes))
    m = lab == biggest
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_opening(m, structure=np.ones((3, 3)))  # drop leader lines
    return m

# ---------------- voxel masks (exact orthographic projection) ----------------
def load_vox(path):
    data = open(path, "rb").read()
    vox = set()
    pos = 8
    # walk chunks (same simple parser as validation)
    def chunks(data, pos, end):
        out = []
        while pos < end:
            cid = data[pos:pos + 4]
            clen, chlen = struct.unpack("<ii", data[pos + 4:pos + 12])
            body = data[pos + 12:pos + 12 + clen]
            kids = chunks(data, pos + 12 + clen, pos + 12 + clen + chlen) if chlen else []
            out.append((cid, body, kids))
            pos += 12 + clen + chlen
        return out
    def walk(nodes):
        for cid, body, kids in nodes:
            if cid == b"XYZI":
                n = struct.unpack("<i", body[:4])[0]
                for i in range(n):
                    x, y, z, ci = struct.unpack("BBBB", body[4 + 4 * i:8 + 4 * i])
                    vox.add((x - 90, y - 110, z - 15))
            walk(kids)
    walk(chunks(data, 8, len(data)))
    return vox

def voxel_masks(vox):
    # top: axes (x=span, y=length). image: X=nose(+y)->right, Y=up-> -x
    top = np.zeros((181, 221), bool)   # [Y_img(-x), X_img(y)]
    front = np.zeros((56, 181), bool)  # [z, x]
    side = np.zeros((56, 221), bool)   # [z, -y] (nose left)
    for (x, y, z) in vox:
        top[90 - x, y + 110] = True
        front[z + 15, x + 90] = True
        side[z + 15, 110 - y] = True
    return {"top": top, "front": front, "side": side}

def bbox(m):
    ys, xs = np.nonzero(m)
    return ys.min(), ys.max(), xs.min(), xs.max()

def overlay_view(cmask, vmask, name):
    cy0, cy1, cx0, cx1 = bbox(cmask)
    vy0, vy1, vx0, vx1 = bbox(vmask)
    clen = cx1 - cx0
    vlen = vx1 - vx0
    scale = clen / vlen
    vh, vw = vmask.shape
    vimg = Image.fromarray((vmask * 255).astype(np.uint8)).resize(
        (max(1, int(round(vw * scale))), max(1, int(round(vh * scale)))), Image.NEAREST)
    v = np.array(vimg) > 128
    # place: bbox centers coincide
    ch, cw = cmask.shape
    canvas = np.zeros((ch, cw), bool)
    oy = int(round((cy0 + cy1) / 2 - v.shape[0] / 2))
    ox = int(round((cx0 + cx1) / 2 - v.shape[1] / 2))
    y0, y1 = max(0, oy), min(ch, oy + v.shape[0])
    x0, x1 = max(0, ox), min(cw, ox + v.shape[1])
    canvas[y0:y1, x0:x1] = v[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    inter = np.logical_and(cmask, canvas).sum()
    union = np.logical_or(cmask, canvas).sum()
    iou = inter / union
    img = np.zeros((ch, cw, 3), np.uint8)
    img[cmask & canvas] = (255, 255, 255)   # both
    img[cmask & ~canvas] = (255, 60, 60)    # concept only
    img[~cmask & canvas] = (80, 140, 255)   # voxel only
    Image.fromarray(img).save(f"{OUT}/overlay_{name}.png")
    print(f"{name}: concept_len={clen}px scale={scale:.3f}px/vox IoU={iou:.3f}")
    return iou

def main():
    ref = Image.open(REF)
    w, h = ref.size
    crops = {
        "top": (0, 0, int(w * 0.63), h),
        "front": (int(w * 0.63), 0, w, int(h * 0.52)),
        "side": (int(w * 0.63), int(h * 0.52), w, h),
    }
    vox = load_vox(f"{OUT}/gunfighter-merged-v1.vox")
    vm = voxel_masks(vox)
    for name, box in crops.items():
        c = np.array(ref.crop(box).convert("L"))
        # re-derive mask from the crop of the full-res ref (cleaner than saved png)
        fg = c > 105
        lab, n = ndimage.label(fg)
        sizes = ndimage.sum(fg, lab, range(1, n + 1))
        m = ndimage.binary_fill_holes(lab == (1 + int(np.argmax(sizes))))
        m = ndimage.binary_opening(m, structure=np.ones((3, 3)))
        Image.fromarray((m * 255).astype(np.uint8)).save(f"{OUT}/mask_{name}.png")
        overlay_view(m, vm[name], name)

if __name__ == "__main__":
    main()
