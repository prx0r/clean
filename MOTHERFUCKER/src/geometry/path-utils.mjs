import { Path2D } from "@napi-rs/canvas";
import { clamp, lerp } from "../../math.mjs";

export const point = (x, y) => ({ x: Number(x), y: Number(y) });
export const distance = (a, b) => Math.hypot(b.x - a.x, b.y - a.y);

export function centroid(points) {
  if (!points.length) return point(0, 0);
  const sum = points.reduce((acc, p) => ({ x: acc.x + p.x, y: acc.y + p.y }), { x: 0, y: 0 });
  return point(sum.x / points.length, sum.y / points.length);
}

export function resamplePolyline(points, count = 96, closed = false) {
  if (!Array.isArray(points) || points.length < 2) return [...(points ?? [])];
  const source = closed ? [...points, points[0]] : [...points];
  const lengths = [0];
  for (let i = 1; i < source.length; i += 1) lengths.push(lengths.at(-1) + distance(source[i - 1], source[i]));
  const total = lengths.at(-1);
  if (total <= 1e-9) return Array.from({ length: count }, () => ({ ...source[0] }));
  return Array.from({ length: count }, (_, index) => {
    const target = (index / Math.max(1, count - (closed ? 0 : 1))) * total;
    let segment = 1;
    while (segment < lengths.length - 1 && lengths[segment] < target) segment += 1;
    const a = source[segment - 1];
    const b = source[segment];
    const start = lengths[segment - 1];
    const span = Math.max(1e-9, lengths[segment] - start);
    const u = clamp((target - start) / span);
    return point(lerp(a.x, b.x, u), lerp(a.y, b.y, u));
  });
}

export function pathFromPoints(points, { closed = false } = {}) {
  const path = new Path2D();
  if (!points.length) return path;
  path.moveTo(points[0].x, points[0].y);
  for (const p of points.slice(1)) path.lineTo(p.x, p.y);
  if (closed) path.closePath();
  return path;
}

export function transformPoints(points, {
  tx = 0, ty = 0, sx = 1, sy = sx, rotation = 0,
  skewX = 0, skewY = 0, reflectX = false, reflectY = false,
} = {}) {
  const c = Math.cos(rotation);
  const s = Math.sin(rotation);
  return points.map((p) => {
    let x = p.x * sx * (reflectX ? -1 : 1);
    let y = p.y * sy * (reflectY ? -1 : 1);
    x += y * Math.tan(skewX);
    y += x * Math.tan(skewY);
    return point(tx + x * c - y * s, ty + x * s + y * c);
  });
}

export function morphPointSets(left, right, amount, count = 128, closed = true) {
  const a = resamplePolyline(left, count, closed);
  const b = resamplePolyline(right, count, closed);
  return a.map((p, i) => point(lerp(p.x, b[i].x, clamp(amount)), lerp(p.y, b[i].y, clamp(amount))));
}

export function signedArea(points) {
  if (points.length < 3) return 0;
  return points.reduce((sum, p, i) => {
    const q = points[(i + 1) % points.length];
    return sum + p.x * q.y - q.x * p.y;
  }, 0) / 2;
}

export function normalAt(points, index) {
  const prev = points[(index - 1 + points.length) % points.length];
  const next = points[(index + 1) % points.length];
  const dx = next.x - prev.x;
  const dy = next.y - prev.y;
  const length = Math.hypot(dx, dy) || 1;
  return point(-dy / length, dx / length);
}

export function offsetPolyline(points, amount) {
  return points.map((p, i) => {
    const n = normalAt(points, i);
    return point(p.x + n.x * amount, p.y + n.y * amount);
  });
}
