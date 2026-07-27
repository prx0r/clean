#!/usr/bin/env node
import { createCanvas, Path2D, PathOp } from "@napi-rs/canvas";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

const outputDir=process.argv[2]??"build/canvas-capability-probe";
await mkdir(outputDir,{recursive:true});
const canvas=createCanvas(1280,720);
const ctx=canvas.getContext("2d",{colorSpace:"display-p3"});
ctx.fillStyle="#f6f1e7";ctx.fillRect(0,0,1280,720);
const support={
  conicGradient:typeof ctx.createConicGradient==="function",
  pathOp:typeof Path2D.prototype.op==="function",
  pathTrim:typeof Path2D.prototype.trim==="function",
  pathDash:typeof Path2D.prototype.dash==="function",
  pathStroke:typeof Path2D.prototype.stroke==="function",
  pathSimplify:typeof Path2D.prototype.simplify==="function",
  pathTransform:typeof Path2D.prototype.transform==="function",
  pathOpEnum:Object.keys(PathOp??{}),
};
ctx.font="24px sans-serif";ctx.fillStyle="#222";ctx.fillText("Skia / @napi-rs/canvas capability probe",56,60);
Object.entries(support).filter(([,value])=>typeof value==="boolean").forEach(([label,value],index)=>{
  ctx.font="18px monospace";ctx.fillStyle=value?"#236b4d":"#a13f45";
  ctx.fillText(`${value?"YES":"NO "}  ${label}`,70,115+index*40);
});
if(support.conicGradient){
  const gradient=ctx.createConicGradient(0,850,300);
  gradient.addColorStop(0,"#ffcf5b");gradient.addColorStop(0.33,"#cf3f70");gradient.addColorStop(0.66,"#3257c8");gradient.addColorStop(1,"#ffcf5b");
  ctx.fillStyle=gradient;ctx.beginPath();ctx.arc(850,300,145,0,Math.PI*2);ctx.fill();
}
await writeFile(join(outputDir,"capabilities.json"),JSON.stringify(support,null,2));
await writeFile(join(outputDir,"capabilities.png"),canvas.toBuffer("image/png"));
console.log(JSON.stringify(support,null,2));
