import { Path2D } from "@napi-rs/canvas";

import {
  TAU,
  clamp,
  easeInOutCubic,
  easeOutCubic,
  rgba,
  smoothstep,
  wave,
  lerp,
  seededRandom,
} from "../math.mjs";
import {
  drawArrowHead,
  drawEllipseRing,
  drawGlowOrb,
  drawGlowingPath,
  drawLabel,
  drawNode,
  drawPartialPath,
  drawRing
} from "../primitives.mjs";

function reveal(t) {
  return smoothstep(0, 0.08, t);
}

function ink(scene, theme) {
  return {
    primary: scene.palette?.accent ?? theme.accent,
    secondary: scene.palette?.secondary ?? theme.secondary,
    luminous: scene.palette?.luminous ?? theme.luminous,
    signal: scene.palette?.signal ?? "#d45c6c",
    prediction: scene.palette?.prediction ?? "#6ab0c6",
    error: scene.palette?.error ?? "#e8845a",
    line: theme.structure,
  };
}

function line(ctx, points, color, width, alpha, dash) {
  if (points.length < 2) return;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  if (dash) ctx.setLineDash(dash);
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (const p of points.slice(1)) ctx.lineTo(p.x, p.y);
  ctx.stroke();
  ctx.restore();
}

function brainPath(cx, cy, scale) {
  const s = scale ?? 1;
  const path = new Path2D();
  const ox = cx - 640 * s;
  const oy = cy - 300 * s;
  const p = (x, y) => ({ x: ox + x * s, y: oy + y * s });
  const M = (x, y) => path.moveTo(p(x, y).x, p(x, y).y);
  const Q = (cx, cy, x, y) => { const a = p(cx, cy); const b = p(x, y); path.quadraticCurveTo(a.x, a.y, b.x, b.y); };
  const C = (c1x, c1y, c2x, c2y, x, y) => {
    const a = p(c1x, c1y); const b = p(c2x, c2y); const c = p(x, y);
    path.bezierCurveTo(a.x, a.y, b.x, b.y, c.x, c.y);
  };
  M(590, 120);
  C(620, 90, 680, 85, 710, 95);
  C(740, 105, 780, 140, 790, 200);
  C(795, 230, 790, 260, 770, 285);
  C(755, 305, 730, 310, 710, 305);
  C(700, 340, 680, 370, 650, 395);
  C(645, 410, 640, 420, 640, 420);
  C(640, 420, 635, 410, 630, 395);
  C(600, 370, 580, 340, 570, 305);
  C(550, 310, 525, 305, 510, 285);
  C(490, 260, 485, 230, 490, 200);
  C(500, 140, 540, 105, 570, 95);
  C(580, 90, 585, 95, 590, 120);
  path.closePath();
  return path;
}

function cerebellumPath(cx, cy, scale) {
  const s = scale ?? 1;
  const path = new Path2D();
  const ox = cx - 640 * s;
  const oy = cy - 300 * s;
  const p = (x, y) => ({ x: ox + x * s, y: oy + y * s });
  path.ellipse(p(680, 400).x, p(680, 400).y, 40 * s, 25 * s, 0.3, 0, TAU);
  return path;
}

const LOBE_COLORS = {
  frontal: "#3b7a9e",
  parietal: "#5a8ca0",
  temporal: "#c4445a",
  occipital: "#6ab0c6",
  cerebellum: "#8a7a6a",
  brainstem: "#4a5563",
};

const LOBE_POLYGONS = {
  frontal:  [{ x: 510, y: 200 }, { x: 570, y: 95 }, { x: 720, y: 105 }, { x: 780, y: 170 }, { x: 760, y: 240 }, { x: 700, y: 250 }, { x: 640, y: 230 }, { x: 560, y: 240 }],
  parietal: [{ x: 720, y: 110 }, { x: 790, y: 170 }, { x: 770, y: 260 }, { x: 710, y: 280 }, { x: 660, y: 260 }, { x: 680, y: 200 }],
  temporal: [{ x: 560, y: 280 }, { x: 630, y: 245 }, { x: 700, y: 270 }, { x: 720, y: 310 }, { x: 680, y: 370 }, { x: 620, y: 360 }, { x: 580, y: 320 }],
  occipital: [{ x: 750, y: 250 }, { x: 790, y: 260 }, { x: 770, y: 320 }, { x: 720, y: 340 }, { x: 700, y: 300 }],
};

function makeRng(seedVal) {
  const r = seededRandom(seedVal ?? 2607);
  return (min, max) => min + r() * (max - min);
}

function netNodePositions(layers, nodesPerLayer, cx, cy, width, height) {
  const positions = [];
  for (let l = 0; l < layers; l++) {
    const layer = [];
    const x = cx - width / 2 + (l + 0.5) * (width / layers);
    for (let n = 0; n < nodesPerLayer; n++) {
      const y = cy - height / 2 + (n + 0.5) * (height / nodesPerLayer);
      layer.push({ x, y });
    }
    positions.push(layer);
  }
  return positions;
}

export const assetImplementations = Object.freeze({
  "brain-schematic": brainSchematic,
  "neural-network": neuralNetwork,
  "cortical-column": corticalColumn,
  "attention-field": attentionField,
  "prediction-signal": predictionSignal,
  "memory-trace": memoryTrace,
  "error-signal": errorSignal,
  "neural-oscillation": neuralOscillation,
});

function brainSchematic(ctx, t, params, env) {
  const theme = env.theme;
  const cx = params.cx ?? 640;
  const cy = params.cy ?? 300;
  const scale = params.scale ?? 0.85;
  const alpha = reveal(t) * (params.alpha ?? 0.9);
  const outline = brainPath(cx, cy, scale);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.fillStyle = rgba(theme.backgroundLight, 0.3);
  ctx.fill(outline);
  ctx.strokeStyle = rgba(theme.structure, alpha);
  ctx.lineWidth = 1.4;
  ctx.stroke(outline);
  const cb = cerebellumPath(cx, cy, scale);
  ctx.strokeStyle = rgba("#8a7a6a", alpha * 0.6);
  ctx.lineWidth = 1.1;
  ctx.stroke(cb);
  if (params.labels) {
    const labels = [
      { text: "frontal", x: 630, y: 175 },
      { text: "parietal", x: 730, y: 210 },
      { text: "temporal", x: 620, y: 315 },
      { text: "occipital", x: 765, y: 290 },
    ];
    for (const label of labels) {
      drawLabel(ctx, label.text, label.x, label.y, {
        color: theme.structure, size: 11, alpha: alpha * 0.7, align: "center",
      });
    }
  }
  ctx.restore();
}

function neuralNetwork(ctx, t, params, env) {
  const theme = env.theme;
  const cx = params.cx ?? 640;
  const cy = params.cy ?? 320;
  const layers = params.layers ?? 4;
  const nodesPerLayer = params.nodesPerLayer ?? 6;
  const density = params.density ?? 0.6;
  const alpha = reveal(t) * (params.alpha ?? 0.85);
  const rand = makeRng(params.seed);
  const pos = netNodePositions(layers, nodesPerLayer, cx, cy, 700, 360);
  const connections = [];
  for (let l = 0; l < layers - 1; l++) {
    for (const src of pos[l]) {
      for (const dst of pos[l + 1]) {
        if (rand(0, 1) < density) {
          connections.push({ src, dst, weight: rand(0.3, 1) });
        }
      }
    }
  }
  ctx.save();
  ctx.globalAlpha = alpha * 0.35;
  for (const conn of connections) {
    ctx.beginPath();
    ctx.moveTo(conn.src.x, conn.src.y);
    ctx.lineTo(conn.dst.x, conn.dst.y);
    ctx.strokeStyle = rgba(theme.structure, conn.weight * 0.35 * alpha);
    ctx.lineWidth = 0.5 + conn.weight * 0.8;
    ctx.stroke();
  }
  ctx.globalAlpha = alpha;
  for (const layer of pos) {
    for (const node of layer) {
      drawNode(ctx, node.x, node.y, 4, {
        fill: theme.backgroundLight,
        stroke: theme.secondary,
        alpha: alpha * 0.85,
      });
    }
  }
  ctx.restore();
}

function corticalColumn(ctx, t, params, env) {
  const theme = env.theme;
  const cx = params.cx ?? 640;
  const cy = params.cy ?? 340;
  const height = params.height ?? 280;
  const alpha = reveal(t) * (params.alpha ?? 0.85);
  const layers = [
    { label: "I", y: 0.05, color: theme.secondary },
    { label: "II/III", y: 0.2, color: theme.structure },
    { label: "IV", y: 0.38, color: theme.accent },
    { label: "V", y: 0.6, color: theme.secondary },
    { label: "VI", y: 0.8, color: theme.structure },
  ];
  const width = 120;
  ctx.save();
  ctx.globalAlpha = alpha;
  for (const layer of layers) {
    const y = cy - height / 2 + layer.y * height;
    const h = height * 0.14;
    ctx.fillStyle = rgba(layer.color, 0.08);
    ctx.fillRect(cx - width / 2, y, width, h);
    ctx.strokeStyle = rgba(layer.color, 0.25);
    ctx.lineWidth = 0.6;
    ctx.strokeRect(cx - width / 2, y, width, h);
    if (params.labels) {
      drawLabel(ctx, layer.label, cx + width / 2 + 12, y + h / 2, {
        color: layer.color, size: 10, alpha: 0.6, align: "left",
      });
    }
  }
  ctx.strokeStyle = rgba(theme.structure, alpha * 0.5);
  ctx.lineWidth = 1;
  ctx.strokeRect(cx - width / 2 - 2, cy - height / 2 - 2, width + 4, height + 4);
  ctx.restore();
}

function attentionField(ctx, t, params, env) {
  const theme = env.theme;
  const cx = params.cx ?? 640;
  const cy = params.cy ?? 320;
  const radius = params.radius ?? 200;
  const intensity = params.intensity ?? 0.7;
  const alpha = reveal(t) * (params.alpha ?? 0.75);
  ctx.save();
  const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
  grad.addColorStop(0, rgba(theme.luminous, intensity * alpha * 0.35));
  grad.addColorStop(0.4, rgba(theme.luminous, intensity * alpha * 0.15));
  grad.addColorStop(0.7, rgba(theme.luminous, 0.04 * alpha));
  grad.addColorStop(1, rgba(theme.luminous, 0));
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 1280, 720);
  drawEllipseRing(ctx, cx, cy, radius, radius * 0.7, theme.luminous, 0.55 * alpha, 1.2, 0);
  ctx.restore();
}

function predictionSignal(ctx, t, params, env) {
  const theme = env.theme;
  const fromX = params.fromX ?? 200;
  const fromY = params.fromY ?? 320;
  const toX = params.toX ?? 1080;
  const toY = params.toY ?? 320;
  const width = params.width ?? 3;
  const style = params.style ?? "wave";
  const alpha = reveal(t) * (params.alpha ?? 0.8);
  const progress = easeOutCubic(t);
  const dx = toX - fromX;
  const dy = toY - fromY;
  ctx.save();
  ctx.globalAlpha = alpha;
  if (style === "wave") {
    const points = [];
    const steps = 60;
    for (let i = 0; i <= steps; i++) {
      const p = i / steps;
      const x = fromX + dx * p;
      const amplitude = 30 * (1 - Math.abs(p - 0.5) * 1.4);
      const y = fromY + dy * p + amplitude * Math.sin(p * TAU * 4 - t * TAU * 0.8);
      points.push({ x, y });
    }
    const drawLen = Math.floor(progress * points.length);
    if (drawLen > 1) {
      drawPartialPath(ctx, points.slice(0, drawLen), 1, theme.prediction, width, 0.85 * alpha, { blur: 6 });
    }
  } else if (style === "arrow") {
    const x = fromX + dx * progress;
    const y = fromY + dy * progress;
    const angle = Math.atan2(dy, dx);
    const origin = { x: fromX, y: fromY };
    line(ctx, [origin, { x, y }], theme.prediction, width, alpha);
    drawArrowHead(ctx, x, y, angle, 14, theme.prediction, alpha);
  } else {
    const x = fromX + dx * progress;
    drawGlowOrb(ctx, x, fromY, 10 + 6 * wave(t, 2), theme.prediction, alpha * 0.8);
    line(ctx, [{ x: fromX, y: fromY }, { x: toX, y: toY }], theme.prediction, width * 0.3, alpha * 0.2);
  }
  ctx.restore();
}

function memoryTrace(ctx, t, params, env) {
  const theme = env.theme;
  const nodes = params.nodes ?? 5;
  const decay = params.decay ?? 0.3;
  const reinforce = params.reinforce ?? false;
  const alpha = reveal(t) * (params.alpha ?? 0.8);
  const cx = params.cx ?? 640;
  const cy = params.cy ?? 320;
  const rand = makeRng(params.seed);
  const positions = [];
  for (let i = 0; i < nodes; i++) {
    positions.push({
      x: cx - 300 + i * (600 / (nodes - 1)),
      y: cy - 100 + rand(-50, 50),
    });
  }
  ctx.save();
  for (let i = 0; i < positions.length - 1; i++) {
    const strength = reinforce ? 1 - decay * (1 - i / (nodes - 1)) : 1 - decay * (i / (nodes - 1));
    const trace = smoothstep(strength * 0.3, 1, t) * alpha;
    line(ctx, [positions[i], positions[i + 1]], theme.secondary, 1 + strength * 2, trace * 0.7);
  }
  for (let i = 0; i < positions.length; i++) {
    const strength = reinforce ? 1 - decay * (1 - i / (nodes - 1)) : 1 - decay * (i / (nodes - 1));
    drawNode(ctx, positions[i].x, positions[i].y, 3 + strength * 4, {
      fill: theme.backgroundLight,
      stroke: i === 0 ? theme.luminous : theme.secondary,
      alpha: alpha * (0.4 + strength * 0.5),
      glow: i === 0 ? theme.luminous : undefined,
    });
  }
  ctx.restore();
}

function errorSignal(ctx, t, params, env) {
  const theme = env.theme;
  const x = params.x ?? 640;
  const y = params.y ?? 320;
  const magnitude = params.magnitude ?? 0.7;
  const alpha = reveal(t) * (params.alpha ?? 0.85);
  const pulse = wave(t, 3 + magnitude * 4);
  const radius = 8 + magnitude * 28;
  ctx.save();
  ctx.globalAlpha = alpha * (0.5 + pulse * 0.5);
  ctx.strokeStyle = theme.error;
  ctx.lineWidth = 1.5 + magnitude * 2;
  const spread = radius * (0.6 + pulse * 0.4);
  ctx.beginPath();
  ctx.moveTo(x - spread, y - spread);
  ctx.lineTo(x + spread, y + spread);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x + spread, y - spread);
  ctx.lineTo(x - spread, y + spread);
  ctx.stroke();
  drawRing(ctx, x, y, radius * (0.5 + pulse * 0.5), theme.error, alpha * 0.3 * pulse, 2);
  ctx.restore();
}

function neuralOscillation(ctx, t, params, env) {
  const theme = env.theme;
  const band = params.band ?? "alpha";
  const amplitude = params.amplitude ?? 0.7;
  const channels = params.channels ?? 2;
  const alpha = reveal(t) * (params.alpha ?? 0.75);
  const freqs = { delta: 1.5, theta: 5, alpha: 10, beta: 18, gamma: 40 };
  const freq = freqs[band] ?? 10;
  const baseY = params.baseY ?? 360;
  const cx = params.cx ?? 640;
  const width = params.width ?? 700;
  ctx.save();
  ctx.globalAlpha = alpha;
  for (let ch = 0; ch < channels; ch++) {
    const y0 = baseY + (ch - (channels - 1) / 2) * 80;
    ctx.strokeStyle = ch === 0 ? theme.signal : theme.secondary;
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    for (let i = 0; i <= 160; i++) {
      const p = i / 160;
      const x = cx - width / 2 + p * width;
      const osc = Math.sin(p * TAU * freq * (t * 0.5 + 0.5) * 0.8 + ch * 1.2) * amplitude * 25;
      const env2 = 1 - Math.abs(p - 0.5) * 0.6;
      const y = y0 + osc * env2;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  drawLabel(ctx, `${band} (${freq} Hz)`, cx, baseY + (channels / 2) * 80 + 30, {
    color: theme.structure, size: 12, alpha: alpha * 0.6, align: "center",
  });
  ctx.restore();
}

export const mechanismImplementations = Object.freeze({
  "attention-selection": attentionSelection,
  "predictive-loop": predictiveLoop,
  "pattern-completion": patternCompletion,
  "memory-consolidation": memoryConsolidation,
  "neural-propagation": neuralPropagation,
  "competitive-binding": competitiveBinding,
  "temporal-integration": temporalIntegration,
  "error-driven-learning": errorDrivenLearning,
});

function attentionSelection(ctx, t, scene, env) {
  const { theme } = env;
  const { primary, secondary, luminous, line } = ink(scene, theme);
  const alpha = reveal(t);
  const count = scene.params?.itemCount ?? 6;
  const apertureSize = scene.params?.apertureSize ?? 0.18;
  const progress = easeInOutCubic(t);
  const selected = Math.min(Math.floor(progress * count), count - 1);
  const itemSpacing = 780 / count;
  const baseX = 250;
  const y = 340;
  const items = [];
  for (let i = 0; i < count; i++) {
    const x = baseX + i * itemSpacing + itemSpacing / 2;
    const isSelected = i === selected;
    const dist = Math.abs(progress * count - i);
    const suppress = smoothstep(0, 2, dist - 0.5);
    items.push({
      x, y, selected: isSelected,
      opacity: isSelected ? 1 : 0.25 + (1 - suppress) * 0.35,
      scale: isSelected ? 1 : 0.7 + (1 - suppress) * 0.2,
    });
  }
  for (const item of items) {
    ctx.save();
    ctx.globalAlpha = alpha * item.opacity;
    ctx.translate(item.x, item.y);
    ctx.scale(item.scale, item.scale);
    drawNode(ctx, 0, 0, 28, {
      fill: theme.backgroundLight,
      stroke: item.selected ? luminous : secondary,
      alpha: alpha * item.opacity,
      glow: item.selected ? luminous : undefined,
    });
    drawLabel(ctx, `${item.selected ? "selected" : "item"}`, 0, 42, {
      color: item.selected ? luminous : line,
      size: 11, alpha: alpha * item.opacity * 0.8, align: "center",
    });
    ctx.restore();
  }
  const apertureX = baseX + itemSpacing / 2 + progress * (count - 1) * itemSpacing;
  drawGlowOrb(ctx, apertureX, y, 50 * apertureSize * 300, luminous, 0.12 * alpha);
  drawEllipseRing(ctx, apertureX, y, 55 * apertureSize * 300, 55 * apertureSize * 300 * 0.6, luminous, 0.4 * alpha, 1.2, 0);
  drawLabel(ctx, scene.params?.caption ?? "attention selects by enhancing some contents while suppressing others", 640, 110, {
    color: primary, size: 16, alpha: 0.82 * alpha, align: "center",
  });
}

function predictiveLoop(ctx, t, scene, env) {
  const { theme } = env;
  const { primary, secondary, luminous, prediction, error, signal, line } = ink(scene, theme);
  const alpha = reveal(t);
  const hierarchy = scene.params?.hierarchy ?? 2;
  const convergenceTime = scene.params?.convergenceTime ?? 0.55;
  const spacing = 600 / (hierarchy + 1);
  const baseX = 340;
  const topY = 200;
  const bottomY = 460;
  for (let level = 0; level <= hierarchy; level++) {
    const x = baseX + level * spacing;
    const converge = smoothstep(convergenceTime * 0.5, convergenceTime, t);
    drawNode(ctx, x, topY, 12, {
      fill: theme.backgroundLight, stroke: prediction, alpha: alpha * 0.9, glow: converge > 0.5 ? undefined : prediction,
    });
    drawNode(ctx, x, bottomY, 12, {
      fill: theme.backgroundLight, stroke: signal, alpha: alpha * 0.9, glow: converge < 0.5 ? undefined : signal,
    });
    if (level < hierarchy) {
      const downArrow = easeOutCubic(smoothstep(0, convergenceTime * 0.6, t));
      const upArrow = easeOutCubic(smoothstep(convergenceTime * 0.3, 1, t));
      const nextX = baseX + (level + 1) * spacing;
      const midX = (x + nextX) / 2;
      const topMidY = (topY + 145) / 2;
      const bottomMidY = (bottomY + 145) / 2;
      line(ctx, [{ x, y: topY + 14 }, { x: midX, y: topMidY }, { x: nextX, y: topY + 14 }], prediction, 1.5, alpha * 0.7 * downArrow);
      line(ctx, [{ x: nextX, y: bottomY - 14 }, { x: midX, y: bottomMidY }, { x, y: bottomY - 14 }], signal, 1.5, alpha * 0.7 * upArrow);
      if (converge > 0.3) {
        const errX = nextX;
        drawGlowOrb(ctx, errX, 320, 6 + 4 * wave(t, 2 + level), error, alpha * (1 - converge) * 0.7);
      }
    }
    if (level === 0) {
      drawLabel(ctx, "input", x - 30, bottomY + 30, { color: signal, size: 12, alpha: 0.8 * alpha });
    }
    if (level === hierarchy) {
      drawLabel(ctx, "prediction", x + 30, topY - 30, { color: prediction, size: 12, alpha: 0.8 * alpha });
      drawLabel(ctx, "error", x + 55, 318, { color: error, size: 11, alpha: alpha * (1 - smoothstep(convergenceTime, 0.85, t)) * 0.8 });
    }
  }
  drawLabel(ctx, scene.params?.caption ?? "prediction and sensory input converge; residual error drives revision", 640, 105, {
    color: primary, size: 16, alpha: 0.82 * alpha, align: "center",
  });
}

function patternCompletion(ctx, t, scene, env) {
  const { theme } = env;
  const { primary, secondary, luminous, line } = ink(scene, theme);
  const alpha = reveal(t);
  const count = scene.params?.nodeCount ?? 10;
  const degradation = scene.params?.degradation ?? 0.45;
  const rand = makeRng(scene.seed);
  const cx = 640;
  const cy = 310;
  const radius = 280;
  const nodes = [];
  for (let i = 0; i < count; i++) {
    const angle = (i / count) * TAU - Math.PI / 2;
    nodes.push({
      x: cx + Math.cos(angle) * radius,
      y: cy + Math.sin(angle) * radius * 0.65,
    });
  }
  const completion = easeInOutCubic(smoothstep(0.1, 0.85, t));
  for (let i = 0; i < count; i++) {
    const appear = smoothstep(i / count * 0.5, 0.5 + i / count * 0.5, completion);
    const shouldAppear = rand(0, 1) > degradation || completion > 0.9;
    if (shouldAppear || appear > 0.3) {
      drawNode(ctx, nodes[i].x, nodes[i].y, 5 + 3 * appear, {
        fill: theme.backgroundLight,
        stroke: i % 3 === 0 ? luminous : secondary,
        alpha: alpha * appear,
        glow: i % 3 === 0 ? luminous : undefined,
      });
    }
  }
  for (let i = 0; i < count - 1; i++) {
    const appear = completion > 0.3 ? smoothstep(0.3, 0.7, completion) : 0;
    line(ctx, [nodes[i], nodes[i + 1]], secondary, 0.8, alpha * appear * 0.25);
  }
  drawLabel(ctx, scene.params?.caption ?? "partial input reconstructs into a complete pattern through spreading activation", 640, 105, {
    color: primary, size: 16, alpha: 0.82 * alpha, align: "center",
  });
}

function memoryConsolidation(ctx, t, scene, env) {
  const { theme } = env;
  const { primary, secondary, luminous, line } = ink(scene, theme);
  const alpha = reveal(t);
  const count = scene.params?.traceCount ?? 10;
  const retention = scene.params?.retention ?? 0.55;
  const rand = makeRng(scene.seed);
  const cx = 640;
  const cy = 310;
  const traces = [];
  for (let i = 0; i < count; i++) {
    const survives = rand(0, 1) < retention;
    const strength = survives ? 0.5 + rand(0, 0.5) : rand(0, 0.3);
    traces.push({
      x: cx - 300 + rand(0, 600),
      y: cy - 200 + rand(0, 400),
      survives,
      strength,
    });
  }
  const reorganisation = easeInOutCubic(smoothstep(0.1, 0.9, t));
  const early = 1 - reorganisation;
  const late = reorganisation;
  for (const trace of traces) {
    const s = trace.survives ? lerp(early * 0.5 + late * trace.strength, trace.strength, reorganisation) : early * trace.strength;
    drawNode(ctx, trace.x, trace.y, 3 + s * 8, {
      fill: theme.backgroundLight,
      stroke: trace.survives ? (reorganisation > 0.5 ? luminous : secondary) : line,
      alpha: alpha * (0.15 + s * 0.7),
      glow: trace.survives && reorganisation > 0.5 ? luminous : undefined,
    });
  }
  for (let i = 0; i < traces.length - 1; i++) {
    const w = (traces[i].strength + traces[i + 1].strength) / 2 * late;
    line(ctx, [traces[i], traces[i + 1]], secondary, 0.6, alpha * w * 0.2);
  }
  drawLabel(ctx, scene.params?.caption ?? "traces reorganise: some stabilise, others decay — consolidation is not mere preservation", 640, 105, {
    color: primary, size: 15, alpha: 0.82 * alpha, align: "center",
  });
}

function neuralPropagation(ctx, t, scene, env) {
  const { theme } = env;
  const { primary, secondary, luminous, line } = ink(scene, theme);
  const alpha = reveal(t);
  const layers = 4;
  const nodesPerLayer = 5;
  const sourceLayer = scene.params?.sourceLayer ?? 0;
  const amplification = scene.params?.amplification ?? 1;
  const pos = netNodePositions(layers, nodesPerLayer, 640, 320, 700, 380);
  const rand = makeRng(scene.seed);
  const conns = [];
  for (let l = 0; l < layers - 1; l++) {
    for (const src of pos[l]) {
      for (const dst of pos[l + 1]) {
        conns.push({ src, dst, delay: l * 0.2 + rand(0, 0.1), gain: 0.3 + rand(0, 0.7) });
      }
    }
  }
  for (const conn of conns) {
    const arrival = smoothstep(conn.delay, conn.delay + 0.15, t);
    const signalAmp = arrival * conn.gain * amplification;
    ctx.beginPath();
    ctx.moveTo(conn.src.x, conn.src.y);
    ctx.lineTo(conn.dst.x, conn.dst.y);
    ctx.strokeStyle = rgba(secondary, signalAmp * 0.3 * alpha);
    ctx.lineWidth = 0.5 + signalAmp * 1.5;
    ctx.globalAlpha = alpha;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }
  for (let l = 0; l < layers; l++) {
    for (let n = 0; n < pos[l].length; n++) {
      const node = pos[l][n];
      const activation = smoothstep(l * 0.2, l * 0.2 + 0.15, t) * amplification;
      const nodeAmp = clamp(activation * 0.3 + 0.2, 0, 1);
      drawNode(ctx, node.x, node.y, 3 + nodeAmp * 6, {
        fill: theme.backgroundLight,
        stroke: l === sourceLayer ? luminous : (nodeAmp > 0.5 ? primary : secondary),
        alpha: alpha * (0.2 + nodeAmp * 0.7),
        glow: nodeAmp > 0.6 ? luminous : undefined,
      });
    }
  }
  drawLabel(ctx, scene.params?.caption ?? "activation spreads through a network, amplified at each junction", 640, 105, {
    color: primary, size: 16, alpha: 0.82 * alpha, align: "center",
  });
}

function competitiveBinding(ctx, t, scene, env) {
  const { theme } = env;
  const { primary, secondary, luminous, line } = ink(scene, theme);
  const alpha = reveal(t);
  const candidates = scene.params?.candidates ?? 3;
  const resolution = scene.params?.resolution ?? "winner-take-all";
  const cx = 640;
  const cy = 340;
  const spacing = 700 / candidates;
  const baseX = cx - (candidates - 1) * spacing / 2;
  const progress = easeInOutCubic(t);
  let winner;
  if (resolution === "alternating") {
    const period = Math.floor(t * 3) % candidates;
    winner = period;
  } else {
    winner = Math.min(Math.floor(progress * candidates), candidates - 1);
  }
  for (let i = 0; i < candidates; i++) {
    const x = baseX + i * spacing;
    const isWinner = i === winner;
    const suppression = resolution === "alternating" ? (isWinner ? 1 : 0.2 + 0.15 * wave(t * (1 + i), 2)) : (isWinner ? 1 : 1 - progress * 0.7);
    drawNode(ctx, x, cy, isWinner ? 32 : 24, {
      fill: theme.backgroundLight,
      stroke: isWinner ? luminous : secondary,
      alpha: alpha * suppression,
      glow: isWinner ? luminous : undefined,
    });
    if (resolution === "alternating") {
      const label = isWinner ? "bound" : "suppressed";
      drawLabel(ctx, label, x, cy + 40, {
        color: isWinner ? luminous : line, size: 11, alpha: alpha * suppression * 0.7, align: "center",
      });
    }
  }
  if (resolution !== "alternating") {
    const bindX = baseX + winner * spacing;
    drawRing(ctx, bindX, cy, 52, luminous, 0.3 * alpha * progress, 1.5);
  }
  drawLabel(ctx, scene.params?.caption ?? "candidate features compete; one binds into a unified percept while alternatives are suppressed", 640, 105, {
    color: primary, size: 15, alpha: 0.82 * alpha, align: "center",
  });
}

function temporalIntegration(ctx, t, scene, env) {
  const { theme } = env;
  const { primary, secondary, luminous, line } = ink(scene, theme);
  const alpha = reveal(t);
  const count = scene.params?.itemCount ?? 5;
  const decay = scene.params?.retentionDecay ?? 0.25;
  const cx = 640;
  const cy = 330;
  const spacing = 720 / count;
  const baseX = cx - (count - 1) * spacing / 2;
  for (let i = 0; i < count; i++) {
    const arrival = smoothstep(i / count * 0.6, 0.3 + i / count * 0.6, t);
    const retention = 1 - decay * (i / (count - 1));
    const x = baseX + i * spacing;
    ctx.save();
    ctx.globalAlpha = alpha * arrival * (0.3 + retention * 0.7);
    drawNode(ctx, x, cy, 8 + retention * 10, {
      fill: theme.backgroundLight,
      stroke: retention > 0.6 ? luminous : secondary,
      alpha: alpha * arrival,
      glow: retention > 0.6 ? luminous : undefined,
    });
    ctx.restore();
  }
  for (let i = 0; i < count - 1; i++) {
    const appear = smoothstep((i + 1) / count * 0.5, 0.5 + (i + 1) / count * 0.4, t);
    const x1 = baseX + i * spacing;
    const x2 = baseX + (i + 1) * spacing;
    line(ctx, [{ x: x1, y: cy }, { x: (x1 + x2) / 2, y: cy - 60 }, { x: x2, y: cy }], secondary, 0.8, alpha * appear * 0.3);
  }
  drawLabel(ctx, scene.params?.caption ?? "sequential items accumulate into a single episode — earlier traces persist as later ones arrive", 640, 105, {
    color: primary, size: 15, alpha: 0.82 * alpha, align: "center",
  });
}

function errorDrivenLearning(ctx, t, scene, env) {
  const { theme } = env;
  const { primary, secondary, luminous, prediction, signal, error, line } = ink(scene, theme);
  const alpha = reveal(t);
  const epochs = scene.params?.epochs ?? 2;
  const learningRate = scene.params?.learningRate ?? 0.3;
  const epochDuration = 1 / epochs;
  const currentEpoch = Math.min(Math.floor(t / epochDuration), epochs - 1);
  const epochProgress = (t - currentEpoch * epochDuration) / epochDuration;
  const cx = 640;
  const layers = [
    { label: "input", y: 200 },
    { label: "hidden", y: 340 },
    { label: "output", y: 480 },
  ];
  const layerPositions = layers.map((l, i) => ({
    x: cx,
    y: l.y,
    nodes: i === 1 ? 4 : 3,
  }));
  for (const layer of layerPositions) {
    for (let n = 0; n < layer.nodes; n++) {
      const nx = layer.x - (layer.nodes - 1) * 25 + n * 50;
      const isActive = epochProgress > 0.1 && epochProgress < 0.6;
      drawNode(ctx, nx, layer.y, 6, {
        fill: theme.backgroundLight,
        stroke: isActive ? (currentEpoch > 0 ? primary : secondary) : line,
        alpha: alpha * (isActive ? 0.9 : 0.3),
        glow: isActive && currentEpoch > 0 ? primary : undefined,
      });
    }
  }
  const feedbackPhase = smoothstep(0.5, 0.85, epochProgress);
  if (feedbackPhase > 0) {
    const errX = cx + 200;
    const errY = layers[2].y;
    drawGlowOrb(ctx, errX, errY, 10 + 8 * wave(t * 2, 1), error, alpha * feedbackPhase * 0.8);
    const errTraces = [
      { from: { x: cx, y: layers[2].y }, to: { x: cx, y: layers[1].y } },
      { from: { x: cx, y: layers[1].y }, to: { x: cx, y: layers[0].y } },
    ];
    for (const trace of errTraces) {
      const errorProgress = smoothstep(0.5, 0.9, epochProgress);
      line(ctx, [trace.from, trace.to], error, 1.5 + feedbackPhase * 2, alpha * feedbackPhase * 0.6 * errorProgress);
    }
  }
  const weightLabel = currentEpoch > 0 ? `epoch ${currentEpoch + 1}/${epochs}` : "initial pass";
  drawLabel(ctx, weightLabel, cx, 535, {
    color: secondary, size: 12, alpha: 0.7 * alpha, align: "center",
  });
  drawLabel(ctx, scene.params?.caption ?? "error signal propagates backward, modifying weights so the next prediction improves", 640, 105, {
    color: primary, size: 15, alpha: 0.82 * alpha, align: "center",
  });
}
