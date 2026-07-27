import { TAU, polar } from "../math.mjs";
import { resampleClosed, transformPoints } from "./invariant-math.mjs";

export function lobedContour(options = {}) {
  const {
    cx = 0,
    cy = 0,
    radius = 64,
    lobes = 5,
    harmonic = 0.22,
    secondary = 0.06,
    rotation = -Math.PI / 2,
    samples = 160,
  } = options;
  return Array.from({ length: samples }, (_, index) => {
    const angle = rotation + (index / samples) * TAU;
    const modulation = 1
      + harmonic * Math.cos(lobes * angle)
      + secondary * Math.cos((lobes * 2 - 1) * angle + 0.7);
    return polar(cx, cy, radius * modulation, angle);
  });
}

export function relationalNecklace(values, options = {}) {
  const {
    cx = 0,
    cy = 0,
    radius = 70,
    radialScale = 25,
    rotation = -Math.PI / 2,
  } = options;
  const safe = values?.length ? values : [0.2, 0.7, 0.4, 0.9, 0.5];
  const maximum = Math.max(...safe.map((value) => Math.abs(value)), 1e-9);
  return safe.map((value, index) => {
    const angle = rotation + (index / safe.length) * TAU;
    return polar(cx, cy, radius + radialScale * (value / maximum), angle);
  });
}

export function carrierGeometry(kind, options = {}) {
  const { cx = 0, cy = 0, size = 90, phase = 0 } = options;
  switch (kind) {
    case "lattice":
      return Array.from({ length: 12 }, (_, index) => {
        const angle = (index / 12) * TAU + phase;
        const ring = index % 2 ? size * 0.68 : size;
        return polar(cx, cy, ring, angle);
      });
    case "ribbon":
      return Array.from({ length: 80 }, (_, index) => {
        const p = index / 79;
        return {
          x: cx - size + p * size * 2,
          y: cy + Math.sin(p * TAU * 2 + phase) * size * 0.38,
        };
      });
    case "wave":
      return Array.from({ length: 96 }, (_, index) => {
        const p = index / 95;
        return {
          x: cx - size + p * size * 2,
          y: cy + Math.sin(p * TAU * 3 + phase) * size * 0.26
            + Math.sin(p * TAU + phase * 0.4) * size * 0.12,
        };
      });
    case "branch": {
      const points = [{ x: cx, y: cy + size }];
      for (let level = 1; level <= 5; level += 1) {
        const y = cy + size - level * size * 0.36;
        const spread = level * size * 0.16;
        points.push({ x: cx - spread, y }, { x: cx + spread, y });
      }
      return points;
    }
    case "vessel":
    default:
      return lobedContour({
        cx, cy, radius: size, lobes: 3, harmonic: 0.08, secondary: 0.02,
        rotation: phase, samples: 120,
      }).map((point, index) => ({
        x: point.x * 1 + (index > 60 ? 0 : 0),
        y: cy + (point.y - cy) * 1.22,
      }));
  }
}

export function topologyThread(options = {}) {
  const {
    cx = 0,
    cy = 0,
    radius = 120,
    nodes = 8,
    branching = 0.35,
    phase = 0,
  } = options;
  const main = Array.from({ length: nodes }, (_, index) => {
    const p = index / Math.max(1, nodes - 1);
    return {
      x: cx - radius + p * radius * 2,
      y: cy + Math.sin(p * TAU * 1.5 + phase) * radius * 0.34,
      id: `m${index}`,
    };
  });
  const edges = main.slice(0, -1).map((node, index) => [node.id, main[index + 1].id]);
  const branches = [];
  for (let index = 1; index < main.length - 1; index += 2) {
    const source = main[index];
    const direction = index % 4 === 1 ? -1 : 1;
    const target = {
      x: source.x + direction * radius * (0.22 + branching * 0.25),
      y: source.y - radius * (0.2 + branching * 0.35),
      id: `b${index}`,
    };
    branches.push(target);
    edges.push([source.id, target.id]);
  }
  return { nodes: [...main, ...branches], edges };
}

export function transformedSeed(options = {}) {
  const base = lobedContour({
    radius: options.radius ?? 64,
    lobes: options.lobes ?? 5,
    harmonic: options.harmonic ?? 0.22,
    samples: options.samples ?? 160,
  });
  return transformPoints(base, {
    tx: options.cx ?? 0,
    ty: options.cy ?? 0,
    scale: options.scale ?? 1,
    rotation: options.rotation ?? 0,
    reflectX: options.reflectX ?? false,
    reflectY: options.reflectY ?? false,
  });
}

export function alignedMorph(left, right, count = 160) {
  return {
    left: resampleClosed(left, count),
    right: resampleClosed(right, count),
  };
}
