#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { spawnSync } from "node:child_process";

const packPath = resolve(process.argv[2] ?? "packs/compiled/logicvid-reality-appears.json");
const audioPath = process.argv[3] ? resolve(process.argv[3]) : null;
const pack = JSON.parse(await readFile(packPath, "utf8"));

const DIAGRAM_TYPES = ["side-by-side", "concept-map", "branch"];
const ALLOWED_TYPES = ["claim", "subclaim", "side-by-side", "branch", "premises", "concept-map", "verdict", "divider"];

let passed = 0, failed = 0;
let errors = [];
function check(ok, msg) {
  if (ok) passed++;
  else { failed++; errors.push(`❌ ${msg}`); }
}

// --- Pack-level ---
check(pack.version === "1.0", "pack version 1.0");
check(pack.render.width === 1280 && pack.render.height === 720, "resolution 1280x720");
check(pack.render.fps === 24, "24 fps");
check(pack.render.transitionDuration === 0, "no transitions");

// --- Audio: check for leading silence (>100ms) ---
if (audioPath) {
  const result = spawnSync("ffmpeg", [
    "-i", audioPath, "-af", "silencedetect=n=-50dB:d=0.05", "-f", "null", "-"
  ], { encoding: "utf8" });
  const output = result.stderr + result.stdout;
  const silences = [...output.matchAll(/silence_start: (\S+)/g)];
  const leadingSilence = silences.find(s => parseFloat(s[1]) < 0.5);
  check(!leadingSilence, `audio: no leading silence (detected at ${leadingSilence ? parseFloat(leadingSilence[1]).toFixed(3)+'s' : 'none'})`);
}

// --- Per-scene ---
const noDiagramScenes = [];
for (const scene of pack.scenes) {
  const moves = scene.params?.moves ?? [];
  const sid = scene.id;

  check(scene.motif === "logicvid", `${sid}: uses logicvid motif`);
  check(typeof scene.duration === "number" && scene.duration > 0, `${sid}: has duration`);
  check(typeof scene.frameCount === "number" && scene.frameCount > 0, `${sid}: has frameCount`);
  check(moves.length >= 1 && moves.length <= 6, `${sid}: ${moves.length} moves (1-6)`);

  const hasDiagram = moves.some(m => [...DIAGRAM_TYPES, "premises"].includes(m.type));
  if (!hasDiagram) noDiagramScenes.push(sid);

  for (const m of moves) {
    check(typeof m.enterFrame === "number", `${sid}: move has enterFrame`);
    check(m.enterFrame >= 0, `${sid}: enterFrame >= 0`);
    check(m.enterFrame < scene.frameCount, `${sid}: enterFrame < frameCount`);
    check(ALLOWED_TYPES.includes(m.type), `${sid}: type="${m.type}" allowed`);

    if (m.text) {
      const lines = m.text.split("\n");
      check(lines.length <= 3, `${sid}: max 3 lines (got ${lines.length} in "${m.text.slice(0, 30)}")`);
    }
  }

  // --- Replacement group overlap check ---
  // For each slot, check move intervals for overlaps
  const slotIntervals = {};
  for (let i = 0; i < moves.length; i++) {
    const m = moves[i];
    const key = `${m.replacementGroup || "default"}:${m.slot || "center"}`;
    const enter = m.enterFrame ?? 0;
    const exit = m.exitFrame != null ? m.exitFrame : scene.frameCount;
    if (!slotIntervals[key]) slotIntervals[key] = [];
    slotIntervals[key].push({ enter, exit, idx: i, type: m.type });
  }
  for (const [slot, intervals] of Object.entries(slotIntervals)) {
    // Sort by enterFrame ascending
    intervals.sort((a, b) => a.enter - b.enter);
    // Check: for each interval, the next should start AFTER the current OR be the same
    for (let i = 0; i < intervals.length; i++) {
      const cur = intervals[i];
      for (let j = i + 1; j < intervals.length; j++) {
        const next = intervals[j];
        // If the NEXT move has higher index AND enters while current is still active,
        // it replaces the current — this is fine. But if it has LOWER index, current replaces it.
        if (cur.idx > next.idx && cur.enter < next.exit && cur.exit > next.enter) {
          check(false, `${sid}: slot "${slot}": older move #${cur.idx} (${cur.type} at ${cur.enter}-${cur.exit}) overlaps newer #${next.idx} (${next.type} at ${next.enter}-${next.exit})`);
        }
        // Also check: if two moves have the same enterFrame in the same slot, that's an error
        if (cur.enter === next.enter && cur.exit === next.exit) {
          check(false, `${sid}: slot "${slot}": moves #${cur.idx} and #${next.idx} have identical frame range`);
        }
      }
    }
  }
}

check(noDiagramScenes.length <= 3, `${noDiagramScenes.length} scenes without diagrams (${noDiagramScenes.join(",")}) (allow ≤3)`);

// --- Summary ---
for (const e of errors) console.log(e);
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
