import numpy as np, cv2, sys, json
S='/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/'
FR=S+'fr/f_%04d.jpg'
def build(frames, K=28, sub=2):
    px = []
    for i in frames:
        im = cv2.imread(FR % i)[::sub, ::sub]
        px.append(cv2.cvtColor(im, cv2.COLOR_BGR2LAB).reshape(-1, 3))
    X = np.concatenate(px).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.5)
    _, lab, cen = cv2.kmeans(X[::5], K, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    return cen
def classify(im, cen):
    L = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32).reshape(-1, 3)
    d = ((L[:, None, :] - cen[None]) ** 2).sum(-1)
    return d.argmin(1).reshape(im.shape[:2])
def swatch(cen, labels_text=True):
    bgr = cv2.cvtColor(cen.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_LAB2BGR).reshape(-1, 3)
    K = len(cen); sw = np.zeros((60, K * 60, 3), np.uint8)
    for k in range(K):
        sw[:, k*60:(k+1)*60] = bgr[k]
        cv2.putText(sw, str(k), (k*60+8, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255) if bgr[k].mean() < 128 else (0,0,0), 2)
    return sw, bgr
if __name__ == '__main__':
    name = sys.argv[1]; frames = list(map(int, sys.argv[2].split(','))); K = int(sys.argv[3])
    cen = build(frames, K)
    np.save(S + f'lab/cen_{name}.npy', cen)
    sw, bgr = swatch(cen)
    # show one classified frame per sample as palette-colored image beside original
    rows = []
    for i in frames[:3]:
        im = cv2.imread(FR % i); lab = classify(im[::2, ::2], cen)
        q = bgr[lab].reshape(lab.shape[0], lab.shape[1], 3).astype(np.uint8)
        rows.append(np.concatenate([im[::2, ::2], q], axis=1))
    big = np.concatenate(rows, axis=0)
    # layout
    w = max(big.shape[1], sw.shape[1])
    canvas = np.zeros((big.shape[0] + 70, w, 3), np.uint8); canvas[:sw.shape[0], :sw.shape[1]] = sw; canvas[70:, :big.shape[1]] = big
    cv2.imwrite(S + f'lab/clus_{name}.png', canvas); print(canvas.shape)
    for k, c in enumerate(bgr): print(k, tuple(int(v) for v in c[::-1]))
