"""O raio que quebra o teto (quadro 1803, plano da moça, zoom do cenário 4,245) e o estouro vermelho com a estrela amarela
do golpe na luta (quadro 576, close do herói), reduzidos à grade do cenário (célula 8,27 x 4,445 px do quadro geral).
Acrescenta 'raio' e 'impacto' em jogo/atlas/extra.json (índices da paleta; 255 = transparente)."""
import cv2, numpy as np, json, base64, os
from seg2 import FR
AQUI = os.path.dirname(os.path.abspath(__file__))
CEN = json.load(open(os.path.join(AQUI, '..', '..', 'cenario.json')))
PAL = np.array([[int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)] for h in CEN['pal']], np.float32)
CW, CH = 8.27, 4.445

def reduz(rgb, mask, s, cores, minimo=0.45):
    """rgb/mask em px do vídeo; s = px do vídeo por px do quadro geral. Cada célula: cor mediana (paleta restrita) se coberta."""
    cw, ch = CW * s, CH * s
    nx, ny = int(np.ceil(rgb.shape[1] / cw)), int(np.ceil(rgb.shape[0] / ch))
    out = np.full((ny, nx), 255, np.uint8)
    P = PAL[cores]
    for j in range(ny):
        for i in range(nx):
            y0, y1, x0, x1 = int(j * ch), int((j + 1) * ch), int(i * cw), int((i + 1) * cw)
            m = mask[y0:y1, x0:x1]
            if m.size == 0 or m.mean() < minimo: continue
            c = np.median(rgb[y0:y1, x0:x1][m], 0)
            out[j, i] = cores[int(((P - c) ** 2).sum(1).argmin())]
    return out
def recorta(a):
    ys, xs = np.nonzero(a != 255); return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

# raio: amarelo do quadro 1803 (só a parte de cima do teto); fica com a altura que tem no plano (s = 4,245)
f = cv2.imread(FR % 1803)[:, :, ::-1].astype(np.float32)
r, g, b = f[..., 0], f[..., 1], f[..., 2]
am = (r > 120) & (g > 105) & (b < 120) & (r - b > 45)
am[:, :520] = False; am[:, 1180:] = False; am[860:] = False
am = cv2.morphologyEx(am.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
raio = recorta(reduz(f, am, 4.245, [23, 30, 25, 16], 0.4))

# estouro: vermelho + estrela amarela + contorno preto do quadro 576, reduzido a ~16 células de largura
f = cv2.imread(FR % 576)[:, :, ::-1].astype(np.float32)
r, g, b = f[..., 0], f[..., 1], f[..., 2]
verm = (r > 90) & (g < 60) & (b < 60)
estrela = (r > 120) & (g > 110) & (b < 110) & (abs(r - g) < 60)
reg = np.zeros_like(verm); reg[:, 820:] = True
corpo = (verm | estrela) & reg
corpo = cv2.morphologyEx(corpo.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
n, l, st, _ = cv2.connectedComponentsWithStats(corpo, 8)
k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); corpo = l == k
contorno = (cv2.dilate(corpo.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0) & ~corpo
mask = corpo | contorno
fc = f.copy(); fc[contorno] = 0
ys, xs = np.nonzero(mask); larg = xs.max() - xs.min()
s_imp = larg / (16 * CW)
impacto = recorta(reduz(fc, mask, s_imp, [14, 18, 13, 0, 23, 30], 0.4))

b64 = lambda a: base64.b64encode(np.ascontiguousarray(a, np.uint8).tobytes()).decode()
out = os.path.join(AQUI, '..', '..', 'atlas', 'extra.json')
extra = json.load(open(out))
extra['raio'] = {'w': raio.shape[1], 'h': raio.shape[0], 'px': b64(raio)}
extra['impacto'] = {'w': impacto.shape[1], 'h': impacto.shape[0], 'px': b64(impacto)}
json.dump(extra, open(out, 'w'))
print('raio', raio.shape, 'impacto', impacto.shape)
np.save('/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/47c2caeb-864e-4102-9245-906a35f22827/scratchpad/graf.npy', dict(raio=raio, impacto=impacto), allow_pickle=True)
