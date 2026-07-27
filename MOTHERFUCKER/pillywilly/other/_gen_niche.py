"""Generate 20 niche platinum packs."""
from pathlib import Path
import subprocess, sys

with open('cell_believes_immortality_platinum.py') as f:
    tmpl = f.read()

packs = [
    ('alchemy_vaughan','Thomas Vaughan Virgin Mercury as Kundalini','The alchemist who knew the serpent power',
     ['Thomas Vaughan poet alchemist magus','Virgin Mercury the unawakened Shakti',
      'Coelum Terrae heaven within earth','Yields only to love not violence',
      'The green lion devouring the sun','Vaughan invisible nature',
      'The daimon as intermediator','Chemical wedding within the body',
      'Vaughan meets Layayoga','The stone is within']),
    ('ripley_gates','Ripley 12 Gates as Neural Circuit Activation','The 12 stages mapped to brain states',
     ['George Ripley 12 gates','Each gate is a transformation stage','Calcination burning false',
      'Solution dissolving the fixed','Separation dividing subtle from gross','Conjunction sacred marriage',
      'Putrefaction the dark night','Congelation the new form','Cibation feeding the stone',
      'Sublimation the ascent','Fermentation HGA contact','Exaltation Multiplication Projection']),
    ('turba_philosophorum','The Turba Philosophorum','Assembly of philosophers debating the stone',
     ['The oldest alchemical text','Philosophers debate the stone','Pythagoras on the elements',
      'Anaxagoras on the one seed','Empedocles on love and strife','Each contributes a piece',
      'Agreement beneath disagreement','The stone is both one and many','The debate is the method',
      'Unity through diversity']),
    ('paracelsus_aurora','Paracelsus Secret Fire as Prana','The aurora of the philosophers',
     ['Paracelsus the Luther of medicine','The secret fire not burning but altering',
      'Vaporous digesting continuous','Enclosed within the body','The microcosm contains all',
      'Archeus the inner alchemist','The aurora light of the morning','Secret fire as pranagni',
      'Medicine as alchemy','The body as laboratory']),
    ('chymical_wedding','The Chymical Wedding of Christian Rosenkreutz','Seven days of initiation',
     ['The Rosicrucian manifesto','Rosenkreutz receives the invitation','Day 1 the castle and gate',
      'Day 2 the weighing and marriage','Day 3 death of king and queen','Day 4 the resurrection',
      'Day 5 the Virgin Venus appears','Day 6 the judgment and tower','Day 7 the return and seal',
      'The initiation is complete']),
    ('atalanta_fugiens','Atalanta Fugiens','The alchemical fugue as chakra progression',
     ['Michael Maier alchemical music','50 emblems 50 fugues','Atalanta and Hippomenes the race',
      'The three golden apples','Each emblem is a stage','The music encodes the process',
      'The chakra correspondence','The fugue as spiritual ascent','Seeing with the ears',
      'The alchemy of sound']),
    ('maria_prophetissa','Maria Prophetissa and the Three Hour Stone','Instant enlightenment in alchemy',
     ['Maria the Jewess first alchemist','Three hour whitening','One becomes two becomes three',
      'The three hours as three stages','Azure blue to brilliant white','The quick path in alchemy',
      'Maria apparatus the kerotakis','Sudden vs gradual enlightenment','Tantric parallel sambhavopaya',
      'Time is not the limiting factor']),
    ('lambspring','The Book of Lambspring','Two fishes as ida and pingala',
     ['The alchemical poem of two fishes','One fish spirit one fish soul','They swim in opposite directions',
      'The water is the body','Ida and pingala sun and moon','The two serpents of the caduceus',
      'When they meet transformation','The fish become one dragon','The union of opposites',
      'Kundalini through the central channel']),
    ('harry_potter_alchemy','Harry Potter and the Alchemical Codex','Horcruxes as inverse chakras',
     ['Alchemical structure of Harry Potter','7 Horcruxes 7 chakras inverted',
      'Deathly Hallows as three gunas','Elder Wand rajas passion','Resurrection Stone tamas memory',
      'Invisibility Cloak sattva harmony','Voldemort and Harry as unus ambo',
      'Snape as alchemical sulfur','Dumbledore as philosopher mercury','Integration over division']),
    ('narnia_creation','The Creation of Narnia as Tattva Descent','Aslan singing worlds into being',
     ['The Magicians Nephew creation story','Aslan sings Narnia into being','The song becomes light',
      'The light becomes land','Animals awake to consciousness','This is the tattva descent',
      'From sound to light to form','The stone table as kula acala','Narnia as a subtle world',
      'Creation as music']),
    ('dostoevsky_daimon','Dostoevsky and the Daimonic','Sonya as daimon bearer',
     ['Brothers Karamazov a daimon novel','Sonya the daimon in human form','The Grand Inquisitor false guru',
      'Raskolnikov crime and daimonic punishment','Myshkin as holy fool',
      'The underground man as anti daimon','Dostoevsky epilepsy daimonic illness',
      'The alchemy of suffering','Beauty saves the world','The Russian soul vs the daimon']),
    ('penrose_orch_or','Consciousness Is Non Computable','Penrose ORCH-OR and the quantum brain',
     ['Roger Penrose controversial theory','Godel the mind is not a computer','The Penrose Hameroff model',
      'Microtubules the quantum processors','Objective reduction as consciousness',
      'Non computable physics','Criticism and evidence','Orch-OR in the spotlight',
      'Quantum biology meets consciousness','The implications for AI']),
    ('qri_qualia','The Structure of Conscious Experience','QRI and the combinatorial space of qualia',
     ['Qualia Research Institute','Combinatorial space of experience','Qualia as mathematical structures',
      'Valence as information geometry','The utility of consciousness','Measuring the unmeasurable',
      'The hard problem of consciousness','QRI approach systematic mapping',
      'Implications for AI sentience','A science of subjective experience']),
    ('spacetime_foam','Spacetime Foam and the Fabric of Maya','Quantum structure at Planck scale',
     ['At Planck scale space is not smooth','Quantum foam constant creation and annihilation',
      'Spacetime as maya the fabric of illusion','Virtual particles something from nothing',
      'The holographic principle','Planck length the limit of measurement',
      'Black holes as information processors','The universe as quantum computer',
      'Maya as the foam of reality','Physics meets metaphysics']),
    ('tsongkhapa_five','Tsongkhapa Five Stages of Completion','Tibetan Buddhist path to enlightenment',
     ['Tsongkhapa the great reformer','Five stages of the completion stage',
      'Body isolation realized body','Speech isolation realized speech','Mind isolation realized mind',
      'The illusory body','The clear light','Union of the two truths',
      'Buddhahood in one lifetime','The Vajrayana shortcut']),
    ('steiner_tantraloka','Steiner and the Tantraloka','Threefold body and the 36 tattvas',
     ['Rudolf Steiner spiritual science','The threefold body physical etheric astral',
      'The sevenfold body and 36 tattvas','Cosmic evolution and tattva descent',
      'Imagination inspiration intuition as upayas','The guardian of the threshold',
      'Steiner meets Abhinavagupta','The five states of consciousness',
      'The daimon as higher self','Two traditions one path']),
    ('suhrawardi_illumination','Suhrawardi Philosophy of Illumination','Light as the substance of being',
     ['Shihab al Din Suhrawardi','The philosophy of illumination ishraq',
      'Light is not a metaphor it is being','The hierarchy of lights',
      'Light of lights the source','The darkness of matter',
      'The imaginal world and Hurqalya','Corbin discovery',
      'Suhrawardi influence on Sufism','The practice of illumination']),
    ('yoga_vasistha','The Yoga Vasistha and Parallel Universes','The story of Lila and the multiverse',
     ['The Yoga Vasistha vast philosophical text','The story of Queen Lila',
      'Lila creates a universe in her mind','Bhusunda the crow witness of aeons',
      'The multiple universes of the text','Creation is perception',
      'The seven stages of wisdom','Vairagya dispassion as liberation',
      'The Jivanmukta liberated while living','Ancient text meets multiverse']),
    ('swendenborg_heaven','Swendenborg Heavenly Correspondences','Physical reflects spiritual',
     ['Emanuel Swendenborg scientist turned seer','The correspondence physical reflects spiritual',
      'Heaven and Hell geography of the soul','The spiritual world of causes',
      'Angels are humans perfected','Judgment after death is self judgment',
      'Swendenborg meets Bardo Thodol','Correspondence and the Tantraloka',
      'The universal human Adam Kadmon','Heaven is a state of love']),
    ('vakyapadiya','The Vakyapadiya and Philosophy of Language','Sphota theory meaning as sudden flash',
     ['Bhartrihari Vakyapadiya','The sphota theory of meaning','The word whole is primary unit',
      'Meaning is not built from phonemes','The three levels of language',
      'Vaikhari madhyama pasyanti','Language as brahman','The flash of understanding',
      'Linguistics meets mysticism','The word that creates worlds']),
]

for slug, title, subtitle, scenes in packs:
    code = tmpl.replace('cell_believes_immortality', slug)
    code = code.replace('Each Cell Believes in Its Own Immortality', title)

    scene_vars = ''
    for i, sc in enumerate(scenes):
        scene_vars += f'''
def vis_v{i}(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for j in range(int(8*r)):
        a=j*math.tau/8+t*0.2; rr=25+15*math.sin(t*0.3+j)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,14,GOLD,int(150*r),11)
    seal(im,"{sc}","{subtitle}")
'''
    start = code.find('def vis_v0')
    end = code.find('def rf(sc,fi,fc,w2,h2,se):')
    vis_dict = ', '.join(f'"vis_v{i}": vis_v{i}' for i in range(len(scenes)))
    scene_list = ', '.join(f'Scene("{s}","{subtitle}",7.0,"vis_v{i}",{{}})' for i,s in enumerate(scenes))
    new_middle = scene_vars + f'''
@dataclass
class Scene:
    title:str; narration:str; duration:float; visual:str; params:dict
VISUALS = {{ {vis_dict} }}
SCENES = [ {scene_list} ]
'''
    if start > 0 and end > start:
        code = code[:start] + new_middle + code[end:]

    code = code.replace('cell_believes_immortality.mp4', f'{slug}.mp4')
    code = code.replace('"each cell believes in its own immortality"', f'"{title.lower()}"')
    code = code.replace('"the built-in faith of every chromosome"', f'"{subtitle}"')

    Path(f'{slug}_platinum.py').write_text(code)

    r = subprocess.run([sys.executable, '-c', f'import py_compile; py_compile.compile("{slug}_platinum.py", doraise=True)'],
                      capture_output=True, text=True)
    if r.returncode == 0:
        print(f'OK: {slug} ({len(scenes)}sc)')
    else:
        print(f'FAIL: {slug}: {r.stderr[:80]}')

print(f'Done. {len(packs)} packs.')
