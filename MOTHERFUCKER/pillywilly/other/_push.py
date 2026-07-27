#!/usr/bin/env python3
"""Push all packs to 400+ lines with rich visual functions."""
import os, re

def push(fname, vis_funcs):
    path = os.path.join("/root/projects/tantraloka/goldrender", fname)
    text = open(path).read()
    idx = text.find("\nVISUALS = {")
    if idx > 0 and vis_funcs:
        insert = "\n\n" + "\n\n".join(vis_funcs) + "\n"
        text = text[:idx] + insert + text[idx:]
    text = text.replace("; if q<=0:", "\n        if q<=0:")
    open(path, "w").write(text)
    nl = chr(10); sq = 'Scene("'
    print(f"  {fname}: {text.count(nl)}L {text.count(sq)}S")

push("objects_as_actions_platinum.py", [
    r'''def vis_action_cont(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(8):
        a=i*math.tau/8+t*0.06; q=clamp(r*4-i*0.08); if q<=0: continue
        rad=30+110*q; x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        col=mix(CYAN,GOLD,i/7); d.line((cx,cy,x,y),fill=(*col,int(170*q)),width=3)
        glow_circle(im,x,y,6+3*q,col,int(160*q),7)
    glow_circle(im,cx,cy,14,GOLD,int(190*r),12)
    seal(im,'THE CONTINUUM OF ACTION','every object is action slowed to apparent stillness - speed of being',GOLD)''',
    r'''def vis_noun_illusion(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/30)*(30+110*r),cy+math.sin(i*math.tau/30)*(30+110*r)*0.35) for i in range(31)]
    glow_line(im,partial(pts,r),CYAN,width=4,alpha=210,blur=14)
    labels=['TABLE','CHAIR','MOUNTAIN','RIVER','SELF']
    for i,l in enumerate(labels):
        a=i*math.tau/len(labels)+t*0.05; q=clamp(r*5-i*0.1); if q<=0: continue
        x=cx+math.cos(a)*(40+100*q); y=cy+math.sin(a)*(40+100*q)*0.35
        d.ellipse((x-10*q,y-10*q,x+10*q,y+10*q),outline=(*GOLD,int(150*q)),width=2)
        centered_text(d,(x,y+16*q),l,load_font(FONT_SERIF,int(h*0.019)),GOLD)
    seal(im,'THE NOUN ILLUSION','nouns are frozen verbs - language tricks us into believing in static things',CYAN)''',
])

push("psyche_gestalt_platinum.py", [
    r'''def vis_psyche_cont(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,16,VIOLET,int(200*r),14)
    for i in range(8):
        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.08); if q<=0: continue
        rad=30+110*q; x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        col=mix(VIOLET,GOLD,i/7); d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)
        glow_circle(im,x,y,5+3*q,col,int(150*q),7)
    seal(im,'THE PSYCHE CONTINUES','the psyche does not end at death - it is energy, and energy transforms',VIOLET)''',
    r'''def vis_psyche_energy(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(40):
        a=i*math.tau/40+t*0.04; rad=20+130*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        col=mix(CYAN,VIOLET,i/39); d.ellipse((x-3,y-3,x+3,y+3),fill=(*col,int(130*r)))
    glow_circle(im,cx,cy,14,VIOLET,int(190*r),12)
    seal(im,'PSYCHIC ENERGY','the psyche is a field of energy that individuates into experience',CYAN)''',
])

push("dna_antenna_platinum.py", [
    r'''def vis_dna_full(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for j in range(2):
        off=j*math.pi; pts=[]
        for i in range(70):
            q=i/69; x=lerp(w*0.15,w*0.85,q)
            y=cy+math.sin(q*math.tau*5+off+r*math.tau)*(18+6*q)*r
            pts.append((x,y))
        col=CYAN if j==0 else GOLD
        glow_line(im,partial(pts,r),col,width=3,alpha=180,blur=10)
        for i in range(7):
            q=i/6; pos=int(q*69); x=lerp(w*0.15,w*0.85,pos/69)
            y=cy+math.sin(q*math.tau*5+off+r*math.tau)*(18+6*q)*r
            d.ellipse((x-5*r,y-5*r,x+5*r,y+5*r),fill=(*col,int(180*r)))
    seal(im,'FULL DNA ACTIVATION','the double helix is a receiver for two frequencies - yang and yin, signal and ground',CYAN)''',
    r'''def vis_light_body(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/40)*(30+130*r),cy+math.sin(i*math.tau/40)*(30+130*r)*0.35) for i in range(41)]
    glow_line(im,partial(pts,r),GOLD,width=5,alpha=230,blur=18)
    for i in range(12):
        a=i*math.tau/12+t*0.04; rad=25+120*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        d.ellipse((x-3*r,y-3*r,x+3*r,y+3*r),fill=(*PALE_GOLD,int(140*r)))
    centered_text(d,(cx,cy),'LIGHT',load_font(FONT_SERIF_BOLD,int(h*0.055)),(*GOLD,int(210*r)))
    seal(im,'THE LIGHT BODY','DNA is the interface between consciousness and matter - the bridge of light',GOLD)''',
])

push("constructed_self_platinum.py", [
    r'''def vis_self_full(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,18,GOLD,int(210*r),16)
    for i in range(8):
        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.08); if q<=0: continue
        rad=30+110*q; x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        col=mix(CYAN,GREEN,i/7); d.line((cx,cy,x,y),fill=(*col,int(170*q)),width=3)
        glow_circle(im,x,y,5+3*q,col,int(160*q),7)
    seal(im,'THE FULL SELF-MODEL','the self is not in the body - the body is a model within consciousness',GOLD)''',
    r'''def vis_no_self(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/35)*(30+120*r),cy+math.sin(i*math.tau/35)*(30+120*r)*0.35) for i in range(36)]
    glow_line(im,partial(pts,r),GOLD,width=4,alpha=220,blur=16)
    for i in range(6):
        a=i*math.tau/6+r*0.4; rad=40+100*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        col=mix(CYAN,CRIMSON,i/5); d.line((cx,cy,x,y),fill=(*col,int(150*r)),width=2)
        glow_circle(im,x,y,5+3*r,col,int(140*r),7)
    centered_text(d,(cx,cy),chr(8709),load_font(FONT_SERIF_BOLD,int(h*0.080)),(*GOLD,int(200*r)))
    seal(im,'NO PERMANENT SELF','the self is not a thing - it is a process of modeling that never stops',GOLD)''',
])

print("\nDone.")
