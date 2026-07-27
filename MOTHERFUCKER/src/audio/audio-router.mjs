import { clamp, lerp } from "../../math.mjs";
import { EnvelopeFollower } from "./audio-features.mjs";

const CURVES = Object.freeze({
  linear: (x) => x,
  square: (x) => x * x,
  sqrt: (x) => Math.sqrt(Math.max(0, x)),
  "ease-out": (x) => 1 - (1 - x) ** 3,
  threshold: (x) => x >= 0.5 ? 1 : 0,
});

export class AudioRouter {
  constructor(routes = []) {
    this.routes = routes.map((route) => ({ ...route, follower: new EnvelopeFollower(route) }));
  }
  update(features, dt) {
    const output = {};
    for (const route of this.routes) {
      const raw = Array.isArray(features[route.source])
        ? features[route.source][route.index ?? 0] ?? 0
        : features[route.source] ?? 0;
      const shaped = (CURVES[route.curve ?? "linear"] ?? CURVES.linear)(clamp(raw));
      const value = route.follower.update(shaped, dt);
      output[route.target] = lerp(route.minimum ?? 0, route.maximum ?? 1, value);
    }
    return output;
  }
}
