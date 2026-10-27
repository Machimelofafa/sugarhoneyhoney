"""Planos fechados da abertura (rostos, tênis, água, coração) para a montagem do jogo.
Cada plano é um vídeo com efeito de mosaico de blocos fixos na tela; o passo do bloco muda de plano para plano (medido
pelo espectro das bordas, ver grade_bloco). Aqui cada quadro vira uma imagenzinha com uma cor por bloco (mediana do
miolo do bloco), tirando os letreiros brancos (os créditos voltam no jogo como texto); quadros repetidos (o vídeo segura
cada pose ~2 quadros) são guardados uma vez só.
saída: jogo/atlas/closes.png + closes.json"""
import cv2, numpy as np, json, os
from seg2 import FR

# nome, primeiro e último quadro, passo do bloco (x, y) em px do quadro 1408x1058, caixas de letreiro (x0, y0, x1, y1, q0, q1)
PLANOS = [
    ('maos',     259,  352, (16.0, 22.2),  [(560, 440, 1330, 650, 259, 280), (480, 570, 1360, 1020, 300, 352)]),
    ('impacto',  569,  598, (18.0, 26.66), []),
    ('olhos',    647,  693, (28.0, 40.0),  [(0, 820, 1408, 1058, 647, 656)]),
    ('tenis',    780,  831, (22.0, 31.3),  [(60, 70, 900, 340, 810, 831)]),
    ('sorriso',  832,  896, (18.0, 26.67), [(60, 70, 900, 340, 820, 896)]),
    ('olha',     941,  996, (16.04, 22.39), [(60, 715, 1020, 1015, 941, 996)]),
    ('agua',    1079, 1128, (12.65, 13.59), [(330, 715, 1195, 1015, 1079, 1128)]),
    ('aflicao', 1129, 1216, (16.0, 22.2),  []),
    ('rosto',   1217, 1276, (22.0, 31.12), []),
    ('surpresa', 1534, 1625, (22.0, 31.1), [(60, 745, 1020, 1015, 1560, 1625)]),
    ('rosto2',  1718, 1777, (27.14, 38.08), [(480, 10, 1408, 285, 1718, 1777)]),
    ('beira',   1778, 1892, (13.94, 17.75), [(480, 40, 1408, 345, 1800, 1892)]),
    ('cabeca',  1893, 1932, (20.0, 31.13), []),
    ('direcao', 1933, 1988, (16.0, 22.2),  [(40, 240, 1080, 760, 1933, 1988, 'espacial')]),
    ('casal',   2131, 2190, (16.0, 22.22), [(240, 330, 1165, 640, 2150, 2190, 'espacial')]),
]

def perfil(ns, eixo):
    acc = 0
    for n in ns:
        g = cv2.cvtColor(cv2.imread(FR % n), cv2.COLOR_BGR2GRAY).astype(np.float32)
        acc = acc + np.abs(np.diff(g, axis=1 - eixo)).sum(axis=eixo)
    acc = acc - cv2.GaussianBlur(np.asarray(acc, np.float32).reshape(1, -1), (0, 0), 12).ravel()
    return np.maximum(acc, 0)
def fase(p, P):
    n = len(p); best = (-1, 0)
    for f in np.arange(0, P, 0.1):
        xs = f + P * np.arange(0, n / P); xs = xs[xs < n - 1]
        i = np.floor(xs).astype(int); t = xs - i
        s = ((1 - t) * p[i] + t * p[i + 1]).mean()
        if s > best[0]: best = (s, f)
    return best[1]

def letreiro(img, caixas, q):
    """máscara do texto branco com sombra preta dentro das caixas ativas neste quadro"""
    m = np.zeros(img.shape[:2], bool)
    b, g, r = [img[..., k].astype(np.int16) for k in range(3)]
    mn, mx = np.minimum(np.minimum(r, g), b), np.maximum(np.maximum(r, g), b)
    branco = (mn > 135) & (mx - mn < 85)
    escuro = (0.3 * r + 0.59 * g + 0.11 * b) < 75                 # a sombra do letreiro (preta, ou vermelho-escura no coração)
    for (x0, y0, x1, y1, q0, q1, *_) in caixas:
        if not (q0 <= q <= q1): continue
        w = np.zeros_like(m); w[y0:y1, x0:x1] = branco[y0:y1, x0:x1]
        w = cv2.dilate(w.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        perto = cv2.dilate(w.astype(np.uint8), np.ones((23, 23), np.uint8)) > 0
        m |= w | (perto & escuro)
    return m

def amostra(img, txt, P, F, nx, ny):
    out = np.zeros((ny, nx, 3), np.float32); buraco = np.zeros((ny, nx), bool)
    for j in range(ny):
        for i in range(nx):
            x0, x1 = F[0] + (i - 1) * P[0], F[0] + i * P[0]
            y0, y1 = F[1] + (j - 1) * P[1], F[1] + j * P[1]
            cx0, cx1 = int(max(0, x0 + 0.2 * P[0])), int(min(1408, x1 - 0.2 * P[0]) + 1)
            cy0, cy1 = int(max(0, y0 + 0.2 * P[1])), int(min(1058, y1 - 0.2 * P[1]) + 1)
            if cx1 <= cx0 or cy1 <= cy0: buraco[j, i] = True; continue
            px = img[cy0:cy1, cx0:cx1].reshape(-1, 3); t = txt[cy0:cy1, cx0:cx1].ravel()
            if t.size == 0 or (~t).mean() < 0.8: buraco[j, i] = True; continue
            out[j, i] = np.median(px[~t], 0)
    return out, buraco

def main():
    planos, tiles = {}, []
    for nome, a, b, P, caixas in PLANOS:
        ns = list(range(a, b + 1))
        amostras = ns[::max(1, len(ns) // 10)]
        F = (fase(perfil(amostras, 0), P[0]), fase(perfil(amostras, 1), P[1]))
        # blocos que cobrem a tela: o primeiro começa em F - P
        nx = int(np.ceil((1408 - F[0]) / P[0])) + 1; ny = int(np.ceil((1058 - F[1]) / P[1])) + 1
        # o letreiro entra e sai em fusão: a máscara de cada caixa é a união dos quadros em que ele aparece,
        # aplicada também a alguns quadros antes e depois
        unioes = []
        so_espacial = any(len(cx) > 6 for cx in caixas)       # o fundo muda demais (coração crescendo): só os vizinhos
        for cx in caixas:
            u = np.zeros((1058, 1408), bool)
            for q in range(max(a, cx[4]), min(b, cx[5]) + 1): u |= letreiro(cv2.imread(FR % q), [cx], q)
            unioes.append((cv2.dilate(u.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0, cx[4] - 12, cx[5] + 12))
        quadros, bur = [], []
        for q in ns:
            img = cv2.imread(FR % q)
            txt = np.zeros((1058, 1408), bool)
            for u, q0, q1 in unioes:
                if q0 <= q <= q1: txt |= u
            o, h = amostra(img, txt, P, F, nx, ny)
            quadros.append(o); bur.append(h)
        # buracos do letreiro: o mesmo bloco no quadro mais próximo sem letreiro; senão, os vizinhos
        Q = np.stack(quadros); B = np.stack(bur)
        for k in range(len(ns)):
            if not so_espacial:
                for j, i in zip(*np.nonzero(B[k])):
                    ok = np.nonzero(~B[:, j, i])[0]
                    if len(ok): Q[k, j, i] = Q[ok[np.argmin(abs(ok - k))], j, i]; B[k, j, i] = False
            if B[k].any():                                      # descasca o buraco da borda para dentro e depois alisa
                h = B[k].copy(); img = Q[k].copy(); feito = ~h
                viz4 = lambda a: sum(np.roll(a, d, ax) for d in (1, -1) for ax in (0, 1))
                while not feito.all():
                    pv = viz4(feito.astype(np.float32)); soma = viz4(img * feito[..., None])
                    novo = (~feito) & (pv > 0)
                    if not novo.any(): break
                    img[novo] = soma[novo] / pv[novo][:, None]; feito |= novo
                for _ in range(60):
                    img[h] = (viz4(img) / 4)[h]
                Q[k][h] = img[h]; B[k][:] = False
        # quadros repetidos
        idx, unicos = [], []
        for k in range(len(ns)):
            # repetido = quase nenhum bloco mudou de verdade (o resto é ruído da compressão)
            if unicos and (np.abs(Q[k] - unicos[-1]).max(-1) > 12).mean() < 0.0025: idx.append(len(unicos) - 1); continue
            unicos.append(Q[k]); idx.append(len(unicos) - 1)
        base = len(tiles)
        tiles += [np.clip(u, 0, 255).astype(np.uint8) for u in unicos]
        planos[nome] = dict(a=a, b=b, P=[round(P[0], 3), round(P[1], 3)], F=[round(F[0] - P[0], 2), round(F[1] - P[1], 2)],
                            nx=nx, ny=ny, q=[base + i for i in idx])
        print(nome, a, b, 'P', P, 'fase', [round(F[0], 1), round(F[1], 1)], 'blocos', nx, ny, 'únicos', len(unicos), 'de', len(ns))
    # empacota em prateleiras
    MAXW = 1024; x = y = rowh = 0; pos = []
    for t in tiles:
        h, w = t.shape[:2]
        if x + w > MAXW: x = 0; y += rowh; rowh = 0
        pos.append((x, y)); x += w; rowh = max(rowh, h)
    sheet = np.zeros((y + rowh, MAXW, 3), np.uint8)
    for t, (px, py) in zip(tiles, pos): sheet[py:py + t.shape[0], px:px + t.shape[1]] = t
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'atlas') + '/'
    from PIL import Image
    im = Image.fromarray(sheet[:, :, ::-1]).quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(out + 'closes.png', optimize=True)
    json.dump(dict(planos=planos, pos=pos), open(out + 'closes.json', 'w'), separators=(',', ':'))
    print('closes.png', sheet.shape, os.path.getsize(out + 'closes.png'), 'bytes;', len(tiles), 'quadros')

if __name__ == '__main__': main()
