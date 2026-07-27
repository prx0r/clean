import { Path2D } from "@napi-rs/canvas";
import { TAU } from "../../math.mjs";
import { bhupuraPath, polygonPath } from "./yantra-generators.mjs";
import { lotusPath } from "./lotus-generators.mjs";

export function ringPath(cx, cy, radius) {
  const path = new Path2D();
  path.arc(cx, cy, radius, 0, TAU);
  return path;
}

export function spokePath({ cx = 0, cy = 0, innerRadius = 40, outerRadius = 160, spokes = 8, phase = -Math.PI / 2 } = {}) {
  const path = new Path2D();
  for (let i = 0; i < spokes; i += 1) {
    const angle = phase + i * TAU / spokes;
    path.moveTo(cx + Math.cos(angle) * innerRadius, cy + Math.sin(angle) * innerRadius);
    path.lineTo(cx + Math.cos(angle) * outerRadius, cy + Math.sin(angle) * outerRadius);
  }
  return path;
}

export function mandalaLayers({ cx = 0, cy = 0, size = 360, petals = 8, spokes = 8 } = {}) {
  return Object.freeze({
    enclosure: bhupuraPath({ cx, cy, size }),
    outerRing: ringPath(cx, cy, size * 0.42),
    lotus: lotusPath({ cx, cy, petals, radius: size * 0.25, petalLength: size * 0.18, petalWidth: size * 0.065 }),
    spokes: spokePath({ cx, cy, innerRadius: size * 0.08, outerRadius: size * 0.36, spokes }),
    core: polygonPath({ cx, cy, radius: size * 0.13, sides: 3 }),
    bindu: ringPath(cx, cy, size * 0.018),
  });
}
