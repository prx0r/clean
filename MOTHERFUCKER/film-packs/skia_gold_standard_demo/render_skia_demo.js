const { Canvas, Path2D, FontLibrary } = require('skia-canvas');
const fs = require('fs');
const path = require('path');

const W = 1280, H = 720, FPS = 12;
const OUT = '/mnt/data/skia_gold_standard_demo';
const FRAMES = path.join(OUT, 'frames');
fs.mkdirSync(FRAMES, { recursive: true });

const C = {
  paper: '#F8F6F0',
  ink: '#171719',
  muted: '#AAA69E',
  gold: '#C99B3F',
  goldSoft: 'rgba(201,155,63,0.22)',
  crimson: '#8D2C39',
  crimsonSoft: 'rgba(141,44,57,0.14)',
  blue: '#4F6682',
  white: '#FFFFFF'
};

function clamp(x, a=0, b=1){ return Math.max(a, Math.min(b, x)); }
function mix(a,b,t){ return a+(b-a)*t; }
function smooth(a,b,x){ const u=clamp((x-a)/(b-a)); return u*u*(3-2*u); }
function easeOutCubic(t){ return 1-Math.pow(1-clamp(t),3); }
function easeInOutSine(t){ return -(Math.cos(Math.PI*clamp(t))-1)/2; }
function easeOutQuart(t){ return 1-Math.pow(1-clamp(t),4); }

function base(ctx, idx, title){
  ctx.fillStyle = C.paper;
  ctx.fillRect(0,0,W,H);
  ctx.strokeStyle = 'rgba(23,23,25,0.10)';
  ctx.lineWidth = 1;
  ctx.strokeRect(24,24,W-48,H-48);
  ctx.font = '18px DejaVu Sans';
  ctx.fillStyle = 'rgba(23,23,25,0.46)';
  ctx.fillText(String(idx).padStart(2,'0'), 46, 53);
  ctx.fillText(title.toUpperCase(), 86, 53);
}

function line(ctx,x1,y1,x2,y2,color,width=2,alpha=1){
  ctx.save(); ctx.globalAlpha=alpha; ctx.strokeStyle=color; ctx.lineWidth=width; ctx.lineCap='round';
  ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke(); ctx.restore();
}
function circle(ctx,x,y,r,stroke,fill=null,width=2,alpha=1){
  ctx.save(); ctx.globalAlpha=alpha; ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2);
  if(fill){ctx.fillStyle=fill;ctx.fill();}
  if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=width;ctx.stroke();}
  ctx.restore();
}
function text(ctx, str, x, y, size=28, color=C.ink, align='center', alpha=1, serif=false){
  ctx.save(); ctx.globalAlpha=alpha; ctx.font=`${serif?'serif':'sans-serif'} ${size}px`; ctx.textAlign=align; ctx.fillStyle=color; ctx.fillText(str,x,y); ctx.restore();
}
function arrow(ctx,x1,y1,x2,y2,color,width=2,alpha=1){
  line(ctx,x1,y1,x2,y2,color,width,alpha);
  const a=Math.atan2(y2-y1,x2-x1), s=12;
  ctx.save();ctx.globalAlpha=alpha;ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(x2,y2);
  ctx.lineTo(x2+s*Math.cos(a+2.6),y2+s*Math.sin(a+2.6));
  ctx.lineTo(x2+s*Math.cos(a-2.6),y2+s*Math.sin(a-2.6));ctx.closePath();ctx.fill();ctx.restore();
}
function glowCircle(ctx,x,y,r,color,alpha=1){
  ctx.save();
  ctx.globalAlpha=alpha;
  ctx.shadowColor=color; ctx.shadowBlur=28;
  ctx.fillStyle=color; ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.restore();
}
function bezier(ctx, pts, color, width=3, alpha=1){
  ctx.save();ctx.globalAlpha=alpha;ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineCap='round';ctx.beginPath();
  ctx.moveTo(pts[0],pts[1]);ctx.bezierCurveTo(pts[2],pts[3],pts[4],pts[5],pts[6],pts[7]);ctx.stroke();ctx.restore();
}

function scene1(ctx,u){
  base(ctx,1,'The expenditure of the drop');
  const reveal=smooth(0.05,0.25,u), fall=smooth(0.20,0.68,u), consume=smooth(0.55,0.92,u);
  text(ctx,'THE ORDINARY DESCENT',640,112,36,C.ink,'center',reveal);
  // lunar reservoir
  ctx.save();ctx.globalAlpha=reveal;ctx.strokeStyle=C.ink;ctx.lineWidth=2;ctx.beginPath();ctx.arc(640,210,88,0.12*Math.PI,0.88*Math.PI);ctx.stroke();ctx.restore();
  circle(ctx,640,210,7,null,C.crimson,0,reveal);
  line(ctx,640,225,640,520,C.muted,1,0.35*reveal);
  // descending drop trail
  const y=mix(230,470,fall);
  for(let k=0;k<7;k++){
    const yy=y-k*26;
    const a=clamp(1-k*0.13)*fall;
    circle(ctx,640,yy,Math.max(2,7-k*0.65),null,C.crimson,0,a);
  }
  // lower fire
  const fireY=515;
  const grad=ctx.createRadialGradient(640,fireY,5,640,fireY,115);
  grad.addColorStop(0,'rgba(201,155,63,0.34)'); grad.addColorStop(1,'rgba(201,155,63,0)');
  ctx.save();ctx.globalAlpha=consume;ctx.fillStyle=grad;ctx.fillRect(510,385,260,260);ctx.restore();
  for(let k=0;k<5;k++){
    const w=110-k*18, h=54+k*12;
    ctx.save();ctx.globalAlpha=consume*(0.9-k*0.12);ctx.strokeStyle=k%2?C.crimson:C.gold;ctx.lineWidth=3;
    ctx.beginPath();ctx.moveTo(640-w/2,fireY+45);ctx.quadraticCurveTo(640-w/3,fireY-h,640,fireY-10-k*7);ctx.quadraticCurveTo(640+w/3,fireY-h,640+w/2,fireY+45);ctx.stroke();ctx.restore();
  }
  text(ctx,'a finite reserve enters the consuming fire',640,652,22,C.ink,'center',smooth(0.64,0.86,u));
}

function scene2(ctx,u){
  base(ctx,2,'Seal and reversal');
  const down=smooth(0.04,0.32,u), seal=smooth(0.34,0.55,u), reverse=smooth(0.52,0.92,u);
  text(ctx,'THE SEAL DOES NOT ADD ENERGY',640,108,32,C.ink,'center',smooth(0.04,0.24,u));
  text(ctx,'it changes the direction of expenditure',640,147,22,C.muted,'center',smooth(0.14,0.34,u));
  line(ctx,640,190,640,542,C.muted,1,0.34);
  // initial descending particles
  for(let k=0;k<7;k++){
    const yy=220+((k*44+down*160)%300);
    circle(ctx,640,yy,4,null,C.crimson,0,down*(1-seal*0.55));
  }
  // seal plate
  const sealW=250*easeOutCubic(seal);
  line(ctx,640-sealW/2,390,640+sealW/2,390,C.ink,6,seal);
  line(ctx,640-sealW/2,401,640+sealW/2,401,C.gold,2,seal);
  // reversed current curls around seal
  const rise=reverse;
  bezier(ctx,[630,390,520,330,540,245,640,210],C.gold,4,rise);
  bezier(ctx,[650,390,760,330,740,245,640,210],C.gold,4,rise);
  for(let k=0;k<5;k++){
    const yy=mix(380,225,clamp(rise-k*0.08));
    circle(ctx,640,yy,5,null,C.crimson,0,clamp(rise-k*0.08));
  }
  glowCircle(ctx,640,210,8,C.gold,0.7*rise);
  text(ctx,'loss becomes return',640,648,26,C.ink,'center',smooth(0.72,0.92,u));
}

function scene3(ctx,u){
  base(ctx,3,'Two currents become a central route');
  const establish=smooth(0.04,0.24,u), sync=smooth(0.24,0.62,u), center=smooth(0.58,0.94,u);
  text(ctx,'DUAL CURRENTS',640,112,34,C.ink,'center',establish);
  const top=190,bottom=560;
  // peripheral sine paths
  const steps=180;
  ctx.save();ctx.lineWidth=3;ctx.lineCap='round';
  for(const side of [-1,1]){
    ctx.beginPath();
    for(let i=0;i<steps;i++){
      const p=i/(steps-1), y=mix(bottom,top,p);
      const phase=(1-sync)*Math.PI*side;
      const x=640+side*(170-80*sync)+42*Math.sin(p*Math.PI*4+phase)*(1-0.72*sync);
      if(i===0)ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.strokeStyle=side<0?C.crimson:C.blue;ctx.globalAlpha=establish;ctx.stroke();
  }
  ctx.restore();
  // convergence nodes
  for(let k=0;k<6;k++){
    const p=k/5, y=mix(bottom,top,p), xOffset=(170-80*sync)*(1-p*0.18);
    circle(ctx,640-xOffset,y,4,null,C.crimson,0,establish);
    circle(ctx,640+xOffset,y,4,null,C.blue,0,establish);
  }
  // central route
  const grad=ctx.createLinearGradient(640,bottom,640,top);grad.addColorStop(0,C.crimson);grad.addColorStop(0.5,C.gold);grad.addColorStop(1,C.gold);
  line(ctx,640,bottom,640,mix(bottom,top,center),grad,5,center);
  glowCircle(ctx,640,mix(bottom,top,center),7,C.gold,0.75*center);
  text(ctx,'synchrony opens a route that neither current possessed alone',640,648,22,C.ink,'center',smooth(0.68,0.90,u));
}

function scene4(ctx,u){
  base(ctx,4,'The vessel becomes a circuit');
  const body=smooth(0.04,0.28,u), systems=smooth(0.22,0.64,u), circulate=smooth(0.56,0.96,u);
  text(ctx,'THE BODY AS ALCHEMICAL APPARATUS',640,108,31,C.ink,'center',body);
  // vessel silhouette
  ctx.save();ctx.globalAlpha=body;ctx.strokeStyle=C.ink;ctx.lineWidth=3;ctx.beginPath();
  ctx.moveTo(505,195);ctx.bezierCurveTo(455,265,470,530,560,580);
  ctx.bezierCurveTo(610,610,670,610,720,580);ctx.bezierCurveTo(810,530,825,265,775,195);ctx.stroke();ctx.restore();
  // reservoir and fire
  ctx.save();ctx.globalAlpha=systems;ctx.strokeStyle=C.gold;ctx.lineWidth=3;ctx.beginPath();ctx.arc(640,250,88,0.08*Math.PI,0.92*Math.PI);ctx.stroke();ctx.restore();
  circle(ctx,640,250,7,null,C.crimson,0,systems);
  // lower chamber
  circle(ctx,640,500,70,C.ink,null,2,systems);
  for(let k=0;k<3;k++){
    ctx.save();ctx.globalAlpha=systems*(0.9-k*0.18);ctx.strokeStyle=k%2?C.crimson:C.gold;ctx.lineWidth=3;ctx.beginPath();
    ctx.moveTo(602+k*9,520);ctx.quadraticCurveTo(625,440-k*10,640,485-k*12);ctx.quadraticCurveTo(660,440-k*10,678-k*9,520);ctx.stroke();ctx.restore();
  }
  // circuit
  const leftPath=[630,490,510,425,510,310,640,265];
  const rightPath=[650,490,770,425,770,310,640,265];
  bezier(ctx,leftPath,C.crimson,4,circulate);
  bezier(ctx,rightPath,C.gold,4,circulate);
  const y=mix(490,275,circulate);
  glowCircle(ctx,640,y,7,C.gold,0.8*circulate);
  // completion ring
  circle(ctx,640,375,170,C.gold,null,2,0.4*circulate);
  text(ctx,'reservoir · seal · fire · return',640,650,22,C.ink,'center',smooth(0.70,0.92,u));
}

const scenes=[
  {title:'The expenditure of the drop',duration:6,fn:scene1},
  {title:'Seal and reversal',duration:6,fn:scene2},
  {title:'Two currents become a central route',duration:6,fn:scene3},
  {title:'The vessel becomes a circuit',duration:6,fn:scene4}
];

async function render(){
  let frameIndex=0; const hero=[];
  for(let s=0;s<scenes.length;s++){
    const scene=scenes[s]; const n=Math.round(scene.duration*FPS);
    for(let f=0;f<n;f++){
      const u=f/(n-1);
      const canvas=new Canvas(W,H), ctx=canvas.getContext('2d');
      scene.fn(ctx,u);
      const buf=await canvas.png;
      const name=String(frameIndex).padStart(5,'0')+'.png';
      fs.writeFileSync(path.join(FRAMES,name),buf);
      if(f===Math.round((n-1)*0.72)) hero.push(buf);
      frameIndex++;
    }
  }
  // contact sheet
  const sheet=new Canvas(1280,820), sctx=sheet.getContext('2d');
  sctx.fillStyle=C.paper;sctx.fillRect(0,0,1280,820);
  text(sctx,'SKIA GOLD STANDARD DEMO',640,54,28,C.ink);
  text(sctx,'Amṛtasiddhi · operative geometry · mature frames at 72%',640,84,18,C.muted);
  for(let i=0;i<hero.length;i++){
    const img=await require('skia-canvas').loadImage(hero[i]);
    const x=40+(i%2)*610, y=120+Math.floor(i/2)*330;
    sctx.drawImage(img,x,y,590,332);
  }
  fs.writeFileSync(path.join(OUT,'contact_sheet.png'), await sheet.png);
  const manifest={
    pack_id:'amrtasiddhi_skia_gold_demo', renderer:'skia-canvas', resolution:[W,H], fps:FPS,
    palette:C, scenes:scenes.map((s,i)=>({shot_id:`skia_${String(i+1).padStart(2,'0')}`,title:s.title,duration_seconds:s.duration,renderer:'skia-custom-v1'}))
  };
  fs.writeFileSync(path.join(OUT,'manifest.json'),JSON.stringify(manifest,null,2));
}
render().catch(e=>{console.error(e);process.exit(1)});
