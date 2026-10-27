"""Recorta de novo o herói nos quadros do chute alto (614-620) e da joelhada (622-628): o recorte geral do plano da luta
(fight_hero) perdia as pernas, porque a calça nesse plano é um verde-azulado mais escuro. Grava em cut/fightk_hero/."""
import cv2, numpy as np, json, os
import seg2
from seg2 import FR, S, chans
from cabeca import cabeca

def nucleo(im, t=95):
    r, g, b = chans(im)
    gold = (r > 110) & (g > 75) & (b < 80) & ((r - g) > 18) & ((r - g) < 95) & ((g - b) > 38)
    teal = (g > r + 35) & (b > r + 15) & (g >= 55) & (b < g + 30)
    return gold, teal
seg2.hero_core = nucleo

QUADROS = [606, 610, 614, 616, 618, 620, 622, 624, 626, 628]
out = S + 'cut/fightk_hero/'; os.makedirs(out, exist_ok=True)
meta = {}
for q in QUADROS:
    im = cv2.imread(FR % q)
    m = seg2.hero_mask(im, 55, 14)
    m[:, 1180:] = 0; m[870:] = 0            # vilão à direita, letreiro embaixo
    m = cabeca(im, m.astype(np.uint8), up=140, half=95)      # cabelo e rosto (escuros demais para a regra de cor)
    m[:, 1180:] = 0; m[870:] = 0
    ys, xs = np.nonzero(m)
    x0, y0, x1, y1 = xs.min() - 5, ys.min() - 5, xs.max() + 6, ys.max() + 6
    rgba = np.dstack([im, (m * 255).astype(np.uint8)])[y0:y1, x0:x1]
    cv2.imwrite(out + f'{q:04d}.png', rgba)
    meta[str(q)] = dict(box=[int(x0), int(y0), int(x1), int(y1)], area=int(m.sum()), cortado=False)
json.dump(meta, open(out + 'meta.json', 'w'))
print('ok', len(meta))
