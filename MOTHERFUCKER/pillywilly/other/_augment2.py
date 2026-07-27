#!/usr/bin/env python3
"""Add richer visual functions and more scenes to generated packs."""
import os, re

PKG_DIR = "/root/projects/tantraloka/goldrender"

def augment2(fname, extra_vis_funcs, extra_scenes):
    path = os.path.join(PKG_DIR, fname)
    text = open(path).read()
    
    # Add extra visual functions before VISUALS dict
    vis_marker = "\nVISUALS = {"
    idx = text.find(vis_marker)
    if idx > 0 and extra_vis_funcs:
        insert = "\n\n" + "\n\n".join(extra_vis_funcs) + "\n"
        text = text[:idx] + insert + text[idx:]
    
    # Add extra scenes before SCENES list end
    scenes_end = text.rfind("\n]")
    if scenes_end > 0 and extra_scenes:
        extra_text = "\n"
        for item in extra_scenes:
            title, narration, duration, visual = item[0], item[1], item[2], item[3]
            params = item[4] if len(item) > 4 else {}
            params_str = "{" + ", ".join(f'"{k}": "{v}"' if isinstance(v, str) else f'"{k}": {v}' for k, v in params.items()) + "}"
            extra_text += f'    Scene("{title}", "{narration}", {duration}, "{visual}", {params_str}),\n'
        extra_text += "\n"
        text = text[:scenes_end] + extra_text + text[scenes_end:]
    
    text = text.replace("; if q<=0: continue", "\n        if q<=0: continue")
    text = text.replace("; if q<=0:", "\n        if q<=0:")
    open(path, "w").write(text)
    lines = text.count("\n")
    scenes_count = text.count('Scene("')
    vis_count = len(re.findall(r'^def vis_', text, re.MULTILINE))
    print(f"  {fname}: {lines} lines, {vis_count} vis, {scenes_count} scenes")
    return lines, scenes_count

# ============================================================
# Richer visual functions for each pack
# ============================================================

# Morphospace - add form_cognition and landscape visuals
morphospace_vis = [
    r'''def vis_landscape(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[]
    for i in range(60):
        q=i/59; x=lerp(w*0.10,w*0.90,q)
        y=cy+math.sin(q*math.tau*3+r*math.tau)*30*math.exp(-((q-0.5)/0.2)**2)
        pts.append((x,y))
    glow_line(im,partial(pts,r),CYAN,width=3,alpha=180,blur=10)
    for i in range(5):
        a=i*math.tau/5+r*0.3; q=clamp(r*3-i*0.12); if q<=0: continue
        x=cx+math.cos(a)*(50+90*q); y=cy+math.sin(a)*(50+90*q)*0.35
        d.line((cx,cy,x,y),fill=(*GOLD,int(150*q)),width=2)
        glow_circle(im,x,y,6+3*r,GOLD,int(150*q),7)
    seal(im,'THE LANDSCAPE OF FORM','morphospace is a terrain with valleys of stable form',GOLD)''',
    
    r'''def vis_collective_field(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    r=ease(u); rng=random.Random(42)
    for i in range(20):
        a=i*math.tau/20+t*0.05; rad=30+100*r
        x=w*0.50+math.cos(a)*rad; y=h*0.42+math.sin(a)*rad*0.40
        for j in range(5):
            aa=a+j*math.tau/5; rr=rad*0.3
            xx=x+math.cos(aa)*rr; yy=y+math.sin(aa)*rr*0.4
            d.ellipse((xx-2,yy-2,xx+2,yy+2),fill=(*CYAN,int(100*r)))
        d.ellipse((x-6,y-6,x+6,y+6),fill=(*mix(CYAN,GREEN,0.5+0.5*math.sin(t+i)),int(160*r)))
    seal(im,'COLLECTIVE BIOELECTRIC FIELD','cells communicate through voltage - the body is a conversation',CYAN)''',

    r'''def vis_target_form(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    rad=60+40*math.sin(t*0.8)
    d.ellipse((cx-rad*r,cy-rad*r*0.6,cx+rad*r,cy+rad*r*0.6),outline=(*GOLD,int(200*r)),width=3)
    for i in range(12):
        a=i*math.tau/12+t*0.06; q=clamp(r*3-i*0.06); if q<=0: continue
        x=cx+math.cos(a)*(rad+50*q); y=cy+math.sin(a)*(rad+50*q)*0.5
        d.line((cx+math.cos(a)*rad*r,cy+math.sin(a)*rad*r*0.6,x,y),fill=(*GOLD,int(140*q)),width=2)
        glow_circle(im,x,y,4+2*q,PALE_GOLD,int(130*q),5)
    seal(im,'THE TARGET FORM','the organism navigates toward an attractor in morphospace',GOLD)''',
]

morphospace_scenes = [
    ("The Landscape of Form", "Morphospace is a terrain with valleys of stable form. Cells settle into attractors.", 8.5, "landscape"),
    ("Collective Bioelectric Field", "Cells communicate through voltage. The body is a conversation.", 8.0, "collective_field"),
    ("The Target Form", "The organism navigates toward an attractor in morphospace. Form is a destination.", 8.5, "target_form"),
    ("Every Cell Remembers", "Each cell carries the memory of the whole body. The field distributes the image.", 8.5, "memory"),
    ("Wound Healing as Navigation", "Healing is re-navigation. The cell finds its way back to the target form.", 9.0, "navigation"),
    ("The Body's Self-Image", "The bioelectric field is the body's self-representation. It is what the body thinks it is.", 9.0, "field"),
    ("Morphogenesis is Learning", "Building a body is a learning process. The organism learns its own shape.", 9.5, "landscape"),
]

# Free energy - add more visual functions
fep_vis = [
    r'''def vis_bayesian(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(3):
        q=clamp(r*3-i*0.1); if q<=0: continue
        y=lerp(h*0.28,h*0.58,i/2)
        col=mix(CYAN,GOLD,i/2)
        d.ellipse((w*0.50-60*q,y-25*q,w*0.50+60*q,y+25*q),outline=(*col,int(180*q)),width=2)
        centered_text(d,(w*0.50,y),f'LEVEL {i+1}',load_font(FONT_SANS_BOLD,int(h*0.025)),(*col,int(200*q)))
        d.line((w*0.50-40*q,y+28*q,w*0.50+40*q,y+28*q),fill=(*col,int(140*q)),width=2)
    seal(im,'THE BAYESIAN BRAIN','the brain is a hierarchical Bayesian inference engine',CYAN)''',

    r'''def vis_curiosity(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    glow_circle(im,cx,cy,14,GOLD,int(180*r),10)
    for i in range(10):
        a=i*math.tau/10+t*0.07; q=clamp(r*4-i*0.06); if q<=0: continue
        x=cx+math.cos(a)*(30+110*q); y=cy+math.sin(a)*(30+110*q)*0.35
        d.line((cx,cy,x,y),fill=(*CYAN,int(150*q)),width=2)
        d.ellipse((x-8*q,y-8*q,x+8*q,y+8*q),fill=(*PALE_CYAN,int(130*q)))
        arrow(d,(cx+(x-cx)*0.85,cy+(y-cy)*0.85),(x,y),CYAN,2,7)
    seal(im,'CURIOSITY IS EPISTEMIC VALUE','we seek information that resolves uncertainty - knowledge reduces free energy',CYAN)''',

    r'''def vis_self_organizing(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/40)*(30+120*r),cy+math.sin(i*math.tau/40)*(30+120*r)*0.35) for i in range(41)]
    glow_line(im,partial(pts,r),GOLD,width=4,alpha=220,blur=14)
    for i in range(6):
        a=i*math.tau/6+t*0.05; q=clamp(r*4-i*0.1); if q<=0: continue
        x=cx+math.cos(a)*(30+100*q); y=cy+math.sin(a)*(30+100*q)*0.35
        d.line((cx,cy,x,y),fill=(*GREEN,int(150*q)),width=2)
        glow_circle(im,x,y,5+3*r,GREEN,int(140*q),6)
    seal(im,'SELF-ORGANIZATION','order emerges from the minimization of free energy at every scale',GOLD)''',
]

fep_scenes = [
    ("The Bayesian Brain", "The brain is a hierarchical Bayesian inference engine. Perception is belief updating.", 8.5, "bayesian"),
    ("Curiosity is Epistemic Value", "We seek information that resolves uncertainty. Knowledge reduces free energy.", 8.5, "curiosity"),
    ("Self-Organization", "Order emerges from the minimization of free energy at every scale.", 9.0, "self_organizing"),
    ("The Variational Free Energy", "Free energy is a bound on surprise. All life is variational inference.", 8.5, "principle"),
    ("Models are All We Have", "Every organism is a model. To be alive is to generate predictions.", 9.0, "prediction"),
    ("Action Shapes Perception", "What we do changes what we see. Active inference closes the loop.", 8.5, "active"),
    ("Precision and Attention", "Attention is precision weighting. It selects which prediction errors matter.", 8.5, "precision"),
]

# Consciousness container
cc_vis = [
    r'''def vis_tattvas_wheel(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for i in range(12):
        a=i*math.tau/12+t*0.04; q=clamp(r*6-i*0.04); if q<=0: continue
        rad=20+110*q; x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        col=mix(GOLD,INK,i/11)
        d.line((cx,cy,x,y),fill=(*col,int(150*q)),width=2)
        d.ellipse((x-8*q,y-8*q,x+8*q,y+8*q),outline=(*col,int(160*q)),width=2)
        centered_text(d,(x,y+15*q),str(i+1),load_font(FONT_SANS_BOLD,int(h*0.016)),col)
    seal(im,'THE WHEEL OF TATTVAS','twelve principles of consciousness - from Shiva to the elements',GOLD)''',

    r'''def vis_iccha_jnana_kriya(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    labels=['ICCHA','JNANA','KRIYA']
    for i,l in enumerate(labels):
        a=i*math.tau/3+t*0.06; q=clamp(r*3-i*0.12); if q<=0: continue
        x=cx+math.cos(a)*100*q; y=cy+math.sin(a)*100*q
        col=[GOLD,CYAN,VIOLET][i]
        glow_circle(im,x,y,12+6*q,col,int(190*q),9)
        d.line((cx,cy,x,y),fill=(*col,int(150*q)),width=3)
        centered_text(d,(x,y+22*q),l,load_font(FONT_SANS_BOLD,int(h*0.022)),col)
    seal(im,'ICCHA-JNANA-KRIYA','will, knowledge, and action - the three powers of consciousness',GOLD)''',
]

cc_scenes = [
    ("The Wheel of Tattvas", "Twelve principles of consciousness - from Shiva to the elements.", 8.5, "tattvas_wheel"),
    ("Iccha-Jnana-Kriya", "Will, knowledge, and action - the three powers of consciousness.", 8.5, "iccha_jnana_kriya"),
    ("Consciousness is One", "The 36 tattvas are not separate things. They are facets of one consciousness.", 9.0, "realization"),
    ("The Mirror of Maya", "Maya reflects the infinite back to itself as finite experience.", 8.5, "maya"),
    ("The Five Powers of Shiva", "Creation, preservation, dissolution, veiling, grace. One act, five names.", 9.0, "sakti"),
    ("The Universe is Your Body", "Shiva's body is the universe. Your body is a universe.", 9.5, "consciousness_final"),
]

# Time is forgetting
tif_vis = [
    r'''def vis_eternal_return(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/50*r*4)*(30+120*r),cy+math.sin(i*math.tau/50*r*4)*(30+120*r)*0.35) for i in range(51)]
    glow_line(im,partial(pts,r),GOLD,width=4,alpha=220,blur=14)
    for i in range(8):
        a=i*math.tau/8+t*0.05; rad=40+100*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35
        d.ellipse((x-4*r,y-4*r,x+4*r,y+4*r),fill=(*PALE_GOLD,int(140*r)))
        d.line((cx,cy,x,y),fill=(*CYAN,int(130*r)),width=2)
    seal(im,'ETERNAL RETURN','not that events repeat - that every moment contains all moments',GOLD)''',

    r'''def vis_time_wave(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for j in range(3):
        pts=[]
        for i in range(80):
            q=i/79; x=lerp(w*0.10,w*0.90,q)
            y=cy+math.sin(q*math.tau*(3+j*2)+t*2+r*math.tau)*(15+10*j)*r
            pts.append((x,y))
        glow_line(im,partial(pts,r),mix(CYAN,GOLD,j/2),width=2+j,alpha=int(160-20*j)*r,blur=8+2*j)
    seal(im,'THE WAVE OF TIME','time is not a line - it is a wave interference pattern',CYAN)''',
]

tif_scenes = [
    ("Eternal Return", "Not that events repeat - that every moment contains all moments.", 9.0, "eternal_return"),
    ("The Wave of Time", "Time is not a line - it is a wave interference pattern.", 8.5, "time_wave"),
    ("The Eye of the Now", "The present is not a point. It is a field of infinite depth.", 9.0, "now_vis"),
    ("Attention Creates Sequence", "Without attention, all moments coexist. Attention strings them into time.", 8.5, "spanda_pulse"),
    ("Forgetting is Compassion", "Could you bear to remember every moment? Forgetting is mercy.", 8.5, "forgetting"),
]

# Svatantrya
svt_vis = [
    r'''def vis_freedom_field(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/40)*(30+130*r),cy+math.sin(i*math.tau/40)*(30+130*r)*0.35) for i in range(41)]
    glow_line(im,partial(pts,r),GOLD,width=5,alpha=230,blur=16)
    for i in range(12):
        a=i*math.tau/12+t*0.04; q=clamp(r*4-i*0.05); if q<=0: continue
        x=cx+math.cos(a)*(40+120*q); y=cy+math.sin(a)*(40+120*q)*0.35
        d.line((cx,cy,x,y),fill=(*GOLD,int(140*q)),width=1)
        glow_circle(im,x,y,3+2*q,PALE_GOLD,int(120*q),5)
    seal(im,'THE FIELD OF FREEDOM','before any law, before any form, there is the freedom that chooses',GOLD)''',
]

svt_scenes = [
    ("The Field of Freedom", "Before any law, before any form, there is the freedom that chooses.", 9.0, "freedom_field"),
    ("Freedom is Not a Choice", "Choice is an expression of freedom. Freedom is not itself chosen.", 9.0, "svatantrya_vis"),
    ("The Constraint is a Gift", "Limitation is not the enemy of freedom. It is freedom's canvas.", 9.0, "paradox_vis"),
    ("Acting from Freedom", "When you know you are free, action becomes effortless.", 8.5, "living_vis"),
]

# objects_as_actions
oaa_vis = [
    r'''def vis_wave_particle(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[]
    for i in range(100):
        q=i/99; x=lerp(w*0.10,w*0.90,q)
        amp=(40-30*q)*r; y=cy+math.sin(q*math.tau*6+t*3)*amp
        pts.append((x,y))
    glow_line(im,partial(pts,r),CYAN,width=3,alpha=180,blur=12)
    if r>0.6:
        q=(r-0.6)/0.4; cx2=w*0.50
        for j in range(5):
            a=j*math.tau/5; rad=80*q; x2=cx2+math.cos(a)*rad; y2=cy+math.sin(a)*rad*0.35
            d.ellipse((x2-8*q,y2-8*q,x2+8*q,y2+8*q),fill=(*GOLD,int(200*q)))
    seal(im,'WAVE AND PARTICLE','action is the wave - the object is the particle. Both are real',CYAN)''',
]

oaa_scenes = [
    ("Wave and Particle", "Action is the wave - the object is the particle. Both are real.", 8.5, "wave_particle"),
    ("The Verb is the Substance", "The noun names the frozen verb. The verb is the living reality.", 8.5, "kriya_vis"),
    ("Attention is Action", "To attend is to act. Perception is not passive - it is a creative act.", 8.5, "perception_vis"),
    ("The Action of Being", "Existence is not a state. It is the most fundamental act.", 9.0, "identity_vis"),
]

# psyche_gestalt
pg_vis = [
    r'''def vis_psi_field(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    pts=[(cx+math.cos(i*math.tau/40)*(20+130*r),cy+math.sin(i*math.tau/40)*(20+130*r)*0.35) for i in range(41)]
    glow_line(im,partial(pts,r),VIOLET,width=4,alpha=210,blur=14)
    for i in range(8):
        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.08); if q<=0: continue
        x=cx+math.cos(a)*(30+110*q); y=cy+math.sin(a)*(30+110*q)*0.35
        col=mix(VIOLET,GOLD,i/7)
        d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)
        glow_circle(im,x,y,5+3*r,col,int(150*q),7)
    seal(im,'THE PSYCHIC FIELD','the psyche is a field, not a thing - it extends beyond the individual',VIOLET)''',
]

pg_scenes = [
    ("The Psychic Field", "The psyche is a field, not a thing - it extends beyond the individual.", 8.5, "psi_field"),
    ("Dreams are Real", "The dreaming psyche navigates realities as real as the waking one.", 8.5, "dreaming_vis"),
    ("Energy Never Dies", "The psyche is energy. Energy transforms but does not cease.", 9.0, "energy_vis"),
    ("Myth is Psychic Truth", "Myths are not fiction. They are the psyche's autobiography.", 9.0, "gods_vis"),
]

# dna_antenna
dna_vis = [
    r'''def vis_frequency(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    for j in range(3):
        pts=[]
        for i in range(80):
            q=i/79; x=lerp(w*0.10,w*0.90,q); freq=4+j*2
            y=cy+math.sin(q*math.tau*freq+r*t)*15*(1+j*0.3)*r
            pts.append((x,y))
        col=mix(CYAN,GOLD,j/2)
        glow_line(im,partial(pts,r),col,width=3-j,alpha=int(180-40*j)*r,blur=10-2*j)
    seal(im,'FREQUENCY IS INFORMATION','DNA receives different frequencies - each frequency is a different reality',GOLD)''',
]

dna_scenes = [
    ("Frequency is Information", "DNA receives different frequencies - each frequency is a different reality.", 8.5, "frequency"),
    ("The Wave Carries Form", "The wave is the carrier of form. DNA translates wave into structure.", 9.0, "strands"),
    ("Consciousness is the Transmitter", "You do not generate thought. You receive it from the field.", 9.0, "transceiver"),
    ("Repairing Reception", "The work of awakening is clearing the interference on the line.", 9.5, "antenna_vis"),
]

# constructed_self
cs_vis = [
    r'''def vis_rubber_hand_full(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    d.ellipse((cx-120*r,cy-25*r,cx-30*r,cy+25*r),outline=(*INK,int(200*r)),width=4)
    d.ellipse((cx+30*r,cy-25*r,cx+120*r,cy+25*r),outline=(*GOLD,int(200*r)),width=4)
    for i in range(5):
        a=i*0.3-0.6; x1=cx-75*r+math.cos(a)*25; y1=cy-25*r+math.sin(a)*10
        x2=cx+75*r+math.cos(a)*25; y2=cy-25*r+math.sin(a)*10
        d.line((x1,y1,x2,y2),fill=(*CYAN,int(140*r)),width=3)
    if r>0.4:
        q=(r-0.4)/0.6; glow_circle(im,cx,cy,12,GOLD,int(200*q),10)
        centered_text(d,(cx,cy-50*q),'MINE',load_font(FONT_SERIF_BOLD,int(h*0.045)),(*GOLD,int(200*q)))
    seal(im,'THE RUBBER HAND ILLUSION','stroking a fake hand makes it yours - the self extends into what it touches',INK)''',
]

cs_scenes = [
    ("The Rubber Hand Illusion", "Stroking a fake hand makes it yours - the self extends into what it touches.", 8.0, "rubber_hand_full"),
    ("The Self is a Boundary", "The self is not a thing. It is the boundary of the model.", 9.0, "kancukas_self"),
    ("Empathy is Model Extension", "You feel another's pain because your self-model can extend to include them.", 9.0, "swap"),
    ("The Flexible Self", "The self-model can be updated. This is the mechanism of growth.", 9.5, "plasticity"),
]

# cooperation
coop_vis = [
    r'''def vis_cell_society(im,u,t,p):
    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)
    rng=random.Random(42)
    pts=[]
    for i in range(30):
        a=rng.uniform(0,math.tau); rad=rng.uniform(20,130)*r
        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.4
        col=CYAN if rng.random()<0.4 else (GREEN if rng.random()<0.7 else GOLD)
        sz=rng.uniform(3,7)*r
        d.ellipse((x-sz,y-sz,x+sz,y+sz),fill=(*col,int(180*r)))
        pts.append((x,y))
    if len(pts)>5:
        for i in range(0,len(pts)-1,2):
            d.line((*pts[i],*pts[i+1]),fill=(*PALE_SILVER,int(60*r)),width=1)
    glow_circle(im,cx,cy,10,GREEN,int(180*r),9)
    seal(im,'THE CELL SOCIETY','the body is a society of trillions - cooperation is the constitution',GREEN)''',
]

coop_scenes = [
    ("The Cell Society", "The body is a society of trillions - cooperation is the constitution.", 9.0, "cell_society"),
    ("The Common Good", "Each cell contributes to the whole. The common good is cellular.", 8.5, "cooperation_vis"),
    ("Trust is Biological", "Cells trust each other. That trust is the foundation of health.", 8.5, "faith_cell"),
    ("The Cooperative Venture", "You are not one thing. You are a cooperation that learned to say 'I'.", 9.5, "cooperation_vis"),
]

# Run all augmentations
results = []
augmentations = [
    ("morphospace_navigation_platinum.py", morphospace_vis, morphospace_scenes),
    ("free_energy_primitive_platinum.py", fep_vis, fep_scenes),
    ("consciousness_container_platinum.py", cc_vis, cc_scenes),
    ("time_is_forgetting_platinum.py", tif_vis, tif_scenes),
    ("svatantrya_freedom_platinum.py", svt_vis, svt_scenes),
    ("objects_as_actions_platinum.py", oaa_vis, oaa_scenes),
    ("psyche_gestalt_platinum.py", pg_vis, pg_scenes),
    ("dna_antenna_platinum.py", dna_vis, dna_scenes),
    ("constructed_self_platinum.py", cs_vis, cs_scenes),
    ("cooperation_platinum.py", coop_vis, coop_scenes),
    # Also augment the first 5 manual packs with extra scenes
    ("spacious_present_platinum.py", [], [
        ("The Spiral of Attention", "Where attention goes, time unfolds. You create time by attending.", 8.0, "attention"),
        ("The Observer of Time", "Who watches the passage of time is not in time.", 9.0, "self_remember"),
    ]),
    ("you_create_reality_platinum.py", [], [
        ("The Mirror of Belief", "What you believe is what you see. Change the belief, change the world.", 8.0, "belief"),
        ("The Creator's Responsibility", "If you create it, you can change it. Healing begins with ownership.", 8.5, "responsibility"),
    ]),
    ("veils_of_forgetting_platinum.py", [], [
        ("The Veil as Mercy", "The veil is not a punishment. It is the soul's gift to itself.", 8.5, "veil"),
        ("Lifting the Veil", "Awakening is not force. It is the natural rising of the sun.", 9.0, "piercing"),
    ]),
    ("daimon_encounter_platinum.py", [], [
        ("The Daimon is You", "What you meet at the threshold is your own deeper self.", 8.5, "encounter"),
        ("Living the Daimonic Life", "When the daimon is integrated, every act becomes sacred.", 9.0, "union"),
    ]),
    ("dream_incubation_platinum.py", [], [
        ("The Dream is the Answer", "The dream does not need interpretation. It IS the interpretation.", 8.5, "core"),
        ("Incubation as Practice", "Nightly practice. The daimon responds to consistency.", 8.5, "practice"),
    ]),
]

for fname, vis_funcs, scenes in augmentations:
    result = augment2(fname, vis_funcs, scenes)
    results.append(result)

print("\n=== Final Stats ===")
total_l = total_s = total_v = 0
for fname, _, _ in augmentations:
    text = open(os.path.join(PKG_DIR, fname)).read()
    lines = text.count("\n")
    scenes = text.count('Scene("')
    vis = len(re.findall(r'^def vis_', text, re.MULTILINE))
    print(f"  {fname}: {lines} lines, {vis} vis, {scenes} scenes")
    total_l += lines; total_v += vis; total_s += scenes
print(f"  TOTAL: {total_l} lines, {total_v} vis, {total_s} scenes")
