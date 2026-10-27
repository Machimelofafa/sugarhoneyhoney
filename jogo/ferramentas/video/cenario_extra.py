"""Peças do cenário que se mexem no fim da fase, tiradas do plano da grade (quadros 1495-1716, zoom 3,13 do canto 676,-2
do quadro geral): o fundo sem a grade, a grade (que sobe e desce entre os dois postes) e os três estados do alçapão
(fechado, abrindo, aberto). Cada célula do cenário (170x238) é amostrada no meio da célula ampliada, a cor é corrigida
para a luz do quadro geral (ajuste linear contra células paradas do mesmo plano) e vai para a paleta do cenário.
saída: jogo/atlas/extra.json (índices da paleta em base64; 255 = transparente)"""
import cv2, numpy as np, json, base64, os
from seg2 import FR

AQUI = os.path.dirname(os.path.abspath(__file__))
CEN = json.load(open(os.path.join(AQUI, '..', '..', 'cenario.json')))
W, H = CEN['W'], CEN['H']
PAL = np.array([[int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)] for h in CEN['pal']], np.float32)
BASE = np.frombuffer(base64.b64decode(CEN['base']), np.uint8).reshape(H, W)
CW, CH, OX0, OY0 = 8.27, 4.445, 2.58, -0.185          # célula do cenário no quadro geral (ver 00-base.js)
S, OX, OY = 3.13, 676, -2                              # o plano da grade
I0, I1, J0, J1 = 82, 128, 0, 76

def celulas(n, frac=0.4):
    f = cv2.imread(FR % n)[:, :, ::-1].astype(np.float32)
    out = np.zeros((J1 - J0, I1 - I0, 3), np.float32)
    for j in range(J0, J1):
        for i in range(I0, I1):
            cx = (OX0 + (i + .5) * CW - OX) * S; cy = (OY0 + (j + .5) * CH - OY) * S
            hw, hh = CW * S * frac / 2, CH * S * frac / 2
            x0, x1, y0, y1 = max(0, int(cx - hw)), min(1408, int(cx + hw) + 1), max(0, int(cy - hh)), min(1058, int(cy + hh) + 1)
            out[j - J0, i - I0] = np.median(f[y0:y1, x0:x1].reshape(-1, 3), 0)
    return out
def paleta(rgb):
    return ((rgb[..., None, :] - PAL[None, None]) ** 2).sum(-1).argmin(-1).astype(np.uint8)
def heroi(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return ((r > 140) & (g > 90) & (r - b > 60)) | ((g > r + 25) & (g > 80)) | ((r > 120) & (r > b + 40) & (g > 60))

# correção de cor: células paradas do quadro 1495 (sem toco da grade, alçapão, esteira e herói) contra a base
raw1495 = celulas(1495)
fixas = np.ones((J1 - J0, I1 - I0), bool)
fixas[0:10, 84 - I0:102 - I0] = False; fixas[56:76, 96 - I0:126 - I0] = False
fixas[26:44, 103 - I0:128 - I0] = False; fixas[:, 90 - I0:106 - I0] = False
X = np.c_[raw1495[fixas], np.ones(fixas.sum())]
M, *_ = np.linalg.lstsq(X, PAL[BASE[J0:J1, I0:I1][fixas]], rcond=None)
def amostra(n):
    raw = celulas(n)
    c = np.clip(np.c_[raw.reshape(-1, 3), np.ones(raw.size // 3)] @ M, 0, 255).reshape(raw.shape)
    return paleta(c), heroi(raw)

from scipy.ndimage import binary_dilation
k1687, h1687 = amostra(1687); k1495, h1495 = amostra(1495)
h1687 = binary_dilation(h1687, iterations=2); h1495 = binary_dilation(h1495, iterations=2)
fundo = np.where(h1687, k1495, k1687)
fundo[h1687 & h1495] = 3                               # o herói tapava nos dois: parede azul
k_grade, _ = amostra(1716)                             # grade embaixo, herói já passou
estados = [amostra(n)[0] for n in (1698, 1704, 1716)]  # alçapão fechado, abrindo, aberto

# ---- grade: entre os postes (x 88..99), linhas 0..57 ----
GX0, GX1, GY1 = 88, 100, 58
AZUL = {1, 2, 3, 4, 5, 7, 9, 12, 15, 22}
bg = fundo[0:GY1, GX0 - I0:GX1 - I0].copy()
bg[~np.isin(bg, [0, 1, 3, 4, 12, 28, 29, 10, 6])] = 3
bg[0:6] = bg[6]                                        # o toco da grade erguida fica de fora do fundo
lat = k_grade[0:GY1, GX0 - I0:GX1 - I0].copy()
lat[np.isin(lat, list(AZUL)) & (bg != 0)] = 255
lat[np.isin(lat, list(AZUL)) & (bg == 0) & (lat != 0)] = 255

# ---- alçapão: só as células da placa mudam; o resto fica como a base ----
AX0, AX1, AY0, AY1 = 99, 124, 57, 75
VERM = [11, 13, 14, 18, 24]; BURACO = [3, 4, 12, 15, 7, 9]
st = [e[AY0:AY1, AX0 - I0:AX1 - I0] for e in estados]
uniao = np.zeros_like(st[0], bool)
for e in st: uniao |= np.isin(e, VERM + BURACO)
for a in range(3):
    for b in range(a + 1, 3): uniao |= (st[a] != st[b])
uniao[:2] = False
base = BASE[AY0:AY1, AX0:AX1]
chao = {}                                              # cor do chão por linha (moda da base fora da placa)
for j in range(AY1 - AY0):
    v = BASE[AY0 + j, 124:128]; chao[j] = int(np.bincount(v).argmax())
pecas = []
for e in st:
    p = np.where(uniao, e, 255).astype(np.uint8)
    for j in range(p.shape[0]):
        cinza = uniao[j] & np.isin(e[j], [6, 10, 19, 29, 28, 5])
        p[j][cinza] = chao[j]
    pecas.append(p)
# abas penduradas embaixo do chão (linhas 75-84) que a base traz do quadro aberto: somem com o alçapão fechado
PY0, PY1 = 73, 85
baixo = BASE[PY0:PY1, AX0:AX1]
vermelho_baixo = np.isin(baixo, VERM)
fech_baixo = np.full(baixo.shape, 255, np.uint8)
for j in range(baixo.shape[0]):
    row = baixo[j][~vermelho_baixo[j]]
    fech_baixo[j][vermelho_baixo[j]] = int(np.bincount(row).argmax()) if len(row) else 0

b64 = lambda a: base64.b64encode(np.ascontiguousarray(a, np.uint8).tobytes()).decode()
extra = {
    'grade': {'x': GX0, 'y': 0, 'w': GX1 - GX0, 'h': GY1, 'fundo': b64(bg), 'grade': b64(lat)},
    'alcapao': {'x': AX0, 'y': AY0, 'w': AX1 - AX0, 'h': AY1 - AY0, 'estados': [b64(p) for p in pecas],
                'baixo': {'y': PY0, 'h': PY1 - PY0, 'fechado': b64(fech_baixo)}},
}
out = os.path.join(AQUI, '..', '..', 'atlas', 'extra.json')
json.dump(extra, open(out, 'w'))
np.save('/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/47c2caeb-864e-4102-9245-906a35f22827/scratchpad/extra_dbg.npy', dict(bg=bg, lat=lat, pecas=pecas, fech_baixo=fech_baixo), allow_pickle=True)
print('extra.json', os.path.getsize(out), 'bytes; células da placa', int(uniao.sum()))
