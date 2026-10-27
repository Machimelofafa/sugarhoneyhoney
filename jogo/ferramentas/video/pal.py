import numpy as np, cv2, sys
sys.path.insert(0,'.')
from seg3 import *
def lab_img(im): return cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
def scenery_palette(frames, core_fn, K=24, roi_r=80, sub=3, seed=1):
    samples=[]
    for i in frames:
        im=cv2.imread(FR%i); core=core_fn(im)
        roi=cv2.dilate(core.astype(np.uint8),K3(roi_r*2+1)) if core.sum()>0 else np.zeros(core.shape,np.uint8)
        L=lab_img(im)[::sub,::sub]; ok=(roi[::sub,::sub]==0)
        samples.append(L[ok])
    X=np.concatenate(samples).astype(np.float32)
    if len(X)>400000: X=X[np.random.default_rng(seed).choice(len(X),400000,replace=False)]
    crit=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,40,0.5)
    _,lab,cen=cv2.kmeans(X,K,None,crit,2,cv2.KMEANS_PP_CENTERS)
    return cen
def dist_map(im, cen):
    L=lab_img(im); H,W,_=L.shape
    d=np.full((H,W),1e9,np.float32)
    for c in cen:
        dd=np.sqrt(((L-c)**2).sum(axis=2)); d=np.minimum(d,dd)
    return d
def candidate_mask(im, cen, tau=22, open_k=5):
    d=dist_map(im,cen)
    m=(d>tau).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,K3(open_k))
    return m
if __name__=='__main__':
    a,b,st=map(int,sys.argv[1:4]); out=sys.argv[4]; tau=float(sys.argv[5]); K=int(sys.argv[6])
    frames=list(range(a,b+1,st))
    cen=scenery_palette(frames, lambda im: girl_groups(im), K)
    tiles=[]
    for i in frames:
        im=cv2.imread(FR%i); m=candidate_mask(im,cen,tau)
        tiles.append(overlay(im,m,i))
    cv2.imwrite(S+f'lab/{out}.png',sheet(tiles))
