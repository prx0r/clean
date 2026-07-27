import {
  TAU,
  clamp,
  easeInOutCubic,
  easeOutCubic,
  rgba,
  smoothstep,
  wave,
} from "./math.mjs";
import {
  drawArrowHead,
  drawEllipseRing,
  drawGlowOrb,
  drawGlowingPath,
  drawLabel,
  drawNode,
  drawPartialPath,
  drawRing,
} from "./primitives.mjs";

function reveal(t) {
  return smoothstep(0.01, 0.11, t);
}

function ink(scene, theme) {
  return {
    blue: scene.palette?.secondary ?? theme.secondary,
    cyan: scene.palette?.accent ?? theme.accent,
    gold: scene.palette?.luminous ?? theme.luminous,
    line: theme.structure,
  };
}

function line(ctx, points, color, width = 1, alpha = 1, dash = []) {
  if (points.length < 2) return;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.setLineDash(dash);
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (const point of points.slice(1)) ctx.lineTo(point.x, point.y);
  ctx.stroke();
  ctx.restore();
}

function technicalAxes(ctx, options = {}) {
  const {
    x = 190,
    y = 470,
    width = 900,
    height = 310,
    color = "#45678f",
    alpha = 0.55,
    xLabel = "x",
    yLabel = "y",
  } = options;
  ctx.save();
  ctx.strokeStyle = rgba(color, alpha);
  ctx.fillStyle = rgba(color, alpha);
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(x, y - height);
  ctx.lineTo(x, y);
  ctx.lineTo(x + width, y);
  ctx.stroke();
  for (let index = 0; index <= 10; index += 1) {
    const px = x + index * width / 10;
    ctx.beginPath();
    ctx.moveTo(px, y - 4);
    ctx.lineTo(px, y + 4);
    ctx.stroke();
  }
  for (let index = 0; index <= 5; index += 1) {
    const py = y - index * height / 5;
    ctx.beginPath();
    ctx.moveTo(x - 4, py);
    ctx.lineTo(x + 4, py);
    ctx.stroke();
  }
  ctx.restore();
  drawLabel(ctx, xLabel, x + width + 24, y + 2, { color, size: 13, alpha });
  drawLabel(ctx, yLabel, x - 5, y - height - 22, { color, size: 13, alpha });
}

function technicalRatePlot(ctx, t, scene, env) {
  const { theme } = env;
  const { blue, cyan, gold, line: structure } = ink(scene, theme);
  const alpha = reveal(t);
  const x0 = 190;
  const y0 = 470;
  const width = 900;
  const height = 310;
  technicalAxes(ctx, {
    x: x0,
    y: y0,
    width,
    height,
    color: structure,
    xLabel: scene.params?.xLabel ?? "condition",
    yLabel: scene.params?.yLabel ?? "rate",
  });

  const curves = [
    { color: blue, gain: 0.92, exponent: 1.45 },
    { color: cyan, gain: 0.72, exponent: 0.82 },
    { color: gold, gain: 0.54, exponent: 2.2 },
  ];
  for (const [index, curve] of curves.entries()) {
    const points = [];
    for (let sample = 0; sample <= 120; sample += 1) {
      const x = sample / 120;
      const response = curve.gain * (1 - Math.exp(-3.5 * x ** curve.exponent));
      points.push({ x: x0 + x * width, y: y0 - response * height });
    }
    drawPartialPath(
      ctx,
      points,
      smoothstep(0.06 + index * 0.08, 0.55 + index * 0.08, t),
      curve.color,
      index === 0 ? 2.2 : 1.35,
      alpha * (index === 0 ? 0.9 : 0.62),
      { blur: index === 0 ? 6 : 3 },
    );
  }

  const cursor = easeInOutCubic(smoothstep(0.24, 0.92, t));
  const px = x0 + cursor * width;
  const response = curves[0].gain * (1 - Math.exp(-3.5 * cursor ** curves[0].exponent));
  const py = y0 - response * height;
  line(ctx, [{ x: px, y: y0 }, { x: px, y: py }], blue, 1, 0.45 * alpha, [5, 6]);
  line(ctx, [{ x: x0, y: py }, { x: px, y: py }], blue, 1, 0.45 * alpha, [5, 6]);
  drawGlowOrb(ctx, px, py, 8, cyan, 0.82 * alpha);
  drawLabel(ctx, scene.params?.equation ?? "response = f(condition)", 640, 112, {
    color: blue,
    size: 17,
    alpha: 0.82 * alpha,
  });
}

function evidenceLadder(ctx, t, scene, env) {
  const { theme } = env;
  const { blue, cyan, gold, line: structure } = ink(scene, theme);
  const alpha = reveal(t);
  const labels = scene.params?.labels ?? [
    "observation",
    "replication",
    "mechanism",
    "prediction",
    "convergence",
  ];
  const selected = clamp(scene.params?.selected ?? 3, 0, labels.length - 1);
  const x = 290;
  const width = 700;
  const baseY = 470;
  const step = 64;
  for (let index = 0; index < labels.length; index += 1) {
    const y = baseY - index * step;
    const arrive = smoothstep(index * 0.08, 0.24 + index * 0.08, t);
    const color = index <= selected ? (index === selected ? gold : blue) : structure;
    const barWidth = 230 + index * 105;
    ctx.save();
    ctx.globalAlpha = alpha * arrive * (index <= selected ? 0.17 : 0.06);
    ctx.fillStyle = color;
    ctx.fillRect(x, y - 36, barWidth, 42);
    ctx.globalAlpha = alpha * arrive * 0.82;
    ctx.strokeStyle = color;
    ctx.lineWidth = index === selected ? 2 : 1;
    ctx.strokeRect(x, y - 36, barWidth, 42);
    ctx.restore();
    drawNode(ctx, x + barWidth, y - 15, index === selected ? 7 : 4, {
      fill: theme.backgroundLight,
      stroke: color,
      alpha: alpha * arrive,
      glow: index === selected ? cyan : undefined,
    });
    drawLabel(ctx, labels[index], x + 18, y - 14, {
      color,
      size: 15,
      alpha: alpha * arrive,
      align: "left",
    });
  }
  drawLabel(ctx, scene.params?.caption ?? "confidence grows by independent constraints", 640, 105, {
    color: blue,
    size: 17,
    alpha: 0.82 * alpha,
  });
}

function phaseSpaceTrajectories(ctx, t, scene, env) {
  const { theme } = env;
  const { blue, cyan, gold, line: structure } = ink(scene, theme);
  const alpha = reveal(t);
  technicalAxes(ctx, {
    x: 205,
    y: 478,
    width: 860,
    height: 330,
    color: structure,
    xLabel: scene.params?.xLabel ?? "state A",
    yLabel: scene.params?.yLabel ?? "state B",
  });
  const cx = 635;
  const cy = 312;
  for (let gx = 0; gx < 12; gx += 1) {
    for (let gy = 0; gy < 6; gy += 1) {
      const x = 245 + gx * 72;
      const y = 175 + gy * 55;
      const angle = Math.atan2(cy - y, cx - x) + Math.PI / 2.8;
      const length = 10 + Math.hypot(cx - x, cy - y) * 0.018;
      line(ctx, [
        { x: x - Math.cos(angle) * length / 2, y: y - Math.sin(angle) * length / 2 },
        { x: x + Math.cos(angle) * length / 2, y: y + Math.sin(angle) * length / 2 },
      ], structure, 0.8, 0.2 * alpha);
    }
  }
  for (let track = 0; track < 5; track += 1) {
    const points = [];
    for (let sample = 0; sample <= 140; sample += 1) {
      const p = sample / 140;
      const radius = 280 * (1 - p) + 22 + track * 11;
      const angle = (2.1 + track * 0.23) * Math.PI * p + track * 0.8;
      points.push({
        x: cx + Math.cos(angle) * radius,
        y: cy + Math.sin(angle) * radius * 0.56,
      });
    }
    const color = [blue, cyan, gold][track % 3];
    drawPartialPath(ctx, points, smoothstep(0.08 + track * 0.04, 0.8, t), color, 1.35, 0.6 * alpha);
    const cursor = Math.min(points.length - 1, Math.floor(easeOutCubic(t) * (points.length - 1)));
    drawNode(ctx, points[cursor].x, points[cursor].y, 4, {
      fill: theme.backgroundLight,
      stroke: color,
      alpha,
      glow: color,
    });
  }
  drawRing(ctx, cx, cy, 18 + 3 * wave(t, 0.7), gold, 0.75 * alpha, 1.3);
  drawLabel(ctx, scene.params?.caption ?? "trajectories reveal the attractor", 640, 105, {
    color: blue,
    size: 17,
    alpha: 0.82 * alpha,
  });
}

function barrierTunnelling(ctx, t, scene, env) {
  const { theme } = env;
  const { blue, cyan, gold, line: structure } = ink(scene, theme);
  const alpha = reveal(t);
  const x0 = 150;
  const y0 = 420;
  const width = 980;
  const barrierLeft = 545;
  const barrierRight = 735;
  technicalAxes(ctx, { x: x0, y: y0, width, height: 250, color: structure, xLabel: "position", yLabel: "energy" });
  const top = 205;
  ctx.save();
  ctx.globalAlpha = 0.12 * alpha;
  ctx.fillStyle = blue;
  ctx.fillRect(barrierLeft, top, barrierRight - barrierLeft, y0 - top);
  ctx.globalAlpha = 0.72 * alpha;
  ctx.strokeStyle = blue;
  ctx.lineWidth = 1.5;
  ctx.strokeRect(barrierLeft, top, barrierRight - barrierLeft, y0 - top);
  ctx.restore();
  drawLabel(ctx, scene.params?.barrierLabel ?? "barrier", 640, 185, { color: blue, size: 14, alpha: 0.75 * alpha });

  const points = [];
  for (let sample = 0; sample <= 260; sample += 1) {
    const p = sample / 260;
    const x = x0 + p * width;
    let amplitude = 1;
    if (x >= barrierLeft && x <= barrierRight) {
      amplitude = Math.exp(-(x - barrierLeft) / 95);
    } else if (x > barrierRight) {
      amplitude = 0.18;
    }
    const distance = (x - (330 + 600 * t)) / 165;
    const envelope = Math.exp(-(distance ** 2));
    const y = 340 - Math.sin(x * 0.055 - t * TAU * 4) * 48 * amplitude * envelope;
    points.push({ x, y });
  }
  drawGlowingPath(ctx, points, cyan, 2, 0.78 * alpha, { blur: 6 });

  const classicalX = Math.min(barrierLeft - 12, 250 + 440 * easeOutCubic(t));
  drawNode(ctx, classicalX, 455, 6, {
    fill: theme.backgroundLight,
    stroke: gold,
    alpha: 0.88 * alpha,
  });
  drawLabel(ctx, "classical path stops", barrierLeft - 35, 490, {
    color: gold,
    size: 12,
    alpha: 0.72 * alpha,
  });
  const detection = smoothstep(0.66, 0.95, t);
  drawGlowOrb(ctx, 930, 340, 10 + 5 * wave(t, 1.2), cyan, detection * alpha);
  drawLabel(ctx, scene.params?.caption ?? "finite amplitude survives the forbidden region", 640, 105, {
    color: blue,
    size: 17,
    alpha: 0.82 * alpha,
  });
}

function energyLandscape(ctx, t, scene, env) {
  const { theme } = env;
  const { blue, cyan, gold, line: structure } = ink(scene, theme);
  const alpha = reveal(t);
  technicalAxes(ctx, { x: 170, y: 470, width: 940, height: 320, color: structure, xLabel: "configuration", yLabel: "energy" });
  const points = [];
  for (let sample = 0; sample <= 220; sample += 1) {
    const p = sample / 220;
    const q = p * 2 - 1;
    const energy = 0.18 + 0.72 * (q * q - 0.48) ** 2;
    points.push({ x: 170 + p * 940, y: 470 - energy * 330 });
  }
  drawPartialPath(ctx, points, smoothstep(0.03, 0.58, t), blue, 2, 0.86 * alpha, { blur: 5 });
  const transition = easeInOutCubic(smoothstep(0.2, 0.82, t));
  const p = 0.26 + transition * 0.48;
  const q = p * 2 - 1;
  const energy = 0.18 + 0.72 * (q * q - 0.48) ** 2;
  const px = 170 + p * 940;
  const py = 470 - energy * 330;
  drawGlowOrb(ctx, px, py, 12, transition > 0.45 ? cyan : gold, 0.9 * alpha);
  line(ctx, [{ x: 640, y: 240 }, { x: 640, y: 470 }], structure, 1, 0.32 * alpha, [5, 6]);
  drawLabel(ctx, scene.params?.leftLabel ?? "state A", 410, 455, { color: gold, size: 14, alpha: 0.75 * alpha });
  drawLabel(ctx, scene.params?.rightLabel ?? "state B", 870, 455, { color: cyan, size: 14, alpha: 0.75 * alpha });
  drawLabel(ctx, scene.params?.caption ?? "structure changes the route between stable states", 640, 105, {
    color: blue,
    size: 17,
    alpha: 0.82 * alpha,
  });
}

function molecularGate(ctx, t, scene, env) {
  const { theme } = env;
  const { blue, cyan, gold, line: structure } = ink(scene, theme);
  const alpha = reveal(t);
  const gateX = 640;
  ctx.save();
  ctx.globalAlpha = 0.22 * alpha;
  ctx.fillStyle = blue;
  ctx.fillRect(gateX - 34, 140, 68, 340);
  ctx.globalAlpha = 0.72 * alpha;
  ctx.strokeStyle = blue;
  ctx.lineWidth = 1.4;
  ctx.strokeRect(gateX - 34, 140, 68, 340);
  ctx.restore();
  for (let y = 158; y < 470; y += 31) {
    if (y > 270 && y < 345) continue;
    drawNode(ctx, gateX - 21, y, 4, { fill: theme.backgroundLight, stroke: blue, alpha: 0.7 * alpha });
    drawNode(ctx, gateX + 21, y, 4, { fill: theme.backgroundLight, stroke: blue, alpha: 0.7 * alpha });
  }
  drawLabel(ctx, scene.params?.gateLabel ?? "selective gate", gateX, 118, {
    color: blue,
    size: 14,
    alpha: 0.8 * alpha,
  });

  const particles = scene.params?.particles ?? 8;
  for (let index = 0; index < particles; index += 1) {
    const accepted = index % 3 !== 0;
    const phase = (t * 0.9 + index / particles) % 1;
    let x = 180 + phase * 920;
    let y = 245 + (index % 5) * 44;
    if (!accepted && x > gateX - 55) {
      x = gateX - 55 - Math.abs(x - (gateX - 55)) * 0.35;
      y += 18 * Math.sin(phase * TAU);
    }
    const color = accepted ? cyan : gold;
    drawGlowOrb(ctx, x, y, accepted ? 7 : 8, color, 0.68 * alpha);
    if (accepted && x > gateX + 40) {
      line(ctx, [{ x: gateX + 40, y }, { x, y }], cyan, 0.7, 0.18 * alpha);
    }
  }
  drawArrowHead(ctx, 930, 310, 0, 12, cyan, 0.62 * alpha);
  drawLabel(ctx, scene.params?.caption ?? "architecture selects which transitions remain possible", 640, 520, {
    color: structure,
    size: 15,
    alpha: 0.75 * alpha,
  });
}

function movingTimeWindow(ctx, t, scene, env) {
  const { theme } = env;
  const { blue, cyan, gold, line: structure } = ink(scene, theme);
  const alpha = reveal(t);
  const y = 310;
  line(ctx, [{ x: 145, y }, { x: 1135, y }], structure, 1.2, 0.56 * alpha);
  drawArrowHead(ctx, 1135, y, 0, 10, structure, 0.56 * alpha);
  const events = scene.params?.events ?? ["trace", "signal", "choice", "action", "revision", "next"];
  events.forEach((label, index) => {
    const x = 220 + index * 165;
    drawNode(ctx, x, y, 5, {
      fill: theme.backgroundLight,
      stroke: index % 2 ? cyan : blue,
      alpha: 0.72 * alpha,
    });
    drawLabel(ctx, label, x, y + 45, {
      color: structure,
      size: 12,
      alpha: 0.7 * alpha,
    });
  });
  const progress = easeInOutCubic(t);
  const nowX = 205 + progress * 825;
  const gradient = ctx.createLinearGradient(nowX - 115, 0, nowX + 115, 0);
  gradient.addColorStop(0, rgba(cyan, 0));
  gradient.addColorStop(0.5, rgba(cyan, 0.16 * alpha));
  gradient.addColorStop(1, rgba(cyan, 0));
  ctx.fillStyle = gradient;
  ctx.fillRect(nowX - 115, 145, 230, 290);
  ctx.save();
  ctx.globalAlpha = 0.85 * alpha;
  ctx.strokeStyle = cyan;
  ctx.lineWidth = 1.4;
  ctx.strokeRect(nowX - 74, 175, 148, 220);
  ctx.restore();
  drawLabel(ctx, scene.params?.windowLabel ?? "NOW", nowX, 155, {
    color: cyan,
    size: 14,
    alpha: 0.88 * alpha,
  });
  drawLabel(ctx, scene.params?.caption ?? "sequence is produced by a moving field of access", 640, 105, {
    color: blue,
    size: 17,
    alpha: 0.82 * alpha,
  });
}

function simultaneitySequence(ctx, t, scene, env) {
  const { theme } = env;
  const { blue, cyan, gold, line: structure } = ink(scene, theme);
  const alpha = reveal(t);
  const count = scene.params?.count ?? 12;
  const sequence = easeInOutCubic(smoothstep(0.28, 0.86, t));
  const nodes = [];
  for (let index = 0; index < count; index += 1) {
    const angle = (index / count) * TAU - Math.PI / 2;
    const field = {
      x: 640 + Math.cos(angle) * (245 + 30 * Math.sin(index * 2.4)),
      y: 300 + Math.sin(angle) * (155 + 18 * Math.cos(index * 1.8)),
    };
    const ordered = {
      x: 220 + index * (840 / (count - 1)),
      y: 305 + 50 * Math.sin(index * 0.9),
    };
    nodes.push({
      x: field.x + (ordered.x - field.x) * sequence,
      y: field.y + (ordered.y - field.y) * sequence,
    });
  }
  for (let index = 0; index < nodes.length - 1; index += 1) {
    line(ctx, [nodes[index], nodes[index + 1]], blue, 1.1, sequence * 0.55 * alpha);
  }
  nodes.forEach((node, index) => {
    const active = Math.floor(t * count * 1.25) % count === index;
    drawNode(ctx, node.x, node.y, active ? 7 : 4, {
      fill: theme.backgroundLight,
      stroke: active ? gold : (index % 2 ? cyan : blue),
      alpha,
      glow: active ? gold : undefined,
    });
  });
  if (sequence > 0.35) drawArrowHead(ctx, nodes.at(-1).x + 20, nodes.at(-1).y, 0, 10, blue, sequence * alpha);
  drawLabel(ctx, sequence < 0.5 ? "simultaneous field" : "ordered access", 640, 115, {
    color: sequence < 0.5 ? cyan : blue,
    size: 17,
    alpha: 0.82 * alpha,
  });
}

function branchingFuture(ctx, t, scene, env) {
  const { theme } = env;
  const { blue, cyan, gold, line: structure } = ink(scene, theme);
  const alpha = reveal(t);
  const root = { x: 255, y: 310 };
  const junctions = [
    { x: 500, y: 310 },
    { x: 735, y: 220 },
    { x: 735, y: 310 },
    { x: 735, y: 400 },
  ];
  drawPartialPath(ctx, [root, junctions[0]], smoothstep(0.02, 0.3, t), blue, 2, 0.8 * alpha);
  const branchReveal = smoothstep(0.2, 0.65, t);
  for (let index = 1; index < junctions.length; index += 1) {
    const endpoint = { x: 1040, y: 145 + (index - 1) * 165 };
    const selected = index === (scene.params?.selectedBranch ?? 2);
    const color = selected ? cyan : (index === 1 ? gold : structure);
    const branch = [
      junctions[0],
      junctions[index],
      endpoint,
    ];
    drawPartialPath(
      ctx,
      branch,
      branchReveal,
      color,
      selected ? 2.3 : 1.1,
      alpha * (selected ? 0.86 : 0.36),
      { blur: selected ? 7 : 2 },
    );
    drawNode(ctx, endpoint.x, endpoint.y, selected ? 7 : 4, {
      fill: theme.backgroundLight,
      stroke: color,
      alpha: branchReveal * alpha,
      glow: selected ? cyan : undefined,
    });
  }
  const choice = smoothstep(0.58, 0.9, t);
  drawGlowOrb(ctx, junctions[0].x, junctions[0].y, 10 + 5 * wave(t, 1), blue, alpha);
  drawLabel(ctx, scene.params?.caption ?? "the future narrows through action without becoming fixed in advance", 640, 105, {
    color: blue,
    size: 17,
    alpha: 0.82 * alpha,
  });
  drawLabel(ctx, "possible", 865, 485, { color: structure, size: 13, alpha: (1 - choice * 0.35) * alpha });
}

export const mechanismImplementations = Object.freeze({
  "technical-rate-plot": technicalRatePlot,
  "evidence-ladder": evidenceLadder,
  "phase-space-trajectories": phaseSpaceTrajectories,
  "barrier-tunnelling": barrierTunnelling,
  "energy-landscape": energyLandscape,
  "molecular-gate": molecularGate,
  "moving-time-window": movingTimeWindow,
  "simultaneity-sequence": simultaneitySequence,
  "branching-future": branchingFuture,
});
