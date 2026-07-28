import { TAU, clamp, easeOutCubic, rgba, smoothstep, wave } from "../math.mjs";
import { drawArrowHead, drawGlowOrb, drawNode, drawPartialPath, drawRing } from "../primitives.mjs";

const CX=640,CY=316,W=1280,H=720;
const FONT='"Source Serif 4", "EB Garamond", serif';
const MATH='"KaTeX Math", "Source Serif 4", serif';
const C={ink:"#171a1e",muted:"#5c626a",blue:"#2d6685",red:"#a43e46",green:"#3e7857",gold:"#a9782f",paper:"#fbfaf6"};

const astate=(env)=>({rms:clamp(env.audio?.rms??0),onset:clamp(env.audio?.onset??0),voice:clamp(env.audio?.voicedProbability??0)});
const mstart=(m,i,n)=>Number.isFinite(m.start)?m.start:i/n;
const mend=(m,i,n)=>Number.isFinite(m.end)?m.end:(i+1)/n;
function progress(m,t,i,n){const a=mstart(m,i,n),b=mend(m,i,n);return b<=a?(t>=a?1:0):clamp((t-a)/(b-a));}
function visibility(m,t,i,n){
  const a=mstart(m,i,n),b=mend(m,i,n),fi=m.fadeIn??0.08,fo=m.fadeOut??0.07;
  if(m.persist)return smoothstep(a,a+fi,t);
  if(t<a||t>b)return 0;
  return smoothstep(a,a+fi,t)*(1-smoothstep(b-fo,b,t));
}
function color(m){return m.status==="refuted"?C.red:m.status==="resolved"?C.green:m.status==="highlight"?C.gold:m.status==="neutral"?C.muted:(m.color??C.ink);}

function runs(text){return String(text).split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g).filter(Boolean).map(s=>s.startsWith("**")?{t:s.slice(2,-2),w:700,i:false}:s.startsWith("*")?{t:s.slice(1,-1),w:400,i:true}:{t:s,w:400,i:false});}
function font(r,size){return `${r.i?"italic ":""}${r.w} ${size}px ${r.i?MATH:FONT}`;}
function measure(ctx,text,size){return runs(text).reduce((sum,r)=>{ctx.font=font(r,size);return sum+ctx.measureText(r.t).width;},0);}
function wrap(ctx,text,size,maxWidth){
  const out=[];for(const para of String(text).split("\n")){let line="";
    for(const word of para.split(/\s+/).filter(Boolean)){const c=line?`${line} ${word}`:word;
      if(line&&measure(ctx,c,size)>maxWidth){out.push(line);line=word;}else line=c;}
    if(line)out.push(line);if(!para)out.push("");
  }return out;
}
function line(ctx,text,x,y,size,col,alpha,align="center"){
  const rs=runs(text),ws=rs.map(r=>{ctx.font=font(r,size);return ctx.measureText(r.t).width;}),total=ws.reduce((a,b)=>a+b,0);
  let cur=align==="center"?x-total/2:x;ctx.textAlign="left";ctx.textBaseline="middle";
  rs.forEach((r,i)=>{ctx.font=font(r,size);ctx.fillStyle=rgba(col,alpha);ctx.fillText(r.t,cur,y);cur+=ws[i];});
}
function block(ctx,text,{x=CX,y=CY,size=32,maxWidth=900,col=C.ink,alpha=1,align="center",p=1}={}){
  const ls=wrap(ctx,text,size,maxWidth),lh=size*1.28,top=y-(ls.length-1)*lh/2;
  ls.forEach((s,i)=>line(ctx,s,x,top+i*lh,size,col,alpha*smoothstep(i*.05,i*.05+.18,p),align));
}
function bg(ctx,t,env){
  const a=astate(env);ctx.fillStyle=C.paper;ctx.fillRect(0,0,W,H);
  const g=ctx.createRadialGradient(CX,CY,20,CX,CY,650);g.addColorStop(0,"rgba(255,255,255,.62)");g.addColorStop(1,"rgba(221,228,226,.05)");
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  for(let i=0;i<4;i++)drawRing(ctx,CX,CY,170+i*145+6*wave(t+i*.17,.11),i%2?C.blue:C.gold,.012+a.rms*.008,.45);
  if(a.onset>.08)drawRing(ctx,CX,CY,55+a.onset*90,C.gold,a.onset*.05,.7);
}
function claim(ctx,p,m,e,v){
  const size=m.size??34,scale=.965+.035*easeOutCubic(smoothstep(0,.25,p));ctx.save();ctx.translate(CX,m.y??CY);ctx.scale(scale,scale);
  block(ctx,m.text,{x:0,y:0,size,maxWidth:m.maxWidth??900,col:color(m),alpha:v*(.92+astate(e).voice*.03),p});ctx.restore();
  if(m.status==="refuted"){const s=smoothstep(.45,.7,p);ctx.strokeStyle=rgba(C.red,v*s*.7);ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(CX-330,m.y??CY);ctx.lineTo(CX+330,m.y??CY);ctx.stroke();}
  if(m.status==="highlight")drawRing(ctx,CX,m.y??CY,m.ringRadius??190,C.gold,v*smoothstep(.4,.75,p)*.11,.8);
}
function subclaim(ctx,p,m,e,v){const y=Number.isFinite(m.y)?m.y:450;block(ctx,m.text,{x:CX,y,size:m.size??19,maxWidth:m.maxWidth??850,col:color(m),alpha:v*.8,p});
  if(m.arrow){const q=smoothstep(.3,.65,p),pts=[{x:CX-270,y:y-34},{x:CX+270,y:y-34}];drawPartialPath(ctx,pts,q,m.color??C.blue,.85,v*.3);if(q>.9)drawArrowHead(ctx,CX+270,y-34,0,7,m.color??C.blue,v*.32);}}
function divider(ctx,p,m,e,v){const q=smoothstep(0,.7,p),y=m.y??CY,w=m.width??360;ctx.strokeStyle=rgba(C.muted,v*.22);ctx.lineWidth=.55;ctx.beginPath();ctx.moveTo(CX-w*q/2,y);ctx.lineTo(CX+w*q/2,y);ctx.stroke();drawGlowOrb(ctx,CX,y,1.8,C.gold,v*q*.15);}
function premises(ctx,p,m,e,v){const ps=m.premises??[],size=m.size??18,lh=m.lineHeight??45,start=m.y??(CY-(ps.length-1)*lh/2-34);
  ps.forEach((s,i)=>{const r=smoothstep(i*.1,i*.1+.2,p);drawNode(ctx,174,start+i*lh,3.2,{fill:i===ps.length-1?C.gold:C.blue,stroke:i===ps.length-1?C.gold:C.blue,alpha:v*r*.5});block(ctx,s,{x:198,y:start+i*lh,size,maxWidth:900,col:C.ink,alpha:v*r*.86,align:"left",p:1});});
  if(m.conclusion){const r=smoothstep(.64,.88,p),y=start+ps.length*lh+4;ctx.strokeStyle=rgba(C.gold,v*r*.48);ctx.beginPath();ctx.moveTo(165,y);ctx.lineTo(1115,y);ctx.stroke();block(ctx,m.conclusion,{x:190,y:y+38,size:size+2,maxWidth:900,col:C.green,alpha:v*r*.95,align:"left",p:1});}}
function side(ctx,p,m,e,v){const l=smoothstep(0,.32,p),r=smoothstep(.2,.52,p);block(ctx,m.left,{x:390,y:m.y??CY,size:m.size??20,maxWidth:370,col:m.leftColor??C.blue,alpha:v*l*.92,p});block(ctx,m.right,{x:890,y:m.y??CY,size:m.size??20,maxWidth:370,col:m.rightColor??C.red,alpha:v*r*.92,p});
  if(l>.3&&r>.3){ctx.setLineDash([3,7]);ctx.strokeStyle=rgba(C.muted,v*.2);ctx.beginPath();ctx.moveTo(CX,CY-180);ctx.lineTo(CX,CY+180);ctx.stroke();ctx.setLineDash([]);}}
function branch(ctx,p,m,e,v){const bs=m.branches??[],spread=Math.min(350,900/Math.max(bs.length,2)),top=m.topY??238,bot=m.bottomY??386;
  bs.forEach((b,i)=>{const r=smoothstep(.05+i*.12,.25+i*.12,p),x=CX+(i-(bs.length-1)/2)*spread,cp=(CX+x)/2+(i-(bs.length-1)/2)*18;
    ctx.strokeStyle=rgba(b.color??C.muted,v*r*.28);ctx.beginPath();ctx.moveTo(CX,top);ctx.quadraticCurveTo(cp,bot-70,x,bot);ctx.stroke();drawGlowOrb(ctx,x,bot,3.2,b.color??C.blue,v*r*.24);
    block(ctx,b.label,{x,y:bot+58,size:b.size??m.size??16,maxWidth:b.maxWidth??265,col:b.color??C.ink,alpha:v*r*.89,p});});}
function cmap(ctx,p,m,e,v){const ns=m.nodes??[],size=m.size??16,r=smoothstep(0,.2,p);drawGlowOrb(ctx,CX,CY,10,C.gold,v*r*.12);drawRing(ctx,CX,CY,50+4*wave(p,.4),C.gold,v*r*.13,.7);block(ctx,`**${m.central??""}**`,{x:CX,y:CY,size:size+3,maxWidth:210,col:C.ink,alpha:v*r*.94,p});
  ns.forEach((n,i)=>{const q=smoothstep(.12+i*.075,.28+i*.075,p),x=CX+(n.x??0),y=CY+(n.y??0),cur=n.curvature??((i%3)-1)*22;
    ctx.setLineDash(n.dashed===false?[]:[3,5]);ctx.strokeStyle=rgba(n.color??C.blue,v*q*.3);ctx.beginPath();ctx.moveTo(CX,CY);ctx.quadraticCurveTo((CX+x)/2+cur,(CY+y)/2-18,x,y);ctx.stroke();ctx.setLineDash([]);
    drawGlowOrb(ctx,x,y,3.8,n.color??C.blue,v*q*.23);block(ctx,n.label,{x,y:y+27,size,maxWidth:n.maxWidth??240,col:n.color??C.ink,alpha:v*q*.9,p});if(n.relation)block(ctx,n.relation,{x,y:y-27,size:size-4,maxWidth:220,col:C.muted,alpha:v*q*.58,p});});}
function converge(ctx,p,m,e,v){const y=(m.y??CY)+30*(1-easeOutCubic(smoothstep(0,.3,p)));block(ctx,m.text,{x:CX,y,size:m.size??28,maxWidth:m.maxWidth??920,col:color(m),alpha:v*.95,p});drawRing(ctx,CX,y,(m.ringRadius??225)+astate(e).rms*12,m.status==="resolved"?C.green:C.gold,v*smoothstep(.34,.76,p)*(.08+astate(e).rms*.03),.75);}
function pulse(ctx,p,m,e,v){const pts=m.points??[{x:210,y:CY},{x:420,y:CY-85},{x:640,y:CY+45},{x:860,y:CY-65},{x:1070,y:CY}];drawPartialPath(ctx,pts,easeOutCubic(p),m.color??C.gold,m.width??1.8,v*.68,{blur:4});}
const R={claim,subclaim,divider,premises,"side-by-side":side,branch,"concept-map":cmap,converge,"pulse-path":pulse,refutation:claim};

export function renderArgumentDiagramV2(ctx,t,scene,env){
  bg(ctx,t,env);const moves=scene.params?.moves??[],n=Math.max(1,moves.length);
  moves.forEach((m,i)=>{const v=visibility(m,t,i,n);if(v<=0)return;const fn=R[m.type];if(fn)fn(ctx,progress(m,t,i,n),m,env,v);});
}
