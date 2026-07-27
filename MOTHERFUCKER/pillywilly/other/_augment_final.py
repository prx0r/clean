#!/usr/bin/env python3
"""Final push to get all packs to 400+ lines."""
import os, re

def augment(fname, extra_vis, extra_scenes):
    path = os.path.join("/root/projects/tantraloka/goldrender", fname)
    text = open(path).read()
    if extra_vis:
        idx = text.find("\nVISUALS = {")
        if idx > 0:
            insert = "\n\n" + "\n\n".join(extra_vis) + "\n"
            text = text[:idx] + insert + text[idx:]
    if extra_scenes:
        se = text.rfind("\n]")
        if se > 0:
            extra = "\n"
            for item in extra_scenes:
                t, n, d, v = item[0], item[1], item[2], item[3]
                p = item[4] if len(item) > 4 else {}
                ps = "{" + ", ".join(f'"{k}":"{v}"' if isinstance(v,str) else f'"{k}":{v}' for k,v in p.items()) + "}"
                extra += f'    Scene("{t}","{n}",{d},"{v}",{ps}),\n'
            extra += "\n"
            text = text[:se] + extra + text[se:]
    text = text.replace("; if q<=0: continue", "\n        if q<=0: continue")
    text = text.replace("; if q<=0:", "\n        if q<=0:")
    open(path, "w").write(text)
    l = text.count("\n"); s = text.count('Scene("'); v = len(re.findall(r'^def vis_', text, re.MULTILINE))
    return l, s, v

augment("free_energy_primitive_platinum.py", [
    r'''def vis_niche_construction(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,14,CYAN,int(180*r),10)
    for i in range(8):
        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.08)
        if q<=0: continue
        x=cx+math.cos(a)*(30+100*q); y=cy+math.sin(a)*(30+100*q)*0.35
        col=mix(CYAN,GREEN,i/7); d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)
        d.ellipse((x-8*q,y-8*q,x+8*q,y+8*q),fill=(*col,int(150*q)))
        arrow(d,(cx+(x-cx)*0.85,cy+(y-cy)*0.85),(x,y),col,2,8)
    seal(im,'NICHE CONSTRUCTION','organisms do not adapt to the world - they build the world they adapt to',GREEN)''',
    r'''def vi_s_cultural_evolution(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(7):
        q=clamp(r*7-i)
        if q<=0: continue
        y=lerp(h*0.20,h*0.65,i/6); col=mix(CYAN,GOLD,i/6)
        width=lerp(30,260,i/6)*q; d.line((w*0.50-width/2,y,w*0.50+width/2,y),fill=(*col,int(190*q)),width=4)
        centered_text(d,(w*0.50,y-14),f'SCALE {i+1}',load_font(FONT_SANS_BOLD,int(h*0.017)),(*col,int(180*q)))
    seal(im,'CULTURAL EVOLUTION','free energy minimization scales from cells to societies - the same principle',GOLD)''',
], [
    ("Niche Construction", "Organisms do not adapt to the world - they build the world they adapt to.", 8.5, "niche_construction"),
    ("Cultural Evolution", "Free energy minimization scales from cells to societies - the same principle.", 9.0, "vi_s_cultural_evolution"),
    ("The Free Energy of Meaning", "Meaning is what reduces uncertainty about what to do next.", 8.5, "curiosity"),
    ("From Bacteria to Beliefs", "The free energy principle applies to everything that persists.", 9.5, "self_organizing"),
])

augment("consciousness_container_platinum.py", [
    r'''def vis_bindu(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,24,GOLD,int(240*r),20)
    centered_text(d,(cx,cy),chr(9679),load_font(FONT_SERIF_BOLD,int(h*0.12)),(*GOLD,int(220*r)))
    for i in range(6):
        a=i*math.tau/6+t*0.05; q=clamp(r*4-i*0.1)
        if q<=0: continue
        rad=40+100*q; x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        col=mix(GOLD,VIOLET,i/5); d.line((cx,cy,x,y),fill=(*col,int(150*q)),width=2)
        glow_circle(im,x,y,5+3*q,col,int(140*q),6)
    seal(im,'THE BINDU','the point from which all tattvas emanate - the seed of the universe',GOLD)''',
    r'''def vis_aham(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,20,GOLD,int(220*r),18)
    centered_text(d,(cx,cy-15),'AHAM',load_font(FONT_SERIF_BOLD,int(h*0.065)),(*GOLD,int(210*r)))
    centered_text(d,(cx,cy+30),'I AM',load_font(FONT_SERIF,int(h*0.035)),(*PALE_GOLD,int(180*r)))
    for i in range(12):
        a=i*math.tau/12+t*0.04; rad=50+120*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        glow_circle(im,x,y,4+2*r,PALE_GOLD,int(130*r),5)
    seal(im,'AHAM - THE I-SENSE','the first vibration of consciousness - I am before I am anything',GOLD)''',
], [
    ("The Bindu", "The point from which all tattvas emanate - the seed of the universe.", 8.5, "bindu"),
    ("Aham - The I-Sense", "The first vibration of consciousness - I am before I am anything.", 9.0, "aham"),
    ("The Thirty-Six Tattvas", "Shiva's body has 36 principles. Your body has the same.", 9.0, "tattvas_wheel"),
    ("Consciousness is the Container", "Not in the body - the body is in consciousness. You are the space.", 9.5, "realization"),
])

augment("time_is_forgetting_platinum.py", [
    r'''def vis_kaala(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(12):
        a=i*math.tau/12+t*0.05; q=clamp(r*6-i*0.04)
        if q<=0: continue
        x=cx+math.cos(a)*(20+120*q); y=cy+math.sin(a)*(20+120*q)*0.35
        col=mix(CYAN,CRIMSON,i/11); d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)
        d.ellipse((x-5*q,y-5*q,x+5*q,y+5*q),fill=(*col,int(150*q)))
    glow_circle(im,cx,cy,12,GOLD,int(180*r),10)
    seal(im,'KAALA - COSMIC TIME','not the time of clocks - the time that is the pulse of consciousness itself',GOLD)''',
    r'''def vis_simultaneity(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/40)*(30+130*r),cy+math.sin(i*math.tau/40)*(30+130*r)*0.35) for i in range(41)]
    glow_line(im,partial(pts,r),GOLD,width=5,alpha=230,blur=16)
    for i in range(10):
        a=i*math.tau/10+t*0.04; rad=20+100*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        glow_circle(im,x,y,5+3*r,PALE_GOLD,int(150*r),6)
    centered_text(d,(w*0.50,h*0.20),'ALL AT ONCE',load_font(FONT_SERIF_BOLD,int(h*0.035)),(*GOLD,int(200*r)))
    seal(im,'SIMULTANEITY','the universe is a single act - time is the illusion of sequence',GOLD)''',
], [
    ("Kaala - Cosmic Time", "Not the time of clocks - the time that is the pulse of consciousness itself.", 8.5, "kaala"),
    ("Simultaneity", "The universe is a single act - time is the illusion of sequence.", 9.0, "simultaneity"),
    ("The Spiral Remembers", "Time spirals, and at each return, you are more awake.", 9.0, "time_spiral"),
    ("Forgetting is the Gift", "Without forgetting, every moment would be eternal. Forgetting is mercy.", 9.5, "forgetting"),
])

augment("svatantrya_freedom_platinum.py", [
    r'''def vi_s_free_will(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(3):
        a=(i-1)*0.7; q=clamp(r*3-i*0.15)
        if q<=0: continue
        x=cx+math.cos(a)*130*q; y=cy+math.sin(a)*130*q
        col=[CRIMSON,CYAN,GREEN][i]; d.line((cx,cy,x,y),fill=(*col,int(170*q)),width=3)
        d.ellipse((x-12*q,y-12*q,x+12*q,y+12*q),fill=(*col,int(160*q)))
        label=['DETERMINISM','FREEDOM','CHOICE'][i]
        centered_text(d,(x,y+22*q),label,load_font(FONT_SANS_BOLD,int(h*0.020)),col)
    seal(im,'FREE WILL IS REAL','not the freedom to choose what you want - the freedom to BE what you choose',GOLD)''',
    r'''def vi_s_consciousness_freedom(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/30)*(30+120*r),cy+math.sin(i*math.tau/30)*(30+120*r)*0.35) for i in range(31)]
    glow_line(im,partial(pts,r),GOLD,width=4,alpha=230,blur=16)
    centered_text(d,(cx,cy),'SVATANTRYA',load_font(FONT_SERIF_BOLD,int(h*0.045)),(*GOLD,int(210*r)))
    centered_text(d,(cx,cy+35),'ABSOLUTE FREEDOM',load_font(FONT_SANS,int(h*0.025)),(*PALE_GOLD,int(160*r)))
    for i in range(6):
        a=i*math.tau/6+t*0.05; rad=30+100*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        glow_circle(im,x,y,5+3*r,PALE_GOLD,int(140*r),6)
    seal(im,'CONSCIOUSNESS IS FREEDOM','freedom is not a property of consciousness - it IS consciousness',GOLD)''',
], [
    ("Free Will is Real", "Not the freedom to choose what you want - the freedom to BE what you choose.", 8.5, "vi_s_free_will"),
    ("Consciousness is Freedom", "Freedom is not a property of consciousness - it IS consciousness.", 9.5, "vi_s_consciousness_freedom"),
    ("The Cage is a View", "What appears as unfreedom is freedom viewing itself from a contracted perspective.", 9.0, "freedom_contraction"),
    ("Living Freedom", "To live from freedom is to act without the need to know why.", 9.5, "living_vis"),
])

augment("objects_as_actions_platinum.py", [
    r'''def vi_s_flow(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for j in range(3):
        pts=[]
        for i in range(60):
            q=i/59; x=lerp(w*0.10,w*0.90,q)
            y=cy+math.sin(q*math.tau*(4+j*2)+t*2+r*math.tau)*(15+j*5)*r
            pts.append((x,y))
        col=mix(CYAN,GOLD,j/2)
        glow_line(im,partial(pts,r),col,width=3-j,alpha=int(180-40*j)*r,blur=8+j*2)
    glow_circle(im,cx,cy,10,GOLD,int(170*r),9)
    seal(im,'THE FLOW OF ACTION','reality is not static - it is a continuous flowing action appearing as objects',GOLD)''',
], [
    ("The Flow of Action", "Reality is not static - it is a continuous flowing action appearing as objects.", 8.5, "vi_s_flow"),
    ("Every Object is an Event", "What appears as a thing is an event happening slowly enough to seem still.", 9.0, "action_field"),
    ("The Universe is a Verb", "The universe is not a thing. It is a vast activity knowing itself.", 9.5, "verb_world"),
])

augment("psyche_gestalt_platinum.py", [
    r'''def vi_s_psyche_field(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(30):
        a=i*math.tau/30+t*0.04; rad=20+130*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        col=mix(VIOLET,CYAN,i/29); d.ellipse((x-3,y-3,x+3,y+3),fill=(*col,int(130*r)))
    glow_circle(im,cx,cy,16,VIOLET,int(200*r),14)
    d=ImageDraw.Draw(im); centered_text(d,(cx,cy),'~',load_font(FONT_SERIF_BOLD,int(h*0.080)),(*VIOLET,int(200*r)))
    seal(im,'THE PSYCHE AS FIELD','not a thing in time - a field of aware energy that manifests as experience',VIOLET)''',
], [
    ("The Psyche as Field", "Not a thing in time - a field of aware energy that manifests as experience.", 9.0, "vi_s_psyche_field"),
    ("The Psyche Never Sleeps", "In dreamless sleep, the psyche is still active - building the next day.", 8.5, "dreaming_vis"),
    ("Myth is the Psyche Speaking", "When the psyche speaks directly, it speaks in myth. Listen.", 9.0, "gods_vis"),
])

augment("dna_antenna_platinum.py", [
    r'''def vi_s_dna_reception(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,16,VIOLET,int(200*r),14)
    for i in range(8):
        a=i*math.tau/8+t*0.06; q=clamp(r*4-i*0.08)
        if q<=0: continue
        x=cx+math.cos(a)*(30+120*q); y=cy+math.sin(a)*(30+120*q)*0.35
        col=mix(VIOLET,GOLD,i/7); d.line((cx,cy,x,y),fill=(*col,int(170*q)),width=2)
        arrow(d,(cx+(x-cx)*0.85,cy+(y-cy)*0.85),(x,y),col,2,8)
        d.ellipse((x-6*q,y-6*q,x+6*q,y+6*q),fill=(*col,int(140*q)))
    seal(im,'DNA RECEPTION','DNA is not a blueprint - it is a receiver for cosmic information',VIOLET)''',
], [
    ("DNA Reception", "DNA is not a blueprint - it is a receiver for cosmic information.", 8.5, "vi_s_dna_reception"),
    ("The Cosmic Signal", "The universe transmits. Humanity is learning to receive a new frequency.", 9.0, "consciousness_field"),
    ("The Antenna is Evolving", "Human DNA is evolving to receive more of the signal. Awakening is biological.", 9.5, "dna_helix"),
])

augment("constructed_self_platinum.py", [
    r'''def vi_s_self_boundary(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    d.ellipse((cx-100*r,cy-80*r,cx+100*r,cy+80*r),outline=(*GOLD,int(200*r)),width=3)
    d.ellipse((cx-60*r,cy-48*r,cx+60*r,cy+48*r),outline=(*CYAN,int(160*r)),width=2)
    d.ellipse((cx-25*r,cy-20*r,cx+25*r,cy+20*r),outline=(*INK,int(140*r)),width=2)
    centered_text(d,(cx,cy-90*r),'THE SELF BOUNDARY',load_font(FONT_SANS_BOLD,int(h*0.022)),GOLD)
    centered_text(d,(cx,cy),'I',load_font(FONT_SERIF_BOLD,int(h*0.060)),(*INK,int(200*r)))
    seal(im,'THE SELF IS A BOUNDARY','the self is not a thing - it is the boundary between me and not-me',GOLD)''',
], [
    ("The Self is a Boundary", "The self is not a thing - it is the boundary between me and not-me.", 9.0, "vi_s_self_boundary"),
    ("The Self Extends", "Tools become part of the self. The car, the phone, the home - all self-model extensions.", 8.5, "self_model"),
    ("Healing the Boundary", "When the self-boundary softens, healing happens. The cage opens from the inside.", 9.5, "out_of_body"),
])

augment("cooperation_platinum.py", [
    r'''def vi_s_body_ecosystem(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(25):
        a=i*math.tau/25+r*0.3; rad=20+130*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        col=mix(GREEN,CYAN,i/24)
        sz=4+2*math.sin(i*1.5+t); d.ellipse((x-sz*r,y-sz*r,x+sz*r,y+sz*r),fill=(*col,int(150*r)))
        if i%3==0:
            d.line((cx,cy,x,y),fill=(*PALE_GREEN,int(80*r)),width=1)
    glow_circle(im,cx,cy,12,GREEN,int(200*r),10)
    seal(im,'THE BODY AS ECOSYSTEM','trillions of beings cooperate to form one body - you are a multitude',GREEN)''',
], [
    ("The Body as Ecosystem", "Trillions of beings cooperate to form one body - you are a multitude.", 9.0, "vi_s_body_ecosystem"),
    ("Every Cell is a Citizen", "Each cell contributes to the whole. The body is a perfect democracy.", 8.5, "cooperation_web"),
    ("Healing is Reconnection", "Disease is disconnection. Health is restored cooperation.", 9.5, "immune_dialogue"),
])
