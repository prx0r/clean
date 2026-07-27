import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { createCanvas } from "@napi-rs/canvas";

import { applyTextStyle, fontStatus, initializeFonts } from "../src/fonts.mjs";
import {
  compileEssayProgram,
  extractEssayParagraphs,
  extractEssayUnits,
  loadEssayProgram,
} from "../src/essay-program.mjs";
import {
  FrameRenderer,
  loadPack,
  renderVideo,
  validateVideo,
} from "../src/renderer.mjs";
import { assertPack } from "../src/schema.mjs";
import { semanticVisualNames } from "../src/semantic-visuals.mjs";
import { typography } from "../src/theme.mjs";
import { auditVisualProgram } from "../src/visual-auditor.mjs";
import { assertEssayAnalysis } from "../src/analysis.mjs";

const packPath = new URL("../packs/hrdaya-original.json", import.meta.url);
const essayProgramPath = new URL("../programs/infinite-learned-visual-program.json", import.meta.url);
const essayPath = new URL("../essays/the-infinite-learned-to-say-i-cant.md", import.meta.url);
const songProgramPath = new URL("../programs/song-no-singer-visual-program.json", import.meta.url);
const songEssayPath = new URL("../essays/the-song-with-no-singer.md", import.meta.url);

function sha256(buffer) {
  return createHash("sha256").update(buffer).digest("hex");
}

test("the original demonstration pack satisfies the AI contract", async () => {
  const pack = await loadPack(packPath);
  assert.equal(pack.scenes.length, 6);
  assert.equal(pack.render.width, 1920);
  assert.equal(pack.render.fps, 24);
});

test("the contract rejects IAST accidentally placed in the Devanagari field", async () => {
  const pack = JSON.parse(await readFile(packPath, "utf8"));
  pack.scenes[0].devanagari = "hṛdayam";
  assert.throws(() => assertPack(pack), /must contain Devanāgarī/);
});

test("full Latin Extended and Sanskrit fonts register and shape", () => {
  initializeFonts();
  const status = fontStatus();
  assert.equal(status.latinRegistered, true);
  assert.equal(status.devanagariRegistered, true);
  const canvas = createCanvas(900, 220);
  const ctx = canvas.getContext("2d");
  applyTextStyle(ctx, typography.title);
  assert.ok(ctx.measureText("Pratyabhijñā — Śiva’s reflexive light").width > 250);
  applyTextStyle(ctx, typography.devanagariLarge, { lang: "sa" });
  assert.ok(ctx.measureText("प्रत्यभिज्ञा हृदयं शिवस्य").width > 200);
});

test("the same scene and time produce byte-identical Skia frames", async () => {
  const pack = await loadPack(packPath);
  const renderer = new FrameRenderer(pack, { width: 640, height: 360, fps: 8 });
  renderer.render(pack.scenes[0], 0.63);
  const first = sha256(renderer.png());
  renderer.render(pack.scenes[0], 0.63);
  const second = sha256(renderer.png());
  renderer.render(pack.scenes[0], 0.67);
  const moving = sha256(renderer.png());
  assert.equal(first, second);
  assert.notEqual(first, moving);
});

test("the declarative composition motif renders without custom code", async () => {
  const pack = await loadPack(packPath);
  pack.scenes = [{
    id: "ai01",
    title: "A Declarative World",
    subtitle: "An AI-authored layer stack remains inside the visual grammar.",
    term: "Saṃvid",
    devanagari: "संवित्",
    motif: "composition",
    layers: [
      { type: "grid", x: 640, y: 292, columns: 9, rows: 5, color: "secondary", warp: 5 },
      { type: "orb", x: 640, y: 292, radius: 36, color: "luminous", motion: { scale: 0.05, cycles: 0.7 } },
      { type: "lotus", x: 640, y: 292, radius: 92, petals: 10, color: "accent", motion: { rotation: 0.03 } },
      { type: "label", x: 640, y: 295, text: "संवित्", script: "devanagari", size: 30, color: "secondary" }
    ]
  }];
  assertPack(pack);
  const renderer = new FrameRenderer(pack, { width: 640, height: 360, fps: 8 });
  renderer.render(pack.scenes[0], 0.72);
  assert.ok(renderer.png().length > 20_000);
});

test("the essay program covers every narration paragraph exactly once", async () => {
  const compiled = await loadEssayProgram(essayProgramPath);
  const essay = await readFile(essayPath, "utf8");
  assert.equal(compiled.pack.scenes.length, 44);
  assert.equal(compiled.storyboard.paragraphCount, extractEssayParagraphs(essay).length);
  assert.equal(compiled.storyboard.shots[0].paragraphRange[0], 1);
  assert.equal(compiled.storyboard.shots.at(-1).paragraphRange[1], 164);
  assert.equal(compiled.storyboard.runtimeSeconds, 685.2916666666666);
});

test("an exact narration manifest overrides draft timing on frame boundaries", async () => {
  const program = JSON.parse(await readFile(essayProgramPath, "utf8"));
  const essay = await readFile(essayPath, "utf8");
  const draft = compileEssayProgram(program, essay);
  const shots = draft.storyboard.shots.map((shot) => ({
    id: shot.id,
    duration: shot.duration,
  }));
  shots[0].duration = 6.125;
  const compiled = compileEssayProgram(program, essay, {
    shots,
  });
  assert.equal(compiled.storyboard.shots[0].duration, 6.125);
  assert.equal(compiled.storyboard.shots[1].start, 6.125);
});

test("publication timing cannot silently mix exact and estimated shots", async () => {
  const program = JSON.parse(await readFile(essayProgramPath, "utf8"));
  const essay = await readFile(essayPath, "utf8");
  assert.throws(
    () => compileEssayProgram(program, essay, {
      shots: [{ id: "inf-001", duration: 6.125 }],
    }),
    /is missing 43 shot/,
  );
});

test("the v2 song program passes correspondence and typed-source audits", async () => {
  const compiled = await loadEssayProgram(songProgramPath);
  const markdown = await readFile(songEssayPath, "utf8");
  const units = extractEssayUnits(markdown);
  assert.equal(units.length, 477);
  assert.equal(units.filter((unit) => unit.type === "visual-only").length, 3);
  assert.equal(units.reduce((total, unit) => total + unit.wordCount, 0), 4496);
  assert.equal(compiled.storyboard.shotCount, 88);
  assert.equal(compiled.storyboard.shots.at(-1).paragraphRange[1], 477);
  assert.equal(compiled.storyboard.correspondenceAudit.valid, true);
  assert.deepEqual(compiled.storyboard.correspondenceAudit.errors, []);
  assert.deepEqual(compiled.storyboard.correspondenceAudit.warnings, []);
});

test("the argument IR is complete and contains no visual selection", async () => {
  const analysis = JSON.parse(await readFile(
    new URL("../programs/song-no-singer-analysis.json", import.meta.url),
    "utf8",
  ));
  assertEssayAnalysis(analysis);
  assert.equal(analysis.sourceUnitCount, 477);
  assert.equal(analysis.beats.length, 88);
  assert.equal(analysis.continuityCandidates.length, 7);
});

test("the v2 auditor rejects a semantic mechanism mismatch", async () => {
  const program = JSON.parse(await readFile(songProgramPath, "utf8"));
  program.shots[0].visual = "memory-relay";
  const audit = auditVisualProgram(program);
  assert.equal(audit.valid, false);
  assert.match(audit.errors.join("\n"), /cannot be used for "emergence"/);
});

test("every semantic essay mechanism renders through native Skia", async () => {
  const compiled = await loadEssayProgram(essayProgramPath);
  const base = compiled.pack.scenes[0];
  const representatives = semanticVisualNames.map((visual, index) => {
    const worked = compiled.pack.scenes.find((candidate) => candidate.params.visual === visual);
    return worked ?? {
      ...base,
      id: `system-${String(index).padStart(2, "0")}`,
      title: visual,
      subtitle: "Synthetic mechanism coverage frame.",
      params: { visual },
    };
  });
  compiled.pack.scenes = representatives;
  const renderer = new FrameRenderer(compiled.pack, { width: 640, height: 360, fps: 8 });
  for (const scene of representatives) {
    renderer.render(scene, 0.72);
    assert.ok(renderer.png().length > 12_000, `${scene.params.visual} produced an empty-looking frame`);
  }
});

test("the raw Skia-to-ffmpeg path produces a validated H.264 MP4", async () => {
  const directory = await mkdtemp(join(tmpdir(), "tantraloka-skia-test-"));
  try {
    const pack = await loadPack(packPath);
    pack.scenes = [
      { ...pack.scenes[0], id: "smoke-a", duration: 1 },
      { ...pack.scenes[1], id: "smoke-b", duration: 1 },
    ];
    pack.render = {
      ...pack.render,
      fps: 4,
      sceneDuration: 1,
      transitionDuration: 0.5,
      crf: 24,
      preset: "veryfast",
    };
    const output = join(directory, "smoke.mp4");
    await renderVideo(pack, output, { width: 640, height: 360, fps: 4, crf: 24, preset: "veryfast" });
    const validation = validateVideo(pack, output, { width: 640, height: 360, fps: 4 });
    assert.equal(validation.valid, true, validation.errors.join("; "));
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
