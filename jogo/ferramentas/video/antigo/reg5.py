import cv2, numpy as np, sys, time, os, json
from concurrent.futures import ThreadPoolExecutor
S='/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/'
FR=S+'fr/f_%04d.jpg'
D=6
OV = cv2.imread(S+'lab/ovplate.png')
def edgemap(img, d=D, sig=1.2, mask_text=False):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    m = np.sqrt(gx*gx + gy*gy)
    if mask_text:
        white = (g > 222).astype(np.uint8)
        white = cv2.dilate(white, np.ones((25, 25), np.uint8))
        m = m * (1 - white)
    m = cv2.resize(m, (m.shape[1]//d, m.shape[0]//d), interpolation=cv2.INTER_AREA)
    m = cv2.GaussianBlur(m, (0,0), sig)
    return np.minimum(m, 120.0)
SCALES = np.round(np.arange(1.0, 6.01, 0.04), 3)
def build(s):
    P = cv2.resize(OV, None, fx=float(s), fy=float(s), interpolation=cv2.INTER_LINEAR)
    return float(s), edgemap(P)
t0 = time.time()
with ThreadPoolExecutor(8) as ex: CACHE = dict(ex.map(build, SCALES))
print('cache', round(time.time()-t0), 's', flush=True)
def match(i, topn=4):
    F = edgemap(cv2.imread(FR % i), mask_text=True)
    out = []
    for s in SCALES:
        P = CACHE[float(s)]
        if P.shape[0] < F.shape[0] or P.shape[1] < F.shape[1]: continue
        r = cv2.matchTemplate(P, F, cv2.TM_CCOEFF_NORMED)
        _, mx, _, loc = cv2.minMaxLoc(r)
        out.append((float(mx), float(s), loc[0]*D, loc[1]*D))
    out.sort(reverse=True)
    return i, out[:topn]
if __name__ == '__main__':
    idx = []
    for rng in sys.argv[1:]:
        a, b, st = map(int, rng.split(':'))
        idx += list(range(a, b+1, st))
    t = time.time(); res = {}
    with ThreadPoolExecutor(8) as ex:
        for i, r in ex.map(match, idx):
            res[i] = r
            print(i, [(round(m, 3), s, x, y) for m, s, x, y in r[:2]], flush=True)
    json.dump(res, open(S+'lab/reg5_%d.json' % int(time.time()), 'w'))
    print('time', round(time.time()-t))
