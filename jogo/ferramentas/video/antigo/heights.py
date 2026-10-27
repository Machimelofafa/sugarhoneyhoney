import numpy as np, cv2, sys
sys.path.insert(0,'.')
from seg4 import *
RANGES={'croc':(696,778,4),'water':(1086,1126,4),'fire':(166,204,3),'scaf':(1492,1530,4),'ur':(998,1050,4),'vil':(392,424,3),'fight':(490,560,5),'girlA':(428,484,6),'girlB':(1372,1486,8),'girlC':(1780,1890,8)}
for name,(a,b,st) in RANGES.items():
    cfg=CFGS[name]; frames=list(range(a,b+1,st))
    try: cen=np.load(S+f'lab/pal_{name}.npy')
    except Exception:
        cen=build_palette(frames[::max(1,len(frames)//14)],cfg); np.save(S+f'lab/pal_{name}.npy',cen)
    H={}
    for i in frames:
        im=cv2.imread(FR%i); mk=segment_frame(im,cfg,cen)
        for k,m in mk.items():
            ys,xs=np.where(m>0)
            if len(xs)<3000: continue
            if ys.min()<=3 or ys.max()>=im.shape[0]-3: continue   # cut by frame
            H.setdefault(k,[]).append(int(ys.max()-ys.min()))
    for k,v in H.items():
        v=np.array(v); print(name,k,'n',len(v),'p50 %d p85 %d max %d'%(np.percentile(v,50),np.percentile(v,85),v.max()),flush=True)
