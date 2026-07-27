from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import textwrap
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FPS = 2
ROOT = Path('/mnt/data/tantra_animation_packs/selected_expansion_essays')

DEV_FONT = '/root/projects/blog/visionary-renderer/assets/fonts/NotoSerifDevanagari-Regular.ttf'
LAT_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
LAT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
LAT_SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
LAT_SERIF_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'

FONT = {
    'dev_xl': ImageFont.truetype(DEV_FONT, 78),
    'dev_l': ImageFont.truetype(DEV_FONT, 52),
    'dev_m': ImageFont.truetype(DEV_FONT, 34),
    'xl': ImageFont.truetype(LAT_BOLD, 54),
    'l': ImageFont.truetype(LAT_BOLD, 38),
    'm': ImageFont.truetype(LAT_FONT, 28),
    's': ImageFont.truetype(LAT_FONT, 22),
    'xs': ImageFont.truetype(LAT_FONT, 17),
    'serif_l': ImageFont.truetype(LAT_SERIF_BOLD, 39),
    'serif_m': ImageFont.truetype(LAT_SERIF, 27),
    'serif_s': ImageFont.truetype(LAT_SERIF, 21),
}

INK = (235, 231, 220)
MUTED = (145, 141, 132)
GOLD = (208, 172, 91)
CRIMSON = (141, 44, 57)
BLUE = (69, 94, 124)
GREEN = (78, 112, 96)
DARK = (12, 12, 15)
DARK_BLUE = (12, 17, 25)
WHITE = (248, 246, 240)
PARCHMENT = (241, 235, 219)
BLACK = (19, 19, 21)


def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return max(a, min(b, x))


def smoothstep(a: float, b: float, x: float) -> float:
    if b == a:
        return 1.0 if x >= b else 0.0
    u = clamp((x-a)/(b-a))
    return u*u*(3-2*u)


def lerp(a: float, b: float, u: float) -> float:
    return a + (b-a)*u


def rgba(c, a=1.0):
    return (c[0], c[1], c[2], int(255*clamp(a)))


def canvas(bg=DARK):
    return Image.new('RGBA', (W,H), (*bg,255))


def text_size(d, text, font):
    b=d.textbbox((0,0), text, font=font)
    return b[2]-b[0], b[3]-b[1]


def wrap_text(d, text, font, max_width):
    out=[]
    for para in text.split('\n'):
        words=para.split()
        if not words:
            out.append(''); continue
        line=words[0]
        for word in words[1:]:
            test=line+' '+word
            if text_size(d,test,font)[0] <= max_width:
                line=test
            else:
                out.append(line); line=word
        out.append(line)
    return out


def centered(d, text, y, font, color=INK, alpha=1.0, max_width=None, gap=8):
    lines=[text] if max_width is None else wrap_text(d,text,font,max_width)
    yy=y
    for line in lines:
        w,h=text_size(d,line,font)
        d.text(((W-w)/2,yy),line,font=font,fill=rgba(color,alpha))
        yy += h+gap
    return yy


def left(d, text, x, y, font, color=INK, alpha=1.0, max_width=None, gap=8):
    lines=[text] if max_width is None else wrap_text(d,text,font,max_width)
    yy=y
    for line in lines:
        _,h=text_size(d,line,font)
        d.text((x,yy),line,font=font,fill=rgba(color,alpha))
        yy += h+gap
    return yy


def dot(d,x,y,r,color=GOLD,alpha=1):
    d.ellipse((x-r,y-r,x+r,y+r),fill=rgba(color,alpha))


def ring(d,x,y,r,color=GOLD,alpha=1,width=2):
    d.ellipse((x-r,y-r,x+r,y+r),outline=rgba(color,alpha),width=width)


def arrow(d,p1,p2,color=GOLD,alpha=1,width=2):
    x1,y1=p1; x2,y2=p2
    d.line((x1,y1,x2,y2),fill=rgba(color,alpha),width=width)
    a=math.atan2(y2-y1,x2-x1); s=10
    d.polygon([(x2,y2),(x2+s*math.cos(a+2.55),y2+s*math.sin(a+2.55)),(x2+s*math.cos(a-2.55),y2+s*math.sin(a-2.55))],fill=rgba(color,alpha))


def label(d,idx,title,dark=True):
    c=MUTED if dark else (105,102,96)
    d.text((42,26),f'{idx:02d}',font=FONT['xs'],fill=rgba(c,.85))
    d.text((84,26),title.upper(),font=FONT['xs'],fill=rgba(c,.85))


def flower(d,cx,cy,r,petals,color=GOLD,alpha=1,rotation=0):
    pts=[]
    for i in range(petals*2):
        a=rotation+i*math.pi/petals
        rr=r if i%2==0 else r*.46
        pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d.line(pts+[pts[0]],fill=rgba(color,alpha),width=2)
    dot(d,cx,cy,4,color,alpha)


def silhouette(d,cx,cy,s=1,color=INK,alpha=1):
    hr=25*s
    d.ellipse((cx-hr,cy-110*s-hr,cx+hr,cy-110*s+hr),outline=rgba(color,alpha),width=max(1,int(3*s)))
    d.rounded_rectangle((cx-50*s,cy-75*s,cx+50*s,cy+95*s),radius=int(24*s),outline=rgba(color,alpha),width=max(1,int(3*s)))
    d.line((cx-45*s,cy-15*s,cx-92*s,cy+60*s),fill=rgba(color,alpha),width=max(1,int(3*s)))
    d.line((cx+45*s,cy-15*s,cx+92*s,cy+60*s),fill=rgba(color,alpha),width=max(1,int(3*s)))
    d.line((cx-22*s,cy+95*s,cx-48*s,cy+190*s),fill=rgba(color,alpha),width=max(1,int(3*s)))
    d.line((cx+22*s,cy+95*s,cx+48*s,cy+190*s),fill=rgba(color,alpha),width=max(1,int(3*s)))


def wavy_line(d,x0,x1,y,amp,phase,color,alpha,width=2,cycles=3):
    pts=[]
    for i in range(180):
        u=i/179
        x=lerp(x0,x1,u)
        yy=y+amp*math.sin(u*math.tau*cycles+phase)
        pts.append((x,yy))
    d.line(pts,fill=rgba(color,alpha),width=width)


def regular_polygon(d,cx,cy,r,n,color=GOLD,alpha=1,width=2,rot=-math.pi/2):
    pts=[(cx+r*math.cos(rot+i*math.tau/n),cy+r*math.sin(rot+i*math.tau/n)) for i in range(n)]
    d.line(pts+[pts[0]],fill=rgba(color,alpha),width=width)
    return pts


@dataclass
class Scene:
    title: str
    duration: float
    fn: Callable[[float,float,int], Image.Image]
    note: str


class Film:
    def __init__(self,key,title,scenes):
        self.key=key; self.title=title; self.scenes=scenes
    @property
    def duration(self): return sum(s.duration for s in self.scenes)
    def manifest(self):
        t=0; rows=[]
        for i,s in enumerate(self.scenes,1):
            rows.append({'index':i,'title':s.title,'start':round(t,2),'end':round(t+s.duration,2),'duration':s.duration,'note':s.note})
            t+=s.duration
        return {'key':self.key,'title':self.title,'resolution':[W,H],'fps':FPS,'duration_seconds':self.duration,'scenes':rows}
    def render(self,out):
        out.parent.mkdir(parents=True,exist_ok=True)
        temp=out.with_suffix('.temp.mp4')
        writer=cv2.VideoWriter(str(temp),cv2.VideoWriter_fourcc(*'mp4v'),FPS,(W,H))
        if not writer.isOpened(): raise RuntimeError('VideoWriter failed')
        try:
            for si,s in enumerate(self.scenes,1):
                frames=max(1,int(s.duration*FPS))
                for fi in range(frames):
                    t=fi/FPS; u=fi/max(1,frames-1)
                    arr=np.array(s.fn(t,u,si).convert('RGB'))[:,:,::-1]
                    writer.write(arr)
                print(f'{self.key}: {si:02d}/{len(self.scenes)} {s.title}',flush=True)
        finally:
            writer.release()
        cmd=f"ffmpeg -y -loglevel error -i '{temp}' -c:v libx264 -pix_fmt yuv420p -preset veryfast -crf 22 -movflags +faststart '{out}'"
        if os.system(cmd)!=0: temp.replace(out)
        else: temp.unlink(missing_ok=True)


# ---------------- RASA ----------------
def rasa_1(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Pain is juice')
    centered(d,'PAIN IS JUICE',95,FONT['xl'],INK,smoothstep(.04,.2,u))
    centered(d,'रस',175,FONT['dev_xl'],GOLD,smoothstep(.14,.3,u))
    cx,cy=W/2,405
    for k in range(6): ring(d,cx,cy,55+k*38+4*math.sin(t*.45+k),CRIMSON if k%2 else GOLD,smoothstep(.18+k*.04,.55+k*.03,u)*(.22-k*.02),1)
    dot(d,cx,cy,7+1.3*math.sin(t*.8),INK,1)
    centered(d,'the taste that remains when feeling is fully felt',610,FONT['s'],INK,smoothstep(.58,.8,u))
    return im

def rasa_2(t,u,i):
    im=canvas(WHITE); d=ImageDraw.Draw(im); label(d,i,'Nine flavors',False)
    emotions=[('grief',-90),('terror',-50),('disgust',-10),('wrath',30),('wonder',70),('laughter',110),('courage',150),('tenderness',190),('peace',230)]
    cx,cy=W/2,360
    for j,(name,deg) in enumerate(emotions):
        a=smoothstep(.04+j*.055,.16+j*.055,u); ang=math.radians(deg); x=cx+250*math.cos(ang); y=cy+220*math.sin(ang)
        d.line((cx,cy,x,y),fill=rgba(MUTED,a*.42),width=1); flower(d,x,y,29,5,CRIMSON if j<4 else GOLD,a,t*.08+j)
        w,_=text_size(d,name,FONT['xs']); d.text((x-w/2,y+40),name,font=FONT['xs'],fill=rgba(BLACK,a))
    dot(d,cx,cy,6,BLACK,1); centered(d,'nine rasas · nine ways consciousness tastes itself',635,FONT['s'],BLACK,smoothstep(.67,.86,u))
    return im

def rasa_3(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Fist to cup')
    # fist: closed nested arcs, opens into cup
    open_u=smoothstep(.35,.82,u); cx,cy=W/2,365
    for k in range(5):
        r=58+k*28; start=lerp(200,25,open_u); end=lerp(340,155,open_u)
        d.arc((cx-r,cy-r,cx+r,cy+r),start=start,end=end,fill=rgba(GOLD,.9-k*.12),width=4)
    centered(d,'The grief does not change.',120,FONT['m'],INK,smoothstep(.05,.25,u))
    centered(d,'You change.',170,FONT['l'],GOLD,smoothstep(.22,.4,u))
    centered(d,'from clenched to open · from fist to cup',600,FONT['s'],INK,smoothstep(.68,.86,u))
    return im

def rasa_4(t,u,i):
    im=canvas(PARCHMENT); d=ImageDraw.Draw(im); label(d,i,'Tasting, not consuming',False)
    cx,cy=390,390
    # cup
    d.arc((cx-110,cy-100,cx+110,cy+120),start=0,end=180,fill=rgba(BLACK,smoothstep(.08,.28,u)),width=4)
    d.line((cx-110,cy+10,cx-75,cy+150),fill=rgba(BLACK,.9),width=4); d.line((cx+110,cy+10,cx+75,cy+150),fill=rgba(BLACK,.9),width=4)
    d.arc((cx-75,cy+120,cx+75,cy+175),start=0,end=180,fill=rgba(BLACK,.9),width=4)
    for k in range(4): wavy_line(d,cx-85,cx+85,cy+15+k*17,5,t*.5+k,GOLD,smoothstep(.25+k*.05,.5+k*.05,u),2,2)
    left(d,'TASTING',700,240,FONT['l'],BLACK,smoothstep(.22,.4,u)); left(d,'is awareness resting',700,315,FONT['m'],MUTED,smoothstep(.36,.55,u)); left(d,'on experience itself.',700,365,FONT['m'],MUTED,smoothstep(.45,.62,u))
    centered(d,'the emotion is the wine · the witness is the tasting',620,FONT['s'],BLACK,smoothstep(.7,.86,u))
    return im

def rasa_5(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Wonder makes worlds')
    cx,cy=W/2,360
    for k in range(11):
        a=smoothstep(.04+k*.045,.2+k*.045,u); ang=k*2.399+t*.05; r=35+k*24
        x=cx+r*math.cos(ang); y=cy+r*math.sin(ang); dot(d,x,y,4+(k%3),GOLD if k%2 else CRIMSON,a)
        if k: d.line((cx,cy,x,y),fill=rgba(MUTED,a*.25),width=1)
    centered(d,'camatkāra',105,FONT['serif_l'],GOLD,smoothstep(.08,.28,u))
    centered(d,'wonder is not a reaction to the world',565,FONT['m'],INK,smoothstep(.55,.72,u))
    centered(d,'it is one way the world comes into being',610,FONT['s'],MUTED,smoothstep(.68,.86,u))
    return im

def rasa_6(t,u,i):
    im=canvas(WHITE); d=ImageDraw.Draw(im); label(d,i,'The witness',False)
    silhouette(d,W/2,370,.9,BLACK,smoothstep(.05,.22,u))
    # wave passes through without moving center
    for k in range(5): wavy_line(d,120,1160,330+k*25,18,t*.65+k,CRIMSON if k<2 else GOLD,smoothstep(.12+k*.08,.4+k*.08,u)*.75,2,2)
    ring(d,W/2,365,155+5*math.sin(t*.35),BLACK,smoothstep(.5,.7,u),2)
    centered(d,'There is sadness.',100,FONT['l'],BLACK,smoothstep(.08,.28,u))
    centered(d,'The witness is made of something grief cannot touch.',625,FONT['s'],BLACK,smoothstep(.65,.84,u))
    return im

def rasa_7(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Crest, crash, dissolve')
    for k in range(7):
        yy=180+k*62; amp=lerp(12,55,smoothstep(.12,.55,u))*(1-k*.08); wavy_line(d,80,1200,yy,amp,t*.75+k*.6,GOLD if k%2 else CRIMSON,1-k*.09,2,2)
    centered(d,'RIDE IT',80,FONT['xl'],INK,smoothstep(.05,.2,u))
    centered(d,'let it crest · let it crash · let it dissolve',620,FONT['m'],INK,smoothstep(.62,.82,u))
    return im

def rasa_8(t,u,i):
    bg=tuple(int(lerp(DARK[j],WHITE[j],smoothstep(.62,1,u))) for j in range(3)); im=canvas(bg); d=ImageDraw.Draw(im); label(d,i,'Rest in the feeling')
    cx,cy=W/2,350
    for k in range(9):
        a=1-smoothstep(.55,.95,u); flower(d,cx,cy,50+k*23,9,GOLD,a*(.34-k*.025),t*.03+k*.1)
    if u<.72: centered(d,'REST IN THE FEELING',135,FONT['l'],INK,smoothstep(.05,.26,u))
    if u>.66: centered(d,'रस',280,FONT['dev_xl'],BLACK,smoothstep(.72,.94,u))
    return im

RASA=[Scene('Pain is juice',30,rasa_1,'Title and central rasa field.'),Scene('Nine flavors',34,rasa_2,'Radial map of nine aesthetic flavors.'),Scene('Fist to cup',30,rasa_3,'Contraction opens without erasing grief.'),Scene('Tasting, not consuming',32,rasa_4,'Cup and wine metaphor.'),Scene('Wonder makes worlds',32,rasa_5,'Camatkāra as generative wonder.'),Scene('The witness',34,rasa_6,'Emotion passes through stable awareness.'),Scene('Crest, crash, dissolve',30,rasa_7,'Wave dynamics.'),Scene('Rest in the feeling',28,rasa_8,'Resolution into white.')]


# ---------------- IMAGINAL ----------------
def imag_1(t,u,i):
    im=canvas(DARK_BLUE); d=ImageDraw.Draw(im); label(d,i,'The world between worlds')
    centered(d,'THE WORLD BETWEEN WORLDS',85,FONT['xl'],INK,smoothstep(.04,.2,u))
    # three planes
    ys=[525,360,195]; names=['matter','imaginal','spirit']; cols=[MUTED,GOLD,INK]
    for j,(y,n,c) in enumerate(zip(ys,names,cols)):
        a=smoothstep(.15+j*.12,.32+j*.12,u); d.line((180,y,1100,y),fill=rgba(c,a),width=2); centered(d,n,y-35,FONT['s'],c,a)
    for k in range(7): dot(d,640,lerp(510,210,k/6)+8*math.sin(t*.35+k),4,GOLD,smoothstep(.48+k*.025,.75+k*.02,u))
    centered(d,'neither physical nor disembodied',620,FONT['s'],INK,smoothstep(.65,.83,u))
    return im

def imag_2(t,u,i):
    im=canvas(WHITE); d=ImageDraw.Draw(im); label(d,i,'An organ of perception',False)
    # eye becoming doorway
    cx,cy=390,350; a=smoothstep(.05,.28,u)
    d.arc((cx-170,cy-80,cx+170,cy+80),start=200,end=340,fill=rgba(BLACK,a),width=4); d.arc((cx-170,cy-80,cx+170,cy+80),start=20,end=160,fill=rgba(BLACK,a),width=4); ring(d,cx,cy,40,GOLD,a,3); dot(d,cx,cy,7,BLACK,a)
    # door
    du=smoothstep(.35,.78,u); d.rounded_rectangle((760,185,1010,555),radius=130,outline=rgba(GOLD,du),width=4)
    for k in range(7): ring(d,885,370,35+k*27,GOLD,du*(.42-k*.045),1)
    arrow(d,(560,350),(735,350),CRIMSON,du,3)
    centered(d,'active imagination is perception',90,FONT['l'],BLACK,smoothstep(.05,.25,u)); centered(d,'not make-believe',620,FONT['m'],CRIMSON,smoothstep(.68,.84,u))
    return im

def imag_3(t,u,i):
    im=canvas(DARK_BLUE); d=ImageDraw.Draw(im); label(d,i,'The suprasensory north')
    cx,cy=W/2,370
    for r in [70,150,235]: ring(d,cx,cy,r,INK,.25,1)
    # compass and north light
    ang=lerp(math.pi*.4,-math.pi/2,smoothstep(.18,.7,u)); arrow(d,(cx,cy),(cx+210*math.cos(ang),cy+210*math.sin(ang)),GOLD,smoothstep(.12,.35,u),4)
    dot(d,cx,cy-235,7,GOLD,smoothstep(.3,.55,u)); centered(d,'NORTH',75,FONT['s'],GOLD,smoothstep(.35,.56,u))
    centered(d,'the direction of origin',600,FONT['m'],INK,smoothstep(.62,.82,u)); centered(d,'where spirit takes form and form becomes luminous',640,FONT['s'],MUTED,smoothstep(.72,.88,u))
    return im

def imag_4(t,u,i):
    im=canvas(WHITE); d=ImageDraw.Draw(im); label(d,i,'One times one',False)
    centered(d,'1 × 1',130,FONT['xl'],BLACK,smoothstep(.05,.22,u))
    # two circles overlap but remain distinct
    sep=lerp(260,105,smoothstep(.18,.75,u)); cx=W/2
    ring(d,cx-sep/2,380,145,GOLD,.9,3); ring(d,cx+sep/2,380,145,CRIMSON,.9,3)
    # spider thread cut and rejoined
    d.line((180,575,560,575),fill=rgba(BLACK,.7),width=2); d.line((720,575,1100,575),fill=rgba(BLACK,.7),width=2)
    join=smoothstep(.5,.85,u); d.line((560,575,lerp(560,720,join),575),fill=rgba(GOLD,join),width=3)
    centered(d,'union without erasing difference',625,FONT['s'],BLACK,smoothstep(.64,.83,u))
    return im

def imag_5(t,u,i):
    im=canvas(DARK_BLUE); d=ImageDraw.Draw(im); label(d,i,'The person of light')
    silhouette(d,410,380,.9,INK,smoothstep(.04,.22,u)); silhouette(d,870,380,.9,GOLD,smoothstep(.25,.5,u))
    for k in range(7): ring(d,870,370,55+k*33+5*math.sin(t*.4+k),GOLD,smoothstep(.32+k*.04,.68+k*.03,u)*(.34-k*.035),1)
    arrow(d,(535,365),(730,365),CRIMSON,smoothstep(.55,.75,u),2)
    centered(d,'another face appears',90,FONT['m'],INK,smoothstep(.1,.28,u)); centered(d,'your own face before birth',610,FONT['l'],GOLD,smoothstep(.64,.84,u))
    return im

def imag_6(t,u,i):
    im=canvas(WHITE); d=ImageDraw.Draw(im); label(d,i,'Light upon light',False)
    cx,cy=W/2,400
    # dhikr fire upward
    for k in range(13):
        a=smoothstep(.04+k*.035,.2+k*.035,u); y=560-k*28; x=cx+50*math.sin(t*.6+k*.8)*(1-k/18)
        d.arc((x-35,y-65,x+35,y+30),start=200,end=340,fill=rgba(CRIMSON if k<6 else GOLD,a),width=3)
    for k in range(6): ring(d,cx,200,45+k*35,GOLD,smoothstep(.48+k*.04,.72+k*.03,u)*(.38-k*.045),2)
    centered(d,'LIGHT UPON LIGHT',85,FONT['l'],BLACK,smoothstep(.1,.28,u)); centered(d,'repetition becomes ascent',630,FONT['s'],BLACK,smoothstep(.65,.83,u))
    return im

def imag_7(t,u,i):
    im=canvas(DARK_BLUE); d=ImageDraw.Draw(im); label(d,i,'Parent and child')
    # recursive circles
    cx,cy=W/2,360
    for k in range(8):
        a=smoothstep(.04+k*.05,.24+k*.05,u); r=230-k*25; ring(d,cx,cy,r,GOLD if k%2 else CRIMSON,a*(.65-k*.045),2)
        dot(d,cx+r*.55*math.cos(t*.15+k),cy+r*.55*math.sin(t*.15+k),4,INK,a)
    centered(d,'the Guide gives birth to you',100,FONT['m'],INK,smoothstep(.08,.26,u)); centered(d,'you give birth to the Guide',590,FONT['m'],GOLD,smoothstep(.58,.76,u)); centered(d,'a relationship that creates both partners',635,FONT['s'],MUTED,smoothstep(.7,.86,u))
    return im

def imag_8(t,u,i):
    bg=tuple(int(lerp(DARK_BLUE[j],WHITE[j],smoothstep(.65,1,u))) for j in range(3)); im=canvas(bg); d=ImageDraw.Draw(im); label(d,i,'The open door')
    a=1-smoothstep(.55,.9,u); d.rounded_rectangle((415,90,865,650),radius=220,outline=rgba(GOLD,a),width=4)
    for k in range(8): ring(d,640,370,45+k*38,GOLD,a*(.35-k*.035),1)
    if u<.7: centered(d,'THE DOOR IS ALWAYS OPEN',120,FONT['l'],INK,smoothstep(.05,.25,u))
    if u>.7: centered(d,'mundus imaginalis',315,FONT['serif_l'],BLACK,smoothstep(.74,.94,u))
    return im

IMAG=[Scene('The world between worlds',32,imag_1,'Three ontological planes.'),Scene('An organ of perception',34,imag_2,'Eye becomes doorway.'),Scene('The suprasensory north',32,imag_3,'Imaginal geography and orientation.'),Scene('One times one',30,imag_4,'Relational unity without collapse.'),Scene('The person of light',35,imag_5,'Encounter with luminous counterpart.'),Scene('Light upon light',32,imag_6,'Dhikr as fire and ascent.'),Scene('Parent and child',32,imag_7,'Recursive angelic relation.'),Scene('The open door',28,imag_8,'Close physical eyes, open the other ones.')]


# ---------------- ALCHEMY ----------------
def alc_1(t,u,i):
    im=canvas(PARCHMENT); d=ImageDraw.Draw(im); label(d,i,'The secret life of matter',False)
    centered(d,'THE SECRET LIFE OF MATTER',85,FONT['serif_l'],BLACK,smoothstep(.04,.2,u))
    cx,cy=W/2,385
    # flask
    d.line((cx-45,140,cx-45,280),fill=rgba(BLACK,.9),width=4); d.line((cx+45,140,cx+45,280),fill=rgba(BLACK,.9),width=4)
    d.arc((cx-185,250,cx+185,610),start=0,end=180,fill=rgba(BLACK,.9),width=4)
    for k in range(6): wavy_line(d,cx-145,cx+145,430+k*20,8,t*.55+k,GOLD,smoothstep(.16+k*.06,.45+k*.06,u),2,2)
    for k in range(5): d.arc((cx-65-k*18,310-k*25,cx+65+k*18,470-k*10),start=200,end=340,fill=rgba(CRIMSON,smoothstep(.3+k*.05,.55+k*.04,u)),width=3)
    centered(d,'matter becoming light',630,FONT['m'],BLACK,smoothstep(.65,.83,u))
    return im

def alc_2(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'As above, so below')
    centered(d,'AS ABOVE',90,FONT['l'],GOLD,smoothstep(.04,.2,u)); centered(d,'SO BELOW',580,FONT['l'],CRIMSON,smoothstep(.2,.38,u))
    cx=W/2
    # mirrored geometries
    top=regular_polygon(d,cx,270,120,6,GOLD,smoothstep(.12,.35,u),3,t*.04)
    bot=regular_polygon(d,cx,450,120,6,CRIMSON,smoothstep(.32,.55,u),3,-t*.04+math.pi)
    for a,b in zip(top,bot): d.line((a[0],a[1],b[0],b[1]),fill=rgba(MUTED,smoothstep(.52,.75,u)*.35),width=1)
    centered(d,'one operation · two mirrors',640,FONT['s'],INK,smoothstep(.7,.86,u))
    return im

def alc_3(t,u,i):
    im=canvas(PARCHMENT); d=ImageDraw.Draw(im); label(d,i,'Separate the subtle from the gross',False)
    cx,cy=W/2,350
    # dark block dissolves upward into dots
    block_a=1-smoothstep(.35,.8,u); d.rectangle((320,390,960,540),outline=rgba(BLACK,block_a),width=4)
    for k in range(36):
        a=smoothstep(.15+k*.012,.35+k*.012,u); x=360+(k%9)*70; y=480-(k//9)*55-lerp(0,170,smoothstep(.35,.9,u)); dot(d,x,y,4+(k%3),GOLD,a)
    arrow(d,(640,520),(640,155),CRIMSON,smoothstep(.18,.45,u),3)
    centered(d,'SEPARATE',85,FONT['l'],BLACK,smoothstep(.05,.22,u)); centered(d,'the subtle from the gross',620,FONT['m'],BLACK,smoothstep(.65,.84,u))
    return im

def alc_4(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Body, soul, spirit')
    cx,cy=W/2,370
    cols=[CRIMSON,GOLD,INK]; names=['BODY','SOUL','SPIRIT']; rs=[210,145,80]
    for j,(r,c,n) in enumerate(zip(rs,cols,names)):
        a=smoothstep(.08+j*.16,.3+j*.16,u); ring(d,cx,cy,r,c,a,3); d.text((cx+r+28,cy-12),n,font=FONT['s'],fill=rgba(c,a))
    centered(d,'THREE IN ONE',90,FONT['l'],INK,smoothstep(.05,.22,u)); centered(d,'not stacked · inseparable',625,FONT['s'],MUTED,smoothstep(.68,.85,u))
    return im

def alc_5(t,u,i):
    im=canvas(PARCHMENT); d=ImageDraw.Draw(im); label(d,i,'The six chambers',False)
    names=['clear','coil','rise','melt','cast','remember']
    for j,n in enumerate(names):
        x=90+j*195; a=smoothstep(.04+j*.1,.19+j*.1,u)
        d.rounded_rectangle((x,210,x+150,520),radius=18,outline=rgba(CRIMSON if j in [0,3] else GOLD,a),width=3)
        centered_x=x+75; w,_=text_size(d,n,FONT['xs']); d.text((centered_x-w/2,550),n,font=FONT['xs'],fill=rgba(BLACK,a))
        # unique glyph
        if j==0: d.line((x+30,440,x+120,290),fill=rgba(BLACK,a),width=3)
        elif j==1:
            for r in [30,48,66]: d.arc((x+75-r,365-r,x+75+r,365+r),start=20,end=300,fill=rgba(BLACK,a),width=2)
        elif j==2: arrow(d,(x+75,455),(x+75,280),GOLD,a,3)
        elif j==3:
            for k in range(4): d.arc((x+25+k*25,350,x+75+k*20,480),start=190,end=345,fill=rgba(CRIMSON,a),width=3)
        elif j==4:
            for k in range(8): dot(d,x+30+(k%4)*30,320+(k//4)*70,5,GOLD,a)
        else:
            for k in range(5): d.line((x+25,285+k*40,x+125,285+k*40),fill=rgba(BLACK,a),width=2)
    centered(d,'knowledge is transformed chamber by chamber',100,FONT['m'],BLACK,smoothstep(.05,.25,u))
    return im

def alc_6(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Solve et coagula')
    cx,cy=W/2,370; split=smoothstep(.08,.42,u); join=smoothstep(.5,.88,u)
    # dissolve solid square into particles then reform circle
    d.rectangle((cx-120,cy-120,cx+120,cy+120),outline=rgba(CRIMSON,1-split),width=4)
    for k in range(50):
        ang=(k*2.399); r=lerp(40,260,split)*(0.35+(k%7)/7); x=cx+r*math.cos(ang+t*.03); y=cy+r*math.sin(ang+t*.03); dot(d,x,y,3,GOLD,split*(1-join*.5))
    ring(d,cx,cy,lerp(250,120,join),GOLD,join,4)
    centered(d,'SOLVE',90,FONT['l'],CRIMSON,smoothstep(.05,.2,u)); centered(d,'ET COAGULA',575,FONT['l'],GOLD,smoothstep(.54,.72,u)); centered(d,'make water of earth · earth of water',640,FONT['s'],INK,smoothstep(.7,.86,u))
    return im

def alc_7(t,u,i):
    im=canvas(PARCHMENT); d=ImageDraw.Draw(im); label(d,i,'The supercelestial marriage',False)
    cx,cy=W/2,370; sep=lerp(260,70,smoothstep(.15,.7,u))
    ring(d,cx-sep/2,cy,150,CRIMSON,.9,4); ring(d,cx+sep/2,cy,150,GOLD,.9,4)
    if u>.55: flower(d,cx,cy,90,8,BLACK,smoothstep(.55,.82,u),t*.04)
    centered(d,'SOUL',230,FONT['m'],CRIMSON,smoothstep(.05,.22,u)); centered(d,'BODY',970,FONT['m'],GOLD,smoothstep(.05,.22,u)); centered(d,'not escape · marriage',625,FONT['m'],BLACK,smoothstep(.68,.85,u))
    return im

def alc_8(t,u,i):
    bg=tuple(int(lerp(DARK[j],PARCHMENT[j],smoothstep(.65,1,u))) for j in range(3)); im=canvas(bg); d=ImageDraw.Draw(im); label(d,i,'The hidden stone')
    cx,cy=W/2,370; a=1-smoothstep(.55,.9,u)
    regular_polygon(d,cx,cy,190,8,GOLD,a,3,t*.03); ring(d,cx,cy,105,CRIMSON,a,3); dot(d,cx,cy,12,INK,a)
    if u<.72: centered(d,'YOU ARE THE FURNACE',110,FONT['l'],INK,smoothstep(.05,.25,u)); centered(d,'the fire is already lit',610,FONT['m'],INK,smoothstep(.55,.72,u))
    if u>.7: centered(d,'LAPIS',310,FONT['serif_l'],BLACK,smoothstep(.74,.94,u))
    return im

ALC=[Scene('The secret life of matter',34,alc_1,'Laboratory as mirror of soul.'),Scene('As above, so below',31,alc_2,'Mirrored operation.'),Scene('Separate subtle and gross',32,alc_3,'Matter dissolves upward.'),Scene('Body, soul, spirit',30,alc_4,'Triune Mercury.'),Scene('The six chambers',36,alc_5,'Blakean transformation sequence.'),Scene('Solve et coagula',32,alc_6,'Dissolve and reform.'),Scene('The supercelestial marriage',32,alc_7,'Reconciliation rather than escape.'),Scene('The hidden stone',28,alc_8,'Worker becomes the work.')]


# ---------------- EMPTINESS ----------------
def emp_1(t,u,i):
    im=canvas(WHITE); d=ImageDraw.Draw(im); label(d,i,'Everything is empty',False)
    centered(d,'EVERYTHING IS EMPTY',95,FONT['xl'],BLACK,smoothstep(.04,.2,u))
    # cup defined by absence
    cx,cy=W/2,380; a=smoothstep(.15,.38,u)
    d.arc((cx-170,cy-145,cx+170,cy+155),start=0,end=180,fill=rgba(BLACK,a),width=4); d.line((cx-170,cy,cx-115,cy+175),fill=rgba(BLACK,a),width=4); d.line((cx+170,cy,cx+115,cy+175),fill=rgba(BLACK,a),width=4); d.arc((cx-115,cy+140,cx+115,cy+205),start=0,end=180,fill=rgba(BLACK,a),width=4)
    centered(d,'capacity, not absence',620,FONT['m'],CRIMSON,smoothstep(.62,.82,u))
    return im

def emp_2(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Dependent arising')
    centered(d,'Whatever arises dependently is empty.',80,FONT['serif_l'],INK,smoothstep(.04,.22,u),1080)
    nodes=[(270,260),(500,180),(760,180),(1010,300),(850,520),(560,560),(300,470)]
    for j,(x,y) in enumerate(nodes):
        a=smoothstep(.15+j*.06,.3+j*.06,u); ring(d,x,y,28,GOLD if j%2 else CRIMSON,a,2); dot(d,x,y,4,INK,a)
        if j: d.line((nodes[j-1][0],nodes[j-1][1],x,y),fill=rgba(MUTED,a*.5),width=2)
    if u>.55: d.line((nodes[-1][0],nodes[-1][1],nodes[0][0],nodes[0][1]),fill=rgba(MUTED,smoothstep(.55,.76,u)*.5),width=2)
    centered(d,'a process · not a thing',630,FONT['s'],INK,smoothstep(.68,.84,u))
    return im

def emp_3(t,u,i):
    im=canvas(WHITE); d=ImageDraw.Draw(im); label(d,i,'The flame',False)
    xs=[330,640,950]; phases=[0,.33,.66]
    for j,(x,p) in enumerate(zip(xs,phases)):
        a=smoothstep(.05+p*.6,.28+p*.6,u)
        d.line((x,460,x,560),fill=rgba(BLACK,a),width=5); d.arc((x-60,310,x+60,470),start=200,end=340,fill=rgba(CRIMSON,a),width=4); d.arc((x-35,340,x+35,445),start=200,end=340,fill=rgba(GOLD,a),width=3)
        if j<2: arrow(d,(x+75,405),(xs[j+1]-75,405),MUTED,a,2)
    centered(d,'the same flame?',110,FONT['l'],BLACK,smoothstep(.06,.24,u)); centered(d,'real as relation · empty of independence',625,FONT['s'],BLACK,smoothstep(.68,.85,u))
    return im

def emp_4(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Time is relation')
    xs=[250,640,1030]; names=['past','present','future']
    for j,(x,n) in enumerate(zip(xs,names)):
        a=smoothstep(.06+j*.17,.26+j*.17,u); ring(d,x,360,70,GOLD if j==1 else MUTED,a,3); w,_=text_size(d,n,FONT['s']); d.text((x-w/2,450),n,font=FONT['s'],fill=rgba(INK,a))
    arrow(d,(320,360),(570,360),CRIMSON,smoothstep(.26,.48,u),2); arrow(d,(710,360),(960,360),CRIMSON,smoothstep(.48,.68,u),2)
    fade=1-smoothstep(.65,.92,u); ring(d,640,360,70,GOLD,fade,3)
    centered(d,'try to grasp the present alone',105,FONT['m'],INK,smoothstep(.08,.26,u)); centered(d,'and it dissolves',610,FONT['l'],GOLD,smoothstep(.65,.84,u))
    return im

def emp_5(t,u,i):
    im=canvas(WHITE); d=ImageDraw.Draw(im); label(d,i,'Two truths',False)
    # waves above, water below
    wavy_line(d,100,1180,310,42,t*.4,BLUE,smoothstep(.08,.3,u),4,3)
    d.rectangle((100,355,1180,555),outline=rgba(BLUE,smoothstep(.26,.5,u)),width=3)
    centered(d,'WAVES',170,FONT['l'],BLACK,smoothstep(.05,.23,u)); centered(d,'WATER',410,FONT['l'],BLUE,smoothstep(.3,.52,u))
    centered(d,'two perspectives · one reality',625,FONT['s'],BLACK,smoothstep(.68,.84,u))
    return im

def emp_6(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Emptiness is empty')
    # ladder climbs then erases
    a=1-smoothstep(.55,.9,u)
    for k in range(8): y=560-k*55; d.line((520,y,760,y),fill=rgba(GOLD,a),width=3)
    d.line((520,590,520,145),fill=rgba(GOLD,a),width=4); d.line((760,590,760,145),fill=rgba(GOLD,a),width=4)
    centered(d,'THE LADDER',90,FONT['l'],INK,smoothstep(.05,.24,u)); centered(d,'must also be released',610,FONT['m'],CRIMSON,smoothstep(.62,.82,u))
    return im

def emp_7(t,u,i):
    im=canvas(WHITE); d=ImageDraw.Draw(im); label(d,i,'Saṃsāra and nirvāṇa',False)
    cx,cy=W/2,365; sep=lerp(220,0,smoothstep(.18,.78,u))
    ring(d,cx-sep,cy,155,CRIMSON,.85,4); ring(d,cx+sep,cy,155,GOLD,.85,4)
    centered(d,'SAṂSĀRA',120,FONT['m'],CRIMSON,smoothstep(.05,.24,u)); centered(d,'NIRVĀṆA',560,FONT['m'],GOLD,smoothstep(.28,.46,u)); centered(d,'the boundary was part of the dream',630,FONT['s'],BLACK,smoothstep(.68,.84,u))
    return im

def emp_8(t,u,i):
    bg=tuple(int(lerp(WHITE[j],DARK[j],smoothstep(.7,1,u))) for j in range(3)); im=canvas(bg); d=ImageDraw.Draw(im); label(d,i,'You are a verb',u>.7)
    # empty room framing two hands reaching
    a=1-smoothstep(.62,.92,u); d.rectangle((170,110,1110,610),outline=rgba(BLACK,a),width=3)
    d.line((250,420,555,360),fill=rgba(CRIMSON,a),width=5); d.line((1030,420,725,360),fill=rgba(GOLD,a),width=5)
    if u<.72: centered(d,'You are not a thing.',110,FONT['l'],BLACK,smoothstep(.05,.24,u)); centered(d,'You are the space where existence learns to touch itself.',620,FONT['s'],BLACK,smoothstep(.58,.76,u),1080)
    if u>.72: centered(d,'VERB',310,FONT['xl'],INK,smoothstep(.76,.96,u))
    return im

EMP=[Scene('Everything is empty',30,emp_1,'Cup and capacity.'),Scene('Dependent arising',34,emp_2,'Network without independent center.'),Scene('The flame',30,emp_3,'Continuity as process.'),Scene('Time is relation',31,emp_4,'Present dissolves when isolated.'),Scene('Two truths',31,emp_5,'Waves and water.'),Scene('Emptiness is empty',29,emp_6,'Release the ladder.'),Scene('Saṃsāra and nirvāṇa',31,emp_7,'Difference collapses.'),Scene('You are a verb',29,emp_8,'Openness makes relationship possible.')]


# ---------------- DANTE ----------------
def dan_1(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'The dark wood')
    # vertical branching trees
    for k in range(11):
        x=80+k*115; a=smoothstep(.03+k*.025,.3+k*.02,u); d.line((x,650,x+30*math.sin(k),120),fill=rgba(MUTED,a*.7),width=4)
        for b in range(4):
            yy=190+b*95; d.line((x,yy,x-45-15*b,yy-65),fill=rgba(MUTED,a*.55),width=2); d.line((x,yy,x+50+10*b,yy-55),fill=rgba(MUTED,a*.55),width=2)
    silhouette(d,W/2,450,.7,INK,smoothstep(.18,.38,u))
    centered(d,'THE JOURNEY YOU DIDN’T KNOW YOU WERE ON',80,FONT['l'],INK,smoothstep(.04,.22,u),1100); centered(d,'confrontation · purification · recognition',620,FONT['s'],GOLD,smoothstep(.65,.83,u))
    return im

def dan_2(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Nine circles')
    cx,cy=W/2,260
    for k in range(9):
        a=smoothstep(.04+k*.06,.18+k*.06,u); r=75+k*31; d.arc((cx-r,cy-r*.35,cx+r,cy+r*.35),start=0,end=180,fill=rgba(CRIMSON if k>5 else MUTED,a),width=3)
    arrow(d,(cx,150),(cx,590),GOLD,smoothstep(.35,.75,u),3)
    centered(d,'DESCENT',90,FONT['l'],INK,smoothstep(.05,.22,u)); centered(d,'each circle reveals a harder contraction',620,FONT['s'],INK,smoothstep(.67,.84,u))
    return im

def dan_3(t,u,i):
    im=canvas(PARCHMENT); d=ImageDraw.Draw(im); label(d,i,'Virgil and the edge of reason',False)
    # guide with lantern and follower
    silhouette(d,420,405,.75,BLACK,smoothstep(.05,.22,u)); silhouette(d,820,430,.62,MUTED,smoothstep(.16,.34,u))
    ring(d,510,260,65+6*math.sin(t*.5),GOLD,smoothstep(.18,.38,u),3); dot(d,510,260,8,GOLD,1)
    arrow(d,(560,360),(730,380),BLACK,smoothstep(.35,.58,u),2)
    centered(d,'REASON CAN LEAD YOU',85,FONT['l'],BLACK,smoothstep(.05,.25,u)); centered(d,'to the edge of what has shape',580,FONT['m'],BLACK,smoothstep(.52,.72,u)); centered(d,'then another kind of seeing begins',625,FONT['s'],CRIMSON,smoothstep(.68,.86,u))
    return im

def dan_4(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Seven terraces')
    # mountain screw
    cx=640; names=['pride','envy','wrath','sloth','avarice','gluttony','lust']
    for k,n in enumerate(names):
        y=585-k*65; width=500-k*55; a=smoothstep(.04+k*.07,.2+k*.07,u)
        d.arc((cx-width/2,y-40,cx+width/2,y+40),start=0,end=180,fill=rgba(GOLD if k>3 else CRIMSON,a),width=3)
        d.text((80,y-12),n,font=FONT['xs'],fill=rgba(INK,a))
    arrow(d,(640,600),(640,105),INK,smoothstep(.4,.82,u),3)
    centered(d,'PURGATORY',70,FONT['l'],INK,smoothstep(.05,.22,u)); centered(d,'fire clarifies rather than destroys',640,FONT['s'],MUTED,smoothstep(.7,.86,u))
    return im

def dan_5(t,u,i):
    im=canvas(PARCHMENT); d=ImageDraw.Draw(im); label(d,i,'Beatrice descends',False)
    silhouette(d,390,430,.68,BLACK,smoothstep(.05,.22,u)); silhouette(d,890,370,.72,GOLD,smoothstep(.2,.45,u))
    for k in range(7): ring(d,890,355,50+k*35+5*math.sin(t*.4+k),GOLD,smoothstep(.28+k*.04,.65+k*.03,u)*(.36-k*.035),1)
    d.line((550,370,735,360),fill=rgba(CRIMSON,smoothstep(.48,.7,u)),width=2)
    centered(d,'THE BELOVED WHO REVEALS',90,FONT['l'],BLACK,smoothstep(.05,.25,u)); centered(d,'she leads by being seen',625,FONT['s'],BLACK,smoothstep(.68,.84,u))
    return im

def dan_6(t,u,i):
    im=canvas(DARK); d=ImageDraw.Draw(im); label(d,i,'Nine spheres')
    cx,cy=W/2,375
    for k in range(9):
        a=smoothstep(.04+k*.055,.18+k*.055,u); ring(d,cx,cy,45+k*29,GOLD if k>4 else MUTED,a*(.95-k*.055),2)
    dot(d,cx,cy,8,INK,1); arrow(d,(cx,cy+250),(cx,cy-250),CRIMSON,smoothstep(.42,.78,u),3)
    centered(d,'ASCENT',80,FONT['l'],INK,smoothstep(.05,.22,u)); centered(d,'less separation · more radiance',625,FONT['s'],INK,smoothstep(.68,.85,u))
    return im

def dan_7(t,u,i):
    im=canvas(PARCHMENT); d=ImageDraw.Draw(im); label(d,i,'The celestial rose',False)
    cx,cy=W/2,365
    for k in range(12):
        a=smoothstep(.03+k*.04,.18+k*.04,u); flower(d,cx,cy,55+k*18,12,GOLD if k%2 else CRIMSON,a*(.55-k*.025),t*.025+k*.04)
    centered(d,'THE CELESTIAL ROSE',90,FONT['serif_l'],BLACK,smoothstep(.05,.24,u)); centered(d,'each face a star · each star a world',625,FONT['s'],BLACK,smoothstep(.68,.84,u))
    return im

def dan_8(t,u,i):
    bg=tuple(int(lerp(DARK[j],WHITE[j],smoothstep(.58,.94,u))) for j in range(3)); im=canvas(bg); d=ImageDraw.Draw(im); label(d,i,'The final flash')
    cx,cy=W/2,360; r=lerp(6,980,smoothstep(.28,.9,u)); dot(d,cx,cy,r,WHITE,1)
    if u<.62: centered(d,'YOU TRY',105,FONT['l'],INK,smoothstep(.05,.2,u)); centered(d,'YOU ARE HELPED',170,FONT['l'],GOLD,smoothstep(.18,.36,u)); centered(d,'YOU DISAPPEAR',235,FONT['l'],CRIMSON,smoothstep(.35,.55,u))
    if u>.72: centered(d,'the love that moves the sun and the other stars',325,FONT['serif_m'],BLACK,smoothstep(.75,.95,u),1000)
    return im

DAN=[Scene('The dark wood',32,dan_1,'Lostness becomes honest orientation.'),Scene('Nine circles',34,dan_2,'Descent through contraction.'),Scene('Virgil and reason',32,dan_3,'Guidance reaches its limit.'),Scene('Seven terraces',35,dan_4,'Purification as ascent.'),Scene('Beatrice descends',32,dan_5,'Pure knowledge takes over.'),Scene('Nine spheres',32,dan_6,'Increasing transparency.'),Scene('The celestial rose',31,dan_7,'Manifestation recognized as one body.'),Scene('The final flash',28,dan_8,'Method ends in direct recognition.')]


FILMS={
 'rasa':Film('rasa','Pain Is Juice — Rasa and Aesthetic Consciousness',RASA),
 'imaginal':Film('imaginal','The World Between Worlds — Mundus Imaginalis',IMAG),
 'alchemy':Film('alchemy','The Secret Life of Matter — Alchemy',ALC),
 'emptiness':Film('emptiness','Everything Is Empty — Nāgārjuna',EMP),
 'dante':Film('dante','The Journey You Did Not Know You Were On — Dante',DAN),
}

META={
 'rasa':{'essay':5,'slug':'pain_is_juice','source_title':'pain is juice','url':'https://github.com/prx0r/blogengine/blob/main/scripts/expansion-essay5.md','visual_system':'Nine-flavor radial map, cup/fist metaphors, waves, witness field.'},
 'imaginal':{'essay':12,'slug':'world_between_worlds','source_title':'the world between worlds','url':'https://github.com/prx0r/blogengine/blob/main/scripts/expansion-essay12.md','visual_system':'Three ontological planes, doorway-eye, cosmic north, doubled luminous figures.'},
 'alchemy':{'essay':13,'slug':'secret_life_of_matter','source_title':'the secret life of matter','url':'https://github.com/prx0r/blogengine/blob/main/scripts/expansion-essay13.md','visual_system':'Flask, mirrored hexagons, element separation, six chambers, solve/coagula.'},
 'emptiness':{'essay':20,'slug':'everything_is_empty','source_title':'everything is empty','url':'https://github.com/prx0r/blogengine/blob/main/scripts/expansion-essay20.md','visual_system':'Negative space, dependency network, flame transfer, relational time, ladder removal.'},
 'dante':{'essay':23,'slug':'dante_journey','source_title':'the journey you did not know you were on','url':'https://github.com/prx0r/blogengine/blob/main/scripts/expansion-essay23.md','visual_system':'Dark wood, nine-circle descent, seven-terrace ascent, nine spheres, celestial rose.'},
}


def make_contact_sheet(film:Film,video:Path,out:Path):
    still_dir=out.parent/(film.key+'_stills'); still_dir.mkdir(exist_ok=True)
    starts=[]; tt=0
    for s in film.scenes:
        starts.append(tt+s.duration*.55); tt+=s.duration
    thumbs=[]
    for j,sec in enumerate(starts,1):
        p=still_dir/f'{j:02d}.jpg'
        os.system(f"ffmpeg -y -loglevel error -ss {sec:.2f} -i '{video}' -frames:v 1 '{p}'")
        if p.exists():
            im=Image.open(p).convert('RGB').resize((320,180)); dd=ImageDraw.Draw(im); dd.rectangle((0,0,92,24),fill='white'); dd.text((6,4),f'{j:02d} · {int(sec)}s',font=FONT['xs'],fill='black'); thumbs.append(im)
    rows=math.ceil(len(thumbs)/2); sheet=Image.new('RGB',(640,rows*180),(110,110,110))
    for j,im in enumerate(thumbs): sheet.paste(im,((j%2)*320,(j//2)*180))
    sheet.save(out,quality=90)


def create_pack(film:Film):
    meta=META[film.key]; folder=ROOT/f"essay{meta['essay']:02d}_{meta['slug']}_output_pack"; folder.mkdir(parents=True,exist_ok=True)
    video=folder/f"essay{meta['essay']:02d}_{meta['slug']}_animation.mp4"
    film.render(video)
    manifest=folder/'scene_manifest.json'; manifest.write_text(json.dumps(film.manifest(),indent=2,ensure_ascii=False),encoding='utf-8')
    sheet=folder/'contact_sheet.jpg'; make_contact_sheet(film,video,sheet)
    script_src=Path(__file__); shutil.copy2(script_src,folder/'render_expansion_essay_collection.py')
    wrapper=folder/'render_this_film.py'; wrapper.write_text(f"from render_expansion_essay_collection import main\nmain(['--film','{film.key}','--pack-only'])\n",encoding='utf-8')
    readme=f"""# {film.title}\n\nSilent minimal animation draft based on expansion essay {meta['essay']}.\n\n- Source: {meta['url']}\n- Resolution: {W}x{H}\n- FPS: {FPS}\n- Duration: {film.duration/60:.1f} minutes\n- Codec: H.264 / yuv420p\n- Audio: none\n\n## Re-render\n\n```bash\npython render_this_film.py\n```\n\nChange `FPS` near the top of `render_expansion_essay_collection.py` for smoother motion.\n"""
    (folder/'README.md').write_text(readme,encoding='utf-8')
    notes=f"""# Process notes\n\nThis pack was produced directly from the supplied expansion essay rather than through the ontology compiler. The essay's argument was reduced to eight visual beats, and each beat was implemented as a deterministic Pillow drawing function. Frames were assembled with OpenCV and transcoded to browser-friendly H.264 with FFmpeg.\n\n## Visual system\n\n{meta['visual_system']}\n\n## Constraints\n\n- No narration or music was available, so timing is approximate.\n- No external art, LTX clips, or manuscript images were used.\n- Text is intentionally sparse; the animation is designed to sit beneath narration.\n- Motion is deliberately slow at {FPS} fps.\n- The renderer is a direct creative draft, not a universal engine.\n\n## Best use\n\nUse the MP4 as a continuous visual bed, or cut its individual scenes into FableCut beneath the final narration. The `scene_manifest.json` gives exact scene boundaries.\n"""
    (folder/'PROCESS_NOTES.md').write_text(notes,encoding='utf-8')
    source=f"""# Source notes\n\n- Repository: `prx0r/blogengine`\n- File: `scripts/expansion-essay{meta['essay']}.md`\n- Title: **{meta['source_title']}**\n- URL: {meta['url']}\n\n## Adaptation method\n\nThe animation follows the source's conceptual progression and uses short phrases only. Long quotations were not placed onscreen.\n\n## Scene list\n\n""" + '\n'.join(f"{i}. **{s.title}** — {s.note}" for i,s in enumerate(film.scenes,1)) + '\n'
    (folder/'SOURCE_NOTES.md').write_text(source,encoding='utf-8')
    zip_path=ROOT/f"essay{meta['essay']:02d}_{meta['slug']}_output_pack.zip"
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for p in folder.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(folder.parent))
    return folder,zip_path,video,sheet


def make_collection_zip():
    p=ROOT/'selected_five_expansion_essay_animation_packs.zip'
    with zipfile.ZipFile(p,'w',zipfile.ZIP_STORED) as z:
        for key,film in FILMS.items():
            meta=META[key]; pack=ROOT/f"essay{meta['essay']:02d}_{meta['slug']}_output_pack.zip"
            if pack.exists(): z.write(pack,pack.name)
        selection=ROOT/'SELECTION_NOTES.md'
        selection.write_text("""# Selected five expansion essays\n\n1. Essay 5 — **Pain Is Juice**: aesthetic emotion and rasa.\n2. Essay 12 — **The World Between Worlds**: Corbin's imaginal geography.\n3. Essay 13 — **The Secret Life of Matter**: alchemical transformation.\n4. Essay 20 — **Everything Is Empty**: Nāgārjuna and dependent arising.\n5. Essay 23 — **The Journey You Didn't Know You Were On**: Dante as descent, purification, and recognition.\n\nThese were chosen after reviewing the opening premise of essays 1–34. They maximize difference in subject, visual metaphor, spatial logic, and emotional rhythm while avoiding duplication of the already-rendered Spanda and kañcuka films.\n""",encoding='utf-8')
        z.write(selection,selection.name)
    return p


def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--film',choices=list(FILMS)+['all'],default='all'); ap.add_argument('--pack-only',action='store_true'); args=ap.parse_args(argv)
    ROOT.mkdir(parents=True,exist_ok=True)
    keys=list(FILMS) if args.film=='all' else [args.film]
    for k in keys: create_pack(FILMS[k])
    if args.film=='all': print('collection',make_collection_zip())

if __name__=='__main__': main()
