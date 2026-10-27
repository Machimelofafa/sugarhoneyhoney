import numpy as np, cv2, sys
sys.path.insert(0,'.')
from seg2 import chans
def cabeca(im, m, up=150, half=100, minv=12, down=30, crimson=False):
    """acrescenta cabelo + rosto logo acima do ponto mais alto da máscara (cabelo/pele são tons quentes;
    cenário é azul/roxo/preto/verde/vermelho-vivo)"""
    ys, xs = np.where(m > 0)
    if len(ys) == 0: return m
    y0 = ys.min()
    top = m[y0:y0 + 36]; tx = np.where(top.any(0))[0]
    cx = int(np.median(tx)) if len(tx) else int(xs.mean())
    X0, X1 = max(0, cx - half), min(im.shape[1], cx + half)
    Y0, Y1 = max(0, y0 - up), min(im.shape[0], y0 + down)
    r, g, b = chans(im)
    sub = lambda a: a[Y0:Y1, X0:X1]
    r, g, b = sub(r), sub(g), sub(b)
    v = np.maximum(np.maximum(r, g), b)
    warm = (r > g + 6) & (g >= b - 8) & (v >= minv) & (v < 235)
    # cinza-escuro do cenário (r~g~b) e vermelho-vivo das molduras ficam de fora
    warm &= ~((r > 150) & (g < 70) & (b < 80))
    warm &= ~((g < 14) & (r > 50))      # vermelho escuro dos corações do painel
    if not crimson: warm &= ~((b > g + 3) & (r > g + 35))      # carmim dos corações (cabelo e pele do herói têm b <= g)
    if not crimson: warm &= ~((g * 10 < r * 3) & (r > 60))      # vermelho-tijolo do contorno dos corações (cabelo tem g/r ~ 0,45)
    cand = warm.astype(np.uint8)
    cand = cv2.morphologyEx(cand, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    cand = cv2.morphologyEx(cand, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    mm = m[Y0:Y1, X0:X1]
    seed = cv2.dilate(mm, np.ones((9, 9), np.uint8))
    n, l, st, _ = cv2.connectedComponentsWithStats(cand, 8)
    keep = np.zeros_like(cand)
    for k in range(1, n):
        sel = l == k
        w, h, a = st[k, cv2.CC_STAT_WIDTH], st[k, cv2.CC_STAT_HEIGHT], st[k, cv2.CC_STAT_AREA]
        if (seed[sel] > 0).sum() >= 15 and a > 300 and w < 2 * half * 0.9 and h < up + 20: keep[sel] = 1
    # só a faixa acima do topo da máscara + um pouco para dentro
    keep[(Y0 + np.arange(Y1 - Y0)) > y0 + down, :] = 0
    out = m.copy(); out[Y0:Y1, X0:X1] |= keep
    out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    cnt, _ = cv2.findContours(out, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    f = np.zeros_like(out); cv2.drawContours(f, cnt, -1, 1, -1)
    return f
girl_head = cabeca
