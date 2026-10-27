import json, base64
import numpy as np
from PIL import Image
PX, OX, PY, OY = 8.27, 2.58, 4.445, 4.26 - 4.445
COLS, ROWS = 170, 238
CEN = json.load(open('/home/davi/projects/despedida-de-solteiro/jogo/cenario.json'))
PAL = np.array([[int(h[i:i+2], 16) for i in (1, 3, 5)] for h in CEN['pal']], np.uint8)
def b64(s): return np.frombuffer(base64.b64decode(s), np.uint8)
BASE = b64(CEN['base']).reshape(ROWS, COLS)
def scene_idx(k, croc=0):
    """palette-index image (238x170) of the scenery at animation step k"""
    g = BASE.copy()
    for name in ('scaf', 'ramp', 'fire'):
        L = CEN['layers'][name]
        fr = b64(L['frames'][k % len(L['frames'])]).reshape(L['h'], L['w'])
        g[L['y']:L['y']+L['h'], L['x']:L['x']+L['w']] = fr
    for name, c in CEN['conv'].items():
        t = b64(c['tile']); P = c['P']; shift = (k * c['step']) % P
        if c['axis'] == 'x':
            t = t.reshape(c['h'], P)
            idx = (np.arange(c['w']) - shift) % P
            g[c['y']:c['y']+c['h'], c['x']:c['x']+c['w']] = t[:, idx]
        else:
            t = t.reshape(c['w'], P)
            idx = (np.arange(c['h']) - shift) % P
            g[c['y']:c['y']+c['h'], c['x']:c['x']+c['w']] = t[:, idx].T
    L = CEN['layers']['croc']
    fr = b64(L['frames'][croc]).reshape(L['h'], L['w'])
    g[L['y']:L['y']+L['h'], L['x']:L['x']+L['w']] = fr
    return g
def scene_rgb(k, croc=0):
    return PAL[scene_idx(k, croc)]
def to_px(cells, W=1408, H=1058):
    xs = np.clip(np.floor((np.arange(W) + 0.5 - OX) / PX).astype(int), 0, COLS - 1)
    ys = np.clip(np.floor((np.arange(H) + 0.5 - OY) / PY).astype(int), 0, ROWS - 1)
    return cells[ys][:, xs]
if __name__ == '__main__':
    out = '/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/lab/'
    for k in (0, 3):
        Image.fromarray(to_px(scene_rgb(k))).save(out + f'plate_k{k}.png')
