#!/usr/bin/env node
import { loadCapabilityScenePack } from "../src/load-capability-scene-pack.mjs";
import { renderContactSheet, renderVideo } from "../renderer.mjs";
import { mkdir } from "node:fs/promises";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export async function main(packPath) {
  const pack = await loadCapabilityScenePack(resolve(packPath));
  const outDir = join("build", pack.id);
  await mkdir(outDir, { recursive: true });
  const contact = join(outDir, `${pack.id}-contact.png`);
  await renderContactSheet(pack, contact, { columns: 3, cellWidth: 480 });
  const output = join(outDir, `${pack.id}.mp4`);
  const result = await renderVideo(pack, output);
  console.log(JSON.stringify({ video: output, contactSheet: contact, ...result }, null, 2));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const path = process.argv[2];
  if (!path) { console.error("Usage: node render-pack.mjs packs/pack.json"); process.exit(1); }
  await main(path);
}
