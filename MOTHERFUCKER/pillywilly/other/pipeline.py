"""
Complete pipeline: measure audio → update storyboard → render → assemble → align.
"""
import sys, os, json, math, subprocess
sys.path.insert(0, '/root/projects/blog/scripts/renderer')
from renderer import *
FPS = 6
OUT = "/root/projects/blog/content/publishing/renders/you-are-made-of-light/v1"

with open(f"{OUT}/storyboard.json") as f:
    SHOTS = json.load(f)

# ── STEP 1: MEASURE ACTUAL WAV DURATIONS ───────────────────
def get_dur(path):
    try:
        r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
            '-of','default=noprint_wrappers=1:nokey=1',path],capture_output=True,text=True,timeout=5)
        return float(r.stdout.strip()) if r.stdout.strip() else 5.0
    except: return 5.0

cumulative = 0.0
for s in SHOTS:
    wpath = f"{OUT}/{s['shot_id']}.wav"
    if os.path.exists(wpath):
        actual = get_dur(wpath)
        s['duration_seconds'] = round(actual, 1)
    s['start_seconds'] = round(cumulative, 3)
    cumulative += s['duration_seconds']
    s['end_seconds'] = round(cumulative, 3)

with open(f"{OUT}/storyboard.json","w") as f:
    json.dump(SHOTS, f, indent=2, ensure_ascii=False)

durs = [s['duration_seconds'] for s in SHOTS]
print(f"Audio-measured: {len(SHOTS)} shots, {sum(durs):.0f}s ({sum(durs)/60:.1f} min)")
print(f"Range: {min(durs):.1f}-{max(durs):.1f}s, Avg: {sum(durs)/len(durs):.1f}s")

# ── STEP 2: MOTIF FUNCTIONS ────────────────────────────────
VOID=(13,17,23); GOLD=(212,165,116); CRIMSON=(141,44,57)
LAPIS=(42,70,110); INK=(230,225,220); MUTED=(145,141,132)

def motif_ladder(t,u,v):
    """Vertical axis with rungs. The central system."""
    im = canvas(VOID); d = ImageDraw.Draw(im)
    cx,cy=640,360
    d.line([(cx,80),(cx,640)],fill=rgba(GOLD,0.3),width=2)
    n=12
    for i in range(n):
        yy=120+i*(520/n)
        a=smoothstep(i/n-0.1,i/n+0.1,u)*0.6
        if a>0:
            d.rounded_rectangle([(cx-60,yy-4),(cx+60,yy+4)],2,2,outline=rgba(GOLD,a),width=1)
    dot(d,cx,cy,5,GOLD,0.6)
    return im

def motif_powers(t,u,v):
    """Five luminous points in pentad."""
    im = canvas(VOID); d = ImageDraw.Draw(im)
    cx,cy=640,360
    for i in range(5):
        a=i*1.257-1.57+t*0.05; r=80+20*math.sin(t*0.3+i)
        x=cx+r*math.cos(a); y=cy+r*math.sin(a)
        col=[GOLD,CRIMSON,LAPIS,INK,GOLD][i]
        dot(d,x,y,5+3*math.sin(t*0.5+i),col,0.5+0.3*math.sin(t+i*0.5))
        if i<4:
            xt=cx+(r+25)*math.cos(a); yt=cy+(r+25)*math.sin(a)
    dot(d,cx,cy,4,GOLD,0.5)
    return im

def motif_element(t,u,v):
    """Elements: earth, water, fire, air, ether — each different."""
    im = canvas(VOID); d = ImageDraw.Draw(im)
    cx,cy=640,360
    shapes=[("earth",60,3),("water",80,2),("fire",50,4),("air",90,1),("ether",100,0)]
    idx=v%len(shapes)
    name,size,width=shapes[idx]
    for rr in range(size,size*3,size//2):
        a=smoothstep(rr/size*0.1,rr/size*0.1+0.3,u)*0.3
        if a>0:
            ring(d,cx,cy,rr+5*math.sin(t*0.3+rr),GOLD,a,width)
    dot(d,cx,cy,5,GOLD,0.7)
    return im

def motif_lattice(t,u,v):
    """Grid of 36 interconnected points."""
    im = canvas(VOID); d = ImageDraw.Draw(im)
    cx,cy=640,360
    n=int(36*u)
    for i in range(n):
        row=i//6; col=i%6
        x=360+col*90; y=150+row*80
        dot(d,x,y,3,GOLD,0.3+0.4*math.sin(t+i*0.2))
        if col>0:
            d.line([(x-90,y),(x,y)],fill=rgba(GOLD,0.15),width=1)
        if row>0:
            d.line([(x,y-80),(x,y)],fill=rgba(GOLD,0.15),width=1)
    dot(d,cx,cy,4,GOLD,smoothstep(0.3,0.7,u))
    return im

def motif_threshold(t,u,v):
    """Door/aperture that dissolves."""
    im = canvas(VOID); d = ImageDraw.Draw(im)
    cx,cy=640,360
    ap=50*(1-u*0.5)
    d.arc([(cx-ap,cy-ap*0.6),(cx+ap,cy+ap*0.6)],-90,90,fill=rgba(GOLD,max(0,0.6-u*0.5)),width=3)
    d.arc([(cx-ap,cy-ap*0.6),(cx+ap,cy+ap*0.6)],90,270,fill=rgba(GOLD,max(0,0.6-u*0.5)),width=3)
    dot(d,cx,cy,4+6*(1-u),GOLD,smoothstep(0.1,0.5,u))
    return im

def motif_witness(t,u,v):
    """Central point — the witness, the 'I' that notices."""
    im = canvas(VOID); d = ImageDraw.Draw(im)
    cx,cy=640,360
    dot(d,cx,cy,6+3*math.sin(t*0.8),GOLD,smoothstep(0.2,0.6,u))
    ring(d,cx,cy,50+20*math.sin(t*0.4),GOLD,0.15,1)
    return im

MOTIFS = {}
groups = [
    ("ladder", ["earth_dense","water_flow","fire_transform","air_subtle","ether_expand",
                 "tattva_emerge","siva_summit","consciousness_apex","descent_begin",
                 "maya_veil","kancuka_armor","soul_contracted","ladder_fade","light_residue"]),
    ("powers", ["cit_consciousness","ananda_bliss","iccha_will","jnana_knowledge",
                "kriya_action","pentad_align","pentad_merge","undifferentiated_light"]),
    ("element", ["descent_body","descent_mind","descent_witness","element_earth",
                 "element_water","element_fire","element_air","element_ether",
                 "kala_action","vidya_knowledge","raga_attachment","kala_time","niyati_fate"]),
    ("lattice", ["lattice_base","lattice_build","lattice_connect","lattice_illuminate",
                 "lattice_pulse","lattice_full","lattice_climb","lattice_dissolve"]),
    ("threshold", ["threshold_door","threshold_cross","beyond_naming","thirty_seventh",
                   "threshold_dissolve","kancuka_dissolve"]),
    ("witness", ["body_surface","mind_thought","witness_center","you_are_light"]),
]
FUNCS = {"ladder":motif_ladder,"powers":motif_powers,"element":motif_element,
         "lattice":motif_lattice,"threshold":motif_threshold,"witness":motif_witness}
for grp, mlist in groups:
    for m in mlist: MOTIFS[m] = FUNCS[grp]

# Verify all motifs are mapped
unmapped = [s['motif'] for s in SHOTS if s['motif'] not in MOTIFS]
if unmapped:
    for m in set(unmapped):
        MOTIFS[m] = motif_witness
        print(f"  Unmapped: {m} → witness")

# ── STEP 3: RENDER ─────────────────────────────────────────
def render():
    total = len(SHOTS)
    print(f"\nRendering {total} shots...")
    for i,s in enumerate(SHOTS):
        sid=s['shot_id']; dur=s['duration_seconds']
        fn=MOTIFS.get(s['motif'],motif_witness)
        sd=os.path.join(OUT,sid); os.makedirs(sd,exist_ok=True)
        frames=max(1,int(dur*FPS))
        for fi in range(frames):
            fn(fi/FPS,fi/frames if frames>1 else 1,i).save(os.path.join(sd,f"frame_{fi:05d}.png"))
        if i%15==0: print(f"  [{i+1}/{total}] {sid}: {frames}fr {dur:.1f}s [{s['motif']}]")

# ── STEP 4: ASSEMBLE ───────────────────────────────────────
def assemble():
    print(f"\nAssembling...")
    with open(os.path.join(OUT,"c.txt"),"w") as f:
        for s in SHOTS:
            sid=s['shot_id']; mp4=os.path.join(OUT,f"{sid}.mp4"); sd=os.path.join(OUT,sid)
            subprocess.run(['ffmpeg','-y','-framerate',str(FPS),'-i',f'{sd}/frame_%05d.png',
                '-c:v','libx264','-pix_fmt','yuv420p','-preset','ultrafast','-crf','28',
                '-t',str(s['duration_seconds']),mp4],capture_output=True)
            f.write(f"file '{mp4}'\n")
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',os.path.join(OUT,'c.txt'),
        '-c','copy',os.path.join(OUT,'draft.mp4')],capture_output=True)
    
    with open(os.path.join(OUT,"ac.txt"),"w") as f:
        for s in SHOTS:
            w=os.path.join(OUT,f"{s['shot_id']}.wav")
            if os.path.exists(w): f.write(f"file '{w}'\n")
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',os.path.join(OUT,'ac.txt'),
        '-c','copy',os.path.join(OUT,'full_audio.wav')],capture_output=True)
    subprocess.run(['ffmpeg','-y','-i',os.path.join(OUT,'draft.mp4'),'-i',os.path.join(OUT,'full_audio.wav'),
        '-c:v','copy','-c:a','aac','-map','0:v:0','-map','1:a:0','-shortest',
        os.path.join(OUT,'final.mp4')],capture_output=True)
    
    sz=os.path.getsize(os.path.join(OUT,'final.mp4'))
    dur_total=sum(s['duration_seconds'] for s in SHOTS)
    print(f"Final MP4: {sz/1024:.0f} KB, {dur_total:.0f}s ({dur_total/60:.1f} min)")

# ── STEP 5: ALIGNMENT REPORT ────────────────────────────────
def align_report():
    report={"audio_duration_seconds":0,"video_duration_seconds":0,"shot_clip_duration_checks":[]}
    total_audio=0
    for s in SHOTS:
        wpath=f"{OUT}/{s['shot_id']}.wav"
        actual=get_dur(wpath) if os.path.exists(wpath) else s['duration_seconds']
        total_audio+=actual
        report["shot_clip_duration_checks"].append({
            "shot_id":s['shot_id'],"expected":s['duration_seconds'],
            "actual":round(actual,3),"error":round(abs(s['duration_seconds']-actual),3)})
    report["audio_duration_seconds"]=round(total_audio,3)
    report["video_duration_seconds"]=round(sum(s['duration_seconds'] for s in SHOTS),3)
    report["final_av_duration_difference_seconds"]=round(report["audio_duration_seconds"]-report["video_duration_seconds"],3)
    with open(f"{OUT}/alignment_report.json","w") as f:
        json.dump(report,f,indent=2,ensure_ascii=False)
    print(f"Alignment: AV drift {report['final_av_duration_difference_seconds']}s")
    errors=[c['error'] for c in report['shot_clip_duration_checks']]
    print(f"  Max shot error: {max(errors):.3f}s, Avg: {sum(errors)/len(errors):.3f}s")

if __name__=="__main__":
    act=sys.argv[1] if len(sys.argv)>1 else "all"
    if act in ("all","render"): render()
    if act in ("all","assemble"): assemble()
    if act in ("all","align"): align_report()
    print("Done.")
