from pathlib import Path
import re,json,math,random,subprocess,shutil,csv,textwrap,zipfile,os
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('/mnt/data/corbin_world_between_worlds_film_pack')
if ROOT.exists() and os.environ.get('RESUME')!='1': shutil.rmtree(ROOT)
ROOT.mkdir(exist_ok=True); AUDIO=ROOT/'audio_segments'; AUDIO.mkdir(exist_ok=True); CLIPS=ROOT/'clips'; CLIPS.mkdir(exist_ok=True); THUMBS=ROOT/'thumbs'; THUMBS.mkdir(exist_ok=True)
W,H,FPS=1280,720,8
BG=(244,239,227); INK=(30,25,27); POR=(121,38,56); LAP=(42,70,110); GOLD=(174,133,52); GREY=(112,105,100); PALE=(224,215,199); WHITE=(252,250,245); DARK=(42,37,44)
fp=next((p for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf','/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if Path(p).exists()),None)
TITLE=ImageFont.truetype(fp,38); CHAPTER=ImageFont.truetype(fp,23); TERM=ImageFont.truetype(fp,28); SMALL=ImageFont.truetype(fp,18); TINY=ImageFont.truetype(fp,14)
SOURCE='''# the world between worlds

> **Title:** The World Between Worlds
>
> **ROs:** ro-corbin-imaginal-expanded (18 passages), ro-corbin-imaginal (4 passages)

---

What if there is a world that is neither physical nor spiritual — but somewhere in between? And what if that world is more real than either? Henry Corbin, the great French scholar of Iranian Sufism, spent his life documenting the evidence for this world. He called it the *mundus imaginalis* — the imaginal world, and he believed it was the place where everything that matters actually happens.

---

Corbin saw a third world between the material and the spiritual — the *mundus imaginalis*, the connective tissue between matter and spirit.

> Between the world of pure spiritual Lights (Luces victoriales, the world of the 'Mothers' in the terminology of Ishraq) and the sensory universe, at the boundary of the ninth Sphere (the Sphere of Spheres) there opens a mundus imaginalis which is a concrete spiritual world of archetype-Figures, apparitional Forms, Angels of species and of individuals; by philosophical dialectics its necessity is deduced and its plane situated; vision of it in actuality is vouchsafed to the visionary apperception of the active Imagination. — ro-corbin-imaginal-expanded, p_001

The active Imagination is an organ of perception, like the eye or the ear, tuned to a real world — ontologically intermediate between matter and spirit — not "make-believe" in the modern sense. The figures you see in this world are real beings in a real place, beyond the reach of physical eyes.

> This suprasensory Orient governs the primary phenomenon of the Gnostic's orientation toward his country of origin. The Orient-origin identified with the center, with the heavenly north pole, heralds access to the beyond, where vision becomes real history, the history of the soul, and where every visionary event symbolizes a spiritual state; or, as the Ishraqiyun say, it is the climate "where what is bodily becomes spirit and what is spiritual acquires a body." — ro-corbin-imaginal-expanded, p_002

The imaginal world has its own geography. Its "north" is not the magnetic pole; it is the cosmic north, the direction of origin, the place your soul came from before it entered this body. To turn toward the imaginal world is to turn toward home. And in that world, the rules are different: spirit takes on form, and matter becomes luminous. The two poles of existence that seem so separate here are continuous there.

> It is the heavenly entity, the philosopher's Angel, conjoined with his star, which rules him and opens the doors of wisdom for him, teaches him what is difficult, reveals to him what is right, in sleeping as in waking. — ro-corbin-imaginal-expanded, p_003

This is the Perfect Nature — the being that has been with you since before your birth, the angel that is your personal guide. The Hermetic tradition called it the "philosopher's Angel"; in the Sufi tradition, it is the *shakhs nurani* — the person of light. It is a real being, and you can meet it — neither a symbol nor a psychological projection.

> Having cut in two the thread spun by a spider, the prince puts it together again, saying: 1 x 1. This is also the formula that we suggested above, because he who deciphers it holds the key to the secret that preserves him both from pseudomystical monism (whose formula is 1 = 1) and from abstract monotheism which is content to superimpose an Ens supremum on the multitude of beings (n + 1). — ro-corbin-imaginal-expanded, p_005

The 1×1 formula is Corbin's master key. You and your Guide are not identical (that would be 1=1, the false merger where you lose yourself). You are not separate (that would be n+1, the distant God who never touches you). You are 1×1 — a unity that preserves difference, a relationship that does not dissolve the partners. The spider's thread is the apparent barrier between you and the Angel; the prince cuts it and re-joins it, showing that separation and union are the same act.

> When the circle of the face has become pure, it effuses lights as a spring pours forth its water... Before you, before your face, there is another Face also of light, irradiating lights... In reality this Face is your own face and this sun is the sun of the Spirit (shams al-ruh) that goes to and fro in your body. Next, the whole of your person is immersed in purity, and suddenly you are gazing at a person of light (shakhs nurani) who is also irradiating lights... This person of light before you is called in Sufi terminology the suprasensory Guide (moqaddam al-ghayb). — ro-corbin-imaginal-expanded, p_007

Najm Kobra, the 13th-century Sufi master, described the meeting with terrifying precision. The face becomes pure and begins to radiate light. Then another face appears — made of light, radiating light. You realize this face is your own face, but not the one you see in the mirror. It is the face you had before you were born, the face you will have after you die. The two faces look at each other, and the looking itself is the relationship.

> Of all spiritual practices... the dhikr is the practice most apt to free spiritual energy, that is, to allow the particle of divine light which is in the mystic to rejoin its like... The fire of the dhikr is visualized as a pure and ardent blaze, animated by a rapid upward movement... It sets fire to all that is there to be consumed, and sheds light on any darkness it may encounter. If light is there already, the two lights associate with each other and there is light upon light. — ro-corbin-imaginal-expanded, p_008

The *dhikr* — the repetition of divine names — is the technology that opens the door to the imaginal world: a fire that burns away the obstacles between you and the Person of Light, more than a mere tool for concentrating the mind. When the fire meets light in you, the two lights combine: *light upon light*. When it meets darkness, it burns it away. The *dhikr* is both the path and the destination — the repetition itself is the ascent, and when it becomes continuous, when the Name is always present in the heart, the door between the worlds dissolves entirely.

> Then who art thou, whose beauty outshines all other beauty ever contemplated in the terrestrial world? I am thine own Daena. I was loved, thou hast made me more loved still. I was beautiful, thou hast made me still more beautiful. — ro-corbin-imaginal-expanded, p_011

The Zoroastrian tradition called the Guide the *Daena* — the soul's own celestial counterpart, who meets you at the Chinvat Bridge after death. The dialogue is breathtaking: "Who art thou?" — "I am your own Daena. I was loved, you made me more loved. I was beautiful, you made me more beautiful." The Guide grows as you grow; your work on yourself makes the Angel more beautiful. Corbin insists on a crucial distinction: the Guide is your celestial counterpart, while the shadow belongs to your history. The dark envelope of the personal unconscious must be burned away before the Person of Light can appear — one belongs to your history, the other to your eternity.

> Thou, my lord and prince, my most holy angel, my precious spiritual being, Thou art the Spirit who gave birth to me, and Thou art the Child to whom my spirit gives birth... Thou who art clothed in the most brilliant of divine Lights... may Thou manifest Thyself to me in the most beautiful of epiphanies, show me the light of Thy dazzling face, be for me the mediator... lift the veils of darkness from my heart... — ro-corbin-imaginal-expanded, p_013

Sohravardi's psalm to his Perfect Nature reveals the paradoxical relationship at the heart of the imaginal world. The Angel is both parent and child. It gave birth to you (as your celestial origin), and you give birth to it (as your realized Guide). The relationship is mutual, recursive, and eternal. You and your Angel create each other.

---

The *mundus imaginalis* is a real world — with its own geography, its own inhabitants, its own laws — neither a metaphor nor a psychological projection. You have access to it right now through the active Imagination, which is perception rather than fantasy. Every time you have felt a presence beyond the physical, seen with the inner eye, or known something without knowing how — you have touched the edge of that world.

What Corbin offers is a method rather than a belief system. The active Imagination can be trained; the *dhikr* can be practiced; the encounter with the Person of Light can be prepared for. And when it happens, you will not doubt its reality — because the *mundus imaginalis* is more real than the physical world. Physical objects pass away; the Person of Light does not.

The door is always open. The Guide is always waiting. The only question is whether you will close your physical eyes and open the other ones.
'''
(ROOT/'source_essay.md').write_text(SOURCE,encoding='utf-8')
P=[
('opening','The World Between Worlds',"What if there is a world that is neither physical nor spiritual — but somewhere in between? And what if that world is more real than either? Henry Corbin, the great French scholar of Iranian Sufism, spent his life documenting the evidence for this world. He called it the mundus imaginalis — the imaginal world, and he believed it was the place where everything that matters actually happens."),
('third','The Third World',"Corbin saw a third world between the material and the spiritual — the mundus imaginalis, the connective tissue between matter and spirit."),
('third','The Ninth Sphere',"Between the world of pure spiritual Lights, Luces victoriales, the world of the 'Mothers' in the terminology of Ishraq, and the sensory universe, at the boundary of the ninth Sphere, the Sphere of Spheres, there opens a mundus imaginalis which is a concrete spiritual world of archetype-Figures, apparitional Forms, Angels of species and of individuals; by philosophical dialectics its necessity is deduced and its plane situated; vision of it in actuality is vouchsafed to the visionary apperception of the active Imagination."),
('imagination','The Organ of Perception',"The active Imagination is an organ of perception, like the eye or the ear, tuned to a real world — ontologically intermediate between matter and spirit — not make-believe in the modern sense. The figures you see in this world are real beings in a real place, beyond the reach of physical eyes."),
('north','The Suprasensory Orient',"This suprasensory Orient governs the primary phenomenon of the Gnostic's orientation toward his country of origin. The Orient-origin identified with the center, with the heavenly north pole, heralds access to the beyond, where vision becomes real history, the history of the soul, and where every visionary event symbolizes a spiritual state; or, as the Ishraqiyun say, it is the climate where what is bodily becomes spirit and what is spiritual acquires a body."),
('north','The Geography of Home',"The imaginal world has its own geography. Its north is not the magnetic pole; it is the cosmic north, the direction of origin, the place your soul came from before it entered this body. To turn toward the imaginal world is to turn toward home. And in that world, the rules are different: spirit takes on form, and matter becomes luminous. The two poles of existence that seem so separate here are continuous there."),
('guide','The Philosopher’s Angel',"It is the heavenly entity, the philosopher's Angel, conjoined with his star, which rules him and opens the doors of wisdom for him, teaches him what is difficult, reveals to him what is right, in sleeping as in waking."),
('guide','The Perfect Nature',"This is the Perfect Nature — the being that has been with you since before your birth, the angel that is your personal guide. The Hermetic tradition called it the philosopher's Angel; in the Sufi tradition, it is the shakhs nurani — the person of light. It is a real being, and you can meet it — neither a symbol nor a psychological projection."),
('thread','One Times One',"Having cut in two the thread spun by a spider, the prince puts it together again, saying: one times one. This is also the formula that we suggested above, because he who deciphers it holds the key to the secret that preserves him both from pseudomystical monism, whose formula is one equals one, and from abstract monotheism which is content to superimpose an Ens supremum on the multitude of beings, n plus one."),
('thread','A Unity Preserving Difference',"The one times one formula is Corbin's master key. You and your Guide are not identical, that would be one equals one, the false merger where you lose yourself. You are not separate, that would be n plus one, the distant God who never touches you. You are one times one — a unity that preserves difference, a relationship that does not dissolve the partners. The spider's thread is the apparent barrier between you and the Angel; the prince cuts it and re-joins it, showing that separation and union are the same act."),
('faces','The Face of Light',"When the circle of the face has become pure, it effuses lights as a spring pours forth its water. Before you, before your face, there is another Face also of light, irradiating lights. In reality this Face is your own face and this sun is the sun of the Spirit, shams al-ruh, that goes to and fro in your body. Next, the whole of your person is immersed in purity, and suddenly you are gazing at a person of light, shakhs nurani, who is also irradiating lights. This person of light before you is called in Sufi terminology the suprasensory Guide, moqaddam al-ghayb."),
('faces','Two Faces Looking',"Najm Kobra, the thirteenth-century Sufi master, described the meeting with terrifying precision. The face becomes pure and begins to radiate light. Then another face appears — made of light, radiating light. You realize this face is your own face, but not the one you see in the mirror. It is the face you had before you were born, the face you will have after you die. The two faces look at each other, and the looking itself is the relationship."),
('dhikr','The Fire of Dhikr',"Of all spiritual practices, the dhikr is the practice most apt to free spiritual energy, that is, to allow the particle of divine light which is in the mystic to rejoin its like. The fire of the dhikr is visualized as a pure and ardent blaze, animated by a rapid upward movement. It sets fire to all that is there to be consumed, and sheds light on any darkness it may encounter. If light is there already, the two lights associate with each other and there is light upon light."),
('dhikr','The Name Becomes the Door',"The dhikr — the repetition of divine names — is the technology that opens the door to the imaginal world: a fire that burns away the obstacles between you and the Person of Light, more than a mere tool for concentrating the mind. When the fire meets light in you, the two lights combine: light upon light. When it meets darkness, it burns it away. The dhikr is both the path and the destination — the repetition itself is the ascent, and when it becomes continuous, when the Name is always present in the heart, the door between the worlds dissolves entirely."),
('daena','The Daena Speaks',"Then who art thou, whose beauty outshines all other beauty ever contemplated in the terrestrial world? I am thine own Daena. I was loved, thou hast made me more loved still. I was beautiful, thou hast made me still more beautiful."),
('daena','The Chinvat Bridge',"The Zoroastrian tradition called the Guide the Daena — the soul's own celestial counterpart, who meets you at the Chinvat Bridge after death. The dialogue is breathtaking: Who art thou? I am your own Daena. I was loved, you made me more loved. I was beautiful, you made me more beautiful. The Guide grows as you grow; your work on yourself makes the Angel more beautiful. Corbin insists on a crucial distinction: the Guide is your celestial counterpart, while the shadow belongs to your history. The dark envelope of the personal unconscious must be burned away before the Person of Light can appear — one belongs to your history, the other to your eternity."),
('recursive','Parent and Child',"Thou, my lord and prince, my most holy angel, my precious spiritual being, Thou art the Spirit who gave birth to me, and Thou art the Child to whom my spirit gives birth. Thou who art clothed in the most brilliant of divine Lights, may Thou manifest Thyself to me in the most beautiful of epiphanies, show me the light of Thy dazzling face, be for me the mediator, lift the veils of darkness from my heart."),
('recursive','Mutual Birth',"Sohravardi's psalm to his Perfect Nature reveals the paradoxical relationship at the heart of the imaginal world. The Angel is both parent and child. It gave birth to you, as your celestial origin, and you give birth to it, as your realized Guide. The relationship is mutual, recursive, and eternal. You and your Angel create each other."),
('return','A Real World',"The mundus imaginalis is a real world — with its own geography, its own inhabitants, its own laws — neither a metaphor nor a psychological projection. You have access to it right now through the active Imagination, which is perception rather than fantasy. Every time you have felt a presence beyond the physical, seen with the inner eye, or known something without knowing how — you have touched the edge of that world."),
('return','A Method Rather Than a Belief',"What Corbin offers is a method rather than a belief system. The active Imagination can be trained; the dhikr can be practiced; the encounter with the Person of Light can be prepared for. And when it happens, you will not doubt its reality — because the mundus imaginalis is more real than the physical world. Physical objects pass away; the Person of Light does not."),
('return','The Other Eyes',"The door is always open. The Guide is always waiting. The only question is whether you will close your physical eyes and open the other ones.")]
(ROOT/'narration_script.txt').write_text('\n\n'.join(x[2] for x in P),encoding='utf-8')
def wc(s): return len(re.findall(r"\b[\wÀ-ž'’-]+\b",s))
def splitlong(s,m=20):
 if wc(s)<=m:return [s.strip()]
 ps=re.split(r'(?<=[,;:—])\s+',s)
 if len(ps)==1:
  ws=s.split(); k=min(m,len(ws)//2); return [' '.join(ws[:k])]+splitlong(' '.join(ws[k:]),m)
 out=[];cur=''
 for p in ps:
  c=(cur+' '+p).strip()
  if cur and wc(c)>m: out+=splitlong(cur,m);cur=p
  else:cur=c
 if cur:out+=splitlong(cur,m)
 return out
def chunks(s):
 ss=re.split(r'(?<=[.!?])\s+(?=[A-Z“"I])',s.strip()); a=[]
 for x in ss:a+=splitlong(x)
 out=[];i=0
 while i<len(a):
  c=a[i].strip()
  if wc(c)<10 and i+1<len(a) and wc(c+' '+a[i+1])<=20:c+=' '+a[i+1];i+=1
  if out and wc(c)<8 and wc(out[-1]+' '+c)<=20:out[-1]+=' '+c
  else:out.append(c)
  i+=1
 return out
S=[]
for pi,(ch,ct,txt) in enumerate(P):
 for ci,x in enumerate(chunks(txt)):S.append({'paragraph_index':pi,'chapter':ch,'chapter_title':ct,'chapter_start':ci==0,'text':x})
def probe(p):
 r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)],capture_output=True,text=True,check=True);return float(r.stdout.strip())
def speak(txt,p):
 q=p.with_suffix('.txt');q.write_text(txt,encoding='utf-8');subprocess.run(['espeak','-v','en-gb','-s','145','-p','42','-a','155','-f',str(q),'-w',str(p)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);q.unlink()
# split on real audio > 9.6
q=list(S);S=[];n=0
while q:
 s=q.pop(0);tmp=AUDIO/f'_p{n}.wav';n+=1;speak(s['text'],tmp);dur=probe(tmp);tmp.unlink()
 if dur>9.6 and wc(s['text'])>9:
  ws=s['text'].split();mid=len(ws)//2;cands=range(max(5,mid-4),min(len(ws)-4,mid+5));k=min(cands,key=lambda j:abs(j-mid)+(0 if re.search(r'[,;:—.!?]$',ws[j-1]) else 2));a=dict(s);b=dict(s);a['text']=' '.join(ws[:k]);b['text']=' '.join(ws[k:]);b['chapter_start']=False;q=[a,b]+q
 else:S.append(s)
for i,s in enumerate(S,1):
 wav=AUDIO/f's{i:03d}.wav'
 if not wav.exists():
  raw=AUDIO/f's{i:03d}_raw.wav';speak(s['text'],raw);rd=probe(raw);target=max(5.15,min(9.95,rd+.35));subprocess.run(['ffmpeg','-y','-i',str(raw),'-af',f'apad=pad_dur={max(0,target-rd):.3f}','-t',f'{target:.3f}',str(wav)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);raw.unlink()
 s['duration']=probe(wav);s['shot_id']=f's{i:03d}'
MOD={
'opening':['threshold_triad','between_worlds','corbin_orbit','room_between'],'third':['three_worlds','ninth_sphere','imaginal_figures','bridge_tissue'],'imagination':['active_eye','eye_city','physical_eyes','apparitional_forms'],'north':['cosmic_compass','orient_path','body_spirit_exchange','map_home'],'guide':['angel_star','wisdom_door','sleep_waking','person_light'],'thread':['spider_thread','cut_rejoin','formula_one','relation_orbit'],'faces':['face_spring','two_faces','spirit_sun','gaze_relation'],'dhikr':['name_spiral','fire_veil','light_upon_light','door_dissolve'],'daena':['chinvat_bridge','daena_figure','beauty_growth','shadow_eternity'],'recursive':['parent_child','mutual_birth','recursive_halo','veil_heart'],'return':['world_geography','trained_eye','objects_pass','other_eyes']}
CAP={'opening':['','mundus imaginalis','',''],'third':['matter • imaginal • spirit','the ninth sphere','',''],'imagination':['active Imagination','','',''],'north':['the cosmic north','the country of origin','',''],'guide':['the Perfect Nature','','sleeping • waking','shakhs nūrānī'],'thread':['','cut • rejoin','1 × 1','difference without separation'],'faces':['','the other Face','shams al-rūḥ','the looking is the relationship'],'dhikr':['dhikr','','light upon light',''],'daena':['the Chinvat Bridge','Daena','','history • eternity'],'recursive':['parent • child','mutual birth','',''],'return':['a real world','perception, not fantasy','','open the other eyes']}
cnt={}
for s in S:
 n=cnt.get(s['chapter'],0);s['mode']=MOD[s['chapter']][n%4];s['variant']=n//4;s['caption']=CAP[s['chapter']][n%4];cnt[s['chapter']]=n+1
CONT={'opening':'three apertures and the central room','third':'the intermediate domain','imagination':'the inner eye','north':'the northward axis','guide':'the personal Guide','thread':'the relational filament','faces':'the line of sight','dhikr':'the ascending Name','daena':'the bridge and counterpart','recursive':'reciprocal generation','return':'the open door'}
def lerp(a,b,t):return a+(b-a)*t
def smooth(a,b,t):
 if t<=a:return 0
 if t>=b:return 1
 x=(t-a)/(b-a);return x*x*(3-2*x)
def mix(a,b,t):return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def circ(d,x,y,r,o=INK,w=2,f=None):d.ellipse((x-r,y-r,x+r,y+r),outline=o,width=w,fill=f)
def line(d,p,c=INK,w=2):d.line(p,fill=c,width=w)
def arc(d,b,a1,a2,c=INK,w=2):d.arc(b,start=a1,end=a2,fill=c,width=w)
def poly(d,p,o=INK,w=2,f=None):
 d.polygon(p,outline=o,fill=f)
 if o and w>1:
  for i in range(len(p)):d.line([p[i],p[(i+1)%len(p)]],fill=o,width=w)
def radial(cx,cy,r,n,ph=0):return [(cx+r*math.cos(ph+2*math.pi*i/n),cy+r*math.sin(ph+2*math.pi*i/n)) for i in range(n)]
def star(d,cx,cy,r1,r2,n=8,o=GOLD,w=2,ph=0,f=None):
 p=[]
 for i in range(n*2):
  a=ph+math.pi*i/n;r=r1 if i%2==0 else r2;p.append((cx+r*math.cos(a),cy+r*math.sin(a)))
 poly(d,p,o,w,f)
def arch(d,x0,y0,x1,y1,o=INK,w=2):d.line((x0,y1,x0,(y0+y1)/2),fill=o,width=w);d.line((x1,y1,x1,(y0+y1)/2),fill=o,width=w);d.arc((x0,y0,x1,y1-(y1-y0)*.3),180,360,fill=o,width=w)
def spiral(cx,cy,r0,r1,turn,n=180,ph=0):return [(cx+lerp(r0,r1,i/(n-1))*math.cos(ph+turn*2*math.pi*i/(n-1)),cy+lerp(r0,r1,i/(n-1))*math.sin(ph+turn*2*math.pi*i/(n-1))) for i in range(n)]
def arrow(d,p1,p2,c=GREY,w=2):
 line(d,[p1,p2],c,w);a=math.atan2(p2[1]-p1[1],p2[0]-p1[0])
 for off in [2.6,-2.6]:line(d,[p2,(p2[0]+10*math.cos(a+off),p2[1]+10*math.sin(a+off))],c,w)
def face(d,cx,cy,side=1,col=INK,sc=1):
 p=[(cx,cy-90*sc),(cx+side*35*sc,cy-80*sc),(cx+side*58*sc,cy-40*sc),(cx+side*48*sc,cy-5*sc),(cx+side*70*sc,cy+15*sc),(cx+side*43*sc,cy+30*sc),(cx+side*38*sc,cy+70*sc),(cx,cy+95*sc)];line(d,p,col,3);circ(d,cx+side*38*sc,cy-26*sc,4*sc,col,1,col)
def base(seed):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);r=random.Random(seed)
 for _ in range(180):d.point((r.randrange(W),r.randrange(H)),fill=mix(PALE,BG,r.random()))
 for i in range(12):d.rectangle((i,i,W-i-1,H-i-1),outline=mix(PALE,BG,.5),width=1)
 return im
BASE=[base(i) for i in range(11)]
def label(d,s,t):
 if s['chapter_start']:
  a=1-smooth(.42,.78,t);d.text((58,40),s['chapter_title'],font=CHAPTER,fill=mix(BG,POR,a))
 if s['caption']:
  a=smooth(.55,.75,t)*(1-smooth(.92,1,t));bb=d.textbbox((0,0),s['caption'],font=TERM);d.text(((W-bb[2]+bb[0])/2,H-82),s['caption'],font=TERM,fill=mix(BG,POR,a))
def frame(s,t):
 im=BASE[hash(s['chapter'])%11].copy();d=ImageDraw.Draw(im);cx,cy=640,370;m=s['mode'];p=smooth(0,1,t);line(d,[(100,590),(1180,590)],PALE,1)
 if m=='threshold_triad':
  for i,x in enumerate([350,640,930]):
   arch(d,x-85,180,x+85,510,[INK,GOLD,LAP][i],3);line(d,[(x,480),(cx,390)],PALE,2)
   if i==1:star(d,x,330,26*p,11*p,8,GOLD,2,t*.1)
   elif i==0:
    for y in range(300,431,32):line(d,[(x-55,y),(x+55,y)],GREY,1)
   else:
    for q in radial(x,350,55,7,t*.06):circ(d,*q,4,LAP,1,LAP)
  circ(d,cx,390,15+8*math.sin(t*math.pi),POR,1,POR)
 elif m=='between_worlds':
  for ix in range(6):
   for iy in range(6):
    x=250+ix*38;y=260+iy*38;d.rectangle((x-12,y-12,x+12,y+12),fill=[GREY,PALE,INK][(ix+iy)%3])
  for q in radial(1010,380,130,11,t*.08):star(d,*q,9,3,6,GOLD,1)
  arch(d,505,170,775,535,POR,3)
  for i in range(7):q=i/6;circ(d,lerp(450,830,q),420-120*math.sin(math.pi*q),5,GOLD if i%2 else POR,1,GOLD if i%2 else POR)
 elif m=='corbin_orbit':
  d.rectangle((510,250,770,480),outline=INK,width=3)
  for i in range(8):line(d,[(540,285+i*22),(740,285+i*22)],GREY if i>2 else INK,1)
  circ(d,cx,365,22,POR,1,POR)
  for r,c in [(90,GOLD),(150,LAP),(220,INK)]:arc(d,(cx-r,365-r,cx+r,365+r),10+t*20,310+t*20,c,2)
 elif m=='room_between':
  d.rectangle((210,210,490,530),outline=INK,width=3);d.rectangle((790,210,1070,530),outline=LAP,width=3);q=smooth(.12,.72,t);d.polygon([(490,210),(790,210),(790,530),(490,530)],fill=mix(BG,WHITE,q),outline=POR)
  for i in range(6):line(d,[(540+i*40,250),(540+i*40,490)],mix(BG,GOLD,q),1)
  star(d,cx,370,34*q,14*q,8,GOLD,2,t*.1)
 elif m=='three_worlds':
  for y0,y1,c,txt in [(160,300,INK,'matter'),(300,460,POR,'imaginal'),(460,600,LAP,'spirit')]:d.rectangle((240,y0,1040,y1),outline=c,width=2);d.text((260,y0+14),txt,font=SMALL,fill=c)
  for x in range(360,941,90):line(d,[(x+18*math.sin(y*.035+t*2+x),y) for y in range(190,570,16)],GOLD,2)
 elif m=='ninth_sphere':
  for r,c in [(70,POR),(120,GOLD),(175,LAP),(235,INK),(285,GREY)]:circ(d,cx,360,r,c,2)
  a=math.pi*1.72;x=cx+285*math.cos(a);y=360+285*math.sin(a);star(d,x,y,22+10*p,9+4*p,8,GOLD,2,t*.1);line(d,[(x,y),(cx,360)],PALE,1)
 elif m=='imaginal_figures':
  d.rectangle((330,180,950,540),outline=POR,width=2)
  q=smooth(.1,.65,t);arc(d,(350,270,500,450),280,70,GOLD,3);arc(d,(410,270,560,450),110,250,GOLD,3);face(d,640,350,1,POR,q);line(d,[(850,460),(850,280)],INK,3)
  for a in [-2.6,-2.2,-.95,-.5]:line(d,[(850,350),(850+90*q*math.cos(a),350+90*q*math.sin(a))],INK,2)
 elif m=='bridge_tissue':
  for k,c in [(0,INK),(1,GOLD),(2,LAP)]:line(d,[(180+920*i/179,360+100*math.sin(i/179*math.pi*4+k*2.1+t*.8)) for i in range(180)],c,3 if k==1 else 2)
  circ(d,180,360,22,INK,2);circ(d,1100,360,22,LAP,2)
 elif m=='active_eye':
  q=smooth(.05,.62,t);arc(d,(330,210,950,520),200,340,INK,4);arc(d,(330,210,950,520),20,160,INK,4);circ(d,cx,365,80*q,POR,3);arch(d,cx-45*q,300,cx+45*q,430,GOLD,2);star(d,cx,360,22*q,9*q,8,GOLD,2,t*.1)
 elif m=='eye_city':
  circ(d,cx,360,210,INK,3);circ(d,cx,360,92,POR,2)
  for x,w,h in [(500,55,130),(580,45,190),(650,70,150),(740,48,220)]:d.rectangle((x,500-h,x+w,500),outline=INK,width=2);star(d,x+w/2,500-h+35,11,4,6,GOLD,1)
  arc(d,(430,150,850,570),200,340,GOLD,1)
 elif m=='physical_eyes':
  for x in [430,850]:q=1-smooth(.12,.65,t);arc(d,(x-120,270-q*40,x+120,450+q*40),200,340,INK,3);arc(d,(x-120,270-q*40,x+120,450+q*40),20,160,INK,3)
  q=smooth(.28,.86,t);star(d,cx,360,45*q,17*q,10,GOLD,2,t*.12)
 elif m=='apparitional_forms':
  for i,(x,y,c) in enumerate([(460,360,POR),(640,330,GOLD),(820,380,LAP)]):r=70+15*math.sin(t*2+i);poly(d,radial(x,y,r,6+i,t*.08*(i+1)),c,2);line(d,[(x,y),(cx,430)],PALE,1)
 elif m=='cosmic_compass':
  circ(d,cx,365,230,INK,3)
  for a in [0,math.pi/2,math.pi,3*math.pi/2]:line(d,[(cx,365),(cx+200*math.cos(a),365+200*math.sin(a))],GREY,2)
  a=lerp(math.pi*.7,-math.pi/2,p);poly(d,[(cx+170*math.cos(a),365+170*math.sin(a)),(cx+12*math.cos(a+2.5),365+12*math.sin(a+2.5)),(cx+12*math.cos(a-2.5),365+12*math.sin(a-2.5))],POR,2,POR);star(d,cx,125,24,9,8,GOLD,2);d.text((632,90),'N',font=TERM,fill=POR)
 elif m=='orient_path':
  for y in range(430,581,30):line(d,[(300,y),(980,y)],PALE,1)
  pts=[(640,575),(570,510),(700,455),(610,390),(670,320),(640,220)];line(d,pts,POR,4);q=pts[min(len(pts)-1,int(p*len(pts)))];circ(d,*q,7,GOLD,1,GOLD);star(d,640,175,28,10,8,GOLD,2)
 elif m=='body_spirit_exchange':
  b=[(370,520),(340,420),(360,300),(420,245),(480,300),(500,420),(470,520)];poly(d,b,INK,3,mix(BG,PALE,.4))
  for i in range(12):a=i*math.pi/6;r=80+30*math.sin(t*2+i);star(d,850+r*math.cos(a),370+r*math.sin(a),9,3,6,GOLD,1)
  for i in range(18):u=(i/18+t*.35)%1;circ(d,lerp(480,780,u),370+50*math.sin(u*math.pi*4+i),3,GOLD if i%2 else POR,1,GOLD if i%2 else POR)
  poly(d,[(800,520),(770,420),(790,300),(850,245),(910,300),(930,420),(900,520)],mix(GREY,GOLD,p),3)
 elif m=='map_home':
  for r in [60,100,145,195,245]:line(d,[(cx+(r+12*math.sin(a*3+t*2+r))*math.cos(a),365+(r+12*math.sin(a*3+t*2+r))*.72*math.sin(a)) for a in [2*math.pi*i/99 for i in range(100)]],GREY if r>150 else POR,1 if r>150 else 2)
  circ(d,cx,365,11,GOLD,1,GOLD);d.text((612,345),'home',font=SMALL,fill=INK)
 elif m=='angel_star':
  star(d,cx,145,36,14,10,GOLD,2,t*.08);circ(d,cx,360,25,INK,3);line(d,[(cx,385),(cx,500)],INK,4);line(d,[(cx,410),(550,460)],INK,3);line(d,[(cx,410),(730,460)],INK,3);line(d,[(cx,500),(590,570)],INK,3);line(d,[(cx,500),(690,570)],INK,3);line(d,[(cx+18*math.sin(i*.7+t*2),y) for i,y in enumerate(range(175,340,14))],POR,3)
 elif m=='wisdom_door':
  arch(d,460,150,820,540,INK,3);q=smooth(.08,.75,t);poly(d,[(460,300),(640,260),(640,540),(460,540)],POR,3,mix(BG,PALE,.25));poly(d,[(820,300),(640,260),(640,540),(820,540)],LAP,3,mix(BG,PALE,.25));gap=120*q;line(d,[(640-gap,300),(640-gap,535)],GOLD,2);line(d,[(640+gap,300),(640+gap,535)],GOLD,2);star(d,cx,330,32*q,12*q,8,GOLD,2)
 elif m=='sleep_waking':
  arc(d,(280,240,520,480),70,290,LAP,4);star(d,920,360,48,18,12,GOLD,2,t*.05);line(d,[(520,360),(870,360)],PALE,2);circ(d,cx,360,22,POR,1,POR)
 elif m=='person_light':
  circ(d,cx,290,24,GOLD,3);line(d,[(cx,314),(cx,470)],GOLD,5);line(d,[(cx,350),(550,420)],GOLD,3);line(d,[(cx,350),(730,420)],GOLD,3);line(d,[(cx,470),(580,560)],GOLD,3);line(d,[(cx,470),(700,560)],GOLD,3)
  for a in [i*math.pi/12 for i in range(24)]:line(d,[(cx+65*math.cos(a),390+65*math.sin(a)),(cx+(140+20*math.sin(t*2+a*3))*math.cos(a),390+(140+20*math.sin(t*2+a*3))*math.sin(a))],PALE,1)
 elif m=='spider_thread':
  l=(390,370);r=(890,370);circ(d,*l,28,INK,3);circ(d,*r,28,GOLD,3)
  for rr in [70,120,170]:arc(d,(cx-rr,370-rr,cx+rr,370+rr),200,340,GREY,1)
  line(d,[(lerp(l[0]+30,r[0]-30,i/119),370+18*math.sin(i/119*math.pi*6+t*2)) for i in range(120)],POR,3)
 elif m=='cut_rejoin':
  l=(390,360);r=(890,360);q=smooth(.05,.42,t);z=smooth(.48,.86,t);circ(d,*l,35,INK,2);circ(d,*r,35,GOLD,2);line(d,[l,(cx-45*q,360)],POR,3);line(d,[(cx+45*q,360),r],POR,3)
  if z:line(d,[(cx-45*q,360),(cx,330+30*z),(cx+45*q,360)],GOLD,3);line(d,[(cx-45*q,360),(cx,390-30*z),(cx+45*q,360)],LAP,3)
 elif m=='formula_one':
  d.text((260,330),'1 = 1',font=TITLE,fill=GREY);d.text((900,330),'n + 1',font=TITLE,fill=GREY);q=smooth(.25,.75,t);d.text((580,330),'1 × 1',font=TITLE,fill=mix(BG,POR,q));circ(d,cx-45,430,70*q,POR,3);circ(d,cx+45,430,70*q,GOLD,3)
 elif m=='relation_orbit':
  a=t*math.pi*1.2;r=95;p1=(cx+r*math.cos(a),365+r*.45*math.sin(a));p2=(cx+r*math.cos(a+math.pi),365+r*.45*math.sin(a+math.pi));circ(d,*p1,24,POR,1,POR);circ(d,*p2,24,GOLD,1,GOLD);line(d,[p1,p2],INK,2);arc(d,(cx-230,250,cx+230,480),0,360,PALE,1)
 elif m=='face_spring':
  face(d,470,360,1,INK,1.1)
  for i in range(13):a=-.9+i*.14;r=100+90*p;line(d,[(545,335),(545+r*math.cos(a),335+r*math.sin(a))],GOLD if i%2 else POR,2)
  for rr in [30,60,90]:arc(d,(760-rr,360-rr*.35,760+rr,360+rr*.35),0,360,LAP,1)
 elif m=='two_faces':
  face(d,470,360,1,INK,1.05);face(d,810,360,-1,GOLD,1.05)
  for i in range(9):q=i/8;line(d,[(560,300+q*120),(720,410-q*120)],mix(POR,GOLD,q),1+i%2)
  circ(d,cx,360,12+8*math.sin(t*math.pi),POR,1,POR)
 elif m=='spirit_sun':
  b=[(640,190),(580,250),(560,390),(590,520),(640,570),(690,520),(720,390),(700,250)];line(d,b+[b[0]],INK,3);y=lerp(510,240,(math.sin(t*math.pi)+.05)/1.05);star(d,cx,y,34,13,10,GOLD,2,t*.12)
 elif m=='gaze_relation':
  face(d,430,360,1,INK,1);face(d,850,360,-1,GOLD,1)
  for k in range(7):y=310+k*18;line(d,[(505,y),(775,410-(y-310))],POR if k%2 else GOLD,2)
  star(d,cx,360,40,16,8,LAP,2,t*.1)
 elif m=='name_spiral':
  pts=spiral(cx,400,40,220,2.6,180,-math.pi/2+t*.15);line(d,pts,GREY,1)
  for i,nm in enumerate(['الله','هو','نور','حق','حي']):q=pts[int((i+.2)*len(pts)/5)%len(pts)];d.text((q[0]-18,q[1]-12),nm,font=TERM,fill=POR if i%2 else INK)
  star(d,cx,400,28,11,8,GOLD,2,t*.1)
 elif m=='fire_veil':
  d.rectangle((360,180,920,550),fill=mix(BG,DARK,.75),outline=INK,width=2);burn=lerp(530,210,p);d.rectangle((360,burn,920,550),fill=BG);line(d,[(x,burn+22*math.sin(x*.035+t*4)) for x in range(360,921,18)],POR,4)
  for x in range(390,900,55):star(d,x,burn-18,9,3,6,GOLD,1,t)
 elif m=='light_upon_light':
  for x,c in [(470,POR),(810,GOLD)]:star(d,x,360,48,19,10,c,2,t*.08);circ(d,x,360,80,PALE,1);circ(d,x,360,125,PALE,1)
  q=smooth(.35,.85,t);circ(d,cx,360,70+130*q,LAP,2);star(d,cx,360,30+35*q,12+12*q,12,GOLD,2,t*.1)
 elif m=='door_dissolve':
  for i in range(8):y=500-i*42-70*p;x=cx+55*math.sin(i*.8+t*2);d.text((x-15,y),'هو',font=TERM,fill=POR if i%2 else GOLD)
  arch(d,470,130,810,550,mix(BG,INK,1-smooth(.55,.95,t)),3);star(d,cx,260,35,13,8,GOLD,2,t*.1)
 elif m=='chinvat_bridge':
  d.polygon([(0,520),(470,410),(810,410),(W,520),(W,H),(0,H)],fill=mix(BG,DARK,.55));line(d,[(270,520),(1010,520)],INK,4)
  for x in range(300,1001,70):line(d,[(x,520),(x+45,460)],GREY,2)
  x=lerp(330,900,p);circ(d,x,430,13,INK,2);line(d,[(x,443),(x,495)],INK,3);star(d,980,350,38,15,10,GOLD,2,t*.08)
 elif m=='daena_figure':
  face(d,430,360,1,INK,1);face(d,850,350,-1,GOLD,1.1);arch(d,650,170,1030,550,GOLD,2)
  for r in [70,115,165]:circ(d,850,350,r,PALE,1)
  line(d,[(520,370),(760,360)],POR,2)
 elif m=='beauty_growth':
  star(d,420,420,22+12*p,9+5*p,8,POR,2,t*.1);star(d,860,380,42+55*p,17+22*p,12,GOLD,2,t*.1)
  for i in range(7):q=smooth(.1+i*.08,.55+i*.06,t);star(d,500+i*55,430-35*math.sin(i),10*q,4*q,6,LAP,1,i)
 elif m=='shadow_eternity':
  d.rectangle((170,200,590,540),fill=mix(BG,DARK,.65),outline=INK,width=2);d.rectangle((690,200,1110,540),fill=WHITE,outline=GOLD,width=2)
  for i in range(18):
   x=210+(i*71)%330;y=240+(i*43)%250
   if i/18>p:poly(d,[(x,y),(x+18,y+4),(x+5,y+22)],GREY,1,GREY)
  star(d,900,370,55,22,12,GOLD,2,t*.08);d.text((285,565),'history',font=SMALL,fill=GREY);d.text((865,565),'eternity',font=SMALL,fill=POR)
 elif m=='parent_child':
  circ(d,470,360,120,GOLD,3);circ(d,810,360,55+35*p,POR,3);arrow(d,(570,330),(735,330),GOLD,2);arrow(d,(735,410),(570,410),POR,2);star(d,470,360,35,14,10,GOLD,2,t*.1);star(d,810,360,22,9,8,POR,2,-t*.1)
 elif m=='mutual_birth':
  arch(d,280,160,700,540,POR,3);arch(d,580,160,1000,540,GOLD,3)
  for i in range(9):q=i/8;circ(d,lerp(440,840,q),350+70*math.sin(q*math.pi*2+t),6,LAP if i%2 else POR,1,LAP if i%2 else POR)
  circ(d,cx,365,18,GOLD,1,GOLD)
 elif m=='recursive_halo':
  for i in range(7):r=180*(.72**i);circ(d,cx+60*math.sin(i*1.2+t*.3),360+25*math.cos(i*.8),r,[GOLD,POR,LAP][i%3],2)
  star(d,cx,360,22,9,8,GOLD,2,t*.1)
 elif m=='veil_heart':
  star(d,cx,390,34,13,8,POR,2,t*.1)
  for i in range(5):y=210+i*65-170*p;d.rectangle((300+i*25,y,980-i*25,y+45),fill=mix(BG,DARK,1-p*.8))
  for r in [70,120,180]:circ(d,cx,390,r,PALE,1)
 elif m=='world_geography':
  circ(d,cx,360,230,INK,2)
  for r in [60,110,165,220]:circ(d,cx,360,r,PALE,1)
  star(d,cx,150,24,9,8,GOLD,2);arch(d,500,290,780,560,POR,2);arc(d,(350,300,550,420),200,340,INK,2);arc(d,(350,300,550,420),20,160,INK,2);line(d,[(730,360),(930,360)],POR,3)
 elif m=='trained_eye':
  arc(d,(320,210,960,520),200,340,INK,4);arc(d,(320,210,960,520),20,160,INK,4);circ(d,cx,365,96,POR,3);q=smooth(.1,.8,t)
  for i in range(8):a=i*math.pi/4;r=60+90*q;line(d,[(cx,365),(cx+r*math.cos(a),365+r*math.sin(a))],GOLD,2)
  star(d,cx,365,25,10,8,GOLD,2,t*.1)
 elif m=='objects_pass':
  col=mix(BG,INK,1-smooth(.25,.82,t));d.rectangle((305,335,375,405),outline=col,width=3);poly(d,[(510,318),(550,390),(470,390)],col,3);circ(d,680,370,38,col,3);poly(d,[(850,318),(892,360),(850,402),(808,360)],col,3);star(d,1040,360,45,18,10,GOLD,2,t*.08)
 elif m=='other_eyes':
  for x in [430,850]:q=1-smooth(.08,.55,t);arc(d,(x-110,285-q*35,x+110,440+q*35),200,340,INK,3);arc(d,(x-110,285-q*35,x+110,440+q*35),20,160,INK,3)
  q=smooth(.35,.88,t);arch(d,cx-90*q,220,cx+90*q,500,POR,3);star(d,cx,355,38*q,15*q,10,GOLD,2,t*.1)
 label(d,s,t);return im
# render
contact=[];start=0
for i,s in enumerate(S,1):
 dur=s['duration'];nf=max(1,round(dur*FPS));silent=CLIPS/f"{s['shot_id']}_silent.mp4";final=CLIPS/f"{s['shot_id']}_{s['mode']}.mp4"
 s['start']=round(start,3);start+=dur;s['end']=round(start,3);s['visual_mechanism']=s['mode'].replace('_',' ');s['continuity_object']=CONT[s['chapter']];s['transition_in']='continuous motif transformation' if i>1 else 'opening from blank field';s['transition_out']='preserve '+CONT[s['chapter']];s['background_justification']='Ivory field sustains one imaginal world; porphyry, lapis and gold distinguish embodied, intermediate and luminous orders.';s['caption_rule']='No full narration captions; only the listed technical term when motion and negative space permit.'
 existing_thumb=THUMBS/f"{s['shot_id']}.jpg"
 if final.exists() and final.stat().st_size>10000:
  if existing_thumb.exists():contact.append((s,existing_thumb))
  print(f"skip {i}/{len(S)} {s['shot_id']}",flush=True)
  continue
 proc=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p',str(silent)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);thumb=None
 for fi in range(nf):
  im=frame(s,fi/max(1,nf-1));proc.stdin.write(im.tobytes())
  if fi==int(nf*.72):thumb=im.copy()
 proc.stdin.close();proc.wait()
 if proc.returncode:raise RuntimeError(s['shot_id'])
 wav=AUDIO/f"{s['shot_id']}.wav";subprocess.run(['ffmpeg','-y','-i',str(silent),'-i',str(wav),'-c:v','copy','-c:a','aac','-b:a','128k','-shortest',str(final)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);silent.unlink()
 if thumb:
  tp=THUMBS/f"{s['shot_id']}.jpg";thumb.save(tp,quality=88);contact.append((s,tp))
 print(f"{i}/{len(S)} {s['shot_id']} {dur:.2f}s {s['mode']}",flush=True)
concat=ROOT/'concat.txt'
concat.write_text('\n'.join("file '{}'".format((CLIPS/(s['shot_id']+'_'+s['mode']+'.mp4')).as_posix()) for s in S))
film=ROOT/'the_world_between_worlds_full_film.mp4'
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(film)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
wl=ROOT/'audio_concat.txt'
wl.write_text('\n'.join("file '{}'".format((AUDIO/(s['shot_id']+'.wav')).as_posix()) for s in S))
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(wl),'-c:a','pcm_s16le',str(ROOT/'reference_narration.wav')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
cols=5;tw,th=256,144;rows=math.ceil(len(contact)/cols);sheet=Image.new('RGB',(cols*tw,rows*th),'white');sd=ImageDraw.Draw(sheet)
for i,(s,tp) in enumerate(contact):
 im=Image.open(tp).resize((tw,th));x=i%cols*tw;y=i//cols*th;sheet.paste(im,(x,y));sd.rectangle((x+4,y+4,x+205,y+23),fill='white');sd.text((x+7,y+6),f"{s['shot_id']} {s['mode'][:19]}",font=TINY,fill=INK)
sheet.save(ROOT/'contact_sheet.jpg',quality=90)
story={'project':'The World Between Worlds — narration-locked visual film','source':'scripts/expansion-essay12.md','narration_policy':'Exact essay prose and quoted passages; Markdown syntax, repository metadata and internal RO citation suffixes are not spoken.','reference_voice':'eSpeak en-gb timing voice; replace with final narration and force-align before publication.','resolution':[W,H],'fps':FPS,'shot_count':len(S),'runtime_seconds':round(start,3),'continuity_systems':['threshold → room → eye → compass → wisdom door → final portal','star → Guide → second face → Daena','thread → gaze → dhikr current → bridge','paired forms preserve difference while relation deepens'],'shots':S}
(ROOT/'storyboard.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf-8')
with open(ROOT/'storyboard.csv','w',newline='',encoding='utf-8') as f:
 fields=['shot_id','start','end','duration','chapter','chapter_title','text','mode','visual_mechanism','continuity_object','transition_in','transition_out','caption','caption_rule'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();[w.writerow({k:s.get(k,'') for k in fields}) for s in S]
vp={'schema_version':'2.0-experimental.narration_locked','scene_id':'expansion-essay12-world-between-worlds','visual_thesis':'A third world gradually becomes perceptible as the same threshold transforms into eye, north, Guide, thread, face, fire, bridge and reciprocal birth.','palette':{'paper':'#F4EFE3','ink':'#1E191B','porphyry':'#792638','lapis':'#2A466E','gold':'#AE8534'},'entities':[{'id':'threshold','archetype':'threshold','continuity':'persistent'},{'id':'guide','archetype':'luminous_counterpart','continuity':'emerges_and_returns'},{'id':'relation_thread','archetype':'current','continuity':'persistent_transformation'},{'id':'inner_eye','archetype':'eye','continuity':'threshold_transformation'}],'operators':['reveal','mediate','orient','embody','illuminate','connect','cut','rejoin','mirror','radiate','ascend','burn','bridge','reciprocate','interiorize'],'shots':[{'id':s['shot_id'],'start':s['start'],'end':s['end'],'spoken_text':s['text'],'mode':s['mode'],'events':[{'op':'develop','range':[0,.72]},{'op':'resolve','range':[.72,.9]},{'op':'hold','range':[.9,1]}],'handoff':{'preserve':[s['continuity_object']]}} for s in S]}
(ROOT/'visual_program.json').write_text(json.dumps(vp,indent=2,ensure_ascii=False),encoding='utf-8')
(ROOT/'PRODUCTION_BLUEPRINT.md').write_text(f'''# Production Blueprint — The World Between Worlds\n\n- Exact essay prose and quotations used as narration, excluding Markdown metadata and internal RO citation suffixes.\n- {len(S)} narration-locked shots, each 5–10 seconds.\n- Reference runtime: {start/60:.2f} minutes.\n- Combined MP4 includes an eSpeak timing-reference narration.\n\n## Coherence\nThe central threshold becomes a room, inner eye, compass, wisdom door, thread, gaze, dhikr current, Chinvat Bridge and final portal. The Guide begins as a star and progressively condenses into the Person of Light and Daena.\n\n## Publication workflow\nReplace the timing voice, force-align the final narration, conform shot boundaries, render handles, and assemble in FableCut.\n''')
(ROOT/'README.md').write_text(f'''# The World Between Worlds — Full Film Pack\n\nMain film: `the_world_between_worlds_full_film.mp4`\n\n- {len(S)} individual 5–10 second audiovisual clips\n- exact narration passages and measured timings in storyboard JSON/CSV\n- reference narration WAV\n- contact sheet\n- Visual Program IR\n- complete renderer\n\nSpecs: {W}×{H}, {FPS} fps, H.264/AAC, {start:.2f} seconds.\n\nThe included eSpeak narration is a timing reference, not a publication-quality voice.\n''')
shutil.copy2(__file__,ROOT/'render_world_between_worlds.py')
zip_path=Path('/mnt/data/corbin_world_between_worlds_film_pack.zip')
if zip_path.exists():zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in ROOT.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(ROOT.parent))
print(json.dumps({'zip':str(zip_path),'film':str(film),'shots':len(S),'runtime':start,'contact':str(ROOT/'contact_sheet.jpg')},indent=2))
