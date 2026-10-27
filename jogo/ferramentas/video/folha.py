"""Folha de contato dos recortes de um plano + medida de escala do herói.
uso: python folha.py <plano>_<ator> [fator] [de] [ate]"""
import numpy as np, cv2, sys, json, os
sys.path.insert(0, '.')
from seg2 import S, hero_core

def carregar(nome):
    d = S + f'cut/{nome}/'
    meta = json.load(open(d + 'meta.json'))
    return d, {int(k): v for k, v in meta.items()}

def vao_heroi(rgba):
    """distância da borda de cima da camisa (dourado) até a de baixo da calça (verde-água)"""
    bgr = rgba[..., :3]; a = rgba[..., 3] > 128
    gold, teal = hero_core(bgr, 60)
    gold &= a; teal &= a
    g = cv2.morphologyEx(gold.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)); t = cv2.morphologyEx(teal.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    if g.sum() < 200 or t.sum() < 200: return None
    gy = np.where(g.any(1))[0]; ty = np.where(t.any(1))[0]
    return int(ty.max() - gy.min()), int(g.sum())

def main():
    nome = sys.argv[1]; f = float(sys.argv[2]) if len(sys.argv) > 2 else 0.35
    de = int(sys.argv[3]) if len(sys.argv) > 3 else 0; ate = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 9
    d, meta = carregar(nome)
    tiles = []
    for i in sorted(meta):
        if not de <= i <= ate: continue
        im = cv2.imread(d + f'{i:04d}.png', cv2.IMREAD_UNCHANGED)
        if os.environ.get('LIMPA'):
            from limpa import limpa; im = limpa(im)
        im = cv2.resize(im, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
        bg = np.zeros((im.shape[0], im.shape[1], 3), np.uint8); bg[:] = (70, 20, 70)
        a = im[..., 3:4].astype(np.float32) / 255
        t = (im[..., :3] * a + bg * (1 - a)).astype(np.uint8)
        t = cv2.copyMakeBorder(t, 14, 2, 2, 2, cv2.BORDER_CONSTANT, value=(30, 10, 30))
        cv2.putText(t, f"{i}{'*' if meta[i]['cortado'] else ''}", (3, 11), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        tiles.append(t)
    rows = []; cur = []; w = 0; MAXW = 2200
    for t in tiles:
        if w + t.shape[1] > MAXW and cur: rows.append(cur); cur = []; w = 0
        cur.append(t); w += t.shape[1]
    if cur: rows.append(cur)
    imgs = []
    for r in rows:
        H = max(t.shape[0] for t in r); sh = np.zeros((H, sum(t.shape[1] for t in r), 3), np.uint8); x = 0
        for t in r: sh[:t.shape[0], x:x + t.shape[1]] = t; x += t.shape[1]
        imgs.append(sh)
    Wd = max(i.shape[1] for i in imgs); out = np.zeros((sum(i.shape[0] for i in imgs), Wd, 3), np.uint8); y = 0
    for i in imgs: out[y:y + i.shape[0], :i.shape[1]] = i; y += i.shape[0]
    cv2.imwrite(S + f'folha_{nome}.png', out); print('folha', out.shape)

if __name__ == '__main__': main()
