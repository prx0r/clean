#!/usr/bin/env node
import { loadCapabilityScenePack } from "../src/load-capability-scene-pack.mjs";
import { renderContactSheet, renderVideo } from "../renderer.mjs";
import { mkdir } from "node:fs/promises";
import { resolve, join } from "node:path";
import { fileURLToPath } from "node:url";
const ROOT = resolve(fileURLToPath(import.meta.url), "../..");
const packPath = join(ROOT, "packs/anatomy-test.json");
const pack = await loadCapabilityScenePack(packPath);
console.log("Pack loaded:", pack.id, "| Theme:", pack.theme, "| Scenes:", pack.scenes.length);
await mkdir(join(ROOT, "build/anatomy-test"), { recursive: true });
const contact = join(ROOT, "build/anatomy-test/anatomy-test-contact.png");
await renderContactSheet(pack, contact, { columns: 3, cellWidth: 480 });
console.log("Contact sheet:", contact);
const output = join(ROOT, "build/anatomy-test/anatomy-test.mp4");
const result = await renderVideo(pack, output);
console.log("Render:", result);
