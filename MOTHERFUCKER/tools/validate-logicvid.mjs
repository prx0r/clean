#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const packPath = resolve(process.argv[2] ?? "packs/compiled/logicvid-reality-appears.json");
const pack = JSON.parse(await readFile(packPath, "utf8"));

const DIAGRAM_TYPES = ["side-by-side", "concept-map", "branch"];
const ALLOWED_TYPES = ["claim", "subclaim", "side-by-side", "branch", "premises", "concept-map", "verdict", "divider"];

let passed = 0, failed = 0;
function check(ok, msg) {
  if (ok) passed++; else { failed++; console.log(`❌ ${msg}`); }
}

check(pack.version === "1.0", "pack version 1.0");
check(pack.render.width === 1280 && pack.render.height === 720, "resolution 1280x720");
check(pack.render.fps === 24, "24 fps");
check(pack.render.transitionDuration === 0, "no transitions");

for (const scene of pack.scenes) {
  const moves = scene.params?.moves ?? [];
  const sid = scene.id;

  check(scene.motif === "logicvid", `${sid}: uses logicvid motif`);
  check(typeof scene.duration === "number" && scene.duration > 0, `${sid}: has duration`);
  check(typeof scene.frameCount === "number" && scene.frameCount > 0, `${sid}: has frameCount`);
  check(moves.length >= 1 && moves.length <= 6, `${sid}: ${moves.length} moves (1-6)`);

  for (const m of moves) {
    check(typeof m.enterFrame === "number", `${sid}: move has enterFrame`);
    check(m.enterFrame >= 0, `${sid}: enterFrame >= 0`);
    check(ALLOWED_TYPES.includes(m.type), `${sid}: type="${m.type}" allowed`);

    if (m.text) {
      const lines = m.text.split("\n");
      check(lines.length <= 3, `${sid}: max 3 lines (got ${lines.length} in "${m.text.slice(0, 30)}")`);
    }
  }
}

// Scene 4 uses premises which is diagram-like; scenes 3,8,9 are claim-only — allow up to 3 non-diagram scenes
const noDiagram = pack.scenes.filter(s => !s.params?.moves?.some(m => [...DIAGRAM_TYPES, "premises"].includes(m.type)));
check(noDiagram.length <= 3, `${noDiagram.length} scenes without diagrams (allow ≤3)`);

// Check no overlapping in same replacementGroup+slot
const occupied = {};
for (const scene of pack.scenes) {
  for (const m of scene.params?.moves ?? []) {
    const key = `${m.replacementGroup || "default"}:${m.slot || "center"}`;
    const ef = m.enterFrame ?? 0;
    const exit = m.exitFrame ?? scene.frameCount;
    for (const [okey, range] of Object.entries(occupied)) {
      if (okey === `${scene.id}:${key}`) continue;
      const [oScene, oKey] = okey.split(":");
      if (oScene !== scene.id) continue;
      if (oKey !== key) continue;
      const [oEnter, oExit] = range;
      if (ef < oExit && exit > oEnter) {
        check(false, `${scene.id}: overlap in ${key} (${m.type} at ${ef}-${exit} overlaps ${oEnter}-${oExit})`);
      }
    }
    occupied[`${scene.id}:${key}`] = [ef, exit];
  }
}

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
