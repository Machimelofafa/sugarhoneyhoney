"""O logotipo 3D do fim da abertura (quadros 2191-2251: o ponto vermelho do 'i' recua e as letras de 'despedida de
solteiro' aparecem; depois ele fica parado e escurece, o que o jogo faz sozinho). Não é mosaico: vai como JPEG pequeno,
um quadro a cada dois, numa folha de 6 colunas. saída: jogo/atlas/logo.jpg + logo.json"""
import cv2, numpy as np, json, os
from seg2 import FR
A, B, PASSO, LW, LH = 2191, 2251, 2, 400, 300
qs = list(range(A, B + 1, PASSO))
cols = 6; rows = (len(qs) + cols - 1) // cols
folha = np.zeros((rows * LH, cols * LW, 3), np.uint8)
for k, q in enumerate(qs):
    im = cv2.resize(cv2.imread(FR % q), (LW, LH), interpolation=cv2.INTER_AREA)
    folha[(k // cols) * LH:(k // cols + 1) * LH, (k % cols) * LW:(k % cols + 1) * LW] = im
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'atlas') + '/'
cv2.imwrite(out + 'logo.jpg', folha, [cv2.IMWRITE_JPEG_QUALITY, 78])
json.dump(dict(a=A, passo=PASSO, n=len(qs), w=LW, h=LH, cols=cols), open(out + 'logo.json', 'w'))
print('logo.jpg', folha.shape, os.path.getsize(out + 'logo.jpg'), 'bytes')
