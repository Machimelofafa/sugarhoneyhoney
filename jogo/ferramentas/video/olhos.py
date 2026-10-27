"""Faixa dos olhos da abertura (quadros 30-102) para a tela-título: em vez de olhos desenhados em código,
as cores dos blocos do mosaico do próprio vídeo.

Medido no recorte 1408×1058: fios vermelhos nas linhas 289-323 e 722-757, miolo 324-721; o mosaico dos olhos
tem blocos de 27,95 × 39,8 px (passo achado por Fourier nos gradientes) com origem em x = 5,55 e y = 324 + 36,05.
Saída: jogo/atlas/olhos.png (um quadro por faixa de NY linhas, NX blocos por linha) + olhos.json.
uso: TRABALHO=... python3 olhos.py
"""
import json, os
import numpy as np
from PIL import Image

S = os.environ.get('TRABALHO', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trabalho')) + '/'
QUADROS = [50, 38, 62, 78, 98]      # olhando à frente, para um lado, à frente, para o outro, à frente
Y0, Y1 = 324, 722                   # miolo da faixa (entre os fios vermelhos)
PX, PY = 27.95, 39.8
OX, OY = 5.55 - PX, 36.05 - PY      # canto do primeiro bloco (parcial) em relação a (0, Y0)
NX = int(np.ceil((1408 - OX) / PX)); NY = int(np.ceil((Y1 - Y0 - OY) / PY))

fatias = []
for q in QUADROS:
    a = np.asarray(Image.open(S + f'fr/f_{q:04d}.jpg').convert('RGB')).astype(float)[Y0:Y1]
    H, W, _ = a.shape
    b = np.zeros((NY, NX, 3), np.uint8)
    for j in range(NY):
        y0, y1 = OY + j * PY, OY + (j + 1) * PY
        cy0, cy1 = max(0, int(y0 + PY * 0.3)), min(H, int(y1 - PY * 0.3))
        if cy1 <= cy0: cy0, cy1 = max(0, int(y0)), min(H, int(y1))
        for i in range(NX):
            x0, x1 = OX + i * PX, OX + (i + 1) * PX
            cx0, cx1 = max(0, int(x0 + PX * 0.3)), min(W, int(x1 - PX * 0.3))
            if cx1 <= cx0: cx0, cx1 = max(0, int(x0)), min(W, int(x1))
            if cy1 > cy0 and cx1 > cx0: b[j, i] = np.median(a[cy0:cy1, cx0:cx1].reshape(-1, 3), 0)
    fatias.append(b)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'atlas')
Image.fromarray(np.concatenate(fatias, 0)).save(os.path.join(out, 'olhos.png'))
json.dump({'quadros': QUADROS, 'nx': NX, 'ny': NY, 'px': PX, 'py': PY, 'ox': OX, 'oy': OY, 'y0': Y0, 'y1': Y1,
           'fio': [[289, 323], [722, 757]]}, open(os.path.join(out, 'olhos.json'), 'w'))
print('olhos:', len(QUADROS), 'quadros de', NX, 'x', NY, 'blocos')
