import cv2, numpy as np, sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seg2 import S
O = S + "fr/f_%04d.jpg"
def spec(e, lo, hi):
    e=e-e.mean(); n=len(e); N=1<<16
    F=np.abs(np.fft.rfft(e*np.hanning(n),N)); f=np.fft.rfftfreq(N); per=1/np.maximum(f,1e-9)
    m=(per>lo)&(per<hi); return per[m],F[m]
def run(name, frames, box):
    x0,y0,x1,y1=box; ax=None; ay=None
    for i in frames:
        g=cv2.imread(O%i)[y0:y1,x0:x1].astype(np.float32).sum(2)
        ex=np.abs(np.diff(g,axis=1)).sum(0); ey=np.abs(np.diff(g,axis=0)).sum(1)
        p,f=spec(ex,6,40); q,h=spec(ey,6,40)
        ax=f if ax is None else ax+f; ay=h if ay is None else ay+h
    from scipy.signal import find_peaks
    def top(p,a):
        pk,_=find_peaks(a); pk=pk[np.argsort(-a[pk])][:4]
        return [(round(float(p[j]),2), round(float(a[j]/a.mean()),1)) for j in pk]
    print(name,'x',top(p,ax),'y',top(q,ay))
# boxes (x0,y0,x1,y1) around the actor in each shot, chosen on a frame
run('ov_hero',range(112,140,3),(1060,660,1260,980))
run('ov_vil',range(112,140,3),(480,330,700,620))
run('ov_girl',range(112,140,3),(230,50,350,290))
