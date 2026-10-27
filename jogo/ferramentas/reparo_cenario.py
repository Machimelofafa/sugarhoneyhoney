"""Conserta trechos do cenário-base (cenario.json) com um quadro limpo do vídeo.

O cenário-base saiu da mediana dos quadros 107-162 da abertura, em que o herói fica parado no píer: sobrou um
"fantasma" dele na água, e o chão cinza ao lado do jacaré virou verde-azulado porque a paleta não tinha cinza neutro.
O quadro 1351 (segunda vista geral) tem essas áreas limpas. Este script:
  1. acrescenta à paleta os cinzas neutros que faltam;
  2. refaz, a partir do quadro 1351 posto na grade (deblur.grid_from), os retângulos de REGIOES;
  3. grava cenario.json (as camadas animadas e as esteiras ficam como estavam).

uso: python3 reparo_cenario.py <pasta com f_NNNN.jpg> [cenario.json]
"""
import sys, json, base64
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from deblur import grid_from

FR = sys.argv[1]
ARQ = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent.parent / 'cenario.json'
QUADRO = 1351
# (x0, x1, y0, y1) em células, fim exclusivo
REGIOES = [
    (120, 170, 140, 238),   # píer e água atrás dele (o fantasma do herói)
    (118, 170, 84, 140),    # chão cinza entre o jacaré e a escada rolante
]
NOVAS = ['#1f1f22', '#303034']   # cinzas neutros do chão (medidos no quadro 1351: ~[31,32,33])


def lab(c):
    c = np.asarray(c, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def despeckle(q):
    """célula isolada (no máximo 1 vizinha igual) toma a cor que domina as 8 vizinhas"""
    H, W = q.shape
    out = q.copy()
    for j in range(H):
        for i in range(W):
            nb = [q[j + dj, i + di] for dj in (-1, 0, 1) for di in (-1, 0, 1)
                  if (dj or di) and 0 <= j + dj < H and 0 <= i + di < W]
            nb = np.array(nb)
            if (nb == q[j, i]).sum() <= 1:
                v, n = np.unique(nb, return_counts=True)
                if n.max() >= 4: out[j, i] = v[n.argmax()]
    return out


a = json.loads(ARQ.read_text())
W, H = a['W'], a['H']
for h in NOVAS:
    if h not in a['pal']: a['pal'].append(h)
pal = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in a['pal']], float)
base = np.frombuffer(base64.b64decode(a['base']), np.uint8).reshape(H, W).copy()

G = grid_from(Image.open(f'{FR}/f_{QUADRO:04d}.jpg'))
d = ((lab(G)[:, :, None, :] - lab(pal)[None, None]) ** 2).sum(-1)
q = despeckle(d.argmin(-1).astype(np.uint8))
for x0, x1, y0, y1 in REGIOES:
    base[y0:y1, x0:x1] = q[y0:y1, x0:x1]
a['base'] = base64.b64encode(base.tobytes()).decode()

# ---------- esteiras ----------
# Os ladrilhos antigos vinham de passos já borrados pelo movimento: setas escuras com uma "cauda" atrás.
# Aqui cada ladrilho é dobrado (período P) de quadros nítidos da vista geral, alinhado ao do quadro 121 e
# tirado pela mediana (atores que passam na frente somem); a seta ganha a cor clara medida no vídeo.
SETA = '#aab16d'   # ponta clara da seta, ~[170,177,109] no quadro 121
if SETA not in a['pal']: a['pal'].append(SETA)
pal = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in a['pal']], float)
QUADROS_EST = list(range(109, 163, 3))
grades = {f: grid_from(Image.open(f'{FR}/f_{f:04d}.jpg')) for f in QUADROS_EST}


def dobra(Gf, c):
    """ladrilho RGB (linhas transversais × P) dobrando a faixa da esteira no período"""
    x0, y0, w, h, P = c['x'], c['y'], c['w'], c['h'], c['P']
    faixa = Gf[y0:y0 + h, x0:x0 + w] if c['axis'] == 'x' else Gf[y0:y0 + h, x0:x0 + w].transpose(1, 0, 2)
    n = faixa.shape[1]
    return np.stack([np.median(faixa[:, p::P], axis=1) for p in range(P)], axis=1)


for nome, c in a['conv'].items():
    ref = dobra(grades[121], c)
    tiles = []
    for f in QUADROS_EST:
        t = dobra(grades[f], c)
        s_best = min(range(c['P']), key=lambda s: ((np.roll(t, s, axis=1) - ref) ** 2).sum())
        tiles.append(np.roll(t, s_best, axis=1))
    T = np.median(np.stack(tiles), axis=0)                       # (m, P, 3)
    # só as cores que uma esteira tem (fios, fundo oliva, seta e ponta): o bege da pele e o marrom ficam de fora
    cand = np.array([0, 1, 3, 5, 11, 13, 14, 16, 18, 24, 25, 23, a['pal'].index(SETA)])
    dq = cand[((lab(T)[:, :, None, :] - lab(pal[cand])[None, None]) ** 2).sum(-1).argmin(-1)].astype(np.uint8)
    # guardado como o pack.py: eixo x -> linha*P + fase; eixo y -> coluna*P + fase
    c['tile'] = base64.b64encode(dq.tobytes()).decode()
    print('esteira', nome, 'P', c['P'], 'cores', sorted(set(dq.ravel().tolist())))

# A placa do meio (setas para a direita) fica atrás do vilão em todos os quadros da vista geral; a mediana
# guarda a pele e a calça dele. Ela é a mesma seta da esteira de baixo, espelhada e descida uma linha
# (o miolo da placa tem 10 linhas, o da esteira 9).
b, sg = a['conv']['bottom'], a['conv']['sign']
assert b['P'] == sg['P'] and b['axis'] == sg['axis'] == 'x'
tb = np.frombuffer(base64.b64decode(b['tile']), np.uint8).reshape(b['h'], b['P'])[:, ::-1]
ts = np.zeros((sg['h'], sg['P']), np.uint8)
ts[0] = 11                                   # fio escuro de cima (#1d0101), como na esteira
ts[1] = tb[1]
ts[2:sg['h'] - 1] = tb[1:sg['h'] - 2]
sg['tile'] = base64.b64encode(ts.tobytes()).decode()

ARQ.write_text(json.dumps(a))
print('paleta', len(a['pal']), 'cores; regiões refeitas', REGIOES)
