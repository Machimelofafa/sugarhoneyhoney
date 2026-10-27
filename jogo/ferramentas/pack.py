import sys, json, base64
import numpy as np
from PIL import Image
d = sys.argv[1]; out = sys.argv[2]
q = np.load(d + '/q_steps.npy').astype(np.int16)
base = np.load(d + '/base_clean.npy').astype(np.int16)
pal = np.load(d + '/pal_final.npy')
S_, H, W = q.shape
b64 = lambda a: base64.b64encode(np.asarray(a, np.uint8).tobytes()).decode()

def best_shift(a, b, axis, P):
    best = None
    for s in range(P):
        e = (np.roll(b, -s, axis=axis) != a).mean()
        if best is None or e < best[0]: best = (e, s)
    return best[1]

def tile(x0, y0, x1, y1, axis, P):
    """Clean periodic tile of a straight conveyor interior, plus per-step shift."""
    crops = q[:, y0:y1, x0:x1]
    ax = 1 if axis == 'x' else 0
    shifts = [0]
    for k in range(1, S_):
        shifts.append(best_shift(crops[0], crops[k], ax, P) if False else None)
    # estimate per-step shift by aligning each step with the previous one
    sh = [0]
    for k in range(1, S_):
        a, b = crops[k - 1], crops[k]
        best = None
        for s in range(-P // 2, P // 2 + 1):
            e = (np.roll(a, s, axis=ax) != b).mean()
            if best is None or e < best[0]: best = (e, s)
        sh.append(best[1])
    vals, cts = np.unique([s for s in sh[1:] if s != 0], return_counts=True)
    step = int(vals[cts.argmax()])
    # vote the tile: phase of each cell = (pos - k*step) mod P using cumulative real shifts
    cum = np.cumsum(sh)
    n = (x1 - x0) if axis == 'x' else (y1 - y0)
    m = (y1 - y0) if axis == 'x' else (x1 - x0)
    votes = np.zeros((m, P, 32), np.int32)
    for k in range(S_):
        for p in range(n):
            ph = (p - cum[k]) % P
            col = crops[k][:, p] if axis == 'x' else crops[k][p, :]
            for r in range(m): votes[r, ph, col[r]] += 1
    t = votes.argmax(axis=2)                      # (m, P)
    return {'x': x0, 'y': y0, 'w': x1 - x0, 'h': y1 - y0, 'axis': axis, 'P': P, 'step': step, 'tile': b64(t)}, t

def period(x0, y0, x1, y1, axis, lo=8, hi=30):
    a = q[0, y0:y1, x0:x1]; ax = 1 if axis == 'x' else 0
    best = None
    for P in range(lo, hi):
        e = (np.roll(a, P, axis=ax) != a)
        e = e[:, P:].mean() if axis == 'x' else e[P:, :].mean()
        if best is None or e < best[0]: best = (e, P)
    return best[1]

conv = {}
specs = {'bottom': (45, 159, 106, 169, 'x'), 'top': (107, 37, 135, 47, 'x'), 'sign': (44, 80, 80, 91, 'x'), 'left': (11, 133, 17, 209, 'y')}
for name, (x0, y0, x1, y1, ax) in specs.items():
    P = period(x0, y0, x1, y1, ax)
    info, t = tile(x0, y0, x1, y1, ax, P)
    conv[name] = info
    print(name, 'P', P, 'step', info['step'])

def crops(x0, y0, x1, y1, frames):
    return {'x': x0, 'y': y0, 'w': x1 - x0, 'h': y1 - y0, 'frames': [b64(q[k, y0:y1, x0:x1]) for k in frames]}
layers = {
    'fire': crops(44, 168, 130, 236, range(S_)),
    'scaf': crops(84, 0, 106, 70, range(S_)),
    'ramp': crops(136, 34, 170, 102, range(S_)),
    'croc': crops(94, 100, 132, 146, [0, 1, 2, 5, 10]),
}
# hearts: red connected components inside the two panels
red = set(i for i, c in enumerate(pal) if c[0] > 120 and c[1] < 40 and c[2] < 40) | set(i for i, c in enumerate(pal) if c[0] > 70 and c[1] < 20 and c[2] < 20)
hearts = []
for (px0, px1) in [(40, 85), (105, 150)]:
    m = np.zeros((H, W), bool)
    for r in range(5, 27):
        for c in range(px0, px1):
            if base[r, c] in red: m[r, c] = True
    # split by columns into 4 groups using gaps
    colsum = m.sum(axis=0)
    groups, cur = [], []
    for c in range(px0, px1):
        if colsum[c] > 0: cur.append(c)
        elif cur: groups.append(cur); cur = []
    if cur: groups.append(cur)
    groups = sorted(groups, key=len, reverse=True)[:4]; groups.sort()
    panel = []
    for g in groups:
        cells = [[int(c), int(r)] for c in g for r in range(5, 27) if m[r, c]]
        xs = [c for c, _ in cells]; ys = [r for _, r in cells]
        around = [int(base[r, c]) for r in range(min(ys), max(ys) + 1) for c in range(min(xs), max(xs) + 1) if not m[r, c]]
        empty = int(np.bincount(around).argmax()) if around else 0
        panel.append({'cells': cells, 'empty': empty})
    hearts.append(panel)
    print('panel hearts', [len(h['cells']) for h in panel])

# the base under the croc should show the lying croc (frame 0)
c = layers['croc']
data = {'W': W, 'H': H, 'pal': ['#%02x%02x%02x' % tuple(int(v) for v in p) for p in pal],
        'base': b64(base), 'conv': conv, 'layers': layers, 'hearts': hearts}
json.dump(data, open(out, 'w'))
print('bytes', len(json.dumps(data)))
