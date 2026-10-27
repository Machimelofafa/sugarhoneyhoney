import sys, json, base64
import numpy as np
from PIL import Image, ImageDraw
d = sys.argv[1]
q = np.load(d + '/q_steps.npy').astype(np.int16)    # (S, H, W)
base = np.load(d + '/q_med.npy').astype(np.int16)
pal = np.load(d + '/pal_final.npy')
S_, H, W = q.shape

def row_allowed(r, x0, x1, span=30):
    vals = list(base[r, max(0, x0 - span):x0]) + list(base[r, x1:min(W, x1 + span)])
    return set(int(v) for v in vals)

def fill_box(x0, y0, x1, y1, mode='row'):
    unknown = []
    for r in range(y0, y1):
        allowed = row_allowed(r, x0, x1)
        for c in range(x0, x1):
            cand = [int(v) for v in q[:, r, c] if int(v) in allowed]
            if cand:
                base[r, c] = np.bincount(cand).argmax()
            else:
                unknown.append((r, c))
    for r, c in unknown:
        # nearest known value in the same row, outside the box
        for dist in range(1, W):
            for cc in (c - dist, c + dist):
                if 0 <= cc < W and not (x0 <= cc < x1):
                    base[r, c] = base[r, cc]; break
            else:
                continue
            break

def col_fill(x0, y0, x1, y1, ry0, ry1, bad):
    for c in range(x0, x1):
        vals = [int(v) for k in range(S_) for v in q[k, ry0:ry1, c] if int(v) not in bad]
        if vals:
            m = np.bincount(vals).argmax()
            base[y0:y1, c] = m

def row_copy(x0, y0, x1, y1, sx0, sx1):
    for r in range(y0, y1):
        vals = list(base[r, sx0:sx1]); m = np.bincount(vals).argmax()
        base[r, x0:x1] = m

# colours that belong to people (skin, hair, clothes)
people = set()
for i, c in enumerate(pal):
    r, g, b = c
    if (r > 90 and g > 60 and b < 120) or (r > 150 and b > 60 and g < 40): people.add(i)
print('people colours', sorted(people), ['#%02x%02x%02x' % tuple(int(v) for v in pal[i]) for i in sorted(people)])

# girl: sky / clouds / roof
fill_box(24, 8, 58, 66)
# hero: water, pipes, pier
fill_box(122, 146, 156, 222)
# villain: curtain by column, sign frame + floor by row
bad = people | {int(v) for v in q[:, 80:90, 62:78].ravel()} - {int(base[110, 20]), int(base[110, 21]), int(base[110, 22])}
col_fill(56, 93, 84, 132, 95, 130, people)
col_fill(56, 70, 84, 78, 70, 78, people)
row_copy(58, 78, 80, 80, 46, 58)
row_copy(58, 91, 80, 94, 46, 58)
row_copy(56, 132, 86, 143, 26, 52)
np.save(d + '/base_clean.npy', base)
img = pal[base].clip(0, 255).astype(np.uint8)
Image.fromarray(img).save(d + '/base_clean.png')
bright = (255 * (img / 255.0) ** 0.6).astype(np.uint8)
big = Image.fromarray(bright).resize((W * 6, H * 3), Image.NEAREST)
pad = 26
c = Image.new('RGB', (big.width + pad, big.height + pad), 'white'); c.paste(big, (pad, pad))
dr = ImageDraw.Draw(c)
for i in range(0, W + 1, 10):
    x = pad + i * 6; dr.line([(x, pad), (x, pad + big.height)], fill=(0, 255, 0)); dr.text((x + 1, 2), str(i), fill='black')
for j in range(0, H + 1, 10):
    y = pad + j * 3; dr.line([(pad, y), (pad + big.width, y)], fill=(0, 255, 0)); dr.text((1, y + 1), str(j), fill='black')
c.save(d + '/base_clean_lab.png')
