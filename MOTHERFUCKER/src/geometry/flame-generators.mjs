import { TAU } from "../../math.mjs";
import { pathFromPoints, point, transformPoints } from "./path-utils.mjs";

export function flameTonguePoints({ height = 90, width = 34, curl = 0.28, samples = 52 } = {}) {
  const left = [], right = [];
  for (let i = 0; i <= samples; i += 1) {
    const u = i / samples;
    const envelope = Math.sin(Math.PI * u) ** 0.85;
    const center = Math.sin(u * Math.PI * 1.3) * curl * width;
    left.push(point(center - envelope * width * (1 - 0.35 * u), -u * height));
    right.push(point(center + envelope * width * (1 - 0.35 * u), -u * height));
  }
  return [...left, ...right.reverse()];
}

export function flameAureole({
  cx = 0, cy = 0, radius = 150, tongues = 18,
  flameHeight = 58, flameWidth = 18, phase = -Math.PI / 2,
} = {}) {
  const base = flameTonguePoints({ height: flameHeight, width: flameWidth });
  return Array.from({ length: tongues }, (_, index) => {
    const angle = phase + index * TAU / tongues;
    return transformPoints(base, {
      tx: cx + Math.cos(angle) * radius,
      ty: cy + Math.sin(angle) * radius,
      rotation: angle + Math.PI / 2,
    });
  });
}

export const flameAureolePaths = (options = {}) =>
  flameAureole(options).map((points) => pathFromPoints(points, { closed: true }));
