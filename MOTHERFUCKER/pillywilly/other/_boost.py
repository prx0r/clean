#!/usr/bin/env python3
"""Boost packs under 400 lines to 400+."""
import os, re

def boost(fname, vis, scenes):
    path = os.path.join("/root/projects/tantraloka/goldrender", fname)
    text = open(path).read()
    if vis:
        idx = text.find("\nVISUALS = {")
        if idx > 0:
            text = text[:idx] + "\n\n" + "\n\n".join(vis) + "\n" + text[idx:]
    if scenes:
        se = text.rfind("\n]")
        if se > 0:
            ex = "\n"
            for t, n, d, v, *rest in scenes:
                p = rest[0] if rest else {}
                ps = "{" + ", ".join(f'"{k}":"{v}"' for k,v in p.items()) + "}"
                ex += f'    Scene("{t}","{n}",{d},"{v}",{ps}),\n'
            ex += "\n"
            text = text[:se] + ex + text[se:]
    text = text.replace("; if q<=0:", "\n        if q<=0:")
    open(path, "w").write(text)
    l = text.count("\n")
    return l

# Add 3-4 scenes + 1-2 vis funcs to each pack under 400
packs = {
    "time_is_forgetting_platinum.py": (
        [r'''def vis_time_depth(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(5):
        q=clamp(r*5-i); if q<=0: continue
        y=lerp(h*0.22,h*0.62,i/4); col=mix(GOLD,CRIMSON,i/4)
        d.ellipse((cx-60*q,y-15*q,cx+60*q,y+15*q),outline=(*col,int(180*q)),width=2)
        centered_text(d,(cx+80*q,y),f'DEPTH {i+1}',load_font(FONT_SANS_BOLD,int(h*0.017)),col)
    seal(im,'THE DEPTHS OF TIME','time has depth - the present moment contains all moments as potential',GOLD)'''],
        [("The Depths of Time","Time has depth - the present moment contains all moments as potential.",8.5,"time_depth"),
         ("The Still Point","At the center of the spiral of time is the still point. You are that point.",9.0,"now_vis"),
         ("Memory Creates Future","The way you remember the past shapes the future you can perceive.",8.5,"past_vis")]
    ),
    "svatantrya_freedom_platinum.py": (
        [r'''def vis_freedom_ground(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/40)*(30+130*r),cy+math.sin(i*math.tau/40)*(30+130*r)*0.35) for i in range(41)]
    glow_line(im,partial(pts,r),GOLD,width=5,alpha=240,blur=18)
    centered_text(d,(cx,cy),chr(8734),load_font(FONT_SERIF_BOLD,int(h*0.10)),(*GOLD,int(210*r)))
    for i in range(8):
        a=i*math.tau/8+t*0.04; rad=50+120*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        d.ellipse((x-4*r,y-4*r,x+4*r,y+4*r),fill=(*PALE_GOLD,int(140*r)))
    seal(im,'FREEDOM IS THE GROUND','freedom is not something you achieve - it is what you are before you are anything',GOLD)'''],
        [("Freedom is the Ground","Freedom is not something you achieve - it is what you are before you are anything.",9.5,"freedom_ground"),
         ("The Free Act","Every act is free. The experience of constraint is freedom playing hide-and-seek.",9.0,"vi_s_free_will"),
         ("Witnessing Freedom","The witness of all experience is the one place that has never been bound.",9.5,"vi_s_consciousness_freedom")]
    ),
    "objects_as_actions_platinum.py": (
        [r'''def vis_process_reality(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for j in range(4):
        pts=[]
        for i in range(60):
            q=i/59; x=lerp(w*0.10,w*0.90,q); freq=3+j*1.5
            y=cy+math.sin(q*math.tau*freq+t*1.5+r*math.tau)*(12+8*j)*r
            pts.append((x,y))
        col=mix(CYAN,GOLD,j/3)
        glow_line(im,partial(pts,r),col,width=2+j,alpha=int(170-30*j)*r,blur=8+j*2)
    seal(im,'PROCESS IS THE SUBSTANCE','the world is not made of matter - it is made of processes interacting',CYAN)'''],
        [("Process is the Substance","The world is not made of matter - it is made of processes interacting.",9.0,"process_reality"),
         ("The Universe as Activity","The universe is not a thing. It is a vast activity experiencing itself.",9.5,"vi_s_flow"),
         ("Action is the Only Truth","What is real is what acts. If it acts, it is real - even if it seems to be a noun.",9.0,"action_field")]
    ),
    "psyche_gestalt_platinum.py": (
        [r'''def vis_psyche_dreaming(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,18,VIOLET,int(200*r),14)
    for i in range(12):
        a=i*math.tau/12+t*0.06; q=clamp(r*4-i*0.06); if q<=0: continue
        x=cx+math.cos(a)*(30+110*q); y=cy+math.sin(a)*(30+110*q)*0.35
        col=mix(VIOLET,GOLD,i/11); d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)
        d.ellipse((x-6*q,y-6*q,x+6*q,y+6*q),fill=(*col,int(150*q)))
        d.ellipse((x-10*q,y-10*q,x+10*q,y+10*q),outline=(*col,int(100*q)),width=1)
    seal(im,'THE DREAMING PSYCHE','every night, the psyche weaves the next day - sleep is the artists studio',VIOLET)'''],
        [("The Dreaming Psyche","Every night, the psyche weaves the next day - sleep is the artist's studio.",8.5,"psyche_dreaming"),
         ("The Psyche is Timeless","The psyche does not age. It accumulates experience but remains ageless.",9.0,"vi_s_psyche_field"),
         ("Myth as Psyche","The myths of every culture are the psyche's self-portrait.",9.0,"gods_vis")]
    ),
    "dna_antenna_platinum.py": (
        [r'''def vis_dna_evolution(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(6):
        q=clamp(r*6-i); if q<=0: continue
        y=lerp(h*0.22,h*0.65,i/5); col=mix(CYAN,GOLD,i/5)
        d.ellipse((cx-40*q,y-18*q,cx+40*q,y+18*q),outline=(*col,int(180*q)),width=2)
        centered_text(d,(cx,y),f'STRAND {i+1}',load_font(FONT_SANS_BOLD,int(h*0.018)),col)
    seal(im,'DNA EVOLUTION','humanity is evolving to receive more of the cosmic signal - the 12-strand potential',GOLD)'''],
        [("DNA Evolution","Humanity is evolving to receive more of the cosmic signal - the 12-strand potential.",9.0,"dna_evolution"),
         ("The Wave is Now","Humanity is in a wave of frequency change. DNA is responding.",9.5,"frequency"),
         ("You Are the Receiver","Not the signal, not the source - you are the receiver learning to tune.",9.5,"vi_s_dna_reception")]
    ),
    "constructed_self_platinum.py": (
        [r'''def vis_self_plasticity_full(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,16,GOLD,int(200*r),14)
    for i in range(6):
        a=i*math.tau/6+t*0.06; q=clamp(r*4-i*0.08); if q<=0: continue
        x=cx+math.cos(a)*(30+100*q); y=cy+math.sin(a)*(30+100*q)*0.35
        col=mix(CYAN,GREEN,i/5); d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)
        d.ellipse((x-8*q,y-8*q,x+8*q,y+8*q),fill=(*col,int(150*q)))
    centered_text(d,(cx,cy+40*r),'PLASTIC',load_font(FONT_SANS_BOLD,int(h*0.030)),(*GOLD,int(200*r)))
    seal(im,'THE SELF IS PLASTIC','the self-model can change - this is the mechanism of healing and growth',GOLD)'''],
        [("The Self is Plastic","The self-model can change - this is the mechanism of healing and growth.",8.5,"self_plasticity_full"),
         ("The Extended Self","Your self-model includes your body, your tools, your loved ones. It extends.",9.0,"vi_s_self_boundary"),
         ("No Fixed Self","There is no unchanging self. There is only the ongoing act of self-ing.",9.5,"self_model")]
    ),
    "cooperation_platinum.py": (
        [r'''def vis_cooperation_gift(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,16,GOLD,int(200*r),14)
    for i in range(8):
        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.08); if q<=0: continue
        x=cx+math.cos(a)*(30+100*q); y=cy+math.sin(a)*(30+100*q)*0.35
        col=mix(GOLD,GREEN,i/7); d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)
        d.ellipse((x-6*q,y-6*q,x+6*q,y+6*q),fill=(*col,int(150*q)))
    seal(im,'COOPERATION IS THE GIFT','life gives itself to itself through cooperation - the universe is a gift economy',GOLD)'''],
        [("Cooperation is the Gift","Life gives itself to itself through cooperation - the universe is a gift economy.",9.0,"cooperation_gift"),
         ("The Body is a Commonwealth","Every cell contributes, every cell receives. The body is a commonwealth of beings.",9.0,"vi_s_body_ecosystem"),
         ("Cooperation is Consciousness","When cells cooperate, the whole becomes aware. Consciousness is cooperation.",9.5,"cooperation_vis")]
    ),
}

for fname, (vis, scenes) in packs.items():
    lines = boost(fname, vis, scenes)
    print(f"  {fname}: {lines} lines")
