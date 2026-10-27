import numpy as np, cv2
PX, OX, PY, OY = 8.27, 2.58, 4.445, 4.26 - 4.445
def edge_profiles(img):
    g = img.astype(np.float32)
    ex = np.abs(np.diff(g, axis=1)).sum(axis=(0, 2)); ey = np.abs(np.diff(g, axis=0)).sum(axis=(1, 2))
    return ex, ey
def peaks(e, thr_rel=0.3, minsep=4):
    e = np.convolve(e, [0.25, 0.5, 0.25], mode='same')
    thr = thr_rel * np.percentile(e, 99)
    idx = [k for k in range(1, len(e) - 1) if e[k] > thr and e[k] >= e[k-1] and e[k] > e[k+1]]
    out = []
    for k in idx:   # subpixel centroid over +-2 ; boundary coordinate = k+1
        lo, hi = max(0, k - 2), min(len(e), k + 3)
        w = e[lo:hi]; c = (np.arange(lo, hi) * w).sum() / w.sum()
        out.append((c + 1.0, e[k]))
    return out
def fit_axis(e, A0, B0, iters=4, tol=0.22):
    pk = peaks(e)
    pos = np.array([p for p, _ in pk]); w = np.array([v for _, v in pk])
    A, B = A0, B0
    for _ in range(iters):
        k = np.round((pos - B) / A)
        res = pos - (A * k + B)
        ok = np.abs(res) < tol * A
        if ok.sum() < 6: break
        W = w[ok]; K = k[ok]; P = pos[ok]
        M = np.stack([K, np.ones_like(K)], 1) * np.sqrt(W)[:, None]
        sol, *_ = np.linalg.lstsq(M, P * np.sqrt(W), rcond=None)
        A, B = sol
    k = np.round((pos - B) / A); ok = np.abs(pos - (A * k + B)) < tol * A
    return A, B, int(ok.sum()), len(pos)
def coarse_AB(s, tx0, ty0):
    return PX * s, s * OX - tx0, PY * s, s * OY - ty0
def fit_frame(img, s, tx0, ty0):
    ex, ey = edge_profiles(img)
    Ax0, Bx0, Ay0, By0 = coarse_AB(s, tx0, ty0)
    # coarse B may be off by a fraction of the pitch: scan phase candidates and pick the best comb
    best = None
    for dB in np.arange(-0.5 * Ax0, 0.5 * Ax0, 1.0):
        pass
    ax = fit_axis(ex, Ax0, Bx0); ay = fit_axis(ey, Ay0, By0)
    return ax, ay
if __name__ == '__main__':
    import json
    S='/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/'
    shots = {'vil': (2.153, 180, 642), 'fight': (2.773, 510, 810), 'croc': (3.06, 2154, 1068), 'water': (3.06, 2184, 1068), 'scaf': (3.105, 2112, 0), 'girlA': (4.245, 648, 414), 'girlC': (4.245, 660, 432)}
    for name, (s, tx, ty) in shots.items():
        img = cv2.imread(S + f'lab/med_{name}.png')
        ax, ay = fit_frame(img, s, tx, ty)
        A0 = coarse_AB(s, tx, ty)
        print(name, 'x: A=%.3f B=%.2f (coarse %.2f,%.2f) inl %d/%d | y: A=%.3f B=%.2f (coarse %.2f,%.2f) inl %d/%d | ratio %.4f (ideal %.4f) sx=%.4f sy=%.4f' % (ax[0], ax[1], A0[0], A0[1], ax[2], ax[3], ay[0], ay[1], A0[2], A0[3], ay[2], ay[3], ax[0] / ay[0], PX / PY, ax[0] / PX, ay[0] / PY))
