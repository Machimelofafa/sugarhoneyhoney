import sys; sys.path.insert(0,'.')
import cv2, numpy as np
from folha import *
from seg2 import hero_core
def gold_alt(rgba):
    bgr=rgba[...,:3]; a=rgba[...,3]>128
    gold,_=hero_core(bgr,60); gold&=a
    g=cv2.morphologyEx(gold.astype(np.uint8),cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,l,st,_=cv2.connectedComponentsWithStats(g,8)
    if n<2: return None
    k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); return int(st[k,cv2.CC_STAT_HEIGHT]), int(st[k,cv2.CC_STAT_WIDTH]), int(st[k,cv2.CC_STAT_AREA])
for nome in sys.argv[1:]:
    d,meta=carregar(nome); r=[]
    for i in sorted(meta):
        if meta[i]['cortado']: continue
        im=cv2.imread(d+f'{i:04d}.png',cv2.IMREAD_UNCHANGED); g=gold_alt(im)
        if g: r.append((i,)+g)
    if not r: print(nome,'sem ouro'); continue
    a=np.array(r); 
    print(nome,len(r),'gold h med',np.median(a[:,1]),'w med',np.median(a[:,2]),'sqrt(area/4354) med',np.median(np.sqrt(a[:,3]/4354)).round(2),' z_h=',(np.median(a[:,1])/75).round(2))
