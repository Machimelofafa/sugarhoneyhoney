"""Monta o atlas de sprites a partir dos recortes escolhidos (poses.py).
Cada recorte vem em pixels do vídeo; é reduzido pela escala z do plano até a escala do quadro geral
e depois por PX (pixels do quadro geral por pixel do atlas).
saída: atlas.png (RGBA) + atlas.json"""
import numpy as np, cv2, json, sys, os
sys.path.insert(0, '.')
from seg2 import S, hero_core
from limpa import limpa
from poses import POSES, Z, PX

def ancora_x(rgba, ator):
    a = rgba[..., 3] > 128
    ys, xs = np.where(a)
    h = ys.max() - ys.min() + 1
    if ator == 'hero':
        _, teal = hero_core(rgba[..., :3], 60); teal &= a
        ty, tx = np.where(teal)
        if len(tx) > 200:
            lim = ty.min() + 0.35 * (ty.max() - ty.min())
            return float(tx[ty <= lim].mean())
    low = ys > ys.min() + 0.5 * h
    return float(xs[low].mean()) if low.any() else float(xs.mean())

def tira_cenario(rgba, ator):
    """apaga cores que só o cenário tem e pedaços soltos (barras do cenário que a segmentação deixou):
    fio vermelho das molduras (só no vilão: o tênis do herói tem vermelho), oliva/amarelo das esteiras,
    verde do jacaré; depois some com o que ficou separado do corpo e é menor que 4% dele"""
    b, g, r = [rgba[..., k].astype(int) for k in range(3)]
    fora = ((g >= r - 8) & (g > b + 30) & (r > b + 10)) | ((g > r + 50) & (g > b + 60))
    if ator == 'vil': fora |= ((r > 60) & (r > 2 * g + 20) & (b < 70)) | ((g > r) & (g > b + 12) & (g < 90))   # + fundo oliva escuro da placa
    out = rgba.copy(); out[..., 3][fora] = 0
    a = (out[..., 3] > 128).astype(np.uint8)
    n, l, st, _ = cv2.connectedComponentsWithStats(a, 8)
    if n > 2:
        big = st[1:, cv2.CC_STAT_AREA].max()
        for c in range(1, n):
            area, w, h = st[c, cv2.CC_STAT_AREA], st[c, cv2.CC_STAT_WIDTH], st[c, cv2.CC_STAT_HEIGHT]
            if area < 0.04 * big or (area < 0.12 * big and w > 3 * h): out[..., 3][l == c] = 0   # barra deitada solta
    return out

# cor do herói por plano: cada plano do vídeo tem uma luz (o do andar é bem mais escuro), então a camisa e a calça
# mudavam de cor ao trocar de pose. Ganho por canal que leva a camisa e a calça medianas do plano às do plano de referência.
REF_COR = 'vil_hero'
def ancoras(rgba):
    gold, teal = hero_core(rgba[..., :3], 60)
    op = rgba[..., 3] > 200
    gold &= op; teal &= op
    if gold.sum() < 50 or teal.sum() < 50: return None
    return np.stack([np.median(rgba[..., :3][gold], 0), np.median(rgba[..., :3][teal], 0)])   # BGR
def ganhos_heroi():
    por_plano = {}
    for (sid, clip, quadro, face, *extra) in POSES['hero']:
        rgba = cv2.imread(S + f'cut/{clip}/{quadro:04d}.png', cv2.IMREAD_UNCHANGED)
        if rgba is None: continue
        an = ancoras(rgba)
        if an is not None: por_plano.setdefault(clip, []).append(an)
    med = {c: np.median(np.stack(v), 0) for c, v in por_plano.items()}
    ref = med[REF_COR]
    return {c: (ref * m).sum(0) / np.maximum((m * m).sum(0), 1) for c, m in med.items()}

# a moça também muda de luz de plano para plano (o da beira do vão é bem mais escuro): ganho por canal que leva o
# vestido mediano do plano ao do plano de referência (girlA)
def ganhos_moca(ref='girlA_girl'):
    por_plano = {}
    for (sid, clip, quadro, face, *extra) in POSES['girl']:
        rgba = cv2.imread(S + f'cut/{clip}/{quadro:04d}.png', cv2.IMREAD_UNCHANGED)
        if rgba is None: continue
        b, g, r = [rgba[..., k].astype(int) for k in range(3)]
        vest = (rgba[..., 3] > 200) & (r > g + 60) & (b > g + 20)
        if vest.sum() > 50: por_plano.setdefault(clip, []).append(np.median(rgba[..., :3][vest], 0))
    med = {c: np.median(np.stack(v), 0) for c, v in por_plano.items()}
    return {c: np.clip(med[ref] / np.maximum(m, 1), 0.7, 1.6) for c, m in med.items()}

def main():
    sprites = []
    ganho = ganhos_heroi()
    ganho_moca = ganhos_moca()
    for c, k in sorted(ganho_moca.items()): print('ganho de cor', c, 'BGR', np.round(k, 2))
    for c, k in sorted(ganho.items()): print('ganho de cor', c, 'BGR', np.round(k, 2))
    for ator, lista in POSES.items():
        for (sid, clip, quadro, face, *extra) in lista:
            opt = extra[0] if extra else {}
            rgba = cv2.imread(S + f'cut/{clip}/{quadro:04d}.png', cv2.IMREAD_UNCHANGED)
            if rgba is None: print('falta', clip, quadro); continue
            if opt.get('pale'):
                b_, g_, r_ = rgba[..., 0].astype(int), rgba[..., 1].astype(int), rgba[..., 2].astype(int)
                rgba = rgba.copy(); rgba[..., 3][((r_ > 190) & (g_ > 195) & (b_ < 190)) | ((r_ > 120) & (g_ >= r_ - 12) & (b_ < 150))] = 0
            if ator == 'vil':
                b_, g_, r_ = rgba[..., 0].astype(int), rgba[..., 1].astype(int), rgba[..., 2].astype(int)
                rgba = rgba.copy()
                rgba[..., 3][(g_ > r_ + 4) & (g_ > b_ + 18) & (np.maximum(np.maximum(r_, g_), b_) < 170)] = 0   # verde-oliva das molduras
            if ator == 'duo':                  # lilás das nuvens que ficou grudado no casal (vestido é magenta, calça é verde-azulada)
                b_, g_, r_ = rgba[..., 0].astype(int), rgba[..., 1].astype(int), rgba[..., 2].astype(int)
                rgba = rgba.copy(); rgba[..., 3][(b_ > r_ + 22) & (r_ > 65) & (g_ > 55) & (b_ > g_ + 30)] = 0
            if ator == 'vil' or opt.get('limpa'): rgba = limpa(rgba, opt.get('abre', 25), opt.get('regrow', 16))
            if ator in ('hero', 'vil'): rgba = tira_cenario(rgba, ator)
            if ator == 'girl' and clip in ganho_moca:
                rgba = rgba.copy(); rgba[..., :3] = np.clip(rgba[..., :3].astype(float) * ganho_moca[clip], 0, 255).astype(np.uint8)
            if ator == 'hero' and clip in ganho:
                rgba = rgba.copy(); rgba[..., :3] = np.clip(rgba[..., :3].astype(float) * ganho[clip], 0, 255).astype(np.uint8)
            a = rgba[..., 3] > 128
            ys, xs = np.where(a)
            if opt.get('flip'): rgba = rgba[:, ::-1].copy(); xs = rgba.shape[1] - 1 - xs; a = rgba[..., 3] > 128
            ax_src = ancora_x(rgba, ator) if not opt.get('flip') else rgba.shape[1] - 1 - ancora_x(cv2.imread(S + f'cut/{clip}/{quadro:04d}.png', cv2.IMREAD_UNCHANGED), ator)
            if 'ax' in opt: ax_src = opt['ax']
            y1 = ys.max() + 1
            ay_src = None
            if 'origin' in opt:            # origem fixa em px do quadro do vídeo: tira a posição relativa entre os quadros
                bx0, by0 = json.load(open(S + f'cut/{clip}/meta.json'))[str(quadro)]['box'][:2]
                ax_src = opt['origin'][0] - bx0; ay_src = opt['origin'][1] - by0
            z = opt.get('z', Z[(clip, ator)])
            f = 1.0 / (z * PX)
            x0, x1, y0, y1b = xs.min(), xs.max() + 1, ys.min(), y1
            crop = rgba[y0:y1b, x0:x1]
            w = max(1, int(round(crop.shape[1] * f))); h = max(1, int(round(crop.shape[0] * f)))
            small = cv2.resize(crop, (w, h), interpolation=cv2.INTER_AREA)
            # cor premultiplicada na redução (sem franjas): refaz a cor onde o alfa é pequeno
            sprites.append(dict(id=sid, img=small, ax=(ax_src - x0) * f, ay=(h if ay_src is None else (ay_src - y0) * f), face=face, src=f'{clip}:{quadro}', z=z))
    # empacota em prateleiras
    sprites.sort(key=lambda s: -s['img'].shape[0])
    MAXW = 1024; x = y = rowh = 0; pos = []
    for s in sprites:
        h, w = s['img'].shape[:2]
        if x + w + 1 > MAXW: x = 0; y += rowh + 1; rowh = 0
        pos.append((x, y)); x += w + 1; rowh = max(rowh, h)
    Hh = y + rowh + 1
    atlas = np.zeros((Hh, MAXW, 4), np.uint8)
    meta = {}
    for s, (px, py) in zip(sprites, pos):
        h, w = s['img'].shape[:2]
        atlas[py:py + h, px:px + w] = s['img']
        meta[s['id']] = dict(x=px, y=py, w=w, h=h, ax=round(float(s['ax']), 2), ay=round(float(s['ay']), 2), f=s['face'], src=s['src'], z=s['z'])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'atlas') + '/'; os.makedirs(out, exist_ok=True)
    cv2.imwrite(out + 'atlas.png', atlas)
    json.dump(dict(px=PX, sprites=dict(sorted(meta.items()))), open(out + 'atlas.json', 'w'), indent=0)
    print(len(meta), 'sprites; atlas', atlas.shape, 'bytes', os.path.getsize(out + 'atlas.png'))

if __name__ == '__main__': main()
