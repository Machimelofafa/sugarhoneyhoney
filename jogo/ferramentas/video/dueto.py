import numpy as np, cv2, sys
sys.path.insert(0,'.')
from seg2 import chans, hero_core, FR, S
def placa():
    import os
    p=S+'lab/placa_dueto.npy'
    if os.path.exists(p): return np.load(p)
    fr=[cv2.imread(FR%i) for i in range(1990,2128,4)]
    pl=np.median(np.stack(fr),axis=0).astype(np.uint8); np.save(p,pl); return pl
def dueto(im, pl):
    r,g,b=chans(im); v=np.maximum(np.maximum(r,g),b)
    warm=(r-b>12)&(v>10)
    heart=(g<35)&(b<55)&(r>25)&((r-g)>20)          # vermelho dos corações
    _,teal=hero_core(im,60)
    m=((warm&~heart)|teal).astype(np.uint8)
    m[:100]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
    link=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41)))
    n,l,st,_=cv2.connectedComponentsWithStats(link,8)
    keep=np.zeros_like(m)
    for k in range(1,n):
        if (m[l==k]).sum()>3000: keep[l==k]=1
    m=m*keep
    cnt,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    f=np.zeros_like(m); cv2.drawContours(f,cnt,-1,1,-1)
    return f
if __name__=='__main__':
    outs=[]; pl=placa()
    for i in (1990,2014,2044,2062,2080,2098,2110,2128):
        im=cv2.imread(FR%i); mk=dueto(im,pl); ov=im.copy()
        ov[mk>0]=(0.5*ov[mk>0]+0.5*np.array([255,255,0])).astype(np.uint8)
        cnt,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cv2.drawContours(ov,cnt,-1,(255,255,255),3)
        cv2.putText(ov,str(i),(10,40),cv2.FONT_HERSHEY_SIMPLEX,1.3,(0,255,255),3)
        outs.append(cv2.resize(ov,None,fx=0.3,fy=0.3,interpolation=cv2.INTER_AREA))
    cv2.imwrite(S+'v/dueto_teste.png',np.vstack([np.hstack(outs[:4]),np.hstack(outs[4:])]))
