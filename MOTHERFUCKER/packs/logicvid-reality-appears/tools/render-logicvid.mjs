#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { renderVideo, renderContactSheet, validateVideo } from "../MOTHERFUCKER/renderer.mjs";

const packPath=resolve(process.argv[2]??"MOTHERFUCKER/packs/logicvid-reality-appears.json");
const output=resolve(process.argv[3]??"MOTHERFUCKER/build/logicvid-reality-appears/video.mp4");
const pack=JSON.parse(await readFile(packPath,"utf8"));
await renderContactSheet(pack,resolve("MOTHERFUCKER/build/logicvid-reality-appears/contact-sheet.png"),{columns:3,cellWidth:480,time:.72});
const result=await renderVideo(pack,output);
const validation=validateVideo(pack,output);
if(!validation.valid)throw new Error(validation.errors.join("\n"));
console.log(JSON.stringify({result,validation},null,2));
