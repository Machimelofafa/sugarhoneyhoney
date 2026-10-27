import numpy as np, cv2, sys, json
sys.path.insert(0,'.')
from seg2 import *
def edges_masked(im, m):
    g=im.astype(np.float32).sum(axis=2); mk=cv2.dilate(m,np.ones((3,3),np.uint8)).astype(np.float32)
    ex=(np.abs(np.diff(g,axis=1))*mk[:,1:]).sum(axis=0); ey=(np.abs(np.diff(g,axis=0))*mk[1:,:]).sum(axis=1)
    return np.convolve(ex,[.25,.5,.25],'same'), np.convolve(ey,[.25,.5,.25],'same')
def comb_best(e, p0, rel=0.03, dp=0.01, step=0.25):
    n=len(e); best=(-1,0,0)
    for p in np.arange(p0*(1-rel), p0*(1+rel), dp):
        for ph in np.arange(0,p,step):
            pos=np.arange(ph,n-1,p); idx=np.clip(np.round(pos).astype(int),0,n-1)
            sc=e[idx].mean()
            if sc>best[0]: best=(sc,p,ph)
    return best
def fit_pitch(frames, maskfn, p0x, p0y, n=8):
    sel=frames[::max(1,len(frames)//n)]
    px=[];py=[]
    for i in sel:
        im=cv2.imread(FR%i); m=maskfn(im)
        if m.sum()<4000: continue
        ex,ey=edges_masked(im,m)
        px.append(comb_best(ex,p0x)[1]); py.append(comb_best(ey,p0y)[1])
    return float(np.median(px)), float(np.median(py)), len(px)
if __name__=='__main__':
    name=sys.argv[1]; a,b,st=map(int,sys.argv[2:5]); cell=int(sys.argv[5]); tmg=int(sys.argv[6]); p0x=float(sys.argv[7]); p0y=float(sys.argv[8])
    frames=list(range(a,b+1,st))
    fn=lambda im: hero_mask(im,tmg,cell)
    print(name, fit_pitch(frames,fn,p0x,p0y))
