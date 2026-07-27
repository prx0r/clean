#!/usr/bin/env node
import { loadCapabilityScenePack } from "../src/load-capability-scene-pack.mjs";
import { renderContactSheet, renderVideo } from "../renderer.mjs";
import { mkdir } from "node:fs/promises";
import { resolve, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(import.meta.url), "../..");
const packPath = join(ROOT, "packs/neuro-test.json");
const output = join(ROOT, "build/neuro-test/neuro-test.mp4");
const pack = await loadCapabilityScenePack(packPath);

console.log("Pack loaded:", pack.id);
console.log("Theme:", pack.theme);
console.log("Scenes:", pack.scenes.length);
for (const s of pack.scenes) {
  console.log("  " + s.id + ": " + s.params.visual + " (" + s.duration + "s)");
}

await mkdir(join(ROOT, "build/neuro-test"), { recursive: true });
const contact = join(ROOT, "build/neuro-test/neuro-test-contact.png");
await renderContactSheet(pack, contact, { columns: 3, cellWidth: 480 });
console.log("Contact sheet:", contact);

const result = await renderVideo(pack, output);
console.log("Render result:", JSON.stringify(result));
