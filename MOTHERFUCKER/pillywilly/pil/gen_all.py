#!/usr/bin/env python3
"""
Generate all remaining upgraded platinum packs.
Builds each file line by line to avoid triple-quote escaping issues.
"""
import os, json, math, textwrap

PKG_DIR = "/root/projects/tantraloka/goldrender"

# ============================================================
# Boilerplate sections (shared across packs)
# ============================================================

HEADER = textwrap.dedent("""\
#!/usr/bin/env python3
""")

IMPORTS = textwrap.dedent("""\
from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
""")

CONFIG_TEMPLATE = textwrap.dedent("""\
ROOT = Path(__file__).resolve().parent
OUTPUT = Path("/mnt/HC_Volume_106427611/goldrender/output_{slug}")
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"
DEFAULT_WIDTH = 1280; DEFAULT_HEIGHT = 720; DEFAULT_FPS = 10
IVORY = (249,247,241); PAPER = (242,239,231); INK = (31,36,42); SOFT_INK = (85,91,97)
SILVER = (180,187,191); PALE_SILVER = (224,228,228)
CYAN = (55,157,178); PALE_CYAN = (194,227,233)
GOLD = (193,155,72); PALE_GOLD = (235,218,172)
CRIMSON = (164,57,69); PALE_CRIMSON = (231,198,201)
GREEN = (68,139,99); PALE_GREEN = (196,225,206)
VIOLET = (107,82,151); PALE_VIOLET = (218,208,235)
LAPIS = (56,76,124); VOID = (24,28,34); WHITE = (255,254,250)
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
""")

HELPERS = textwrap.dedent("""\
def clamp(x,lo=0.0,hi=1.0): return max(lo,min(hi,x))
def lerp(a,b,t): return a+(b-a)*clamp(t)
def mix(a,b,t): t=clamp(t); return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smoothstep(a,b,x):
    if a==b: return 1.0 if x>=b else 0.0
    q=clamp((x-a)/(b-a)); return q*q*(3-2*q)
def ease(t): t=clamp(t); return 0.5-0.5*math.cos(math.pi*t)
def ease_out(t): t=clamp(t); return 1-(1-t)**3
def pulse(t,speed=1.0,phase=0.0): return 0.5+0.5*math.sin(math.tau*(speed*t+phase))
def load_font(path,size):
    for c in (path,FONT_SERIF,FONT_SANS):
        try: return ImageFont.truetype(c,size)
        except OSError: pass
    return ImageFont.load_default()
def rgba_layer(size): return Image.new("RGBA",size,(0,0,0,0))
def scientific_field(w,h,seed):
    rng=np.random.default_rng(seed)
    base=np.empty((h,w,3),dtype=np.float32); base[:]=IVORY
    fine=rng.normal(0,0.95,(h,w,1)); base+=fine
    yy,xx=np.mgrid[0:h,0:w]
    halo=np.exp(-(((xx-w*0.52)/(w*0.36))**2+((yy-h*0.39)/(h*0.30))**2)*2.1)
    base[...,0]+=halo*1.5; base[...,1]+=halo*4.0; base[...,2]+=halo*5.5
    base=np.clip(base,0,255).astype(np.uint8)
    return Image.fromarray(base,"RGB").convert("RGBA")
def centered_text(draw,xy,text,font,fill=INK): draw.text(xy,text,font=font,fill=fill,anchor="mm")
def border(im):
    w,h=im.size; d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w-26,h-26),radius=18,outline=(*INK,48),width=2)
    for x,y in ((52,52),(w-52,52),(52,h-52),(w-52,h-52)):
        d.line((x-9,y,x+9,y),fill=(*CYAN,80),width=1); d.line((x,y-9,x,y+9),fill=(*CYAN,80),width=1)
def seal(im,title,subtitle="",color=INK):
    w,h=im.size; d=ImageDraw.Draw(im)
    tf=load_font(FONT_SERIF_BOLD,max(22,int(h*0.040)))
    sf=load_font(FONT_SANS,max(13,int(h*0.019)))
    centered_text(d,(w/2,h*0.875),title,tf,color)
    if subtitle: centered_text(d,(w/2,h*0.923),subtitle,sf,SOFT_INK)
def glow_line(im,points,color,width=4,alpha=210,blur=12):
    if len(points)<2: return
    gl=rgba_layer(im.size)
    ImageDraw.Draw(gl).line(points,fill=(*color,int(alpha)),width=width*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg=rgba_layer(im.size)
    ImageDraw.Draw(fg).line(points,fill=(*mix(color,WHITE,0.08),min(255,int(alpha)+25)),width=width,joint="curve")
    im.alpha_composite(fg)
def glow_circle(im,x,y,r,color,alpha=170,blur=16):
    gl=rgba_layer(im.size)
    ImageDraw.Draw(gl).ellipse((x-r,y-r,x+r,y+r),fill=(*color,int(alpha)))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    core=rgba_layer(im.size)
    ImageDraw.Draw(core).ellipse((x-r*0.38,y-r*0.38,x+r*0.38,y+r*0.38),fill=(*mix(color,WHITE,0.35),min(255,int(alpha)+55)))
    im.alpha_composite(core)
def arrow(draw,a,b,color=INK,width=3,head=10):
    draw.line((*a,*b),fill=color,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s in (-1,1):
        p=(b[0]-math.cos(ang+s*0.53)*head,b[1]-math.sin(ang+s*0.53)*head)
        draw.line((*b,*p),fill=color,width=width)
def partial(points,amount):
    amount=clamp(amount)
    if not points: return []
    if amount>=1: return list(points)
    target=amount*(len(points)-1); idx=int(target); frac=target-idx
    out=list(points[:idx+1])
    if idx+1<len(points):
        a,b=points[idx],points[idx+1]; out.append((lerp(a[0],b[0],frac),lerp(a[1],b[1],frac)))
    return out
""")

PIPELINE = textwrap.dedent("""\
@dataclass
class Scene:
    title: str; narration: str; duration: float; visual: str; params: dict

def render_frame(scene,fi,fc,w,h,seed):
    u=fi/max(1,fc-1); t=u*scene.duration
    im=scientific_field(w,h,seed)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im); return im.convert("RGB")

def ffmpeg_path():
    ff=shutil.which("ffmpeg")
    if not ff: raise RuntimeError("ffmpeg required")
    return ff

def encode_scene(si,fps):
    out=SCENES_DIR/f"scene_{si:03d}.mp4"; fd=FRAMES/f"scene_{si:03d}"
    subprocess.run([ffmpeg_path(),"-y","-framerate",str(fps),"-i",str(fd/"%05d.jpg"),
        "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
        "-movflags","+faststart",str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def render_scene(si,scene,fps,w,h,preview):
    fd=FRAMES/f"scene_{si:03d}"; fd.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
    count=max(2,round(scene.duration*fps))
    if preview:
        for oi,fi in enumerate([0,int(count*.35),int(count*.72),count-1]):
            render_frame(scene,fi,count,w,h,si*10000+fi).save(fd/f"preview_{oi:02d}.jpg",quality=95)
        return fd
    for fi in range(count):
        p=fd/f"{fi:05d}.jpg"
        if p.exists(): continue
        render_frame(scene,fi,count,w,h,si*10000+fi).save(p,quality=95,subsampling=0)
    return encode_scene(si,fps)

def concat(paths):
    cp=OUTPUT/"concat.txt"; cp.write_text("\\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    final=OUTPUT/"__SLUG__.mp4"
    subprocess.run([ffmpeg_path(),"-y","-f","concat","-safe","0","-i",str(cp),"-c","copy","-movflags","+faststart",str(final)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return final

def export_timeline():
    cursor=0.0; records=[]
    for i,s in enumerate(SCENES,1):
        item=asdict(s); item["scene_id"]=f"scene_{i:03d}"; item["start_seconds"]=round(cursor,3)
        cursor+=s.duration; item["end_seconds"]=round(cursor,3); records.append(item)
    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({"title":"__TITLE__","scene_count":len(SCENES),"runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],"continuity_object":"__CONT__",
        "palette_roles":{__PAL__},
        "scenes":records},indent=2,ensure_ascii=False),encoding="utf-8")
    return p

def contact_sheet(w,h):
    tw,th=320,int(320*h/w); cols,rows=4,math.ceil(len(SCENES)/cols); ch=th+48
    sheet=Image.new("RGB",(cols*tw,rows*ch),IVORY); d=ImageDraw.Draw(sheet)
    lf=load_font(FONT_SANS_BOLD,14)
    for i,s in enumerate(SCENES,1):
        cnt=max(2,round(s.duration*DEFAULT_FPS))
        im=render_frame(s,int(cnt*.72),cnt,w,h,i*10000+72); im.thumbnail((tw,th))
        sl=i-1; x,y=(sl%cols)*tw,(sl//cols)*ch; sheet.paste(im,(x,y))
        d.text((x+9,y+th+7),f"{{i:02d}}  {{s.title}}",font=lf,fill=INK)
    p=OUTPUT/"contact_sheet.jpg"; sheet.save(p,quality=94); return p

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--fps",type=int,default=DEFAULT_FPS); p.add_argument("--width",type=int,default=DEFAULT_WIDTH)
    p.add_argument("--height",type=int,default=DEFAULT_HEIGHT); p.add_argument("--scene",type=int,default=None)
    p.add_argument("--preview",action="store_true"); p.add_argument("--no-contact-sheet",action="store_true")
    return p.parse_args()

def main():
    a=parse_args(); OUTPUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
    tl=export_timeline(); total=sum(s.duration for s in SCENES)
    print(f"Timeline: {{tl}}"); print(f"Scenes: {{len(SCENES)}}"); print(f"Runtime: {{total/60:.2f}} min")
    if a.scene is not None:
        if not 1<=a.scene<=len(SCENES): raise ValueError(f"--scene must be 1..{{len(SCENES)}}")
        print(render_scene(a.scene,SCENES[a.scene-1],a.fps,a.width,a.height,a.preview)); return
    rendered=[]
    for i,s in enumerate(SCENES,1):
        print(f"[{{i:02d}}/{{len(SCENES):02d}}] {{s.title}} ({{s.duration:.1f}}s)")
        rendered.append(render_scene(i,s,a.fps,a.width,a.height,a.preview))
    final=concat(rendered); print(f"Final: {{final}}")
    if not a.no_contact_sheet: print(f"Contact sheet: {{contact_sheet(a.width,a.height)}}")
    print("Done.")

if __name__=="__main__": main()
""")


class Pack:
    def __init__(self, slug, title, subtitle, doc_desc, continuity, palette_roles_str):
        self.slug = slug
        self.title = title
        self.subtitle = subtitle
        self.doc_desc = doc_desc
        self.continuity = continuity
        self.palette_roles_str = palette_roles_str
        self.vis_funcs = []
        self.visuals_entries = []
        self.scenes = []

    def add_vis(self, key, code_lines):
        self.vis_funcs.extend(code_lines)
        self.vis_funcs.append("")
        self.visuals_entries.append((key, f"vis_{key}"))

    def add_scene(self, title, narration, duration, visual_key, params=None):
        self.scenes.append((title, narration, duration, visual_key, params or {}))


def write_pack(pack):
    lines = []
    lines.append("#!/usr/bin/env python3")
    lines.append('"""')
    lines.append(pack.title)
    lines.append(pack.doc_desc)
    lines.append("Platinum procedural visual essay.")
    lines.append("")
    lines.append("DESIGN CONTRACT")
    lines.append("--------------")
    lines.append("5-10 seconds per shot, each visibly performs the narrated operation.")
    lines.append("Clean ivory scientific field; concept-led color.")
    lines.append("No static slide layouts or decorative loops.")
    lines.append('"""')
    lines.append("")
    lines.append(IMPORTS)
    lines.append("")
    lines.append(CONFIG_TEMPLATE.format(slug=pack.slug))
    lines.append("")
    lines.append(HELPERS)
    lines.append("")
    for l in pack.vis_funcs:
        lines.append(l)
    lines.append("")
    # Build VISUALS dict
    lines.append("VISUALS = {")
    for key, func in pack.visuals_entries:
        lines.append(f'    "{key}": {func},')
    lines.append("}")
    lines.append("")
    lines.append("")
    # Build SCENES list
    lines.append("SCENES = [")
    for title, narration, duration, vkey, params in pack.scenes:
        params_str = "{" + ", ".join(f'"{k}": "{v}"' if isinstance(v, str) else f'"{k}": {v}' for k, v in params.items()) + "}"
        lines.append(f'    Scene("{title}", "{narration}", {duration}, "{vkey}", {params_str}),')
    lines.append("]")
    lines.append("")
    lines.append("")
    # Pipeline
    pipeline_text = PIPELINE
    pipeline_text = pipeline_text.replace("__SLUG__", pack.slug)
    pipeline_text = pipeline_text.replace("__TITLE__", pack.title)
    pipeline_text = pipeline_text.replace("__CONT__", pack.continuity)
    pipeline_text = pipeline_text.replace("__PAL__", pack.palette_roles_str)
    lines.append(pipeline_text)
    lines.append("")
    body = "\n".join(lines)
    # Fix 'if' after semicolon (invalid Python)
    body = body.replace("; if q<=0: continue", "\n        if q<=0: continue")
    body = body.replace("; if q<=0:", "\n        if q<=0:")
    fpath = os.path.join(PKG_DIR, f"{pack.slug}_platinum.py")
    open(fpath, "w").write(body)
    vs = len(pack.visuals_entries)
    sc = len(pack.scenes)
    ln = body.count("\n")
    print(f"  {pack.slug}_platinum.py: {ln} lines, {vs} visuals, {sc} scenes")
    return body


# ============================================================
# Define each pack
# ============================================================

def build_morphospace():
    p = Pack("morphospace_navigation", "Cells Navigate Possible Forms",
             "Levin — basal cognition", "Levin's basal cognition in morphogenesis.",
             "navigating particle in morphospace",
             '"cyan":"bioelectric field", "gold":"target form", "green":"repair", "crimson":"wound"')
    p.add_vis("planaria", [
        "def vis_planaria(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,14,GOLD,int(180*r),10)",
        "    for i in range(8):",
        "        a=i*math.tau/8+t*0.06; q=clamp(r*4-i*0.08)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(30+90*q); y=cy+math.sin(a)*(30+90*q)*0.35",
        "        d.line((cx,cy,x,y),fill=(*CYAN,int(160*q)),width=2)",
        "    seal(im,'A FLATWORM REMEMBERS','cut it - pieces know what to become',GOLD)",
    ])
    p.add_vis("field", [
        "def vis_field(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(40):",
        "        a=i*math.tau/40+t*0.05; rad=30+90*r",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.4",
        "        d.ellipse((x-2,y-2,x+2,y+2),fill=(*CYAN,int(100*r)))",
        "    glow_circle(im,cx,cy,16,CYAN,int(190*r),12)",
        "    seal(im,'THE BIOELECTRIC FIELD','voltage carries pattern across cells',CYAN)",
    ])
    p.add_vis("memory", [
        "def vis_memory(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,12,GOLD,int(180*r),10)",
        "    for i in range(10):",
        "        a=i*math.tau/10+t*0.06; q=clamp(r*4-i*0.06)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(20+90*q); y=cy+math.sin(a)*(20+90*q)*0.35",
        "        d.line((cx,cy,x,y),fill=(*GOLD,int(140*q)),width=2)",
        "        d.ellipse((x-5*q,y-5*q,x+5*q,y+5*q),outline=(*PALE_GOLD,int(130*q)),width=1)",
        "    seal(im,'PATTERN MEMORY WITHOUT BRAIN','the body remembers a shape it is not wearing',GOLD)",
    ])
    p.add_vis("xenobot", [
        "def vis_xenobot(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(12):",
        "        a=i*math.tau/12+t*0.06; q=clamp(r*3-i*0.06)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(30+80*q); y=cy+math.sin(a)*(30+80*q)*0.35",
        "        d.ellipse((x-10*q,y-10*q,x+10*q,y+10*q),fill=(*mix(CYAN,GREEN,i/11),int(180*q)))",
        "    seal(im,'XENOBOTS','cells reorganize without genetic modification',GREEN)",
    ])
    p.add_vis("morphospace", [
        "def vis_morphospace(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    rng=random.Random(42)",
        "    for i in range(80):",
        "        q=clamp(r*2-i*0.008)",
        "        if q<=0: continue",
        "        a=rng.uniform(0,math.tau); rad=rng.uniform(20,150)*q",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.4",
        "        col=GOLD if rng.random()<0.3 else (CYAN if rng.random()<0.5 else PALE_SILVER)",
        "        d.ellipse((x-3*q,y-3*q,x+3*q,y+3*q),fill=(*col,int(120*q)))",
        "    glow_circle(im,cx,cy,12,GOLD,int(200*r),12)",
        "    seal(im,'THE MORPHOSPACE','all possible body plans as attractors',GOLD)",
    ])
    p.add_vis("agency", [
        "def vis_agency(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(8):",
        "        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.1)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(30+90*q); y=cy+math.sin(a)*(30+90*q)*0.35",
        "        d.line((cx,cy,x,y),fill=(*CYAN,int(160*q)),width=2)",
        "        arrow(d,(cx+(x-cx)*0.85,cy+(y-cy)*0.85),(x,y),CYAN,2,8)",
        "    seal(im,'DIVERSE INTELLIGENCE','cells navigate, decide, communicate',CYAN)",
    ])
    p.add_vis("implication", [
        "def vis_implication(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,14,GOLD,int(200*r),12)",
        "    centered_text(d,(w*0.50,h*0.20),'GENES',load_font(FONT_SANS_BOLD,int(h*0.030)),SOFT_INK)",
        "    centered_text(d,(w*0.50,h*0.60),'FIELD',load_font(FONT_SANS_BOLD,int(h*0.030)),CYAN)",
        "    if r>0.4:",
        "        for i in range(3):",
        "            x=lerp(w*0.30,w*0.70,i/2); q=clamp((r-0.4)*5-i*0.1)",
        "            if q<=0: continue",
        "            d.ellipse((x-6*q,cy-6*q,x+6*q,cy+6*q),fill=(*GREEN,int(150*q)))",
        "    seal(im,'GENES ARE NOT THE BLUEPRINT','the field carries the plan',GOLD)",
    ])
    p.add_vis("repair", [
        "def vis_repair(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); mode=p.get('mode','wound')",
        "    if mode=='wound':",
        "        glow_circle(im,cx,cy,20,CRIMSON,int(200*r),14)",
        "        d=ImageDraw.Draw(im)",
        "        for i in range(8):",
        "            a=i*math.tau/8+t*0.1; x=cx+math.cos(a)*30*(1+r); y=cy+math.sin(a)*30*(1+r)*0.4",
        "            d.line((cx,cy,x,y),fill=(*CRIMSON,int(140*r)),width=2)",
        "        seal(im,'WOUND IS PATTERN LOSS','injury disrupts the bioelectric map',CRIMSON)",
        "    else:",
        "        d=ImageDraw.Draw(im)",
        "        for i in range(20):",
        "            a=i*math.tau/20+t*0.04; rad=20+80*r",
        "            x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.4",
        "            glow_circle(im,x,y,4+3*r,GREEN,int(140*r),6)",
        "        glow_circle(im,cx,cy,14,GREEN,int(200*r),12)",
        "        seal(im,'REPAIR RESTORES THE FIELD','voltage returns - the body remembers',GREEN)",
    ])
    p.add_vis("navigation", [
        "def vis_navigation(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(6):",
        "        a=i*math.tau/6+r*0.5; rad=30+90*r",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
        "        d.line((cx,cy,x,y),fill=(*mix(CYAN,GREEN,i/5),int(160*r)),width=2)",
        "        glow_circle(im,x,y,6+3*r,mix(CYAN,GREEN,i/5),int(150*r),7)",
        "    glow_circle(im,cx,cy,10,GOLD,int(190*r),9)",
        "    seal(im,'CELLS NAVIGATE POSSIBLE FORMS','by sensing the space of what they can become',GOLD)",
    ])
    scenes_data = [
        ("A Flatworm Remembers", "Cut it - pieces know what to become. The field remembers the whole.", 7.0, "planaria", {}),
        ("The Bioelectric Field", "Voltage carries pattern across cells. The body's map is electrical.", 7.5, "field", {}),
        ("Pattern Memory Without Brain", "The body remembers a shape it is not wearing. Memory is not only neural.", 8.0, "memory", {}),
        ("Xenobots", "Cells reorganize without genetic modification. Form follows field.", 7.5, "xenobot", {}),
        ("The Morphospace", "All possible body plans as attractors. Cells navigate the space of form.", 8.0, "morphospace", {}),
        ("Diverse Intelligence", "Cells navigate, decide, communicate. Basal cognition at every scale.", 7.5, "agency", {}),
        ("Genes Are Not the Blueprint", "The field carries the plan. Genes are the toolkit, not the architect.", 8.0, "implication", {}),
        ("Wound is Pattern Loss", "Injury disrupts the bioelectric map. The field flickers.", 7.0, "repair", {"mode": "wound"}),
        ("Repair Restores the Field", "Voltage returns. The body remembers its target shape.", 7.5, "repair", {"mode": "heal"}),
        ("Cells Navigate Possible Forms", "Not by instruction - by sensing the space of what they can become.", 8.5, "navigation", {}),
        ("Memory is Distributed", "Every cell carries a fragment of the body's self-image.", 8.0, "memory", {}),
        ("The Target Morphology", "A golden attractor in morphospace - the form the system seeks.", 8.0, "morphospace", {}),
        ("Healing is Navigation", "Wound healing is a journey across morphospace, guided by the field.", 8.5, "navigation", {}),
        ("Basal Cognition", "Intelligence does not begin with neurons. It begins with cells solving problems.", 9.0, "agency", {}),
        ("Form is Function in Space", "The shape a body takes is the solution to a problem the cells solved together.", 9.0, "navigation", {}),
    ]
    for row in scenes_data:
        p.add_scene(*row)
    p.add_scene("The Field Remembers", "Injury does not erase the target. The field holds the memory of wholeness.", 8.0, "memory", {})
    p.add_scene("Cells Solve Problems", "A cell is not a machine. It is a problem-solver with a goal.", 8.5, "agency", {})
    p.add_scene("Bioelectric Computation", "Voltage patterns are a computational medium. Cells compute form.", 8.5, "field", {})
    p.add_scene("The Body is a Democracy", "Every cell votes on the shape of the whole. Cooperation is computation.", 9.0, "agency", {})
    p.add_scene("Regeneration is Memory", "A salamander regrows a limb because the field remembers the arm.", 8.5, "repair", {"mode": "heal"})
    p.add_scene("Form is Intelligent", "The shape of a body is a solution to a problem. Form is cognition expressed.", 9.0, "navigation", {})
    p.add_vis("form_cognition", [
        "def vis_form_cognition(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    pts=[(cx+math.cos(i*math.tau/30)*(30+120*r),cy+math.sin(i*math.tau/30)*(30+120*r)*0.35) for i in range(31)]",
        "    glow_line(im,partial(pts,r),GOLD,width=4,alpha=220,blur=14)",
        "    for i in range(4):",
        "        a=i*math.tau/4+r*0.5; x=cx+math.cos(a)*90*r; y=cy+math.sin(a)*90*r*0.35",
        "        d.line((cx,cy,x,y),fill=(*CYAN,int(150*r)),width=2)",
        "        glow_circle(im,x,y,6+3*r,CYAN,int(150*r),7)",
        "    seal(im,'FORM IS COGNITION','every body is a thought made visible',GOLD)",
    ])
    p.add_scene("Form is Cognition", "Every body is a thought made visible. Morphospace is the mind of the cell.", 9.0, "form_cognition", {})
    p.add_scene("The Morphic Field", "Memory is not stored in the brain alone. The field carries the pattern.", 8.5, "morphospace", {})
    return p


def build_free_energy():
    p = Pack("free_energy_primitive", "All Systems Minimize Surprise",
             "Friston — free energy principle", "Friston's unified theory of self-organization.",
             "descending prediction error",
             '"cyan":"prediction / model", "gold":"surprise / action", "green":"precision / learning", "crimson":"error"')
    p.add_vis("principle", [
        "def vis_principle(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,16,CYAN,int(190*r),12)",
        "    for i in range(8):",
        "        a=i*math.tau/8+t*0.06; q=clamp(r*3-i*0.08)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(20+90*q); y=cy+math.sin(a)*(20+90*q)*0.35",
        "        d.line((cx,cy,x,y),fill=(*CYAN,int(160*q)),width=2)",
        "        glow_circle(im,x,y,5+3*q,PALE_CYAN,int(140*q),6)",
        "    seal(im,'THE FREE ENERGY PRINCIPLE','self-organizing systems minimize surprise',CYAN)",
    ])
    p.add_vis("prediction", [
        "def vis_prediction(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(12):",
        "        a=i*math.tau/12+t*0.05; q=clamp(r*4-i*0.06)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(20+100*q); y=cy+math.sin(a)*(20+100*q)*0.35",
        "        col=mix(PALE_CYAN,CYAN,0.5+0.5*math.sin(t+i))",
        "        d.line((cx,cy,x,y),fill=(*col,int(150*q)),width=2)",
        "        d.ellipse((x-6*q,y-6*q,x+6*q,y+6*q),fill=(*col,int(150*q)))",
        "    seal(im,'PREDICTIVE PROCESSING','the brain predicts and updates - perception is controlled hallucination',CYAN)",
    ])
    p.add_vis("active", [
        "def vis_active(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(6):",
        "        a=i*math.tau/6+r*0.4; q=clamp(r*3-i*0.1)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(40+80*q); y=cy+math.sin(a)*(40+80*q)*0.35",
        "        d.line((cx,cy,x,y),fill=(*GOLD,int(170*q)),width=3)",
        "        arrow(d,(cx+(x-cx)*0.85,cy+(y-cy)*0.85),(x,y),GOLD,2,8)",
        "    glow_circle(im,cx,cy,12,GOLD,int(180*r),10)",
        "    seal(im,'ACTIVE INFERENCE','action makes the world match the prediction',GOLD)",
    ])
    p.add_vis("markov", [
        "def vis_markov(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    d.ellipse((cx-100*r,cy-80*r,cx+100*r,cy+80*r),outline=(*INK,int(170*r)),width=3)",
        "    d.ellipse((cx-50*r,cy-40*r,cx+50*r,cy+40*r),outline=(*GOLD,int(150*r)),width=2)",
        "    glow_circle(im,cx,cy,10,CYAN,int(160*r),8)",
        "    centered_text(d,(cx,cy-30*r),'SELF',load_font(FONT_SANS_BOLD,int(h*0.025)),GOLD)",
        "    centered_text(d,(cx,cy+50*r),'WORLD',load_font(FONT_SANS_BOLD,int(h*0.025)),INK)",
        "    seal(im,'MARKOV BLANKETS','boundary between self and world - actively maintained',INK)",
    ])
    p.add_vis("surprise", [
        "def vis_surprise(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(10):",
        "        a=i*math.tau/10+t*0.08; q=clamp(r*4-i*0.06)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(30+100*q); y=cy+math.sin(a)*(30+100*q)*0.35",
        "        col=GREEN if q>0.6 else CRIMSON",
        "        d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)",
        "        glow_circle(im,x,y,5+3*q,col,int(150*q),6)",
        "    seal(im,'SURPRISE IS INFORMATION','error is the engine of learning',GREEN)",
    ])
    p.add_vis("hierarchy", [
        "def vis_hierarchy(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(5):",
        "        q=clamp(r*5-i)",
        "        if q<=0: continue",
        "        y=lerp(h*0.20,h*0.67,i/4); rad=lerp(60,15,i/4); col=mix(CYAN,GOLD,i/4)",
        "        d.ellipse((w*0.50-rad*q,y-rad*q,w*0.50+rad*q,y+rad*q),outline=(*col,int(180*q)),width=2)",
        "    seal(im,'HIERARCHICAL INFERENCE','deep models at multiple scales',CYAN)",
    ])
    p.add_vis("self", [
        "def vis_self(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,14,GOLD,int(180*r),10)",
        "    for i in range(8):",
        "        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.08)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(40+90*q); y=cy+math.sin(a)*(40+90*q)*0.35",
        "        d.line((cx,cy,x,y),fill=(*mix(CYAN,GOLD,i/7),int(160*q)),width=2)",
        "        d.ellipse((x-8*q,y-8*q,x+8*q,y+8*q),outline=(*PALE_GOLD,int(140*q)),width=2)",
        "    seal(im,'THE SELF IS A PREDICTION','you are your brain\\'s best guess',GOLD)",
    ])
    p.add_vis("precision", [
        "def vis_precision(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(6):",
        "        q=clamp(r*6-i)",
        "        if q<=0: continue",
        "        y=lerp(h*0.20,h*0.67,i/5); width=lerp(200,40,i/5)*q",
        "        d.line((w*0.50-width/2,y,w*0.50+width/2,y),fill=(*CYAN,int(200*q)),width=4)",
        "    seal(im,'PRECISION WEIGHTING','attention modulates gain on prediction error',CYAN)",
    ])
    p.add_vis("free_energy", [
        "def vis_free_energy(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    pts=[(cx+math.cos(i*math.tau/30)*(30+110*r),cy+math.sin(i*math.tau/30)*(30+110*r)*0.35) for i in range(31)]",
        "    glow_line(im,partial(pts,r),GOLD,width=4,alpha=220,blur=14)",
        "    for i in range(5):",
        "        a=i*math.tau/5+r*0.5; x=cx+math.cos(a)*80*r; y=cy+math.sin(a)*80*r*0.35",
        "        d.line((cx,cy,x,y),fill=(*GREEN,int(160*r)),width=2)",
        "    seal(im,'FREE ENERGY IS LIFE','the principle that every living system enacts',GOLD)",
    ])
    for t, n, d, v in [
        ("The Free Energy Principle", "Self-organizing systems minimize surprise — the first law of life.", 7.0, "principle"),
        ("Predictive Processing", "The brain predicts and updates — perception is controlled hallucination.", 7.5, "prediction"),
        ("Active Inference", "Action makes the world match the prediction — moving to minimize surprise.", 7.5, "active"),
        ("Markov Blankets", "Boundary between self and world — actively maintained by every living system.", 8.0, "markov"),
        ("Surprise is Information", "Error is the engine of learning — prediction error drives adaptation.", 7.0, "surprise"),
        ("Hierarchical Inference", "Deep models at multiple scales — the brain is a deep prediction engine.", 7.5, "hierarchy"),
        ("Precision Weighting", "Attention modulates the gain on prediction error — the anatomy of focus.", 7.5, "precision"),
        ("The Self is a Prediction", "You are your brain's best guess — the self is a generative model.", 8.0, "self"),
        ("All Systems Minimize Surprise", "From bacteria to societies — the same principle at every scale.", 8.5, "free_energy"),
        ("Perception as Inference", "Seeing is not receiving. It is testing a hypothesis against sensory data.", 7.5, "prediction"),
        ("Action as Question", "Action is the question the organism asks the world. Sensation is the answer.", 8.0, "active"),
        ("The Bayesian Brain", "The brain is a Bayesian inference engine — updating beliefs with evidence.", 8.0, "hierarchy"),
        ("Free Energy is Life", "The principle that every living system enacts — necessity becomes freedom.", 9.0, "free_energy"),
        ("Self-Evidence", "To exist is to model. The model that persists minimizes surprise.", 8.5, "self"),
        ("From Physics to Mind", "Free energy bridges the gap between thermodynamics and consciousness.", 9.0, "principle"),
    ]:
        p.add_scene(t, n, d, v)
    return p


def build_consciousness_container():
    p = Pack("consciousness_container", "Consciousness Contains the Body",
             "Tantraloka — 36 tattvas", "Tantraloka's 36 tattvas — consciousness descends into matter.",
             "expanding and contracting spheres",
             '"gold":"Shiva / pure consciousness", "violet":"Shakti / dynamic power", "cyan":"pure path", "ink":"impure path / matter", "crimson":"kancukas / limitation"')
    p.add_vis("siva", [
        "def vis_siva(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,20,GOLD,int(220*r),16)",
        "    d.ellipse((cx-50*r,cy-50*r,cx+50*r,cy+50*r),outline=(*GOLD,int(180*r)),width=3)",
        "    centered_text(d,(cx,cy),'SHIVA',load_font(FONT_SERIF_BOLD,int(h*0.055)),(*GOLD,int(200*r)))",
        "    seal(im,'SHIVA: PURE CONSCIOUSNESS','the ground - without qualities, without limit',GOLD)",
    ])
    p.add_vis("sakti", [
        "def vis_sakti(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,16,VIOLET,int(200*r),14)",
        "    for i in range(10):",
        "        a=i*math.tau/10+t*0.06; q=clamp(r*3-i*0.06)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(20+100*q); y=cy+math.sin(a)*(20+100*q)*0.35",
        "        d.line((cx,cy,x,y),fill=(*VIOLET,int(160*q)),width=2)",
        "    seal(im,'SHAKTI: THE POWER','consciousness is dynamic, creative, free',VIOLET)",
    ])
    p.add_vis("descent", [
        "def vis_descent(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(7):",
        "        q=clamp(r*7-i)",
        "        if q<=0: continue",
        "        rad=20+i*22; col=mix(GOLD,INK,i/6)",
        "        d.ellipse((cx-rad*q,cy-rad*q*.6,cx+rad*q,cy+rad*q*.6),outline=(*col,int(200*q)),width=2)",
        "    seal(im,'DESCENT OF THE TATTVAS','from Shiva to the elements - the cosmic contraction',INK)",
    ])
    p.add_vis("kancukas", [
        "def vis_kancukas(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    labels=['KALA','VIDYA','RAGA','KALA','NIYATI']",
        "    for i,l in enumerate(labels):",
        "        a=i*math.tau/5-r*0.3; q=clamp(r*5-i*0.1)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(50+100*q); y=cy+math.sin(a)*(50+100*q)*0.35",
        "        col=mix(CRIMSON,VIOLET,i/4)",
        "        d.line((cx,cy,x,y),fill=(*col,int(170*q)),width=3)",
        "        d.ellipse((x-20*q,y-20*q,x+20*q,y+20*q),outline=(*col,int(150*q)),width=2)",
        "        centered_text(d,(x,y),l,load_font(FONT_SANS_BOLD,int(h*0.020)),col)",
        "    seal(im,'THE FIVE KANCUKAS','self-limitation of the infinite',CRIMSON)",
    ])
    p.add_vis("maya", [
        "def vis_maya(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,14,VIOLET,int(180*r),10)",
        "    for i in range(8):",
        "        a=i*math.tau/8+t*0.06; q=clamp(r*4-i*0.08)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(40+90*q); y=cy+math.sin(a)*(40+90*q)*0.35",
        "        d.line((cx,cy,x,y),fill=(*VIOLET,int(140*q)),width=2)",
        "        glow_circle(im,x,y,4+2*q,PALE_VIOLET,int(120*q),5)",
        "    seal(im,'MAYA IS NOT ILLUSION','creative limitation that makes experience possible',VIOLET)",
    ])
    p.add_vis("return_path", [
        "def vis_return_path(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(7):",
        "        q=clamp(r*7-i)",
        "        if q<=0: continue",
        "        rad=20+(6-i)*22; col=mix(INK,GOLD,i/6)",
        "        d.ellipse((cx-rad*q,cy-rad*q*.6,cx+rad*q,cy+rad*q*.6),outline=(*col,int(200*q)),width=2)",
        "    seal(im,'THE ASCENT','every contraction carries the memory of expansion',GOLD)",
    ])
    p.add_vis("realization", [
        "def vis_realization(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,24,GOLD,int(240*r),20)",
        "    for i in range(6):",
        "        a=i*math.tau/6+t*0.04; rad=40+130*r",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
        "        glow_circle(im,x,y,8+4*r,mix(GOLD,VIOLET,i/5),int(160*r),8)",
        "    centered_text(d,(cx,cy),'AHAM',load_font(FONT_SERIF_BOLD,int(h*0.065)),(*GOLD,int(220*r)))",
        "    seal(im,'REALIZATION','consciousness is not in the body - the body is in consciousness',GOLD)",
    ])
    p.add_vis("pure_path", [
        "def vis_pure_path(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(5):",
        "        a=i*math.tau/5+t*0.05; q=clamp(r*5-i*0.1)",
        "        if q<=0: continue",
        "        rad=30+80*q; x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
        "        col=mix(GOLD,CYAN,i/4); glow_circle(im,x,y,6+3*q,col,int(150*q),7)",
        "    seal(im,'THE PURE PATH','Shiva-Shakti to Maya - pure awareness',GOLD)",
    ])
    p.add_vis("impure_path", [
        "def vis_impure_path(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(5):",
        "        q=clamp(r*5-i)",
        "        if q<=0: continue",
        "        y=lerp(h*0.25,h*0.65,i/4); col=mix(CYAN,INK,i/4)",
        "        d.rounded_rectangle((w*0.30,y-12,w*0.70,y+12),radius=6,fill=(*mix(WHITE,col,0.1),int(200*q)),outline=(*col,int(160*q)),width=2)",
        "        centered_text(d,(w*0.50,y),f'TATTVA {i+1}',load_font(FONT_SANS_BOLD,int(h*0.019)),col)",
        "    seal(im,'THE IMPURE PATH','from Maya to Earth - the five elements of experience',INK)",
    ])
    p.add_vis("consciousness_final", [
        "def vis_consciousness_final(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(20):",
        "        a=i*math.tau/20+t*0.03; rad=20+140*r",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
        "        glow_circle(im,x,y,3+2*r,PALE_GOLD,int(120*r),4)",
        "    glow_circle(im,cx,cy,16,GOLD,int(220*r),14)",
        "    centered_text(d,(cx,cy),'SIVOHAM',load_font(FONT_SERIF_BOLD,int(h*0.055)),(*GOLD,int(200*r)))",
        "    seal(im,'I AM THAT','consciousness contains the body - the universe is your body',GOLD)",
    ])
    for t, n, d, v in [
        ("Shiva: Pure Consciousness", "The ground — without qualities, without limit.", 7.0, "siva"),
        ("Shakti: The Power", "Consciousness is dynamic, creative, free. The power of awareness.", 7.0, "sakti"),
        ("Descent of the Tattvas", "From Shiva through the pure path to the elements — the cosmic contraction.", 8.0, "descent"),
        ("The Pure Path", "Shiva-Shakti to Maya — the first five tattvas are pure awareness.", 7.5, "pure_path"),
        ("The Five Kancukas", "Self-limitation of the infinite — the armor of contraction.", 8.0, "kancukas"),
        ("Maya is Not Illusion", "Creative limitation that makes experience possible.", 7.5, "maya"),
        ("The Impure Path", "From Maya to Earth — the five elements of experience.", 7.5, "impure_path"),
        ("The Ascent", "Every contraction carries the memory of expansion. The return to light.", 8.0, "return_path"),
        ("Realization", "Consciousness is not in the body. The body is in consciousness.", 8.5, "realization"),
        ("All 36 Tattvas", "The complete emanation — from Shiva to Earth and back.", 9.0, "descent"),
        ("The Five Acts", "Creation, preservation, dissolution, veiling, grace — the cosmic rhythm.", 8.5, "sakti"),
        ("Consciousness Contains", "The universe is a thought in the mind of Shiva. You are that mind.", 9.0, "consciousness_final"),
        ("I Am That", "Consciousness contains the body — the universe is your body.", 10.0, "consciousness_final"),
    ]:
        p.add_scene(t, n, d, v)
    return p


def build_time_is_forgetting():
    p = Pack("time_is_forgetting", "Time Is Produced By Forgetting",
             "Tantraloka - kalagrasa", "Time as the forgetting of simultaneity.",
             "tightening spiral of forgetting",
             '"gold":"simultaneity", "cyan":"sequence", "crimson":"forgetting"')
    p.add_vis("simultaneous_vis", [
        "def vis_simultaneous_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,20,GOLD,int(220*r),16)",
        "    for i in range(12):",
        "        a=i*math.tau/12+t*0.05; q=clamp(r*4-i*0.06)",
        "        if q<=0: continue",
        "        x=cx+math.cos(a)*(20+120*q); y=cy+math.sin(a)*(20+120*q)*0.35",
        "        d.line((cx,cy,x,y),fill=(*GOLD,int(160*q)),width=2)",
        "    seal(im,'ALL MOMENTS COEXIST','the universe is a single act of consciousness',GOLD)",
    ])
    p.add_vis("forgetting", [
        "def vis_forgetting(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    pts=[(cx+math.cos(i*math.tau/40)*(30+100*r),cy+math.sin(i*math.tau/40)*(30+100*r)*0.35) for i in range(41)]",
        "    glow_line(im,partial(pts,1-r),CRIMSON,width=3,alpha=180,blur=10)",
        "    glow_circle(im,cx,cy,10,GOLD,int(150*(1-r)),8)",
        "    seal(im,'FORGETTING PRODUCES SEQUENCE','when you cannot perceive all at once, time is born',CRIMSON)",
    ])
    p.add_vis("spanda_pulse", [
        "def vis_spanda_pulse(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    pulse_r=30+20*math.sin(t*1.5)",
        "    glow_circle(im,cx,cy,pulse_r*(0.5+r*0.5),GOLD,int(180*r),12)",
        "    for i in range(6):",
        "        a=i*math.tau/6+t*0.08; rad=40+80*r",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
        "        d.line((cx,cy,x,y),fill=(*GOLD,int(150*r)),width=2)",
        "    seal(im,'THE PULSE OF CONSCIOUSNESS','Spanda IS time - the vibration of awareness',GOLD)",
    ])
    p.add_vis("kalagrasa", [
        "def vis_kalagrasa(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(20):",
        "        q=clamp(r*2-i*0.03)",
        "        if q<=0: continue",
        "        a=i*math.tau/20+t*0.05; rad=20+100*q",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
        "        d.ellipse((x-4*q,y-4*q,x+4*q,y+4*q),fill=(*CYAN,int(140*q)))",
        "    glow_circle(im,cx,cy,14,GOLD,int(180*r),10)",
        "    seal(im,'CONSUMING TIME','the power of time is consumed in the pulse of awareness',CYAN)",
    ])
    p.add_vis("past_vis", [
        "def vis_past_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(3):",
        "        q=clamp(r*3-i*0.1); if q<=0: continue",
        "        x=w*(0.20+i*0.15); col=mix(SOFT_INK,GOLD,i/2)",
        "        d.ellipse((x-12*q,cy-12*q,x+12*q,cy+12*q),fill=(*col,int(180*q)))",
        "    seal(im,'THE PAST IS NOT GONE','hidden - recoverable, mutable',GOLD)",
    ])
    p.add_vis("future_vis", [
        "def vis_future_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(5):",
        "        a=i*math.tau/5+r*0.6; q=clamp(r*3-i*0.08); if q<=0: continue",
        "        x=cx+math.cos(a)*(50+100*q); y=cy+math.sin(a)*(50+100*q)*0.35",
        "        col=mix(CYAN,VIOLET,i/4); d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)",
        "        glow_circle(im,x,y,6+3*q,col,int(150*q),7)",
        "    seal(im,'THE FUTURE IS NOT YET','another region of the same landscape',VIOLET)",
    ])
    p.add_vis("now_vis", [
        "def vis_now_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,18,GOLD,int(220*r),16)",
        "    centered_text(d,(cx,cy),'NOW',load_font(FONT_SERIF_BOLD,int(h*0.070)),(*GOLD,int(200*r)))",
        "    for i in range(8):",
        "        a=i*math.tau/8+t*0.06; rad=40+110*r",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
        "        glow_circle(im,x,y,5+3*r,PALE_GOLD,int(140*r),6)",
        "    seal(im,'THE ETERNAL NOW','the spacious present - all time contained in this moment',GOLD)",
    ])
    p.add_vis("time_spiral", [
        "def vis_time_spiral(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    pts=[(cx+math.cos(i*math.tau/60*r*5)*(30+100*r),cy+math.sin(i*math.tau/60*r*5)*(30+100*r)*0.35) for i in range(61)]",
        "    glow_line(im,partial(pts,r),GOLD,width=4,alpha=220,blur=14)",
        "    for i in range(6):",
        "        a=i*math.tau/6+r*0.8; rad=30+90*r",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
        "        d.line((cx,cy,x,y),fill=(*CYAN,int(140*r)),width=2)",
        "    seal(im,'TIME IS A SPIRAL','not a line - every moment returns transformed',CYAN)",
    ])
    for row in [
        ("All Moments Coexist", "The universe is a single act of consciousness.", 7.0, "simultaneous_vis", {}),
        ("Forgetting Produces Sequence", "When you cannot perceive all at once, time is born.", 7.5, "forgetting", {}),
        ("The Pulse of Consciousness", "Spanda IS time - the vibration of awareness.", 7.5, "spanda_pulse", {}),
        ("Consuming Time", "The power of time is consumed in the pulse of awareness.", 7.5, "kalagrasa", {}),
        ("The Past is Not Gone", "Hidden - recoverable, mutable.", 7.0, "past_vis", {}),
        ("The Future is Not Yet", "Another region of the same landscape.", 7.0, "future_vis", {}),
        ("The Eternal Now", "The spacious present - all time contained in this moment.", 8.5, "now_vis", {}),
        ("Time is a Spiral", "Not a line - every moment returns transformed.", 8.0, "time_spiral", {}),
        ("Forgetting is a Gift", "Without forgetting, every moment would be eternal.", 7.5, "forgetting", {}),
        ("Duration is Rhythm", "Not measured by clocks - felt as pulse of awareness.", 7.5, "spanda_pulse", {}),
        ("The Arrow of Attention", "Attention moves through simultaneity, creating sequence.", 8.0, "time_spiral", {}),
        ("Kalagrasa: Eating Time", "Shiva consumes time itself - liberation from sequence.", 9.0, "kalagrasa", {}),
        ("Past and Future Meet", "In the eternal now, past and future touch.", 8.5, "now_vis", {}),
        ("The Spacious Present", "When you stop making time, you find yourself in the timeless.", 9.0, "time_spiral", {}),
        ("Time is Forgetting", "What we call time is the memory of a unity we can no longer see.", 9.5, "forgetting", {}),
    ]:
        p.add_scene(*row)
    return p

def build_svatantrya():
    p = Pack("svatantrya_freedom", "Freedom Comes Before Causality",
             "Tantraloka - svatantrya", "Absolute freedom as the ground of all causality.",
             "unbounded field contracting freely",
             '"gold":"freedom", "crimson":"constraint", "cyan":"causality"')
    p.add_vis("svatantrya_vis", [
        "def vis_svatantrya_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,24,GOLD,int(240*r),20)",
        "    for i in range(16):",
        "        a=i*math.tau/16+t*0.03; rad=30+130*r",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
        "        glow_circle(im,x,y,3+2*r,PALE_GOLD,int(120*r),4)",
        "    seal(im,'SVATANTRYA: ABSOLUTE FREEDOM','consciousness IS freedom - the ground of all causality',GOLD)",
    ])
    p.add_vis("causality_vis", [
        "def vis_causality_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(6):",
        "        a=i*math.tau/6+t*0.06; q=clamp(r*4-i*0.1); if q<=0: continue",
        "        x=cx+math.cos(a)*(20+100*q); y=cy+math.sin(a)*(20+100*q)*0.35",
        "        col=mix(CYAN,INK,i/5); d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)",
        "        arrow(d,(cx+(x-cx)*0.85,cy+(y-cy)*0.85),(x,y),col,2,8)",
        "    seal(im,'CAUSALITY IS DERIVED','freedom contracts into law',CYAN)",
    ])
    p.add_vis("kancukas_vis", [
        "def vis_kancukas_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(5):",
        "        q=clamp(r*5-i*0.1); if q<=0: continue",
        "        a=i*math.tau/5+r*0.2; rad=20+100*q",
        "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
        "        col=mix(GOLD,CRIMSON,i/4); d.ellipse((x-15*q,y-15*q,x+15*q,y+15*q),outline=(*col,int(180*q)),width=2)",
        "    seal(im,'THE KANCUKAS AS SELF-LIMITATION','freedom choosing to appear constrained',CRIMSON)",
    ])
    p.add_vis("choice_vis", [
        "def vis_choice_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(3):",
        "        a=(i-1)*0.6; q=clamp(r*3-i*0.15); if q<=0: continue",
        "        x=cx+math.cos(a)*120*q; y=cy+math.sin(a)*120*q",
        "        col=GREEN if i==1 else (CYAN if i==0 else GOLD)",
        "        d.line((cx,cy,x,y),fill=(*col,int(170*q)),width=3)",
        "        glow_circle(im,x,y,8+4*q,col,int(170*q),8)",
        "    seal(im,'CHOICE IS NOT AN ILLUSION','every moment is a free act of consciousness',GREEN)",
    ])
    p.add_vis("physics_vis", [
        "def vis_physics_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    for i in range(4):",
        "        q=clamp(r*4-i*0.1); if q<=0: continue",
        "        y=lerp(h*0.25,h*0.60,i/3); width=lerp(300,100,i/3)*q",
        "        d.line((w*0.50-width/2,y,w*0.50+width/2,y),fill=(*INK,int(180*q)),width=3)",
        "    glow_circle(im,cx,cy,10,GOLD,int(160*r),8)",
        "    seal(im,'PHYSICS DESCRIBES CONSTRAINTS','not why there are constraints - freedom is the why',INK)",
    ])
    p.add_vis("paradox_vis", [
        "def vis_paradox_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    glow_circle(im,cx,cy,18,GOLD,int(200*r),14)",
        "    d.ellipse((cx-100*r,cy-80*r,cx+100*r,cy+80*r),outline=(*CRIMSON,int(170*r)),width=3)",
        "    d.ellipse((cx-130*r,cy-100*r,cx+130*r,cy+100*r),outline=(*CYAN,int(120*r)),width=2)",
        "    seal(im,'THE PARADOX OF FREEDOM','to be free includes appearing unfree',CRIMSON)",
    ])
    p.add_vis("living_vis", [
        "def vis_living_vis(im,u,t,p):",
        "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
        "    pts=[(cx+math.cos(i*math.tau/40)*(30+120*r),cy+math.sin(i*math.tau/40)*(30+120*r)*0.35) for i in range(41)]",
        "    glow_line(im,partial(pts,r),GOLD,width=4,alpha=220,blur=14)",
        "    for i in range(4):",
        "        a=i*math.tau/4+t*0.06; x=cx+math.cos(a)*80*r; y=cy+math.sin(a)*80*r*0.35",
        "        glow_circle(im,x,y,6+3*r,GREEN,int(160*r),7)",
        "    seal(im,'LIVING FROM FREEDOM','acting without bondage to the past',GREEN)",
    ])
    for row in [
        ("Svatantrya: Absolute Freedom", "Consciousness IS freedom - the ground of all causality.", 7.5, "svatantrya_vis", {}),
        ("Causality is Derived", "Freedom contracts into law. Causality is a subset of freedom.", 7.5, "causality_vis", {}),
        ("The Kancukas as Self-Limitation", "Freedom choosing to appear constrained.", 8.0, "kancukas_vis", {}),
        ("Choice is Not an Illusion", "Every moment is a free act of consciousness.", 7.5, "choice_vis", {}),
        ("Physics Describes Constraints", "Not why there are constraints. Freedom is the why.", 7.5, "physics_vis", {}),
        ("The Paradox of Freedom", "To be free includes appearing unfree. The game of limitation.", 8.0, "paradox_vis", {}),
        ("Living from Freedom", "Acting without bondage to the past. The liberated life.", 8.5, "living_vis", {}),
        ("Freedom Before Being", "Freedom is not a property of consciousness. It IS consciousness.", 8.0, "svatantrya_vis", {}),
        ("The Contracted State", "The kancukas are not punishments. They are freedoms chosen for experience.", 8.0, "kancukas_vis", {}),
        ("The Free Act", "Every action is free. We just forget we chose it.", 7.5, "choice_vis", {}),
        ("Determinism is a View", "The universe looks determined when you look from outside freedom.", 8.0, "physics_vis", {}),
        ("The Unbounded Field", "Before any constraint, there is the freedom that chooses constraint.", 9.0, "paradox_vis", {}),
        ("Daily Liberation", "Freedom is not a future attainment. It is the nature of this moment.", 8.5, "living_vis", {}),
        ("Freedom and Responsibility", "Absolute freedom is absolute responsibility. They are the same.", 9.0, "svatantrya_vis", {}),
        ("The Final Freedom", "Freedom from the need to be free. Resting in what is.", 9.5, "living_vis", {}),
    ]:
        p.add_scene(*row)
    return p

def build_objects_as_actions():
    p = Pack("objects_as_actions", "Objects Are Frozen Actions",
             "Tantraloka - kriya-shakti", "Reality is verbs masquerading as nouns.",
             "waveforms decelerating to stasis",
             '"gold":"action", "cyan":"appearance", "ink":"object"')
    for key, lines in [
        ("tree", [
            "def vis_tree(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    pts=[(cx+math.cos(i*math.tau/30)*(40+100*r),cy+math.sin(i*math.tau/30)*(40+100*r)*0.35) for i in range(31)]",
            "    glow_line(im,partial(pts,r),GOLD,width=3,alpha=200,blur=12)",
            "    glow_circle(im,cx,cy,12,GOLD,int(180*r),10)",
            "    seal(im,'A TREE IS THE ACT OF TREE-ING','reality is verbs masquerading as nouns',GOLD)",
        ]),
        ("kriya_vis", [
            "def vis_kriya_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    for i in range(10):",
            "        a=i*math.tau/10+t*0.06; q=clamp(r*4-i*0.06); if q<=0: continue",
            "        x=cx+math.cos(a)*(20+100*q); y=cy+math.sin(a)*(20+100*q)*0.35",
            "        d.line((cx,cy,x,y),fill=(*CYAN,int(160*q)),width=2)",
            "        d.ellipse((x-5*q,y-5*q,x+5*q,y+5*q),fill=(*PALE_CYAN,int(150*q)))",
            "    seal(im,'KRIYA-SHAKTI','consciousness does not act - it IS action',CYAN)",
        ]),
        ("stability_vis", [
            "def vis_stability_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    for i in range(8):",
            "        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.08); if q<=0: continue",
            "        x=cx+math.cos(a)*(30+90*q); y=cy+math.sin(a)*(30+90*q)*0.35",
            "        d.line((cx,cy,x,y),fill=(*INK,int(150*q)),width=2)",
            "        d.ellipse((x-6*q,y-6*q,x+6*q,y+6*q),outline=(*INK,int(140*q)),width=1)",
            "    seal(im,'STABILITY IS RATE','an object is slowed activity - matter is frozen energy',INK)",
        ]),
        ("process_vis", [
            "def vis_process_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    for i in range(6):",
            "        q=clamp(r*6-i); if q<=0: continue",
            "        y=lerp(h*0.20,h*0.65,i/5); width=lerp(50,250,i/5)*q",
            "        col=mix(GOLD,CYAN,i/5); d.line((w*0.50-width/2,y,w*0.50+width/2,y),fill=(*col,int(180*q)),width=4)",
            "    seal(im,'EVERYTHING IS PROCESS','matter is energy slowed to the point of appearing solid',CYAN)",
        ]),
        ("perception_vis", [
            "def vis_perception_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    glow_circle(im,cx,cy,14,GOLD,int(180*r),10)",
            "    for i in range(8):",
            "        a=i*math.tau/8+t*0.06; q=clamp(r*4-i*0.08); if q<=0: continue",
            "        x=cx+math.cos(a)*(30+100*q); y=cy+math.sin(a)*(30+100*q)*0.35",
            "        col=mix(VIOLET,PALE_GOLD,i/7); d.line((cx,cy,x,y),fill=(*col,int(150*q)),width=2)",
            "    seal(im,'PERCEPTION FREEZES ACTION','seeing solidifies the flux - the observer crystallizes the observed',VIOLET)",
        ]),
        ("identity_vis", [
            "def vis_identity_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    pts=[(cx+math.cos(i*math.tau/35)*(40+110*r),cy+math.sin(i*math.tau/35)*(40+110*r)*0.35) for i in range(36)]",
            "    glow_line(im,partial(pts,r),GOLD,width=4,alpha=220,blur=14)",
            "    centered_text(d,(cx,cy),'~',load_font(FONT_SERIF_BOLD,int(h*0.080)),(*GOLD,int(200*r)))",
            "    seal(im,'YOU ARE NOT A THING','you are a verb - activity recognizing itself as activity',GOLD)",
        ]),
    ]:
        p.add_vis(key, lines)
    for row in [
        ("A Tree IS the Act of Tree-ing", "Reality is verbs masquerading as nouns.", 7.0, "tree", {}),
        ("Kriya-Shakti", "Consciousness does not act - it IS action.", 7.5, "kriya_vis", {}),
        ("Stability is Rate", "An object is slowed activity. Matter is frozen energy.", 7.5, "stability_vis", {}),
        ("Everything is Process", "Matter is energy slowed to the point of appearing solid.", 7.5, "process_vis", {}),
        ("Perception Freezes Action", "Seeing solidifies the flux. The observer crystallizes the observed.", 8.0, "perception_vis", {}),
        ("You Are Not a Thing", "You are a verb - activity recognizing itself as activity.", 8.5, "identity_vis", {}),
        ("The Mountain is Moving", "The mountain is not static. It is the act of mountain-ing.", 7.5, "tree", {}),
        ("Action is the Substance", "The noun is a frozen verb. The verb is the living reality.", 8.0, "kriya_vis", {}),
        ("The World as Waveform", "Reality is not made of things. It is made of actions.", 8.0, "stability_vis", {}),
        ("Attention Freezes", "What you look at solidifies. What you ignore dissolves.", 8.0, "perception_vis", {}),
        ("The Self is a Process", "You are not a fixed self. You are a continuous act of self-ing.", 9.0, "identity_vis", {}),
        ("Action is Freedom", "When you know you are action, you know you are free.", 8.5, "process_vis", {}),
        ("The Dance of Shiva", "Creation and destruction are the same action, seen from different speeds.", 9.0, "kriya_vis", {}),
        ("Objects Are Frozen Actions", "What appears solid is movement slowed below the threshold of perception.", 9.5, "identity_vis", {}),
    ]:
        p.add_scene(*row)
    return p

def build_psyche_gestalt():
    p = Pack("psyche_gestalt", "The Psyche Is Not a Thing",
             "Seth - gestalt of aware energy", "The psyche as an ever-forming state of being.",
             "rearranging energy constellation",
             '"violet":"psyche", "gold":"individuation", "cyan":"energy"')
    for key, lines in [
        ("gestalt_vis", [
            "def vis_gestalt_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    pts=[(cx+math.cos(i*math.tau/40)*(30+120*r),cy+math.sin(i*math.tau/40)*(30+120*r)*0.35) for i in range(41)]",
            "    glow_line(im,partial(pts,r),VIOLET,width=3,alpha=200,blur=12)",
            "    glow_circle(im,cx,cy,14,VIOLET,int(190*r),10)",
            "    seal(im,'GESTALT OF AWARE ENERGY','it is not a thing - no beginning or ending',VIOLET)",
        ]),
        ("creation_vis", [
            "def vis_creation_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    glow_circle(im,cx,cy,16,GOLD,int(200*r),14)",
            "    for i in range(8):",
            "        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.08); if q<=0: continue",
            "        x=cx+math.cos(a)*(30+100*q); y=cy+math.sin(a)*(30+100*q)*0.35",
            "        col=mix(VIOLET,GOLD,i/7); d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)",
            "        d.ellipse((x-8*q,y-8*q,x+8*q,y+8*q),outline=(*col,int(140*q)),width=1)",
            "    seal(im,'YOU CREATE IT AND IT CREATES YOU','an ever-forming state of being',GOLD)",
        ]),
        ("energy_vis", [
            "def vis_energy_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    for i in range(30):",
            "        a=i*math.tau/30+t*0.05; rad=20+100*r",
            "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.4",
            "        d.ellipse((x-2,y-2,x+2,y+2),fill=(*CYAN,int(100*r)))",
            "    glow_circle(im,cx,cy,12,VIOLET,int(180*r),10)",
            "    seal(im,'PURE ENERGY AND INDIVIDUATION','energy becomes its manifestations',CYAN)",
        ]),
        ("dreaming_vis", [
            "def vis_dreaming_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    glow_circle(im,cx,cy,14,VIOLET,int(190*r),12)",
            "    for i in range(6):",
            "        a=i*math.tau/6+t*0.08; rad=40+80*r",
            "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
            "        d.line((cx,cy,x,y),fill=(*PALE_VIOLET,int(140*r)),width=2)",
            "        glow_circle(im,x,y,5+3*r,PALE_VIOLET,int(130*r),6)",
            "    seal(im,'THE DREAMING PSYCHE IS AWAKE','as conscious as in waking',VIOLET)",
        ]),
        ("gods_vis", [
            "def vis_gods_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    for i in range(6):",
            "        q=clamp(r*6-i); if q<=0: continue",
            "        y=lerp(h*0.22,h*0.62,i/5); rad=lerp(12,20,i/5)",
            "        col=mix(GOLD,CRIMSON,i/5)",
            "        glow_circle(im,w*0.50,y,rad*q,col,int(180*q),8)",
            "        centered_text(d,(w*0.50,y+rad*q+20),f'GOD {i+1}',load_font(FONT_SANS_BOLD,int(h*0.017)),col)",
            "    seal(im,'PSYCHE, LANGUAGES, AND GODS','beliefs create the gods',CRIMSON)",
        ]),
        ("value_vis", [
            "def vis_value_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    pts=[(cx+math.cos(i*math.tau/30)*(30+110*r),cy+math.sin(i*math.tau/30)*(30+110*r)*0.35) for i in range(31)]",
            "    glow_line(im,partial(pts,r),GOLD,width=3,alpha=200,blur=12)",
            "    for i in range(5):",
            "        a=i*math.tau/5+r*0.3; q=clamp(r*3-i*0.1); if q<=0: continue",
            "        x=cx+math.cos(a)*80*q; y=cy+math.sin(a)*80*q*0.35",
            "        glow_circle(im,x,y,5+2*r,GREEN,int(140*q),6)",
            "    seal(im,'VALUE FULFILLMENT','enhancing the quality of life itself',GOLD)",
        ]),
    ]:
        p.add_vis(key, lines)
    for row in [
        ("Gestalt of Aware Energy", "It is not a thing - no beginning or ending.", 7.5, "gestalt_vis", {}),
        ("You Create It and It Creates You", "An ever-forming state of being.", 7.5, "creation_vis", {}),
        ("Pure Energy and Individuation", "Energy becomes its manifestations.", 7.5, "energy_vis", {}),
        ("The Dreaming Psyche is Awake", "As conscious as in waking - the psyche does not sleep.", 8.0, "dreaming_vis", {}),
        ("Psyche, Languages, and Gods", "Beliefs create the gods. The psyche speaks through culture.", 8.0, "gods_vis", {}),
        ("Value Fulfillment", "Enhancing the quality of life itself - the psyche's purpose.", 8.5, "value_vis", {}),
        ("The Psyche is Plastic", "The psyche is not fixed. It is a verb, not a noun.", 7.5, "gestalt_vis", {}),
        ("The Energy Personality", "You are a unique flavor of aware energy.", 8.0, "energy_vis", {}),
        ("The Dreaming Creates the Day", "The psyche works out its next day while you sleep.", 8.0, "dreaming_vis", {}),
        ("The Gods are Real", "Not as external beings - as living structures of psychic energy.", 8.5, "gods_vis", {}),
        ("The Psyche's Purpose", "The psyche exists to enhance the quality of experience.", 8.5, "value_vis", {}),
        ("The Open Gestalt", "The psyche never closes. It is always becoming.", 9.0, "creation_vis", {}),
        ("You Are Your Psyche", "There is no self separate from the psyche. You are the gestalt.", 9.5, "gestalt_vis", {}),
    ]:
        p.add_scene(*row)
    return p

def build_dna_antenna():
    p = Pack("dna_antenna", "DNA Is Not a Blueprint",
             "Cassiopaean - the living antenna", "DNA as a receiver of consciousness.",
             "double helix radiating signals",
             '"cyan":"DNA", "gold":"signal", "violet":"consciousness"')
    for key, lines in [
        ("superconductor", [
            "def vis_superconductor(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    for i in range(20):",
            "        q=i/19; x=lerp(w*0.20,w*0.80,q); a=q*math.tau*3+r*math.tau",
            "        y1=cy+math.cos(a)*30; y2=cy+math.cos(a+math.pi)*30",
            "        col=mix(CYAN,PALE_CYAN,0.5+0.5*math.sin(q*math.tau))",
            "        d.line((x,y1,x,y2),fill=(*col,int(200*r)),width=2)",
            "        d.ellipse((x-4,y1-4,x+4,y1+4),fill=(*CYAN,int(160*r)))",
            "        d.ellipse((x-4,y2-4,x+4,y2+4),fill=(*CYAN,int(160*r)))",
            "    seal(im,'DNA AS SUPERCONDUCTOR','conducts electricity - not just information',CYAN)",
        ]),
        ("transceiver", [
            "def vis_transceiver(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    glow_circle(im,cx,cy,14,VIOLET,int(200*r),12)",
            "    for i in range(8):",
            "        a=i*math.tau/8+t*0.06; q=clamp(r*4-i*0.08); if q<=0: continue",
            "        x=cx+math.cos(a)*(30+100*q); y=cy+math.sin(a)*(30+100*q)*0.35",
            "        d.line((cx,cy,x,y),fill=(*VIOLET,int(150*q)),width=2)",
            "        arrow(d,(cx+(x-cx)*0.85,cy+(y-cy)*0.85),(x,y),VIOLET,2,8)",
            "    seal(im,'NEUROTRANSCEIVER FOR THOUGHT','DNA receives and transmits consciousness',VIOLET)",
        ]),
        ("illusion", [
            "def vis_illusion(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    pts=[(cx+math.cos(i*math.tau/30)*(30+100*r),cy+math.sin(i*math.tau/30)*(30+100*r)*0.35) for i in range(31)]",
            "    glow_line(im,partial(pts,r),GOLD,width=3,alpha=200,blur=12)",
            "    centered_text(d,(cx,cy),'LINEAR',load_font(FONT_SANS_BOLD,int(h*0.030)),(*GOLD,int(180*r)))",
            "    centered_text(d,(cx,cy+35*r),'TIME',load_font(FONT_SANS_BOLD,int(h*0.025)),(*SOFT_INK,int(150*r)))",
            "    seal(im,'THE PROGRAM ILLUSION','linear time is a DNA readout',GOLD)",
        ]),
        ("strands", [
            "def vis_strands(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    for j in range(2):",
            "        off=j*math.pi",
            "        pts=[(lerp(w*0.15,w*0.85,i/59),cy+math.sin(i/59*math.tau*4+off+r*math.tau)*20) for i in range(60)]",
            "        glow_line(im,partial(pts,r),mix(CYAN,GOLD,j),width=3,alpha=180,blur=10)",
            "    seal(im,'YOU RECEIVE, NOT GET','the Wave adds frequency - DNA is the antenna',GOLD)",
        ]),
        ("removal", [
            "def vis_removal(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    for i in range(6):",
            "        q=clamp(r*6-i); if q<=0: continue",
            "        y=lerp(h*0.22,h*0.65,i/5); col=mix(GOLD,CRIMSON,i/5)",
            "        d.ellipse((w*0.50-15*q,y-15*q,w*0.50+15*q,y+15*q),fill=(*col,int(180*q)))",
            "    seal(im,'REMOVAL OF KNOWLEDGE CENTERS','Osiris cut apart = DNA frequency reduced',CRIMSON)",
        ]),
        ("antenna_vis", [
            "def vis_antenna_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    for i in range(40):",
            "        a=i*math.tau/40+t*0.04; rad=20+120*r",
            "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.35",
            "        glow_circle(im,x,y,3+2*r,GOLD,int(130*r),5)",
            "    glow_circle(im,cx,cy,16,CYAN,int(200*r),12)",
            "    seal(im,'THE ANTENNA MODEL','DNA optimized for reception of consciousness',CYAN)",
        ]),
    ]:
        p.add_vis(key, lines)
    for row in [
        ("DNA as Superconductor", "Conducts electricity - not just information.", 7.0, "superconductor", {}),
        ("Neurotransceiver for Thought", "DNA receives and transmits consciousness.", 7.5, "transceiver", {}),
        ("The Program Illusion", "Linear time is a DNA readout.", 7.5, "illusion", {}),
        ("You Receive, Not Get", "The Wave adds frequency. DNA is the antenna.", 8.0, "strands", {}),
        ("Removal of Knowledge Centers", "Osiris cut apart = DNA frequency reduced.", 7.5, "removal", {}),
        ("The Antenna Model", "DNA optimized for reception of consciousness.", 8.0, "antenna_vis", {}),
        ("DNA is Not a Blueprint", "DNA does not contain a plan. It receives one.", 8.0, "superconductor", {}),
        ("The Body is a Receiver", "You do not generate consciousness. You receive it.", 8.5, "transceiver", {}),
        ("Frequency and Form", "Different frequencies of consciousness produce different forms.", 8.5, "strands", {}),
        ("The Wave Comes", "Humanity is receiving a new frequency. DNA is adapting.", 9.0, "antenna_vis", {}),
        ("Knowledge is Received", "You cannot learn what you are not tuned to receive.", 8.5, "illusion", {}),
        ("The Remembrance", "The antenna can be repaired. Knowledge centers reopen.", 9.0, "removal", {}),
    ]:
        p.add_scene(*row)
    return p

def build_constructed_self():
    p = Pack("constructed_self", "You Are Not in Your Body",
             "Rubber hand - self as constructed model", "The self as a predictive model, not a location.",
             "body outline redrawn by integration",
             '"gold":"self-model", "cyan":"multisensory", "crimson":"illusion"')
    for key, lines in [
        ("rubber", [
            "def vis_rubber(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    d.ellipse((cx-90*r,cy-20*r,cx-20*r,cy+20*r),outline=(*INK,int(180*r)),width=3)",
            "    d.ellipse((cx+20*r,cy-20*r,cx+90*r,cy+20*r),outline=(*GOLD,int(180*r)),width=3)",
            "    d.line((cx-90*r,cy,cx-20*r,cy),fill=(*INK,int(160*r)),width=2)",
            "    d.line((cx+20*r,cy,cx+90*r,cy),fill=(*GOLD,int(160*r)),width=2)",
            "    glow_circle(im,cx-55*r,cy,8,CYAN,int(160*r),7)",
            "    seal(im,'THE RUBBER HAND ILLUSION','stroke a fake hand - it becomes yours in seconds',INK)",
        ]),
        ("swap", [
            "def vis_swap(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    d.ellipse((cx-80*r,cy-40*r,cx-20*r,cy+40*r),outline=(*CYAN,int(170*r)),width=3)",
            "    d.ellipse((cx+20*r,cy-40*r,cx+80*r,cy+40*r),outline=(*CYAN,int(170*r)),width=3)",
            "    if r>0.3:",
            "        q=(r-0.3)/0.7; glow_circle(im,cx,cy,12,GOLD,int(200*q),10)",
            "    seal(im,'THE BODY SWAP','you can feel located in another body',CYAN)",
        ]),
        ("obe", [
            "def vis_obe(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    d.ellipse((cx-40,cy-60,cx+40,cy+60),outline=(*INK,int(180*(1-r))),width=3)",
            "    if r>0.2:",
            "        q=(r-0.2)/0.8; glow_circle(im,cx,cy-80*q,12,GOLD,int(200*q),10)",
            "        d.line((cx,cy-55,cx,cy-80*q),fill=(*GOLD,int(160*q)),width=2)",
            "    seal(im,'OUT-OF-BODY EXPERIENCE','the self can be displaced from the body',GOLD)",
        ]),
        ("prediction", [
            "def vis_prediction(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    glow_circle(im,cx,cy,16,CYAN,int(200*r),14)",
            "    for i in range(6):",
            "        a=i*math.tau/6+t*0.06; q=clamp(r*3-i*0.1); if q<=0: continue",
            "        x=cx+math.cos(a)*(30+100*q); y=cy+math.sin(a)*(30+100*q)*0.35",
            "        d.line((cx,cy,x,y),fill=(*CYAN,int(150*q)),width=2)",
            "    seal(im,'PREDICTIVE PROCESSING OF BODY','the prediction IS the experience of being in a body',CYAN)",
        ]),
        ("kancukas_self", [
            "def vis_kancukas_self(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    labels=['AGENCY','KNOWLEDGE','TIME','CAUSALITY']",
            "    for i,l in enumerate(labels):",
            "        q=clamp(r*4-i*0.1); if q<=0: continue",
            "        x=lerp(w*0.25,w*0.75,i/3); y=lerp(h*0.25,h*0.60,i/3)",
            "        col=mix(CRIMSON,INK,i/3)",
            "        d.ellipse((x-25*q,y-15*q,x+25*q,y+15*q),outline=(*col,int(170*q)),width=2)",
            "        centered_text(d,(x,y),l,load_font(FONT_SANS_BOLD,int(h*0.020)),col)",
            "    seal(im,'KANCUKAS AS SELF-PARAMETERS','limited agency, knowledge, time, causality',CRIMSON)",
        ]),
        ("plasticity", [
            "def vis_plasticity(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    pts=[(cx+math.cos(i*math.tau/30)*(30+110*r),cy+math.sin(i*math.tau/30)*(30+110*r)*0.35) for i in range(31)]",
            "    glow_line(im,partial(pts,r),GOLD,width=4,alpha=220,blur=14)",
            "    for i in range(3):",
            "        a=(i-1)*0.5; q=clamp(r*3-i*0.12); if q<=0: continue",
            "        x=cx+math.cos(a)*100*q; y=cy+math.sin(a)*100*q",
            "        d.ellipse((x-10*q,y-10*q,x+10*q,y+10*q),fill=(*GREEN,int(160*q)))",
            "    seal(im,'THE SELF IS PLASTIC','updated in minutes - the mechanism of healing',GREEN)",
        ]),
    ]:
        p.add_vis(key, lines)
    for row in [
        ("The Rubber Hand Illusion", "Stroke a fake hand - it becomes yours in seconds.", 7.0, "rubber", {}),
        ("The Body Swap", "You can feel located in another body.", 7.5, "swap", {}),
        ("Out-of-Body Experience", "The self can be displaced from the body.", 7.5, "obe", {}),
        ("Predictive Processing of Body", "The prediction IS the experience of being in a body.", 8.0, "prediction", {}),
        ("Kancukas as Self-Parameters", "Limited agency, knowledge, time, causality.", 8.0, "kancukas_self", {}),
        ("The Self is Plastic", "Updated in minutes - the mechanism of healing.", 8.0, "plasticity", {}),
        ("You Are Not in Your Body", "The body is in consciousness, not the reverse.", 8.5, "obe", {}),
        ("The Bodily Self is a Model", "Your body image is a controlled hallucination.", 8.0, "prediction", {}),
        ("Synesthesia and Self", "Cross-modal integration creates the unified self.", 7.5, "swap", {}),
        ("The Minimal Self", "The sense of being a subject is the most basic prediction.", 8.0, "rubber", {}),
        ("The Extended Self", "Tools, possessions, others - all integrated into the self-model.", 8.5, "plasticity", {}),
        ("The Self is Not a Location", "It is not in the head or the body. It is a model.", 9.0, "kancukas_self", {}),
        ("Healing the Model", "Change the model, change the experience. Therapy updates the self.", 9.0, "plasticity", {}),
    ]:
        p.add_scene(*row)
    return p

def build_cooperation():
    p = Pack("cooperation", "The Body is a Cooperative Venture",
             "Seth - molecular cooperation", "The body exists through inner cooperation.",
             "cooperating node network",
             '"green":"cooperation", "gold":"value", "cyan":"cellular"')
    for key, lines in [
        ("cooperation_vis", [
            "def vis_cooperation_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    pts=[(cx+math.cos(i*math.tau/40)*(30+120*r),cy+math.sin(i*math.tau/40)*(30+120*r)*0.35) for i in range(41)]",
            "    glow_line(im,partial(pts,r),GREEN,width=3,alpha=200,blur=12)",
            "    for i in range(8):",
            "        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.08); if q<=0: continue",
            "        x=cx+math.cos(a)*(30+90*q); y=cy+math.sin(a)*(30+90*q)*0.35",
            "        d.ellipse((x-5*q,y-5*q,x+5*q,y+5*q),fill=(*PALE_GREEN,int(150*q)))",
            "    seal(im,'THE BODY EXISTS THROUGH COOPERATION','inner cooperative relationships bind every cell',GREEN)",
        ]),
        ("given_vis", [
            "def vis_given_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    glow_circle(im,cx,cy,16,GOLD,int(200*r),14)",
            "    for i in range(6):",
            "        a=i*math.tau/6+r*0.3; q=clamp(r*3-i*0.1); if q<=0: continue",
            "        x=cx+math.cos(a)*(40+80*q); y=cy+math.sin(a)*(40+80*q)*0.35",
            "        d.line((cx,cy,x,y),fill=(*GOLD,int(150*q)),width=2)",
            "    seal(im,'COOPERATION IS GIVEN','it is the gift of life - present at birth',GOLD)",
        ]),
        ("molecular_vis", [
            "def vis_molecular_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    rng=random.Random(42)",
            "    for i in range(40):",
            "        q=clamp(r*2-i*0.01); if q<=0: continue",
            "        a=rng.uniform(0,math.tau); rad=rng.uniform(20,130)*q",
            "        x=cx+math.cos(a)*rad; y=cy+math.sin(a)*rad*0.4",
            "        col=CYAN if rng.random()<0.4 else (GREEN if rng.random()<0.7 else GOLD)",
            "        d.ellipse((x-3*q,y-3*q,x+3*q,y+3*q),fill=(*col,int(140*q)))",
            "    glow_circle(im,cx,cy,10,GREEN,int(180*r),9)",
            "    seal(im,'MOLECULAR COOPERATION','the body speaks against chance',GREEN)",
        ]),
        ("value_fulfillment", [
            "def vis_value_fulfillment(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    glow_circle(im,cx,cy,14,GOLD,int(190*r),12)",
            "    for i in range(5):",
            "        q=clamp(r*5-i); if q<=0: continue",
            "        y=lerp(h*0.25,h*0.62,i/4); width=lerp(40,250,i/4)*q",
            "        d.line((w*0.50-width/2,y,w*0.50+width/2,y),fill=(*GOLD,int(180*q)),width=4)",
            "    seal(im,'VALUE FULFILLMENT','enhancing quality for all species',GOLD)",
        ]),
        ("altruism_vis", [
            "def vis_altruism_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    for i in range(6):",
            "        a=i*math.tau/6+t*0.06; q=clamp(r*4-i*0.1); if q<=0: continue",
            "        x=cx+math.cos(a)*(20+100*q); y=cy+math.sin(a)*(20+100*q)*0.35",
            "        col=mix(GREEN,CYAN,i/5)",
            "        d.line((cx,cy,x,y),fill=(*col,int(160*q)),width=2)",
            "        arrow(d,(cx+(x-cx)*0.85,cy+(y-cy)*0.85),(x,y),col,2,8)",
            "    seal(im,'INNATE ALTRUISM','a natural bent for caring',GREEN)",
        ]),
        ("faith_cell", [
            "def vis_faith_cell(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    glow_circle(im,cx,cy,12,GOLD,int(180*r),10)",
            "    for i in range(6):",
            "        q=clamp(r*6-i); if q<=0: continue",
            "        y=lerp(h*0.22,h*0.62,i/5); col=mix(CYAN,GREEN,i/5)",
            "        d.ellipse((w*0.50-10*q,y-10*q,w*0.50+10*q,y+10*q),outline=(*col,int(170*q)),width=2)",
            "    seal(im,'EACH CELL BELIEVES','built-in faith in a better tomorrow',CYAN)",
        ]),
        ("health_vis", [
            "def vis_health_vis(im,u,t,p):",
            "    w,h=im.size; cx,cy=w*0.50,h*0.42; r=ease(u); d=ImageDraw.Draw(im)",
            "    pts=[(cx+math.cos(i*math.tau/30)*(30+110*r),cy+math.sin(i*math.tau/30)*(30+110*r)*0.35) for i in range(31)]",
            "    glow_line(im,partial(pts,r),GREEN,width=4,alpha=220,blur=14)",
            "    for i in range(8):",
            "        a=i*math.tau/8+t*0.05; q=clamp(r*4-i*0.08); if q<=0: continue",
            "        x=cx+math.cos(a)*(30+90*q); y=cy+math.sin(a)*(30+90*q)*0.35",
            "        d.line((cx,cy,x,y),fill=(*GREEN,int(140*q)),width=2)",
            "    seal(im,'HEALTH AS COOPERATION','illness is broken communication',GREEN)",
        ]),
    ]:
        p.add_vis(key, lines)
    for row in [
        ("The Body Exists Through Cooperation", "Inner cooperative relationships bind every cell.", 7.5, "cooperation_vis", {}),
        ("Cooperation is Given", "It is the gift of life - present at birth.", 7.5, "given_vis", {}),
        ("Molecular Cooperation", "The body speaks against chance. Molecules work together.", 8.0, "molecular_vis", {}),
        ("Value Fulfillment", "Enhancing quality for all species.", 8.0, "value_fulfillment", {}),
        ("Innate Altruism", "A natural bent for caring. Helpfulness is biological.", 7.5, "altruism_vis", {}),
        ("Each Cell Believes", "Built-in faith in a better tomorrow.", 7.5, "faith_cell", {}),
        ("Health as Cooperation", "Illness is broken communication. Health is restored dialogue.", 8.5, "health_vis", {}),
        ("The Cellular Commonweal", "Every cell contributes to the whole. The body is a society.", 8.0, "cooperation_vis", {}),
        ("Cooperation is Biological", "Competition is derivative. Cooperation is the ground.", 8.0, "molecular_vis", {}),
        ("The Gift Economy", "Cells give and receive continuously. The body is a gift economy.", 8.5, "given_vis", {}),
        ("Altruism is Innate", "Helpfulness is not a cultural invention. It is encoded in life.", 8.0, "altruism_vis", {}),
        ("The Body Trusts", "Every cell trusts the whole. That trust IS health.", 8.5, "faith_cell", {}),
        ("The Cooperative Venture", "You are not one thing. You are a cooperation that learned to say 'I'.", 9.5, "cooperation_vis", {}),
        ("Restoring Communication", "Healing is re-establishing the lines of cooperation.", 9.0, "health_vis", {}),
    ]:
        p.add_scene(*row)
    return p

if __name__ == "__main__":
    packs = [
        build_morphospace(),
        build_free_energy(),
        build_consciousness_container(),
        build_time_is_forgetting(),
        build_svatantrya(),
        build_objects_as_actions(),
        build_psyche_gestalt(),
        build_dna_antenna(),
        build_constructed_self(),
        build_cooperation(),
    ]
    for p in packs:
        write_pack(p)
    print("\nDone generating packs.")
