import cv2, numpy as np, json, sys
from seg2 import S
import os
AQUI=os.path.dirname(os.path.abspath(__file__)); AT=os.path.join(AQUI,'..','..','atlas')
at=cv2.imread(os.path.join(AT,'atlas.png'),cv2.IMREAD_UNCHANGED); meta=json.load(open(os.path.join(AT,'atlas.json'))); PX=meta['px']; sp=meta['sprites']
ref=cv2.imread(os.path.join(AQUI,'..','..','..','referencia','fase_visao_geral.png'))
refs={'hero':ref[660:990,1050:1260],'vil':ref[320:640,470:710],'girl':ref[50:300,220:360]}
def render(ator, scale=1.0, maxw=2000):
    ids=[k for k in sp if k.startswith(ator+'.')]
    tiles=[]
    for k in ids:
        s=sp[k]; im=at[s['y']:s['y']+s['h'],s['x']:s['x']+s['w']]
        if s['f']*(-1 if ator in('vil',) else 1) and False: pass
        big=cv2.resize(im,None,fx=PX*scale,fy=PX*scale,interpolation=cv2.INTER_NEAREST)
        bg=np.zeros(big.shape[:2]+(3,),np.uint8); bg[:]=(70,20,70); a=big[...,3:4]/255.0
        t=(big[...,:3]*a+bg*(1-a)).astype(np.uint8)
        tiles.append((k,t,s))
    # baseline row layout
    rows=[]; cur=[]; w=0
    r=cv2.resize(refs[ator],None,fx=scale,fy=scale)
    cur=[('ref',r,None)]; w=r.shape[1]
    for k,t,s in tiles:
        if w+t.shape[1]>maxw: rows.append(cur); cur=[]; w=0
        cur.append((k,t,s)); w+=t.shape[1]+4
    rows.append(cur)
    imgs=[]
    for row in rows:
        H=max(t.shape[0] for _,t,_ in row)+18; Wd=sum(t.shape[1]+4 for _,t,_ in row)
        o=np.zeros((H,Wd,3),np.uint8); o[:]=(30,10,30); x=0
        for k,t,s in row:
            o[H-t.shape[0]:H,x:x+t.shape[1]]=t
            cv2.putText(o,k.split('.',1)[1] if k!='ref' else 'ref',(x+2,12),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,255),1)
            if s is not None: # âncora
                cv2.circle(o,(int(x+s['ax']*PX*scale),H-1),3,(0,255,0),-1)
            x+=t.shape[1]+4
        imgs.append(o)
    Wm=max(i.shape[1] for i in imgs); out=np.zeros((sum(i.shape[0] for i in imgs),Wm,3),np.uint8); y=0
    for i in imgs: out[y:y+i.shape[0],:i.shape[1]]=i; y+=i.shape[0]
    return out
for ator in sys.argv[1:]:
    o=render(ator); cv2.imwrite(S+f'v/tira_{ator}.png',o); print(ator,o.shape)
