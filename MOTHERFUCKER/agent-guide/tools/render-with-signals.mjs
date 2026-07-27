#!/usr/bin/env node
// Integration scaffold. Adapt the import paths to the repository after copying.
import { resolve } from "node:path";
import { loadCapabilityScenePack } from "../MOTHERFUCKER/src/load-capability-scene-pack.mjs";
import { loadAudioFeatureManifest, sampleAudioFeatures } from "../MOTHERFUCKER/src/audio/audio-features.mjs";

const [packPath, audioPath, outputPath] = process.argv.slice(2);
if (!packPath || !audioPath || !outputPath) {
  throw new Error("Usage: render-with-signals.mjs PACK AUDIO_FEATURES OUTPUT");
}

const pack = await loadCapabilityScenePack(resolve(packPath));
const audioManifest = await loadAudioFeatureManifest(resolve(audioPath));

// Patch point:
// update FrameRenderer so each frame environment includes:
//
// env.audio = sampleAudioFeatures(audioManifest, seconds)
//
// Then call the framework's normal renderVideo(pack, outputPath).
console.log(JSON.stringify({
  pack: pack.id,
  audioDuration: audioManifest.duration,
  outputPath,
  requiredPatch: "Inject sampled audio into per-frame render environment."
}, null, 2));
