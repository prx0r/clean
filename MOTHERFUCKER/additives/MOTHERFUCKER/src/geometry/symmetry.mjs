import { TAU } from "../../math.mjs";
import { transformPoints } from "./path-utils.mjs";

export function radialCopies(points, count, {
  cx = 0, cy = 0, phase = 0, alternateReflection = false, scale = 1,
} = {}) {
  return Array.from({ length: count }, (_, index) => transformPoints(points, {
    tx: cx, ty: cy, sx: scale,
    rotation: phase + index * TAU / count,
    reflectX: alternateReflection && index % 2 === 1,
  }));
}

export const dihedralCopies = (points, count, options = {}) =>
  radialCopies(points, count, { ...options, alternateReflection: true });
