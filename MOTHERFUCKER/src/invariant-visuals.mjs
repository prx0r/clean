import {
  TAU,
  clamp,
  easeInOutCubic,
  easeOutCubic,
  hashString,
  lerp,
  polar,
  pulse,
  rgba,
  seededRandom,
  smoothstep,
  wave,
} from "../math.mjs";
import {
  drawArrowHead,
  drawEllipseRing,
  drawGlowOrb,
  drawLabel,
  drawNode,
  drawPartialPath,
  drawRing,
  pointAlong,
} from "../primitives.mjs";
import {
  causalTraceSeries,
  clampArray,
  hermiteScalar,
  normalizedSimilarity,
  pairwiseDistanceSignature,
  parity,
  sampleTrajectory,
  signatureDistance,
  transformPoints,
} from "./invariant-math.mjs";
import {
  carrierGeometry,
  lobedContour,
  relationalNecklace,
  topologyThread,
  transformedSeed,
} from "./invariant-geometry.mjs";

function reveal(t) {
  return smoothstep(0.01, 0.12, t);
}

function colors(theme) {
  return {
    ink: theme.ink,
    structure: theme.structure,
    accent: theme.accent,
    secondary: theme.secondary,
    luminous: theme.invariant ?? theme.luminous,
    trace: theme.trace ?? "#8d7893",
    carrier: theme.carrier ?? "#467985",
    breaking: theme.break ?? theme.accent,
    lead: theme.lead ?? theme.accent,
    lag: theme.lag ?? theme.secondary,
    field: theme.field ?? "#668d78",
  };
}

function strokePath(ctx, points, options = {}) {
  if (points.length < 2) return;
  const {
    color = "#222222",
    width = 1.5,
    alpha = 1,
    closed = false,
    dash = [],
    glow = 0,
  } = options;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.setLineDash(dash);
  if (glow > 0) {
    ctx.shadowColor = color;
    ctx.shadowBlur = glow;
  }
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (const point of points.slice(1)) ctx.lineTo(point.x, point.y);
  if (closed) ctx.closePath();
  ctx.stroke();
  ctx.restore();
}

function fillPath(ctx, points, options = {}) {
  if (points.length < 3) return;
  ctx.save();
  ctx.globalAlpha *= options.alpha ?? 1;
  ctx.fillStyle = options.color ?? "#ffffff";
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (const point of points.slice(1)) ctx.lineTo(point.x, point.y);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function line(ctx, a, b, color, alpha = 1, width = 1.2, dash = []) {
  strokePath(ctx, [a, b], { color, alpha, width, dash });
}

function seeded(seed) {
  const rng = seededRandom((seed ?? 2607) >>> 0);
  return (minimum = 0, maximum = 1) => minimum + rng() * (maximum - minimum);
}

function seedPoints(params = {}, phase = 0) {
  return transformedSeed({
    cx: params.x ?? params.cx ?? 640,
    cy: params.y ?? params.cy ?? 300,
    radius: params.radius ?? 64,
    lobes: params.lobes ?? 5,
    harmonic: params.harmonic ?? 0.22,
    scale: params.scale ?? 1,
    rotation: (params.rotation ?? 0) + phase,
    reflectX: params.reflectX ?? false,
    reflectY: params.reflectY ?? false,
  });
}

function drawSeed(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.9);
  const phase = (params.rotationSpeed ?? 0.02) * t * TAU;
  const points = seedPoints(params, phase);
  fillPath(ctx, points, {
    color: rgba(params.fill ?? c.luminous, params.fillAlpha ?? 0.08),
    alpha,
  });
  strokePath(ctx, points, {
    color: params.color ?? c.luminous,
    alpha,
    width: params.width ?? 1.8,
    closed: true,
    glow: params.glow ?? 5,
  });
  const center = {
    x: params.x ?? params.cx ?? 640,
    y: params.y ?? params.cy ?? 300,
  };
  drawGlowOrb(ctx, center.x, center.y, params.coreRadius ?? 7, c.luminous, 0.45 * alpha);
  return points;
}

function continuitySeed(ctx, t, params, env) {
  drawSeed(ctx, t, params, env);
}

function relationalSignature(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.85);
  const values = params.values ?? [0.18, 0.78, 0.42, 1, 0.56];
  if ((params.mode ?? "radial") === "linear") {
    const left = params.x ?? 320;
    const top = params.y ?? 280;
    const width = params.width ?? 640;
    const maximum = Math.max(...values.map((value) => Math.abs(value)), 1e-9);
    const points = values.map((value, index) => ({
      x: left + (index / Math.max(1, values.length - 1)) * width,
      y: top - (value / maximum) * 80,
    }));
    strokePath(ctx, points, { color: c.secondary, width: 2, alpha, glow: 4 });
    points.forEach((point, index) => drawNode(ctx, point.x, point.y, 4, {
      fill: env.theme.backgroundLight,
      stroke: index === 0 ? c.luminous : c.secondary,
      alpha,
    }));
    return;
  }
  const points = relationalNecklace(values, {
    cx: params.x ?? params.cx ?? 640,
    cy: params.y ?? params.cy ?? 300,
    radius: params.radius ?? 72,
    radialScale: params.radialScale ?? 30,
    rotation: (params.rotation ?? 0) + t * 0.03,
  });
  strokePath(ctx, points, { color: c.secondary, width: 1.6, alpha, closed: true, glow: 4 });
  points.forEach((point, index) => drawNode(ctx, point.x, point.y, 3.5 + (index % 2), {
    fill: env.theme.backgroundLight,
    stroke: index === 0 ? c.luminous : c.secondary,
    alpha,
  }));
}

function transformationOrbit(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.82);
  const count = Math.max(3, Math.min(16, Math.round(params.count ?? 7)));
  const cx = params.x ?? 640;
  const cy = params.y ?? 300;
  const orbitRadius = params.orbitRadius ?? 205;
  for (let index = 0; index < count; index += 1) {
    const angle = -Math.PI / 2 + (index / count) * TAU;
    const center = polar(cx, cy, orbitRadius, angle);
    const operation = params.operation ?? "mixed";
    const reflection = operation === "reflect" || (operation === "mixed" && index % 3 === 1);
    const scale = operation === "scale" || operation === "mixed"
      ? 0.48 + 0.18 * Math.sin(index * 1.7 + t * TAU * 0.35)
      : 0.58;
    drawSeed(ctx, t, {
      x: center.x,
      y: center.y,
      radius: params.seedRadius ?? 38,
      scale,
      rotation: operation === "rotate" || operation === "mixed" ? angle + t * 0.18 : 0,
      reflectX: reflection,
      color: index === 0 ? c.luminous : c.secondary,
      fillAlpha: 0.025,
      glow: index === 0 ? 5 : 2,
      alpha: alpha * (0.65 + 0.25 * pulse(t, 0.45, index / count)),
    }, env);
  }
  drawRing(ctx, cx, cy, orbitRadius, c.structure, 0.18 * alpha, 0.8);
  drawGlowOrb(ctx, cx, cy, 17, c.luminous, 0.65 * alpha);
}

function carrierShell(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.82);
  const kind = params.kind ?? "vessel";
  const points = carrierGeometry(kind, {
    cx: params.x ?? params.cx ?? 640,
    cy: params.y ?? params.cy ?? 310,
    size: params.size ?? 110,
    phase: t * 0.65,
  });
  const closed = ["vessel", "lattice"].includes(kind);
  strokePath(ctx, points, {
    color: params.color ?? c.carrier,
    width: params.width ?? 1.6,
    alpha,
    closed,
    dash: (params.integrity ?? 0.85) < 0.45 ? [6, 5] : [],
    glow: 3,
  });
}

function causalTrace(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.82);
  const values = params.values ?? [0.08, 0.82, 0.25, 0.94, 0.18];
  const series = causalTraceSeries(values, params.tau ?? 0.55, params.samples ?? 36, values[0]);
  const left = params.left ?? 260;
  const top = params.top ?? 340;
  const width = params.width ?? 760;
  const height = params.height ?? 190;
  const targetPoints = series.map((sample) => ({
    x: left + sample.t * width,
    y: top - sample.target * height,
  }));
  const tracePoints = series.map((sample) => ({
    x: left + sample.t * width,
    y: top - sample.trace * height,
  }));
  strokePath(ctx, targetPoints, { color: c.secondary, width: 1.2, alpha: 0.42 * alpha });
  strokePath(ctx, tracePoints, { color: c.trace, width: 2.6, alpha, glow: 5 });
  const cursor = Math.min(series.length - 1, Math.floor(t * (series.length - 1)));
  const target = targetPoints[cursor];
  const memory = tracePoints[cursor];
  line(ctx, target, memory, c.luminous, 0.55 * alpha, 1, [3, 4]);
  drawNode(ctx, target.x, target.y, 5, {
    fill: env.theme.backgroundLight, stroke: c.secondary, alpha,
  });
  drawGlowOrb(ctx, memory.x, memory.y, 8, c.trace, 0.62 * alpha);
}

function trajectoryRibbon(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.86);
  const keys = params.values ?? [0.08, 0.72, 0.46, 0.91, 0.28, 0.74];
  const trajectory = sampleTrajectory(keys, 140);
  const left = params.left ?? 220;
  const top = params.top ?? 360;
  const width = params.width ?? 840;
  const height = params.height ?? 210;
  const maximumVelocity = Math.max(...trajectory.map((sample) => Math.abs(sample.velocity)), 1e-9);
  const maximumAcceleration = Math.max(...trajectory.map((sample) => Math.abs(sample.acceleration)), 1e-9);
  const upper = trajectory.map((sample) => ({
    x: left + sample.t * width,
    y: top - sample.value * height - 12 * Math.abs(sample.velocity) / maximumVelocity,
  }));
  const lower = trajectory.map((sample) => ({
    x: left + sample.t * width,
    y: top - sample.value * height + 12 * Math.abs(sample.velocity) / maximumVelocity,
  }));
  const ribbon = [...upper, ...lower.reverse()];
  fillPath(ctx, ribbon, { color: rgba(c.secondary, 0.1), alpha });
  strokePath(ctx, upper, { color: c.secondary, width: 1.6, alpha });
  const current = hermiteScalar(keys, t);
  const currentX = left + t * width;
  const currentY = top - current.value * height;
  const velocityAmount = clamp(Math.abs(current.velocity) / maximumVelocity);
  const accelerationAmount = clamp(Math.abs(current.acceleration) / maximumAcceleration);
  drawGlowOrb(ctx, currentX, currentY, 7 + 8 * velocityAmount, c.luminous, 0.7 * alpha);
  drawArrowHead(
    ctx,
    currentX + Math.sign(current.velocity || 1) * 44,
    currentY - current.velocity * 12,
    current.velocity >= 0 ? -Math.PI / 6 : Math.PI + Math.PI / 6,
    11 + 6 * accelerationAmount,
    current.acceleration >= 0 ? c.accent : c.secondary,
    alpha,
  );
}

function leadLagLanes(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.85);
  const lanes = params.lanes ?? ["music proposes", "visual complicates", "narration reorients", "audience completes"];
  const offsets = [
    -(params.musicLead ?? 0.12),
    0,
    params.semanticLag ?? 0.14,
    (params.semanticLag ?? 0.14) + 0.12,
  ];
  const laneColors = [c.lead, c.carrier, c.lag, c.luminous];
  const left = 220;
  const right = 1060;
  lanes.forEach((label, index) => {
    const y = 190 + index * 92;
    line(ctx, { x: left, y }, { x: right, y }, c.structure, 0.18 * alpha, 0.8);
    const local = clamp(t - offsets[index]);
    const x = lerp(left, right, easeInOutCubic(local));
    drawGlowOrb(ctx, x, y, 7 + index * 1.2, laneColors[index], 0.72 * alpha);
    drawLabel(ctx, label, 150, y, {
      color: laneColors[index],
      size: 13,
      alpha: 0.82 * alpha,
      align: "left",
    });
  });
}

function invariantGauge(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.85);
  const score = clamp(params.score ?? 0.95);
  const threshold = clamp(params.threshold ?? 0.78);
  const cx = params.x ?? 640;
  const cy = params.y ?? 310;
  const radius = params.radius ?? 105;
  const start = Math.PI * 0.78;
  const span = Math.PI * 1.44;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.lineCap = "round";
  ctx.strokeStyle = rgba(c.structure, 0.25);
  ctx.lineWidth = 12;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, start, start + span);
  ctx.stroke();
  ctx.strokeStyle = score >= threshold ? c.luminous : c.breaking;
  ctx.lineWidth = 7;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, start, start + span * score);
  ctx.stroke();
  const thresholdPoint = polar(cx, cy, radius, start + span * threshold);
  drawNode(ctx, thresholdPoint.x, thresholdPoint.y, 4.5, {
    fill: env.theme.backgroundLight,
    stroke: c.structure,
    alpha,
  });
  ctx.restore();
  drawLabel(ctx, `${Math.round(score * 100)}% preserved`, cx, cy + 3, {
    color: score >= threshold ? c.luminous : c.breaking,
    size: 17,
    alpha,
  });
}

function topologyThreadAsset(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.78);
  const graph = topologyThread({
    cx: params.x ?? 640,
    cy: params.y ?? 310,
    radius: params.radius ?? 230,
    nodes: Math.max(3, Math.min(20, Math.round(params.nodes ?? 8))),
    branching: clamp(params.branching ?? 0.35),
    phase: t * TAU * 0.18,
  });
  const byId = new Map(graph.nodes.map((node) => [node.id, node]));
  for (const [leftId, rightId] of graph.edges) {
    line(ctx, byId.get(leftId), byId.get(rightId), c.secondary, 0.52 * alpha, 1.2);
  }
  graph.nodes.forEach((node, index) => drawNode(ctx, node.x, node.y, index % 3 === 0 ? 5 : 3.2, {
    fill: env.theme.backgroundLight,
    stroke: index % 3 === 0 ? c.luminous : c.secondary,
    alpha,
  }));
}

function verbGeometry(verb, cx, cy, size, t) {
  const progress = easeInOutCubic(t);
  switch (verb) {
    case "fracture":
      return [
        [{ x: cx - size, y: cy - size * 0.3 }, { x: cx - 10 - progress * 36, y: cy }],
        [{ x: cx + 10 + progress * 36, y: cy }, { x: cx + size, y: cy + size * 0.3 }],
      ];
    case "invert":
      return [[
        { x: cx - size, y: cy + size * (0.7 - progress * 1.4) },
        { x: cx, y: cy },
        { x: cx + size, y: cy - size * (0.7 - progress * 1.4) },
      ]];
    case "entrain":
      return Array.from({ length: 4 }, (_, lane) => Array.from({ length: 48 }, (_, index) => {
        const p = index / 47;
        const phase = lerp(lane * 0.7, 0, progress);
        return {
          x: cx - size + p * size * 2,
          y: cy + (lane - 1.5) * 28 + Math.sin(p * TAU * 2 + phase) * 15,
        };
      }));
    case "unbind":
      return Array.from({ length: 5 }, (_, index) => {
        const angle = (index / 5) * TAU;
        return [
          { x: cx, y: cy },
          polar(cx, cy, size * progress, angle),
        ];
      });
    case "condense":
      return Array.from({ length: 7 }, (_, index) => {
        const angle = (index / 7) * TAU;
        return [
          polar(cx, cy, size, angle),
          polar(cx, cy, lerp(size, size * 0.18, progress), angle),
        ];
      });
    case "remember":
      return [
        Array.from({ length: 64 }, (_, index) => {
          const p = index / 63;
          return {
            x: cx - size + p * size * 2,
            y: cy + Math.sin(p * TAU * 2) * size * 0.28 * (1 - progress),
          };
        }),
        Array.from({ length: 64 }, (_, index) => {
          const p = index / 63;
          return {
            x: cx - size + p * size * 2,
            y: cy + Math.sin(p * TAU * 2) * size * 0.28,
          };
        }),
      ];
    case "germinate":
    default:
      return Array.from({ length: 5 }, (_, index) => {
        const angle = -Math.PI / 2 + (index / 5) * TAU;
        return [
          { x: cx, y: cy },
          polar(cx, cy, size * progress, angle),
        ];
      });
  }
}

function semanticVerbMark(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.86);
  const verb = params.verb ?? "germinate";
  const paths = verbGeometry(
    verb,
    params.x ?? 640,
    params.y ?? 310,
    params.size ?? 120,
    t,
  );
  paths.forEach((points, index) => strokePath(ctx, points, {
    color: index % 2 ? c.secondary : c.accent,
    width: 1.5 + index * 0.15,
    alpha,
    glow: 4,
  }));
  drawLabel(ctx, verb, params.x ?? 640, (params.y ?? 310) + 160, {
    color: c.structure,
    size: 14,
    alpha: 0.75 * alpha,
  });
}

function attentionBudget(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.84);
  const values = clampArray([
    params.visual ?? 0.55,
    params.music ?? 0.75,
    params.narration ?? 0.25,
  ]);
  const labels = ["visual", "music", "narration"];
  const laneColors = [c.carrier, c.lead, c.lag];
  const budget = Math.max(1, values.reduce((sum, value) => sum + value, 0));
  values.forEach((value, index) => {
    const y = 220 + index * 105;
    const normalized = value / budget;
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.fillStyle = rgba(c.structure, 0.08);
    ctx.fillRect(330, y - 13, 620, 26);
    ctx.fillStyle = rgba(laneColors[index], 0.42);
    ctx.fillRect(330, y - 13, 620 * clamp(normalized * 1.8), 26);
    ctx.restore();
    drawLabel(ctx, labels[index], 250, y, {
      color: laneColors[index], size: 14, alpha, align: "right",
    });
  });
  const overload = clamp((budget - 1.7) / 1.3);
  drawLabel(ctx, overload > 0.05 ? "competition for attention" : "organized counterpoint", 640, 510, {
    color: overload > 0.05 ? c.breaking : c.luminous,
    size: 15,
    alpha,
  });
}

function recognitionField(ctx, t, params, env) {
  const c = colors(env.theme);
  const alpha = reveal(t) * (params.alpha ?? 0.85);
  const weight = clamp(params.relationalWeight ?? t);
  const cx = params.x ?? 640;
  const cy = params.y ?? 300;
  const materialRadius = lerp(175, 75, weight);
  const relationRadius = lerp(35, 165, weight);
  drawEllipseRing(ctx, cx, cy, materialRadius, materialRadius * 0.64, c.carrier, 0.35 * (1 - weight) * alpha, 1.4);
  drawRing(ctx, cx, cy, relationRadius, c.luminous, 0.62 * weight * alpha, 1.8);
  for (let index = 0; index < 5; index += 1) {
    const point = polar(cx, cy, relationRadius, -Math.PI / 2 + (index / 5) * TAU);
    drawGlowOrb(ctx, point.x, point.y, 5 + 3 * weight, c.luminous, 0.42 * weight * alpha);
  }
}

export const assetImplementations = Object.freeze({
  "continuity-seed": continuitySeed,
  "relational-signature": relationalSignature,
  "transformation-orbit": transformationOrbit,
  "carrier-shell": carrierShell,
  "causal-trace": causalTrace,
  "trajectory-ribbon": trajectoryRibbon,
  "lead-lag-lanes": leadLagLanes,
  "invariant-gauge": invariantGauge,
  "topology-thread": topologyThreadAsset,
  "semantic-verb-mark": semanticVerbMark,
  "attention-budget": attentionBudget,
  "recognition-field": recognitionField,
});

function title(ctx, text, c, alpha = 1) {
  drawLabel(ctx, text, 640, 112, {
    color: c.ink,
    size: 17,
    alpha: 0.82 * alpha,
  });
}

function transformationInvariance(ctx, t, scene, env) {
  const c = colors(env.theme);
  const alpha = reveal(t);
  const operation = scene.params?.operation ?? "mixed";
  const lobes = Math.max(3, Math.min(12, Math.round(scene.params?.lobes ?? 5)));
  const base = lobedContour({ radius: 72, lobes, harmonic: 0.22, samples: 160 });
  let transform;
  if (operation === "rotation") {
    transform = { rotation: t * TAU * 0.78, scale: 1, tx: 820, ty: 305 };
  } else if (operation === "scale") {
    transform = { rotation: 0, scale: 0.48 + t * 1.05, tx: 820, ty: 305 };
  } else if (operation === "reflection") {
    transform = { rotation: t * 0.25, scale: 1, reflectX: t > 0.5, tx: 820, ty: 305 };
  } else {
    transform = {
      rotation: t * TAU * 0.62,
      scale: 0.62 + 0.65 * pulse(t, 0.55),
      reflectX: t > 0.58,
      tx: 820,
      ty: 305,
    };
  }
  const left = transformPoints(base, { tx: 420, ty: 305 });
  const right = transformPoints(base, transform);
  strokePath(ctx, left, { color: c.secondary, width: 1.8, alpha, closed: true, glow: 4 });
  strokePath(ctx, right, { color: c.accent, width: 2.1, alpha, closed: true, glow: 5 });
  const baseSignature = pairwiseDistanceSignature(left);
  const transformedSignature = pairwiseDistanceSignature(right);
  const similarity = normalizedSimilarity(baseSignature, transformedSignature, 0.25);
  relationalSignature(ctx, t, {
    x: 640, y: 300, radius: 42, radialScale: 16,
    values: baseSignature.slice(0, 8),
    alpha: 0.72,
  }, env);
  invariantGauge(ctx, t, {
    x: 640, y: 455, radius: 56, score: similarity, threshold: 0.82,
  }, env);
  title(ctx, "appearance changes · relation persists", c, alpha);
}

function carrierTransfer(ctx, t, scene, env) {
  const c = colors(env.theme);
  const alpha = reveal(t);
  const carriers = Math.max(2, Math.min(6, Math.round(scene.params?.carriers ?? 4)));
  const fidelity = clamp(scene.params?.fidelity ?? 0.88);
  const kinds = ["vessel", "lattice", "ribbon", "wave", "branch", "vessel"];
  const left = 235;
  const span = 810;
  for (let index = 0; index < carriers; index += 1) {
    const x = left + (index / Math.max(1, carriers - 1)) * span;
    const local = clamp((t - index * 0.11) / 0.52);
    const outgoing = 1 - smoothstep(0.7, 1, local);
    carrierShell(ctx, local, {
      x, y: 310, size: 74, kind: kinds[index], alpha: alpha * outgoing,
      integrity: 0.55 + fidelity * 0.4,
    }, env);
    drawSeed(ctx, local, {
      x, y: 310, radius: 26, scale: 0.62 + fidelity * 0.28,
      rotation: index * 0.42 + t * 0.12,
      color: c.luminous,
      alpha: alpha * smoothstep(0.12, 0.42, local),
      fillAlpha: 0.035,
    }, env);
    if (index < carriers - 1) {
      const nextX = left + ((index + 1) / Math.max(1, carriers - 1)) * span;
      const transfer = clamp((t - index / carriers) * carriers);
      drawPartialPath(
        ctx,
        [{ x: x + 80, y: 310 }, { x: nextX - 80, y: 310 }],
        easeOutCubic(transfer),
        c.luminous,
        1.4,
        0.45 * alpha,
        { blur: 5 },
      );
      const pulsePoint = pointAlong(
        [{ x: x + 80, y: 310 }, { x: nextX - 80, y: 310 }],
        transfer,
      );
      drawGlowOrb(ctx, pulsePoint.x, pulsePoint.y, 6, c.luminous, 0.6 * alpha);
    }
  }
  title(ctx, "no carrier remains · the relation migrates", c, alpha);
}

function causalMemoryMechanism(ctx, t, scene, env) {
  const c = colors(env.theme);
  const alpha = reveal(t);
  const path = scene.params?.path ?? "rise-fall";
  const values = path === "pulse-return"
    ? [0.08, 0.08, 0.92, 0.08, 0.08]
    : path === "hysteresis"
      ? [0.1, 0.85, 0.45, 0.85, 0.1]
      : [0.1, 0.9, 0.1];
  causalTrace(ctx, t, {
    values,
    tau: scene.params?.tau ?? 0.52,
    left: 230,
    top: 420,
    width: 820,
    height: 235,
  }, env);
  const series = causalTraceSeries(values, scene.params?.tau ?? 0.52, 180, values[0]);
  const current = series[Math.min(series.length - 1, Math.floor(t * (series.length - 1)))];
  drawLabel(ctx, `present ${current.target.toFixed(2)}`, 470, 500, {
    color: c.secondary, size: 14, alpha,
  });
  drawLabel(ctx, `trace ${current.trace.toFixed(2)}`, 810, 500, {
    color: c.trace, size: 14, alpha,
  });
  title(ctx, "the present retains the path by which it arrived", c, alpha);
}

function derivativeTrajectoryMechanism(ctx, t, scene, env) {
  const c = colors(env.theme);
  const profile = scene.params?.profile ?? "overshoot";
  const profiles = {
    accelerate: [0.08, 0.12, 0.3, 0.72, 0.95],
    decelerate: [0.05, 0.48, 0.74, 0.86, 0.92],
    oscillate: [0.2, 0.86, 0.24, 0.78, 0.36, 0.65],
    overshoot: [0.12, 0.56, 1, 0.58, 0.72],
  };
  trajectoryRibbon(ctx, t, {
    values: profiles[profile],
    left: 220,
    top: 430,
    width: 840,
    height: 250,
  }, env);
  const state = hermiteScalar(profiles[profile], t);
  drawLabel(ctx, `value ${state.value.toFixed(2)}`, 370, 505, { color: c.structure, size: 13, alpha: reveal(t) });
  drawLabel(ctx, `velocity ${state.velocity.toFixed(2)}`, 640, 505, { color: c.secondary, size: 13, alpha: reveal(t) });
  drawLabel(ctx, `acceleration ${state.acceleration.toFixed(2)}`, 910, 505, { color: c.accent, size: 13, alpha: reveal(t) });
  title(ctx, "equal values can carry opposite futures", c, reveal(t));
}

function leadLagCounterpoint(ctx, t, scene, env) {
  const c = colors(env.theme);
  leadLagLanes(ctx, t, {
    musicLead: scene.params?.musicLead ?? 0.12,
    semanticLag: scene.params?.semanticLag ?? 0.16,
  }, env);
  const event = clamp(t * 1.25);
  const positions = [
    clamp(event + (scene.params?.musicLead ?? 0.12)),
    event,
    clamp(event - (scene.params?.semanticLag ?? 0.16)),
  ];
  const center = 640;
  positions.forEach((position, index) => {
    drawRing(
      ctx,
      center,
      300,
      45 + position * 170,
      [c.lead, c.carrier, c.lag][index],
      0.12 * reveal(t),
      1,
    );
  });
  title(ctx, "coordination does not require simultaneity", c, reveal(t));
}

function conservationFilter(ctx, t, scene, env) {
  const c = colors(env.theme);
  const alpha = reveal(t);
  const strictness = clamp(scene.params?.strictness ?? 0.78);
  const candidates = [
    { x: 250, transform: { rotation: t * 0.6, scale: 0.68 }, pass: true },
    { x: 430, transform: { rotation: -t * 0.5, scale: 1.08 }, pass: true },
    { x: 610, transform: { reflectX: true, rotation: t * 0.25, scale: 0.82 }, pass: true },
    { x: 790, transform: { rotation: t * 0.8, scale: 0.58 }, pass: true },
    { x: 970, transform: null, pass: false },
  ];
  const gateX = 730;
  candidates.forEach((candidate, index) => {
    const travel = easeInOutCubic(clamp((t - index * 0.055) / 0.72));
    const x = lerp(candidate.x, candidate.pass ? 1000 : gateX - 35, travel);
    if (candidate.pass) {
      drawSeed(ctx, t, {
        x, y: 310, radius: 32,
        rotation: candidate.transform.rotation ?? 0,
        scale: candidate.transform.scale ?? 1,
        reflectX: candidate.transform.reflectX ?? false,
        color: c.luminous,
        alpha,
        fillAlpha: 0.025,
      }, env);
    } else {
      const unrelated = lobedContour({
        cx: x, cy: 310, radius: 34, lobes: 7, harmonic: 0.42, samples: 100,
      });
      strokePath(ctx, unrelated, {
        color: c.breaking, width: 1.8, alpha: alpha * (1 - smoothstep(0.65, 0.9, t)),
        closed: true, dash: [4, 4],
      });
    }
  });
  line(ctx, { x: gateX, y: 165 }, { x: gateX, y: 455 }, c.structure, 0.58 * alpha, 2);
  drawLabel(ctx, `invariant threshold ${strictness.toFixed(2)}`, gateX, 485, {
    color: c.structure, size: 13, alpha,
  });
  drawLabel(ctx, "forbidden substitution", 970, 390, {
    color: c.breaking, size: 12, alpha: alpha * (1 - smoothstep(0.72, 0.96, t)),
  });
  title(ctx, "continuity is governed by laws, not resemblance alone", c, alpha);
}

function semanticTransitionMechanism(ctx, t, scene, env) {
  const c = colors(env.theme);
  const alpha = reveal(t);
  const verb = scene.params?.verb ?? "germinate";
  drawSeed(ctx, 1 - smoothstep(0.32, 0.75, t), {
    x: 330, y: 310, radius: 62, color: c.secondary, alpha,
  }, env);
  semanticVerbMark(ctx, t, {
    verb, x: 640, y: 310, size: 120, alpha,
  }, env);
  const destination = {
    germinate: { kind: "branch", x: 950 },
    fracture: { kind: "lattice", x: 950 },
    invert: { kind: "wave", x: 950 },
    entrain: { kind: "ribbon", x: 950 },
    unbind: { kind: "lattice", x: 950 },
    condense: { kind: "vessel", x: 950 },
    remember: { kind: "wave", x: 950 },
  }[verb] ?? { kind: "vessel", x: 950 };
  carrierShell(ctx, smoothstep(0.35, 0.85, t), {
    kind: destination.kind, x: destination.x, y: 310, size: 90,
    color: c.accent, alpha,
  }, env);
  drawArrowHead(ctx, 805, 310, 0, 12, c.luminous, 0.7 * alpha);
  title(ctx, `the next state is produced by: ${verb}`, c, alpha);
}

function polyphonicIdentity(ctx, t, scene, env) {
  const c = colors(env.theme);
  const alpha = reveal(t);
  const voices = Math.max(2, Math.min(8, Math.round(scene.params?.voices ?? 5)));
  const entrySpread = clamp(scene.params?.entrySpread ?? 0.34);
  const voiceColors = [c.secondary, c.accent, c.carrier, c.trace, c.luminous, c.field];
  for (let index = 0; index < voices; index += 1) {
    const entry = index * entrySpread / Math.max(1, voices - 1);
    const local = clamp((t - entry) / Math.max(0.01, 1 - entry));
    const x = 250 + (index / Math.max(1, voices - 1)) * 780;
    const y = 310 + Math.sin(index * 1.6 + t * TAU * 0.42) * 105;
    drawSeed(ctx, local, {
      x, y,
      radius: 42,
      rotation: local * (index % 2 ? -0.8 : 0.8) + index * 0.3,
      scale: 0.65 + index * 0.055,
      reflectX: index % 3 === 2,
      color: voiceColors[index % voiceColors.length],
      fillAlpha: 0.02,
      alpha: alpha * smoothstep(0, 0.18, local),
      glow: index === voices - 1 ? 5 : 2,
    }, env);
    if (index > 0) {
      line(ctx, { x: x - 90, y: 310 }, { x, y }, c.structure, 0.12 * alpha, 0.8);
    }
  }
  title(ctx, "one subject · several independent agencies", c, alpha);
}

function recognitionTransaction(ctx, t, scene, env) {
  const c = colors(env.theme);
  const alpha = reveal(t);
  const recognitionTime = clamp(scene.params?.recognitionTime ?? 0.68);
  const recognition = smoothstep(recognitionTime - 0.16, recognitionTime + 0.08, t);
  const centers = [
    { x: 350, y: 280, kind: "vessel", rotation: 0.1 },
    { x: 640, y: 330, kind: "wave", rotation: 0.7 },
    { x: 930, y: 270, kind: "lattice", rotation: -0.4 },
  ];
  centers.forEach((item, index) => {
    carrierShell(ctx, t, {
      kind: item.kind, x: item.x, y: item.y, size: 85,
      alpha: alpha * lerp(0.85, 0.16, recognition),
    }, env);
    drawSeed(ctx, t, {
      x: item.x, y: item.y, radius: 34,
      rotation: item.rotation + t * (index % 2 ? -0.3 : 0.3),
      reflectX: index === 2,
      scale: [0.7, 1.15, 0.85][index],
      color: c.luminous,
      alpha,
      fillAlpha: lerp(0.02, 0.08, recognition),
      glow: lerp(2, 7, recognition),
    }, env);
  });
  recognitionField(ctx, t, {
    x: 640, y: 310, relationalWeight: recognition, alpha,
  }, env);
  if (recognition > 0.55) {
    relationalSignature(ctx, recognition, {
      x: 640, y: 310, radius: 96, radialScale: 18,
      values: [0.2, 0.9, 0.42, 0.76, 0.55],
      alpha: recognition,
    }, env);
  }
  title(ctx, recognition < 0.5 ? "first: follow the changing carriers" : "then: recognize what never depended on them", c, alpha);
}

function climaxAssimilation(ctx, t, scene, env) {
  const c = colors(env.theme);
  const alpha = reveal(t);
  const climaxTime = clamp(scene.params?.climaxTime ?? 0.58);
  const afterlife = clamp(scene.params?.afterlife ?? 0.72);
  const distance = Math.abs(t - climaxTime);
  const peak = Math.exp(-(distance ** 2) / 0.0045);
  const assimilation = smoothstep(climaxTime, 1, t);
  const worldRadius = 90 + 210 * peak + 105 * assimilation * afterlife;
  for (let ring = 0; ring < 6; ring += 1) {
    drawRing(
      ctx,
      640,
      310,
      worldRadius + ring * 22,
      ring % 2 ? c.secondary : c.luminous,
      alpha * (0.1 + 0.25 * peak + 0.08 * assimilation) * (1 - ring * 0.08),
      ring === 0 ? 2.2 : 1,
    );
  }
  const multiplicity = 5;
  for (let index = 0; index < multiplicity; index += 1) {
    const angle = -Math.PI / 2 + (index / multiplicity) * TAU + t * 0.08;
    const radius = lerp(0, 155, smoothstep(climaxTime - 0.1, climaxTime + 0.16, t));
    const point = polar(640, 310, radius, angle);
    drawSeed(ctx, t, {
      x: point.x, y: point.y, radius: 31 + peak * 18,
      rotation: angle + t * 0.2,
      color: c.luminous,
      alpha,
      fillAlpha: 0.025 + peak * 0.07,
      glow: 3 + peak * 8,
    }, env);
  }
  const persistent = lerp(1, afterlife, assimilation);
  relationalSignature(ctx, t, {
    x: 640, y: 310, radius: 54 + assimilation * 42,
    radialScale: 15,
    values: [0.2, 0.9, 0.42, 0.76, 0.55],
    alpha: persistent,
  }, env);
  title(ctx, peak > 0.45 ? "climax: the invariant becomes undeniable" : assimilation > 0.1 ? "assimilation: intensity recedes, relation remains" : "preparation", c, alpha);
}

function structuralHomology(ctx, t, scene, env) {
  const c = colors(env.theme);
  const alpha = reveal(t);
  const relation = scene.params?.relation ?? "invariance";
  const lanes = [
    { label: "argument", y: 205, color: c.structure },
    { label: "music", y: 310, color: c.lead },
    { label: "image", y: 415, color: c.carrier },
  ];
  const left = 270;
  const right = 1010;
  lanes.forEach((lane, index) => {
    drawLabel(ctx, lane.label, 190, lane.y, {
      color: lane.color, size: 14, alpha, align: "right",
    });
    if (relation === "feedback") {
      drawEllipseRing(ctx, 640, lane.y, 210, 38, lane.color, 0.5 * alpha, 1.4, 0);
      const point = polar(640, lane.y, 210, t * TAU + index * 0.6);
      drawGlowOrb(ctx, point.x, point.y, 6, lane.color, 0.65 * alpha);
    } else if (relation === "transfer") {
      const progress = easeInOutCubic(clamp(t - index * 0.08));
      line(ctx, { x: left, y: lane.y }, { x: right, y: lane.y }, lane.color, 0.3 * alpha, 1);
      const x = lerp(left, right, progress);
      drawGlowOrb(ctx, x, lane.y, 8, lane.color, 0.72 * alpha);
    } else if (relation === "constraint") {
      line(ctx, { x: left, y: lane.y }, { x: right, y: lane.y }, lane.color, 0.25 * alpha, 1);
      const gate = lerp(left + 150, right - 100, index / 2);
      line(ctx, { x: gate, y: lane.y - 34 }, { x: gate, y: lane.y + 34 }, c.structure, 0.55 * alpha, 1.5);
      const x = Math.min(gate - 8, lerp(left, right, t));
      drawGlowOrb(ctx, x, lane.y, 7, lane.color, 0.7 * alpha);
    } else if (relation === "emergence") {
      for (let node = 0; node < 7; node += 1) {
        const start = { x: left + node * 95, y: lane.y + (node % 2 ? 18 : -18) };
        const end = { x: 640, y: lane.y };
        const amount = smoothstep(node * 0.02, 0.68 + node * 0.02, t);
        const point = {
          x: lerp(start.x, end.x, amount),
          y: lerp(start.y, end.y, amount),
        };
        drawNode(ctx, point.x, point.y, 3.5, {
          fill: env.theme.backgroundLight, stroke: lane.color, alpha,
        });
      }
    } else {
      const x = lerp(left, right, easeInOutCubic(t));
      drawSeed(ctx, t, {
        x, y: lane.y, radius: 29 + index * 4,
        rotation: t * (index + 1) * 0.4,
        reflectX: index === 2 && t > 0.5,
        color: lane.color,
        alpha,
        fillAlpha: 0.018,
        glow: 2,
      }, env);
    }
  });
  title(ctx, "same causal law · different material language", c, alpha);
}

function constraintTournament(ctx, t, scene, env) {
  const c = colors(env.theme);
  const alpha = reveal(t);
  const candidateCount = Math.max(3, Math.min(7, Math.round(scene.params?.candidates ?? 5)));
  const gateCount = Math.max(2, Math.min(5, Math.round(scene.params?.gates ?? 3)));
  const rand = seeded((scene.seed ?? env.seed ?? 2607) ^ hashString(scene.id));
  const candidates = Array.from({ length: candidateCount }, (_, index) => ({
    index,
    score: [
      0.35 + rand(0, 0.6),
      0.35 + rand(0, 0.6),
      0.35 + rand(0, 0.6),
    ],
  }));
  candidates[candidateCount - 1].score = [0.92, 0.9, 0.94];
  const gateLabels = ["causal necessity", "continuity", "epistemic restraint", "silent legibility", "novelty"];
  const left = 220;
  const right = 1050;
  const gateXs = Array.from({ length: gateCount }, (_, index) => (
    lerp(430, 870, index / Math.max(1, gateCount - 1))
  ));
  gateXs.forEach((x, index) => {
    line(ctx, { x, y: 150 }, { x, y: 470 }, c.structure, 0.34 * alpha, 1.2);
    drawLabel(ctx, gateLabels[index], x, 500, {
      color: c.structure, size: 11, alpha: 0.7 * alpha,
    });
  });
  candidates.forEach((candidate, index) => {
    const y = 180 + index * (270 / Math.max(1, candidateCount - 1));
    let passed = true;
    let stopX = right;
    for (let gate = 0; gate < gateCount; gate += 1) {
      const score = candidate.score[gate % candidate.score.length];
      if (score < 0.62 + gate * 0.03) {
        passed = false;
        stopX = gateXs[gate] - 18;
        break;
      }
    }
    const progress = easeInOutCubic(t);
    const x = lerp(left, stopX, progress);
    const fade = passed ? 1 : 1 - smoothstep(0.66, 0.95, t);
    drawSeed(ctx, t, {
      x, y, radius: 23 + index,
      lobes: passed ? 5 : 4 + (index % 4),
      harmonic: passed ? 0.22 : 0.1 + index * 0.06,
      color: passed ? c.luminous : c.secondary,
      alpha: alpha * fade,
      fillAlpha: passed ? 0.05 : 0.015,
      glow: passed ? 5 : 1,
    }, env);
    if (!passed && t > 0.72) {
      drawLabel(ctx, `fails gate ${gateXs.findIndex((gateX) => gateX > stopX) + 1}`, stopX - 10, y + 28, {
        color: c.breaking, size: 10, alpha: alpha * fade,
      });
    }
  });
  title(ctx, "quality is the survival of necessary decisions", c, alpha);
}

export const mechanismImplementations = Object.freeze({
  "transformation-invariance": transformationInvariance,
  "carrier-transfer": carrierTransfer,
  "causal-memory": causalMemoryMechanism,
  "derivative-trajectory": derivativeTrajectoryMechanism,
  "lead-lag-counterpoint": leadLagCounterpoint,
  "conservation-filter": conservationFilter,
  "semantic-transition": semanticTransitionMechanism,
  "polyphonic-identity": polyphonicIdentity,
  "recognition-transaction": recognitionTransaction,
  "climax-assimilation": climaxAssimilation,
  "structural-homology": structuralHomology,
  "constraint-tournament": constraintTournament,
});
