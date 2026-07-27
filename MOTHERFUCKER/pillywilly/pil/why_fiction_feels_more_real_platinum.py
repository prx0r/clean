#!/usr/bin/env python3
"""
WHY FICTION FEELS MORE REAL THAN REALITY
Abhinavagupta's Theory of Rasa

An original Platinum-house procedural visual essay.

CENTRAL QUESTION
----------------
Why can grief in ordinary life crush us, while grief in theatre can become
beautiful, expansive, and even blissful?

ABHINAVAGUPTA'S ANSWER
----------------------
Ordinary emotion is contracted by ownership:

    this happened to me
    this threatens my future
    this defines my identity

Aesthetic experience loosens that contraction.

Through dramatic distance, stylization, performance, memory, suggestion,
shared attention, and sādhāraṇīkaraṇa, emotion becomes universalized.

It is no longer:
    my grief
    your anger
    his courage

It becomes:
    grief
    anger
    courage

This universalized emotion is rasa: emotion freed from private possession,
made available for contemplative savoring.

Theatre therefore becomes a laboratory of liberation.
It lets consciousness experience intensity without being trapped inside
the practical demands of a private self.

FILM THESIS
-----------
Rasa is not weak emotion.
It is emotion released from ownership.

The decisive transformation is:

personal affect
→ dramatic presentation
→ de-individuation
→ universalization
→ contemplative savoring
→ recognition of consciousness tasting its own powers

HOUSE RULES
-----------
• Every scene lasts 5–10 seconds.
• Every scene performs a visible transformation.
• Clean ivory gallery field.
• No slideshow compositions.
• Sparse labels only.
• Mature frame near u=0.72.
• Personal emotion = tight crimson geometry.
• Rasa = expanding translucent color-field.
• Witness-consciousness = gold center/field.
• Continuity object: one emotion-point that expands as ownership dissolves.

OUTPUT
------
output_rasa_theory/
  frames/
  scenes/
  why_fiction_feels_more_real.mp4
  narration_timeline.json
  contact_sheet.jpg

USAGE
-----
python why_fiction_feels_more_real_platinum.py
python why_fiction_feels_more_real_platinum.py --preview
python why_fiction_feels_more_real_platinum.py --scene 12
python why_fiction_feels_more_real_platinum.py --fps 12 --width 1920 --height 1080
"""

from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output_rasa_theory"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

IVORY=(249,247,241)
WHITE=(255,254,250)
INK=(29,33,39)
SOFT_INK=(86,91,98)
SILVER=(180,187,194)
PALE_SILVER=(226,229,232)
CYAN=(57,156,180)
PALE_CYAN=(196,227,233)
GOLD=(194,156,72)
PALE_GOLD=(236,219,175)
GREEN=(70,139,99)
PALE_GREEN=(198,225,208)
CRIMSON=(162,58,69)
PALE_CRIMSON=(231,198,202)
VIOLET=(109,83,153)
PALE_VIOLET=(220,211,237)
ORANGE=(194,112,53)
BLUE=(65,103,165)
PINK=(190,91,126)
BROWN=(125,89,60)

FONT_SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def clamp(x,lo=0.0,hi=1.0): return max(lo,min(hi,x))
def lerp(a,b,t): return a+(b-a)*clamp(t)
def mix(a,b,t): return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smoothstep(a,b,x):
    if a==b: return 1.0 if x>=b else 0.0
    q=clamp((x-a)/(b-a))
    return q*q*(3-2*q)
def ease(t):
    t=clamp(t)
    return .5-.5*math.cos(math.pi*t)
def pulse(t,speed=1.0,phase=0.0):
    return .5+.5*math.sin(math.tau*(speed*t+phase))

def font(path,size):
    for c in (path,FONT_SERIF,FONT_SANS):
        try: return ImageFont.truetype(c,size)
        except OSError: pass
    return ImageFont.load_default()

def layer(size): return Image.new("RGBA",size,(0,0,0,0))

def field(w,h,seed):
    rng=np.random.default_rng(seed)
    arr=np.empty((h,w,3),dtype=np.float32)
    arr[:]=IVORY
    arr+=rng.normal(0,.9,(h,w,1))
    yy,xx=np.mgrid[0:h,0:w]
    halo=np.exp(-(((xx-w*.5)/(w*.37))**2+((yy-h*.40)/(h*.31))**2)*2)
    arr[...,1]+=halo*3.4
    arr[...,2]+=halo*5.0
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")

def centered(d,xy,text,fnt,fill=INK):
    d.text(xy,text,font=fnt,fill=fill,anchor="mm")

def seal(im,title,subtitle="",color=INK):
    w,h=im.size
    d=ImageDraw.Draw(im)
    centered(d,(w/2,h*.875),title,font(FONT_SERIF_BOLD,max(22,int(h*.04))),color)
    if subtitle:
        centered(d,(w/2,h*.923),subtitle,font(FONT_SANS,max(13,int(h*.019))),SOFT_INK)

def border(im):
    w,h=im.size
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w-26,h-26),radius=18,outline=(*INK,45),width=2)

def glow_circle(im,x,y,r,color,alpha=170,blur=14):
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.ellipse((x-r,y-r,x+r,y+r),fill=(*color,alpha))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).ellipse(
        (x-r*.34,y-r*.34,x+r*.34,y+r*.34),
        fill=(*mix(color,WHITE,.35),min(255,alpha+50))
    )
    im.alpha_composite(fg)

def glow_line(im,pts,color,width=4,alpha=210,blur=11):
    if len(pts)<2: return
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.line(pts,fill=(*color,alpha),width=width*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(
        pts,fill=(*mix(color,WHITE,.08),min(255,alpha+25)),
        width=width,joint="curve"
    )
    im.alpha_composite(fg)

def partial(pts,a):
    if not pts: return []
    a=clamp(a)
    if a>=1: return pts
    k=a*(len(pts)-1)
    i=int(k)
    f=k-i
    out=list(pts[:i+1])
    if i+1<len(pts):
        p,q=pts[i],pts[i+1]
        out.append((lerp(p[0],q[0],f),lerp(p[1],q[1],f)))
    return out

def arrow(d,a,b,color=INK,width=3,head=10):
    d.line((*a,*b),fill=color,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s in (-1,1):
        p=(b[0]-math.cos(ang+s*.52)*head,b[1]-math.sin(ang+s*.52)*head)
        d.line((*b,*p),fill=color,width=width)

def draw_body(d,cx,cy,scale=1.0,color=INK,alpha=210):
    d.ellipse((cx-27*scale,cy-145*scale,cx+27*scale,cy-91*scale),
              outline=(*color,alpha),width=max(2,int(4*scale)))
    d.line((cx,cy-91*scale,cx,cy+55*scale),
           fill=(*color,alpha),width=max(3,int(6*scale)))
    d.line((cx-68*scale,cy-54*scale,cx+68*scale,cy-54*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))
    d.line((cx-68*scale,cy-54*scale,cx-140*scale,cy+18*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))
    d.line((cx+68*scale,cy-54*scale,cx+140*scale,cy+18*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))
    d.line((cx,cy+55*scale,cx-52*scale,cy+160*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))
    d.line((cx,cy+55*scale,cx+52*scale,cy+160*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))

def draw_face(d,cx,cy,scale=1.0,color=INK,alpha=210,emotion=0.0):
    d.ellipse((cx-60*scale,cy-78*scale,cx+60*scale,cy+78*scale),
              outline=(*color,alpha),width=max(2,int(4*scale)))
    for ex in (-20,20):
        d.ellipse((cx+(ex-4)*scale,cy-18*scale,
                   cx+(ex+4)*scale,cy-10*scale),
                  fill=(*color,alpha))
    if emotion>=0:
        d.arc((cx-24*scale,cy+5*scale,cx+24*scale,cy+35*scale),
              10,170,fill=(*color,alpha),width=max(2,int(3*scale)))
    else:
        d.arc((cx-24*scale,cy+12*scale,cx+24*scale,cy+42*scale),
              190,350,fill=(*color,alpha),width=max(2,int(3*scale)))

def draw_mask(d,cx,cy,scale,color,alpha=200):
    pts=[
        (cx,cy-80*scale),
        (cx-58*scale,cy-42*scale),
        (cx-48*scale,cy+35*scale),
        (cx,cy+82*scale),
        (cx+48*scale,cy+35*scale),
        (cx+58*scale,cy-42*scale),
        (cx,cy-80*scale),
    ]
    d.line(pts,fill=(*color,alpha),width=max(2,int(4*scale)))
    d.ellipse((cx-28*scale,cy-25*scale,cx-12*scale,cy-10*scale),
              outline=(*color,alpha),width=2)
    d.ellipse((cx+12*scale,cy-25*scale,cx+28*scale,cy-10*scale),
              outline=(*color,alpha),width=2)

def rasa_field(im,cx,cy,r,color,alpha=105):
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.ellipse((cx-r,cy-r*.62,cx+r,cy+r*.62),fill=(*color,alpha))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(22)))

RASA_COLORS={
    "SRINGARA":PINK,
    "HASYA":GOLD,
    "KARUNA":VIOLET,
    "RAUDRA":CRIMSON,
    "VIRA":ORANGE,
    "BHAYANAKA":INK,
    "BIBHATSA":GREEN,
    "ADBHUTA":CYAN,
    "SHANTA":PALE_GOLD,
}


# =============================================================================
# VISUALS
# =============================================================================

def vis_real_vs_stage(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    draw_body(d,*left,.72,INK,170)
    draw_body(d,*right,.72,INK,170)
    # real contraction
    r1=lerp(145,70,q)
    d.ellipse((left[0]-r1,left[1]-r1*.72,left[0]+r1,left[1]+r1*.72),
              outline=(*CRIMSON,210),width=5)
    # stage expansion
    r2=lerp(35,165,q)
    d.ellipse((right[0]-r2,right[1]-r2*.62,right[0]+r2,right[1]+r2*.62),
              outline=(*VIOLET,190),width=4)
    centered(d,(left[0],h*.68),"REAL INSULT",font(FONT_SERIF_BOLD,22),CRIMSON)
    centered(d,(right[0],h*.68),"STAGED INSULT",font(FONT_SERIF_BOLD,22),VIOLET)
    seal(im,"THE SAME EMOTION · A DIFFERENT ARCHITECTURE",
         "why does fiction intensify feeling without trapping us inside it?")

def vis_ownership_chain(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    items=[
        ("EVENT",CYAN,w*.14),
        ("REACTION",CRIMSON,w*.31),
        ("STORY",VIOLET,w*.48),
        ("IDENTITY",INK,w*.66),
        ("SUFFERING",CRIMSON,w*.84),
    ]
    q=ease(u)
    for i,(lab,col,x) in enumerate(items):
        glow_circle(im,x,h*.40,12,col,150,9)
        centered(d,(x,h*.67),lab,font(FONT_SANS_BOLD,13),col)
        if i<len(items)-1:
            arrow(d,(x+16,h*.40),(items[i+1][2]-16,h*.40),
                  (*col,int(170*q)),3,8)
    seal(im,"ORDINARY EMOTION BECOMES A CHAIN OF OWNERSHIP",
         "what happened becomes what this means about me")

def vis_theatre_chain(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    items=[
        ("EVENT",CYAN,w*.14),
        ("EMOTION",CRIMSON,w*.31),
        ("DISTANCE",VIOLET,w*.48),
        ("EXPANSION",GOLD,w*.66),
        ("RASA",GREEN,w*.84),
    ]
    q=ease(u)
    for i,(lab,col,x) in enumerate(items):
        glow_circle(im,x,h*.40,12,col,150,9)
        centered(d,(x,h*.67),lab,font(FONT_SANS_BOLD,13),col)
        if i<len(items)-1:
            arrow(d,(x+16,h*.40),(items[i+1][2]-16,h*.40),
                  (*col,int(170*q)),3,8)
    seal(im,"THEATRE INTERRUPTS THE CHAIN",
         "emotion remains intense while private consequence falls away")

def vis_personal_to_universal(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    r=lerp(18,230,q)
    rasa_field(im,cx,cy,r,VIOLET,int(55+90*q))
    glow_circle(im,cx,cy,18,VIOLET,180,11)
    if q<.55:
        centered(d,(cx,h*.68),"MY GRIEF",font(FONT_SERIF_BOLD,27),CRIMSON)
    else:
        centered(d,(cx,h*.68),"GRIEF",font(FONT_SERIF_BOLD,31),VIOLET)
    seal(im,"PERSONAL EMOTION BECOMES UNIVERSALIZED",
         "not weaker, but released from exclusive ownership")

def vis_many_faces_one_rasa(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    faces=[
        (w*.24,h*.30),
        (w*.40,h*.52),
        (w*.60,h*.28),
        (w*.76,h*.52),
    ]
    for i,(x,y) in enumerate(faces):
        alpha=int(200*(1-q))
        draw_face(d,x,y,.55,INK,alpha,-1)
        glow_line(im,partial([(x,y),(cx,cy)],q),VIOLET,3,130,8)
    rasa_field(im,cx,cy,lerp(30,210,q),VIOLET,int(75+65*q))
    if q>.55:
        centered(d,(cx,h*.68),"KARUṆA",font(FONT_SERIF_BOLD,30),VIOLET)
    seal(im,"THE FACES DISSOLVE · THE EMOTION REMAINS",
         "sādhāraṇīkaraṇa removes the claim of exclusive possession")

def vis_sadharanikarana(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    labels=[
        ("MY",CRIMSON,-190,-85),
        ("YOUR",CYAN,190,-85),
        ("HIS",VIOLET,-190,100),
        ("HER",GREEN,190,100),
    ]
    for lab,col,ox,oy in labels:
        x=lerp(cx+ox,cx,q*.8)
        y=lerp(cy+oy,cy,q*.8)
        centered(d,(x,y),lab,font(FONT_SERIF_BOLD,24),
                 (*col,int(220*(1-q*.78))))
    rasa_field(im,cx,cy,lerp(25,220,q),GOLD,int(50+85*q))
    if q>.55:
        centered(d,(cx,cy),"EMOTION ITSELF",font(FONT_SERIF_BOLD,28),GOLD)
    seal(im,"SĀDHĀRAṆĪKARAṆA",
         "the emotion becomes common, universal, and aesthetically available")

def vis_actor_role_audience(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    xs=[w*.18,w*.39,w*.61,w*.82]
    labs=["ACTOR","ROLE","AUDIENCE","AWARENESS"]
    cols=[INK,VIOLET,CYAN,GOLD]
    q=ease(u)
    draw_body(d,xs[0],h*.40,.55,INK,180)
    draw_mask(d,xs[1],h*.40,.65,VIOLET,180)
    for i in range(5):
        draw_face(d,xs[2]-50+i*25,h*.40,.25,CYAN,145,-1)
    glow_circle(im,xs[3],h*.40,18,GOLD,180,12)
    for i in range(len(xs)-1):
        arrow(d,(xs[i]+35,h*.40),(xs[i+1]-35,h*.40),
              (*cols[i+1],int(170*q)),3,8)
    for x,lab,col in zip(xs,labs,cols):
        centered(d,(x,h*.68),lab,font(FONT_SANS_BOLD,13),col)
    seal(im,"ACTOR · ROLE · AUDIENCE · AWARENESS",
         "multiple levels remain true without collapsing into one another")

def vis_vibhava_anubhava(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.23,h*.40)
    center=(w*.50,h*.40)
    right=(w*.77,h*.40)
    q=ease(u)
    glow_circle(im,*left,15,GOLD,160,10)
    glow_circle(im,*center,15,CRIMSON,170,10)
    glow_circle(im,*right,15,VIOLET,170,10)
    arrow(d,(left[0]+18,left[1]),(center[0]-18,center[1]),
          (*GOLD,int(170*q)),3,8)
    arrow(d,(center[0]+18,center[1]),(right[0]-18,right[1]),
          (*VIOLET,int(170*q)),3,8)
    centered(d,(left[0],h*.67),"VIBHĀVA",font(FONT_SERIF_BOLD,21),GOLD)
    centered(d,(center[0],h*.67),"BHĀVA",font(FONT_SERIF_BOLD,21),CRIMSON)
    centered(d,(right[0],h*.67),"ANUBHĀVA",font(FONT_SERIF_BOLD,21),VIOLET)
    seal(im,"CAUSE · FELT STATE · EXPRESSION",
         "dramatic emotion is built from interacting conditions")

def vis_vyabhicari(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    transients=[
        ("DOUBT",CYAN),
        ("SHAME",VIOLET),
        ("WEARINESS",SILVER),
        ("HOPE",GOLD),
        ("FEAR",CRIMSON),
        ("MEMORY",GREEN),
    ]
    for i,(lab,col) in enumerate(transients):
        a=t*.22+i*math.tau/len(transients)
        r=175
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*r*.58
        glow_circle(im,x,y,10,col,140,8)
        centered(d,(x,y+26),lab,font(FONT_SANS_BOLD,12),col)
    glow_circle(im,cx,cy,18,VIOLET,180,12)
    centered(d,(cx,h*.68),"STHĀYIBHĀVA",font(FONT_SERIF_BOLD,25),VIOLET)
    seal(im,"TRANSITORY STATES ORBIT A DURABLE EMOTIONAL DISPOSITION",
         "rasa emerges from an organized field, not one isolated feeling")

def vis_sthayibhava_rasa(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    core_r=lerp(18,55,q)
    glow_circle(im,cx,cy,core_r,CRIMSON,180,12)
    for rr in range(70,240,30):
        d.ellipse((cx-rr*q,cy-rr*.62*q,cx+rr*q,cy+rr*.62*q),
                  outline=(*VIOLET,int(80*q*(1-rr/270))),width=3)
    centered(d,(cx,h*.68),"STHĀYIBHĀVA → RASA",
             font(FONT_SERIF_BOLD,27),GOLD)
    seal(im,"THE DURABLE EMOTION BECOMES AESTHETIC FLAVOR",
         "private affect is transformed into contemplative experience")

def vis_rasa_tasting(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    drop=(cx,lerp(h*.20,cy,q))
    glow_circle(im,*drop,14,VIOLET,180,11)
    for rr in range(35,235,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(75*q*(1-rr/260))),width=3)
    centered(d,(cx,h*.68),"ĀSVĀDA",font(FONT_SERIF_BOLD,31),GOLD)
    seal(im,"RASA IS TASTED",
         "the spectator savors consciousness in the form of emotion")

def vis_contraction_expansion(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.31,h*.40)
    right=(w*.69,h*.40)
    q=ease(u)
    r1=lerp(155,60,q)
    r2=lerp(35,175,q)
    d.ellipse((left[0]-r1,left[1]-r1*.7,left[0]+r1,left[1]+r1*.7),
              outline=(*CRIMSON,205),width=5)
    d.ellipse((right[0]-r2,right[1]-r2*.62,right[0]+r2,right[1]+r2*.62),
              outline=(*GOLD,190),width=5)
    centered(d,(left[0],h*.68),"CONTRACTION",font(FONT_SERIF_BOLD,23),CRIMSON)
    centered(d,(right[0],h*.68),"EXPANSION",font(FONT_SERIF_BOLD,23),GOLD)
    seal(im,"INDIVIDUAL EMOTION CONTRACTS · RASA EXPANDS",
         "the same energy enters a wider field of awareness")

def vis_nine_rasas(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    items=list(RASA_COLORS.items())
    for i,(lab,col) in enumerate(items):
        a=i*math.tau/len(items)-math.pi/2
        r=190*q
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*r*.62
        glow_circle(im,x,y,13,col,150,9)
        if q>.55:
            centered(d,(x,y+28),lab,font(FONT_SANS_BOLD,11),col)
    glow_circle(im,cx,cy,17,GOLD,180,11)
    seal(im,"THE RASAS ARE MODES OF UNIVERSALIZED FEELING",
         "love, laughter, grief, fury, courage, fear, disgust, wonder, peace")

def vis_karuna(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    rasa_field(im,cx,cy,lerp(25,240,q),VIOLET,int(55+85*q))
    for i in range(5):
        x=w*.25+i*w*.125
        draw_face(d,x,h*.40,.38,VIOLET,int(180*(1-q*.5)),-1)
    if q>.6:
        centered(d,(cx,h*.68),"KARUṆA",font(FONT_SERIF_BOLD,31),VIOLET)
    seal(im,"GRIEF FREED FROM BIOGRAPHY BECOMES KARUṆA",
         "sorrow is no longer only the wound of one person")

def vis_vira(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # many warriors dissolve into heroic field
    for i in range(7):
        x=w*.20+i*w*.10
        alpha=int(180*(1-q*.65))
        draw_body(d,x,h*.43,.35,INK,alpha)
    rasa_field(im,cx,cy,lerp(25,235,q),ORANGE,int(55+90*q))
    if q>.55:
        centered(d,(cx,h*.68),"VĪRA",font(FONT_SERIF_BOLD,31),ORANGE)
    seal(im,"THE BATTLEFIELD DISSOLVES · HEROISM REMAINS",
         "the event becomes a universal capacity for courageous action")

def vis_sringara(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.35,h*.40)
    right=(w*.65,h*.40)
    q=ease(u)
    draw_body(d,*left,.55,INK,int(180*(1-q*.45)))
    draw_body(d,*right,.55,INK,int(180*(1-q*.45)))
    glow_line(im,partial([left,(w*.50,h*.25),right],q),PINK,5,190,12)
    rasa_field(im,w*.50,h*.40,lerp(25,220,q),PINK,int(55+85*q))
    if q>.58:
        centered(d,(w*.50,h*.68),"ŚṚṄGĀRA",font(FONT_SERIF_BOLD,30),PINK)
    seal(im,"DESIRE FREED FROM POSSESSION BECOMES ŚṚṄGĀRA",
         "love appears as a universal rhythm of attraction and beauty")

def vis_shanta(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    for rr in range(35,270,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(80*q*(1-rr/300))),width=3)
    glow_circle(im,cx,cy,14,GOLD,180,11)
    centered(d,(cx,h*.68),"ŚĀNTA",font(FONT_SERIF_BOLD,31),GOLD)
    seal(im,"WHEN ALL MOVEMENT IS SAVORED WITHOUT GRASPING, PEACE APPEARS",
         "śānta is not emotional absence, but uncontracted repose")

def vis_predictive_self(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    layers=[
        ("SENSATION",CYAN,55),
        ("PREDICTION",VIOLET,105),
        ("SELF-MODEL",CRIMSON,160),
        ("PRACTICAL CONSEQUENCE",INK,220),
    ]
    for lab,col,r in layers:
        alpha=int(190*(1-q*.75 if lab!="SENSATION" else 1))
        d.ellipse((cx-r,cy-r*.62,cx+r,cy+r*.62),
                  outline=(*col,alpha),width=4)
        if q<.55:
            centered(d,(cx,cy-r*.62-15),lab,font(FONT_SANS_BOLD,12),col)
    if q>.45:
        rasa_field(im,cx,cy,190,GOLD,int(85*q))
    seal(im,"AESTHETIC DISTANCE WEAKENS THE PRACTICAL SELF-MODEL",
         "emotion remains while immediate action-demand recedes")

def vis_mirror_recognition(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    d.ellipse((cx-205,cy-225,cx+205,cy+225),
              fill=(*PALE_SILVER,90),outline=(*CYAN,180),width=5)
    for i,col in enumerate([CRIMSON,VIOLET,GOLD]):
        a=i*math.tau/3-math.pi/2+t*.12
        x=cx+math.cos(a)*115
        y=cy+math.sin(a)*75
        glow_circle(im,x,y,16,col,150,10)
        d.line((x,y,cx,cy),fill=(*col,80),width=2)
    glow_circle(im,cx,cy,17,GOLD,185,12)
    if q>.62:
        centered(d,(cx,h*.68),"CONSCIOUSNESS TASTING ITSELF",
                 font(FONT_SERIF_BOLD,24),GOLD)
    seal(im,"RASA IS REFLEXIVE AWARENESS IN AESTHETIC FORM",
         "vimarśa recognizes its own powers as emotion")

def vis_theatre_liberation(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.25,h*.40)
    right=(w*.75,h*.40)
    q=ease(u)
    # theatre
    d.rounded_rectangle((left[0]-130,left[1]-105,left[0]+130,left[1]+105),
                        radius=18,fill=(*PALE_SILVER,110),
                        outline=(*INK,120),width=3)
    draw_mask(d,left[0],left[1],.65,VIOLET,180)
    # meditation
    draw_body(d,right[0],right[1],.58,INK,170)
    for rr in range(35,145,25):
        d.ellipse((right[0]-rr,right[1]-rr*.62,right[0]+rr,right[1]+rr*.62),
                  outline=(*GOLD,int(75*q*(1-rr/165))),width=3)
    glow_line(im,partial([left,(w*.50,h*.20),right],q),GOLD,4,175,11)
    centered(d,(left[0],h*.68),"THEATRE",font(FONT_SERIF_BOLD,22),VIOLET)
    centered(d,(right[0],h*.68),"MEDITATION",font(FONT_SERIF_BOLD,22),GOLD)
    seal(im,"TWO MACHINES FOR LOOSENING PRIVATE OWNERSHIP",
         "emotion can be witnessed without being denied")

def vis_art_lab(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # chamber opens into field
    d.rounded_rectangle((cx-180,cy-120,cx+180,cy+120),
                        radius=22,outline=(*INK,int(180*(1-q*.5))),width=4)
    draw_mask(d,cx,cy,.70,VIOLET,int(190*(1-q*.35)))
    for rr in range(40,260,30):
        d.ellipse((cx-rr*q,cy-rr*.62*q,cx+rr*q,cy+rr*.62*q),
                  outline=(*GOLD,int(75*q*(1-rr/290))),width=3)
    if q>.65:
        centered(d,(cx,h*.68),"ART IS A LABORATORY FOR LIBERATION",
                 font(FONT_SERIF_BOLD,23),GOLD)
    seal(im,"THEATRE TEMPORARILY REMOVES THE ILLUSION OF PRIVATE POSSESSION",
         "feeling survives the fall of mine")

def vis_no_emotion_erasure(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    for i,(lab,col) in enumerate(list(RASA_COLORS.items())):
        a=i*math.tau/9+t*.10
        r=175
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*r*.62
        glow_circle(im,x,y,12,col,145,9)
    glow_circle(im,cx,cy,18,GOLD,185,12)
    if q>.58:
        for i in range(9):
            a=i*math.tau/9+t*.10
            x=cx+math.cos(a)*175
            y=cy+math.sin(a)*108
            d.line((x,y,cx,cy),fill=(*GOLD,85),width=2)
    seal(im,"LIBERATION IS NOT THE DISAPPEARANCE OF EMOTION",
         "it is emotion freed from possession")

def vis_caution(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    rows=[
        ("RASA = ORDINARY EMOTION","FALSE",CRIMSON),
        ("RASA REQUIRES UNIVERSALIZATION","SUPPORTED",GREEN),
        ("MIRROR NEURONS FULLY EXPLAIN RASA","NOT ESTABLISHED",CRIMSON),
        ("AESTHETIC DISTANCE MODIFIES SELF-INVOLVEMENT","PLAUSIBLE",CYAN),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i)
        y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),
                            radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.39,y),claim,font(FONT_SANS_BOLD,14),INK)
        centered(d,(w*.74,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"DO NOT REDUCE RASA TO ONE MODERN MECHANISM",
         "neuroscience may illuminate conditions without replacing the theory")

def vis_final(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # battlefield/figures dissolve into field
    for i in range(9):
        x=w*.18+i*w*.08
        draw_body(d,x,h*.46,.26,INK,int(170*(1-q)))
    rasa_field(im,cx,cy,lerp(30,250,q),ORANGE,int(60+90*q))
    glow_circle(im,cx,cy,18,GOLD,190,12)
    if q>.7:
        centered(d,(cx,h*.68),"RASA",font(FONT_SERIF_BOLD,34),GOLD)
    seal(im,"WHY FICTION FEELS MORE REAL THAN REALITY",
         "because emotion becomes most itself when it is no longer only mine",GOLD)


VISUALS: dict[str,Callable] = {
    "real_stage":vis_real_vs_stage,
    "ownership":vis_ownership_chain,
    "theatre_chain":vis_theatre_chain,
    "universal":vis_personal_to_universal,
    "faces":vis_many_faces_one_rasa,
    "sadharana":vis_sadharanikarana,
    "layers":vis_actor_role_audience,
    "components":vis_vibhava_anubhava,
    "transients":vis_vyabhicari,
    "sthayi":vis_sthayibhava_rasa,
    "taste":vis_rasa_tasting,
    "expand":vis_contraction_expansion,
    "nine":vis_nine_rasas,
    "karuna":vis_karuna,
    "vira":vis_vira,
    "sringara":vis_sringara,
    "shanta":vis_shanta,
    "predictive":vis_predictive_self,
    "mirror":vis_mirror_recognition,
    "theatre_meditation":vis_theatre_liberation,
    "lab":vis_art_lab,
    "noerase":vis_no_emotion_erasure,
    "caution":vis_caution,
    "final":vis_final,
}


@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict


SCENES = [
    Scene("Insult",
          "Last week your friend insulted you.",
          6.0,"real_stage",{}),
    Scene("Contraction",
          "The jaw tightened. The body contracted. Thought began building a case.",
          8.5,"real_stage",{}),
    Scene("Same insult",
          "Now place the same insult inside a play.",
          7.0,"real_stage",{}),
    Scene("Enjoyment",
          "The emotion remains, but the suffering changes. You may even enjoy it.",
          8.5,"real_stage",{}),
    Scene("Question",
          "Why can fiction intensify feeling while freeing us from its practical weight?",
          9.0,"real_stage",{}),

    Scene("Ordinary chain",
          "In ordinary life, emotion is rapidly captured by ownership.",
          8.0,"ownership",{}),
    Scene("Story",
          "An event becomes reaction. Reaction becomes story. Story becomes identity.",
          9.5,"ownership",{}),
    Scene("Mine",
          "The emotion becomes evidence about me, my future, my value, my danger.",
          9.5,"ownership",{}),
    Scene("Suffering",
          "Feeling becomes suffering when it is locked into the architecture of mine.",
          8.5,"ownership",{}),

    Scene("Theatre interrupts",
          "Theatre interrupts this chain.",
          7.0,"theatre_chain",{}),
    Scene("No practical demand",
          "The event is presented, but it does not demand immediate practical action.",
          8.5,"theatre_chain",{}),
    Scene("Emotion remains",
          "Emotion remains intense while direct consequence recedes.",
          8.0,"theatre_chain",{}),
    Scene("Expansion",
          "The feeling has room to expand beyond one private life.",
          8.0,"theatre_chain",{}),

    Scene("Abhinava",
          "Abhinavagupta's answer is radical.",
          7.0,"universal",{}),
    Scene("Not weaker",
          "Aesthetic emotion is not ordinary emotion made weaker.",
          8.0,"universal",{}),
    Scene("Universalized",
          "It is ordinary emotion made universal.",
          7.5,"universal",{}),
    Scene("My grief",
          "My grief becomes grief.",
          6.0,"universal",{}),
    Scene("Larger",
          "Not less intense. Larger.",
          6.0,"universal",{}),

    Scene("Many faces",
          "One face suffers. Then another. Then another.",
          7.5,"faces",{}),
    Scene("Faces dissolve",
          "The biographies dissolve while the emotional form remains.",
          8.5,"faces",{}),
    Scene("Karuna",
          "What remains is karuṇa: compassion or pathos universalized as aesthetic experience.",
          9.5,"karuna",{}),

    Scene("Sadharanikarana",
          "The key process is sādhāraṇīkaraṇa.",
          7.5,"sadharana",{}),
    Scene("Common",
          "The emotion becomes common, general, shareable, no longer owned by one empirical person.",
          9.5,"sadharana",{}),
    Scene("No owner",
          "My, your, his, and her fall away.",
          7.5,"sadharana",{}),
    Scene("Emotion itself",
          "Emotion itself becomes aesthetically available.",
          8.0,"sadharana",{}),

    Scene("Actor",
          "The actor does not literally become the character.",
          7.5,"layers",{}),
    Scene("Role",
          "The role is not identical with the actor.",
          7.0,"layers",{}),
    Scene("Audience",
          "The audience is not identical with the role.",
          7.0,"layers",{}),
    Scene("Awareness",
          "Yet actor, role, audience, and awareness participate in one event.",
          9.0,"layers",{}),
    Scene("Many levels",
          "Multiple levels remain true without destroying one another.",
          8.0,"layers",{}),

    Scene("Dramatic construction",
          "Rasa does not appear from emotion alone.",
          7.5,"components",{}),
    Scene("Vibhava",
          "Vibhāvas establish the causes and conditions: persons, settings, situations, objects.",
          9.5,"components",{}),
    Scene("Bhava",
          "A durable emotional disposition becomes active.",
          8.0,"components",{}),
    Scene("Anubhava",
          "Anubhāvas make it visible through voice, face, gesture, and action.",
          9.0,"components",{}),

    Scene("Transitory states",
          "Around the durable emotion move many transitory states.",
          8.0,"transients",{}),
    Scene("Orbit",
          "Doubt, shame, fatigue, hope, memory, fear, agitation, and relief orbit the dominant mood.",
          10.0,"transients",{}),
    Scene("Organized field",
          "Rasa is therefore an organized emotional field, not one isolated feeling.",
          9.0,"transients",{}),

    Scene("Sthayibhava",
          "At the center is the sthāyibhāva: a durable emotional disposition.",
          9.0,"sthayi",{}),
    Scene("Transformation",
          "Dramatic conditions awaken it, amplify it, and detach it from private circumstance.",
          9.5,"sthayi",{}),
    Scene("Rasa",
          "The durable emotion becomes rasa: aesthetic flavor.",
          8.0,"sthayi",{}),

    Scene("Taste",
          "Abhinavagupta repeatedly speaks of tasting.",
          7.5,"taste",{}),
    Scene("Asvada",
          "Rasa is āsvāda: savoring.",
          6.5,"taste",{}),
    Scene("Consciousness tastes",
          "The spectator does not merely identify an emotion. Consciousness tastes itself in the form of emotion.",
          10.0,"taste",{}),

    Scene("Contraction",
          "Ordinary emotion contracts around one threatened or desiring center.",
          9.0,"expand",{}),
    Scene("Expansion",
          "Rasa expands the same energy into a field that many can inhabit.",
          8.5,"expand",{}),
    Scene("Liberated emotion",
          "Individual emotion is trapped emotion. Rasa is liberated emotion.",
          8.5,"expand",{}),

    Scene("Nine rasas",
          "The tradition organizes aesthetic experience through major rasas.",
          8.0,"nine",{}),
    Scene("List",
          "Love, laughter, grief, fury, courage, fear, disgust, wonder, and peace.",
          9.0,"nine",{}),
    Scene("Not labels",
          "These are not merely labels for facial expressions.",
          7.5,"nine",{}),
    Scene("Worlds",
          "Each rasa is a mode in which an entire world becomes emotionally intelligible.",
          9.0,"nine",{}),

    Scene("Karuna world",
          "In karuṇa, sorrow ceases to be one person's private wound.",
          9.0,"karuna",{}),
    Scene("Compassion",
          "The spectator tastes the universal vulnerability of finite life.",
          8.5,"karuna",{}),

    Scene("Vira world",
          "In vīra, the battlefield dissolves into the felt structure of courage.",
          9.0,"vira",{}),
    Scene("Heroism",
          "The audience does not merely observe a hero. It tastes heroism.",
          8.0,"vira",{}),

    Scene("Sringara world",
          "In śṛṅgāra, desire is released from immediate possession.",
          8.5,"sringara",{}),
    Scene("Love rhythm",
          "Attraction becomes a universal rhythm of beauty, longing, union, and separation.",
          9.5,"sringara",{}),

    Scene("Shanta",
          "Śānta presents a different limit.",
          7.0,"shanta",{}),
    Scene("Peace",
          "Peace is not emotional blankness.",
          7.0,"shanta",{}),
    Scene("Repose",
          "It is the savoring of experience without grasping, resistance, or practical agitation.",
          9.5,"shanta",{}),

    Scene("Cognitive architecture",
          "A modern vocabulary can clarify part of this transformation.",
          8.0,"predictive",{}),
    Scene("Self model",
          "Ordinary emotion is organized by prediction, body regulation, self-model, and practical consequence.",
          10.0,"predictive",{}),
    Scene("Distance",
          "Aesthetic distance weakens immediate action-demand and loosens exclusive self-reference.",
          9.0,"predictive",{}),
    Scene("Not reduction",
          "But predictive processing does not replace rasa theory. It describes possible mechanisms beneath one part of it.",
          10.0,"caution",{}),

    Scene("Mirror neurons",
          "Mirror systems may help explain embodied resonance with performed action.",
          8.5,"caution",{}),
    Scene("Not full answer",
          "They do not explain universalization, savoring, or why de-owned emotion can become blissful.",
          9.5,"caution",{}),

    Scene("Vimarsa",
          "The deeper claim is metaphysical.",
          7.0,"mirror",{}),
    Scene("Self apprehension",
          "Consciousness is not only illuminated experience. It is reflexive awareness of experience.",
          9.0,"mirror",{}),
    Scene("Taste itself",
          "In rasa, vimarśa tastes its own powers as grief, courage, wonder, fury, love, and peace.",
          10.0,"mirror",{}),

    Scene("Theatre and meditation",
          "Theatre and meditation now reveal a shared geometry.",
          8.0,"theatre_meditation",{}),
    Scene("Witness",
          "Emotion appears.",
          5.5,"theatre_meditation",{}),
    Scene("No possession",
          "Awareness remains. Ownership loosens.",
          7.0,"theatre_meditation",{}),
    Scene("Different methods",
          "One uses staged representation. The other uses disciplined attention.",
          8.5,"theatre_meditation",{}),

    Scene("Laboratory",
          "Art is therefore a laboratory for liberation.",
          8.0,"lab",{}),
    Scene("Not entertainment",
          "Theatre is not merely entertainment added to philosophy.",
          8.0,"lab",{}),
    Scene("Machine",
          "It is a machine for temporarily removing the illusion of private emotional ownership.",
          10.0,"lab",{}),
    Scene("Demonstration",
          "It demonstrates that intensity can remain when mine falls away.",
          8.5,"lab",{}),

    Scene("No erasure",
          "Liberation is not the disappearance of emotion.",
          8.0,"noerase",{}),
    Scene("Full range",
          "Love, fear, grief, disgust, courage, wonder, fury, laughter, and peace remain available.",
          10.0,"noerase",{}),
    Scene("Freed",
          "What disappears is compulsory possession.",
          7.5,"noerase",{}),
    Scene("Recognition",
          "Emotion is recognized as a mode of consciousness rather than a prison built around the self.",
          9.5,"noerase",{}),

    Scene("Return to battlefield",
          "Return to the battlefield.",
          6.0,"final",{}),
    Scene("Warriors vanish",
          "The warriors disappear.",
          6.0,"final",{}),
    Scene("Heroism remains",
          "Heroism remains.",
          6.0,"final",{}),
    Scene("Awareness",
          "Then even heroism becomes transparent to awareness.",
          8.0,"final",{}),
    Scene("Closing",
          "Fiction can feel more real than reality because emotion becomes most itself when it is no longer only mine.",
          10.0,"final",{}),
]


def render_frame(scene,frame_index,frame_count,width,height,seed):
    u=frame_index/max(1,frame_count-1)
    t=u*scene.duration
    im=field(width,height,seed)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im)
    return im.convert("RGB")

def ffmpeg_path():
    exe=shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg is required but was not found on PATH")
    return exe

def encode_scene(index,fps):
    frame_dir=FRAMES/f"scene_{index:03d}"
    output=SCENES_DIR/f"scene_{index:03d}.mp4"
    subprocess.run([
        ffmpeg_path(),"-y",
        "-framerate",str(fps),
        "-i",str(frame_dir/"%05d.jpg"),
        "-c:v","libx264",
        "-preset","medium",
        "-crf","18",
        "-pix_fmt","yuv420p",
        "-movflags","+faststart",
        str(output),
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return output

def render_scene(index,scene,fps,width,height,preview):
    frame_dir=FRAMES/f"scene_{index:03d}"
    frame_dir.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)
    count=max(2,round(scene.duration*fps))

    if preview:
        samples=[0,int(count*.33),int(count*.72),count-1]
        for oi,fi in enumerate(samples):
            render_frame(
                scene,fi,count,width,height,index*10000+fi
            ).save(frame_dir/f"preview_{oi:02d}.jpg",quality=95)
        return frame_dir

    for fi in range(count):
        p=frame_dir/f"{fi:05d}.jpg"
        if not p.exists():
            render_frame(
                scene,fi,count,width,height,index*10000+fi
            ).save(p,quality=95,subsampling=0)
    return encode_scene(index,fps)

def concatenate(paths):
    txt=OUTPUT/"concat.txt"
    txt.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in paths),
        encoding="utf-8"
    )
    output=OUTPUT/"why_fiction_feels_more_real.mp4"
    subprocess.run([
        ffmpeg_path(),"-y",
        "-f","concat","-safe","0",
        "-i",str(txt),
        "-c","copy",
        "-movflags","+faststart",
        str(output),
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return output

def export_timeline():
    cursor=0.0
    records=[]
    for index,scene in enumerate(SCENES,1):
        rec=asdict(scene)
        rec["scene_id"]=f"scene_{index:03d}"
        rec["start_seconds"]=round(cursor,3)
        cursor+=scene.duration
        rec["end_seconds"]=round(cursor,3)
        records.append(rec)

    path=OUTPUT/"narration_timeline.json"
    path.write_text(json.dumps({
        "title":"why fiction feels more real than reality",
        "subtitle":"Abhinavagupta's theory of rasa",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"emotion point expanding as ownership dissolves",
        "visual_arc":[
            "private contraction",
            "dramatic distance",
            "universalization",
            "aesthetic savoring",
            "recognition"
        ],
        "scenes":records,
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return path

def make_contact_sheet(width,height):
    tw=320
    th=int(tw*height/width)
    cols=4
    rows=math.ceil(len(SCENES)/cols)
    cell_h=th+48

    sheet=Image.new("RGB",(cols*tw,rows*cell_h),IVORY)
    d=ImageDraw.Draw(sheet)
    lf=font(FONT_SANS_BOLD,14)

    for index,scene in enumerate(SCENES,1):
        count=max(2,round(scene.duration*DEFAULT_FPS))
        image=render_frame(
            scene,int(count*.72),count,width,height,index*10000+72
        )
        image.thumbnail((tw,th))
        slot=index-1
        x=(slot%cols)*tw
        y=(slot//cols)*cell_h
        sheet.paste(image,(x,y))
        d.text((x+8,y+th+7),
               f"{index:02d}  {scene.title}",
               font=lf,fill=INK)

    path=OUTPUT/"contact_sheet.jpg"
    sheet.save(path,quality=94)
    return path

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--fps",type=int,default=DEFAULT_FPS)
    p.add_argument("--width",type=int,default=DEFAULT_WIDTH)
    p.add_argument("--height",type=int,default=DEFAULT_HEIGHT)
    p.add_argument("--scene",type=int)
    p.add_argument("--preview",action="store_true")
    p.add_argument("--no-contact-sheet",action="store_true")
    return p.parse_args()

def main():
    args=parse_args()

    OUTPUT.mkdir(parents=True,exist_ok=True)
    FRAMES.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)

    print(f"Timeline: {export_timeline()}")
    print(f"Scenes: {len(SCENES)}")
    print(f"Runtime: {sum(scene.duration for scene in SCENES)/60:.2f} minutes")

    if args.scene:
        if not 1<=args.scene<=len(SCENES):
            raise ValueError("scene out of range")
        print(render_scene(
            args.scene,
            SCENES[args.scene-1],
            args.fps,
            args.width,
            args.height,
            args.preview,
        ))
        return

    rendered=[]
    for index,scene in enumerate(SCENES,1):
        print(f"[{index:02d}/{len(SCENES):02d}] {scene.title} ({scene.duration:.1f}s)")
        result=render_scene(
            index,
            scene,
            args.fps,
            args.width,
            args.height,
            args.preview,
        )
        if not args.preview:
            rendered.append(result)

    if not args.no_contact_sheet:
        print(f"Contact sheet: {make_contact_sheet(args.width,args.height)}")

    if not args.preview:
        print(f"Final video: {concatenate(rendered)}")


if __name__=="__main__":
    main()
