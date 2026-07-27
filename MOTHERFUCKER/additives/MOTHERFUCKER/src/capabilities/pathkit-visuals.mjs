import { rgba } from "../../math.mjs";
import { trimPath } from "../geometry/path-ops.mjs";
import { lotusPath } from "../geometry/lotus-generators.mjs";
import { chakraYantra, sriYantraApprox } from "../geometry/yantra-generators.mjs";
import { flameAureolePaths } from "../geometry/flame-generators.mjs";
import { mandalaLayers } from "../geometry/mandala-generators.mjs";
import { conicGradient } from "../materials/materials.mjs";

function stroke(ctx,path,color,width=1.6,alpha=1,blur=0,dash=[]) {
  ctx.save(); ctx.globalAlpha=alpha; ctx.strokeStyle=color; ctx.lineWidth=width;
  ctx.setLineDash(dash); ctx.shadowColor=blur?color:"transparent"; ctx.shadowBlur=blur;
  ctx.stroke(path); ctx.restore();
}
function fill(ctx,path,style,alpha=1,blend="source-over") {
  ctx.save(); ctx.globalCompositeOperation=blend; ctx.globalAlpha=alpha;
  ctx.fillStyle=style; ctx.fill(path); ctx.restore();
}

export function lotusRingAsset(ctx,t,params,env) {
  const path=lotusPath({cx:params.x??640,cy:params.y??300,petals:params.petals??8,radius:params.radius??105,petalLength:params.petalLength??78,petalWidth:params.petalWidth??24});
  const gradient=conicGradient(ctx,{cx:params.x??640,cy:params.y??300,angle:t*Math.PI*0.18,
    stops:[[0,"#ffe9a6"],[0.35,"#d79f36"],[0.7,"#8b2f3c"],[1,"#ffe9a6"]]});
  fill(ctx,path,gradient??rgba("#d79f36",0.2),0.18,"screen");
  stroke(ctx,path,params.color??env.theme.luminous,1.4,0.85,4);
}
export function yantraCoreAsset(ctx,t,params,env) {
  const path=params.variant==="sri"?sriYantraApprox({cx:params.x??640,cy:params.y??300,radius:params.radius??145}):
    chakraYantra({cx:params.x??640,cy:params.y??300,petals:params.petals??8});
  stroke(ctx,path,params.color??env.theme.accent,1.45,0.8,3);
}
export function flameAureoleAsset(ctx,t,params,env) {
  const paths=flameAureolePaths({cx:params.x??640,cy:params.y??300,radius:params.radius??145,tongues:params.tongues??20,flameHeight:params.flameHeight??60,phase:t*0.08});
  paths.forEach((path,index)=>{
    fill(ctx,path,index%2?rgba("#d79f36",0.22):rgba("#a64252",0.18),0.8,"screen");
    stroke(ctx,path,index%2?env.theme.luminous:env.theme.accent,1.1,0.75,5);
  });
}
export function mandalaLayersAsset(ctx,t,params,env) {
  const layers=mandalaLayers({cx:params.x??640,cy:params.y??300,size:params.size??360,petals:params.petals??8,spokes:params.spokes??8});
  Object.entries(layers).forEach(([name,path],index)=>stroke(ctx,path,[env.theme.structure,env.theme.secondary,env.theme.accent,env.theme.luminous][index%4],1.1+index*0.08,0.55+index*0.05,index>2?4:0));
}

export const assetImplementations=Object.freeze({
  "lotus-ring":lotusRingAsset,
  "yantra-core":yantraCoreAsset,
  "flame-aureole":flameAureoleAsset,
  "mandala-layers":mandalaLayersAsset,
});

function lotusUnfold(ctx,t,scene,env) {
  const full=lotusPath({cx:640,cy:305,petals:scene.params?.petals??12,radius:95,petalLength:82,petalWidth:22});
  stroke(ctx,trimPath(full,0,Math.max(0.001,t)),env.theme.luminous,2,0.9,7);
  if(t>0.5) fill(ctx,full,rgba(env.theme.accent,0.08),(t-0.5)*0.3,"screen");
}
function yantraConstruction(ctx,t,scene,env) {
  const layers=mandalaLayers({cx:640,cy:305,size:390,petals:scene.params?.petals??8,spokes:8});
  const order=["bindu","core","spokes","lotus","outerRing","enclosure"];
  order.forEach((name,index)=>{
    const local=Math.max(0,Math.min(1,(t-index*0.12)/0.36));
    stroke(ctx,trimPath(layers[name],0,Math.max(0.001,local)),
      [env.theme.luminous,env.theme.accent,env.theme.secondary,env.theme.luminous,env.theme.structure,env.theme.accent][index],
      1.2+index*0.08,0.82,index<4?5:0);
  });
}
function mandalaEntry(ctx,t,scene,env) {
  mandalaLayersAsset(ctx,t,{x:640,y:305,size:390,petals:8,spokes:8},env);
  const radii=[180,140,92,48,8], segment=Math.min(radii.length-1,Math.floor(t*radii.length));
  const local=(t*radii.length)%1, r=radii[segment]+((radii[segment+1]??0)-radii[segment])*local;
  const angle=-Math.PI/2+t*Math.PI*4, x=640+Math.cos(angle)*r, y=305+Math.sin(angle)*r;
  ctx.save(); ctx.globalCompositeOperation="screen";
  const gradient=ctx.createRadialGradient(x,y,0,x,y,22);
  gradient.addColorStop(0,rgba(env.theme.luminous,0.95)); gradient.addColorStop(1,rgba(env.theme.luminous,0));
  ctx.fillStyle=gradient; ctx.fillRect(x-22,y-22,44,44); ctx.restore();
}
export const mechanismImplementations=Object.freeze({
  "lotus-unfold":lotusUnfold,
  "yantra-construction":yantraConstruction,
  "mandala-entry":mandalaEntry,
});
