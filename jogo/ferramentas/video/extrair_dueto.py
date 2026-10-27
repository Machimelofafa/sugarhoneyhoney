import numpy as np, cv2, sys, json, os
sys.path.insert(0, '.')
from seg2 import FR, S
from dueto import dueto, placa
from extrair import recorte
out = S + 'cut/dueto_duo/'; os.makedirs(out, exist_ok=True); meta = {}
for i in range(1990, 2129, 2):
    im = cv2.imread(FR % i); mk = dueto(im, None)
    if mk.sum() < 2500: continue
    rgba, box = recorte(im, mk)
    cv2.imwrite(out + f'{i:04d}.png', rgba); meta[i] = dict(box=box, area=int(mk.sum()), cortado=False)
json.dump(meta, open(out + 'meta.json', 'w')); print(len(meta), 'recortes')
