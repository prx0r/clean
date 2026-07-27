#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const [input, output] = process.argv.slice(2);
if (!input || !output) {
  throw new Error("Usage: node tools/export-storyboard.mjs <compiled-storyboard.json> <public-timing-map.json>");
}

const storyboard = JSON.parse(await readFile(resolve(input), "utf8"));
const publicStoryboard = {
  ...storyboard,
  shots: storyboard.shots.map(({ spokenPassage, visualOnlySource, ...shot }) => shot),
};
await writeFile(resolve(output), `${JSON.stringify(publicStoryboard, null, 2)}\n`);
console.log(resolve(output));
