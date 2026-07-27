import { createCanvas, Path2D } from "@napi-rs/canvas";

import { applyTextStyle, fitText } from "./fonts.mjs";
import {
  TAU,
  clamp,
  hashString,
  lerp,
  partialPoints,
  polar,
  rgba,
  seededRandom,
} from "./math.mjs";
import {
  LOGICAL_HEIGHT,
  LOGICAL_WIDTH,
  palette,
  typography,
} from "./theme.mjs";

const backgroundCache = new Map();

export function logicalScale(width, height) {
  return {
    x: width / LOGICAL_WIDTH,
    y: height / LOGICAL_HEIGHT,
  };
}

export function setLogicalTransform(ctx, width, height) {
  const scale = logicalScale(width, height);
  ctx.setTransform(scale.x, 0, 0, scale.y, 0, 0);
}

export function createStableBackground(width, height, theme, seed = 1) {
  const key = `${width}:${height}:${theme.name}:${seed}`;
  if (backgroundCache.has(key)) return backgroundCache.get(key);

  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext("2d");
  setLogicalTransform(ctx, width, height);

  const field = ctx.createRadialGradient(640, 250, 30, 640, 360, 780);
  field.addColorStop(0, theme.backgroundLight);
  field.addColorStop(0.58, theme.background);
  field.addColorStop(1, theme.backgroundEdge);
  ctx.fillStyle = field;
  ctx.fillRect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT);

  const rng = seededRandom(seed ^ hashString(theme.name));
  ctx.save();
  ctx.globalAlpha = theme.textureOpacity;
  for (let index = 0; index < 2200; index += 1) {
    const x = rng() * LOGICAL_WIDTH;
    const y = rng() * LOGICAL_HEIGHT;
    const radius = 0.18 + rng() * 0.82;
    ctx.fillStyle = rng() > 0.46 ? theme.structure : theme.backgroundLight;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, TAU);
    ctx.fill();
  }
  ctx.lineWidth = 0.45;
  for (let index = 0; index < 160; index += 1) {
    const x = rng() * LOGICAL_WIDTH;
    const y = rng() * LOGICAL_HEIGHT;
    const length = 6 + rng() * 28;
    const angle = (rng() - 0.5) * 0.2;
    ctx.strokeStyle = rng() > 0.5 ? theme.structure : theme.backgroundLight;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + Math.cos(angle) * length, y + Math.sin(angle) * length);
    ctx.stroke();
  }
  ctx.restore();

  const vignette = ctx.createRadialGradient(640, 345, 300, 640, 345, 740);
  vignette.addColorStop(0, "rgba(0,0,0,0)");
  vignette.addColorStop(1, theme.name === "midnightVellum"
    ? "rgba(0,0,0,0.23)"
    : "rgba(76,58,45,0.11)");
  ctx.fillStyle = vignette;
  ctx.fillRect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT);

  backgroundCache.set(key, canvas);
  return canvas;
}

export function clearWithBackground(ctx, background, width, height) {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, width, height);
  ctx.drawImage(background, 0, 0, width, height);
  setLogicalTransform(ctx, width, height);
}

export function drawRosette(ctx, x, y, radius, primary, secondary, alpha = 1) {
  ctx.save();
  ctx.translate(x, y);
  ctx.globalAlpha = alpha;
  ctx.lineJoin = "round";
  for (let index = 0; index < 8; index += 1) {
    ctx.save();
    ctx.rotate((index / 8) * TAU);
    ctx.fillStyle = rgba(primary, 0.86);
    ctx.strokeStyle = rgba(secondary, 0.88);
    ctx.lineWidth = 0.85;
    ctx.beginPath();
    ctx.moveTo(0, -radius * 0.18);
    ctx.bezierCurveTo(
      radius * 0.22,
      -radius * 0.6,
      radius * 0.13,
      -radius,
      0,
      -radius,
    );
    ctx.bezierCurveTo(
      -radius * 0.13,
      -radius,
      -radius * 0.22,
      -radius * 0.6,
      0,
      -radius * 0.18,
    );
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }
  ctx.fillStyle = secondary;
  ctx.beginPath();
  ctx.arc(0, 0, radius * 0.22, 0, TAU);
  ctx.fill();
  ctx.restore();
}

export function drawBorder(ctx, theme, alpha = 1) {
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = rgba(theme.border, 0.68);
  ctx.lineWidth = 1.6;
  ctx.strokeRect(28, 28, LOGICAL_WIDTH - 56, LOGICAL_HEIGHT - 56);
  ctx.strokeStyle = rgba(theme.luminous, 0.5);
  ctx.lineWidth = 0.8;
  ctx.strokeRect(42, 42, LOGICAL_WIDTH - 84, LOGICAL_HEIGHT - 84);
  for (const [x, y] of [
    [70, 70],
    [LOGICAL_WIDTH - 70, 70],
    [70, LOGICAL_HEIGHT - 70],
    [LOGICAL_WIDTH - 70, LOGICAL_HEIGHT - 70],
  ]) {
    drawRosette(ctx, x, y, 15.5, theme.accent, theme.luminous);
  }
  ctx.restore();
}

export function drawFooter(ctx, scene, theme, alpha = 1) {
  const y = LOGICAL_HEIGHT - 112;
  ctx.save();
  ctx.globalAlpha = clamp(alpha);
  ctx.fillStyle = rgba(theme.panel, theme.name === "midnightVellum" ? 0.88 : 0.92);
  ctx.strokeStyle = rgba(theme.structure, 0.36);
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.roundRect(90, y, LOGICAL_WIDTH - 180, 78, 13);
  ctx.fill();
  ctx.stroke();

  const titleStyle = { ...typography.title };
  fitText(ctx, scene.title, titleStyle, 690, 22);
  ctx.fillStyle = theme.ink;
  ctx.textAlign = "left";
  ctx.textBaseline = "alphabetic";
  ctx.fillText(scene.title, 122, y + 31);

  applyTextStyle(ctx, typography.subtitle, { baseline: "alphabetic" });
  ctx.fillStyle = rgba(theme.structure, 0.92);
  const subtitle = scene.subtitle.length > 100
    ? `${scene.subtitle.slice(0, 97).trim()}…`
    : scene.subtitle;
  fitText(ctx, subtitle, typography.subtitle, 760, 13);
  ctx.fillText(subtitle, 124, y + 61);

  const right = LOGICAL_WIDTH - 120;
  if (scene.term) {
    const termStyle = { ...typography.term };
    fitText(ctx, scene.term, termStyle, 290, 15);
    ctx.fillStyle = theme.accent;
    ctx.textAlign = "right";
    ctx.textBaseline = "alphabetic";
    ctx.fillText(scene.term, right, y + 29);
  }
  if (scene.devanagari) {
    const devaStyle = { ...typography.devanagari };
    const devaSize = fitText(ctx, scene.devanagari, devaStyle, 290, 15);
    applyTextStyle(ctx, { ...devaStyle, size: devaSize }, {
      align: "right",
      baseline: "alphabetic",
      lang: "sa",
    });
    ctx.fillStyle = theme.secondary;
    ctx.fillText(scene.devanagari, right, y + 60);
  }
  ctx.restore();
}

export function drawGlowOrb(ctx, x, y, radius, color, alpha = 1, core = true) {
  ctx.save();
  const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius * 2.3);
  gradient.addColorStop(0, rgba("#ffffff", 0.96 * alpha));
  gradient.addColorStop(0.12, rgba(color, 0.94 * alpha));
  gradient.addColorStop(0.5, rgba(color, 0.26 * alpha));
  gradient.addColorStop(1, rgba(color, 0));
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(x, y, radius * 2.3, 0, TAU);
  ctx.fill();
  if (core) {
    ctx.fillStyle = rgba("#ffffff", 0.9 * alpha);
    ctx.beginPath();
    ctx.arc(x, y, Math.max(1.5, radius * 0.13), 0, TAU);
    ctx.fill();
  }
  ctx.restore();
}

export function drawGlowingPath(
  ctx,
  points,
  color,
  width = 2,
  alpha = 1,
  options = {},
) {
  if (points.length < 2) return;
  const path = new Path2D();
  path.moveTo(points[0].x, points[0].y);
  for (const point of points.slice(1)) path.lineTo(point.x, point.y);

  ctx.save();
  ctx.lineCap = options.lineCap ?? "round";
  ctx.lineJoin = "round";
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = rgba(color, 0.17);
  ctx.lineWidth = width * 5.5;
  ctx.shadowColor = rgba(color, 0.75);
  ctx.shadowBlur = options.blur ?? width * 5;
  ctx.stroke(path);
  ctx.shadowBlur = 0;
  ctx.strokeStyle = rgba(color, 0.88);
  ctx.lineWidth = width;
  ctx.stroke(path);
  ctx.restore();
}

export function drawPartialPath(ctx, points, amount, color, width = 2, alpha = 1, options = {}) {
  drawGlowingPath(ctx, partialPoints(points, amount), color, width, alpha, options);
}

export function drawLotus(
  ctx,
  cx,
  cy,
  radius,
  options = {},
) {
  const petals = options.petals ?? 8;
  const rotation = options.rotation ?? 0;
  const scaleY = options.scaleY ?? 1;
  const stroke = options.stroke ?? palette.crimson;
  const fill = options.fill ?? rgba(palette.lotusPink, 0.08);
  const alpha = options.alpha ?? 1;

  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(rotation);
  ctx.globalAlpha = alpha;
  ctx.lineWidth = options.lineWidth ?? 1.4;
  for (let index = 0; index < petals; index += 1) {
    ctx.save();
    ctx.rotate((index / petals) * TAU);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.bezierCurveTo(
      radius * 0.34,
      -radius * 0.26 * scaleY,
      radius * 0.44,
      -radius * 0.8 * scaleY,
      0,
      -radius * scaleY,
    );
    ctx.bezierCurveTo(
      -radius * 0.44,
      -radius * 0.8 * scaleY,
      -radius * 0.34,
      -radius * 0.26 * scaleY,
      0,
      0,
    );
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.strokeStyle = rgba(stroke, 0.85);
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }
  ctx.restore();
}

export function drawSilhouette(ctx, cx, cy, scale, color, alpha = 1) {
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(cx, cy - 44 * scale, 15 * scale, 0, TAU);
  ctx.fill();
  ctx.beginPath();
  ctx.moveTo(cx, cy - 25 * scale);
  ctx.bezierCurveTo(
    cx - 42 * scale,
    cy - 8 * scale,
    cx - 56 * scale,
    cy + 46 * scale,
    cx - 66 * scale,
    cy + 69 * scale,
  );
  ctx.lineTo(cx + 66 * scale, cy + 69 * scale);
  ctx.bezierCurveTo(
    cx + 56 * scale,
    cy + 46 * scale,
    cx + 42 * scale,
    cy - 8 * scale,
    cx,
    cy - 25 * scale,
  );
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

export function drawRing(ctx, cx, cy, radius, color, alpha = 1, width = 1.5) {
  ctx.save();
  ctx.strokeStyle = rgba(color, alpha);
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, TAU);
  ctx.stroke();
  ctx.restore();
}

export function drawEllipseRing(ctx, cx, cy, rx, ry, color, alpha = 1, width = 1.5, rotation = 0) {
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(rotation);
  ctx.strokeStyle = rgba(color, alpha);
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.ellipse(0, 0, rx, ry, 0, 0, TAU);
  ctx.stroke();
  ctx.restore();
}

export function drawNode(ctx, x, y, radius, options = {}) {
  const fill = options.fill ?? palette.ivory;
  const stroke = options.stroke ?? palette.indigo;
  const alpha = options.alpha ?? 1;
  ctx.save();
  ctx.globalAlpha = alpha;
  if (options.glow) drawGlowOrb(ctx, x, y, radius * 1.2, options.glow, 0.55 * alpha);
  ctx.fillStyle = fill;
  ctx.strokeStyle = stroke;
  ctx.lineWidth = options.width ?? 1.4;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, TAU);
  ctx.fill();
  ctx.stroke();
  ctx.restore();
}

export function drawLabel(ctx, text, x, y, options = {}) {
  const style = options.devanagari ? typography.devanagari : (options.style ?? typography.label);
  applyTextStyle(ctx, { ...style, size: options.size ?? style.size }, {
    align: options.align ?? "center",
    baseline: options.baseline ?? "middle",
    lang: options.devanagari ? "sa" : "en",
    letterSpacing: options.letterSpacing ?? "0px",
  });
  ctx.fillStyle = options.color ?? palette.umber;
  ctx.globalAlpha = options.alpha ?? 1;
  ctx.fillText(text, x, y);
  ctx.globalAlpha = 1;
}

export function drawArrowHead(ctx, x, y, angle, size, color, alpha = 1) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.globalAlpha = alpha;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(-size, size * 0.44);
  ctx.lineTo(-size * 0.72, 0);
  ctx.lineTo(-size, -size * 0.44);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

export function drawOrbitingNodes(ctx, cx, cy, count, rx, ry, phase, options = {}) {
  const color = options.color ?? palette.indigo;
  for (let index = 0; index < count; index += 1) {
    const angle = (index / count) * TAU + phase;
    const x = cx + Math.cos(angle) * rx;
    const y = cy + Math.sin(angle) * ry;
    const alpha = options.alpha ?? 0.8;
    drawNode(ctx, x, y, options.radius ?? 4, {
      fill: options.fill ?? palette.ivory,
      stroke: color,
      alpha,
      width: 1,
    });
  }
}

export function pointAlong(points, amount) {
  if (points.length === 0) return { x: 0, y: 0 };
  const position = clamp(amount) * (points.length - 1);
  const index = Math.floor(position);
  const fraction = position - index;
  const a = points[index];
  const b = points[Math.min(index + 1, points.length - 1)];
  return { x: lerp(a.x, b.x, fraction), y: lerp(a.y, b.y, fraction) };
}

export function drawRadialWords(ctx, words, cx, cy, radius, phase, options = {}) {
  const style = options.style ?? typography.small;
  for (let index = 0; index < words.length; index += 1) {
    const angle = phase + (index / words.length) * TAU;
    const point = polar(cx, cy, radius, angle);
    drawLabel(ctx, words[index], point.x, point.y, {
      style,
      size: options.size ?? style.size,
      color: options.color ?? palette.umber,
      alpha: options.alpha ?? 0.75,
    });
  }
}
