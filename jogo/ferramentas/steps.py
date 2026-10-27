import sys
import numpy as np
from PIL import Image
sys.path.insert(0, sys.argv[1])
from deblur import grid_from
d, out = sys.argv[2], sys.argv[3]
groups = [(3, 5), (7, 10), (11, 14), (17, 20), (22, 25), (26, 29), (31, 35), (36, 38), (39, 40), (41, 45), (47, 50), (51, 54)]
grids = []
for k, (a, b) in enumerate(groups):
    fr = np.stack([np.asarray(Image.open(f'{d}/a_{i:03d}.png').convert('RGB')).astype(np.float32) for i in range(a, b + 1)]).mean(axis=0)
    g = grid_from(Image.fromarray(fr.astype(np.uint8)))
    grids.append(g)
    Image.fromarray(g.astype(np.uint8)).save(f'{out}/step_{k:02d}.png')
G = np.stack(grids)
np.save(f'{out}/steps.npy', G)
var = G.std(axis=0).mean(axis=2)
Image.fromarray((var / var.max() * 255).astype(np.uint8)).resize((170 * 4, 238 * 2), Image.NEAREST).save(f'{out}/steps_var.png')
print(G.shape)
