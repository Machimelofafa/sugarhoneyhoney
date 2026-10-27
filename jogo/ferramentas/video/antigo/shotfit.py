import cv2, numpy as np, sys, json
S='/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/'
FR=S+'fr/f_%04d.jpg'
def median_img(idx):
    st = np.stack([cv2.imread(FR % i) for i in idx])
    return np.median(st, axis=0).astype(np.uint8)
def profiles(img):
    g = img.astype(np.float32)
    ex = np.abs(np.diff(g, axis=1)).sum(axis=(0, 2)); ey = np.abs(np.diff(g, axis=0)).sum(axis=1).sum(axis=1)
    return ex, ey
def comb_obj(e, p, phs):
    n = len(e); es = np.convolve(e, [0.25, 0.5, 0.25], mode='same')
    best = (-1, 0)
    for ph in phs:
        pos = np.arange(ph, n - 1, p)
        idx = np.clip(np.round(pos).astype(int), 0, n - 1)
        sc = es[idx].mean()
        if sc > best[0]: best = (sc, ph)
    return best
def fit_shot(img, s0, rel=0.04, PX=8.27, PY=4.445, ds=0.001):
    ex, ey = profiles(img)
    ex /= ex.mean(); ey /= ey.mean()
    res = []
    for s in np.arange(s0 * (1 - rel), s0 * (1 + rel), s0 * ds):
        px, py = PX * s, PY * s
        bx = comb_obj(ex, px, np.arange(0, px, 0.5))
        by = comb_obj(ey, py, np.arange(0, py, 0.5))
        res.append((bx[0] + by[0], s, bx, by))
    res.sort(key=lambda t: -t[0])
    return res
def fit_xy(img, sx0, sy0, rel=0.04, PX=8.27, PY=4.445, ds=0.001):
    ex, ey = profiles(img); ex /= ex.mean(); ey /= ey.mean()
    rx = []; 
    for s in np.arange(sx0 * (1 - rel), sx0 * (1 + rel), sx0 * ds):
        p = PX * s; b = comb_obj(ex, p, np.arange(0, p, 0.5)); rx.append((b[0], s, b[1]))
    ry = []
    for s in np.arange(sy0 * (1 - rel), sy0 * (1 + rel), sy0 * ds):
        p = PY * s; b = comb_obj(ey, p, np.arange(0, p, 0.5)); ry.append((b[0], s, b[1]))
    rx.sort(key=lambda t: -t[0]); ry.sort(key=lambda t: -t[0])
    return rx[:3], ry[:3]
if __name__ == '__main__':
    shots = {'vil': (range(358, 425, 2), 2.16), 'fight': (range(490, 570, 2), 2.76), 'croc': (range(694, 779, 2), 3.05), 'water': (range(1084, 1127, 2), 3.04),
             'scaf': (list(range(1492, 1529, 2)) + list(range(1630, 1715, 3)), 3.12), 'girlB': (range(1372, 1488, 3), 4.26), 'girlC': (range(1780, 1890, 3), 4.32), 'girlA': (range(428, 488, 3), 4.24)}
    for name, (idx, s0) in shots.items():
        m = median_img(list(idx)); cv2.imwrite(S + f'lab/med_{name}.png', m)
        rx, ry = fit_xy(m, s0, s0, rel=0.05)
        print(name, 'x:', [(round(sc, 2), round(s, 4), ph) for sc, s, ph in rx[:2]], ' y:', [(round(sc, 2), round(s, 4), ph) for sc, s, ph in ry[:2]], flush=True)
