#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const packPath = resolve(process.argv[2] ?? "packs/logicvid-v5.json");
const pack = JSON.parse(await readFile(packPath, "utf8"));

const DIAGRAM_TYPES = ["side-by-side", "concept-map", "branch"];
const ALLOWED_TYPES = ["claim", "subclaim", "side-by-side", "branch", "converge", "premises", "concept-map"];

const results = [];
function check(ok, msg) {
  results.push({ pass: !!ok, message: msg });
}

// --- Pack-level ---
check(pack.render.width === 1280 && pack.render.height === 720, "resolution 1280x720");
check(pack.render.fps === 24, "24 fps");
check(pack.render.transitionDuration === 0, "no transitions");
check(Array.isArray(pack.scenes) && pack.scenes.length >= 1, `scene count: ${pack.scenes.length}`);
check(pack.scenes.every(s => s.motif === "argument-diagram-v5"), "all scenes use v5 motif");

// --- Per-scene ---
let totalMoves = 0;
let textLines = [];
for (const scene of pack.scenes) {
  const moves = scene.params?.moves ?? [];
  const sid = scene.id;
  totalMoves += moves.length;

  // Scene duration
  check(typeof scene.duration === "number" && scene.duration > 0, `${sid}: has duration`);

  // Move count: 2-4 per scene
  check(moves.length >= 1 && moves.length <= 4, `${sid}: ${moves.length} moves (target 2-4)`);

  // At least one diagram per scene
  const hasDiagram = moves.some(m => DIAGRAM_TYPES.includes(m.type));
  check(hasDiagram, `${sid}: has a diagram type`);

  // No overlapping move windows
  let prevEnd = -1;
  for (const m of moves) {
    const start = m.at ?? 0;
    const end = start + (m.duration ?? 4);
    if (prevEnd > 0) {
      check(start >= prevEnd - 0.1, `${sid}: move "${trunc(m.text || m.left || "", 30)}" starts ${start}s after prev ends ${prevEnd}s`);
    }
    prevEnd = end;

    // Move types
    check(ALLOWED_TYPES.includes(m.type), `${sid}: type "${m.type}" is allowed`);
    check(typeof m.at === "number", `${sid}: has "at" in seconds`);
    check(typeof m.duration === "number", `${sid}: has duration`);

    // Text checks
    const textFields = [m.text, m.left, m.right, ...(m.branches || []).map(b => b.label)];
    if (m.premises) textFields.push(...m.premises);
    for (const t of textFields) {
      if (!t) continue;
      textLines.push({ sid, text: t, move: m.type });
      // No numbered lists / bullet patterns
      check(!/^[A]\d/.test(t.trim()), `${sid}: no numbered list items ("${trunc(t, 40)}")`);
      check(!/^\d+[\.\)]/.test(t.trim()), `${sid}: no numbered items ("${trunc(t, 40)}")`);
      check(!/^[-•·]/.test(t.trim()), `${sid}: no bullet items ("${trunc(t, 40)}")`);
      // Max 3 lines
      const lines = t.split("\n");
      check(lines.length <= 3, `${sid}: max 3 lines (got ${lines.length} in "${trunc(t, 40)}")`);
    }

    // Premises specific
    if (m.type === "premises") {
      check(m.premises.length <= 3, `${sid}: premises max 3 items (got ${m.premises.length})`);
    }
  }
}

// --- Content quality ---
const totalScenes = pack.scenes.length;
check(totalMoves / totalScenes <= 3.5, `avg ${(totalMoves / totalScenes).toFixed(1)} moves/scene (target ≤3.5)`);

// --- Summary ---
const passed = results.filter(r => r.pass).length;
const failed = results.filter(r => !r.pass).length;
console.log(`\nValidation: ${passed} passed, ${failed} failed of ${results.length}\n`);
for (const r of results) {
  console.log(`${r.pass ? "✅" : "❌"} ${r.message}`);
}
console.log(`\n${failed === 0 ? "ALL PASS" : `${failed} FAILURES`}`);
process.exit(failed > 0 ? 1 : 0);

function trunc(s, n) { return s.length > n ? s.slice(0, n) + "..." : s; }
