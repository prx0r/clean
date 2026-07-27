#!/usr/bin/env node
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

async function patch(path, transform) {
  const source = await readFile(path, "utf8");
  const updated = transform(source);
  if (updated !== source) await writeFile(path, updated);
  console.log(updated !== source ? `patched ${path}` : `unchanged ${path}`);
}

const root = resolve(process.cwd());

await patch(resolve(root, "motifs.mjs"), (source) => {
  if (!source.includes("renderArgumentDiagramV2")) {
    source = source.replace(
      'import { renderArgumentDiagram } from "./src/argument-diagram.mjs";',
      'import { renderArgumentDiagram } from "./src/argument-diagram.mjs";\nimport { renderArgumentDiagramV2 } from "./src/argument-diagram-v2.mjs";',
    );
  }
  if (!source.includes('"argument-diagram-v2": renderArgumentDiagramV2')) {
    source = source.replace(
      '"argument-diagram": renderArgumentDiagram,',
      '"argument-diagram": renderArgumentDiagram,\n  "argument-diagram-v2": renderArgumentDiagramV2,',
    );
  }
  return source;
});

await patch(resolve(root, "renderer.mjs"), (source) => {
  source = source.replace(
    'scene.motif === "argument-diagram" || scene.motif === "logical-argument"',
    'scene.motif === "argument-diagram" || scene.motif === "argument-diagram-v2" || scene.motif === "logical-argument"',
  );
  source = source.replace(
`      width: this.width,
      height: this.height,
      audio: this.audio ? sampleAudioFeatures(this.audio, seconds) : null,`,
`      width: this.width,
      height: this.height,
      fps: this.fps,
      frame: this.frame ?? 0,
      seconds,
      sceneProgress: t,
      sceneSeconds: t * (scene.duration ?? this.pack.render.sceneDuration),
      audio: this.audio ? sampleAudioFeatures(this.audio, seconds) : null,`,
  );
  return source;
});

await patch(resolve(root, "fonts.mjs"), (source) => {
  if (source.includes('"Source Serif 4"')) return source;
  const anchor = `  registerFont(
    join(FRAMEWORK_ROOT, "assets/fonts/noto-serif-devanagari/NotoSerifDevanagari-Variable.ttf"),
    typography.devanagari.family,
  );`;
  const addition = `${anchor}

  for (const candidate of [
    "assets/fonts/source-serif-4/SourceSerif4-Variable.ttf",
    "assets/fonts/source-serif-4/SourceSerif4-Regular.ttf",
  ]) {
    try {
      registerFont(join(FRAMEWORK_ROOT, candidate), "Source Serif 4");
      break;
    } catch {}
  }`;
  return source.includes(anchor) ? source.replace(anchor, addition) : source;
});

console.log("Logicvid framework patch complete.");
