#!/usr/bin/env python3
"""STEINER AND THE TANTRALOKA
The Threefold Body and the 36 Tattvas"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import asdict, dataclass
from pathlib import Path; from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parent
OUTPUT=Path("/mnt/HC_Volume_106427611/goldrender/output_steiner_tantraloka")
FRAMES=OUTPUT/"frames"; SCENES_DIR=OUTPUT/"scenes"; W=1280; H=720; FPS=10
IVORY=(249,247,241); WHITE=(255,254,250); INK=(29,33,39); SOFT_INK=(86,91,98)
SILVER=(180,187,194); PALE_SILVER=(224,228,228); CYAN=(57,156,180); PALE_CYAN=(196,227,233)
GOLD=(194,156,72); PALE_GOLD=(236,219,175); GREEN=(70,139,99); PALE_GREEN=(196,225,206)
CRIMSON=(162,58,69); VIOLET=(109,83,153); PALE_VIOLET=(218,208,235)
FS="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"; FSB=FS.replace("Serif","Serif-Bold")
FNS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FNSB=FNS.replace("Sans","Sans-Bold")
def clamp(x,l=0.0,h=1.0): return max(l,min(h,x))
def lerp(a,b,t): return a+(b-a)*clamp(t)
def mix(a,b,t): return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smoothstep(a,b,x):
    if a==b: return 1.0 if x>=b else 0.0
    q=clamp((x-a)/(b-a)); return q*q*(3-2*q)
def ease(t): t=clamp(t); return .5-.5*math.cos(math.pi*t)
def font(p,s):
    for c in (p,FS,FNS):
        try: return ImageFont.truetype(c,s)
        except: pass
    return ImageFont.load_default()
def layer(s): return Image.new("RGBA",s,(0,0,0,0))
def field(w,h,seed):
    r=np.random.default_rng(seed); a=np.empty((h,w,3),dtype=np.float32); a[:]=IVORY
    a+=r.normal(0,.9,(h,w,1)); yy,xx=np.mgrid[0:h,0:w]
    h2=np.exp(-(((xx-w*.5)/(w*.37))**2+((yy-h*.40)/(h*.31))**2)*2)
    a[...,1]+=h2*3.2; a[...,2]+=h2*4.6
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8),"RGB").convert("RGBA")
def centered(d,xy,t,f,fill=INK): d.text(xy,t,font=f,fill=fill,anchor="mm")
def seal(im,t,s="",c=INK):
    w2,h2=im.size; d=ImageDraw.Draw(im)
    centered(d,(w2/2,h2*.875),t,font(FSB,max(22,int(h2*.04))),c)
    if s: centered(d,(w2/2,h2*.923),s,font(FNS,max(13,int(h2*.019))),SOFT_INK)
def border(im):
    w2,h2=im.size; d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w2-26,h2-26),radius=18,outline=(*INK,45),width=2)
def glow_circle(im,x,y,r,c,a=170,b=14):
    gl=layer(im.size); ImageDraw.Draw(gl).ellipse((x-r,y-r,x+r,y+r),fill=(*c,int(a)))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(b)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).ellipse((x-r*.34,y-r*.34,x+r*.34,y+r*.34),fill=(*mix(c,WHITE,.35),min(255,int(a)+50)))
    im.alpha_composite(fg)
def glow_line(im,pts,c,w=4,a=210,b2=11):
    if len(pts)<2: return; gl=layer(im.size)
    ImageDraw.Draw(gl).line(pts,fill=(*c,int(a)),width=w*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(b2)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(pts,fill=(*mix(c,WHITE,.08),min(255,int(a)+25)),width=w,joint="curve")
    im.alpha_composite(fg)
def partial(pts,a):
    if not pts: return []; a=clamp(a)
    if a>=1: return pts; k=a*(len(pts)-1); i=int(k); f=k-i
    out=list(pts[:i+1])
    if i+1<len(pts): p,q=pts[i],pts[i+1]; out.append((lerp(p[0],q[0],f),lerp(p[1],q[1],f)))
    return out
def arrow(d,a,b,c=INK,w=3,h2=10):
    d.line((*a,*b),fill=c,width=w); ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s2 in(-1,1): p=(b[0]-math.cos(ang+s2*.52)*h2,b[1]-math.sin(ang+s2*.52)*h2); d.line((*b,*p),fill=c,width=w)

def draw_microtubule(im,cx,cy,w2,reveal=1.0,phase=0.0):
    d=ImageDraw.Draw(im); prev=None
    for i in range(int(20*reveal)):
        q=i/19; x=cx-w2/2+q*w2; y=cy+math.sin(q*math.tau*6+phase)*6
        d.ellipse((x-3,y-3,x+3,y+3),fill=(*CYAN,200),outline=(*CYAN,150),width=1)
        if prev: d.line((prev[0],prev[1],x,y),fill=(*CYAN,120),width=2)
        prev=(x,y)

def draw_godel(im,cx,cy,size,alpha=200):
    d=ImageDraw.Draw(im)
    d.text((cx-size*.4,cy-size*.2),"G -> ~Provable(G)",font=font(FNS,16),fill=(*INK,alpha))
    d.text((cx-size*.4,cy+size*.1),"~Provable(G) is TRUE",font=font(FNS,16),fill=(*CRIMSON,alpha))



def vis_v0(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"Rudolf Steiner's spiritual science","The Threefold Body and the 36 Tattvas")

def vis_v1(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"The threefold body: physical, etheric, astral","The Threefold Body and the 36 Tattvas")

def vis_v2(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"The sevenfold body and the 36 tattvas","The Threefold Body and the 36 Tattvas")

def vis_v3(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"Cosmic evolution and tattva descent","The Threefold Body and the 36 Tattvas")

def vis_v4(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"Imagination, inspiration, intuition as upayas","The Threefold Body and the 36 Tattvas")

def vis_v5(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"The guardian of the threshold","The Threefold Body and the 36 Tattvas")

def vis_v6(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"Steiner meets Abhinavagupta","The Threefold Body and the 36 Tattvas")

def vis_v7(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"The five states of consciousness","The Threefold Body and the 36 Tattvas")

def vis_v8(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"The daimon as higher self","The Threefold Body and the 36 Tattvas")

def vis_v9(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"Two traditions, one path","The Threefold Body and the 36 Tattvas")

@dataclass
class Scene:
    title:str; narration:str; duration:float; visual:str; params:dict
VISUALS = { "vis_v0": vis_v0, "vis_v1": vis_v1, "vis_v2": vis_v2, "vis_v3": vis_v3, "vis_v4": vis_v4, "vis_v5": vis_v5, "vis_v6": vis_v6, "vis_v7": vis_v7, "vis_v8": vis_v8, "vis_v9": vis_v9 }
SCENES = [ Scene("Rudolf Steiner's spiritual science","The Threefold Body and the 36 Tattvas",7.0,"vis_v0",{}), Scene("The threefold body: physical, etheric, astral","The Threefold Body and the 36 Tattvas",7.0,"vis_v1",{}), Scene("The sevenfold body and the 36 tattvas","The Threefold Body and the 36 Tattvas",7.0,"vis_v2",{}), Scene("Cosmic evolution and tattva descent","The Threefold Body and the 36 Tattvas",7.0,"vis_v3",{}), Scene("Imagination, inspiration, intuition as upayas","The Threefold Body and the 36 Tattvas",7.0,"vis_v4",{}), Scene("The guardian of the threshold","The Threefold Body and the 36 Tattvas",7.0,"vis_v5",{}), Scene("Steiner meets Abhinavagupta","The Threefold Body and the 36 Tattvas",7.0,"vis_v6",{}), Scene("The five states of consciousness","The Threefold Body and the 36 Tattvas",7.0,"vis_v7",{}), Scene("The daimon as higher self","The Threefold Body and the 36 Tattvas",7.0,"vis_v8",{}), Scene("Two traditions, one path","The Threefold Body and the 36 Tattvas",7.0,"vis_v9",{}) ]
def rf(sc,fi,fc,w2,h2,se):
    u=fi/max(1,fc-1); t=u*sc.duration; im=field(w2,h2,se)
    VISUALS[sc.visual](im,u,t,sc.params); border(im); return im.convert("RGB")
def _ff():
    f2=shutil.which("ffmpeg")
    if not f2: raise RuntimeError("ffmpeg required"); return f2
def es(idx,f2):
    o=SCENES_DIR/f"scene_{idx:03d}.mp4"; d=FRAMES/f"scene_{idx:03d}"
    subprocess.run([_ff(),"-y","-framerate",str(f2),"-i",str(d/"%05d.jpg"),"-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(o)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return o
def rs(idx,s,f2,w2,h2,prev):
    d=FRAMES/f"scene_{idx:03d}"; d.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
    cnt=max(2,round(s.duration*f2))
    if prev:
        for oi,fi2 in enumerate([0,int(cnt*.33),int(cnt*.72),cnt-1]): rf(s,fi2,cnt,w2,h2,idx*10000+fi2).save(d/f"preview_{oi:02d}.jpg",quality=95); return d
    for fi2 in range(cnt):
        p=d/f"{fi2:05d}.jpg"
        if p.exists(): continue; rf(s,fi2,cnt,w2,h2,idx*10000+fi2).save(p,quality=95,subsampling=0)
    return es(idx,f2)
def concat(paths):
    cp=OUTPUT/"concat.txt"; cp.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    final=OUTPUT/"steiner_tantraloka.mp4"
    subprocess.run([_ff(),"-y","-f","concat","-safe","0","-i",str(cp),"-c","copy","-movflags","+faststart",str(final)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return final
def export_timeline():
    cursor=0.0; recs=[]
    for i,s in enumerate(SCENES,1):
        item=asdict(s); item["scene_id"]=f"scene_{i:03d}"; item["start_seconds"]=round(cursor,3); cursor+=s.duration; item["end_seconds"]=round(cursor,3); recs.append(item)
    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({"title":"steiner_tantraloka","scene_count":len(SCENES),"runtime_seconds":round(cursor,3),"shot_duration_range":[5,10],"scenes":recs},indent=2,ensure_ascii=False),encoding="utf-8"); return p
def contact_sheet(w2,h2):
    tw,th=320,int(320*h2/w2); cols,rows=4,math.ceil(len(SCENES)/4); ch=th+48
    s=Image.new("RGB",(cols*tw,rows*ch),IVORY); d2=ImageDraw.Draw(s); lf=font(FNSB,14)
    for i,sc in enumerate(SCENES,1):
        cnt=max(2,round(sc.duration*FPS)); im=rf(sc,int(cnt*.72),cnt,w2,h2,i*10000+72); im.thumbnail((tw,th)); sl=i-1
        x=(sl%cols)*tw; y=(sl//cols)*ch; s.paste(im,(x,y)); d2.text((x+9,y+th+7),f"{i:02d}  {sc.title}",font=lf,fill=INK)
    p=OUTPUT/"contact_sheet.jpg"; s.save(p,quality=94); return p
def parse_args():
    p2=argparse.ArgumentParser()
    p2.add_argument("--fps",type=int,default=FPS); p2.add_argument("--width",type=int,default=W); p2.add_argument("--height",type=int,default=H)
    p2.add_argument("--scene",type=int); p2.add_argument("--preview",action="store_true"); p2.add_argument("--no-contact-sheet",action="store_true")
    return p2.parse_args()
def main():
    a2=parse_args()
    OUTPUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
    tl=export_timeline(); total=sum(s.duration for s in SCENES)
    print(f"Timeline: {tl}\nScenes: {len(SCENES)}\nRuntime: {total/60:.2f} min")
    if a2.scene:
        if not 1<=a2.scene<=len(SCENES): raise ValueError("scene range")
        print(rs(a2.scene,SCENES[a2.scene-1],a2.fps,a2.width,a2.height,a2.preview)); return
    rendered=[]
    for i,s in enumerate(SCENES,1):
        print(f"[{i:02d}/{len(SCENES):02d}] {s.title} ({s.duration:.1f}s)")
        rendered.append(rs(i,s,a2.fps,a2.width,a2.height,a2.preview))
    final=concat(rendered); print(f"Final: {final}")
    if not a2.no_contact_sheet: print(f"Contact: {contact_sheet(a2.width,a2.height)}")
    print("Done.")
if __name__=="__main__": main()
