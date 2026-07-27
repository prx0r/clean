#!/usr/bin/env python3
"""Final augmentation round for packs under 350 lines."""
import os, re, sys

PKG_DIR = "/root/projects/tantraloka/goldrender"

def augment(fname, extra_vis, extra_scenes):
    path = os.path.join(PKG_DIR, fname)
    text = open(path).read()
    
    if extra_vis:
        vis_marker = "\nVISUALS = {"
        idx = text.find(vis_marker)
        if idx > 0:
            insert = "\n\n" + "\n\n".join(extra_vis) + "\n"
            text = text[:idx] + insert + text[idx:]
    
    if extra_scenes:
        scenes_end = text.rfind("\n]")
        if scenes_end > 0:
            extra = "\n"
            for item in extra_scenes:
                t, n, d, v = item[0], item[1], item[2], item[3]
                p = item[4] if len(item) > 4 else {}
                ps = "{" + ", ".join(f'"{k}": "{v}"' if isinstance(v, str) else f'"{k}": {v}' for k, v in p.items()) + "}"
                extra += f'    Scene("{t}", "{n}", {d}, "{v}", {ps}),\n'
            extra += "\n"
            text = text[:scenes_end] + extra + text[scenes_end:]
    
    # Fix 'if' after semicolon (invalid Python)
    text = text.replace("; if q<=0: continue", "\n        if q<=0: continue")
    text = text.replace("; if q<=0:", "\n        if q<=0:")
    open(path, "w").write(text)
    l = text.count("\n"); s = text.count('Scene("'); v = len(re.findall(r'^def vis_', text, re.MULTILINE))
    print(f"  {fname}: {l}L {v}vis {s}scenes")
    return l

# Add richer vis functions for packs that need them
augment("svatantrya_freedom_platinum.py", [
    r'''def vis_freedom_contraction(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,20,GOLD,int(220*r),16)
    for i in range(6):
        q=clamp(r*6-i); if q<=0: continue
        rad=20+i*25; col=mix(GOLD,CRIMSON,i/5)
        d.ellipse((cx-rad*q,cy-rad*q*.6,cx+rad*q,cy+rad*q*.6),outline=(*col,int(200*q)),width=3)
        centered_text(d,(cx,cy-rad*q*.6-15),f'KANCUKA {i+1}',load_font(FONT_SANS_BOLD,int(h*0.017)),(*col,int(180*q)))
    seal(im,'FREEDOM CONTRACTS','freedom limits itself to experience limitation - the game of consciousness',GOLD)''',

    r'''def vis_absolute_freedom(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/50)*(30+140*r),cy+math.sin(i*math.tau/50)*(30+140*r)*0.35) for i in range(51)]
    glow_line(im,partial(pts,r),GOLD,width=5,alpha=240,blur=18)
    centered_text(d,(cx,cy),'SVATANTRYA',load_font(FONT_SERIF_BOLD,int(h*0.050)),(*GOLD,int(200*r)))
    if r>0.6:
        for i in range(15):
            a=i*math.tau/15+t*0.03; rad=40+140*r
            x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
            d.ellipse((x-3*r,y-3*r,x+3*r,y+3*r),fill=(*PALE_GOLD,int(150*r)))
    seal(im,'ABSOLUTE FREEDOM','not the freedom to choose - the freedom that IS choice itself',GOLD)''',
], [
    ("Freedom Contracts", "Freedom limits itself to experience limitation - the game of consciousness.", 8.5, "freedom_contraction"),
    ("Absolute Freedom", "Not the freedom to choose - the freedom that IS choice itself.", 9.5, "absolute_freedom"),
    ("The Free Witness", "Before every choice, there is the witness who is already free.", 9.0, "svatantrya_vis"),
    ("Bondage is a Choice", "What appears as bondage is freedom choosing to forget.", 9.0, "paradox_vis"),
])

augment("objects_as_actions_platinum.py", [
    r'''def vis_action_field(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(8):
        a=i*math.tau/8+t*0.06; q=clamp(r*4-i*0.08); if q<=0: continue
        x=cx+math.cos(a)*(30+110*q); y=cy+math.sin(a)*(30+110*q)*0.35
        col=mix(GOLD,CYAN,i/7)
        d.line((cx,cy,x,y),fill=(*col,int(170*q)),width=3)
        d.ellipse((x-8*q,y-8*q,x+8*q,y+8*q),fill=(*col,int(150*q)))
        if q>0.6: centered_text(d,(x,y+20*q),'ACT',load_font(FONT_SANS_BOLD,int(h*0.018)),col)
    seal(im,'THE ACTION FIELD','every point in space is a potential action - reality is the actualized',GOLD)''',

    r'''def vis_verb_world(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/40)*(30+120*r),cy+math.sin(i*math.tau/40)*(30+120*r)*0.35) for i in range(41)]
    glow_line(im,partial(pts,r),CYAN,width=4,alpha=210,blur=14)
    labels=['FLOWING','BECOMING','DANCING','SINGING','LOVING','KNOWING']
    for i,l in enumerate(labels):
        a=i*math.tau/len(labels)+t*0.05; q=clamp(r*6-i*0.08); if q<=0: continue
        x=cx+math.cos(a)*(40+100*q); y=cy+math.sin(a)*(40+100*q)*0.35
        centered_text(d,(x,y),l,load_font(FONT_SERIF,int(h*0.020)),(*GOLD,int(180*q)))
    seal(im,'THE VERB WORLD','reality is not made of things - it is made of actions we have learned to ignore',CYAN)''',
], [
    ("The Action Field", "Every point in space is a potential action. Reality is the actualized.", 8.5, "action_field"),
    ("The Verb World", "Reality is not made of things - it is made of actions we have learned to ignore.", 9.0, "verb_world"),
    ("The Dance of Shiva", "Creation and destruction are the same action at different speeds.", 9.0, "kriya_vis"),
    ("Knowing is Action", "To know is not to possess. It is to participate.", 9.0, "identity_vis"),
])

augment("psyche_gestalt_platinum.py", [
    r'''def vis_psyche_ocean(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for j in range(5):
        pts=[]
        for i in range(60):
            q=i/59; x=lerp(w*0.10,w*0.90,q)
            y=cy+math.sin(q*math.tau*(3+j*1.5)+t*1.5+r*math.tau)*(10+j*6)*r
            pts.append((x,y))
        col=mix(VIOLET,CYAN,j/4)
        glow_line(im,partial(pts,r),col,width=2,alpha=int(160-20*j)*r,blur=8+j)
    seal(im,'THE PSYCHE IS AN OCEAN','the surface is your conscious mind - the depths hold all that you are',VIOLET)''',

    r'''def vis_psyche_fulfillment(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,16,GOLD,int(200*r),14)
    for i in range(7):
        q=clamp(r*7-i); if q<=0: continue
        y=lerp(h*0.20,h*0.65,i/6); width=lerp(20,260,i/6)*q
        col=mix(VIOLET,GOLD,i/6)
        d.line((w*0.50-width/2,y,w*0.50+width/2,y),fill=(*col,int(180*q)),width=4)
        centered_text(d,(w*0.50,y-12),f'VALUE {i+1}',load_font(FONT_SANS_BOLD,int(h*0.016)),(*col,int(180*q)))
    seal(im,'VALUE FULFILLMENT','the psyche moves toward what enhances life - value is its compass',GOLD)''',
], [
    ("The Psyche is an Ocean", "The surface is your conscious mind - the depths hold all that you are.", 8.5, "psyche_ocean"),
    ("Value Fulfillment", "The psyche moves toward what enhances life - value is its compass.", 9.0, "psyche_fulfillment"),
    ("The Dreaming Creates the Waking", "Every night, the psyche designs the next day. Sleep is creative.", 8.5, "dreaming_vis"),
    ("Myth and Meaning", "The psyche speaks in myth because myth is the language of meaning.", 9.0, "gods_vis"),
])

augment("dna_antenna_platinum.py", [
    r'''def vis_dna_helix(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for j in range(2):
        off=j*math.pi; pts=[]
        for i in range(60):
            q=i/59; x=lerp(w*0.20,w*0.80,q)
            y=cy+math.sin(q*math.tau*4+off+r*math.tau)*(20+8*q)*r
            pts.append((x,y))
        col=CYAN if j==0 else GOLD
        glow_line(im,partial(pts,r),col,width=3,alpha=180,blur=10)
        for i in range(0,60,10):
            q=i/59; x=lerp(w*0.20,w*0.80,q)
            y=cy+math.sin(q*math.tau*4+off+r*math.tau)*(20+8*q)*r
            d.ellipse((x-4*r,y-4*r,x+4*r,y+4*r),fill=(*col,int(160*r)))
    seal(im,'THE DNA HELIX','a double helix of reception - each strand receives a different frequency',CYAN)''',

    r'''def vis_consciousness_field(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/40)*(30+130*r),cy+math.sin(i*math.tau/40)*(30+130*r)*0.35) for i in range(41)]
    glow_line(im,partial(pts,r),VIOLET,width=4,alpha=220,blur=14)
    for i in range(10):
        a=i*math.tau/10+t*0.04; q=clamp(r*4-i*0.06); if q<=0: continue
        x=cx+math.cos(a)*(30+120*q); y=cy+math.sin(a)*(30+120*q)*0.35
        d.line((cx,cy,x,y),fill=(*VIOLET,int(140*q)),width=2)
        glow_circle(im,x,y,4+2*q,PALE_VIOLET,int(130*q),6)
    seal(im,'THE CONSCIOUSNESS FIELD','consciousness is not produced by the brain - it is received through DNA',VIOLET)''',
], [
    ("The DNA Helix", "A double helix of reception - each strand receives a different frequency.", 8.5, "dna_helix"),
    ("The Consciousness Field", "Consciousness is not produced by the brain - it is received through DNA.", 9.0, "consciousness_field"),
    ("The Wave of Evolution", "Evolution is not random. It is guided by received frequency information.", 9.0, "frequency"),
    ("The Antenna of Humanity", "Humanity is an antenna for cosmic consciousness. DNA is the tuning fork.", 9.5, "antenna_vis"),
])

augment("constructed_self_platinum.py", [
    r'''def vis_self_model(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    d.ellipse((cx-60*r,cy-80*r,cx+60*r,cy+80*r),outline=(*GOLD,int(200*r)),width=3)
    d.ellipse((cx-40*r,cy-55*r,cx+40*r,cy+55*r),outline=(*CYAN,int(160*r)),width=2)
    d.ellipse((cx-20*r,cy-30*r,cx+20*r,cy+30*r),outline=(*INK,int(140*r)),width=2)
    labels=['NARRATIVE','BODILY','MINIMAL']
    for i,l in enumerate(labels):
        y=cy-70*r+i*50; col=[INK,CYAN,GOLD][i]
        centered_text(d,(cx-90*r,y),l,load_font(FONT_SANS_BOLD,int(h*0.020)),(*col,int(200*r)))
    seal(im,'THE SELF IS A MODEL','not a thing - a nested hierarchy of predictions about who you are',GOLD)''',

    r'''def vis_out_of_body(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    d.ellipse((cx-40,cy-60,cx+40,cy+60),outline=(*INK,int(180*(1-r))),width=4)
    d.ellipse((cx-30,cy-45,cx+30,cy+45),outline=(*SOFT_INK,int(120*(1-r))),width=2)
    if r>0.2:
        q=clamp((r-0.2)/0.8)
        px=cx; py=cy-80*q
        glow_circle(im,px,py,10,GOLD,int(200*q),8)
        d.line((cx,cy-60,px,py),fill=(*GOLD,int(150*q)),width=2)
        for i in range(4):
            a=i*math.tau/4; x=px+math.cos(a)*15*q; y=py+math.sin(a)*15*q
            d.line((px,py,x,y),fill=(*GOLD,int(120*q)),width=1)
    seal(im,'OUT-OF-BODY EXPERIENCE','the self can be displaced - proof that the self is not located in the body',GOLD)''',
], [
    ("The Self is a Model", "Not a thing - a nested hierarchy of predictions about who you are.", 9.0, "self_model"),
    ("Out-of-Body Experience", "The self can be displaced - proof that the self is not located in the body.", 8.5, "out_of_body"),
    ("The Bodily Self is Plastic", "Your body image can be updated in minutes. This is the mechanism of healing.", 8.5, "plasticity"),
    ("You Are Not in Your Body", "The body is in consciousness. The self is not located anywhere.", 9.5, "kancukas_self"),
])

augment("cooperation_platinum.py", [
    r'''def vis_cooperation_web(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(20):
        a=i*math.tau/20+r*0.5; rad=20+120*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*GREEN,int(160*r)))
        for j in range(3):
            aa=a+(j-1)*0.3; rr=rad*0.4
            xx=x+math.cos(aa)*rr; yy=y+math.sin(aa)*rr*0.4
            d.line((x,y,xx,yy),fill=(*PALE_GREEN,int(80*r)),width=1)
            d.ellipse((xx-2,yy-2,xx+2,yy+2),fill=(*CYAN,int(120*r)))
    seal(im,'THE WEB OF COOPERATION','every cell is connected to every other - the body is a network of gifts',GREEN)''',

    r'''def vis_immune_dialogue(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,14,GREEN,int(180*r),10)
    for i in range(12):
        a=i*math.tau/12+t*0.05; q=clamp(r*4-i*0.06); if q<=0: continue
        x=cx+math.cos(a)*(30+100*q); y=cy+math.sin(a)*(30+100*q)*0.35
        col=mix(CYAN,GREEN,i/11)
        d.line((cx,cy,x,y),fill=(*col,int(150*q)),width=2)
        d.ellipse((x-6*q,y-6*q,x+6*q,y+6*q),fill=(*col,int(140*q)))
        if q>0.7: centered_text(d,(x,y+15*q),f'CELL {i+1}',load_font(FONT_SANS_BOLD,int(h*0.014)),(*col,int(150*q)))
    seal(im,'THE IMMUNE DIALOGUE','the immune system is not an army - it is a conversation about identity',GREEN)''',
], [
    ("The Web of Cooperation", "Every cell is connected to every other - the body is a network of gifts.", 8.5, "cooperation_web"),
    ("The Immune Dialogue", "The immune system is not an army - it is a conversation about identity.", 8.5, "immune_dialogue"),
    ("The Gift Economy of Cells", "Cells give without counting. The body is a pure gift economy.", 9.0, "given_vis"),
    ("Cooperation is the Ground", "Competition is a special case of cooperation. The ground is always collaborative.", 9.5, "cooperation_vis"),
])

augment("time_is_forgetting_platinum.py", [], [
    ("The Spiral Memory", "Memory is not storage. It is a spiral that returns to the same point at a different level.", 8.5, "time_spiral"),
    ("The Pulse of Now", "Between heartbeats, between breaths, there is no time. Only the pulse of awareness.", 8.5, "spanda_pulse"),
    ("The Gift of Forgetting", "Forgetting is not a flaw. It is the condition of new experience.", 8.5, "forgetting"),
])
