import numpy as np, cv2, sys
from scipy.signal import find_peaks
S='/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/'
FR=S+'fr/f_%04d.jpg'
def spec_curve(e, lo, hi, N=1<<15):
    e=e-e.mean(); n=len(e)
    F=np.abs(np.fft.rfft(e*np.hanning(n),N)); f=np.fft.rfftfreq(N)
    per=1/np.maximum(f,1e-9); m=(per>lo)&(per<hi)
    return per[m], F[m]
def shot_spectra(frames, lo, hi, axis):
    acc=None
    for i in frames:
        g=cv2.imread(FR%i).astype(np.float32).sum(axis=2)
        e=np.abs(np.diff(g,axis=1)).sum(axis=0) if axis=='x' else np.abs(np.diff(g,axis=0)).sum(axis=1)
        p,f=spec_curve(e,lo,hi); acc=f if acc is None else acc+f
    return p, acc/len(frames)
def top(p,a,s_scen,pscen, k=4):
    pk,_=find_peaks(a); pk=pk[np.argsort(-a[pk])]
    out=[]
    for j in pk:
        per=p[j]
        # skip scenery harmonics
        bad=any(abs(per-pscen*s_scen*m)/(pscen*s_scen*m)<0.025 for m in (0.5,1,2,3,4))
        if not bad: out.append((round(float(per),2), round(float(a[j]/a.mean()),1)))
        if len(out)>=k: break
    return out
shots={'fire':(range(166,206,3),2.40),'vil':(range(358,425,3),2.154),'fight':(range(490,570,4),2.775),'croc':(range(694,779,4),3.058),'water':(range(1084,1127,4),3.058),
 'scaf':(list(range(1492,1530,3))+list(range(1630,1715,6)),3.105),'girlA':(range(428,488,4),4.245),'girlB':(range(1372,1488,4),4.25),'girlC':(range(1780,1890,4),4.25),'ov':(range(112,160,3),1.0)}
for name,(idx,s) in shots.items():
    px,ax=shot_spectra(idx,5,50,'x'); py,ay=shot_spectra(idx,5,40,'y')
    print(name,'x',top(px,ax,s,8.27),'| y',top(py,ay,s,4.445), flush=True)
