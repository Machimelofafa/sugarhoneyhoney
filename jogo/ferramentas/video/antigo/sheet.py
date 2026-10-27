import sys
from PIL import Image, ImageDraw
fr0, fr1, step = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6
tw = int(sys.argv[5]) if len(sys.argv) > 5 else 330
out = sys.argv[6] if len(sys.argv) > 6 else f'sheet_{fr0}_{fr1}.png'
th = int(tw * 1058 / 1408)
idx = list(range(fr0, fr1 + 1, step))
rows = (len(idx) + cols - 1) // cols
S = '/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/fr'
sh = Image.new('RGB', (cols * tw, rows * th), 'white')
d = ImageDraw.Draw(sh)
for n, i in enumerate(idx):
    im = Image.open(f'{S}/f_{i:04d}.jpg').resize((tw, th), Image.BILINEAR)
    x, y = (n % cols) * tw, (n // cols) * th
    sh.paste(im, (x, y)); d.rectangle([x, y, x + 62, y + 12], fill='black'); d.text((x + 2, y), f'{i} {i/29.97:.2f}s', fill='yellow')
sh.save(out)
print(out, sh.size)
