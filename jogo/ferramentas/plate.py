import sys, glob
import numpy as np
from PIL import Image
d, out = sys.argv[1], sys.argv[2]
files = [f'{d}/a_{i:03d}.png' for i in range(2, 58)]
stack = np.stack([np.asarray(Image.open(f).convert('RGB')) for f in files]).astype(np.float32)
med = np.median(stack, axis=0)
Image.fromarray(med.clip(0, 255).astype(np.uint8)).save(out + '/plate_a.png')
std = stack.std(axis=0).mean(axis=2)
s = (std / np.percentile(std, 99.5) * 255).clip(0, 255).astype(np.uint8)
Image.fromarray(s).save(out + '/plate_std.png')
# distinct frame groups (the animation steps)
prev = None; groups = []
for i, f in enumerate(files):
    if prev is not None and np.abs(stack[i] - prev).mean() > 2.0: groups.append(i + 2)
    prev = stack[i]
print('frame changes at', groups)
