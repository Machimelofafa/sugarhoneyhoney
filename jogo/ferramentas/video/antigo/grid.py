import numpy as np
from PIL import Image
from math import erf, sqrt
PX, OX, PY, OY = 8.27, 2.58, 4.445, 4.26 - 4.445
COLS, ROWS = 170, 238
_Phi = np.vectorize(lambda z: 0.5 * (1 + erf(z / sqrt(2))))
_solver = {}
def solver(Ww, sig=2.5, lam=0.02):
    key = (Ww, sig, lam)
    if key not in _solver:
        xs = np.arange(Ww) + 0.5
        b = OX + PX * np.arange(COLS + 1)
        A = np.zeros((Ww, COLS))
        for i in range(COLS):
            A[:, i] = _Phi((min(b[i + 1], Ww) - xs) / sig) - _Phi((max(b[i], 0) - xs) / sig)
        _solver[key] = np.linalg.inv(A.T @ A + lam * np.eye(COLS)) @ A.T
    return _solver[key]
_rows = {}
def rowbands(Hh):
    if Hh not in _rows:
        r = []
        for j in range(ROWS):
            y0, y1 = OY + PY * j, OY + PY * (j + 1)
            lo, hi = int(np.ceil(max(0, y0 + 1.0))), int(np.floor(min(Hh, y1 - 1.0)))
            if hi <= lo: lo, hi = int(max(0, (y0 + y1) / 2 - 1)), int(min(Hh, (y0 + y1) / 2 + 1))
            r.append((lo, hi))
        _rows[Hh] = r
    return _rows[Hh]
def grid_from(a, sig=2.5, lam=0.02):
    """a: (H,W,3) float array -> (ROWS,COLS,3) float cell colours"""
    Hh, Ww, _ = a.shape
    S = np.stack([a[lo:hi].mean(axis=0) for lo, hi in rowbands(Hh)])   # (ROWS, W, 3)
    out = np.einsum('cw,rwk->rck', solver(Ww, sig, lam), S)
    return out.clip(0, 255)
def load(i):
    return np.asarray(Image.open(f'/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/fr/f_{i:04d}.jpg').convert('RGB')).astype(np.float64)
