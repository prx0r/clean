#!/usr/bin/env node
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { renderContactSheet, renderVideo, validateVideo } from "../renderer.mjs";
import { loadCapabilityScenePack } from "../src/load-capability-scene-pack.mjs";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const packPath = resolve(process.argv[2] ?? join(ROOT, "packs/invariant-composition-demo.json"));
const output = resolve(process.argv[3] ?? join(ROOT, "build/invariant-composition-demo/invariant-composition-demo.mp4"));
const pack = await loadCapabilityScenePack(packPath);

await mkdir(dirname(output), { recursive: true });
const contact = join(dirname(output), `${pack.id}-contact-sheet.png`);
await renderContactSheet(pack, contact, { columns: 3, cellWidth: 480 });
const result = await renderVideo(pack, output);
const validation = validateVideo(pack, output);
await writeFile(
  join(dirname(output), `${pack.id}-validation.json`),
  JSON.stringify({ render: result, validation }, null, 2),
);
if (!validation.valid) {
  throw new Error(validation.errors.join("\n"));
}
console.log(JSON.stringify({ video: output, contactSheet: contact, validation: true }, null, 2));
