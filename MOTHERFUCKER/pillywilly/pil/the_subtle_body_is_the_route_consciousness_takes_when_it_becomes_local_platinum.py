#!/usr/bin/env python3
"""
THE SUBTLE BODY IS THE ROUTE CONSCIOUSNESS TAKES WHEN IT BECOMES LOCAL
An original Imaginarium visual essay and Platinum-house procedural renderer.

THESIS
------
The subtle body is not best understood as a second invisible anatomy made of
glowing tubes. It is an intermediate organization: the route by which
undivided capacity becomes breath, sensation, thought, memory, image, action,
ritual identity, and—according to some traditions—a vehicle through dream,
death, and visionary ascent.

The nāḍīs are therefore not merely pipes.
Prāṇa is not merely air.
The body of light is not made of photons.
The chakras are not decorative lotuses.

They are different visual languages for topology, constraint, mediation,
integration, transmission, memory, and recognition.

SOURCE CONSTELLATION
--------------------
• Synesius: phantasia, pneuma, and the vehicle of the soul
• Iamblichus and Proclus: soul vehicle, participation, theurgy
• Ficino: spiritus as mediator of body, soul, image, and stars
• Laya Yoga and Haṭha traditions: prāṇa, nāḍī, granthi, suṣumṇā, kuṇḍalinī
• Kashmir Śaivism: spanda, śakti, contraction, ābhāsa, recognition
• Tibetan completion-stage systems: channels, winds, drops, clear light
• Vajrayāna dream and death yogas
• modern network, control, and dynamical-systems analogies used carefully

DESIGN CONTRACT
---------------
• Every shot lasts 5–10 seconds.
• Every shot performs the narrated operation.
• Clean white field; deep indigo only for dream, death, and clear-light depth.
• No static slide layouts and no decorative chakra infographics.
• White = undifferentiated awareness
• Silver = subtle vehicle / structural continuity
• Cyan = prāṇa, pneuma, wind, transmission
• Gold = recognition, intellect, central integration
• Violet = imaginal depth, dream body, latent form
• Crimson = contraction, obstruction, granthi, fragmentation
• Green = integration, healing, embodied return
• Continuity object: one luminous lattice differentiates into every later form.
• Nāḍīs are rendered as dynamic routing topology, not plumbing.
• Chakras are rendered as stable knots of circulation and compression.
• Suṣumṇā is rendered as alignment of competing trajectories.
• Kuṇḍalinī is rendered as recursive activation and phase transition.
• The body of light is rendered as coherent relational geometry, not photons.
• Final criterion: subtle embodiment returns to ordinary life as clarity and action.

OUTPUT
------
output_subtle_body_route/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  the_subtle_body_is_the_route_consciousness_takes_when_it_becomes_local.mp4
  narration_timeline.json
  original_essay.md
  contact_sheet.jpg
"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/"output_subtle_body_route"
FRAMES=OUTPUT/"frames"
SCENES_DIR=OUTPUT/"scenes"

DEFAULT_WIDTH=1280
DEFAULT_HEIGHT=720
DEFAULT_FPS=10

WHITE=(248,247,243); INK=(28,31,35); SOFT=(84,88,94)
SILVER=(177,184,190); PALE_SILVER=(224,227,229)
CYAN=(55,153,181); PALE_CYAN=(192,226,233)
GOLD=(194,153,68); PALE_GOLD=(235,218,175)
VIOLET=(104,79,146); PALE_VIOLET=(216,205,232)
CRIMSON=(158,52,66); PALE_CRIMSON=(230,192,198)
GREEN=(70,139,98); PALE_GREEN=(194,225,206)
VOID=(22,25,31); NIGHT=(17,23,39)

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

def body(d,cx,cy,scale=1,col=INK,alpha=180):
    d.ellipse((cx-22*scale,cy-115*scale,cx+22*scale,cy-71*scale),outline=(*col,alpha),width=4)
    d.line((cx,cy-71*scale,cx,cy+55*scale),fill=(*col,alpha),width=5)
    d.line((cx,cy-30*scale,cx-72*scale,cy+12*scale),fill=(*col,alpha),width=5)
    d.line((cx,cy-30*scale,cx+72*scale,cy+12*scale),fill=(*col,alpha),width=5)
    d.line((cx,cy+55*scale,cx-45*scale,cy+130*scale),fill=(*col,alpha),width=5)
    d.line((cx,cy+55*scale,cx+45*scale,cy+130*scale),fill=(*col,alpha),width=5)

def lattice_nodes(cx,cy,rx,ry,rings=4,points=12):
    nodes=[(cx,cy)]
    for j in range(1,rings+1):
        rr=j/rings
        for i in range(points):
            a=i*math.tau/points+(j%2)*math.pi/points
            nodes.append((cx+math.cos(a)*rx*rr,cy+math.sin(a)*ry*rr))
    return nodes

def draw_lattice(im,cx,cy,rx,ry,progress=1,col=SILVER,alpha=130):
    d=ImageDraw.Draw(im)
    nodes=lattice_nodes(cx,cy,rx,ry,4,12)
    q=ease(progress)
    for i,a in enumerate(nodes):
        if i==0: continue
        b=nodes[1+((i-1+3)%48)]
        glow_line(im,partial([a,b],q),col,2,7,alpha)
        if i%3==0: glow_line(im,partial([a,(cx,cy)],q),col,2,7,alpha//2)
    for x,y in nodes:
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*col,int(alpha*q)))

def wave_path(w,h,phase=0,amp=.10,offset=0):
    pts=[]
    for i in range(200):
        q=i/199
        x=lerp(w*.10,w*.90,q)
        y=h*(.42+offset)+math.sin(q*math.tau*2+phase)*h*amp+math.sin(q*math.tau*5-phase)*h*.015
        pts.append((x,y))
    return pts

def channel_path(cx,cy,height,side,phase=0,turns=3,points=180):
    pts=[]
    for i in range(points):
        q=i/(points-1)
        y=lerp(cy+height/2,cy-height/2,q)
        x=cx+side*math.sin(q*math.tau*turns+phase)*55
        pts.append((x,y))
    return pts

def star_field(d,w,h,seed=5,alpha=95):
    rng=random.Random(seed)
    for _ in range(100):
        x=rng.uniform(w*.08,w*.92); y=rng.uniform(h*.08,h*.72)
        r=rng.choice([1,1,1,2])
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*PALE_GOLD,alpha))

@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict

def v_field_to_body(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); q=ease(u)
    cx,cy=w*.5,h*.42
    draw_lattice(im,cx,cy,lerp(w*.32,w*.17,q),lerp(h*.28,h*.31,q),q,mix(WHITE,SILVER,q),140)
    body(d,cx,cy,lerp(.35,1,q),mix(SILVER,INK,q),int(80+110*q))
    seal(im,"THE SUBTLE BODY IS AN INTERMEDIATE ORGANIZATION","not a second corpse hidden inside the first")

def v_layers(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    levels=[("AWARENESS",WHITE,h*.13),("IMAGE",VIOLET,h*.29),("PRĀṆA",CYAN,h*.45),("SENSATION",GOLD,h*.60),("ACTION",INK,h*.72)]
    x=w*.5; q=ease(u)
    for i,(txt,col,y) in enumerate(levels):
        outline=GOLD if col==WHITE else col
        d.ellipse((x-66,y-27,x+66,y+27),fill=(*mix(WHITE,outline,.12),220),outline=(*outline,180),width=3)
        ctext(d,(x,y),txt,font(FSSB,int(h*.013)),outline)
        if i>0:
            glow_line(im,partial([(x,levels[i-1][2]+27),(x,y-27)],q),mix(outline,levels[i-1][1] if levels[i-1][1]!=WHITE else GOLD,.5),4,11,160)
    seal(im,"LOCALITY IS BUILT IN LAYERS","capacity becomes image, current, sensation, and act")

def v_prana(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); q=ease(u)
    glow_line(im,partial(wave_path(w,h,t*.35,.075),q),CYAN,6,15,210)
    for i,txt in enumerate(("TENSION","VECTOR","CURRENT","BREATH","THOUGHT","ACTION")):
        x=w*(.13+i*.145)
        if q>i/7: ctext(d,(x,h*.64),txt,font(FSSB,int(h*.011)),mix(CYAN,GOLD,i/5))
    seal(im,"PRĀṆA IS MOVEMENT BEFORE VISIBLE MOVEMENT","not oxygen, but organized tendency")

def v_nadis_network(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42
    body(d,cx,cy,.95,INK,120)
    q=ease(u)
    rng=random.Random(7)
    nodes=[(cx+rng.uniform(-120,120),cy+rng.uniform(-220,210)) for _ in range(36)]
    for i,a in enumerate(nodes):
        for step in (3,7):
            b=nodes[(i+step)%len(nodes)]
            glow_line(im,partial([a,b],q),mix(CYAN,VIOLET,(i%12)/11),2,7,70)
        d.ellipse((a[0]-4,a[1]-4,a[0]+4,a[1]+4),fill=(*CYAN,130))
    seal(im,"NĀḌĪS ARE ROUTING RELATIONS","a topology of transmission, not anatomical plumbing")

def v_ida_pingala(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42; q=ease(u)
    body(d,cx,cy,.95,INK,100)
    left=channel_path(cx,cy,h*.58,-1,t*.05)
    right=channel_path(cx,cy,h*.58,1,t*.05+math.pi)
    glow_line(im,partial(left,q),CYAN,5,13,190)
    glow_line(im,partial(right,q),GOLD,5,13,190)
    for i in range(7):
        y=lerp(cy+h*.29,cy-h*.29,i/6)
        glow_circle(im,cx,y,8,mix(CYAN,GOLD,i/6),100,7)
    seal(im,"IḌĀ AND PIṄGALĀ GENERATE RHYTHM THROUGH DIFFERENCE","cooling and heating · inward and outward · lunar and solar")

def v_sushumna(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42
    body(d,cx,cy,.95,INK,95)
    q=ease(u)
    rng=random.Random(19)
    paths=[]
    for i in range(18):
        pts=[]
        for j in range(120):
            s=j/119
            y=lerp(cy+h*.30,cy-h*.30,s)
            x=cx+math.sin(s*math.tau*(2+i%4)+i)*lerp(110,8,q)
            pts.append((x,y))
        paths.append(pts)
    for i,path in enumerate(paths):
        glow_line(im,path,mix(CRIMSON,GOLD,q),2,7,55)
    glow_line(im,partial([(cx,cy+h*.30),(cx,cy-h*.30)],q),GOLD,7,16,220)
    seal(im,"SUṢUMṆĀ IS ALIGNMENT","many competing trajectories collapse into one traversable axis")

def v_chakra_knots(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42; q=ease(u)
    body(d,cx,cy,.95,INK,90)
    ys=[h*.67,h*.58,h*.49,h*.40,h*.31,h*.22]
    cols=[CRIMSON,GOLD,GREEN,CYAN,VIOLET,SILVER]
    for i,(y,col) in enumerate(zip(ys,cols)):
        qq=smooth(i*.10,.75+i*.04,u)
        for r in (18,32,48):
            d.arc((cx-r*qq,y-r*.62*qq,cx+r*qq,y+r*.62*qq),10,int(320*qq),fill=(*col,110),width=3)
        glow_circle(im,cx,y,8+8*qq,col,110,8)
    seal(im,"CHAKRAS ARE STABLE KNOTS OF CIRCULATION","compression, integration, and redistribution")

def v_granthi(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42
    body(d,cx,cy,.95,INK,90)
    q=ease(u)
    ys=[h*.59,h*.43,h*.27]
    for i,y in enumerate(ys):
        r=lerp(55,18,q)
        for k in range(4):
            a=k*math.pi/2+t*.4
            x=cx+math.cos(a)*r; yy=y+math.sin(a)*r*.55
            glow_line(im,[(cx,y),(x,yy)],mix(CRIMSON,GREEN,q),5,12,170)
    glow_line(im,partial([(cx,h*.69),(cx,h*.18)],q),GOLD,5,13,190)
    seal(im,"GRANTHIS ARE CONSTRAINTS THAT HAVE BECOME SELF-HOLDING","the knot loosens when circulation no longer defends its old form")

def v_kundalini(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42
    body(d,cx,cy,.95,INK,80)
    q=ease(u)
    # recursive activation wave
    y0=h*.69; y1=h*.18
    for i in range(80):
        s=i/79
        y=lerp(y0,y1,s)
        active=s<=q
        amp=50*(1-s)
        x=cx+math.sin(s*math.tau*4+t*.45)*amp
        col=mix(CRIMSON,GOLD,s)
        if active: glow_circle(im,x,y,5+4*pulse(t,.5,s),col,90,7)
    for y,col in zip([h*.67,h*.58,h*.49,h*.40,h*.31,h*.22],[CRIMSON,GOLD,GREEN,CYAN,VIOLET,SILVER]):
        if q>(h*.69-y)/(h*.51): glow_circle(im,cx,y,14,col,140,10)
    seal(im,"KUṆḌALINĪ IS A CASCADING REORGANIZATION","potential becomes recursive activation, synchronization, and phase change")

def v_body_light(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42; q=ease(u)
    body(d,cx,cy,1,INK,int(150*(1-q)))
    draw_lattice(im,cx,cy,w*.18,h*.31,q,mix(SILVER,GOLD,q),150)
    glow_circle(im,cx,h*.39,18+18*q,GOLD,120,12)
    seal(im,"THE BODY OF LIGHT IS COHERENT RELATION","not a silhouette made of photons")

def v_synesius_vehicle(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42); q=ease(u)
    body(d,*left,.75,INK,160)
    d.ellipse((right[0]-145,right[1]-165,right[0]+145,right[1]+165),outline=(*CYAN,130),width=4)
    draw_lattice(im,right[0],right[1],110,135,q,mix(SILVER,VIOLET,q),120)
    glow_line(im,partial([left,(w*.50,h*.30),right],q),CYAN,4,11,150)
    seal(im,"SYNESIUS CALLS IT THE VEHICLE OF PHANTASIA","the subtle medium that carries image between soul and body")

def v_ficino_spiritus(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42; q=ease(u)
    star_field(d,w,h,9,70)
    body(d,cx,cy,.78,SILVER,120)
    for i,col in enumerate((GOLD,VIOLET,CYAN,GREEN)):
        x=w*(.18+i*.21)
        glow_line(im,partial([(x,h*.09),(cx,cy)],smooth(i*.08,.9,u)),col,4,11,140)
    for r in (80,130,185):
        d.arc((cx-r,cy-r*.62,cx+r,cy+r*.62),20,int(310*q),fill=(*PALE_GOLD,80),width=3)
    seal(im,"FICINO'S SPIRITUS MAKES BODY AND STARS MUTUALLY LEGIBLE","a subtle atmosphere of sensation, image, and influence",dark=True)

def v_tibetan_winds(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42; q=ease(u)
    body(d,cx,cy,.95,INK,85)
    channels=[channel_path(cx,cy,h*.58,-1,0,2.4),[(cx,lerp(cy+h*.29,cy-h*.29,i/179)) for i in range(180)],channel_path(cx,cy,h*.58,1,math.pi,2.4)]
    for path,col in zip(channels,[CYAN,GOLD,VIOLET]):
        glow_line(im,partial(path,q),col,5,13,180)
    # winds carry thought glyphs
    for i in range(12):
        s=(i/12+t*.12)%1
        x,y=channels[i%3][int(s*179)]
        d.ellipse((x-5,y-5,x+5,y+5),fill=(*(CYAN if i%3==0 else GOLD),150))
    seal(im,"WINDS CARRY COGNITION","change the wind, and the organization of mind changes")

def v_clear_light(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42; q=ease(u)
    star_field(d,w,h,17,int(70*(1-q)))
    draw_lattice(im,cx,cy,w*.20,h*.30,1-q,SILVER,int(140*(1-q)))
    glow_circle(im,cx,cy,lerp(18,135,q),WHITE,150,28)
    seal(im,"CLEAR LIGHT IS WHAT REMAINS WHEN STRUCTURE RELEASES","not blankness, but luminosity without ordinary construction",dark=True)

def v_dream_body(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); left=(w*.28,h*.42); right=(w*.72,h*.42); q=ease(u)
    body(d,*left,.78,INK,150)
    draw_lattice(im,right[0],right[1],110,145,q,VIOLET,130)
    for i in range(8):
        glow_line(im,partial([(left[0],left[1]),(right[0],right[1])],smooth(i*.05,.85,u)),mix(CYAN,VIOLET,i/7),2,7,60)
    seal(im,"THE DREAM BODY IS THE SUBTLE VEHICLE UNDER DIFFERENT CONSTRAINTS","location persists while physical input loosens")

def v_ritual_rewire(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42; q=ease(u)
    draw_lattice(im,cx,cy,w*.22,h*.31,1,SILVER,95)
    # mantra, mudra, nyasa rewrite edges
    for i,col in enumerate((CYAN,GOLD,VIOLET,GREEN)):
        a=i*math.tau/4
        x=cx+math.cos(a)*w*.30; y=cy+math.sin(a)*h*.27
        glow_line(im,partial([(x,y),(cx,cy)],smooth(i*.08,.9,u)),col,4,11,150)
    glow_circle(im,cx,cy,18+18*q,GOLD,130,12)
    seal(im,"RITUAL REWRITES SUBTLE TOPOLOGY","mantra, mudrā, nyāsa, breath, and image alter the routes of participation")

def v_death_layers(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.5,h*.42; q=ease(u)
    body(d,cx,cy,1,INK,int(180*(1-q)))
    layers=[(w*.16,h*.29,SILVER),(w*.13,h*.24,CYAN),(w*.10,h*.19,VIOLET),(w*.07,h*.14,GOLD)]
    for i,(rx,ry,col) in enumerate(layers):
        qq=smooth(i*.08,.90,u)
        d.ellipse((cx-rx*qq,cy-ry*qq,cx+rx*qq,cy+ry*qq),outline=(*col,int(140*qq)),width=4)
    seal(im,"DEATH SYSTEMS ASK WHICH ORGANIZATION PERSISTS","body, breath, image, tendency, vehicle, or recognition",dark=True)

def v_science_boundary(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    d.rounded_rectangle((left[0]-120,left[1]-80,left[0]+120,left[1]+80),radius=18,
                        fill=(*PALE_CYAN,210),outline=(*CYAN,180),width=3)
    ctext(d,left,"NETWORK\nDYNAMICS",font(FSSB,int(h*.017)),CYAN)
    draw_lattice(im,right[0],right[1],105,130,ease(u),GOLD,120)
    q=smooth(.35,.9,u)
    d.line((w*.49,h*.23,w*.51,h*.60),fill=(*CRIMSON,int(210*q)),width=6)
    seal(im,"ANALOGY IS NOT IDENTITY","network science can clarify topology without proving subtle anatomy")

def v_recognition(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); left=(w*.25,h*.42); right=(w*.75,h*.42); q=ease(u)
    body(d,*left,.72,INK,160)
    draw_lattice(im,right[0],right[1],105,135,q,GOLD,140)
    glow_line(im,partial([left,(w*.50,h*.30),right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.50,h*.56),left],smooth(.30,.95,u)),GOLD,5,13,200)
    seal(im,"RECOGNITION REVERSES THE SEARCH","the subtle body is no longer elsewhere; it is the pattern of appearing itself")

def v_return(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    draw_lattice(im,w*.22,h*.42,75,100,ease(u),GOLD,120)
    d.line((w*.08,h*.63,w*.92,h*.63),fill=(*INK,120),width=5)
    for i in range(8):
        x=w*(.16+i*.09)
        d.rectangle((x-18,h*.49,x+18,h*.63),fill=(*PALE_SILVER,120),outline=(*SILVER,100))
    q=ease(u)
    glow_line(im,partial([(w*.30,h*.42),(w*.45,h*.55),(w*.64,h*.50),(w*.88,h*.57)],q),GREEN,6,14,210)
    seal(im,"THE SUBTLE BODY MUST RETURN AS CONDUCT","clearer speech, steadier attention, less fragmented action")

def v_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.55,h*.42; q=ease(u)
    draw_lattice(im,cx,cy,lerp(60,w*.22,q),lerp(80,h*.31,q),q,mix(SILVER,GOLD,q),150)
    glow_line(im,partial(wave_path(w,h,t*.30,.055),q),CYAN,5,14,170)
    for y,col in zip([h*.67,h*.58,h*.49,h*.40,h*.31,h*.22],[CRIMSON,GOLD,GREEN,CYAN,VIOLET,SILVER]):
        if q>(h*.69-y)/h*.52: glow_circle(im,cx,y,10+8*q,col,115,9)
    glow_circle(im,cx,h*.39,18+20*q,GOLD,140,13)
    seal(im,"THE SUBTLE BODY IS THE ROUTE CONSCIOUSNESS TAKES WHEN IT BECOMES LOCAL",
         "lattice becomes current · current becomes body · body becomes recognition",color=GREEN)

VISUALS:dict[str,Callable]={
    "field":v_field_to_body,
    "layers":v_layers,
    "prana":v_prana,
    "nadis":v_nadis_network,
    "ida":v_ida_pingala,
    "sushumna":v_sushumna,
    "chakras":v_chakra_knots,
    "granthi":v_granthi,
    "kundalini":v_kundalini,
    "light":v_body_light,
    "synesius":v_synesius_vehicle,
    "ficino":v_ficino_spiritus,
    "winds":v_tibetan_winds,
    "clear":v_clear_light,
    "dream":v_dream_body,
    "ritual":v_ritual_rewire,
    "death":v_death_layers,
    "science":v_science_boundary,
    "recognition":v_recognition,
    "return":v_return,
    "final":v_final,
}

SCENES:list[Scene]=[
    Scene("Wrong picture","The subtle body is often pictured as a glowing person hidden inside the physical one.",9.0,"field",{}),
    Scene("Second corpse","That image creates a second corpse rather than explaining mediation.",8.0,"field",{}),
    Scene("Better question","The better question is: what problem is the subtle body solving?",8.0,"layers",{}),
    Scene("Intermediate route","It supplies an intermediate route between undivided capacity and local experience.",9.0,"layers",{}),
    Scene("Thesis","The subtle body is the route consciousness takes when it becomes local.",8.5,"final",{}),

    Scene("Not substance first","Begin with organization rather than substance.",7.0,"field",{}),
    Scene("Relations first","A body is not only what it is made from, but how its parts relate.",8.0,"field",{}),
    Scene("Subtle means mediating","Subtle means difficult to isolate because it mediates levels.",8.0,"layers",{}),
    Scene("Image breath sensation","Image, breath, sensation, memory, and intention form a layered continuity.",9.5,"layers",{}),
    Scene("No single layer","No single layer is the whole body.",7.0,"layers",{}),

    Scene("Synesius","Synesius gives the soul a pneumatic vehicle.",7.0,"synesius",{}),
    Scene("Phantasia medium","Phantasia needs a medium capable of carrying image between soul and flesh.",9.0,"synesius",{}),
    Scene("Dream vehicle","In dreams, this vehicle organizes a world while the physical senses quiet.",9.0,"dream",{}),
    Scene("Not detachable ghost","It is not simply a detachable ghost-body.",7.5,"synesius",{}),
    Scene("Mediating capacity","It is the mediating capacity by which the soul becomes image-bearing.",8.5,"synesius",{}),

    Scene("Ficino","Ficino names a related middle spiritus.",7.0,"ficino",{}),
    Scene("Body soul stars","Spiritus joins body, soul, imagination, sensation, and stars.",9.0,"ficino",{}),
    Scene("Atmosphere","It is an atmosphere of relation rather than a tiny organ.",7.5,"ficino",{}),
    Scene("Images affect body","Images can affect the body because both meet within spiritus.",8.5,"ficino",{}),
    Scene("Cosmos legible","The cosmos becomes bodily legible through a subtle medium.",8.0,"ficino",{}),

    Scene("Prana","Indian traditions speak of prāṇa.",6.0,"prana",{}),
    Scene("Not oxygen","Prāṇa is not simply oxygen.",6.0,"prana",{}),
    Scene("Movement before movement","It is movement before visible movement.",7.5,"prana",{}),
    Scene("Tension vector current","Stillness differentiates into tension, vector, current, breath, thought, and action.",9.5,"prana",{}),
    Scene("Breath one expression","Respiration is one expression of a broader organizing tendency.",8.0,"prana",{}),

    Scene("Nadis","Nāḍīs are usually drawn as luminous tubes.",7.0,"nadis",{}),
    Scene("Routing topology","A better image is routing topology.",6.5,"nadis",{}),
    Scene("Signals coupled","Sensations, breath, posture, attention, and imagery become coupled along recurrent paths.",9.0,"nadis",{}),
    Scene("Path strengthened","A path becomes strong because activity repeatedly travels through it.",8.0,"nadis",{}),
    Scene("Network not plumbing","The nāḍī system is closer to a dynamic network than plumbing.",8.5,"nadis",{}),

    Scene("Ida pingala","Iḍā and piṅgalā are not left-brain and right-brain channels.",8.0,"ida",{}),
    Scene("Complementary rhythms","They encode complementary rhythms.",7.0,"ida",{}),
    Scene("Cooling heating","Cooling and heating.",5.5,"ida",{}),
    Scene("Inward outward","Inward and outward.",5.5,"ida",{}),
    Scene("Lunar solar","Lunar and solar.",5.5,"ida",{}),
    Scene("Crossing generates experience","Their crossings generate alternating patterns of experience.",8.5,"ida",{}),
    Scene("Difference makes rhythm","Difference makes rhythm possible.",7.0,"ida",{}),

    Scene("Sushumna","Suṣumṇā is not merely a tube in the spine.",8.0,"sushumna",{}),
    Scene("Constraint collapse","It appears when competing constraints cease pulling in different directions.",9.0,"sushumna",{}),
    Scene("Trajectories align","Many trajectories align into one axis.",7.5,"sushumna",{}),
    Scene("Energy no longer leaks","Activity no longer leaks sideways into habitual conflict.",8.0,"sushumna",{}),
    Scene("Central path","The central channel is unified trajectory.",7.0,"sushumna",{}),

    Scene("Chakras","Chakras are not decorative lotus stickers.",7.0,"chakras",{}),
    Scene("Stable knots","They are stable knots of circulation.",6.5,"chakras",{}),
    Scene("Compression","Information is compressed.",5.5,"chakras",{}),
    Scene("Integration","Signals are integrated.",5.5,"chakras",{}),
    Scene("Redistribution","Activity is redistributed.",5.5,"chakras",{}),
    Scene("Lotus geometry","Lotus geometry expresses recurrent dynamic organization.",8.5,"chakras",{}),
    Scene("Petals as modes","Petals can be read as differentiated modes around one center.",8.0,"chakras",{}),

    Scene("Granthi","Granthi means knot.",5.5,"granthi",{}),
    Scene("Self-holding constraint","A granthi is a constraint that has become self-holding.",8.0,"granthi",{}),
    Scene("Body defends pattern","Breath, muscle, emotion, image, and belief defend the same pattern.",9.0,"granthi",{}),
    Scene("Not blockage object","The knot is not a foreign object lodged in a tube.",8.0,"granthi",{}),
    Scene("Circulation loosens","It loosens when circulation no longer needs the old organization.",8.5,"granthi",{}),

    Scene("Kundalini","Kuṇḍalinī is usually animated as a snake climbing upward.",8.0,"kundalini",{}),
    Scene("Potential","The serpent is better read as concentrated potential.",7.0,"kundalini",{}),
    Scene("Recursive activation","Activation becomes recursive.",6.5,"kundalini",{}),
    Scene("Local recruits global","Local change recruits larger networks.",7.5,"kundalini",{}),
    Scene("Synchronization","Separated systems synchronize.",6.5,"kundalini",{}),
    Scene("Phase transition","A phase transition becomes possible.",7.0,"kundalini",{}),
    Scene("Symbol serpent","The serpent appears as symbolic shorthand for folded power.",8.0,"kundalini",{}),

    Scene("Body of light","The body of light is often mistaken for a body made of photons.",8.0,"light",{}),
    Scene("Relational geometry","It is better understood as coherent relational geometry.",8.0,"light",{}),
    Scene("Material turnover","Material components may change while organization persists.",8.0,"light",{}),
    Scene("Identity lattice","Identity appears as a lattice of relations rather than one substance.",8.5,"light",{}),
    Scene("Light disclosure","Light names disclosure, intelligibility, and coherence—not necessarily radiation.",9.0,"light",{}),

    Scene("Tibetan winds","Tibetan completion-stage systems join channels and winds.",8.0,"winds",{}),
    Scene("Mind rides wind","Mind is said to ride the winds.",7.0,"winds",{}),
    Scene("Change wind mind","Change the organization of wind and cognition changes.",8.0,"winds",{}),
    Scene("Central channel practice","Practice draws winds toward the central channel.",8.0,"winds",{}),
    Scene("Conceptual construction loosens","Ordinary conceptual construction loosens.",8.0,"winds",{}),
    Scene("Clear light possible","Clear light becomes experientially available.",7.5,"clear",{}),

    Scene("Clear light","Clear light is not a giant white lamp.",7.0,"clear",{}),
    Scene("Structure releases","It names luminosity when ordinary structuring releases.",8.0,"clear",{}),
    Scene("Not unconscious blank","It is not unconscious blankness.",7.0,"clear",{}),
    Scene("Appearance before division","It is appearance before subject and object are fully divided.",9.0,"clear",{}),
    Scene("Structure can return","Structures can return without obscuring their source.",8.0,"clear",{}),

    Scene("Dream body","Dream provides a laboratory for subtle embodiment.",7.0,"dream",{}),
    Scene("Physical input loosens","Physical sensory input loosens.",7.0,"dream",{}),
    Scene("Location persists","Yet location, movement, agency, and form persist.",8.5,"dream",{}),
    Scene("Different constraints","The body reorganizes under different constraints.",8.0,"dream",{}),
    Scene("Same vehicle question","Dream body and subtle body may name overlapping problems of mediated embodiment.",9.0,"dream",{}),

    Scene("Ritual","Ritual rewrites the topology.",6.5,"ritual",{}),
    Scene("Mantra routes sound","Mantra routes sound and attention.",7.0,"ritual",{}),
    Scene("Mudra routes gesture","Mudrā routes gesture.",6.5,"ritual",{}),
    Scene("Nyasa routes identity","Nyāsa routes identity across the body.",7.0,"ritual",{}),
    Scene("Breath routes current","Breath routes current.",6.5,"ritual",{}),
    Scene("Image routes expectation","Image routes expectation.",6.5,"ritual",{}),
    Scene("Engineering metaphor","Ritual can be understood as subtle-body engineering without reducing it to mechanics.",9.0,"ritual",{}),

    Scene("Death","Death traditions ask which layers separate.",7.0,"death",{}),
    Scene("Gross body","Gross body ceases.",6.0,"death",{}),
    Scene("Breath withdraws","Breath withdraws.",6.0,"death",{}),
    Scene("Sensation dissolves","Sensation dissolves.",6.0,"death",{}),
    Scene("Imagery persists question","Imagery, tendency, or vehicle may be said to persist.",8.5,"death",{}),
    Scene("Traditions disagree","Traditions disagree about what survives and how.",8.0,"death",{}),
    Scene("Persistence layers","The subtle body is partly a theory of persistence layers.",8.0,"death",{}),

    Scene("Science comparison","Modern network science offers useful analogies.",7.0,"science",{}),
    Scene("Topology","Topology matters.",5.5,"science",{}),
    Scene("Bottlenecks","Bottlenecks matter.",5.5,"science",{}),
    Scene("Synchronization science","Synchronization matters.",5.5,"science",{}),
    Scene("Attractors","Attractors matter.",5.5,"science",{}),
    Scene("No proof subtle anatomy","None of this proves subtle anatomy.",8.0,"science",{}),
    Scene("Analogy discipline","Analogy clarifies function while preserving metaphysical difference.",9.0,"science",{}),

    Scene("Shaiva contraction","Kashmir Śaivism places the deepest problem in contraction.",8.0,"layers",{}),
    Scene("Universal becomes local","Universal consciousness becomes a finite center without ceasing to be universal.",9.0,"layers",{}),
    Scene("Subtle body route","The subtle body can be read as the route of that localization.",8.5,"field",{}),
    Scene("Channels contracted powers","Channels are contracted powers of relation.",8.0,"nadis",{}),
    Scene("Prana contracted activity","Prāṇa is contracted activity.",7.0,"prana",{}),
    Scene("Chakras contracted centers","Chakras are contracted centers of organization.",8.0,"chakras",{}),
    Scene("Recognition reverses contraction","Recognition reverses ignorance without destroying embodiment.",9.0,"recognition",{}),

    Scene("Recognition","The end is not escape into a brighter body.",7.0,"recognition",{}),
    Scene("No second self","It is not discovery of a second self hidden behind the first.",8.0,"recognition",{}),
    Scene("Pattern appearing","It is recognition that body, current, image, and world are patterns of appearing.",9.0,"recognition",{}),
    Scene("Body light already","The body of light was not elsewhere.",7.5,"recognition",{}),
    Scene("Another description","It was this body seen from another level of description.",9.0,"recognition",{}),

    Scene("Return","The subtle body must return to ordinary life.",7.0,"return",{}),
    Scene("Speech steadier","Speech becomes steadier.",6.0,"return",{}),
    Scene("Attention less scattered","Attention becomes less scattered.",6.5,"return",{}),
    Scene("Action less divided","Action becomes less divided.",6.5,"return",{}),
    Scene("Body more inhabited","The physical body becomes more inhabited, not less.",8.0,"return",{}),
    Scene("Fruit","The fruit is integration.",6.0,"return",{}),

    Scene("Final field","At first there is undifferentiated capacity.",7.0,"field",{}),
    Scene("Lattice forms","A lattice forms.",5.5,"field",{}),
    Scene("Current moves","Current moves through it.",5.5,"prana",{}),
    Scene("Routes stabilize","Routes stabilize.",5.5,"nadis",{}),
    Scene("Knots integrate","Knots integrate.",5.5,"chakras",{}),
    Scene("Axis aligns","An axis aligns.",5.5,"sushumna",{}),
    Scene("Phase changes","Potential becomes phase change.",6.0,"kundalini",{}),
    Scene("Light body","The body becomes coherent light.",6.5,"light",{}),
    Scene("Recognition final","And light recognizes itself as this embodied world.",8.0,"final",{}),
    Scene("Final thesis","The subtle body is the route consciousness takes when it becomes local.",9.0,"final",{}),
]

def export_original_essay():
    lines=["# the subtle body is the route consciousness takes when it becomes local",""]
    for s in SCENES: lines += [s.narration,""]
    p=OUTPUT/"original_essay.md"
    p.write_text("\n".join(lines),encoding="utf-8")
    return p

def render_frame(scene,fi,fc,w,h,seed):
    u=fi/max(1,fc-1); t=u*scene.duration
    dark=scene.visual in {"ficino","clear","death"}
    im=bg(w,h,seed,dark)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im,dark)
    return im.convert("RGB")

def ffmpeg():
    x=shutil.which("ffmpeg")
    if not x: raise RuntimeError("ffmpeg is required but was not found on PATH")
    return x

def encode(i,fps):
    fd=FRAMES/f"scene_{i:03d}"; out=SCENES_DIR/f"scene_{i:03d}.mp4"
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
    out=OUTPUT/"the_subtle_body_is_the_route_consciousness_takes_when_it_becomes_local.mp4"
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
        "title":"the subtle body is the route consciousness takes when it becomes local",
        "runtime_seconds":round(cur,3),
        "scene_count":len(SCENES),
        "original_essay":True,
        "style":{
            "continuity_object":"luminous lattice differentiating into channels, knots, axis, and body of light",
            "shot_duration_range_seconds":[5,10],
            "palette_roles":{
                "white":"undifferentiated awareness",
                "silver":"subtle vehicle",
                "cyan":"prana, pneuma, wind",
                "gold":"central integration and recognition",
                "violet":"imaginal depth and dream body",
                "crimson":"contraction and obstruction",
                "green":"integration and embodied return"
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
