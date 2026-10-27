import numpy as np, cv2
S='/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/'
FR=S+'fr/f_%04d.jpg'
def chans(im):
    b,g,r=[im[...,k].astype(np.int16) for k in range(3)]
    return r,g,b
def hero_core(im, teal_min_g=95):
    r,g,b=chans(im)
    gold=(r>110)&(g>75)&(b<80)&((r-g)>18)&((r-g)<95)&((g-b)>38)
    teal=(g>r+48)&(b>r+30)&(g>=teal_min_g)&(g>=b-8)&(b<g+30)
    return gold, teal
def skin_mask(im):
    r,g,b=chans(im)
    sk=(r>78)&(r>g+4)&(g>b+2)&((r-g)<70)&((g-b)<62)&(r<250)&(b>25)
    return sk
def dark_mask(im, vmax=85):
    r,g,b=chans(im); v=np.maximum(np.maximum(r,g),b)
    return (v<vmax)&((b-r)<50)     # dark but not deep blue/purple
def light_mask(im):
    r,g,b=chans(im); v=np.maximum(np.maximum(r,g),b); mn=np.minimum(np.minimum(r,g),b)
    return (v>150)&((v-mn)<60)
K3=lambda n: np.ones((n,n),np.uint8)
def hero_mask(im, teal_min_g=95, cell=14, extra=None):
    gold,teal=hero_core(im,teal_min_g)
    core=(gold|teal).astype(np.uint8)
    core=cv2.morphologyEx(core,cv2.MORPH_OPEN,K3(3))
    # keep core components with decent size
    n,l,st,_=cv2.connectedComponentsWithStats(core,8)
    keep=np.zeros_like(core)
    for k in range(1,n):
        if st[k,cv2.CC_STAT_AREA]>=0.12*cell*cell*9: keep[l==k]=1
    core=keep
    if core.sum()==0: return core
    near=cv2.dilate(core,K3(int(cell*1.6)|1))
    sk=skin_mask(im).astype(np.uint8)&near
    sk=cv2.morphologyEx(sk,cv2.MORPH_OPEN,K3(3))
    base=(core|sk).astype(np.uint8)
    near2=cv2.dilate(base,K3(int(cell*1.3)|1))
    dk=(dark_mask(im).astype(np.uint8)&near2)
    lt=(light_mask(im).astype(np.uint8)&near2)
    m=(base|dk|lt)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,K3(int(cell*0.9)|1))
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,K3(5))
    # keep every component linked (within ~2.5 cells) to the largest group
    link=cv2.dilate(m,K3(int(cell*2.5)|1))
    n,l,st,_=cv2.connectedComponentsWithStats(link,8)
    if n<2: return m
    areas=[(m[l==k].sum(),k) for k in range(1,n)]
    k=max(areas)[1]
    return (m*(l==k)).astype(np.uint8)
def overlay(im, m, label=None):
    ov=im.copy(); ov[m>0]=(0.45*ov[m>0]+0.55*np.array([255,0,255])).astype(np.uint8)
    cnt,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cv2.drawContours(ov,cnt,-1,(0,255,255),2)
    if label is not None: cv2.putText(ov,str(label),(10,40),cv2.FONT_HERSHEY_SIMPLEX,1.4,(0,255,255),3)
    return ov
def sheet(tiles, cols=6, tw=352, th=264):
    rows=(len(tiles)+cols-1)//cols; sh=np.zeros((rows*th,cols*tw,3),np.uint8)
    for n,t in enumerate(tiles):
        t=cv2.resize(t,(tw,th)); sh[(n//cols)*th:(n//cols+1)*th,(n%cols)*tw:(n%cols+1)*tw]=t
    return sh
if __name__=='__main__':
    import sys
    a,b,st=map(int,sys.argv[1:4]); out=sys.argv[4]; cell=float(sys.argv[5]); tmg=int(sys.argv[6]) if len(sys.argv)>6 else 95
    tiles=[]
    for i in range(a,b+1,st):
        im=cv2.imread(FR%i); m=hero_mask(im,tmg,int(cell)); tiles.append(overlay(im,m,i))
    cv2.imwrite(S+f'lab/{out}.png',sheet(tiles))
