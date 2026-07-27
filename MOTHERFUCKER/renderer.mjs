import { once } from "node:events";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { spawn, spawnSync } from "node:child_process";

import { createCanvas } from "@napi-rs/canvas";

import { initializeFonts } from "./fonts.mjs";
import { smoothstep } from "./math.mjs";
import { renderMotif } from "./motifs.mjs";
import {
  clearWithBackground,
  createStableBackground,
  drawBorder,
  drawFooter,
} from "./primitives.mjs";
import { assertPack } from "./schema.mjs";
import { getTheme } from "./theme.mjs";
import { loadAudioFeatureManifest, sampleAudioFeatures } from "./src/audio/audio-features.mjs";

export async function loadPack(path) {
  const data = JSON.parse(await readFile(path, "utf8"));
  return assertPack(data);
}

export class FrameRenderer {
  constructor(pack, options = {}) {
    assertPack(pack);
    initializeFonts();
    this.pack = pack;
    this.width = options.width ?? pack.render.width;
    this.height = options.height ?? pack.render.height;
    this.fps = options.fps ?? pack.render.fps;
    this.canvas = createCanvas(this.width, this.height);
    this.ctx = this.canvas.getContext("2d");
    this.ctx.imageSmoothingEnabled = true;
    this.ctx.imageSmoothingQuality = "high";
    this.backgrounds = new Map();
    this.audio = options.audio ?? null;
  }

  backgroundFor(scene) {
    const themeName = scene.theme ?? this.pack.theme;
    const seed = (scene.seed ?? this.pack.seed) >>> 0;
    const key = `${themeName}:${seed}`;
    if (!this.backgrounds.has(key)) {
      this.backgrounds.set(
        key,
        createStableBackground(this.width, this.height, getTheme(themeName), seed),
      );
    }
    return this.backgrounds.get(key);
  }

  render(scene, t) {
    const theme = getTheme(scene.theme ?? this.pack.theme);
    clearWithBackground(this.ctx, this.backgroundFor(scene), this.width, this.height);
    drawBorder(this.ctx, theme);
    const seconds = this.frame != null ? this.frame / this.fps : 0;
    renderMotif(this.ctx, t, scene, {
      theme,
      seed: (scene.seed ?? this.pack.seed) >>> 0,
      width: this.width,
      height: this.height,
      audio: this.audio ? sampleAudioFeatures(this.audio, seconds) : null,
    });
    drawFooter(this.ctx, scene, theme, smoothstep(0.01, 0.12, t));
    return this.canvas;
  }

  rgba() {
    return this.canvas.data();
  }

  png() {
    return this.canvas.encodeSync("png");
  }
}

async function writeChunk(stream, chunk) {
  if (!stream.write(chunk)) await once(stream, "drain");
}

export async function renderVideo(pack, outputPath, options = {}) {
  assertPack(pack);
  let audioManifest = null;
  if (pack.audioManifest) {
    try {
      audioManifest = await loadAudioFeatureManifest(resolve(pack.audioManifest));
    } catch (e) {
      console.warn(`Audio manifest not loaded: ${e.message}`);
    }
  }
  const audioOption = audioManifest ?? options.audio ?? null;
  const renderer = new FrameRenderer(pack, { ...options, audio: audioOption });
  const fps = renderer.fps;
  const crf = options.crf ?? pack.render.crf ?? 16;
  const preset = options.preset ?? pack.render.preset ?? "medium";
  const transitionDuration = options.transitionDuration ?? pack.render.transitionDuration ?? 0;
  const absoluteOutput = resolve(outputPath);
  await mkdir(dirname(absoluteOutput), { recursive: true });

  const ffmpeg = spawn("ffmpeg", [
    "-y",
    "-loglevel", "error",
    "-f", "rawvideo",
    "-pix_fmt", "rgba",
    "-s:v", `${renderer.width}x${renderer.height}`,
    "-r", String(fps),
    "-i", "-",
    "-an",
    "-c:v", "libx264",
    "-preset", preset,
    "-crf", String(crf),
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    absoluteOutput,
  ], { stdio: ["pipe", "ignore", "pipe"] });

  let ffmpegError = "";
  ffmpeg.stderr.setEncoding("utf8");
  ffmpeg.stderr.on("data", (chunk) => {
    ffmpegError += chunk;
  });

  const framesPerScene = pack.scenes.map((scene) => (
    Math.round((scene.duration ?? pack.render.sceneDuration) * fps)
  ));
  const totalFrames = framesPerScene.reduce((sum, count) => sum + count, 0);
  const transitionFrames = Math.max(0, Math.round(transitionDuration * fps));
  const previousRenderer = transitionFrames > 0 ? new FrameRenderer(pack, options) : undefined;
  const composite = transitionFrames > 0 ? createCanvas(renderer.width, renderer.height) : undefined;
  const compositeContext = composite?.getContext("2d");
  let rendered = 0;
  let nextProgress = 0.1;
  let globalFrame = 0;

  try {
    for (const [sceneIndex, scene] of pack.scenes.entries()) {
      const count = framesPerScene[sceneIndex];
      for (let frame = 0; frame < count; frame += 1) {
        const t = frame / Math.max(1, count - 1);
        renderer.frame = globalFrame;
        renderer.render(scene, t);
        let pixels = renderer.rgba();
        if (sceneIndex > 0 && frame < Math.min(transitionFrames, count)) {
          const previous = pack.scenes[sceneIndex - 1];
          previousRenderer.render(previous, 1);
          const progress = smoothstep(
            0,
            Math.max(1, Math.min(transitionFrames, count) - 1),
            frame,
          );
          compositeContext.setTransform(1, 0, 0, 1, 0, 0);
          compositeContext.clearRect(0, 0, renderer.width, renderer.height);
          compositeContext.globalAlpha = 1;
          compositeContext.drawImage(previousRenderer.canvas, 0, 0);
          compositeContext.globalAlpha = progress;
          compositeContext.drawImage(renderer.canvas, 0, 0);
          compositeContext.globalAlpha = 1;
          pixels = composite.data();
        }
        await writeChunk(ffmpeg.stdin, pixels);
        rendered += 1;
        globalFrame += 1;
        if (rendered / totalFrames >= nextProgress) {
          process.stdout.write(`Rendered ${Math.round(nextProgress * 100)}% (${rendered}/${totalFrames})\n`);
          nextProgress += 0.1;
        }
      }
    }
    ffmpeg.stdin.end();
  } catch (error) {
    ffmpeg.stdin.destroy();
    ffmpeg.kill("SIGTERM");
    throw error;
  }

  const [code] = await once(ffmpeg, "close");
  if (code !== 0) {
    throw new Error(`ffmpeg failed with code ${code}: ${ffmpegError.trim()}`);
  }

  return {
    outputPath: absoluteOutput,
    frames: totalFrames,
    fps,
    width: renderer.width,
    height: renderer.height,
    duration: totalFrames / fps,
  };
}

export async function renderPoster(pack, sceneId, outputPath, options = {}) {
  assertPack(pack);
  const scene = pack.scenes.find((candidate) => candidate.id === sceneId);
  if (!scene) throw new Error(`Unknown scene id "${sceneId}"`);
  const renderer = new FrameRenderer(pack, options);
  renderer.render(scene, options.time ?? 0.72);
  const absoluteOutput = resolve(outputPath);
  await mkdir(dirname(absoluteOutput), { recursive: true });
  await writeFile(absoluteOutput, renderer.png());
  return absoluteOutput;
}

export async function renderContactSheet(pack, outputPath, options = {}) {
  assertPack(pack);
  const columns = options.columns ?? 3;
  const cellWidth = options.cellWidth ?? 480;
  const cellHeight = Math.round(cellWidth * 9 / 16);
  const rows = Math.ceil(pack.scenes.length / columns);
  const renderer = new FrameRenderer(pack, {
    width: cellWidth,
    height: cellHeight,
    fps: 1,
  });
  const sheet = createCanvas(columns * cellWidth, rows * cellHeight);
  const ctx = sheet.getContext("2d");
  for (const [index, scene] of pack.scenes.entries()) {
    renderer.render(scene, options.time ?? 0.72);
    ctx.drawImage(
      renderer.canvas,
      (index % columns) * cellWidth,
      Math.floor(index / columns) * cellHeight,
      cellWidth,
      cellHeight,
    );
  }
  const absoluteOutput = resolve(outputPath);
  await mkdir(dirname(absoluteOutput), { recursive: true });
  await writeFile(absoluteOutput, sheet.encodeSync("png"));
  return absoluteOutput;
}

export function probeVideo(path) {
  const result = spawnSync("ffprobe", [
    "-v", "error",
    "-show_entries",
    "stream=codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,nb_frames:format=duration,size",
    "-of", "json",
    resolve(path),
  ], { encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`ffprobe failed: ${result.stderr.trim()}`);
  }
  return JSON.parse(result.stdout);
}

export function validateVideo(pack, path, options = {}) {
  const probe = probeVideo(path);
  const stream = probe.streams?.[0];
  const expectedWidth = options.width ?? pack.render.width;
  const expectedHeight = options.height ?? pack.render.height;
  const expectedFps = options.fps ?? pack.render.fps;
  const expectedFrames = pack.scenes.reduce((sum, scene) => (
    sum + Math.round((scene.duration ?? pack.render.sceneDuration) * expectedFps)
  ), 0);
  const errors = [];
  if (!stream) errors.push("No video stream");
  if (stream?.codec_name !== "h264") errors.push(`Expected h264, got ${stream?.codec_name}`);
  if (stream?.width !== expectedWidth || stream?.height !== expectedHeight) {
    errors.push(`Expected ${expectedWidth}x${expectedHeight}, got ${stream?.width}x${stream?.height}`);
  }
  if (stream?.pix_fmt !== "yuv420p") errors.push(`Expected yuv420p, got ${stream?.pix_fmt}`);
  if (stream?.r_frame_rate !== `${expectedFps}/1`) {
    errors.push(`Expected ${expectedFps}/1 fps, got ${stream?.r_frame_rate}`);
  }
  if (Number(stream?.nb_frames) !== expectedFrames) {
    errors.push(`Expected ${expectedFrames} frames, got ${stream?.nb_frames}`);
  }
  const expectedDuration = expectedFrames / expectedFps;
  if (Math.abs(Number(probe.format?.duration) - expectedDuration) > 0.05) {
    errors.push(`Expected ${expectedDuration}s, got ${probe.format?.duration}s`);
  }
  return { valid: errors.length === 0, errors, probe };
}
