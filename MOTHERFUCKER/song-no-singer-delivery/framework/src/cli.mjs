#!/usr/bin/env node

import { mkdir, writeFile } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  loadPack,
  renderContactSheet,
  renderPoster,
  renderVideo,
  validateVideo,
} from "./renderer.mjs";
import { fontStatus } from "./fonts.mjs";
import { motifDescriptions } from "./motifs.mjs";
import { loadEssayProgram } from "./essay-program.mjs";
import { loadEssayAnalysis } from "./analysis.mjs";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const DEFAULT_PACK = join(ROOT, "packs/hrdaya-original.json");

function parseArgs(values) {
  const positional = [];
  const options = {};
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (!value.startsWith("--")) {
      positional.push(value);
      continue;
    }
    const [rawKey, inline] = value.slice(2).split("=", 2);
    if (inline !== undefined) {
      options[rawKey] = inline;
    } else if (values[index + 1] && !values[index + 1].startsWith("--")) {
      options[rawKey] = values[index + 1];
      index += 1;
    } else {
      options[rawKey] = true;
    }
  }
  return { positional, options };
}

function numericOption(options, name) {
  if (options[name] === undefined) return undefined;
  const value = Number(options[name]);
  if (!Number.isFinite(value)) throw new Error(`--${name} must be numeric`);
  return value;
}

function usage() {
  return `Tantrāloka Skia Framework

Commands:
  render [pack.json] [--out video.mp4] [--width 1920] [--height 1080] [--fps 24]
  poster [pack.json] --scene hr01 [--out poster.png] [--time 0.72]
  contact [pack.json] [--out contact_sheet.png]
  validate [pack.json] [--video video.mp4]
  compile-essay program.json [--out build_directory] [--timings exact-timings.json]
  audit-analysis analysis.json
  audit-essay program.json
  render-essay program.json [--out video.mp4] [--timings exact-timings.json]
  motifs
  fonts

If pack.json is omitted, packs/hrdaya-original.json is used.`;
}

async function main() {
  const { positional, options } = parseArgs(process.argv.slice(2));
  const command = positional[0] ?? "help";
  const packPath = resolve(positional[1] ?? DEFAULT_PACK);

  if (command === "help" || command === "--help" || command === "-h") {
    console.log(usage());
    return;
  }
  if (command === "motifs") {
    console.log(JSON.stringify(motifDescriptions, null, 2));
    return;
  }
  if (command === "fonts") {
    console.log(JSON.stringify(fontStatus(), null, 2));
    return;
  }
  if (command === "audit-analysis") {
    if (!positional[1]) throw new Error("audit-analysis requires an essay analysis JSON path");
    const analysis = await loadEssayAnalysis(resolve(positional[1]));
    console.log(JSON.stringify({
      valid: true,
      essayId: analysis.essayId,
      sourceUnits: analysis.sourceUnitCount,
      beats: analysis.beats.length,
      continuitySystems: analysis.continuityCandidates.length,
      relationTypesUsed: new Set(analysis.beats.map((beat) => beat.relationType)).size,
    }, null, 2));
    return;
  }

  if (command === "compile-essay" || command === "audit-essay" || command === "render-essay") {
    if (!positional[1]) throw new Error(`${command} requires an essay visual program JSON path`);
    const programPath = resolve(positional[1]);
    const compiled = await loadEssayProgram(programPath, options.timings);
    if (command === "audit-essay") {
      console.log(JSON.stringify({
        valid: compiled.storyboard.correspondenceAudit.valid,
        sourceUnits: compiled.storyboard.sourceUnitCount,
        shots: compiled.storyboard.shotCount,
        runtimeSeconds: compiled.storyboard.runtimeSeconds,
        audit: compiled.storyboard.correspondenceAudit,
      }, null, 2));
      return;
    }
    const buildDirectory = command === "compile-essay"
      ? resolve(options.out ?? join(ROOT, "build", compiled.pack.id))
      : resolve(options.out ? dirname(options.out) : join(ROOT, "build", compiled.pack.id));
    await mkdir(buildDirectory, { recursive: true });
    const packPath = join(buildDirectory, `${compiled.pack.id}-compiled-pack.json`);
    const storyboardPath = join(buildDirectory, `${compiled.pack.id}-storyboard.json`);
    const narrationPath = join(buildDirectory, `${compiled.pack.id}-narration.txt`);
    await Promise.all([
      writeFile(packPath, JSON.stringify(compiled.pack, null, 2)),
      writeFile(storyboardPath, JSON.stringify(compiled.storyboard, null, 2)),
      writeFile(narrationPath, compiled.narration),
    ]);

    if (command === "compile-essay") {
      console.log(JSON.stringify({
        valid: true,
        pack: packPath,
        storyboard: storyboardPath,
        narration: narrationPath,
        shots: compiled.storyboard.shotCount,
        duration: compiled.storyboard.runtimeSeconds,
      }, null, 2));
      return;
    }

    const videoPath = resolve(options.out ?? join(buildDirectory, `${compiled.pack.id}.mp4`));
    const renderOptions = {
      width: numericOption(options, "width"),
      height: numericOption(options, "height"),
      fps: numericOption(options, "fps"),
      crf: numericOption(options, "crf"),
      preset: options.preset,
    };
    Object.keys(renderOptions).forEach((key) => {
      if (renderOptions[key] === undefined) delete renderOptions[key];
    });
    console.log(`Rendering essay companion: ${compiled.pack.title}`);
    const result = await renderVideo(compiled.pack, videoPath, renderOptions);
    const contactPath = join(buildDirectory, `${compiled.pack.id}-contact-sheet.png`);
    await renderContactSheet(compiled.pack, contactPath, { columns: 4, cellWidth: 400 });
    const validation = validateVideo(compiled.pack, videoPath, renderOptions);
    const reportPath = join(buildDirectory, `${compiled.pack.id}-validation.json`);
    await writeFile(reportPath, JSON.stringify({
      program: basename(programPath),
      render: result,
      storyboard: {
        shots: compiled.storyboard.shotCount,
        runtimeSeconds: compiled.storyboard.runtimeSeconds,
        timingMethod: compiled.storyboard.timingMethod,
      },
      fonts: fontStatus(),
      validation,
    }, null, 2));
    if (!validation.valid) {
      throw new Error(`Rendered video failed validation:\n${validation.errors.join("\n")}`);
    }
    console.log(JSON.stringify({
      video: videoPath,
      contactSheet: contactPath,
      storyboard: storyboardPath,
      validation: true,
      frames: result.frames,
      duration: result.duration,
    }, null, 2));
    return;
  }

  const pack = await loadPack(packPath);
  const buildDirectory = resolve(options.out ? dirname(options.out) : join(ROOT, "build", pack.id));

  if (command === "render") {
    const output = resolve(options.out ?? join(buildDirectory, `${pack.id}.mp4`));
    const renderOptions = {
      width: numericOption(options, "width"),
      height: numericOption(options, "height"),
      fps: numericOption(options, "fps"),
      crf: numericOption(options, "crf"),
      preset: options.preset,
    };
    Object.keys(renderOptions).forEach((key) => {
      if (renderOptions[key] === undefined) delete renderOptions[key];
    });

    console.log(`Rendering ${pack.title}`);
    const result = await renderVideo(pack, output, renderOptions);
    const contactPath = join(dirname(output), `${pack.id}-contact-sheet.png`);
    await renderContactSheet(pack, contactPath);
    const validation = validateVideo(pack, output, renderOptions);
    const report = {
      pack: pack.id,
      title: pack.title,
      source: basename(packPath),
      render: result,
      fonts: fontStatus(),
      validation,
    };
    await writeFile(
      join(dirname(output), `${pack.id}-validation.json`),
      JSON.stringify(report, null, 2),
    );
    if (!validation.valid) {
      throw new Error(`Rendered video failed validation:\n${validation.errors.join("\n")}`);
    }
    console.log(JSON.stringify({
      video: output,
      contactSheet: contactPath,
      validation: true,
      frames: result.frames,
      duration: result.duration,
    }, null, 2));
    return;
  }

  if (command === "poster") {
    const sceneId = options.scene ?? pack.scenes[0].id;
    const output = resolve(options.out ?? join(buildDirectory, `${sceneId}.png`));
    await renderPoster(pack, sceneId, output, {
      width: numericOption(options, "width"),
      height: numericOption(options, "height"),
      time: numericOption(options, "time"),
    });
    console.log(output);
    return;
  }

  if (command === "contact") {
    const output = resolve(options.out ?? join(buildDirectory, `${pack.id}-contact-sheet.png`));
    await renderContactSheet(pack, output);
    console.log(output);
    return;
  }

  if (command === "validate") {
    if (!options.video) {
      console.log(JSON.stringify({
        valid: true,
        pack: pack.id,
        scenes: pack.scenes.length,
        message: "Scene pack schema and semantic checks passed.",
      }, null, 2));
      return;
    }
    const video = resolve(options.video);
    const validation = validateVideo(pack, video);
    console.log(JSON.stringify(validation, null, 2));
    if (!validation.valid) process.exitCode = 1;
    return;
  }

  throw new Error(`Unknown command "${command}"\n\n${usage()}`);
}

main().catch((error) => {
  console.error(error.stack ?? error.message);
  process.exitCode = 1;
});
