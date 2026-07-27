#!/usr/bin/env python3
"""
THE SOUL CARRIES ITS OWN ORACLE
Synesius, Dream Divination, and the Portable Temple of Phantasia

An original Imaginarium visual essay and Platinum-house procedural renderer.

THESIS
------
Synesius of Cyrene makes a radical claim in De insomniis:
the divine did not reserve revelation for wealthy pilgrims, public temples,
or professional priests. Every person carries a mobile oracle in the soul's
imaginative vehicle. In sleep, bodily noise subsides and phantasia becomes
a mirror in which higher, lower, personal, cosmic, truthful, and distorted
influences can all appear.

The oracle is therefore universal—but not automatically reliable.
Its mirror must be purified. Its symbols must be studied. Its private language
must be learned through a "night book." Dream interpretation becomes neither
a fixed dictionary nor passive superstition, but a disciplined art joining
ethics, self-knowledge, cosmic sympathy, and philosophical ascent.

SOURCE CONSTELLATION
--------------------
• Synesius of Cyrene, De insomniis / On Dreams
• the imaginative spirit (phantastikon pneuma) and vehicle of the soul
• cosmic sympathy and dream-divination
• the democratic, portable oracle
• the night book and personal dream-symbol lexicon
• Macrobius' taxonomy: enigmatic, prophetic, oracular, nightmare, apparition
• Artemidorus' contextual method and resistance to universal symbol dictionaries
• late Platonic ascent, purification, and theurgy
• Corbinian imaginal mediation
• Kashmir Śaiva svapna, ābhāsa, pratibhā, and recognition
• modern generative models and offline learning, used carefully as comparison

DESIGN CONTRACT
---------------
• Every shot lasts 5–10 seconds.
• Every shot visibly performs the narrated operation.
• Clean white philosophical field; deep indigo only for nocturnal and intelligible depth.
• No static slide layouts and no decorative loops.
• Silver = phantasia as mirror / dream trace / personal symbolic memory
• Gold = intelligible disclosure / true orientation / philosophical ascent
• Cyan = pneuma, breath, sensory residue, embodied mediation
• Violet = imaginal depth, symbolic transmutation, nocturnal world
• Crimson = bodily turbulence, passion, distortion, false interpretation
• Green = purification, integration, ethical fruit, waking application
• Graphite = ordinary life, material embodiment, historical method
• Continuity object: a small inner sanctuary carried inside a translucent pneumatic sphere.
• The sanctuary changes from cloudy mirror to portable oracle to ascent vehicle.
• Dreams are never presented as automatically prophetic.
• Scientific comparisons never prove Neoplatonic metaphysics.
• Final criterion: the oracle becomes clearer as the life becomes more ordered.

OUTPUT
------
output_synesius_oracle/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  the_soul_carries_its_own_oracle.mp4
  narration_timeline.json
  original_essay.md
  contact_sheet.jpg

REQUIREMENTS
------------
pip install pillow numpy
ffmpeg must be on PATH.

USAGE
-----
python the_soul_carries_its_own_oracle_synesius_platinum.py
python the_soul_carries_its_own_oracle_synesius_platinum.py --preview
python the_soul_carries_its_own_oracle_synesius_platinum.py --scene 12
python the_soul_carries_its_own_oracle_synesius_platinum.py --fps 12 --width 1920 --height 1080
"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/"output_synesius_oracle"
FRAMES=OUTPUT/"frames"
SCENES_DIR=OUTPUT/"scenes"

DEFAULT_WIDTH=1280
DEFAULT_HEIGHT=720
DEFAULT_FPS=10

WHITE=(248,247,243); INK=(28,31,35); SOFT=(84,88,94)
SILVER=(177,184,190); PALE_SILVER=(224,227,229)
GOLD=(194,153,68); PALE_GOLD=(235,218,175)
CYAN=(55,153,181); PALE_CYAN=(192,226,233)
VIOLET=(104,79,146); PALE_VIOLET=(216,205,232)
CRIMSON=(158,52,66); PALE_CRIMSON=(230,192,198)
GREEN=(70,139,98); PALE_GREEN=(194,225,206)
LAPIS=(48,72,124); NIGHT=(17,23,39); VOID=(22,25,31)

FS="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FSB="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FSS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FSSB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def clamp(x,a=0,b=1): return max(a,min(b,x))
def lerp(a,b,t): return a+(b-a)*t
def mix(a,b,t):
    t=clamp(t); return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smooth(a,b,x):
    if a==b:return float(x>=b)
    q=clamp((x-a)/(b-a)); return q*q*(3-2*q)
def ease(t): return .5-.5*math.cos(math.pi*clamp(t))
def pulse(t,hz=1,phase=0): return .5+.5*math.sin(math.tau*(hz*t+phase))

def font(path,size):
    for p in (path,FS,FSS):
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()

def bg(w,h,seed,dark=False):
    rng=np.random.default_rng(seed); base=NIGHT if dark else WHITE
    arr=np.empty((h,w,3),np.float32); arr[:]=base
    arr += rng.normal(0,1.05 if not dark else 1.7,(h,w,1))
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")

def layer(im): return Image.new("RGBA",im.size,(0,0,0,0))
def ctext(d,xy,text,f,fill=INK): d.text(xy,text,font=f,fill=fill,anchor="mm")

def seal(im,title,subtitle="",dark=False,color=INK):
    w,h=im.size; d=ImageDraw.Draw(im)
    ctext(d,(w/2,h*.875),title,font(FSB,max(22,int(h*.042))),WHITE if dark else color)
    if subtitle: ctext(d,(w/2,h*.925),subtitle,font(FSS,max(13,int(h*.020))),PALE_SILVER if dark else SOFT)

def border(im,dark=False):
    w,h=im.size
    ImageDraw.Draw(im).rounded_rectangle((25,25,w-25,h-25),radius=17,
        outline=(*(WHITE if dark else INK),42),width=2)

def glow_line(im,pts,col,width=4,blur=14,alpha=220):
    if len(pts)<2:return
    ov=layer(im); d=ImageDraw.Draw(ov)
    d.line(pts,fill=(*col,alpha),width=width,joint="curve")
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur))); im.alpha_composite(ov)

def glow_circle(im,x,y,r,col,alpha=180,blur=16):
    ov=layer(im); d=ImageDraw.Draw(ov)
    d.ellipse((x-r,y-r,x+r,y+r),fill=(*col,alpha))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).ellipse((x-r*.38,y-r*.38,x+r*.38,y+r*.38),
        fill=(*mix(col,WHITE,.3),230))

def partial(points,p):
    p=clamp(p)
    if len(points)<2:return points
    lens=[math.dist(a,b) for a,b in zip(points[:-1],points[1:])]
    total=sum(lens); target=total*p; out=[points[0]]; walked=0
    for i,L in enumerate(lens):
        if walked+L<=target:
            out.append(points[i+1]); walked+=L
        else:
            q=(target-walked)/L if L else 0
            a,b=points[i],points[i+1]
            out.append((lerp(a[0],b[0],q),lerp(a[1],b[1],q))); break
    return out

def arrow(d,a,b,col=INK,width=3,head=11):
    d.line((*a,*b),fill=col,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for delta in (2.55,-2.55):
        p=(b[0]+math.cos(ang+delta)*head,b[1]+math.sin(ang+delta)*head)
        d.line((*b,*p),fill=col,width=width)

def star_field(d,w,h,seed=5,alpha=95):
    rng=random.Random(seed)
    for _ in range(100):
        x=rng.uniform(w*.08,w*.92); y=rng.uniform(h*.08,h*.72)
        r=rng.choice([1,1,1,2])
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*PALE_GOLD,alpha))

def person(d,cx,cy,scale=1,col=INK,alpha=190):
    d.ellipse((cx-12*scale,cy-54*scale,cx+12*scale,cy-30*scale),outline=(*col,alpha),width=3)
    d.line((cx,cy-30*scale,cx,cy+25*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy-5*scale,cx-28*scale,cy+20*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy-5*scale,cx+28*scale,cy+20*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy+25*scale,cx-18*scale,cy+62*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy+25*scale,cx+18*scale,cy+62*scale),fill=(*col,alpha),width=4)

def sanctuary(d,cx,cy,wid,hei,col=SILVER,alpha=190,open_amt=0):
    d.rounded_rectangle((cx-wid/2,cy-hei/2,cx+wid/2,cy+hei/2),radius=18,
                        outline=(*col,alpha),width=4)
    d.polygon([(cx-wid*.58,cy-hei/2),(cx,cy-hei*.78),(cx+wid*.58,cy-hei/2)],
              outline=(*col,alpha))
    inner_w=wid*.34
    d.rounded_rectangle((cx-inner_w/2,cy-hei*.10,cx+inner_w/2,cy+hei/2),
                        radius=10,fill=(*mix(PALE_VIOLET,VOID,.65),int(210*open_amt)),
                        outline=(*GOLD,int(180*open_amt)),width=3)

def pneumatic_sphere(d,cx,cy,rx,ry,col=CYAN,alpha=130):
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(*col,alpha),width=4)
    for i in range(4):
        rrx=rx*(.45+.13*i)
        rry=ry*(.45+.13*i)
        d.arc((cx-rrx,cy-rry,cx+rrx,cy+rry),15,345,fill=(*mix(CYAN,VIOLET,i/3),70),width=2)

def mirror_disc(d,cx,cy,r,col=SILVER,alpha=180,cloud=0):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(*mix(PALE_SILVER,PALE_CRIMSON,cloud),90),
              outline=(*col,alpha),width=4)
    for i in range(6):
        y=lerp(cy-r*.7,cy+r*.7,i/5)
        d.line((cx-r*.70,y,cx+r*.70,y-8),fill=(*WHITE,70),width=2)

def cloud_field(im,cx,cy,rx,ry,amount,seed=4):
    rng=random.Random(seed)
    ov=layer(im); d=ImageDraw.Draw(ov)
    for _ in range(36):
        x=cx+rng.uniform(-rx,rx)
        y=cy+rng.uniform(-ry,ry)
        r=rng.uniform(10,30)*amount
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*CRIMSON,int(18+55*amount)))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(14)))

def scroll(d,cx,cy,wid,hei,col=PAPER if 'PAPER' in globals() else WHITE,outline=SILVER,alpha=200):
    d.rounded_rectangle((cx-wid/2,cy-hei/2,cx+wid/2,cy+hei/2),radius=12,
                        fill=(*col,alpha),outline=(*outline,alpha),width=3)
    for i in range(7):
        y=cy-hei*.32+i*hei*.10
        d.line((cx-wid*.35,y,cx+wid*.35,y),fill=(*SILVER,90),width=2)

def symbol_node(d,x,y,col,alpha=180):
    d.ellipse((x-10,y-10,x+10,y+10),fill=(*mix(WHITE,col,.2),alpha),outline=(*col,alpha),width=2)

def orbit(d,cx,cy,rx,ry,col,alpha=130,width=3):
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(*col,alpha),width=width)

@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict

def v_portable_oracle(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.56,h*.42; q=ease(u)
    pneumatic_sphere(d,cx,cy,lerp(70,w*.24,q),lerp(45,h*.25,q),CYAN,int(80+80*q))
    sanctuary(d,cx,cy,w*.15,h*.28,mix(SILVER,GOLD,q),int(140+70*q),q)
    person(d,w*.18,h*.49,.65,INK,180)
    glow_line(im,partial([(w*.25,h*.43),(cx-w*.15,h*.43)],q),CYAN,4,11,160)
    seal(im,"THE SOUL CARRIES ITS OWN ORACLE","no pilgrimage can place it nearer")

def v_public_private(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.27,h*.42); right=(w*.73,h*.42)
    # monumental oracle
    sanctuary(d,*left,w*.22,h*.38,INK,180,0)
    for i in range(5):
        person(d,left[0]-80+i*40,h*.67,.35,SILVER,130)
    # inner oracle
    pneumatic_sphere(d,*right,w*.13,h*.18,CYAN,130)
    sanctuary(d,*right,w*.10,h*.20,GOLD,190,ease(u))
    seal(im,"PUBLIC ORACLES REQUIRE ACCESS · DREAMS ARRIVE TO EVERYONE","rich and poor sleep beneath the same sky")

def v_phantasia_mirror(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    pneumatic_sphere(d,cx,cy,w*.25,h*.26,CYAN,130)
    mirror_disc(d,cx,cy,90,mix(SILVER,GOLD,q),190,p.get("cloud",0))
    if p.get("cloud",0)>0:
        cloud_field(im,cx,cy,100,100,p.get("cloud",0),8)
    sanctuary(d,cx,cy,w*.10,h*.19,GOLD,int(120+70*q),q)
    seal(im,"PHANTASIA IS THE DREAM-ORGAN","mirror, screen, vehicle, and translator")

def v_three_level_soul(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    levels=[("INTELLECT",GOLD,h*.16),("PHANTASIA",VIOLET,h*.41),("BODY",CYAN,h*.67)]
    x=w*.5; q=ease(u)
    for i,(txt,col,y) in enumerate(levels):
        d.ellipse((x-66,y-31,x+66,y+31),fill=(*mix(WHITE,col,.15),220),
                  outline=(*col,180),width=3)
        ctext(d,(x,y),txt,font(FSSB,int(h*.014)),col)
        if i>0:
            glow_line(im,partial([(x,levels[i-1][2]+31),(x,y-31)],q),
                      mix(levels[i-1][1],col,.5),4,11,170)
    seal(im,"PHANTASIA MEDIATES","what has no image acquires one; what has no concept becomes interpretable")

def v_cosmic_sympathy(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    star_field(d,w,h,19,75)
    cx,cy=w*.5,h*.42; q=ease(u)
    pneumatic_sphere(d,cx,cy,w*.18,h*.20,CYAN,120)
    sanctuary(d,cx,cy,w*.10,h*.18,GOLD,180,q)
    for i,col in enumerate((GOLD,VIOLET,CYAN,GREEN,CRIMSON)):
        a=-math.pi/2+i*math.tau/5
        x=cx+math.cos(a)*w*.32; y=cy+math.sin(a)*h*.28
        glow_circle(im,x,y,10,col,105,8)
        glow_line(im,partial([(x,y),(cx,cy)],smooth(i*.08,.9,u)),col,3,9,120)
    seal(im,"COSMIC SYMPATHY","distant levels communicate because the cosmos is one articulated life",dark=True)

def v_body_noise(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    pneumatic_sphere(d,cx,cy,w*.24,h*.25,CYAN,110)
    mirror_disc(d,cx,cy,82,SILVER,170,1)
    cloud_field(im,cx,cy,150,130,1,12)
    rng=random.Random(4)
    for _ in range(22):
        x=rng.uniform(w*.20,w*.80); y=rng.uniform(h*.18,h*.66)
        arrow(d,(x,y),(cx,cy),CRIMSON,2,7)
    seal(im,"THE BODY CAN CLOUD THE MIRROR","food, passion, fear, illness, and habit enter the dream")

def v_sleep_quiet(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    pneumatic_sphere(d,cx,cy,w*.24,h*.25,CYAN,int(100+40*q))
    mirror_disc(d,cx,cy,82,mix(SILVER,GOLD,q),180,1-q)
    cloud_field(im,cx,cy,150,130,1-q,12)
    glow_circle(im,cx,cy,15+15*q,GOLD,120,11)
    seal(im,"SLEEP REDUCES THE NOISE OF THE SENSES","but silence alone does not guarantee truth")

def v_purification(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    pneumatic_sphere(d,cx,cy,w*.24,h*.25,mix(CYAN,GREEN,q),130)
    mirror_disc(d,cx,cy,82,mix(SILVER,GOLD,q),190,1-q)
    cloud_field(im,cx,cy,145,125,1-q,11)
    for i,txt in enumerate(("SOBRIETY","CHASTITY","ATTENTION","TRUTHFULNESS")):
        a=-math.pi/2+i*math.tau/4
        x=cx+math.cos(a)*w*.28; y=cy+math.sin(a)*h*.25
        if q>.62: ctext(d,(x,y),txt,font(FSSB,int(h*.012)),GREEN)
    seal(im,"ETHICS POLISHES THE ORACLE","for Synesius, the dreamer's life alters the dream-medium")

def v_ascent(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u); x=w*.5
    levels=[(h*.70,CYAN),(h*.51,VIOLET),(h*.31,GOLD),(h*.12,PALE_GOLD)]
    for i,(y,col) in enumerate(levels):
        glow_circle(im,x,y,14,col,125,10)
        if i>0:
            glow_line(im,partial([(x,levels[i-1][0]-14),(x,y+14)],q),mix(levels[i-1][1],col,.5),5,13,180)
    sanctuary(d,x,lerp(h*.70,h*.13,q),w*.10,h*.18,GOLD,190,q)
    seal(im,"A DREAM CAN BECOME ANAGŌGĒ","an ascent from image toward intelligible orientation",dark=True)

def v_fall_distortion(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u); x=w*.5
    path=[(x,h*.16),(w*.62,h*.31),(w*.39,h*.47),(w*.58,h*.67)]
    glow_line(im,partial(path,q),CRIMSON,6,14,200)
    sanctuary(d,path[min(len(path)-1,int(q*(len(path)-1)))][0],
              path[min(len(path)-1,int(q*(len(path)-1)))][1],w*.09,h*.16,CRIMSON,180,0)
    seal(im,"THE SAME VEHICLE CAN DESCEND","images can clarify, flatter, terrify, or entangle")

def v_macrobius_taxonomy(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    items=[("SOMNIUM",GOLD),("VISIO",CYAN),("ORACULUM",VIOLET),("INSOMNIUM",CRIMSON),("VISUM",SILVER)]
    xs=[w*(.12+i*.19) for i in range(5)]
    for i,((txt,col),x) in enumerate(zip(items,xs)):
        q=smooth(i*.10,.62+i*.06,u)
        d.ellipse((x-44*q,h*.41-44*q,x+44*q,h*.41+44*q),
                  fill=(*mix(WHITE,col,.15),int(220*q)),outline=(*col,int(180*q)),width=3)
        if q>.68:ctext(d,(x,h*.60),txt,font(FSSB,int(h*.012)),col)
    seal(im,"NOT ALL DREAMS BELONG TO ONE CLASS","Macrobius separates enigmatic, prophetic, oracular, anxious, and apparitional dreams")

def v_artemidorus_context(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    center=(w*.5,h*.42)
    scroll(d,*center,w*.24,h*.40,WHITE,SILVER,210)
    contexts=[("AGE",CYAN,w*.20,h*.23),("STATUS",GOLD,w*.80,h*.23),
              ("WORK",VIOLET,w*.20,h*.61),("HEALTH",GREEN,w*.80,h*.61)]
    for i,(txt,col,x,y) in enumerate(contexts):
        q=smooth(i*.10,.65+i*.05,u)
        glow_line(im,partial([(x,y),center],q),col,3,9,120)
        if q>.68:ctext(d,(x,y),txt,font(FSSB,int(h*.013)),col)
    seal(im,"THE SYMBOL CHANGES WITH THE DREAMER","Artemidorus interprets context, not isolated images")

def v_night_book(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    scroll(d,*left,w*.25,h*.42,WHITE,SILVER,210)
    q=ease(u)
    # recurring symbols become a personal graph
    nodes=[(right[0],h*.22,GOLD),(right[0]-95,h*.38,CYAN),(right[0]+95,h*.38,VIOLET),
           (right[0]-75,h*.58,GREEN),(right[0]+75,h*.58,CRIMSON)]
    for i,(x,y,col) in enumerate(nodes):
        symbol_node(d,x,y,col,int(150+40*q))
        if i>0:glow_line(im,partial([(nodes[0][0],nodes[0][1]),(x,y)],smooth(i*.08,.9,u)),col,3,8,110)
    seal(im,"KEEP A NIGHT BOOK","your symbols form a personal language only repeated observation can teach")

def v_personal_lexicon(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    symbols=[("SEA",CYAN,-170,-80),("HOUSE",GOLD,170,-80),("DOG",GREEN,-170,85),("FIRE",CRIMSON,170,85)]
    sanctuary(d,cx,cy,w*.10,h*.18,VIOLET,180,q)
    for i,(txt,col,ox,oy) in enumerate(symbols):
        x=cx+ox; y=cy+oy
        glow_line(im,partial([(x,y),(cx,cy)],smooth(i*.10,.88,u)),col,3,9,120)
        if q>.65:ctext(d,(x,y),txt,font(FSSB,int(h*.014)),col)
    seal(im,"NO UNIVERSAL DICTIONARY IS ENOUGH","the oracle speaks through the dreamer's own history")

def v_dream_poetry(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    sanctuary(d,cx,cy,w*.11,h*.20,GOLD,180,q)
    # one image transforms through analogical chain
    chain=[(w*.15,h*.42,"SEED",GREEN),(w*.34,h*.29,"STAR",GOLD),
           (w*.55,h*.48,"EYE",CYAN),(w*.76,h*.29,"GATE",VIOLET),(w*.88,h*.49,"RETURN",GREEN)]
    for i,(x,y,txt,col) in enumerate(chain):
        symbol_node(d,x,y,col,170)
        if i>0:glow_line(im,partial([(chain[i-1][0],chain[i-1][1]),(x,y)],smooth(i*.08,.92,u)),col,4,10,140)
        if q>.70:ctext(d,(x,y+28),txt,font(FSSB,int(h*.011)),col)
    seal(im,"DREAMS SPEAK BY TRANSMUTATION","one image becomes another while preserving a hidden relation")

def v_democratic_oracle(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    people=[(w*(.12+i*.11),h*(.32 if i%2==0 else .55)) for i in range(8)]
    q=ease(u)
    for i,(x,y) in enumerate(people):
        person(d,x,y,.38,mix(SILVER,GREEN,i/7),160)
        pneumatic_sphere(d,x,y-18,28,22,CYAN,90)
        sanctuary(d,x,y-18,22,38,GOLD,int(90+70*q),q)
    seal(im,"REVELATION IS DEMOCRATIZED","the slave, the woman, the poor, and the powerful all dream")

def v_theurgy_comparison(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.27,h*.42); right=(w*.73,h*.42)
    # external rite
    sanctuary(d,*left,w*.20,h*.34,GOLD,180,ease(u))
    orbit(d,left[0],left[1],130,90,VIOLET,100)
    # internal dream temple
    pneumatic_sphere(d,*right,w*.14,h*.18,CYAN,120)
    sanctuary(d,*right,w*.10,h*.19,GOLD,180,ease(u))
    seal(im,"DREAMS CAN REPLACE EXPENSIVE THEURGY","the portable rite occurs in the soul's own vehicle")

def v_science_comparison(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.27,h*.42); right=(w*.73,h*.42)
    # generative model
    d.rounded_rectangle((left[0]-100,left[1]-70,left[0]+100,left[1]+70),radius=18,
                        fill=(*PALE_CYAN,215),outline=(*CYAN,180),width=3)
    ctext(d,left,"GENERATIVE\nMODEL",font(FSSB,int(h*.017)),CYAN)
    # pneumatic vehicle
    pneumatic_sphere(d,*right,w*.13,h*.18,VIOLET,140)
    sanctuary(d,*right,w*.09,h*.17,GOLD,180,ease(u))
    q=smooth(.35,.9,u)
    d.line((w*.49,h*.24,w*.51,h*.58),fill=(*CRIMSON,int(210*q)),width=6)
    seal(im,"COMPARISON IS NOT IDENTITY","offline learning does not prove a pneumatic soul")

def v_shaiva_bridge(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.27,h*.42); right=(w*.73,h*.42)
    pneumatic_sphere(d,*left,w*.13,h*.18,CYAN,130)
    sanctuary(d,*left,w*.09,h*.17,GOLD,180,ease(u))
    glow_circle(im,right[0],right[1],20,GOLD,140,12)
    for i in range(12):
        a=i*math.tau/12
        x=right[0]+math.cos(a)*130; y=right[1]+math.sin(a)*85
        col=mix(CYAN,VIOLET,i/11)
        glow_circle(im,x,y,6,col,80,7)
        glow_line(im,[(right[0],right[1]),(x,y)],col,2,7,65)
    seal(im,"SYNESIUS ASKS WHAT DREAMS REVEAL · ŚAIVISM ASKS WHAT DREAMING IS","both meet at the power of appearance")

def v_recognition(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.25,h*.42); right=(w*.75,h*.42)
    person(d,*left,.68,INK,180)
    pneumatic_sphere(d,*right,w*.14,h*.18,CYAN,130)
    sanctuary(d,*right,w*.10,h*.19,GOLD,180,ease(u))
    q=ease(u)
    glow_line(im,partial([left,(w*.50,h*.30),right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.50,h*.56),left],smooth(.30,.95,u)),GOLD,5,13,200)
    seal(im,"THE HIGHEST DREAM RETURNS THE DREAMER TO THE SOURCE OF SEEING","revelation becomes recognition")

def v_ethics(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    sanctuary(d,w*.25,h*.42,w*.10,h*.19,GOLD,180,ease(u))
    fruits=[("SOBRIETY",CYAN,w*.52,h*.25),("HUMILITY",VIOLET,w*.72,h*.33),
            ("COURAGE",GOLD,w*.52,h*.56),("JUSTICE",GREEN,w*.76,h*.60)]
    for i,(txt,col,x,y) in enumerate(fruits):
        q=smooth(i*.10,.65+i*.05,u)
        glow_line(im,partial([(w*.32,h*.42),(x,y)],q),col,3,9,150)
        d.ellipse((x-29*q,y-29*q,x+29*q,y+29*q),
                  fill=(*mix(WHITE,col,.18),int(220*q)),outline=(*col,int(180*q)),width=3)
        if q>.68:ctext(d,(x,y),txt,font(FSSB,int(h*.012)),col)
    seal(im,"THE ORACLE IS TESTED BY THE LIFE IT PRODUCES","clarity without virtue is another cloudy dream")

def v_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.56,h*.42; q=ease(u)
    star_field(d,w,h,29,int(65*q))
    pneumatic_sphere(d,cx,cy,lerp(70,w*.25,q),lerp(50,h*.26,q),mix(CYAN,GOLD,q*.35),int(90+60*q))
    sanctuary(d,cx,cy,w*.15,h*.28,mix(SILVER,GOLD,q),int(150+60*q),q)
    mirror_disc(d,cx,cy,44,mix(SILVER,GOLD,q),180,1-q)
    person(d,w*.17,h*.50,.62,INK,180)
    path=[(w*.24,h*.43),(w*.37,h*.31),(cx-w*.13,h*.40),(cx,cy)]
    glow_line(im,partial(path,q),GOLD,5,13,200)
    seal(im,"THE SOUL CARRIES ITS OWN ORACLE",
         "the temple travels with the dreamer, but must be purified to speak clearly",dark=True,color=GREEN)

VISUALS:dict[str,Callable]={
    "portable":v_portable_oracle,
    "public":v_public_private,
    "phantasia":v_phantasia_mirror,
    "levels":v_three_level_soul,
    "sympathy":v_cosmic_sympathy,
    "noise":v_body_noise,
    "sleep":v_sleep_quiet,
    "purify":v_purification,
    "ascent":v_ascent,
    "fall":v_fall_distortion,
    "macrobius":v_macrobius_taxonomy,
    "artemidorus":v_artemidorus_context,
    "book":v_night_book,
    "lexicon":v_personal_lexicon,
    "poetry":v_dream_poetry,
    "democratic":v_democratic_oracle,
    "theurgy":v_theurgy_comparison,
    "science":v_science_comparison,
    "shaiva":v_shaiva_bridge,
    "recognition":v_recognition,
    "ethics":v_ethics,
    "final":v_final,
}

SCENES:list[Scene]=[
    Scene("Temple journey","Ancient oracles demanded a journey.",6.5,"public",{}),
    Scene("Distance and wealth","One needed distance, wealth, access, sacrifice, and permission.",9.0,"public",{}),
    Scene("Synesius reversal","Synesius of Cyrene reverses the architecture.",8.0,"portable",{}),
    Scene("Oracle inside","The oracle is already inside the traveller.",7.0,"portable",{}),
    Scene("Sleep entrance","Sleep opens its doors each night.",6.5,"portable",{}),
    Scene("Thesis","The soul carries its own oracle.",7.5,"final",{}),

    Scene("Late antique thinker","Synesius was a late antique Platonist who later became a Christian bishop.",9.0,"portable",{}),
    Scene("Sent Hypatia","He sent his treatise On Dreams to Hypatia.",7.0,"portable",{}),
    Scene("Not marginal topic","For him, dreams were not a marginal curiosity.",7.0,"phantasia",{}),
    Scene("Soul cosmology","They revealed how soul, body, image, and cosmos communicate.",9.0,"levels",{}),
    Scene("Dream philosophy","Dream theory became a philosophy of mediation.",8.0,"levels",{}),

    Scene("Phantasia","The central faculty is phantasia.",6.0,"phantasia",{}),
    Scene("Not fantasy only","It does not mean fantasy in the modern dismissive sense.",8.0,"phantasia",{}),
    Scene("Image power","It is the soul's power to receive and produce images.",8.0,"phantasia",{}),
    Scene("Translator","Phantasia translates between what has no body and what has no concept.",9.0,"levels",{}),
    Scene("Intellect image","Intelligible influence acquires image.",7.0,"levels",{}),
    Scene("Body meaning","Bodily disturbance acquires symbolic form.",7.0,"levels",{}),
    Scene("Universal interface","The dream is born at this interface.",7.5,"phantasia",{}),

    Scene("Pneumatic vehicle","Synesius gives phantasia a vehicle.",6.5,"phantasia",{}),
    Scene("Subtle pneuma","A subtle pneuma mediates soul and physical body.",8.0,"levels",{}),
    Scene("Not gross flesh","It is not gross flesh.",6.0,"levels",{}),
    Scene("Not pure intellect","It is not pure intellect.",6.0,"levels",{}),
    Scene("Mobile middle","It is a mobile middle capable of taking form.",8.0,"phantasia",{}),
    Scene("Portable sanctuary","The oracle is therefore portable because its sanctuary travels with the soul.",9.0,"portable",{}),

    Scene("Cosmic sympathy","Why should dreams reveal anything beyond private memory?",9.0,"sympathy",{}),
    Scene("One cosmos","Synesius answers through cosmic sympathy.",7.0,"sympathy",{}),
    Scene("Articulated life","The cosmos is not a pile of isolated things but one articulated life.",9.0,"sympathy",{}),
    Scene("Distant resonance","Distant levels can resonate because they belong to one order.",8.5,"sympathy",{}),
    Scene("Dream receives","The imaginative vehicle receives these relations as image.",8.0,"sympathy",{}),
    Scene("No external telegram","Prophecy is not an external telegram inserted into the skull.",9.0,"sympathy",{}),
    Scene("Relation becomes image","Cosmic relation becomes dream-image.",7.5,"sympathy",{}),

    Scene("Mirror analogy","Synesius repeatedly thinks through mirrors.",7.0,"phantasia",{}),
    Scene("Clear mirror","A clear mirror receives form accurately.",6.5,"phantasia",{}),
    Scene("Distorted mirror","A warped mirror distorts what it receives.",6.5,"noise",{}),
    Scene("Dream medium condition","The condition of phantasia changes the dream.",8.0,"noise",{}),
    Scene("No automatic revelation","Dreaming is universal, but revelation is not automatically clear.",9.0,"noise",{}),

    Scene("Body enters dream","The body enters the oracle.",6.5,"noise",{}),
    Scene("Heavy food","Heavy food can cloud it.",6.0,"noise",{}),
    Scene("Illness","Illness can color it.",5.5,"noise",{}),
    Scene("Fear","Fear can populate it.",5.5,"noise",{}),
    Scene("Desire","Desire can flatter it.",5.5,"noise",{}),
    Scene("Habit","Habit can repeat itself as fate.",6.5,"noise",{}),
    Scene("Dream mixed signal","The dream is often a mixed signal.",7.0,"noise",{}),

    Scene("Sleep quiet","Sleep quiets the external senses.",7.0,"sleep",{}),
    Scene("Not enough","But quiet is not enough.",5.5,"sleep",{}),
    Scene("Cloud remains","A mirror can remain cloudy in darkness.",7.0,"sleep",{}),
    Scene("Ethical preparation","Synesius therefore links divination to ethical preparation.",8.5,"purify",{}),
    Scene("Sober life","Sobriety improves the medium.",6.5,"purify",{}),
    Scene("Chaste bed","Restraint makes the bed resemble an oracle rather than a battlefield of appetites.",9.5,"purify",{}),
    Scene("Truthful waking","Truthful waking prepares truthful dreaming.",7.5,"purify",{}),

    Scene("Purification not payment","This is not payment to a god.",7.0,"purify",{}),
    Scene("Instrument care","It is care for the instrument of reception.",8.0,"purify",{}),
    Scene("Life tunes dream","The life tunes the dream.",6.5,"purify",{}),
    Scene("Dream diagnoses life","The dream in turn diagnoses the life.",7.5,"purify",{}),
    Scene("Circular practice","Oracle and ethics form a circle.",7.0,"purify",{}),

    Scene("Highest dream","At its highest, a dream can become ascent.",7.0,"ascent",{}),
    Scene("Unexpected opening","A soul unprepared by argument may suddenly see a path upward.",9.0,"ascent",{}),
    Scene("Image toward reality","The image opens toward a more perfect vision of reality.",8.5,"ascent",{}),
    Scene("Anagoge","Synesius calls the movement anagōgē—leading upward.",8.0,"ascent",{}),
    Scene("Return origin","The dreamer remembers an origin forgotten in waking dispersion.",9.0,"ascent",{}),

    Scene("Same vehicle danger","But the same vehicle can descend.",7.0,"fall",{}),
    Scene("Passion thickens","Passion thickens the pneuma.",6.5,"fall",{}),
    Scene("Images become sticky","Images become sticky and self-confirming.",7.0,"fall",{}),
    Scene("Nightmare trap","The dreamer becomes trapped inside the image's emotional force.",8.5,"fall",{}),
    Scene("No image authority","No image deserves authority merely because it arrived at night.",9.0,"fall",{}),

    Scene("Ancient classification","Ancient dream theory therefore classified dreams.",7.0,"macrobius",{}),
    Scene("Macrobius five","Macrobius distinguishes five major types.",7.0,"macrobius",{}),
    Scene("Somnium","The enigmatic dream conceals meaning in symbols.",7.0,"macrobius",{}),
    Scene("Visio","The prophetic vision presents a future event directly.",7.0,"macrobius",{}),
    Scene("Oraculum","The oracular dream contains an authoritative figure who speaks.",8.0,"macrobius",{}),
    Scene("Insomnium","The anxious dream repeats waking disturbance.",7.0,"macrobius",{}),
    Scene("Visum","The apparition hovers at the border of sleep and waking.",8.0,"macrobius",{}),
    Scene("Different handling","Different dreams require different handling.",7.5,"macrobius",{}),

    Scene("Artemidorus","Artemidorus offers another discipline.",6.5,"artemidorus",{}),
    Scene("No fixed dictionary","He resists interpretation by fixed dictionary alone.",8.0,"artemidorus",{}),
    Scene("Dreamer context","The dreamer's age, occupation, health, status, habits, and circumstances matter.",9.5,"artemidorus",{}),
    Scene("Same image differs","The same image can mean differently for a sailor, prisoner, ruler, or patient.",9.0,"artemidorus",{}),
    Scene("Symbol relational","A symbol is relational before it is universal.",7.5,"artemidorus",{}),

    Scene("Synesius personal method","Synesius makes the method radically personal.",8.0,"book",{}),
    Scene("Night book","Keep a night book.",5.5,"book",{}),
    Scene("Record immediately","Record the dream before waking reason rearranges it.",8.0,"book",{}),
    Scene("Compare outcomes","Compare images with later events.",7.0,"book",{}),
    Scene("Track repetitions","Track repetitions, inversions, private associations, and emotional tones.",9.0,"book",{}),
    Scene("Become material","Each person must become material for the art.",8.0,"book",{}),

    Scene("Personal lexicon","Your oracle speaks your dialect.",7.0,"lexicon",{}),
    Scene("Sea differs","The sea does not mean the same thing for everyone.",7.0,"lexicon",{}),
    Scene("House differs","A house may be body, family, memory, status, or shelter.",8.0,"lexicon",{}),
    Scene("Dog differs","A dog may be loyalty, danger, appetite, memory, or one actual dog.",8.5,"lexicon",{}),
    Scene("Context learns","Interpretation becomes an empirical art of recurring relations.",8.5,"lexicon",{}),
    Scene("No dream dictionary","The night book defeats the dream dictionary.",7.0,"book",{}),

    Scene("Dream poetry","Dreams rarely speak in discursive propositions.",8.0,"poetry",{}),
    Scene("Condensation","They condense.",5.5,"poetry",{}),
    Scene("Transpose","They transpose.",5.5,"poetry",{}),
    Scene("Personify","They personify.",5.5,"poetry",{}),
    Scene("Invert","They invert.",5.5,"poetry",{}),
    Scene("One becomes another","A seed becomes a star; a star becomes an eye; an eye becomes a gate.",9.0,"poetry",{}),
    Scene("Hidden relation","Meaning persists through metamorphosis rather than literal identity.",8.5,"poetry",{}),

    Scene("Democratic oracle","The political implication is extraordinary.",7.0,"democratic",{}),
    Scene("No monopoly","Dream revelation cannot be monopolized by temples or wealth.",8.0,"democratic",{}),
    Scene("Everyone sleeps","Everyone sleeps.",5.5,"democratic",{}),
    Scene("Everyone carries faculty","Everyone carries phantasia.",6.5,"democratic",{}),
    Scene("Unequal clarity","People differ in clarity, not in possession of the basic faculty.",8.5,"democratic",{}),
    Scene("Universal access","The oracle is universal even when interpretation is difficult.",8.0,"democratic",{}),

    Scene("Dreams and theurgy","This places dreams beside theurgy.",7.0,"theurgy",{}),
    Scene("Theurgy costly","Theurgy may require objects, specialists, timing, and ritual expertise.",8.5,"theurgy",{}),
    Scene("Dream free","Dreaming is free.",5.5,"portable",{}),
    Scene("Temple mobile","Its temple is mobile.",5.5,"portable",{}),
    Scene("Rite nightly","Its rite begins nightly.",5.5,"portable",{}),
    Scene("Synesius polemic","Synesius can therefore present dream-divination as a portable alternative.",8.5,"theurgy",{}),

    Scene("Modern comparison","Modern dream science offers a distant comparison.",7.0,"science",{}),
    Scene("Offline generation","During sleep, brains generate virtual experiences with reduced current input.",9.0,"science",{}),
    Scene("Memory reorganized","Dreaming may reorganize memory and learned representations.",8.0,"science",{}),
    Scene("Novel recombination","It can recombine experience rather than merely replay it.",8.0,"science",{}),
    Scene("No prophecy proof","This does not demonstrate prophecy or cosmic sympathy.",8.0,"science",{}),
    Scene("No pneumatic proof","It does not prove Synesius' pneumatic vehicle.",8.0,"science",{}),
    Scene("Shared question","Both ask what virtual experience does to the structure of a life.",9.0,"science",{}),

    Scene("Shaiva comparison","Kashmir Śaivism pushes the inquiry deeper.",7.0,"shaiva",{}),
    Scene("Dream content question","Synesius asks how dreams carry information.",8.0,"shaiva",{}),
    Scene("Dream appearing question","Śaivism asks what dreaming reveals about appearing itself.",8.5,"shaiva",{}),
    Scene("Svapna","Svapna is a mode in which consciousness manifests a world from within.",8.0,"shaiva",{}),
    Scene("Abhasa","Dream figures are ābhāsas—forms of appearing.",7.0,"shaiva",{}),
    Scene("Pratibha","Pratibhā is the flash in which meaning appears before analysis.",8.0,"shaiva",{}),
    Scene("No collapse","The traditions should not be collapsed.",6.5,"science",{}),

    Scene("Recognition","Their strongest meeting point is recognition.",7.0,"recognition",{}),
    Scene("Image not final","The dream image is not the final reality.",7.0,"recognition",{}),
    Scene("Image turns","It can turn awareness toward the power by which image and dreamer appear.",9.0,"recognition",{}),
    Scene("Oracle inward","The oracle becomes most profound when it reveals the source of revelation.",9.0,"recognition",{}),
    Scene("Prophecy to philosophy","Dream-divination becomes philosophy.",7.0,"recognition",{}),

    Scene("Final test","The final test is not spectacle.",6.5,"ethics",{}),
    Scene("Not vividness","Not vividness.",5.0,"ethics",{}),
    Scene("Not fear","Not fear.",5.0,"ethics",{}),
    Scene("Not prediction hit","Not one prediction that happened to match.",7.0,"ethics",{}),
    Scene("Life fruit","The test is the life produced.",6.5,"ethics",{}),
    Scene("Sobriety fruit","Does the practice increase sobriety?",6.5,"ethics",{}),
    Scene("Humility fruit","Does it reduce self-importance?",6.5,"ethics",{}),
    Scene("Courage fruit","Does it enable difficult action?",6.5,"ethics",{}),
    Scene("Justice fruit","Does it make waking conduct more just?",7.0,"ethics",{}),

    Scene("Final temple","The public temple stands in one place.",6.5,"public",{}),
    Scene("Inner temple travels","The inner temple travels.",6.0,"portable",{}),
    Scene("Mirror receives","Its mirror receives body, memory, cosmos, and intellect.",8.0,"phantasia",{}),
    Scene("Cloud or clarity","It can cloud or clarify.",6.0,"purify",{}),
    Scene("Book teaches language","The night book teaches its language.",7.0,"book",{}),
    Scene("Ethics polish","Ethics polishes its surface.",6.5,"purify",{}),
    Scene("Ascent possibility","Philosophy turns its images toward ascent.",7.0,"ascent",{}),
    Scene("Final thesis","The soul carries its own oracle.",8.0,"final",{}),
    Scene("Final criterion","The oracle speaks most clearly when the dreamer's life becomes capable of hearing.",9.5,"ethics",{}),
]

def export_original_essay():
    lines=["# the soul carries its own oracle","",
           "## Synesius, dream divination, and the portable temple of phantasia",""]
    for s in SCENES: lines += [s.narration,""]
    p=OUTPUT/"original_essay.md"
    p.write_text("\n".join(lines),encoding="utf-8")
    return p

def render_frame(scene,fi,fc,w,h,seed):
    u=fi/max(1,fc-1); t=u*scene.duration
    dark=scene.visual in {"sympathy","ascent","final"}
    im=bg(w,h,seed,dark)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im,dark)
    return im.convert("RGB")

def ffmpeg():
    x=shutil.which("ffmpeg")
    if not x: raise RuntimeError("ffmpeg is required but was not found on PATH")
    return x

def encode(i,fps):
    fd=FRAMES/f"scene_{i:03d}"
    out=SCENES_DIR/f"scene_{i:03d}.mp4"
    subprocess.run([ffmpeg(),"-y","-framerate",str(fps),"-i",str(fd/"%05d.jpg"),
                    "-c:v","libx264","-preset","medium","-crf","18",
                    "-pix_fmt","yuv420p","-movflags","+faststart",str(out)],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def render_scene(i,s,fps,w,h,preview):
    fd=FRAMES/f"scene_{i:03d}"
    fd.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
    fc=max(2,round(s.duration*fps))
    if preview:
        for oi,fi in enumerate([0,int(fc*.35),int(fc*.72),fc-1]):
            render_frame(s,fi,fc,w,h,i*1000+fi).save(fd/f"preview_{oi:02d}.jpg",quality=95)
        return fd
    for fi in range(fc):
        p=fd/f"{fi:05d}.jpg"
        if not p.exists():
            render_frame(s,fi,fc,w,h,i*1000+fi).save(p,quality=95,subsampling=0)
    return encode(i,fps)

def concatenate(paths):
    c=OUTPUT/"concat.txt"
    c.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    out=OUTPUT/"the_soul_carries_its_own_oracle.mp4"
    subprocess.run([ffmpeg(),"-y","-f","concat","-safe","0","-i",str(c),
                    "-c","copy","-movflags","+faststart",str(out)],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def export_timeline():
    cur=0; items=[]
    for i,s in enumerate(SCENES,1):
        r=asdict(s); r["scene_id"]=f"scene_{i:03d}"
        r["start_seconds"]=round(cur,3); cur+=s.duration; r["end_seconds"]=round(cur,3)
        items.append(r)
    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({
        "title":"the soul carries its own oracle",
        "subtitle":"Synesius, dream divination, and the portable temple of phantasia",
        "runtime_seconds":round(cur,3),
        "scene_count":len(SCENES),
        "original_essay":True,
        "style":{
            "continuity_object":"portable sanctuary inside the pneumatic vehicle",
            "shot_duration_range_seconds":[5,10],
            "palette_roles":{
                "silver":"phantasia mirror and dream trace",
                "gold":"intelligible disclosure and ascent",
                "cyan":"pneuma and embodied mediation",
                "violet":"imaginal depth and symbol",
                "crimson":"passion and distortion",
                "green":"purification and ethical integration",
                "graphite":"ordinary embodied life"
            }
        },
        "scenes":items
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return p

def contact_sheet(w,h):
    tw=320; th=int(tw*h/w); thumbs=[]
    for i,s in enumerate(SCENES,1):
        fc=max(2,round(s.duration*DEFAULT_FPS))
        im=render_frame(s,int(fc*.72),fc,w,h,i*1000+72)
        im.thumbnail((tw,th)); thumbs.append((i,s.title,im.copy()))
    cols=4; rows=math.ceil(len(thumbs)/cols)
    sheet=Image.new("RGB",(cols*tw,rows*(th+52)),WHITE)
    d=ImageDraw.Draw(sheet); f=font(FSSB,15)
    for i,title,im in thumbs:
        k=i-1; x=(k%cols)*tw; y=(k//cols)*(th+52)
        sheet.paste(im,(x,y))
        d.text((x+10,y+th+8),f"{i:03d}  {title}",font=f,fill=INK)
    p=OUTPUT/"contact_sheet.jpg"; sheet.save(p,quality=94); return p

def args():
    p=argparse.ArgumentParser()
    p.add_argument("--fps",type=int,default=DEFAULT_FPS)
    p.add_argument("--width",type=int,default=DEFAULT_WIDTH)
    p.add_argument("--height",type=int,default=DEFAULT_HEIGHT)
    p.add_argument("--scene",type=int)
    p.add_argument("--preview",action="store_true")
    p.add_argument("--no-contact-sheet",action="store_true")
    return p.parse_args()

def main():
    a=args()
    OUTPUT.mkdir(parents=True,exist_ok=True)
    FRAMES.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)
    print(f"Essay: {export_original_essay()}")
    print(f"Timeline: {export_timeline()}")
    print(f"Scenes: {len(SCENES)}")
    print(f"Runtime: {sum(s.duration for s in SCENES)/60:.2f} minutes")
    if a.scene:
        if not 1<=a.scene<=len(SCENES): raise ValueError("scene out of range")
        print(render_scene(a.scene,SCENES[a.scene-1],a.fps,a.width,a.height,a.preview))
        return
    rendered=[]
    for i,s in enumerate(SCENES,1):
        print(f"[{i:03d}/{len(SCENES):03d}] {s.title} ({s.duration:.1f}s)")
        r=render_scene(i,s,a.fps,a.width,a.height,a.preview)
        if not a.preview: rendered.append(r)
    if not a.no_contact_sheet: print(f"Contact sheet: {contact_sheet(a.width,a.height)}")
    if not a.preview: print(f"Final video: {concatenate(rendered)}")

if __name__=="__main__":
    main()
