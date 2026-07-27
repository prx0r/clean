#!/usr/bin/env python3
"""
THE ONE DOES NOT COMMAND
From Plotinus and Proclus to Michael Levin

An original Platinum-house procedural visual essay.

CENTRAL CLAIM
-------------
A genuine whole does not need to micromanage every movement of every part.

Plotinus describes reality as dependent upon increasingly universal principles:
the One, Intellect, Soul, and Nature. The One is not a craftsman issuing local
orders. Plotinian causation is better imagined as overflowing activity: a source
remains what it is while another level proceeds from it and turns back toward it.

Proclus later formalizes a recurring triad:
remaining (monē), procession (proodos), and return (epistrophē).

Michael Levin investigates a biological architecture with a visually homologous
shape but a different explanatory status:
competent molecular and cellular agents remain active at their own scales;
they participate in larger networks; those networks pursue tissue- and
organism-level goals; corrective action returns damaged form toward a target.

The film does NOT claim that Neoplatonism predicted bioelectricity or that
regeneration proves the One. It uses the formal comparison to ask:

How can a higher-order unity coordinate active parts without erasing them?

VISUAL THESIS
-------------
One point does not fire commands downward.
It becomes a field of constraints within which lower levels solve local problems.

The same composition is shown twice:
1. Neoplatonic language: One → Intellect → Soul → Nature.
2. Levin language: physiological network → tissue → organ → organism.

The audience discovers the structural resemblance visually before it is stated.

HOUSE RULES
-----------
• Every shot lasts 5–10 seconds.
• Every shot performs a transformation.
• Clean ivory gallery/scientific field.
• No static slideshow compositions.
• Sparse labels only.
• Mature frame near u=0.72.
• Continuity object: a gold center that becomes a distributed constraint field.
• Plotinian causation is shown as radiance and dependence, never crude pushing.
• Biological coordination is shown with cells, voltage fields, and correction.

OUTPUT
------
output_one_does_not_command/
  frames/
  scenes/
  one_does_not_command.mp4
  narration_timeline.json
  contact_sheet.jpg

USAGE
-----
python the_one_does_not_command_platinum.py
python the_one_does_not_command_platinum.py --preview
python the_one_does_not_command_platinum.py --scene 12
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
OUTPUT = ROOT / "output_one_does_not_command"
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

FONT_SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def clamp(x,lo=0.0,hi=1.0): return max(lo,min(hi,x))
def lerp(a,b,t): return a+(b-a)*clamp(t)
def mix(a,b,t): return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smoothstep(a,b,x):
    if a==b: return 1.0 if x>=b else 0.0
    q=clamp((x-a)/(b-a)); return q*q*(3-2*q)
def ease(t):
    t=clamp(t); return .5-.5*math.cos(math.pi*t)
def pulse(t,speed=1.0,phase=0.0):
    return .5+.5*math.sin(math.tau*(speed*t+phase))

def font(path,size):
    for candidate in (path,FONT_SERIF,FONT_SANS):
        try: return ImageFont.truetype(candidate,size)
        except OSError: pass
    return ImageFont.load_default()

def layer(size): return Image.new("RGBA",size,(0,0,0,0))

def field(w,h,seed):
    rng=np.random.default_rng(seed)
    arr=np.empty((h,w,3),dtype=np.float32); arr[:]=IVORY
    arr+=rng.normal(0,.9,(h,w,1))
    yy,xx=np.mgrid[0:h,0:w]
    halo=np.exp(-(((xx-w*.5)/(w*.37))**2+((yy-h*.40)/(h*.31))**2)*2)
    arr[...,1]+=halo*3.4; arr[...,2]+=halo*5.0
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")

def centered(d,xy,text,fnt,fill=INK):
    d.text(xy,text,font=fnt,fill=fill,anchor="mm")

def seal(im,title,subtitle="",color=INK):
    w,h=im.size; d=ImageDraw.Draw(im)
    centered(d,(w/2,h*.875),title,font(FONT_SERIF_BOLD,max(22,int(h*.04))),color)
    if subtitle:
        centered(d,(w/2,h*.923),subtitle,font(FONT_SANS,max(13,int(h*.019))),SOFT_INK)

def border(im):
    w,h=im.size; d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w-26,h-26),radius=18,outline=(*INK,45),width=2)

def glow_circle(im,x,y,r,color,alpha=170,blur=14):
    gl=layer(im.size); gd=ImageDraw.Draw(gl)
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
    gl=layer(im.size); gd=ImageDraw.Draw(gl)
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
    k=a*(len(pts)-1); i=int(k); f=k-i
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

def draw_cell(d,cx,cy,r,color=CYAN,alpha=190):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),
              fill=(*mix(WHITE,color,.12),alpha//2),
              outline=(*color,alpha),width=3)

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

def tissue_points(w,h,count=100,seed=0):
    rng=random.Random(seed); pts=[]
    cx,cy=w*.5,h*.4
    for _ in range(count):
        a=rng.random()*math.tau
        rr=(rng.random()**.58)*min(w,h)*.24
        pts.append((cx+math.cos(a)*rr*1.55,cy+math.sin(a)*rr))
    return pts

def voltage_wave(cx,cy,length,amp,t,phase=0,samples=170):
    pts=[]
    for i in range(samples):
        q=i/(samples-1)
        x=cx-length/2+q*length
        y=cy+math.sin(q*math.tau*4+t*.65+phase)*amp*math.sin(math.pi*q)**.6
        pts.append((x,y))
    return pts


# =============================================================================
# VISUALS
# =============================================================================

def vis_command_failure(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    top=(w*.50,h*.18); q=ease(u)
    glow_circle(im,*top,18,CRIMSON,180,11)
    rng=random.Random(4)
    points=[(rng.uniform(w*.12,w*.88),rng.uniform(h*.32,h*.66)) for _ in range(55)]
    for i,pt in enumerate(points):
        local=clamp(q*3-(i%3))
        arrow(d,top,pt,(*CRIMSON,int(90+80*local)),1,5)
        glow_circle(im,*pt,6,SILVER,90,5)
    seal(im,"COMMAND EVERY PART",
         "the number of instructions explodes with complexity",CRIMSON)

def vis_relation_emerges(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rng=random.Random(8); q=ease(u)
    pts=[(rng.uniform(w*.16,w*.84),rng.uniform(h*.22,h*.62)) for _ in range(36)]
    for x,y in pts:
        glow_circle(im,x,y,7,CYAN,120,6)
    if q>.22:
        for i,(x,y) in enumerate(pts):
            near=sorted(pts,key=lambda p2:(x-p2[0])**2+(y-p2[1])**2)[1:3]
            for p2 in near:
                d.line((x,y,*p2),fill=(*GOLD,int(75*q)),width=2)
    if q>.55:
        d.ellipse((w*.25,h*.20,w*.75,h*.62),outline=(*GOLD,int(190*q)),width=5)
    seal(im,"ORDER APPEARS THROUGH RELATION",
         "a whole emerges without a central dispatcher")

def vis_one_radiance(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    glow_circle(im,cx,cy,18,GOLD,190,13)
    for rr in range(35,300,32):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(88*q*(1-rr/330))),width=3)
    seal(im,"THE ONE DOES NOT PUSH",
         "it is the simple source upon which multiplicity depends",GOLD)

def vis_hypostases(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    levels=[
        ("ONE",45,GOLD),
        ("INTELLECT",105,VIOLET),
        ("SOUL",170,CYAN),
        ("NATURE",240,GREEN),
    ]
    for i,(lab,r,col) in enumerate(levels):
        local=clamp(q*len(levels)-i)
        d.ellipse((cx-r*local,cy-r*.62*local,cx+r*local,cy+r*.62*local),
                  outline=(*col,int(190*local)),width=4)
        if local>.55:
            centered(d,(cx,cy-r*.62*local-18),lab,font(FONT_SANS_BOLD,14),col)
    seal(im,"ONE · INTELLECT · SOUL · NATURE",
         "not locations, but increasingly articulated principles")

def vis_internal_external_activity(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    glow_circle(im,cx,cy,22,GOLD,190,13)
    inner=80
    d.ellipse((cx-inner,cy-inner*.62,cx+inner,cy+inner*.62),
              outline=(*GOLD,180),width=4)
    rays=[]
    for i in range(24):
        a=i*math.tau/24
        rays.append([(cx+math.cos(a)*inner,cy+math.sin(a)*inner*.62),
                     (cx+math.cos(a)*240,cy+math.sin(a)*150)])
    for ray in rays:
        glow_line(im,partial(ray,q),VIOLET,2,105,7)
    seal(im,"INNER ACTIVITY OVERFLOWS AS OUTER ACTIVITY",
         "the source remains itself while another level proceeds")

def vis_mone_proodos_epistrophe(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    remain=smoothstep(.02,.28,u)
    proceed=smoothstep(.22,.62,u)
    ret=smoothstep(.58,.96,u)
    glow_circle(im,cx,cy,17,GOLD,int(120+70*remain),12)
    out=[(cx,cy),(w*.72,h*.25),(w*.79,h*.47)]
    glow_line(im,partial(out,proceed),CYAN,5,190,12)
    back=[(w*.79,h*.47),(w*.57,h*.58),(cx,cy)]
    glow_line(im,partial(back,ret),VIOLET,5,190,12)
    centered(d,(w*.25,h*.68),"REMAIN",font(FONT_SANS_BOLD,15),GOLD)
    centered(d,(w*.50,h*.68),"PROCEED",font(FONT_SANS_BOLD,15),CYAN)
    centered(d,(w*.75,h*.68),"RETURN",font(FONT_SANS_BOLD,15),VIOLET)
    seal(im,"MONĒ · PROODOS · EPISTROPHĒ",
         "identity, expression, and reorientation toward source")

def vis_same_geometry_biology(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    levels=[
        ("CELL",48,CYAN),
        ("TISSUE",105,GREEN),
        ("ORGAN",170,GOLD),
        ("ORGANISM",235,VIOLET),
    ]
    pts=tissue_points(w,h,80,21)
    for x,y in pts:
        draw_cell(d,x,y,5,CYAN,120)
    for i,(lab,r,col) in enumerate(levels):
        local=clamp(q*len(levels)-i)
        d.ellipse((cx-r*local,cy-r*.62*local,cx+r*local,cy+r*.62*local),
                  outline=(*col,int(185*local)),width=4)
        if local>.55:
            centered(d,(cx,cy-r*.62*local-18),lab,font(FONT_SANS_BOLD,14),col)
    seal(im,"CELL · TISSUE · ORGAN · ORGANISM",
         "the same visual geometry, now as empirical biological organization")

def vis_local_competence(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    pts=tissue_points(w,h,90,31); q=ease(u)
    cx,cy=w*.50,h*.40
    for i,(x,y) in enumerate(pts):
        angle=math.atan2(cy-y,cx-x)+math.sin(i)*.35*(1-q)
        end=(x+math.cos(angle)*28,y+math.sin(angle)*28)
        draw_cell(d,x,y,6,[CYAN,GREEN,VIOLET][i%3],145)
        arrow(d,(x,y),end,(*SILVER,100),1,5)
    if q>.50:
        d.ellipse((cx-225,cy-135,cx+225,cy+135),outline=(*GOLD,180),width=5)
    seal(im,"PARTS REMAIN COMPETENT INSIDE THE WHOLE",
         "integration does not turn cells into passive bricks")

def vis_constraint_field(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    pts=tissue_points(w,h,100,42); cx,cy=w*.50,h*.40; q=ease(u)
    for i,(x,y) in enumerate(pts):
        tx=cx+(x-cx)*(.75+.10*math.sin(i))
        ty=cy+(y-cy)*(.62+.10*math.cos(i))
        xx=lerp(x,tx,q); yy=lerp(y,ty,q)
        draw_cell(d,xx,yy,6,mix(CYAN,GREEN,q),145)
    for rr in range(50,240,32):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(65*q*(1-rr/270))),width=3)
    seal(im,"THE WHOLE COMMUNICATES CONSTRAINTS",
         "competent parts discover the local route")

def vis_micromanagement_vs_goal(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.40); right=(w*.72,h*.40); q=ease(u)
    rng=random.Random(54)
    # left chaos
    for i in range(25):
        p0=(left[0]+rng.uniform(-120,120),left[1]+rng.uniform(-105,105))
        p1=(left[0]+rng.uniform(-120,120),left[1]+rng.uniform(-105,105))
        arrow(d,p0,p1,(*CRIMSON,110),1,5)
    # right constraint
    for rr in range(40,145,25):
        d.ellipse((right[0]-rr,right[1]-rr*.62,right[0]+rr,right[1]+rr*.62),
                  outline=(*GOLD,int(75*q*(1-rr/165))),width=3)
    pts=[]
    for i in range(24):
        a=i*math.tau/24
        pts.append((right[0]+math.cos(a)*100,right[1]+math.sin(a)*65))
    for x,y in pts:
        draw_cell(d,lerp(x,right[0]+(x-right[0])*.72,q),
                  lerp(y,right[1]+(y-right[1])*.65,q),5,GREEN,140)
    centered(d,(left[0],h*.68),"COMMANDS",font(FONT_SERIF_BOLD,23),CRIMSON)
    centered(d,(right[0],h*.68),"GOAL FIELD",font(FONT_SERIF_BOLD,23),GOLD)
    seal(im,"COMMANDS SCALE BADLY · GOALS RECRUIT COMPETENCE",
         "higher-order control need not specify every movement")

def vis_regeneration_return(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.24,h*.40); right=(w*.76,h*.40); q=ease(u)
    # damaged tissue
    pts=tissue_points(w,h,55,63)
    for x,y in pts:
        xx=left[0]+(x-w*.50)*.48
        yy=left[1]+(y-h*.40)*.66
        if xx>left[0]+20: continue
        draw_cell(d,xx,yy,6,CRIMSON,140)
    # target
    d.ellipse((right[0]-125,right[1]-75,right[0]+125,right[1]+75),
              outline=(*GOLD,190),width=5)
    glow_line(im,partial([left,(w*.50,h*.22),right],q),CYAN,5,200,13)
    seal(im,"REGENERATION IS BIOLOGICAL RETURN",
         "damage proceeds through correction toward a target relation")

def vis_remaining_parts(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    pts=tissue_points(w,h,95,71); q=ease(u)
    for i,(x,y) in enumerate(pts):
        draw_cell(d,x,y,6,[CYAN,GREEN,VIOLET][i%3],145)
        if i%5==0:
            a=i*.7+t*.15
            arrow(d,(x,y),(x+math.cos(a)*22,y+math.sin(a)*22),(*SILVER,95),1,4)
    if q>.4:
        d.ellipse((w*.25,h*.20,w*.75,h*.62),outline=(*GOLD,int(180*q)),width=5)
    seal(im,"REMAINING IS NOT IMMOBILITY",
         "each part preserves identity while participating in a wider act")

def vis_procession_growth(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    origins=[(cx,cy)]
    for gen in range(5):
        new=[]
        for x,y in origins:
            for a in (-.65,.65):
                nx=x+math.cos(a+gen*.22)*45
                ny=y+math.sin(a+gen*.22)*34
                glow_line(im,partial([(x,y),(nx,ny)],q),CYAN,2,120,6)
                new.append((nx,ny))
        origins=new
    for x,y in origins:
        glow_circle(im,x,y,5,GREEN,100,5)
    glow_circle(im,cx,cy,13,GOLD,170,10)
    seal(im,"PROCESSION IS DIFFERENTIATION",
         "new levels express capacities implicit in their source")

def vis_return_correction(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    rng=random.Random(80)
    starts=[(rng.uniform(w*.12,w*.88),rng.uniform(h*.20,h*.62)) for _ in range(16)]
    target=(cx,cy)
    for i,s in enumerate(starts):
        mid=(lerp(s[0],cx,.55)+math.sin(i)*25,lerp(s[1],cy,.55)+math.cos(i)*20)
        glow_line(im,partial([s,mid,target],q),[CYAN,VIOLET,GREEN][i%3],3,135,8)
    glow_circle(im,cx,cy,18,GOLD,185,12)
    seal(im,"RETURN IS ORIENTATION TOWARD COMPLETION",
         "difference is preserved while error is reduced")

def vis_city_body(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    # city blocks morph into tissue
    rng=random.Random(92)
    for i in range(55):
        x=rng.uniform(w*.14,w*.86); y=rng.uniform(h*.22,h*.61)
        if q<.52:
            ww=rng.uniform(14,35); hh=rng.uniform(18,55)
            d.rectangle((x-ww/2,y-hh/2,x+ww/2,y+hh/2),
                        outline=(*INK,int(170*(1-q))),width=2)
        draw_cell(d,x,y,lerp(2,7,q),mix(INK,CYAN,q),int(180*q))
    if q>.45:
        for rr in range(50,240,35):
            d.ellipse((w*.50-rr,h*.40-rr*.62,w*.50+rr,h*.40+rr*.62),
                      outline=(*GOLD,int(55*q*(1-rr/270))),width=2)
    seal(im,"EVERY WHOLE IS ALSO A SOCIETY",
         "cities and bodies coordinate active citizens through shared constraints")

def vis_citizen_civilization(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    rings=[
        ("MOLECULE",40,CYAN),
        ("CELL",85,GREEN),
        ("TISSUE",135,GOLD),
        ("ORGANISM",195,VIOLET),
        ("COLLECTIVE",260,CRIMSON),
    ]
    for i,(lab,r,col) in enumerate(rings):
        local=clamp(q*len(rings)-i)
        d.ellipse((cx-r*local,cy-r*.62*local,cx+r*local,cy+r*.62*local),
                  outline=(*col,int(175*local)),width=3)
        if local>.55:
            centered(d,(cx,cy-r*.62*local-15),lab,font(FONT_SANS_BOLD,12),col)
    glow_circle(im,cx,cy,12,GOLD,180,10)
    seal(im,"EVERY LEVEL IS CITIZEN AND CIVILIZATION",
         "a part below, a whole above")

def vis_descent_as_loss(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.30; q=ease(u)
    levels=[(cy,GOLD),(cy+90,VIOLET),(cy+180,CYAN),(cy+270,INK)]
    for i,(y,col) in enumerate(levels):
        r=lerp(35,150,i/3)
        d.ellipse((cx-r,y-r*.32,cx+r,y+r*.32),outline=(*col,180),width=4)
        if i<len(levels)-1:
            arrow(d,(cx,y+18),(cx,levels[i+1][0]-18),(*SILVER,140),3,8)
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.rectangle((w*.12,h*.22,w*.88,h*.65),fill=(*CRIMSON,int(35*q)))
    im.alpha_composite(gl)
    seal(im,"PROCESSION IS NOT A MORAL FALL",
         "greater multiplicity means narrower power, not cosmic guilt")

def vis_desire_plotinus(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.32,h*.40); right=(w*.72,h*.40); q=ease(u)
    glow_circle(im,*left,17,CYAN,170,11)
    glow_circle(im,*right,21,GOLD,185,12)
    glow_line(im,partial([left,(w*.52,h*.26),right],q),GOLD,5,200,13)
    centered(d,(left[0],h*.68),"SOUL",font(FONT_SERIF_BOLD,24),CYAN)
    centered(d,(right[0],h*.68),"ABSENT GOOD",font(FONT_SERIF_BOLD,24),GOLD)
    seal(im,"SOUL DESIRES WHAT IS NOT PRESENT",
         "embodiment introduces external need and directed seeking")

def vis_goal_leveraged(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.24,h*.40); right=(w*.76,h*.40); q=ease(u)
    glow_circle(im,*left,14,CYAN,160,10)
    for rr in range(40,145,25):
        d.ellipse((right[0]-rr,right[1]-rr*.62,right[0]+rr,right[1]+rr*.62),
                  outline=(*GOLD,int(75*q*(1-rr/170))),width=3)
    for i in range(12):
        a=i*math.tau/12
        p0=(left[0]+math.cos(a)*75,left[1]+math.sin(a)*55)
        p1=(right[0]+math.cos(a)*95,right[1]+math.sin(a)*60)
        glow_line(im,partial([p0,(w*.50,h*.22),p1],q),GREEN,2,110,7)
    seal(im,"A HIGHER-LEVEL GOAL LEVERAGES LOWER-LEVEL SKILL",
         "the whole gains power by not doing everything itself")

def vis_no_elimination(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    pts=tissue_points(w,h,90,111)
    for i,(x,y) in enumerate(pts):
        draw_cell(d,x,y,6,[CYAN,GREEN,VIOLET][i%3],145)
    d.ellipse((cx-230*q,cy-140*q,cx+230*q,cy+140*q),
              outline=(*GOLD,190),width=5)
    if q>.65:
        centered(d,(cx,h*.69),"WHOLE ≠ ERASURE OF PARTS",
                 font(FONT_SERIF_BOLD,24),GOLD)
    seal(im,"INTELLIGENCE SCALES · IT DOES NOT REPLACE",
         "new agency appears while local agency remains")

def vis_hierarchy_not_tyranny(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    levels=[(w*.50,h*.18,GOLD,20),(w*.50,h*.32,VIOLET,30),
            (w*.36,h*.49,CYAN,24),(w*.64,h*.49,GREEN,24),
            (w*.23,h*.64,SILVER,16),(w*.43,h*.64,SILVER,16),
            (w*.57,h*.64,SILVER,16),(w*.77,h*.64,SILVER,16)]
    q=ease(u)
    for i,(x,y,col,r) in enumerate(levels):
        glow_circle(im,x,y,r,col,150,9)
    edges=[(0,1),(1,2),(1,3),(2,4),(2,5),(3,6),(3,7)]
    for a,b in edges:
        d.line((*levels[a][:2],*levels[b][:2]),fill=(*INK,int(140*q)),width=3)
    seal(im,"HIERARCHY NEED NOT MEAN TYRANNY",
         "higher levels coordinate ranges of possibility rather than puppeteering parts")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    claims=[
        ("PLOTINUS EXPLAINS ONTOLOGICAL DEPENDENCE","PHILOSOPHY",VIOLET),
        ("LEVIN TESTS BIOLOGICAL GOAL-DIRECTEDNESS","SCIENCE",GREEN),
        ("THE GEOMETRIES ARE COMPARABLE","FORMAL ANALOGY",CYAN),
        ("REGENERATION PROVES THE ONE","NOT ESTABLISHED",CRIMSON),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(claims):
        local=clamp(q*len(claims)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.40,y),claim,font(FONT_SANS_BOLD,14),INK)
        centered(d,(w*.74,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"FORMAL HOMOLOGY IS NOT IDENTICAL EXPLANATION",
         "the comparison is illuminating only while the levels remain distinct")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    pts=tissue_points(w,h,110,150)
    for i,(x,y) in enumerate(pts):
        draw_cell(d,x,y,5,[CYAN,GREEN,VIOLET][i%3],125)
    for rr,col in [(55,GOLD),(115,VIOLET),(180,CYAN),(250,GREEN)]:
        d.ellipse((cx-rr*q,cy-rr*.62*q,cx+rr*q,cy+rr*.62*q),
                  outline=(*col,int(175*q)),width=4)
    glow_circle(im,cx,cy,15,GOLD,185,12)
    if q>.72:
        centered(d,(cx,h*.69),"MONĒ · PROODOS · EPISTROPHĒ",
                 font(FONT_SERIF_BOLD,24),GOLD)
    seal(im,"THE ONE DOES NOT COMMAND",
         "a living whole coordinates active parts by giving their competence a larger form",GOLD)


VISUALS: dict[str,Callable] = {
    "command":vis_command_failure,
    "relation":vis_relation_emerges,
    "one":vis_one_radiance,
    "hypostases":vis_hypostases,
    "activity":vis_internal_external_activity,
    "triad":vis_mone_proodos_epistrophe,
    "biolevels":vis_same_geometry_biology,
    "local":vis_local_competence,
    "constraint":vis_constraint_field,
    "compare":vis_micromanagement_vs_goal,
    "regen":vis_regeneration_return,
    "remain":vis_remaining_parts,
    "process":vis_procession_growth,
    "return":vis_return_correction,
    "city":vis_city_body,
    "citizen":vis_citizen_civilization,
    "descent":vis_descent_as_loss,
    "desire":vis_desire_plotinus,
    "leverage":vis_goal_leveraged,
    "noerase":vis_no_elimination,
    "hierarchy":vis_hierarchy_not_tyranny,
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
    Scene("Command fantasy",
          "We imagine intelligence as something issuing commands.",
          7.0,"command",{}),
    Scene("Too many orders",
          "One controller specifies every movement, every molecule, every local correction.",
          9.0,"command",{}),
    Scene("Explosion",
          "But the number of instructions explodes with complexity.",
          7.5,"command",{}),

    Scene("Relations",
          "Remove the commands.",
          5.5,"relation",{}),
    Scene("Local links",
          "Let the parts sense one another, preserve local competence, and respond to shared constraints.",
          9.5,"relation",{}),
    Scene("Whole",
          "A coherent whole begins to appear.",
          7.0,"relation",{}),

    Scene("Plotinus",
          "Plotinus begins from a deeper problem.",
          7.0,"one",{}),
    Scene("Multiplicity",
          "Every complex thing depends upon principles that make its unity possible.",
          9.0,"one",{}),
    Scene("The One",
          "At the limit of explanation he places the One: absolutely simple, beyond the multiplicity of thinker and thought.",
          10.0,"one",{}),

    Scene("Not craftsman",
          "The One is not a cosmic engineer pushing atoms into place.",
          8.0,"one",{}),
    Scene("Dependence",
          "It names the ultimate dependence of every articulated reality upon a source that is not itself another articulated thing.",
          10.0,"one",{}),
    Scene("Radiance",
          "Its causality is better imagined as radiance than command.",
          8.0,"one",{}),

    Scene("Hypostases",
          "Plotinus describes three fundamental principles: the One, Intellect, and Soul.",
          9.0,"hypostases",{}),
    Scene("Nature",
          "Soul's outward activity gives rise to Nature, the intelligible organization of embodied things.",
          9.0,"hypostases",{}),
    Scene("Not places",
          "These are not floors in a supernatural building.",
          7.5,"hypostases",{}),
    Scene("Modes",
          "They are increasingly articulated modes of unity, intelligibility, life, and manifestation.",
          9.0,"hypostases",{}),

    Scene("Inner activity",
          "A source remains what it is through its inner activity.",
          8.0,"activity",{}),
    Scene("Outer activity",
          "Its power appears outwardly as another level of reality.",
          8.0,"activity",{}),
    Scene("No depletion",
          "The source is not divided into pieces or depleted by what proceeds from it.",
          9.0,"activity",{}),

    Scene("Proclus",
          "Proclus later gives this movement a precise triadic rhythm.",
          8.0,"triad",{}),
    Scene("Remaining",
          "Remaining: the cause preserves its own identity.",
          7.0,"triad",{}),
    Scene("Procession",
          "Procession: an effect expresses the cause at a more differentiated level.",
          8.5,"triad",{}),
    Scene("Return",
          "Return: the effect becomes intelligible and complete through orientation toward its source.",
          9.0,"triad",{}),

    Scene("First reveal",
          "Now replace the philosophical labels.",
          7.0,"biolevels",{}),
    Scene("Biological levels",
          "Cell. Tissue. Organ. Organism.",
          7.5,"biolevels",{}),
    Scene("Same geometry",
          "The visual geometry is strikingly similar.",
          7.0,"biolevels",{}),
    Scene("Different theory",
          "But the explanatory status is different. This is biology, not emanation.",
          8.5,"caution",{}),

    Scene("Levin",
          "Michael Levin studies how competent biological parts form larger goal-directed wholes.",
          9.5,"local",{}),
    Scene("Cells remain agents",
          "Cells do not become passive bricks when they enter a tissue.",
          8.0,"local",{}),
    Scene("Local work",
          "They regulate metabolism, voltage, shape, migration, gene expression, and relations with neighbors.",
          10.0,"local",{}),

    Scene("Larger goals",
          "Yet the tissue can pursue outcomes defined at a scale no single cell occupies.",
          9.5,"constraint",{}),
    Scene("Anatomy",
          "Polarity, proportion, wound closure, organ position, and whole-body form.",
          9.0,"constraint",{}),
    Scene("Constraint field",
          "The whole influences local action by changing constraints, signals, and error conditions.",
          9.5,"constraint",{}),

    Scene("Comparison",
          "This is the biological answer to micromanagement.",
          8.0,"compare",{}),
    Scene("Commands fail",
          "Do not specify every cell movement.",
          7.0,"compare",{}),
    Scene("Communicate target",
          "Communicate a target state to a collective already competent at solving local problems.",
          9.5,"compare",{}),

    Scene("Regeneration",
          "Regeneration makes the architecture visible.",
          8.0,"regen",{}),
    Scene("Damage",
          "A wound disrupts present anatomy.",
          7.0,"regen",{}),
    Scene("Correction",
          "Cells grow, migrate, differentiate, and remodel toward a target morphology.",
          9.5,"regen",{}),
    Scene("Stop",
          "The process stops when the larger relation has been restored.",
          8.0,"regen",{}),

    Scene("Biological remaining",
          "The cells remain themselves.",
          6.5,"remain",{}),
    Scene("Not immobile",
          "Remaining does not mean inactivity. Each part preserves its organization while participating in a wider act.",
          10.0,"remain",{}),

    Scene("Biological procession",
          "Development is procession in a formal, not metaphysical, sense.",
          9.0,"process",{}),
    Scene("Differentiation",
          "One living system differentiates into many specialized tissues and organs.",
          9.0,"process",{}),
    Scene("More articulation",
          "The organism becomes more articulated without losing all unity.",
          8.0,"process",{}),

    Scene("Biological return",
          "Regulation is return in a similarly formal sense.",
          8.5,"return",{}),
    Scene("Deviation",
          "A system departs from a viable state.",
          7.0,"return",{}),
    Scene("Reorientation",
          "Feedback, memory, and action reorient it toward completion.",
          8.5,"return",{}),

    Scene("Danger",
          "The analogy becomes misleading if procession is treated as cell division or the One as a bioelectric field.",
          10.0,"caution",{}),
    Scene("Distinct questions",
          "Plotinus explains ontological dependence. Levin tests biological coordination.",
          9.0,"caution",{}),
    Scene("Formal comparison",
          "The comparison concerns form: active parts, larger unities, constrained expression, and corrective return.",
          10.0,"caution",{}),

    Scene("Descent",
          "Plotinian procession is also not a story of moral corruption.",
          8.5,"descent",{}),
    Scene("Narrowing",
          "Greater multiplicity means narrower power and greater dependence.",
          8.0,"descent",{}),
    Scene("Not evil biology",
          "Embodiment is not bad because it is biological.",
          7.0,"descent",{}),

    Scene("Desire",
          "For Plotinus, embodied soul desires what is not present.",
          8.0,"desire",{}),
    Scene("External need",
          "Food, knowledge, sleep, reproduction, and other goods are sought beyond the agent's current state.",
          10.0,"desire",{}),
    Scene("Biological resonance",
          "Here Plotinus unexpectedly touches the biological problem of a bounded life pursuing absent conditions.",
          9.5,"desire",{}),

    Scene("Leverage",
          "A higher-level whole gains power by not performing every lower-level task.",
          9.0,"leverage",{}),
    Scene("Recruit",
          "It recruits local competencies through a shared goal.",
          8.0,"leverage",{}),
    Scene("Intelligence",
          "Intelligence scales by leverage.",
          7.0,"leverage",{}),

    Scene("No elimination",
          "A tissue does not eliminate cellular agency.",
          7.0,"noerase",{}),
    Scene("No replacement",
          "An organism does not replace every tissue with one central agent.",
          8.0,"noerase",{}),
    Scene("New level",
          "A new level of agency appears while lower-level capacities remain active.",
          9.0,"noerase",{}),
    Scene("Core line",
          "Intelligence scales. It does not replace.",
          7.0,"noerase",{}),

    Scene("Hierarchy",
          "This gives us a different image of hierarchy.",
          7.5,"hierarchy",{}),
    Scene("Not tyranny",
          "Hierarchy need not mean tyranny.",
          6.5,"hierarchy",{}),
    Scene("Range of freedom",
          "A higher level can coordinate ranges of possibility while leaving local details to competent parts.",
          9.5,"hierarchy",{}),

    Scene("City",
          "The same logic appears in cities, ecosystems, institutions, and nervous systems.",
          9.0,"city",{}),
    Scene("Citizens",
          "Each whole depends upon active citizens whose goals only partly overlap.",
          8.5,"city",{}),
    Scene("Coordination problem",
          "The central problem is always coordination without annihilation.",
          8.5,"city",{}),

    Scene("Citizen civilization",
          "Every biological level is simultaneously citizen and civilization.",
          9.0,"citizen",{}),
    Scene("Part and whole",
          "A whole relative to what lies below. A part relative to what lies above.",
          8.5,"citizen",{}),
    Scene("Open upward",
          "No level is obviously the final scale of agency.",
          8.0,"citizen",{}),

    Scene("Return to philosophy",
          "Plotinus asks what makes any coherent multiplicity possible.",
          8.5,"hypostases",{}),
    Scene("Return to biology",
          "Levin asks how living multiplicities remember goals and correct toward them.",
          9.0,"biolevels",{}),
    Scene("Synthesis",
          "One offers an ontology of dependence. The other offers an experimental science of multiscale agency.",
          10.0,"caution",{}),

    Scene("Final image",
          "A living whole is not a dictator surrounded by obedient matter.",
          8.0,"final",{}),
    Scene("Field",
          "It is a field in which competent parts discover how to become more together than they could become alone.",
          10.0,"final",{}),
    Scene("Closing",
          "The One does not command. A living whole coordinates active parts by giving their competence a larger form.",
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
    if not exe: raise RuntimeError("ffmpeg is required but was not found on PATH")
    return exe

def encode_scene(index,fps):
    frame_dir=FRAMES/f"scene_{index:03d}"
    output=SCENES_DIR/f"scene_{index:03d}.mp4"
    subprocess.run([
        ffmpeg_path(),"-y",
        "-framerate",str(fps),
        "-i",str(frame_dir/"%05d.jpg"),
        "-c:v","libx264","-preset","medium","-crf","18",
        "-pix_fmt","yuv420p","-movflags","+faststart",str(output),
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return output

def render_scene(index,scene,fps,width,height,preview):
    frame_dir=FRAMES/f"scene_{index:03d}"
    frame_dir.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)
    count=max(2,round(scene.duration*fps))

    if preview:
        for oi,fi in enumerate([0,int(count*.33),int(count*.72),count-1]):
            render_frame(scene,fi,count,width,height,index*10000+fi).save(
                frame_dir/f"preview_{oi:02d}.jpg",quality=95
            )
        return frame_dir

    for fi in range(count):
        p=frame_dir/f"{fi:05d}.jpg"
        if not p.exists():
            render_frame(scene,fi,count,width,height,index*10000+fi).save(
                p,quality=95,subsampling=0
            )
    return encode_scene(index,fps)

def concatenate(paths):
    txt=OUTPUT/"concat.txt"
    txt.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    output=OUTPUT/"one_does_not_command.mp4"
    subprocess.run([
        ffmpeg_path(),"-y","-f","concat","-safe","0",
        "-i",str(txt),"-c","copy","-movflags","+faststart",str(output),
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return output

def export_timeline():
    cursor=0.0; records=[]
    for index,scene in enumerate(SCENES,1):
        rec=asdict(scene)
        rec["scene_id"]=f"scene_{index:03d}"
        rec["start_seconds"]=round(cursor,3)
        cursor+=scene.duration
        rec["end_seconds"]=round(cursor,3)
        records.append(rec)
    path=OUTPUT/"narration_timeline.json"
    path.write_text(json.dumps({
        "title":"the one does not command",
        "subtitle":"from Plotinus and Proclus to Michael Levin",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"gold source becoming distributed constraint field",
        "scenes":records,
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return path

def make_contact_sheet(width,height):
    tw=320; th=int(tw*height/width); cols=4
    rows=math.ceil(len(SCENES)/cols); cell_h=th+48
    sheet=Image.new("RGB",(cols*tw,rows*cell_h),IVORY)
    d=ImageDraw.Draw(sheet); lf=font(FONT_SANS_BOLD,14)
    for index,scene in enumerate(SCENES,1):
        count=max(2,round(scene.duration*DEFAULT_FPS))
        image=render_frame(scene,int(count*.72),count,width,height,index*10000+72)
        image.thumbnail((tw,th))
        slot=index-1; x=(slot%cols)*tw; y=(slot//cols)*cell_h
        sheet.paste(image,(x,y))
        d.text((x+8,y+th+7),f"{index:02d}  {scene.title}",font=lf,fill=INK)
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
    print(f"Runtime: {sum(s.duration for s in SCENES)/60:.2f} minutes")

    if args.scene:
        if not 1<=args.scene<=len(SCENES):
            raise ValueError("scene out of range")
        print(render_scene(
            args.scene,SCENES[args.scene-1],args.fps,args.width,args.height,args.preview
        ))
        return

    rendered=[]
    for index,scene in enumerate(SCENES,1):
        print(f"[{index:02d}/{len(SCENES):02d}] {scene.title} ({scene.duration:.1f}s)")
        result=render_scene(index,scene,args.fps,args.width,args.height,args.preview)
        if not args.preview:
            rendered.append(result)

    if not args.no_contact_sheet:
        print(f"Contact sheet: {make_contact_sheet(args.width,args.height)}")

    if not args.preview:
        print(f"Final video: {concatenate(rendered)}")

if __name__=="__main__":
    main()
