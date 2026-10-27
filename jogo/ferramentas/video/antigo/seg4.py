import numpy as np, cv2, sys
sys.path.insert(0,'.')
from seg2 import chans, dark_mask, light_mask, K3, sheet, FR, S
from seg3 import hero_groups, skin_gen, girl_groups
from pal import lab_img, dist_map
def circ(r): return cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(r)*2+1,int(r)*2+1))
class Cfg(dict): __getattr__=dict.get
def vil_pants(im, rule):
    r,g,b=chans(im)
    if rule=='maroon':   # vil shot: dark maroon trousers
        return (r>40)&(r<105)&(g>12)&(g<58)&(b>12)&(b<62)&((r-g)>20)&((r-g)<62)&(abs(g-b)<24)
    return (r>42)&(r<135)&(g>32)&(g<112)&(b>14)&(b<92)&(r>=g-2)&(g>=b-6)&((r-b)>12)&((r-g)<38)&((g-b)*100<(r-b)*72)
def seeds(im, cfg):
    """rough per-actor seed masks (uint8)"""
    out={}
    if 'hero' in cfg.kinds:
        gold,teal=hero_groups(im,cfg.teal_min_g or 95,cfg.cell)
        core=(gold|teal).astype(np.uint8); core=cv2.morphologyEx(core,cv2.MORPH_OPEN,K3(3))
        if core.sum()>0:
            link=cv2.dilate(core,circ(cfg.cell*2.0)); n,l,st,_=cv2.connectedComponentsWithStats(link,8)
            gm=gold.astype(np.uint8); tm=teal.astype(np.uint8)
            best=max(((3*gm[l==k].sum()+tm[l==k].sum()),k) for k in range(1,n))[1]
            core=core*(l==best).astype(np.uint8)
            if gm[core>0].sum()<(cfg.min_gold or 250): core[:]=0
        out['hero']=core
    if 'vil' in cfg.kinds:
        pants=vil_pants(im,cfg.vil_rule).astype(np.uint8); pants=cv2.morphologyEx(pants,cv2.MORPH_OPEN,K3(5))
        r,g,b=chans(im); sk=((r>135)&(r>g+22)&(g>b+8)&((r-g)<95)&(b>45)&(r<252)).astype(np.uint8)
        sk=cv2.morphologyEx(sk,cv2.MORPH_OPEN,K3(5))
        pants[:14]=0
        both=pants|sk
        if both.sum()>0:
            link=cv2.dilate(both,circ(cfg.cell*2.2)); n,l,st,_=cv2.connectedComponentsWithStats(link,8)
            best=max(((2*sk[l==k].sum()+pants[l==k].sum()),k) for k in range(1,n))[1]
            pants=pants*(l==best).astype(np.uint8)
        out['vil']=pants
    if 'girl' in cfg.kinds:
        d=girl_groups(im).astype(np.uint8); out['girl']=cv2.morphologyEx(d,cv2.MORPH_OPEN,K3(3))
    return out
def build_palette(frames, cfg, K=24, sub=3):
    samples=[]
    for i in frames:
        im=cv2.imread(FR%i); sd=seeds(im,cfg)
        u=np.zeros(im.shape[:2],np.uint8)
        for k,v in sd.items(): u|=v
        # for vil include a skin-blob guess so the bare torso is excluded from the palette
        if 'vil' in cfg.kinds:
            r,g,b=chans(im); sk=((r>135)&(r>g+22)&(g>b+8)&((r-g)<95)&(b>45)&(r<252)).astype(np.uint8)
            sk=cv2.morphologyEx(sk,cv2.MORPH_OPEN,K3(5)); u|=sk
        if u.sum()>0: roi=cv2.dilate(u,circ(cfg.roi_r or 90))
        else: roi=np.zeros(u.shape,np.uint8)
        L=lab_img(im)[::sub,::sub]; ok=roi[::sub,::sub]==0
        samples.append(L[ok])
    X=np.concatenate(samples).astype(np.float32)
    if len(X)>400000: X=X[np.random.default_rng(1).choice(len(X),400000,replace=False)]
    crit=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,40,0.5)
    _,_,cen=cv2.kmeans(X,K,None,crit,2,cv2.KMEANS_PP_CENTERS)
    extra=[(235,240,150),(200,210,110),(190,170,60),(150,140,40),(225,225,150),(185,25,35),(120,10,15),(255,255,255),(10,10,10),(30,25,35)]
    from pal import lab_img as _l
    ex=[cv2.cvtColor(np.uint8([[c[::-1]]]),cv2.COLOR_BGR2LAB).reshape(3).astype(np.float32) for c in extra] if cfg.extra_pal else []
    return np.concatenate([cen,np.array(ex,np.float32).reshape(-1,3)]) if ex else cen
def segment_frame(im, cfg, cen):
    cell=cfg.cell
    sd=seeds(im,cfg)
    d=dist_map(im,cen)
    C=(d>(cfg.tau or 22)).astype(np.uint8)
    C=cv2.morphologyEx(C,cv2.MORPH_OPEN,K3(cfg.open_k or 5))
    for a_,v in sd.items():
        C|=v
        rad=(cfg.skin_near or {}).get(a_)
        if rad and v.sum()>0:
            near_=cv2.dilate(v,circ(cell*rad))
            sk_=(skin_gen(im,70).astype(np.uint8)&near_); sk_=cv2.morphologyEx(sk_,cv2.MORPH_OPEN,K3(3))
            C|=sk_
    if cfg.band:
        x0,y0,x1,y1=cfg.band
        rules=(skin_gen(im,70).astype(np.uint8)|dark_mask(im,60).astype(np.uint8))
        for v in sd.values(): rules=rules|v
        rr=cv2.morphologyEx(rules,cv2.MORPH_OPEN,K3(5))
        band=np.zeros_like(C); band[y0:y1,x0:x1]=1
        C=np.where(band>0,C&rr,C).astype(np.uint8)
    masks={}
    kinds=list(sd.keys())
    # markers per actor
    mk={}
    for k in kinds:
        m=sd[k].copy()
        mk[k]=m
    if 'vil' in cfg.kinds and 'hero' in kinds:
        # villain bare torso: skin pixels not close to hero core
        r,g,b=chans(im); sk=((r>135)&(r>g+22)&(g>b+8)&((r-g)<95)&(b>45)&(r<252)).astype(np.uint8)
        sk=cv2.morphologyEx(sk,cv2.MORPH_OPEN,K3(5))
        far=1-cv2.dilate(mk['hero'],circ(cell*2.2))
        mk['vil']=mk['vil']|(sk&far)
    elif 'vil' in cfg.kinds:
        r,g,b=chans(im); sk=((r>135)&(r>g+22)&(g>b+8)&((r-g)<95)&(b>45)&(r<252)).astype(np.uint8)
        mk['vil']=mk['vil']|cv2.morphologyEx(sk,cv2.MORPH_OPEN,K3(5))
    # keep candidate comps linked (2.5 cells) to any marker
    link=cv2.dilate(C,circ(cell*0.9))
    n,l,st,_=cv2.connectedComponentsWithStats(link,8)
    keep=np.zeros_like(C)
    for k in range(1,n):
        sel=(l==k)
        if any((mk[a][sel]&C[sel]).sum()>=60 for a in mk): keep[sel]=1
    C=C&keep
    # assign pixels to nearest marker actor
    if len(mk)>1:
        best=None
        dists={}
        for a,m in mk.items():
            if m.sum()==0: dists[a]=np.full(C.shape,1e9,np.float32); continue
            dists[a]=cv2.distanceTransform(1-m,cv2.DIST_L2,3)
        stack=np.stack([dists[a] for a in mk],0); who=stack.argmin(0)
        for idx,a in enumerate(mk): masks[a]=(C&(who==idx)).astype(np.uint8)
    else:
        a=list(mk)[0]; masks[a]=C
    out={}
    for a,m in masks.items():
        if m.sum()==0: out[a]=m; continue
        near=cv2.dilate(m,circ(cell*1.3))
        dk=(dark_mask(im).astype(np.uint8)&near); lt=(light_mask(im).astype(np.uint8)&near)
        if a=='vil': lt[:]=0
        mm=m|dk|lt
        mm=cv2.morphologyEx(mm,cv2.MORPH_CLOSE,circ(cell*0.55))
        mm=cv2.morphologyEx(mm,cv2.MORPH_OPEN,K3(5))
        # fill holes
        cnt,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        filled=np.zeros_like(mm); cv2.drawContours(filled,cnt,-1,1,-1)
        # keep linked comps near the biggest
        lk=cv2.dilate(filled,circ(cell*1.6)); n,l,st,_=cv2.connectedComponentsWithStats(lk,8)
        if n>1:
            k=max((filled[l==k].sum(),k) for k in range(1,n))[1]; filled=filled*(l==k)
        out[a]=filled.astype(np.uint8)
    return out
COL={'hero':(255,0,255),'vil':(0,200,255),'girl':(255,255,0)}
def overlay_multi(im, masks, label=None):
    ov=im.copy()
    for a,m in masks.items():
        c=np.array(COL[a],np.uint8)
        ov[m>0]=(0.5*ov[m>0]+0.5*c).astype(np.uint8)
        cnt,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cv2.drawContours(ov,cnt,-1,(255,255,255),2)
    if label is not None: cv2.putText(ov,str(label),(10,40),cv2.FONT_HERSHEY_SIMPLEX,1.4,(0,255,255),3)
    return ov
CFGS={
 'croc': Cfg(kinds=['hero'],cell=14,teal_min_g=60,tau=22,roi_r=100,skin_near={'hero':2.6}),
 'water':Cfg(kinds=['hero'],cell=14,teal_min_g=60,tau=22,roi_r=100,skin_near={'hero':2.6}),
 'fire': Cfg(kinds=['hero'],cell=14,teal_min_g=105,tau=22,roi_r=100,skin_near={'hero':2.6}),
 'scaf': Cfg(kinds=['hero'],cell=10,teal_min_g=60,tau=22,roi_r=80,skin_near={'hero':3.0}),
 'ur':   Cfg(kinds=['hero'],cell=10,teal_min_g=60,tau=22,roi_r=80,skin_near={'hero':3.0}),
 'vil':  Cfg(kinds=['hero','vil'],cell=14,teal_min_g=95,vil_rule='maroon',tau=24,roi_r=90,extra_pal=True,band=(590,105,1265,305),skin_near={'hero':2.6}),
 'fight':Cfg(kinds=['hero','vil'],cell=14,teal_min_g=95,vil_rule='olive',tau=24,roi_r=90,extra_pal=True,band=(465,145,1340,340),skin_near={'hero':2.6}),
 'girlA':Cfg(kinds=['girl'],cell=14,tau=22,roi_r=90,skin_near={'girl':5.5}),
 'girlB':Cfg(kinds=['girl'],cell=14,tau=22,roi_r=90,skin_near={'girl':5.5}),
 'girlC':Cfg(kinds=['girl'],cell=14,tau=22,roi_r=90,skin_near={'girl':5.5}),
}
if __name__=='__main__':
    name=sys.argv[1]; a,b,st=map(int,sys.argv[2:5]); cfg=CFGS[name]
    frames=list(range(a,b+1,st))
    cen=build_palette(frames[::max(1,len(frames)//14)],cfg)
    np.save(S+f'lab/pal_{name}.npy',cen)
    tiles=[]
    for i in frames:
        im=cv2.imread(FR%i); mk=segment_frame(im,cfg,cen); tiles.append(overlay_multi(im,mk,i))
    cv2.imwrite(S+f'lab/seg4_{name}.png',sheet(tiles))
