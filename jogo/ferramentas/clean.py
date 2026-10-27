import sys
import numpy as np
from PIL import Image
d = sys.argv[1]; K = int(sys.argv[2])
G = np.load(d + '/steps.npy')             # (12, H, W, 3)
med = np.median(G, axis=0)
def srgb2lab(c):
    c = c / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
allc = np.concatenate([med.reshape(-1, 3), G.reshape(-1, 3)])
L = srgb2lab(allc)
rng = np.random.default_rng(3)
samp_i = rng.choice(len(L), 80000, replace=False); samp = L[samp_i]; samp_rgb = allc[samp_i]
C = [samp[rng.integers(len(samp))]]
for _ in range(K - 1):
    dd = np.min(((samp[:, None] - np.array(C)[None]) ** 2).sum(-1), axis=1)
    C.append(samp[rng.choice(len(samp), p=dd / dd.sum())])
C = np.array(C)
for _ in range(50):
    lab = ((samp[:, None] - C[None]) ** 2).sum(-1).argmin(1)
    C = np.array([samp[lab == i].mean(0) if (lab == i).any() else C[i] for i in range(K)])
lab = ((samp[:, None] - C[None]) ** 2).sum(-1).argmin(1)
PAL = np.array([np.median(samp_rgb[lab == i], axis=0) if (lab == i).any() else [0, 0, 0] for i in range(K)])
cnt = np.bincount(lab, minlength=K); order = np.argsort(-cnt)
C, PAL = C[order], PAL[order]
def quant(img):
    l = srgb2lab(img.reshape(-1, 3))
    return ((l[:, None] - C[None]) ** 2).sum(-1).argmin(1).reshape(img.shape[:2]).astype(np.uint8)
def despeckle(q, passes=2):
    q = q.copy(); H, W = q.shape
    for _ in range(passes):
        out = q.copy()
        for j in range(H):
            for i in range(W):
                v = q[j, i]; nb = []
                for dj in (-1, 0, 1):
                    for di in (-1, 0, 1):
                        if (dj or di) and 0 <= j + dj < H and 0 <= i + di < W: nb.append(q[j + dj, i + di])
                nb = np.array(nb)
                same = (nb == v).sum()
                if same <= 1:
                    vals, cts = np.unique(nb, return_counts=True)
                    if cts.max() >= 4: out[j, i] = vals[cts.argmax()]
        q = out
    return q
qmed = despeckle(quant(med))
qsteps = np.stack([despeckle(quant(G[s]), 1) for s in range(G.shape[0])])
np.save(d + '/pal_final.npy', PAL); np.save(d + '/q_med.npy', qmed); np.save(d + '/q_steps.npy', qsteps)
img = PAL[qmed].clip(0, 255).astype(np.uint8)
Image.fromarray(img).save(d + '/clean_med.png')
bright = (255 * (img / 255.0) ** 0.6).astype(np.uint8)
Image.fromarray(bright).resize((170 * 8, 238 * 4), Image.NEAREST).save(d + '/clean_med_bright.png')
Image.fromarray(PAL[qsteps[0]].clip(0, 255).astype(np.uint8)).resize((170 * 8, 238 * 4), Image.NEAREST).save(d + '/clean_s0_big.png')
print(' '.join('#%02x%02x%02x' % tuple(int(v) for v in c) for c in PAL))
