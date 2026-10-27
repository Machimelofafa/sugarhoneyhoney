import numpy as np, cv2, sys, pickle
sys.path.insert(0,'.')
from seg4 import *
LAT=(6.9,8.8)   # overview actor lattice (canonical px)
def area_sample(im, mask, z, margin=1):
    px,py=LAT[0]*z,LAT[1]*z
    ys,xs=np.where(mask>0)
    x0=int(xs.min()); y0=int(ys.min()); x1=int(xs.max())+1; y1=int(ys.max())+1
    w=int(np.ceil((x1-x0)/px))+margin*2; h=int(np.ceil((y1-y0)/py))+margin*2
    # origin so that the bbox is centered in the cell grid
    ox=x0-(w*px-(x1-x0))/2; oy=y0-(h*py-(y1-y0))/2
    # build the crop with float origin via warpAffine (bilinear on premultiplied; then average within cell via INTER_AREA)
    M=np.float32([[1,0,-ox],[0,1,-oy]])
    cw,ch=int(round(w*px)),int(round(h*py))
    m=mask.astype(np.float32)
    prem=(im.astype(np.float32)*m[...,None])
    big=cv2.warpAffine(prem,M,(cw,ch),flags=cv2.INTER_NEAREST,borderValue=0)
    bm=cv2.warpAffine(m,M,(cw,ch),flags=cv2.INTER_NEAREST,borderValue=0)
    pc=cv2.resize(big,(w,h),interpolation=cv2.INTER_AREA); pa=cv2.resize(bm,(w,h),interpolation=cv2.INTER_AREA)
    col=np.where(pa[...,None]>1e-3,pc/np.maximum(pa[...,None],1e-3),0)
    return dict(col=col.astype(np.float32),al=pa.astype(np.float32),origin=(ox,oy),pitch=(px,py),z=z)
def render_blocks(sp, kx=7, ky=9, thr=0.5, bg=(60,0,60)):
    h,w=sp['al'].shape; out=np.zeros((h*ky,w*kx,3),np.uint8); out[:]=bg
    for j in range(h):
        for i in range(w):
            if sp['al'][j,i]>=thr: out[j*ky:(j+1)*ky,i*kx:(i+1)*kx]=np.clip(sp['col'][j,i],0,255).astype(np.uint8)
    return out
def sheet_of(tiles, maxw=2000, gap=6):
    rows=[];cur=[];w=0
    for t in tiles:
        if w+t.shape[1]+gap>maxw and cur: rows.append(cur);cur=[];w=0
        cur.append(t); w+=t.shape[1]+gap
    if cur: rows.append(cur)
    imgs=[]
    for row in rows:
        H=max(t.shape[0] for t in row); W=sum(t.shape[1]+gap for t in row)
        sh=np.zeros((H,W,3),np.uint8); x=0
        for t in row: sh[:t.shape[0],x:x+t.shape[1]]=t; x+=t.shape[1]+gap
        imgs.append(sh)
    W=max(i.shape[1] for i in imgs); cv=np.zeros((sum(i.shape[0]+gap for i in imgs),W,3),np.uint8); y=0
    for i in imgs: cv[y:y+i.shape[0],:i.shape[1]]=i; y+=i.shape[0]+gap
    return cv
def run_clip(name, actor, a, b, st, z, label=None):
    cfg=CFGS[name]
    try: cen=np.load(S+f'lab/pal_{name}.npy')
    except Exception:
        fr=list(range(a,b+1,max(1,(b-a)//14))); cen=build_palette(fr,cfg); np.save(S+f'lab/pal_{name}.npy',cen)
    sprites={}
    for i in range(a,b+1,st):
        im=cv2.imread(FR%i); mk=segment_frame(im,cfg,cen)
        m=mk.get(actor)
        if m is None or m.sum()<2500: continue
        ys,xs=np.where(m>0)
        cut=ys.min()<=2 or ys.max()>=im.shape[0]-3 or xs.min()<=2 or xs.max()>=im.shape[1]-3
        sp=area_sample(im,m,z); sp['cut']=bool(cut); sp['frame']=i
        sprites[i]=sp
    return sprites
if __name__=='__main__':
    name,actor=sys.argv[1],sys.argv[2]; a,b,st=map(int,sys.argv[3:6]); z=float(sys.argv[6])
    sp=run_clip(name,actor,a,b,st,z)
    tiles=[]
    for i,s in sp.items():
        t=render_blocks(s)
        cv2.putText(t,f'{i}{"*" if s["cut"] else ""}',(2,12),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1); tiles.append(t)
    cv2.imwrite(S+f'lab/sp_{name}_{actor}.png',sheet_of(tiles))
    pickle.dump(sp,open(S+f'lab/sp_{name}_{actor}.pkl','wb'))
    print(name,actor,len(sp),'sprites')
