"""Recorta cada ator de cada quadro de um plano: RGBA em pixels do vídeo (1408x1058).
uso: python extrair.py <plano> <ator> <a> <b> [<a2> <b2> ...]   (pares de intervalos de quadros)
grava cut/<plano>_<ator>/NNNN.png e cut/<plano>_<ator>/meta.json"""
import numpy as np, cv2, sys, json, os
sys.path.insert(0, '.')
from seg4 import CFGS, build_palette, segment_frame
from seg2 import FR, S
from scipy import ndimage as ndi
from cabeca import cabeca
from moca import moca
ZF = {'fire': 1.35, 'croc': 1.2, 'scaf': 1.2, 'fight': 1.05, 'vil': 1.05, 'water': 1.1, 'ur': 0.9}

def recorte(im, m, margem=6):
    ys, xs = np.where(m > 0)
    x0, x1 = max(0, xs.min() - margem), min(im.shape[1], xs.max() + 1 + margem)
    y0, y1 = max(0, ys.min() - margem), min(im.shape[0], ys.max() + 1 + margem)
    mm = m[y0:y1, x0:x1]; ii = im[y0:y1, x0:x1]
    # cor do miolo da máscara estendida para fora (sem sangrar o cenário na borda ao reduzir)
    core = cv2.erode(mm, np.ones((5, 5), np.uint8)) > 0
    if core.sum() < 50: core = mm > 0
    idx = ndi.distance_transform_edt(~core, return_distances=False, return_indices=True)
    col = ii[idx[0], idx[1]]
    a = cv2.GaussianBlur(mm.astype(np.float32), (0, 0), 1.2)
    a = np.clip((a - 0.25) / 0.5, 0, 1)
    rgba = np.dstack([col, (a * 255).astype(np.uint8)])
    return rgba, (int(x0), int(y0), int(x1), int(y1))

def main():
    plano, ator = sys.argv[1], sys.argv[2]
    nums = list(map(int, sys.argv[3:]))
    quadros = []
    for k in range(0, len(nums), 2): quadros += list(range(nums[k], nums[k + 1] + 1))
    cfg = CFGS[plano]
    pal = S + f'lab/pal_{plano}.npy'
    if ator == 'girl': cen = None
    elif os.path.exists(pal): cen = np.load(pal)
    else:
        cen = build_palette(quadros[::max(1, len(quadros) // 14)], cfg); np.save(pal, cen)
    os.makedirs(S + 'lab', exist_ok=True)
    out = S + f'cut/{plano}_{ator}/'; os.makedirs(out, exist_ok=True)
    meta = {}
    for i in quadros:
        im = cv2.imread(FR % i)
        mk = moca(im) if ator == 'girl' else segment_frame(im, cfg, cen).get(ator)
        if mk is None or mk.sum() < 2500: continue
        zf = ZF.get(plano, 1.0)
        if ator != 'girl': mk = cabeca(im, mk, up=int(200 * zf), half=int(110 * zf), minv=25)
        rgba, box = recorte(im, mk)
        ys, xs = np.where(mk > 0)
        cortado = bool(ys.min() <= 2 or ys.max() >= im.shape[0] - 3 or xs.min() <= 2 or xs.max() >= im.shape[1] - 3)
        cv2.imwrite(out + f'{i:04d}.png', rgba)
        meta[i] = dict(box=box, area=int(mk.sum()), cortado=cortado)
    json.dump(meta, open(out + 'meta.json', 'w'))
    print(plano, ator, len(meta), 'recortes')

if __name__ == '__main__': main()
