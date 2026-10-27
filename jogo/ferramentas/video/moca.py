import numpy as np, cv2, sys
sys.path.insert(0,'.')
from seg2 import chans
def moca(im, minarea=2500):
    r,g,b=chans(im); v=np.maximum(np.maximum(r,g),b)
    m=((r-b>12)&(v>10)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
    link=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(25,25)))
    n,l,st,_=cv2.connectedComponentsWithStats(link,8)
    if n<2: return np.zeros_like(m)
    k=1+np.argmax([ (m[l==c]).sum() for c in range(1,n)])
    out=(m*(l==k)).astype(np.uint8)
    cnt,_=cv2.findContours(out,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    f=np.zeros_like(out); cv2.drawContours(f,cnt,-1,1,-1)
    return f if f.sum()>=minarea else np.zeros_like(m)
if __name__=='__main__':
    from seg2 import FR,S
    outs=[]
    for i in (450,470,1400,1450,1784,1800,1820,1840,1860,1880,1990,2050):
        im=cv2.imread(FR%i); mk=moca(im)
        ov=im.copy()
        if mk.sum(): 
            ov[mk>0]=(0.5*ov[mk>0]+0.5*np.array([255,255,0])).astype(np.uint8)
            cnt,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cv2.drawContours(ov,cnt,-1,(255,255,255),3)
        cv2.putText(ov,str(i),(10,40),cv2.FONT_HERSHEY_SIMPLEX,1.3,(0,255,255),3)
        outs.append(cv2.resize(ov,None,fx=0.3,fy=0.3,interpolation=cv2.INTER_AREA))
    cv2.imwrite(S+'v/moca_teste.png',np.vstack([np.hstack(outs[k:k+4]) for k in (0,4,8)]))
