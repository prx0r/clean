import { TAU } from "../../math.mjs";

function particle({ x, y, rng, options = {} }) {
  return {
    x, y, vx:options.vx ?? 0, vy:options.vy ?? 0, age:0,
    life:options.life ?? 2 + rng() * 2,
    size:options.size ?? 2 + rng() * 3,
    alpha:options.alpha ?? 0.8, color:options.color,
    trail:options.trail ? [] : null,
    trailLength:options.trailLength ?? 18,
    phase:rng() * TAU,
  };
}

export function pointEmitter({ x, y, rate = 20, spread = 0, options = {} }) {
  return { rate, create({ rng }) {
    const angle = rng() * TAU, radius = Math.sqrt(rng()) * spread;
    return particle({ x:x+Math.cos(angle)*radius, y:y+Math.sin(angle)*radius, rng, options });
  }};
}

export function ringEmitter({ cx, cy, radius, rate = 24, options = {} }) {
  return { rate, create({ rng }) {
    const angle = rng() * TAU;
    return particle({
      x:cx+Math.cos(angle)*radius, y:cy+Math.sin(angle)*radius, rng,
      options:{ ...options, vx:options.vx ?? Math.cos(angle)*(options.speed ?? 4), vy:options.vy ?? Math.sin(angle)*(options.speed ?? 4) },
    });
  }};
}

export function pathEmitter({ points, rate = 30, jitter = 0, options = {} }) {
  return { rate, create({ rng }) {
    const index = Math.min(points.length - 2, Math.floor(rng() * (points.length - 1)));
    const a = points[index], b = points[index + 1], u = rng();
    return particle({
      x:a.x+(b.x-a.x)*u+(rng()-0.5)*jitter,
      y:a.y+(b.y-a.y)*u+(rng()-0.5)*jitter,
      rng, options,
    });
  }};
}
