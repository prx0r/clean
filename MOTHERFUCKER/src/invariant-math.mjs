import { clamp, lerp } from "../math.mjs";

export function expAlpha(dt, tau) {
  const safeTau = Math.max(1e-6, tau);
  return -Math.expm1(-Math.max(0, dt) / safeTau);
}

export function expApproach(current, target, dt, tau) {
  return current + expAlpha(dt, tau) * (target - current);
}

export function vectorExpApproach(current, target, dt, tau) {
  const alpha = expAlpha(dt, tau);
  return current.map((value, index) => value + alpha * ((target[index] ?? 0) - value));
}

export function centroid(points) {
  if (!points.length) return { x: 0, y: 0 };
  const total = points.reduce((sum, point) => ({
    x: sum.x + point.x,
    y: sum.y + point.y,
  }), { x: 0, y: 0 });
  return { x: total.x / points.length, y: total.y / points.length };
}

export function rmsRadius(points, center = centroid(points)) {
  if (!points.length) return 1;
  const meanSquare = points.reduce((sum, point) => (
    sum + (point.x - center.x) ** 2 + (point.y - center.y) ** 2
  ), 0) / points.length;
  return Math.sqrt(meanSquare) || 1;
}

export function normalizePointCloud(points) {
  const center = centroid(points);
  const radius = rmsRadius(points, center);
  return points.map((point) => ({
    x: (point.x - center.x) / radius,
    y: (point.y - center.y) / radius,
  }));
}

export function transformPoints(points, options = {}) {
  const {
    tx = 0,
    ty = 0,
    scale = 1,
    rotation = 0,
    reflectX = false,
    reflectY = false,
  } = options;
  const cosine = Math.cos(rotation);
  const sine = Math.sin(rotation);
  return points.map((point) => {
    const x0 = point.x * (reflectX ? -1 : 1) * scale;
    const y0 = point.y * (reflectY ? -1 : 1) * scale;
    return {
      x: tx + x0 * cosine - y0 * sine,
      y: ty + x0 * sine + y0 * cosine,
    };
  });
}

export function morphPoints(left, right, amount) {
  const count = Math.min(left.length, right.length);
  return Array.from({ length: count }, (_, index) => ({
    x: lerp(left[index].x, right[index].x, amount),
    y: lerp(left[index].y, right[index].y, amount),
  }));
}

export function resampleClosed(points, count = 96) {
  if (points.length < 2) return [...points];
  const closed = [...points, points[0]];
  const segments = [];
  let total = 0;
  for (let index = 0; index < closed.length - 1; index += 1) {
    const a = closed[index];
    const b = closed[index + 1];
    const length = Math.hypot(b.x - a.x, b.y - a.y);
    segments.push({ a, b, length, start: total });
    total += length;
  }
  if (total <= 1e-9) return Array.from({ length: count }, () => ({ ...points[0] }));
  return Array.from({ length: count }, (_, index) => {
    const target = (index / count) * total;
    const segment = segments.find((candidate) => target <= candidate.start + candidate.length)
      ?? segments.at(-1);
    const local = clamp((target - segment.start) / Math.max(1e-9, segment.length));
    return {
      x: lerp(segment.a.x, segment.b.x, local),
      y: lerp(segment.a.y, segment.b.y, local),
    };
  });
}

export function pairwiseDistanceSignature(points, bins = 12) {
  const normalized = normalizePointCloud(points);
  const distances = [];
  for (let left = 0; left < normalized.length; left += 1) {
    for (let right = left + 1; right < normalized.length; right += 1) {
      distances.push(Math.hypot(
        normalized[left].x - normalized[right].x,
        normalized[left].y - normalized[right].y,
      ));
    }
  }
  distances.sort((a, b) => a - b);
  if (!distances.length) return Array.from({ length: bins }, () => 0);
  return Array.from({ length: bins }, (_, index) => {
    const position = (index / Math.max(1, bins - 1)) * (distances.length - 1);
    const low = Math.floor(position);
    const high = Math.min(distances.length - 1, low + 1);
    return lerp(distances[low], distances[high], position - low);
  });
}

export function signatureDistance(left, right) {
  const count = Math.min(left.length, right.length);
  if (!count) return 1;
  const error = Array.from({ length: count }, (_, index) => (
    (left[index] - right[index]) ** 2
  )).reduce((sum, value) => sum + value, 0) / count;
  return Math.sqrt(error);
}

export function normalizedSimilarity(left, right, tolerance = 0.35) {
  return clamp(1 - signatureDistance(left, right) / Math.max(1e-9, tolerance));
}

export function cyclicIntervals(values) {
  if (values.length < 2) return [];
  return values.map((value, index) => {
    const next = values[(index + 1) % values.length];
    return next - value;
  });
}

export function hermiteScalar(keys, t) {
  if (!Array.isArray(keys) || keys.length < 2) {
    const value = Number(keys?.[0]?.value ?? keys?.[0] ?? 0);
    return { value, velocity: 0, acceleration: 0 };
  }
  const sorted = keys.map((key, index) => (
    typeof key === "number" ? { time: index / (keys.length - 1), value: key } : key
  )).sort((a, b) => a.time - b.time);
  const valueT = clamp(t);
  let index = 0;
  while (index < sorted.length - 2 && valueT > sorted[index + 1].time) index += 1;
  const a = sorted[index];
  const b = sorted[index + 1];
  const span = Math.max(1e-6, b.time - a.time);
  const u = clamp((valueT - a.time) / span);
  const previous = sorted[Math.max(0, index - 1)];
  const next = sorted[Math.min(sorted.length - 1, index + 2)];
  const m0 = (b.value - previous.value) / Math.max(1e-6, b.time - previous.time);
  const m1 = (next.value - a.value) / Math.max(1e-6, next.time - a.time);
  const h00 = 2 * u ** 3 - 3 * u ** 2 + 1;
  const h10 = u ** 3 - 2 * u ** 2 + u;
  const h01 = -2 * u ** 3 + 3 * u ** 2;
  const h11 = u ** 3 - u ** 2;
  const value = h00 * a.value + h10 * span * m0 + h01 * b.value + h11 * span * m1;

  const dh00 = 6 * u ** 2 - 6 * u;
  const dh10 = 3 * u ** 2 - 4 * u + 1;
  const dh01 = -6 * u ** 2 + 6 * u;
  const dh11 = 3 * u ** 2 - 2 * u;
  const velocity = (dh00 * a.value + dh10 * span * m0 + dh01 * b.value + dh11 * span * m1) / span;

  const d2h00 = 12 * u - 6;
  const d2h10 = 6 * u - 4;
  const d2h01 = -12 * u + 6;
  const d2h11 = 6 * u - 2;
  const acceleration = (
    d2h00 * a.value + d2h10 * span * m0 + d2h01 * b.value + d2h11 * span * m1
  ) / (span ** 2);

  return { value, velocity, acceleration };
}

export function sampleTrajectory(keys, count = 120) {
  return Array.from({ length: count }, (_, index) => {
    const t = index / Math.max(1, count - 1);
    return { t, ...hermiteScalar(keys, t) };
  });
}

export function causalTraceSeries(values, tau = 0.5, count = 120, initial = 0) {
  const keys = values.map((value, index) => (
    typeof value === "number"
      ? { time: index / Math.max(1, values.length - 1), value }
      : value
  ));
  let trace = initial;
  let previousT = 0;
  return Array.from({ length: count }, (_, index) => {
    const t = index / Math.max(1, count - 1);
    const target = hermiteScalar(keys, t).value;
    trace = expApproach(trace, target, t - previousT, tau);
    previousT = t;
    return { t, target, trace, lag: target - trace };
  });
}

export function signedArea(points) {
  if (points.length < 3) return 0;
  return points.reduce((sum, point, index) => {
    const next = points[(index + 1) % points.length];
    return sum + point.x * next.y - next.x * point.y;
  }, 0) / 2;
}

export function parity(points) {
  const area = signedArea(points);
  return area === 0 ? 0 : Math.sign(area);
}

export function clampArray(values, minimum = 0, maximum = 1) {
  return values.map((value) => clamp(Number(value) || 0, minimum, maximum));
}
