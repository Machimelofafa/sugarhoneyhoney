import sys, cv2, numpy as np, os
from seg2 import S
from limpa import limpa
def carrega(spec):
    c,f=spec.split(':'); return cv2.imread(S+f'cut/{c}/{int(f):04d}.png',cv2.IMREAD_UNCHANGED)
def sheet(specs, sc, out, lim=False):
    tiles=[]
    for sp in specs:
        im=carrega(sp)
        if lim: im=limpa(im)
        im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA)
        bg=np.zeros(im.shape[:2]+(3,),np.uint8); bg[:]=(70,20,70); a=im[...,3:4]/255.0
        t=(im[...,:3]*a+bg*(1-a)).astype(np.uint8); t=cv2.copyMakeBorder(t,16,2,2,2,cv2.BORDER_CONSTANT,value=(30,10,30))
        cv2.putText(t,sp,(3,12),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,255),1); tiles.append(t)
    H=max(t.shape[0] for t in tiles); W=sum(t.shape[1] for t in tiles)
    o=np.zeros((H,W,3),np.uint8); x=0
    for t in tiles: o[:t.shape[0],x:x+t.shape[1]]=t; x+=t.shape[1]
    cv2.imwrite(out,o); print(o.shape)
if __name__=='__main__':
    sc=float(sys.argv[1]); out=sys.argv[2]; sheet(sys.argv[3:],sc,out, os.environ.get('LIMPA')=='1')
