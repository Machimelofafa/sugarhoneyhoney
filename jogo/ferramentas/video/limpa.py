import numpy as np, cv2
def limpa(rgba, abre=25, regrow=16):
    """tira estruturas finas (barras do cenário) da máscara: abertura grande + reconstrução curta, só o maior corpo"""
    a = (rgba[..., 3] > 128).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (abre, abre))
    op = cv2.morphologyEx(a, cv2.MORPH_OPEN, k)
    if op.sum() == 0: return rgba
    rec = op.copy()
    kk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    for _ in range(regrow): rec = cv2.dilate(rec, kk) & a
    n, l, st, _ = cv2.connectedComponentsWithStats(rec, 8)
    if n > 2:
        big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
        keep = np.zeros_like(rec)
        for c in range(1, n):
            if st[c, cv2.CC_STAT_AREA] >= 0.12 * st[big, cv2.CC_STAT_AREA]: keep[l == c] = 1
        rec = keep
    out = rgba.copy()
    soft = cv2.GaussianBlur(rec.astype(np.float32), (0, 0), 1.2)
    out[..., 3] = (np.minimum(rgba[..., 3] / 255.0, np.clip((soft - 0.25) / 0.5, 0, 1)) * 255).astype(np.uint8)
    return out
