import sys
import numpy as np
from PIL import Image
from numpy.lib.stride_tricks import sliding_window_view
plate = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32)
std = np.asarray(Image.open(sys.argv[2]).convert('L')).astype(np.float32)
H, W, _ = plate.shape
axis = sys.argv[3]
if axis == 'y':
    plate = plate.transpose(1, 0, 2); std = std.T; H, W = W, H
# use every 3rd line, static pixels only
rows = np.arange(4, H - 4, 3)
P = plate[rows]          # (R, W, 3)
M = (std[rows] < 40).astype(np.float32)
x = np.arange(W) + 0.5
def gauss(sig):
    r = int(3 * sig) + 1; k = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2); return k / k.sum()
def recon_err(p, phi, sig):
    idx = np.floor((x - phi) / p).astype(int)
    idx -= idx.min()
    n = idx.max() + 1
    # cell means using only the central half of each cell
    frac = ((x - phi) / p) % 1.0
    core = (frac > 0.25) & (frac < 0.75)
    w = core.astype(np.float32)
    sums = np.zeros((P.shape[0], n, 3), np.float32); cnt = np.zeros(n, np.float32)
    np.add.at(sums, (slice(None), idx[core], slice(None)), P[:, core, :])
    np.add.at(cnt, idx[core], 1)
    cnt[cnt == 0] = 1
    means = sums / cnt[None, :, None]
    rec = means[:, idx, :]
    k = gauss(sig)
    rec = np.apply_along_axis(lambda v: np.convolve(v, k, mode='same'), 1, rec)
    e = ((rec - P) ** 2).mean(axis=2) * M
    return e[:, 20:-20].sum() / M[:, 20:-20].sum()
sig = float(sys.argv[4])
lo, hi, step = float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7])
res = []
for p in np.arange(lo, hi, step):
    best = min((recon_err(p, ph, sig), ph) for ph in np.linspace(0, p, 48, endpoint=False))
    res.append((p, best[0], best[1]))
for p, e, ph in res:
    print(f'{p:6.3f} {e:8.2f} {ph:6.2f}')
