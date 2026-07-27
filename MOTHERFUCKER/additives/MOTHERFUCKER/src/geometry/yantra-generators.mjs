import { Path2D } from "@napi-rs/canvas";
import { TAU } from "../../math.mjs";
import { pathFromPoints, point } from "./path-utils.mjs";
import { lotusPath } from "./lotus-generators.mjs";

export function regularPolygonPoints({ cx = 0, cy = 0, radius = 100, sides = 3, rotation = -Math.PI / 2 } = {}) {
  return Array.from({ length: sides }, (_, i) => point(
    cx + Math.cos(rotation + i * TAU / sides) * radius,
    cy + Math.sin(rotation + i * TAU / sides) * radius,
  ));
}
export const polygonPath = (options = {}) => pathFromPoints(regularPolygonPoints(options), { closed: true });

export function trianglePair({ cx = 0, cy = 0, radius = 120, separation = 0 } = {}) {
  return [
    polygonPath({ cx, cy: cy - separation, radius, sides: 3, rotation: -Math.PI / 2 }),
    polygonPath({ cx, cy: cy + separation, radius, sides: 3, rotation: Math.PI / 2 }),
  ];
}

export function bhupuraPath({ cx = 0, cy = 0, size = 340, wall = 24, gateWidth = 62, gateDepth = 32 } = {}) {
  const half = size / 2;
  const path = new Path2D();
  for (const rotation of [0, Math.PI / 2, Math.PI, Math.PI * 1.5]) {
    const raw = [
      point(-half, -half), point(-gateWidth / 2, -half),
      point(-gateWidth / 2, -half - gateDepth), point(gateWidth / 2, -half - gateDepth),
      point(gateWidth / 2, -half), point(half, -half),
      point(half, -half + wall), point(-half, -half + wall),
    ];
    const c = Math.cos(rotation), s = Math.sin(rotation);
    const rotated = raw.map((p) => point(cx + p.x * c - p.y * s, cy + p.x * s + p.y * c));
    path.addPath(pathFromPoints(rotated, { closed: true }));
  }
  return path;
}

export function chakraYantra({ cx = 0, cy = 0, petals = 8, radius = 180, triangleRadius = 92, binduRadius = 8 } = {}) {
  const path = new Path2D();
  path.addPath(lotusPath({ cx, cy, petals, radius: radius * 0.55, petalLength: radius * 0.42, petalWidth: radius * 0.16 }));
  for (const triangle of trianglePair({ cx, cy, radius: triangleRadius })) path.addPath(triangle);
  path.arc(cx, cy, binduRadius, 0, TAU);
  return path;
}

export function sriYantraApprox({ cx = 0, cy = 0, radius = 155 } = {}) {
  const path = new Path2D();
  [1.0, 0.82, 0.64, 0.48].forEach((scale, index) => path.addPath(polygonPath({
    cx, cy: cy + (index - 1.3) * radius * 0.055, radius: radius * scale, sides: 3, rotation: -Math.PI / 2,
  })));
  [0.94, 0.74, 0.58, 0.42, 0.3].forEach((scale, index) => path.addPath(polygonPath({
    cx, cy: cy + (index - 2) * radius * 0.05, radius: radius * scale, sides: 3, rotation: Math.PI / 2,
  })));
  return path;
}
