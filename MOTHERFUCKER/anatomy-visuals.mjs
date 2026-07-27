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
  drawLotus,
  drawNode,
  drawPartialPath,
  drawRing,
} from "./primitives.mjs";
import {
  anatomyLandmarks,
  bodyFrame,
  bodyPoint,
  chakraLandmarks,
  dvadasantaStations,
  standingBodyPath,
  withBodyTransform,
} from "./anatomy-geometry.mjs";

function reveal(t) {
  return smoothstep(0.01, 0.12, t);
}

function colors(scene, theme) {
  return {
    ink: theme.ink,
    structure: theme.structure,
    physical: scene.palette?.accent ?? "#a94955",
    neural: scene.palette?.secondary ?? "#455b94",
    breath: "#3b9ba0",
    awareness: scene.palette?.luminous ?? "#d2a744",
    subtle: "#8a5f9e",
    earth: "#b06b3c",
    field: "#56828a",
  };
}

function stroke(ctx, points, color, width = 1.2, alpha = 1, dash = []) {
  if (points.length < 2) return;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.setLineDash(dash);
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (const point of points.slice(1)) ctx.lineTo(point.x, point.y);
  ctx.stroke();
  ctx.restore();
}

function localPoint(point, params = {}) {
  const frame = bodyFrame(params);
  return {
    x: frame.cx + point.x * frame.scale,
    y: frame.top + point.y * frame.scale,
  };
}

function pathPoint(points, amount) {
  const position = clamp(amount) * (points.length - 1);
  const index = Math.floor(position);
  const fraction = position - index;
  const a = points[index];
  const b = points[Math.min(points.length - 1, index + 1)];
  return {
    x: a.x + (b.x - a.x) * fraction,
    y: a.y + (b.y - a.y) * fraction,
  };
}

function humanStandingOutline(ctx, t, params, env) {
  const theme = env.theme;
  const color = params.color ?? theme.structure;
  const alpha = (params.alpha ?? 0.8) * reveal(t);
  withBodyTransform(ctx, params, () => {
    ctx.save();
    ctx.fillStyle = rgba(params.fill ?? theme.backgroundLight, params.fillAlpha ?? 0.28);
    ctx.strokeStyle = rgba(color, alpha);
    ctx.lineWidth = params.lineWidth ?? 1.45;
    ctx.lineJoin = "round";
    const body = standingBodyPath();
    ctx.fill(body);
    ctx.stroke(body);
    ctx.beginPath();
    ctx.ellipse(0, 46, 26, 31, 0, 0, TAU);
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, 78);
    ctx.lineTo(0, 304);
    ctx.strokeStyle = rgba(color, alpha * 0.22);
    ctx.lineWidth = 0.7;
    ctx.stroke();
    ctx.restore();
  });
}

function humanSeatedOutline(ctx, t, params, env) {
  const theme = env.theme;
  const color = params.color ?? theme.structure;
  const alpha = (params.alpha ?? 0.82) * reveal(t);
  const cx = params.x ?? 640;
  const cy = params.y ?? 314;
  const scale = params.scale ?? 1;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.scale(scale, scale);
  ctx.strokeStyle = rgba(color, alpha);
  ctx.fillStyle = rgba(params.fill ?? theme.backgroundLight, params.fillAlpha ?? 0.22);
  ctx.lineWidth = params.lineWidth ?? 1.6;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  ctx.ellipse(0, -166, 25, 30, 0, 0, TAU);
  ctx.fill();
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-13, -135);
  ctx.bezierCurveTo(-52, -112, -58, -25, -44, 40);
  ctx.bezierCurveTo(-20, 55, 20, 55, 44, 40);
  ctx.bezierCurveTo(58, -25, 52, -112, 13, -135);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-42, -83);
  ctx.bezierCurveTo(-88, -34, -84, 24, -20, 42);
  ctx.bezierCurveTo(-8, 46, -4, 51, 0, 57);
  ctx.bezierCurveTo(4, 51, 8, 46, 20, 42);
  ctx.bezierCurveTo(84, 24, 88, -34, 42, -83);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-42, 35);
  ctx.bezierCurveTo(-92, 54, -142, 89, -158, 126);
  ctx.bezierCurveTo(-100, 139, -49, 133, 0, 92);
  ctx.bezierCurveTo(49, 133, 100, 139, 158, 126);
  ctx.bezierCurveTo(142, 89, 92, 54, 42, 35);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(0, -132);
  ctx.lineTo(0, 78);
  ctx.strokeStyle = rgba(color, alpha * 0.3);
  ctx.lineWidth = 0.8;
  ctx.stroke();
  ctx.restore();
}

function bodyLandmarks(ctx, t, params, env) {
  const theme = env.theme;
  const names = params.names ?? [
    "crown", "brow", "throat", "heart", "diaphragm", "navel", "root",
  ];
  const alpha = (params.alpha ?? 0.75) * reveal(t);
  names.forEach((name, index) => {
    const point = bodyPoint(name, params);
    const arrive = smoothstep(index * 0.045, 0.18 + index * 0.045, t);
    drawNode(ctx, point.x, point.y, params.radius ?? 3.4, {
      fill: theme.backgroundLight,
      stroke: params.color ?? theme.secondary,
      alpha: alpha * arrive,
      width: 1,
    });
    if (params.labels) {
      drawLabel(ctx, params.labels[name] ?? name, point.x + (params.labelOffset ?? 48), point.y, {
        color: params.color ?? theme.structure,
        size: 11,
        alpha: alpha * arrive,
        align: "left",
      });
    }
  });
}

function lungsDiaphragm(ctx, t, params, env) {
  const theme = env.theme;
  const color = params.color ?? "#3b9ba0";
  const inhale = params.phase === "exhale"
    ? 1 - easeInOutCubic(t)
    : 0.5 - 0.5 * Math.cos(TAU * (params.cycles ?? 1) * t);
  const alpha = (params.alpha ?? 0.78) * reveal(t);
  withBodyTransform(ctx, params, () => {
    ctx.save();
    ctx.translate(0, 176);
    ctx.scale(1 + inhale * 0.08, 1 + inhale * 0.13);
    ctx.fillStyle = rgba(color, 0.08 * alpha);
    ctx.strokeStyle = rgba(color, 0.88 * alpha);
    ctx.lineWidth = 1.6;
    for (const direction of [-1, 1]) {
      ctx.beginPath();
      ctx.moveTo(direction * 8, -54);
      ctx.bezierCurveTo(direction * 48, -51, direction * 48, 13, direction * 32, 42);
      ctx.bezierCurveTo(direction * 18, 55, direction * 6, 25, direction * 8, -54);
      ctx.fill();
      ctx.stroke();
    }
    ctx.restore();
    ctx.save();
    ctx.strokeStyle = rgba(color, 0.72 * alpha);
    ctx.lineWidth = 2;
    ctx.beginPath();
    const y = 218 + inhale * 7;
    ctx.moveTo(-44, y);
    ctx.bezierCurveTo(-22, y - 15, 22, y - 15, 44, y);
    ctx.stroke();
    ctx.restore();
  });
  const throat = bodyPoint("throat", params);
  const diaphragm = bodyPoint("diaphragm", params);
  drawPartialPath(ctx, [throat, diaphragm], smoothstep(0.04, 0.45, t), color, 1.4, 0.45 * alpha);
}

function heartCirculation(ctx, t, params, env) {
  const theme = env.theme;
  const color = params.color ?? "#a94955";
  const alpha = (params.alpha ?? 0.82) * reveal(t);
  const heart = bodyPoint("heart", params);
  const beat = 1 + 0.1 * Math.max(0, Math.sin(TAU * (params.rate ?? 1.3) * t));
  ctx.save();
  ctx.translate(heart.x, heart.y);
  ctx.scale(beat, beat);
  ctx.fillStyle = rgba(color, 0.16 * alpha);
  ctx.strokeStyle = rgba(color, 0.9 * alpha);
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(0, 15);
  ctx.bezierCurveTo(-27, -2, -25, -28, -8, -29);
  ctx.bezierCurveTo(2, -29, 7, -20, 8, -14);
  ctx.bezierCurveTo(11, -22, 20, -28, 29, -22);
  ctx.bezierCurveTo(43, -10, 29, 7, 0, 31);
  ctx.bezierCurveTo(-7, 25, -7, 20, 0, 15);
  ctx.fill();
  ctx.stroke();
  ctx.restore();

  const crown = bodyPoint("crown", params);
  const leftWrist = bodyPoint("leftWrist", params);
  const rightWrist = bodyPoint("rightWrist", params);
  const leftAnkle = bodyPoint("leftAnkle", params);
  const rightAnkle = bodyPoint("rightAnkle", params);
  const routes = [
    [heart, crown],
    [heart, leftWrist],
    [heart, rightWrist],
    [heart, leftAnkle],
    [heart, rightAnkle],
  ];
  routes.forEach((route, index) => {
    stroke(ctx, route, color, 0.85, 0.25 * alpha);
    const point = pathPoint(route, (t * 1.4 + index * 0.17) % 1);
    drawGlowOrb(ctx, point.x, point.y, 3.5, color, 0.62 * alpha);
  });
}

function nervousSystem(ctx, t, params, env) {
  const theme = env.theme;
  const color = params.color ?? "#455b94";
  const alpha = (params.alpha ?? 0.75) * reveal(t);
  const crown = bodyPoint("brow", params);
  const sacrum = bodyPoint("sacrum", params);
  const spine = [];
  for (let index = 0; index <= 60; index += 1) {
    const q = index / 60;
    spine.push({
      x: crown.x + Math.sin(q * Math.PI * 4) * 2.4,
      y: crown.y + (sacrum.y - crown.y) * q,
    });
  }
  drawGlowingPath(ctx, spine, color, 1.5, 0.55 * alpha, { blur: 4 });
  const branchNames = [
    ["leftShoulder", "leftWrist"],
    ["rightShoulder", "rightWrist"],
    ["leftHip", "leftAnkle"],
    ["rightHip", "rightAnkle"],
  ];
  branchNames.forEach(([originName, targetName], index) => {
    const origin = bodyPoint(originName, params);
    const target = bodyPoint(targetName, params);
    const mid = {
      x: (origin.x + target.x) / 2 + (index % 2 ? 8 : -8),
      y: (origin.y + target.y) / 2,
    };
    const branch = [origin, mid, target];
    drawPartialPath(ctx, branch, smoothstep(0.05 + index * 0.06, 0.55, t), color, 0.9, 0.4 * alpha);
    const point = pathPoint(branch, (t * 1.7 + index * 0.2) % 1);
    drawGlowOrb(ctx, point.x, point.y, 3.2, color, 0.58 * alpha);
  });
  drawGlowOrb(ctx, crown.x, crown.y, 14, color, 0.34 * alpha);
}

function bodyBoundary(ctx, t, params, env) {
  const theme = env.theme;
  const frame = bodyFrame(params);
  const alpha = (params.alpha ?? 0.55) * reveal(t);
  const pulse = 1 + 0.02 * wave(t, params.rate ?? 0.65);
  drawEllipseRing(
    ctx,
    frame.cx,
    frame.top + 250 * frame.scale,
    150 * frame.scale * pulse,
    260 * frame.scale * pulse,
    params.color ?? theme.secondary,
    alpha,
    params.lineWidth ?? 1.2,
  );
  drawEllipseRing(
    ctx,
    frame.cx,
    frame.top + 250 * frame.scale,
    174 * frame.scale / pulse,
    286 * frame.scale / pulse,
    params.secondary ?? theme.luminous,
    alpha * 0.3,
    0.8,
  );
}

function awarenessHalo(ctx, t, params, env) {
  const theme = env.theme;
  const focus = params.focus ?? "heart";
  const point = typeof focus === "string" ? bodyPoint(focus, params) : localPoint(focus, params);
  const color = params.color ?? theme.luminous;
  const radius = (params.radius ?? 62) * (1 + 0.045 * wave(t, params.rate ?? 0.6));
  const alpha = (params.alpha ?? 0.65) * reveal(t);
  drawGlowOrb(ctx, point.x, point.y, radius, color, alpha, false);
  drawRing(ctx, point.x, point.y, radius * 0.72, color, alpha * 0.62, 1.1);
}

function bodyScanBand(ctx, t, params, env) {
  const theme = env.theme;
  const frame = bodyFrame(params);
  const progress = params.direction === "up" ? 1 - easeInOutCubic(t) : easeInOutCubic(t);
  const y = frame.top + (35 + progress * 430) * frame.scale;
  const width = (params.width ?? 330) * frame.scale;
  const height = (params.height ?? 44) * frame.scale;
  const color = params.color ?? theme.luminous;
  const gradient = ctx.createLinearGradient(frame.cx - width / 2, 0, frame.cx + width / 2, 0);
  gradient.addColorStop(0, rgba(color, 0));
  gradient.addColorStop(0.5, rgba(color, params.alpha ?? 0.18));
  gradient.addColorStop(1, rgba(color, 0));
  ctx.fillStyle = gradient;
  ctx.fillRect(frame.cx - width / 2, y - height / 2, width, height);
  stroke(ctx, [
    { x: frame.cx - width * 0.36, y },
    { x: frame.cx + width * 0.36, y },
  ], color, 1.1, (params.alpha ?? 0.55) * reveal(t));
}

function flowParticles(ctx, t, params, env) {
  const theme = env.theme;
  const frame = bodyFrame(params);
  const count = params.count ?? 24;
  const color = params.color ?? theme.luminous;
  const direction = params.direction === "down" ? -1 : 1;
  for (let index = 0; index < count; index += 1) {
    const phase = (direction * t * (params.speed ?? 0.65) + index / count + 2) % 1;
    const y = frame.top + (470 - phase * 425) * frame.scale;
    const x = frame.cx + Math.sin(phase * TAU * 2 + index * 1.7) * (params.spread ?? 62) * frame.scale;
    drawGlowOrb(ctx, x, y, params.radius ?? 3.2, color, (params.alpha ?? 0.42) * Math.sin(phase * Math.PI));
  }
}

function centralChannel(ctx, t, params, env) {
  const theme = env.theme;
  const root = bodyPoint("root", params);
  const crown = bodyPoint("crown", params);
  const color = params.color ?? theme.luminous;
  drawPartialPath(
    ctx,
    [root, crown],
    params.revealAmount ?? smoothstep(0.04, 0.55, t),
    color,
    params.width ?? 2.2,
    (params.alpha ?? 0.72) * reveal(t),
    { blur: 7 },
  );
}

function chakraStack(ctx, t, params, env) {
  const theme = env.theme;
  const alpha = (params.alpha ?? 0.85) * reveal(t);
  const active = params.active ?? Math.min(6, Math.floor(t * 7.4));
  chakraLandmarks.forEach((chakra, index) => {
    const point = localPoint(chakra, params);
    const arrive = smoothstep(index * 0.07, 0.18 + index * 0.07, t);
    const activated = index <= active;
    const radius = (params.radius ?? 16) + (activated ? 3 * wave(t, 0.75, index * 0.12) : 0);
    drawLotus(ctx, point.x, point.y, radius, {
      petals: chakra.petals,
      rotation: t * 0.035 * (index % 2 ? -1 : 1),
      stroke: chakra.color,
      fill: rgba(chakra.color, activated ? 0.08 : 0.025),
      alpha: alpha * arrive * (activated ? 0.95 : 0.45),
      lineWidth: activated ? 1.25 : 0.7,
    });
    drawGlowOrb(ctx, point.x, point.y, activated ? 5 : 2.5, chakra.color, alpha * arrive * (activated ? 0.65 : 0.18));
    if (params.labels) {
      drawLabel(ctx, chakra.term, point.x + (params.labelOffset ?? 72), point.y, {
        color: chakra.color,
        size: 10.5,
        alpha: alpha * arrive,
        align: "left",
      });
    }
  });
}

function idaPingala(ctx, t, params, env) {
  const theme = env.theme;
  const frame = bodyFrame(params);
  const rootY = frame.top + anatomyLandmarks.root.y * frame.scale;
  const crownY = frame.top + anatomyLandmarks.crown.y * frame.scale;
  const amplitude = (params.amplitude ?? 27) * frame.scale;
  const turns = params.turns ?? 3.5;
  for (const [direction, color] of [
    [-1, params.idaColor ?? theme.secondary],
    [1, params.pingalaColor ?? theme.accent],
  ]) {
    const points = [];
    for (let index = 0; index <= 160; index += 1) {
      const q = index / 160;
      points.push({
        x: frame.cx + direction * Math.sin(q * TAU * turns) * amplitude,
        y: rootY + (crownY - rootY) * q,
      });
    }
    drawPartialPath(ctx, points, smoothstep(0.05, 0.72, t), color, 1.35, (params.alpha ?? 0.65) * reveal(t), { blur: 4 });
    const pulse = pathPoint(points, (t * 0.72 + (direction > 0 ? 0.5 : 0)) % 1);
    drawGlowOrb(ctx, pulse.x, pulse.y, 4, color, 0.68 * reveal(t));
  }
}

function nadiNetwork(ctx, t, params, env) {
  const theme = env.theme;
  const frame = bodyFrame(params);
  const centerNames = ["root", "navel", "heart", "throat", "brow"];
  const targets = [
    "leftAnkle", "rightAnkle", "leftWrist", "rightWrist",
    "leftShoulder", "rightShoulder", "leftHip", "rightHip",
  ];
  targets.forEach((targetName, index) => {
    const sourceName = centerNames[index % centerNames.length];
    const source = bodyPoint(sourceName, params);
    const target = bodyPoint(targetName, params);
    const bend = {
      x: frame.cx + (target.x - frame.cx) * 0.46,
      y: source.y + (target.y - source.y) * 0.35,
    };
    drawPartialPath(
      ctx,
      [source, bend, target],
      smoothstep(index * 0.025, 0.45 + index * 0.025, t),
      index % 2 ? (params.secondary ?? theme.secondary) : (params.color ?? theme.luminous),
      0.75,
      0.32 * reveal(t),
    );
  });
}

function kundaliniCoil(ctx, t, params, env) {
  const theme = env.theme;
  const root = bodyPoint("root", params);
  const color = params.color ?? "#b06b3c";
  const alpha = (params.alpha ?? 0.82) * reveal(t);
  const uncoil = params.uncoil ?? smoothstep(0.18, 0.88, t);
  const turns = 3.5 - uncoil * 2.1;
  const radius = 29 - uncoil * 12;
  const points = [];
  for (let index = 0; index <= 120; index += 1) {
    const q = index / 120;
    const angle = q * TAU * turns;
    points.push({
      x: root.x + Math.cos(angle) * radius * (1 - q * 0.32),
      y: root.y + Math.sin(angle) * radius * 0.38 - q * uncoil * 54,
    });
  }
  drawPartialPath(ctx, points, smoothstep(0.02, 0.6, t), color, 2.2, alpha, { blur: 7 });
  const head = points.at(-1);
  drawGlowOrb(ctx, head.x, head.y, 8, color, alpha);
}

function crownField(ctx, t, params, env) {
  const theme = env.theme;
  const crown = bodyPoint("crown", params);
  const color = params.color ?? theme.luminous;
  const expansion = easeOutCubic(smoothstep(0.08, 0.82, t));
  for (let index = 0; index < 6; index += 1) {
    drawEllipseRing(
      ctx,
      crown.x,
      crown.y - 8,
      24 + expansion * (30 + index * 22),
      12 + expansion * (14 + index * 11),
      index % 2 ? theme.secondary : color,
      (0.48 - index * 0.045) * reveal(t),
      index === 0 ? 1.5 : 0.8,
    );
  }
  drawGlowOrb(ctx, crown.x, crown.y, 18 + expansion * 20, color, 0.68 * reveal(t));
}

function embodiedAwarenessField(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  const focuses = scene.params?.focuses ?? ["brow", "heart", "navel"];
  const phase = Math.min(focuses.length - 1, Math.floor(t * focuses.length));
  humanStandingOutline(ctx, t, scene.params, env);
  bodyBoundary(ctx, t, { ...scene.params, color: local.field }, env);
  awarenessHalo(ctx, t, {
    ...scene.params,
    focus: focuses[phase],
    color: local.awareness,
    radius: 58,
  }, env);
  bodyLandmarks(ctx, t, {
    ...scene.params,
    names: focuses,
    color: local.neural,
  }, env);
  drawLabel(ctx, "awareness is located by changing relevance", 640, 112, {
    color: local.structure,
    size: 15,
    alpha: 0.78 * reveal(t),
  });
}

function bodyScan(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanStandingOutline(ctx, t, scene.params, env);
  nervousSystem(ctx, t, { ...scene.params, alpha: 0.25 }, env);
  bodyScanBand(ctx, t, { ...scene.params, color: local.awareness }, env);
  const trailCount = 7;
  for (let index = 0; index < trailCount; index += 1) {
    bodyScanBand(ctx, Math.max(0, t - index * 0.025), {
      ...scene.params,
      color: local.awareness,
      alpha: 0.11 * (1 - index / trailCount),
      height: 28,
    }, env);
  }
  drawLabel(ctx, "attention samples the body in ordered regions", 640, 112, {
    color: local.structure,
    size: 15,
    alpha: 0.78 * reveal(t),
  });
}

function meditationSettling(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  const settle = easeInOutCubic(smoothstep(0.12, 0.86, t));
  humanSeatedOutline(ctx, t, { ...scene.params, color: local.structure }, env);
  const cx = scene.params?.x ?? 640;
  const cy = scene.params?.y ?? 314;
  for (let index = 0; index < 52; index += 1) {
    const angle = index * 2.399;
    const outer = 125 + (index % 7) * 37;
    const inner = 62 + (index % 5) * 7;
    const radius = outer + (inner - outer) * settle;
    const jitter = (1 - settle) * 16 * Math.sin(index * 1.8 + t * TAU * 3);
    drawNode(ctx, cx + Math.cos(angle) * (radius + jitter), cy - 40 + Math.sin(angle) * radius * 0.55, 1.4 + (index % 3) * 0.5, {
      fill: env.theme.backgroundLight,
      stroke: index % 4 ? local.neural : local.physical,
      alpha: (0.48 - settle * 0.22) * reveal(t),
      width: 0.7,
    });
  }
  drawEllipseRing(ctx, cx, cy - 42, 90 + 5 * wave(t, 0.55), 145 + 7 * wave(t, 0.55), local.awareness, 0.28 * reveal(t), 1);
  awarenessHalo(ctx, t, { x: cx, y: cy - 174, scale: 1, focus: { x: 0, y: 0 }, color: local.awareness, radius: 38 }, env);
  drawLabel(ctx, "settling coordinates many processes without erasing them", 640, 112, {
    color: local.structure,
    size: 15,
    alpha: 0.78 * reveal(t),
  });
}

function breathCycle(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanStandingOutline(ctx, t, scene.params, env);
  lungsDiaphragm(ctx, t, { ...scene.params, color: local.breath, cycles: 1 }, env);
  const throat = bodyPoint("throat", scene.params);
  const outside = { x: throat.x, y: 104 };
  const inhale = 0.5 - 0.5 * Math.cos(TAU * t);
  const airPath = inhale < 0.5 ? [throat, outside] : [outside, throat];
  const progress = inhale < 0.5 ? 1 - inhale * 2 : (inhale - 0.5) * 2;
  drawPartialPath(ctx, airPath, progress, local.breath, 2.1, 0.72 * reveal(t), { blur: 7 });
  drawLabel(ctx, inhale > 0.5 ? "inhalation · expansion" : "exhalation · release", 640, 112, {
    color: local.breath,
    size: 16,
    alpha: 0.84 * reveal(t),
  });
}

function breathAttentionCoupling(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanSeatedOutline(ctx, t, { ...scene.params, color: local.structure }, env);
  const bodyParams = { x: 640, y: 100, scale: 0.8 };
  lungsDiaphragm(ctx, t, { ...bodyParams, color: local.breath, cycles: 1 }, env);
  const inhale = 0.5 - 0.5 * Math.cos(TAU * t);
  const focus = inhale > 0.5 ? "brow" : "heart";
  awarenessHalo(ctx, t, { ...bodyParams, focus, color: local.awareness, radius: 48 + inhale * 18 }, env);
  stroke(ctx, [bodyPoint("heart", bodyParams), bodyPoint("brow", bodyParams)], local.awareness, 1, 0.32 * reveal(t), [4, 5]);
  drawLabel(ctx, "breath rhythm changes the field of attention", 640, 112, {
    color: local.structure,
    size: 15,
    alpha: 0.78 * reveal(t),
  });
}

function nervousSignalPropagation(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanStandingOutline(ctx, t, scene.params, env);
  nervousSystem(ctx, t, { ...scene.params, color: local.neural, alpha: 0.9 }, env);
  const stimulus = bodyPoint(scene.params?.stimulus ?? "leftWrist", scene.params);
  drawGlowOrb(ctx, stimulus.x, stimulus.y, 11 + 3 * wave(t, 1.3), local.physical, 0.72 * reveal(t));
  drawLabel(ctx, "a local event propagates through a distributed system", 640, 112, {
    color: local.structure,
    size: 15,
    alpha: 0.78 * reveal(t),
  });
}

function interoceptiveMap(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanStandingOutline(ctx, t, { ...scene.params, alpha: 0.55 }, env);
  const sources = ["heart", "lungLeft", "lungRight", "diaphragm", "navel", "sacrum"];
  const target = bodyPoint("brow", scene.params);
  sources.forEach((name, index) => {
    const source = bodyPoint(name, scene.params);
    const bend = { x: source.x + (index % 2 ? 45 : -45), y: (source.y + target.y) / 2 };
    const path = [source, bend, target];
    drawPartialPath(ctx, path, smoothstep(index * 0.055, 0.62 + index * 0.025, t), index % 2 ? local.breath : local.physical, 1.15, 0.48 * reveal(t));
    const pulsePoint = pathPoint(path, (t * 0.75 + index * 0.13) % 1);
    drawGlowOrb(ctx, pulsePoint.x, pulsePoint.y, 3.8, index % 2 ? local.breath : local.physical, 0.55 * reveal(t));
  });
  drawGlowOrb(ctx, target.x, target.y, 20, local.neural, 0.5 * reveal(t));
  drawLabel(ctx, "many internal signals become one provisional body-state", 640, 112, {
    color: local.structure,
    size: 15,
    alpha: 0.78 * reveal(t),
  });
}

function bodyWorldInterface(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanStandingOutline(ctx, t, scene.params, env);
  bodyBoundary(ctx, t, { ...scene.params, color: local.neural, alpha: 0.72 }, env);
  const frame = bodyFrame(scene.params);
  const centerY = frame.top + 235 * frame.scale;
  for (let index = 0; index < 12; index += 1) {
    const side = index % 2 ? -1 : 1;
    const y = 145 + (index % 6) * 65;
    const outsideX = 640 + side * 360;
    const boundaryX = 640 + side * 142;
    const accepted = index % 3 !== 0;
    const progress = easeOutCubic((t + index * 0.09) % 1);
    const endpoint = accepted ? 640 + side * 42 : boundaryX + side * 4;
    const x = outsideX + (endpoint - outsideX) * progress;
    drawGlowOrb(ctx, x, y, 4.5, accepted ? local.breath : local.physical, 0.58 * reveal(t));
    if (!accepted && progress > 0.82) {
      drawArrowHead(ctx, boundaryX + side * 9, y, side > 0 ? 0 : Math.PI, 8, local.physical, 0.55 * reveal(t));
    }
  }
  drawGlowOrb(ctx, 640, centerY, 18, local.awareness, 0.38 * reveal(t));
  drawLabel(ctx, "a boundary creates selective access before perspective", 640, 112, {
    color: local.structure,
    size: 15,
    alpha: 0.78 * reveal(t),
  });
}

function heartBreathEntrainment(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  const sync = easeInOutCubic(smoothstep(0.22, 0.82, t));
  const x0 = 230;
  const width = 820;
  const top = 180;
  const waves = [
    { color: local.breath, y: 270, frequency: 2, phase: 0 },
    { color: local.physical, y: 390, frequency: 2 + (1 - sync) * 0.8, phase: (1 - sync) * 0.23 },
  ];
  waves.forEach((item) => {
    const points = [];
    for (let index = 0; index <= 180; index += 1) {
      const q = index / 180;
      points.push({
        x: x0 + q * width,
        y: item.y + Math.sin(TAU * (item.frequency * q + item.phase - t * 0.55)) * 32,
      });
    }
    drawPartialPath(ctx, points, smoothstep(0.02, 0.55, t), item.color, 1.8, 0.76 * reveal(t), { blur: 5 });
  });
  stroke(ctx, [{ x: x0, y: top }, { x: x0, y: 455 }, { x: x0 + width, y: 455 }], local.structure, 0.8, 0.4 * reveal(t));
  drawLabel(ctx, "breath", x0 - 26, 270, { color: local.breath, size: 13, alpha: 0.8 * reveal(t), align: "right" });
  drawLabel(ctx, "heart", x0 - 26, 390, { color: local.physical, size: 13, alpha: 0.8 * reveal(t), align: "right" });
  drawLabel(ctx, sync > 0.72 ? "coordinated rhythm" : "independent rhythms", 640, 112, {
    color: sync > 0.72 ? local.awareness : local.structure,
    size: 16,
    alpha: 0.84 * reveal(t),
  });
}

function chakraAxis(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanStandingOutline(ctx, t, { ...scene.params, alpha: 0.48 }, env);
  centralChannel(ctx, t, { ...scene.params, color: local.awareness }, env);
  chakraStack(ctx, t, { ...scene.params, labels: scene.params?.labels ?? true }, env);
  drawLabel(ctx, "contemplative map · not anatomical tissue", 640, 112, {
    color: local.subtle,
    size: 14,
    alpha: 0.8 * reveal(t),
  });
}

function nadiFlow(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanStandingOutline(ctx, t, { ...scene.params, alpha: 0.38 }, env);
  centralChannel(ctx, t, { ...scene.params, color: local.awareness }, env);
  idaPingala(ctx, t, scene.params, env);
  chakraStack(ctx, t, { ...scene.params, radius: 9, alpha: 0.55 }, env);
  drawLabel(ctx, "three-channel yogic model of coordinated flow", 640, 112, {
    color: local.subtle,
    size: 14,
    alpha: 0.8 * reveal(t),
  });
}

function kundaliniAscent(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanStandingOutline(ctx, t, { ...scene.params, alpha: 0.4 }, env);
  centralChannel(ctx, t, { ...scene.params, color: local.awareness }, env);
  chakraStack(ctx, t, { ...scene.params, radius: 10, alpha: 0.45 }, env);
  kundaliniCoil(ctx, t, { ...scene.params, color: local.earth }, env);
  const root = bodyPoint("root", scene.params);
  const crown = bodyPoint("crown", scene.params);
  const progress = easeInOutCubic(smoothstep(0.16, 0.92, t));
  const point = {
    x: root.x + Math.sin(progress * TAU * 3.5) * 12 * (1 - progress),
    y: root.y + (crown.y - root.y) * progress,
  };
  drawGlowOrb(ctx, point.x, point.y, 10 + 4 * wave(t, 1), local.earth, 0.88 * reveal(t));
  if (progress > 0.8) crownField(ctx, (progress - 0.8) / 0.2, scene.params, env);
  drawLabel(ctx, "symbolic ascent through a staged contemplative axis", 640, 112, {
    color: local.subtle,
    size: 14,
    alpha: 0.8 * reveal(t),
  });
}

function subtleCirculation(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanStandingOutline(ctx, t, { ...scene.params, alpha: 0.4 }, env);
  bodyBoundary(ctx, t, { ...scene.params, color: local.subtle, alpha: 0.42 }, env);
  const root = bodyPoint("root", scene.params);
  const crown = bodyPoint("crown", scene.params);
  const frame = bodyFrame(scene.params);
  const route = [
    root,
    crown,
    { x: frame.cx + 130 * frame.scale, y: frame.top + 125 * frame.scale },
    { x: frame.cx + 145 * frame.scale, y: frame.top + 345 * frame.scale },
    root,
  ];
  drawGlowingPath(ctx, route, local.awareness, 1.35, 0.42 * reveal(t), { blur: 5 });
  for (let index = 0; index < 8; index += 1) {
    const point = pathPoint(route, (t * 0.7 + index / 8) % 1);
    drawGlowOrb(ctx, point.x, point.y, 4.4, index % 2 ? local.awareness : local.subtle, 0.62 * reveal(t));
  }
  drawArrowHead(ctx, root.x, root.y - 8, -Math.PI / 2, 10, local.awareness, 0.68 * reveal(t));
  drawLabel(ctx, "a cyclic practice-map preserves return as well as ascent", 640, 112, {
    color: local.subtle,
    size: 14,
    alpha: 0.8 * reveal(t),
  });
}

function physicalSubtleCompare(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  const left = { x: 405, y: 120, scale: 0.7 };
  const right = { x: 875, y: 120, scale: 0.7 };
  humanStandingOutline(ctx, t, { ...left, color: local.structure, alpha: 0.72 }, env);
  lungsDiaphragm(ctx, t, { ...left, color: local.breath }, env);
  heartCirculation(ctx, t, { ...left, color: local.physical, alpha: 0.58 }, env);
  nervousSystem(ctx, t, { ...left, color: local.neural, alpha: 0.5 }, env);
  humanStandingOutline(ctx, t, { ...right, color: local.structure, alpha: 0.72 }, env);
  centralChannel(ctx, t, { ...right, color: local.awareness }, env);
  idaPingala(ctx, t, { ...right, alpha: 0.62 }, env);
  chakraStack(ctx, t, { ...right, radius: 9, alpha: 0.7 }, env);
  stroke(ctx, [{ x: 640, y: 150 }, { x: 640, y: 510 }], local.structure, 1, 0.35 * reveal(t), [5, 7]);
  drawLabel(ctx, "biomedical model", left.x, 520, { color: local.neural, size: 14, alpha: 0.84 * reveal(t) });
  drawLabel(ctx, "yogic practice-map", right.x, 520, { color: local.subtle, size: 14, alpha: 0.84 * reveal(t) });
  drawLabel(ctx, "compare functions without collapsing categories", 640, 102, {
    color: local.structure,
    size: 15,
    alpha: 0.82 * reveal(t),
  });
}

function dvadasantaAscent(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  const params = { x: 640, y: 210, scale: 0.68 };
  humanStandingOutline(ctx, t, { ...params, alpha: 0.4 }, env);
  const points = dvadasantaStations.map((station) => localPoint(station, params));
  drawPartialPath(ctx, points, smoothstep(0.03, 0.82, t), local.awareness, 1.8, 0.72 * reveal(t), { blur: 6 });
  const active = Math.min(points.length - 1, Math.floor(t * points.length));
  points.forEach((point, index) => {
    const arrive = smoothstep(index * 0.045, 0.15 + index * 0.045, t);
    drawNode(ctx, point.x, point.y, index === active ? 6 : 3.2, {
      fill: env.theme.backgroundLight,
      stroke: index <= active ? local.awareness : local.subtle,
      alpha: arrive * reveal(t),
      glow: index === active ? local.awareness : undefined,
    });
    if (index % 2 === 0 || index === points.length - 1) {
      drawLabel(ctx, dvadasantaStations[index].label, point.x + 34, point.y, {
        color: local.subtle,
        size: 10,
        alpha: 0.68 * arrive * reveal(t),
        align: "left",
      });
    }
  });
  const cursor = pathPoint(points, easeInOutCubic(t));
  drawGlowOrb(ctx, cursor.x, cursor.y, 8, local.awareness, 0.8 * reveal(t));
  drawLabel(ctx, "twelve contemplative stations from heart into exterior space", 640, 102, {
    color: local.subtle,
    size: 14,
    alpha: 0.82 * reveal(t),
  });
}

function pranaApanaBalance(ctx, t, scene, env) {
  const local = colors(scene, env.theme);
  humanStandingOutline(ctx, t, { ...scene.params, alpha: 0.42 }, env);
  const navel = bodyPoint("navel", scene.params);
  const crown = bodyPoint("crown", scene.params);
  const root = bodyPoint("root", scene.params);
  const convergence = easeInOutCubic(smoothstep(0.12, 0.78, t));
  drawPartialPath(ctx, [crown, navel], convergence, local.breath, 2, 0.68 * reveal(t), { blur: 6 });
  drawPartialPath(ctx, [root, navel], convergence, local.earth, 2, 0.68 * reveal(t), { blur: 6 });
  drawArrowHead(ctx, navel.x, navel.y - 6, Math.PI / 2, 9, local.breath, 0.65 * reveal(t));
  drawArrowHead(ctx, navel.x, navel.y + 6, -Math.PI / 2, 9, local.earth, 0.65 * reveal(t));
  drawGlowOrb(ctx, navel.x, navel.y, 16 + convergence * 20, local.awareness, 0.78 * reveal(t));
  drawRing(ctx, navel.x, navel.y, 42 + convergence * 28, local.subtle, 0.42 * reveal(t), 1.1);
  drawLabel(ctx, "opposed currents become a provisional equilibrium", 640, 112, {
    color: local.subtle,
    size: 14,
    alpha: 0.8 * reveal(t),
  });
}

export const assetImplementations = Object.freeze({
  "human-standing-outline": humanStandingOutline,
  "human-seated-outline": humanSeatedOutline,
  "body-landmarks": bodyLandmarks,
  "lungs-diaphragm": lungsDiaphragm,
  "heart-circulation": heartCirculation,
  "nervous-system": nervousSystem,
  "body-boundary": bodyBoundary,
  "awareness-halo": awarenessHalo,
  "body-scan-band": bodyScanBand,
  "flow-particles": flowParticles,
  "central-channel": centralChannel,
  "chakra-stack": chakraStack,
  "ida-pingala": idaPingala,
  "nadi-network": nadiNetwork,
  "kundalini-coil": kundaliniCoil,
  "crown-field": crownField,
});

export const mechanismImplementations = Object.freeze({
  "embodied-awareness-field": embodiedAwarenessField,
  "body-scan": bodyScan,
  "meditation-settling": meditationSettling,
  "breath-cycle": breathCycle,
  "breath-attention-coupling": breathAttentionCoupling,
  "nervous-signal-propagation": nervousSignalPropagation,
  "interoceptive-map": interoceptiveMap,
  "body-world-interface": bodyWorldInterface,
  "heart-breath-entrainment": heartBreathEntrainment,
  "chakra-axis": chakraAxis,
  "nadi-flow": nadiFlow,
  "kundalini-ascent": kundaliniAscent,
  "subtle-circulation": subtleCirculation,
  "physical-subtle-compare": physicalSubtleCompare,
  "dvadasanta-ascent": dvadasantaAscent,
  "prana-apana-balance": pranaApanaBalance,
});

