import sys
import numpy as np
from PIL import Image
from math import erf, sqrt
PX, OX, PY, OY = 8.27, 2.58, 4.445, 4.26 - 4.445
COLS, ROWS = 170, 238
def grid_from(img, sig=2.5, lam=0.02):
    a = np.asarray(img.convert('RGB')).astype(np.float64)
    Hh, Ww, _ = a.shape
    xs = np.arange(Ww) + 0.5
    b = OX + PX * np.arange(COLS + 1)
    Phi = np.vectorize(lambda z: 0.5 * (1 + erf(z / sqrt(2))))
    A = np.zeros((Ww, COLS))
    for i in range(COLS):
        A[:, i] = Phi((min(b[i + 1], Ww) - xs) / sig) - Phi((max(b[i], 0) - xs) / sig)
    AtA = A.T @ A + lam * np.eye(COLS)
    solver = np.linalg.inv(AtA) @ A.T
    out = np.zeros((ROWS, COLS, 3))
    for j in range(ROWS):
        y0, y1 = OY + PY * j, OY + PY * (j + 1)
        lo, hi = int(np.ceil(max(0, y0 + 1.0))), int(np.floor(min(Hh, y1 - 1.0)))
        if hi <= lo: lo, hi = int(max(0, (y0 + y1) / 2 - 1)), int(min(Hh, (y0 + y1) / 2 + 1))
        s = a[lo:hi].mean(axis=0)
        out[j] = solver @ s
    return out.clip(0, 255)
if __name__ == '__main__':
    g = grid_from(Image.open(sys.argv[1]))
    Image.fromarray(g.astype(np.uint8)).save(sys.argv[2])
    big = Image.fromarray(g.astype(np.uint8)).resize((COLS * 8, ROWS * 4), Image.NEAREST)
    big.save(sys.argv[3])
