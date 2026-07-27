import {
  TAU,
  clamp,
  polar,
  regularPolygon,
  sampleCubic,
  smoothstep,
  wave,
} from "./math.mjs";
import {
  drawEllipseRing,
  drawGlowOrb,
  drawLabel,
  drawLotus,
  drawNode,
  drawOrbitingNodes,
  drawPartialPath,
  drawRadialWords,
  drawRing,
  drawSilhouette,
  pointAlong,
} from "./primitives.mjs";
import { palette, typography } from "./theme.mjs";

export const layerTypes = Object.freeze([
  "orb",
  "ring",
  "ellipse",
  "lotus",
  "label",
  "silhouette",
  "polygon",
  "path",
  "bezier",
  "orbit-nodes",
  "radial-words",
  "grid",
]);

function colorValue(value, theme, fallback) {
  if (!value) return fallback;
  if (value.startsWith("#")) return value;
  return theme[value] ?? palette[value] ?? fallback;
}

function layerState(layer, t) {
  const appear = layer.appear ?? [0.02, 0.24];
  const disappear = layer.disappear;
  let alpha = smoothstep(appear[0], appear[1], t);
  if (disappear) alpha *= 1 - smoothstep(disappear[0], disappear[1], t);
  const motion = layer.motion ?? {};
  const cycles = motion.cycles ?? 1;
  const phase = motion.phase ?? 0;
  const amount = wave(t, cycles, phase);
  const x = (layer.x ?? 640) + (motion.x ?? 0) * amount;
  const y = (layer.y ?? 300) + (motion.y ?? 0) * amount;
  const scale = 1 + (motion.scale ?? 0) * amount;
  const rotation = (layer.rotation ?? 0) + (motion.rotation ?? 0) * t * TAU;
  return { alpha: alpha * (layer.alpha ?? 1), x, y, scale, rotation, amount };
}

function drawGrid(ctx, layer, state, theme, t) {
  const columns = Math.max(2, Math.min(24, layer.columns ?? 9));
  const rows = Math.max(2, Math.min(18, layer.rows ?? 7));
  const spacingX = layer.spacingX ?? 54;
  const spacingY = layer.spacingY ?? 42;
  const color = colorValue(layer.color, theme, theme.secondary);
  const warp = layer.warp ?? 8;
  const originX = state.x - ((columns - 1) * spacingX) / 2;
  const originY = state.y - ((rows - 1) * spacingY) / 2;
  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      const phase = row * 0.17 + column * 0.11;
      const x = originX + column * spacingX + Math.sin(t * TAU + phase * TAU) * warp;
      const y = originY + row * spacingY + Math.cos(t * TAU * 0.7 + phase * TAU) * warp * 0.45;
      drawNode(ctx, x, y, layer.radius ?? 2.3, {
        fill: theme.backgroundLight,
        stroke: color,
        alpha: state.alpha * (0.45 + 0.25 * Math.sin(phase * TAU + t * TAU)),
        width: layer.width ?? 0.8,
      });
    }
  }
}

function drawBezierLayer(ctx, layer, state, theme, t) {
  const points = sampleCubic(
    layer.p0 ?? { x: 180, y: 330 },
    layer.p1 ?? { x: 390, y: 120 },
    layer.p2 ?? { x: 850, y: 480 },
    layer.p3 ?? { x: 1100, y: 290 },
    180,
  ).map((point) => ({
    x: state.x === 640 ? point.x : point.x + state.x - 640,
    y: state.y === 300 ? point.y : point.y + state.y - 300,
  }));
  const color = colorValue(layer.color, theme, theme.secondary);
  drawPartialPath(
    ctx,
    points,
    smoothstep(layer.drawStart ?? 0.02, layer.drawEnd ?? 0.58, t),
    color,
    layer.width ?? 2,
    state.alpha,
    { blur: layer.blur ?? 6 },
  );
  const particles = Math.max(0, Math.min(32, layer.particles ?? 0));
  for (let index = 0; index < particles; index += 1) {
    const amount = (t * (layer.speed ?? 0.55) + index / particles) % 1;
    const point = pointAlong(points, amount);
    drawGlowOrb(
      ctx,
      point.x,
      point.y,
      layer.particleRadius ?? 4,
      color,
      state.alpha * 0.5 * Math.sin(amount * Math.PI),
    );
  }
}

function drawLayer(ctx, layer, t, theme) {
  const state = layerState(layer, t);
  const color = colorValue(layer.color, theme, theme.secondary);
  const luminous = colorValue(layer.luminous, theme, theme.luminous);
  ctx.save();

  switch (layer.type) {
    case "orb":
      drawGlowOrb(
        ctx,
        state.x,
        state.y,
        (layer.radius ?? 36) * state.scale,
        color,
        state.alpha,
        layer.core ?? true,
      );
      break;
    case "ring":
      drawRing(ctx, state.x, state.y, (layer.radius ?? 100) * state.scale, color, state.alpha, layer.width ?? 1.5);
      break;
    case "ellipse":
      drawEllipseRing(
        ctx,
        state.x,
        state.y,
        (layer.rx ?? 100) * state.scale,
        (layer.ry ?? 60) * state.scale,
        color,
        state.alpha,
        layer.width ?? 1.5,
        state.rotation,
      );
      break;
    case "lotus":
      drawLotus(ctx, state.x, state.y, (layer.radius ?? 80) * state.scale, {
        petals: layer.petals ?? 8,
        rotation: state.rotation,
        stroke: color,
        fill: layer.fill ?? "rgba(191,110,132,0.06)",
        alpha: state.alpha,
        lineWidth: layer.width ?? 1.2,
      });
      break;
    case "label":
      drawLabel(ctx, layer.text ?? "", state.x, state.y, {
        devanagari: layer.script === "devanagari",
        style: layer.style === "small" ? typography.small : typography.label,
        size: layer.size,
        color,
        alpha: state.alpha,
      });
      break;
    case "silhouette":
      drawSilhouette(ctx, state.x, state.y, (layer.scale ?? 1) * state.scale, color, state.alpha);
      break;
    case "polygon": {
      const points = regularPolygon(
        state.x,
        state.y,
        (layer.radius ?? 100) * state.scale,
        Math.max(3, Math.min(16, layer.sides ?? 3)),
        state.rotation - Math.PI / 2,
      );
      drawPartialPath(
        ctx,
        [...points, points[0]],
        smoothstep(layer.drawStart ?? 0.04, layer.drawEnd ?? 0.62, t),
        color,
        layer.width ?? 1.6,
        state.alpha,
        { blur: layer.blur ?? 5 },
      );
      break;
    }
    case "path": {
      const points = (layer.points ?? []).map((point) => ({
        x: point.x + (state.x - (layer.x ?? 640)),
        y: point.y + (state.y - (layer.y ?? 300)),
      }));
      drawPartialPath(
        ctx,
        points,
        smoothstep(layer.drawStart ?? 0.02, layer.drawEnd ?? 0.62, t),
        color,
        layer.width ?? 2,
        state.alpha,
        { blur: layer.blur ?? 6 },
      );
      break;
    }
    case "bezier":
      drawBezierLayer(ctx, layer, state, theme, t);
      break;
    case "orbit-nodes":
      drawOrbitingNodes(
        ctx,
        state.x,
        state.y,
        Math.max(2, Math.min(48, layer.count ?? 12)),
        (layer.rx ?? layer.radius ?? 130) * state.scale,
        (layer.ry ?? layer.radius ?? 130) * state.scale,
        state.rotation + t * (layer.speed ?? 0.08) * TAU,
        {
          color,
          fill: colorValue(layer.fillColor, theme, theme.backgroundLight),
          radius: layer.nodeRadius ?? 4,
          alpha: state.alpha,
        },
      );
      break;
    case "radial-words":
      drawRadialWords(
        ctx,
        layer.words ?? [],
        state.x,
        state.y,
        (layer.radius ?? 220) * state.scale,
        state.rotation,
        {
          size: layer.size ?? 12,
          color,
          alpha: state.alpha,
        },
      );
      break;
    case "grid":
      drawGrid(ctx, layer, state, theme, t);
      break;
    default:
      throw new Error(`Unknown composition layer type "${layer.type}"`);
  }

  if (layer.anchorGlow) {
    drawGlowOrb(ctx, state.x, state.y, layer.anchorGlow, luminous, state.alpha * 0.5);
  }
  ctx.restore();
}

export function renderComposition(ctx, t, scene, env) {
  const layers = scene.layers ?? [];
  for (const layer of layers) drawLayer(ctx, layer, clamp(t), env.theme);
}
