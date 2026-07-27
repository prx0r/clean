import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { createCanvas } from "@napi-rs/canvas";

import { applyTextStyle, fontStatus, initializeFonts } from "../src/fonts.mjs";
import {
  FrameRenderer,
  loadPack,
  renderVideo,
  validateVideo,
} from "../src/renderer.mjs";
import { assertPack } from "../src/schema.mjs";
import { typography } from "../src/theme.mjs";

const packPath = new URL("../packs/hrdaya-original.json", import.meta.url);

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

test("the raw Skia-to-ffmpeg path produces a validated H.264 MP4", async () => {
  const directory = await mkdtemp(join(tmpdir(), "tantraloka-skia-test-"));
  try {
    const pack = await loadPack(packPath);
    pack.scenes = [{ ...pack.scenes[0], duration: 1 }];
    pack.render = { ...pack.render, fps: 4, sceneDuration: 1, crf: 24, preset: "veryfast" };
    const output = join(directory, "smoke.mp4");
    await renderVideo(pack, output, { width: 640, height: 360, fps: 4, crf: 24, preset: "veryfast" });
    const validation = validateVideo(pack, output, { width: 640, height: 360, fps: 4 });
    assert.equal(validation.valid, true, validation.errors.join("; "));
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
