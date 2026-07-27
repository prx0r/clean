export const TAU = Math.PI * 2;

export function clamp(value, min = 0, max = 1) {
  return Math.max(min, Math.min(max, value));
}

export function lerp(a, b, t) {
  return a + (b - a) * clamp(t);
}

export function invLerp(a, b, value) {
  if (a === b) return value >= b ? 1 : 0;
  return clamp((value - a) / (b - a));
}

export function smoothstep(a, b, value) {
  const t = invLerp(a, b, value);
  return t * t * (3 - 2 * t);
}

export function smootherstep(a, b, value) {
  const t = invLerp(a, b, value);
  return t * t * t * (t * (t * 6 - 15) + 10);
}

export function easeOutCubic(t) {
  t = clamp(t);
  return 1 - (1 - t) ** 3;
}

export function easeInOutCubic(t) {
  t = clamp(t);
  return t < 0.5 ? 4 * t ** 3 : 1 - ((-2 * t + 2) ** 3) / 2;
}

export function bell(t, edge = 0.1) {
  return smoothstep(0, edge, t) * (1 - smoothstep(1 - edge, 1, t));
}

export function wave(t, cycles = 1, phase = 0) {
  return Math.sin((t * cycles + phase) * TAU);
}

export function pulse(t, cycles = 1, phase = 0) {
  return 0.5 + 0.5 * wave(t, cycles, phase);
}

export function stagger(index, count, t, spread = 0.42) {
  const denominator = Math.max(1, count - 1);
  const start = (index / denominator) * spread;
  return smoothstep(start, Math.min(1, start + 0.28), t);
}

export function hashString(value) {
  let hash = 2166136261;
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

export function seededRandom(seed) {
  let state = seed >>> 0;
  return () => {
    state += 0x6d2b79f5;
    let result = state;
    result = Math.imul(result ^ (result >>> 15), result | 1);
    result ^= result + Math.imul(result ^ (result >>> 7), result | 61);
    return ((result ^ (result >>> 14)) >>> 0) / 4294967296;
  };
}

export function colorToRgb(color) {
  const value = color.replace("#", "");
  const hex = value.length === 3
    ? value.split("").map((character) => character.repeat(2)).join("")
    : value;
  return [
    Number.parseInt(hex.slice(0, 2), 16),
    Number.parseInt(hex.slice(2, 4), 16),
    Number.parseInt(hex.slice(4, 6), 16),
  ];
}

export function rgba(color, alpha = 1) {
  const [r, g, b] = colorToRgb(color);
  return `rgba(${r}, ${g}, ${b}, ${clamp(alpha)})`;
}

export function mixColor(a, b, t) {
  const left = colorToRgb(a);
  const right = colorToRgb(b);
  const mixed = left.map((channel, index) => Math.round(lerp(channel, right[index], t)));
  return `#${mixed.map((channel) => channel.toString(16).padStart(2, "0")).join("")}`;
}

export function cubicPoint(p0, p1, p2, p3, t) {
  const u = 1 - t;
  return {
    x: u ** 3 * p0.x + 3 * u ** 2 * t * p1.x + 3 * u * t ** 2 * p2.x + t ** 3 * p3.x,
    y: u ** 3 * p0.y + 3 * u ** 2 * t * p1.y + 3 * u * t ** 2 * p2.y + t ** 3 * p3.y,
  };
}

export function sampleCubic(p0, p1, p2, p3, count = 120) {
  return Array.from({ length: count }, (_, index) => (
    cubicPoint(p0, p1, p2, p3, index / Math.max(1, count - 1))
  ));
}

export function partialPoints(points, amount) {
  const value = clamp(amount);
  if (value <= 0 || points.length === 0) return [];
  if (value >= 1) return points;
  const position = value * (points.length - 1);
  const index = Math.floor(position);
  const fraction = position - index;
  const result = points.slice(0, index + 1);
  const a = points[index];
  const b = points[Math.min(index + 1, points.length - 1)];
  result.push({ x: lerp(a.x, b.x, fraction), y: lerp(a.y, b.y, fraction) });
  return result;
}

export function polar(cx, cy, radius, angle) {
  return {
    x: cx + Math.cos(angle) * radius,
    y: cy + Math.sin(angle) * radius,
  };
}

export function regularPolygon(cx, cy, radius, sides, rotation = -Math.PI / 2) {
  return Array.from({ length: sides }, (_, index) => (
    polar(cx, cy, radius, rotation + (index / sides) * TAU)
  ));
}
