import { readFile } from "node:fs/promises";
import { clamp, lerp } from "../../math.mjs";

export async function loadAudioFeatureManifest(path) {
  const data = JSON.parse(await readFile(path, "utf8"));
  if (data.version !== "1.0" || !Array.isArray(data.frames)) throw new Error("Invalid audio feature manifest");
  return data;
}

function lowerBound(frames, seconds) {
  let low = 0, high = frames.length;
  while (low < high) {
    const middle = (low + high) >> 1;
    if (frames[middle].time < seconds) low = middle + 1;
    else high = middle;
  }
  return Math.min(frames.length - 1, low);
}

export function sampleAudioFeatures(manifest, seconds) {
  const frames = manifest.frames;
  if (!frames.length) return {};
  const rightIndex = lowerBound(frames, seconds);
  const leftIndex = Math.max(0, rightIndex - 1);
  const left = frames[leftIndex], right = frames[rightIndex];
  const amount = clamp((seconds - left.time) / Math.max(1e-9, right.time - left.time));
  const result = { time: seconds };
  for (const key of Object.keys(left)) {
    if (key === "time") continue;
    const a = left[key], b = right[key] ?? a;
    result[key] = Array.isArray(a)
      ? a.map((value, index) => lerp(value, b[index] ?? value, amount))
      : lerp(a, b, amount);
  }
  return result;
}

export class EnvelopeFollower {
  constructor({ attack = 0.03, release = 0.28, initial = 0 } = {}) {
    this.attack = attack;
    this.release = release;
    this.value = initial;
  }
  update(target, dt) {
    const tau = target > this.value ? this.attack : this.release;
    const alpha = -Math.expm1(-Math.max(0, dt) / Math.max(1e-6, tau));
    this.value += alpha * (target - this.value);
    return this.value;
  }
}
