import { Path2D } from "@napi-rs/canvas";
import { TAU } from "../../math.mjs";
import { point, pathFromPoints, transformPoints } from "./path-utils.mjs";

export function petalPoints({ length = 90, width = 36, tipSharpness = 0.72, samples = 48 } = {}) {
  const half = Math.floor(samples / 2);
  const upper = Array.from({ length: half + 1 }, (_, index) => {
    const u = index / half;
    const x = (u - 0.5) * width * 2;
    const envelope = Math.sin(Math.PI * u) ** tipSharpness;
    return point(x, -length * envelope);
  });
  const lower = upper.slice(1, -1).reverse().map((p) => point(p.x, -p.y * 0.18));
  return [...upper, ...lower];
}

export function lotusRing({
  cx = 0, cy = 0, petals = 8, radius = 80,
  petalLength = 80, petalWidth = 28, phase = -Math.PI / 2,
  alternateScale = 0,
} = {}) {
  const base = petalPoints({ length: petalLength, width: petalWidth });
  return Array.from({ length: petals }, (_, index) => {
    const angle = phase + index * TAU / petals;
    const scale = 1 + alternateScale * (index % 2 ? -1 : 1);
    return transformPoints(base, {
      tx: cx + Math.cos(angle) * radius,
      ty: cy + Math.sin(angle) * radius,
      sx: scale,
      rotation: angle + Math.PI / 2,
    });
  });
}

export function lotusPath(options = {}) {
  const path = new Path2D();
  for (const points of lotusRing(options)) path.addPath(pathFromPoints(points, { closed: true }));
  return path;
}

export function nestedLotus({ cx = 0, cy = 0, rings = [] } = {}) {
  const path = new Path2D();
  const resolved = rings.length ? rings : [
    { petals: 8, radius: 58, petalLength: 58, petalWidth: 22 },
    { petals: 16, radius: 105, petalLength: 74, petalWidth: 18 },
  ];
  for (const ring of resolved) path.addPath(lotusPath({ cx, cy, ...ring }));
  return path;
}
