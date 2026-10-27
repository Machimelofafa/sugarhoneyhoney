import numpy as np, cv2, sys
sys.path.insert(0,'.')
from seg2 import chans, dark_mask, light_mask, K3, overlay, sheet, FR, S
def hero_groups(im, teal_min_g, cell):
    r,g,b=chans(im)
    gold=(r>110)&(g>75)&(b<80)&((r-g)>18)&((r-g)<95)&((g-b)>38)
    teal=(g>r+48)&(b>r+30)&(g>=teal_min_g)&(g>=b-8)&(b<g+30)
    return gold,teal
def skin_gen(im, rmin=78):
    r,g,b=chans(im)
    return (r>rmin)&(r>g+4)&(g>b+2)&((r-g)<70)&((g-b)<62)&(r<250)&(b>25)
def pick_group(core_mask, weight_masks, cell):
    """link components within 2.5 cells; choose the group with max weighted area"""
    link=cv2.dilate(core_mask,K3(int(cell*2.5)|1))
    n,l,st,_=cv2.connectedComponentsWithStats(link,8)
    best=(-1,0)
    for k in range(1,n):
        sel=(l==k)
        sc=sum(w*(m[sel].sum()) for m,w in weight_masks)
        if sc>best[0]: best=(sc,k)
    return (l==best[1]) if best[1] else np.zeros_like(core_mask,bool)
def finish(base, im, cell, dark=True, light=True, keep_link=True):
    near2=cv2.dilate(base,K3(int(cell*1.3)|1))
    m=base.copy()
    if dark: m|= (dark_mask(im).astype(np.uint8)&near2)
    if light: m|= (light_mask(im).astype(np.uint8)&near2)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,K3(int(cell*0.9)|1))
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,K3(5))
    return m
def hero_mask(im, teal_min_g=95, cell=14, skin_rmin=78):
    gold,teal=hero_groups(im,teal_min_g,cell)
    core=(gold|teal).astype(np.uint8); core=cv2.morphologyEx(core,cv2.MORPH_OPEN,K3(3))
    if core.sum()==0: return core
    g1=pick_group(core,[(teal.astype(np.uint8),2.0),(gold.astype(np.uint8),1.0)],cell)
    core=(core&g1).astype(np.uint8)
    near=cv2.dilate(core,K3(int(cell*1.6)|1))
    sk=(skin_gen(im,skin_rmin).astype(np.uint8)&near); sk=cv2.morphologyEx(sk,cv2.MORPH_OPEN,K3(3))
    m=finish((core|sk).astype(np.uint8),im,cell)
    link=cv2.dilate(m,K3(int(cell*2.5)|1)); n,l,st,_=cv2.connectedComponentsWithStats(link,8)
    if n<2: return m
    k=max((m[l==k].sum(),k) for k in range(1,n))[1]
    return (m*(l==k)).astype(np.uint8)
def vil_groups(im):
    r,g,b=chans(im)
    skin=(r>135)&(r>g+22)&(g>b+8)&((r-g)<95)&(b>45)&(r<252)
    pants=(r>42)&(r<135)&(g>32)&(g<112)&(b>14)&(b<92)&(r>=g-2)&(g>=b-6)&((r-b)>12)&((r-g)<38)
    return skin, pants
def vil_mask(im, cell=14):
    skin,pants=vil_groups(im)
    skin=skin.astype(np.uint8); pants=pants.astype(np.uint8)
    skin=cv2.morphologyEx(skin,cv2.MORPH_OPEN,K3(5)); pants=cv2.morphologyEx(pants,cv2.MORPH_OPEN,K3(5))
    core=skin|pants
    if core.sum()==0: return core
    g1=pick_group(core,[(skin,1.0),(pants,1.0)],cell)
    core=(core&g1).astype(np.uint8)
    m=finish(core,im,cell)
    return m
def girl_groups(im):
    r,g,b=chans(im)
    dress=(r>160)&(g<125)&((r-g)>90)&(b>45)&(b<200)&(b<r)
    return dress
def girl_mask(im, cell=14):
    dress=girl_groups(im).astype(np.uint8); dress=cv2.morphologyEx(dress,cv2.MORPH_OPEN,K3(3))
    if dress.sum()==0: return dress
    g1=pick_group(dress,[(dress,1.0)],cell); core=(dress&g1).astype(np.uint8)
    near=cv2.dilate(core,K3(int(cell*2.2)|1))
    sk=(skin_gen(im,70).astype(np.uint8)&near); sk=cv2.morphologyEx(sk,cv2.MORPH_OPEN,K3(3))
    m=finish((core|sk).astype(np.uint8),im,cell)
    return m
FUN={'hero':hero_mask,'vil':vil_mask,'girl':girl_mask}
if __name__=='__main__':
    kind=sys.argv[1]; a,b,st=map(int,sys.argv[2:5]); out=sys.argv[5]; cell=int(sys.argv[6]); tmg=int(sys.argv[7]) if len(sys.argv)>7 else 95
    tiles=[]
    for i in range(a,b+1,st):
        im=cv2.imread(FR%i)
        m=hero_mask(im,tmg,cell) if kind=='hero' else FUN[kind](im,cell)
        tiles.append(overlay(im,m,i))
    cv2.imwrite(S+f'lab/{out}.png',sheet(tiles))
