import {
  TAU,
  clamp,
  easeInOutCubic,
  easeOutCubic,
  polar,
  pulse,
  sampleCubic,
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
  drawOrbitingNodes,
  drawPartialPath,
  drawRing,
  drawSilhouette,
  pointAlong,
} from "./primitives.mjs";
import { renderAssetLayers } from "./visual-assets.mjs";
import { typography } from "./theme.mjs";
import {
  renderSystemVisual,
  systemVisualDescriptions,
  systemVisualNames,
} from "./systems-visuals.mjs";

export const semanticVisualNames = Object.freeze([
  "constraint-field",
  "point-of-view",
  "five-lenses",
  "local-power",
  "melody-time",
  "attention-beam",
  "desire-orbit",
  "smallness-cage",
  "powered-prison",
  "practice-folds",
  "upsurge",
  "wave-ocean",
  "textures-display",
  "limitation-reversal",
  "opening-fist",
  ...systemVisualNames,
]);

export const semanticVisualDescriptions = Object.freeze({
  "constraint-field": "An unbounded luminous field concentrates into a local point, gesture, or frame.",
  "point-of-view": "A centerless field acquires an angle, foreground, and excluded horizon.",
  "five-lenses": "Five restrictions transform universal powers into local capacities.",
  "local-power": "A universal radial capacity becomes one finite action without losing its source.",
  "melody-time": "Simultaneity becomes sequence, rhythm, anticipation, and memory.",
  "attention-beam": "A narrow act of knowing reveals a foreground and produces a surrounding dark.",
  "desire-orbit": "Fullness localizes as a felt gap and a reaching movement toward an object.",
  "smallness-cage": "The thought ‘only this’ builds a local enclosure inside a larger field.",
  "powered-prison": "Luminous power actively constructs and renews the walls of limitation.",
  "practice-folds": "Body, breath, mantra, and attention retrace nested folds toward their source.",
  upsurge: "A local center reverses into a centerless field while the world remains present.",
  "wave-ocean": "A finite wave keeps its contour while revealing continuity with its substance.",
  "textures-display": "One field differentiates into many sensory and affective textures.",
  "limitation-reversal": "A finite condition remains real as experience but loses its status as identity.",
  "opening-fist": "Five enclosing arcs relax around the luminous field without vanishing.",
  ...systemVisualDescriptions,
});

function revealIn(t) {
  return smoothstep(0, 0.06, t);
}

function colors(scene, theme) {
  return {
    accent: scene.palette?.accent ?? theme.accent,
    secondary: scene.palette?.secondary ?? theme.secondary,
    gold: scene.palette?.luminous ?? theme.luminous,
  };
}

function fieldNodes(ctx, t, env, options = {}) {
  const { theme, random } = env;
  const count = options.count ?? 84;
  const alpha = options.alpha ?? 0.35;
  const cx = options.cx ?? 640;
  const cy = options.cy ?? 290;
  const radiusX = options.radiusX ?? 480;
  const radiusY = options.radiusY ?? 220;
  for (let index = 0; index < count; index += 1) {
    const angle = random() * TAU;
    const radius = Math.sqrt(random());
    const baseX = cx + Math.cos(angle) * radiusX * radius;
    const baseY = cy + Math.sin(angle) * radiusY * radius;
    const drift = 3.5 * wave(t, 0.42, random());
    drawNode(ctx, baseX + drift, baseY + drift * 0.45, 1.2 + random() * 1.2, {
      fill: theme.backgroundLight,
      stroke: index % 5 === 0 ? theme.luminous : theme.secondary,
      alpha: alpha * (0.5 + random() * 0.5),
      width: 0.65,
    });
  }
}

function fieldCore(ctx, t, theme, gold, alpha = 1, radius = 38) {
  const breath = 1 + 0.055 * wave(t, 0.6);
  drawGlowOrb(ctx, 640, 290, radius * breath, gold, 0.78 * alpha);
  drawRing(ctx, 640, 290, radius * 1.78 / breath, gold, 0.48 * alpha, 1.2);
  drawRing(ctx, 640, 290, radius * 2.55 * breath, theme.secondary, 0.22 * alpha, 0.9);
}

function note(ctx, x, y, color, alpha, active = false) {
  drawNode(ctx, x, y, active ? 7 : 5, {
    fill: active ? color : "#f8f2e2",
    stroke: color,
    alpha,
    width: active ? 1.5 : 1,
    glow: active ? color : undefined,
  });
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.moveTo(x + 5, y);
  ctx.lineTo(x + 5, y - 36);
  ctx.stroke();
  ctx.restore();
}

function constraintField(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const audio = env.audio ?? null;
  const pulse = audio ? 0.8 + 0.2 * audio.rms : 1;
  const reveal = revealIn(t) * pulse;
  const contraction = easeInOutCubic(smoothstep(0.12, 0.78, t));
  fieldNodes(ctx, t, env, { count: 112, alpha: 0.2 + 0.22 * (1 - contraction) });

  for (let index = 0; index < 7; index += 1) {
    const openRadius = 125 + index * 58;
    const closedRadius = 42 + index * 12;
    const radius = openRadius + (closedRadius - openRadius) * contraction;
    const audioBoost = audio ? 1 + 0.3 * audio.onset : 1;
    drawEllipseRing(
      ctx,
      640,
      290,
      radius * audioBoost,
      radius * (0.72 + index * 0.02) * audioBoost,
      index % 2 ? secondary : gold,
      reveal * (0.12 + index * 0.035) * (audio ? 0.5 + 0.5 * audio.rms : 1),
      (index === 0 ? 1.8 : 0.9) * (audio ? 1 + audio.onset * 0.5 : 1),
      t * 0.025 * (index % 2 ? -1 : 1),
    );
  }

  const frameWidth = 760 - 510 * contraction;
  const frameHeight = 390 - 250 * contraction;
  ctx.save();
  ctx.globalAlpha = 0.75 * reveal;
  ctx.strokeStyle = accent;
  ctx.lineWidth = 1.6;
  ctx.strokeRect(640 - frameWidth / 2, 290 - frameHeight / 2, frameWidth, frameHeight);
  ctx.restore();
  fieldCore(ctx, t, theme, gold, reveal, (33 + 8 * contraction) * (audio ? 0.8 + 0.2 * audio.rms : 1));
  drawLabel(ctx, scene.params?.centerText ?? "अहम्", 640, 294, {
    devanagari: true,
    size: audio ? 28 + 4 * audio.onset : 30,
    color: secondary,
    alpha: reveal,
  });
}

function pointOfView(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  fieldNodes(ctx, t, env, { count: 120, alpha: 0.28 });

  const eyeX = 290;
  const eyeY = 310;
  const target = { x: 880, y: 245 + 35 * wave(t, 0.32) };
  ctx.save();
  ctx.globalAlpha = 0.1 * reveal;
  ctx.fillStyle = gold;
  ctx.beginPath();
  ctx.moveTo(eyeX, eyeY);
  ctx.lineTo(target.x - 110, target.y - 90);
  ctx.lineTo(target.x + 110, target.y + 90);
  ctx.closePath();
  ctx.fill();
  ctx.restore();

  drawSilhouette(ctx, eyeX, eyeY + 35, 0.74, secondary, 0.88 * reveal);
  drawGlowOrb(ctx, eyeX, eyeY - 7, 18, gold, 0.72 * reveal);
  drawPartialPath(
    ctx,
    [{ x: eyeX + 28, y: eyeY - 10 }, target],
    smoothstep(0.08, 0.58, t),
    gold,
    1.7,
    0.68 * reveal,
    { blur: 7 },
  );
  drawEllipseRing(ctx, target.x, target.y, 122, 88, accent, 0.68 * reveal, 1.6, 0.08 * wave(t, 0.5));
  drawRing(ctx, target.x, target.y, 28 + 4 * wave(t, 0.7), gold, 0.86 * reveal, 1.3);

  const horizon = sampleCubic(
    { x: 120, y: 440 },
    { x: 410, y: 390 },
    { x: 870, y: 470 },
    { x: 1160, y: 410 },
    140,
  );
  drawPartialPath(ctx, horizon, easeOutCubic(smoothstep(0.02, 0.7, t)), theme.structure, 1.1, 0.35);
  drawLabel(ctx, scene.params?.leftText ?? "here", eyeX, 480, {
    color: secondary,
    size: 15,
    alpha: 0.8 * reveal,
  });
  drawLabel(ctx, scene.params?.rightText ?? "there", target.x, 480, {
    color: accent,
    size: 15,
    alpha: 0.8 * reveal,
  });
}

function fiveLenses(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const labels = scene.params?.labels ?? ["kalā", "vidyā", "rāga", "kāla", "niyati"];
  const local = scene.params?.focus ?? -1;
  const reveal = revealIn(t);
  fieldNodes(ctx, t, env, { count: 90, alpha: 0.18 });

  for (let index = 0; index < 5; index += 1) {
    const x = 280 + index * 180;
    const selected = local < 0 || local === index;
    const alpha = reveal * (selected ? 0.82 : 0.2);
    const radius = 82 + 5 * wave(t, 0.52, index * 0.16);
    drawEllipseRing(ctx, x, 285, radius * 0.64, radius, index % 2 ? secondary : accent, alpha, selected ? 1.6 : 0.9);
    drawGlowOrb(ctx, x, 285, selected ? 21 : 11, gold, alpha * 0.72);
    drawLabel(ctx, labels[index], x, 410, {
      style: typography.small,
      size: selected ? 17 : 13,
      color: selected ? theme.ink : theme.structure,
      alpha,
    });
  }

  const path = sampleCubic(
    { x: 165, y: 285 },
    { x: 430, y: 205 + 12 * wave(t, 0.5) },
    { x: 850, y: 365 - 12 * wave(t, 0.5) },
    { x: 1115, y: 285 },
    180,
  );
  drawGlowingPath(ctx, path, gold, 1.4, 0.25 * reveal, { blur: 5 });
  for (let index = 0; index < 10; index += 1) {
    const point = pointAlong(path, (t * 0.17 + index / 10) % 1);
    drawGlowOrb(ctx, point.x, point.y, 3.5, gold, 0.32 * reveal);
  }
}

function localPower(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const cx = 640;
  const cy = 292;
  const count = scene.params?.count ?? 16;
  const active = scene.params?.active ?? 2;
  for (let index = 0; index < count; index += 1) {
    const angle = -Math.PI / 2 + (index / count) * TAU;
    const inner = polar(cx, cy, 54, angle);
    const outer = polar(cx, cy, 205 + 12 * wave(t, 0.4, index / count), angle);
    const selected = index === active || index === (active + 1) % count;
    drawPartialPath(
      ctx,
      [inner, outer],
      smoothstep(index * 0.009, 0.42 + index * 0.009, t),
      selected ? accent : secondary,
      selected ? 2.8 : 0.8,
      reveal * (selected ? 0.9 : 0.2),
      { blur: selected ? 9 : 3 },
    );
    drawNode(ctx, outer.x, outer.y, selected ? 6 : 3, {
      fill: theme.backgroundLight,
      stroke: selected ? accent : secondary,
      alpha: reveal * (selected ? 0.9 : 0.28),
      glow: selected ? gold : undefined,
    });
  }
  fieldCore(ctx, t, theme, gold, reveal, 42);
  drawLabel(ctx, scene.params?.centerText ?? "शक्ति", cx, cy + 4, {
    devanagari: true,
    size: 28,
    color: secondary,
    alpha: reveal,
  });
}

function melodyTime(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const playhead = easeInOutCubic(t);
  const left = 190;
  const right = 1090;
  for (let line = 0; line < 5; line += 1) {
    ctx.save();
    ctx.globalAlpha = 0.2 * reveal;
    ctx.strokeStyle = theme.structure;
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(left, 230 + line * 28);
    ctx.lineTo(right, 230 + line * 28);
    ctx.stroke();
    ctx.restore();
  }
  const notes = scene.params?.notes ?? [0, 2, 4, 1, 3, 0, 4, 2];
  for (let index = 0; index < notes.length; index += 1) {
    const x = left + 70 + index * ((right - left - 140) / Math.max(1, notes.length - 1));
    const y = 342 - notes[index] * 28;
    const position = index / Math.max(1, notes.length - 1);
    const active = Math.abs(position - playhead) < 0.075;
    const passed = position < playhead;
    note(ctx, x, y, active ? accent : (passed ? secondary : gold), reveal * (passed ? 0.34 : 0.74), active);
  }
  const x = left + playhead * (right - left);
  drawPartialPath(ctx, [{ x, y: 180 }, { x, y: 400 }], 1, accent, 1.5, 0.58 * reveal, { blur: 5 });
  drawGlowOrb(ctx, x, 290, 16, gold, 0.5 * reveal);
  drawLabel(ctx, "memory", left + 80, 445, { color: secondary, size: 14, alpha: 0.7 * reveal });
  drawLabel(ctx, "now", 640, 445, { color: accent, size: 14, alpha: 0.85 * reveal });
  drawLabel(ctx, "anticipation", right - 90, 445, { color: gold, size: 14, alpha: 0.7 * reveal });
}

function attentionBeam(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  fieldNodes(ctx, t, env, { count: 140, alpha: 0.16 });
  const source = { x: 245, y: 300 };
  const target = { x: 885 + 55 * wave(t, 0.22), y: 280 + 42 * wave(t, 0.33, 0.2) };
  ctx.save();
  ctx.globalAlpha = 0.12 * reveal;
  ctx.fillStyle = gold;
  ctx.beginPath();
  ctx.moveTo(source.x, source.y);
  ctx.lineTo(target.x - 118, target.y - 82);
  ctx.lineTo(target.x + 118, target.y + 82);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
  drawGlowOrb(ctx, source.x, source.y, 31, secondary, 0.72 * reveal);
  drawGlowingPath(ctx, [source, target], gold, 2, 0.72 * reveal, { blur: 10 });
  drawRing(ctx, target.x, target.y, 64 + 5 * wave(t, 0.65), accent, 0.78 * reveal, 1.8);
  drawGlowOrb(ctx, target.x, target.y, 18, gold, 0.86 * reveal);
  drawLabel(ctx, scene.params?.foreground ?? "this", target.x, target.y + 92, {
    color: accent,
    size: 16,
    alpha: reveal,
  });
  drawLabel(ctx, "the same field", 640, 475, {
    color: theme.structure,
    size: 14,
    alpha: 0.68 * reveal,
  });
}

function desireOrbit(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const self = { x: 400, y: 300 };
  const object = { x: 880, y: 280 };
  drawSilhouette(ctx, self.x, self.y + 25, 0.78, secondary, 0.88 * reveal);
  drawGlowOrb(ctx, self.x, self.y - 10, 21, gold, 0.62 * reveal);
  drawGlowOrb(ctx, object.x, object.y, 38 + 5 * pulse(t, 0.55), accent, 0.82 * reveal);
  drawRing(ctx, object.x, object.y, 78 + 6 * wave(t, 0.5), gold, 0.44 * reveal, 1.2);
  const reach = sampleCubic(
    { x: self.x + 60, y: self.y },
    { x: 545, y: 160 + 22 * wave(t, 0.42) },
    { x: 735, y: 410 - 22 * wave(t, 0.42) },
    { x: object.x - 50, y: object.y },
    180,
  );
  drawPartialPath(ctx, reach, smoothstep(0.05, 0.72, t), accent, 2.2, 0.76 * reveal, { blur: 8 });
  for (let index = 0; index < 12; index += 1) {
    const amount = (t * 0.18 + index / 12) % 1;
    const point = pointAlong(reach, amount);
    drawGlowOrb(ctx, point.x, point.y, 4, index % 2 ? accent : gold, 0.42 * Math.sin(amount * Math.PI) * reveal);
  }
  drawLabel(ctx, scene.params?.gapText ?? "lack", 640, 455, {
    color: theme.structure,
    size: 15,
    alpha: 0.72 * reveal,
  });
}

function smallnessCage(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  fieldNodes(ctx, t, env, { count: 130, alpha: 0.18 });
  const cx = 640;
  const cy = 292;
  const bars = 7;
  for (let index = 0; index < bars; index += 1) {
    const x = 505 + index * 45;
    const height = 250 + 24 * wave(t, 0.42, index / bars);
    drawPartialPath(
      ctx,
      [{ x, y: cy - height / 2 }, { x, y: cy + height / 2 }],
      smoothstep(0.05 + index * 0.025, 0.52 + index * 0.025, t),
      index === 0 || index === bars - 1 ? accent : secondary,
      1.5,
      0.58 * reveal,
      { blur: 5 },
    );
  }
  ctx.save();
  ctx.globalAlpha = 0.5 * reveal;
  ctx.strokeStyle = accent;
  ctx.lineWidth = 1.5;
  ctx.strokeRect(475, 150, 330, 285);
  ctx.restore();
  drawSilhouette(ctx, cx, cy + 25, 0.82, secondary, 0.9 * reveal);
  drawGlowOrb(ctx, cx, cy - 12, 20, gold, 0.74 * reveal);
  drawRing(ctx, cx, cy, 238 + 10 * wave(t, 0.45), gold, 0.18 * reveal, 1);
  drawLabel(ctx, scene.params?.centerText ?? "only this", cx, 475, {
    color: accent,
    size: 17,
    alpha: 0.86 * reveal,
  });
}

function poweredPrison(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  fieldCore(ctx, t, theme, gold, reveal, 36);
  const segments = 18;
  for (let index = 0; index < segments; index += 1) {
    const side = index % 4;
    const unit = Math.floor(index / 4) / Math.ceil(segments / 4);
    let a;
    let b;
    if (side === 0) {
      a = { x: 390 + unit * 500, y: 145 };
      b = { x: 485 + unit * 310, y: 145 };
    } else if (side === 1) {
      a = { x: 890, y: 145 + unit * 300 };
      b = { x: 890, y: 205 + unit * 190 };
    } else if (side === 2) {
      a = { x: 890 - unit * 500, y: 445 };
      b = { x: 795 - unit * 310, y: 445 };
    } else {
      a = { x: 390, y: 445 - unit * 300 };
      b = { x: 390, y: 385 - unit * 190 };
    }
    drawPartialPath(
      ctx,
      [a, b],
      smoothstep(index * 0.02, 0.38 + index * 0.02, t),
      index % 3 === 0 ? accent : secondary,
      2.4,
      0.72 * reveal,
      { blur: 8 },
    );
    const particle = {
      x: a.x + (b.x - a.x) * ((t * 0.7 + index * 0.13) % 1),
      y: a.y + (b.y - a.y) * ((t * 0.7 + index * 0.13) % 1),
    };
    drawGlowOrb(ctx, particle.x, particle.y, 4, gold, 0.5 * reveal);
  }
  drawLabel(ctx, scene.params?.centerText ?? "power maintains the boundary", 640, 488, {
    color: theme.structure,
    size: 15,
    alpha: 0.78 * reveal,
  });
}

function practiceFolds(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const labels = scene.params?.labels ?? ["body", "breath", "mantra", "attention"];
  const radii = [198, 158, 118, 78];
  const selected = scene.params?.focus ?? -1;
  for (let index = 0; index < radii.length; index += 1) {
    const focusAlpha = selected < 0 || selected === index ? 1 : 0.24;
    const radius = radii[index] + 8 * wave(t, 0.52, index * 0.18);
    drawEllipseRing(
      ctx,
      640,
      290,
      radius,
      radius * 0.58,
      index % 2 ? secondary : accent,
      reveal * focusAlpha * (0.38 + index * 0.12),
      selected === index ? 2.4 : 1.1,
      0.035 * wave(t, 0.4, index * 0.2),
    );
    drawLabel(ctx, labels[index], 640 + radius + 35, 290 - radius * 0.34, {
      color: index % 2 ? secondary : accent,
      size: selected === index ? 17 : 13,
      alpha: reveal * focusAlpha * 0.85,
    });
  }
  drawSilhouette(ctx, 640, 320, 0.72, secondary, 0.76 * reveal);
  drawGlowOrb(ctx, 640, 270, 28 + 3 * wave(t, 0.65), gold, 0.84 * reveal);
  const current = sampleCubic(
    { x: 640, y: 450 },
    { x: 500, y: 405 },
    { x: 760, y: 230 },
    { x: 640, y: 180 },
    160,
  );
  drawPartialPath(ctx, current, smoothstep(0.04, 0.72, t), gold, 2.1, 0.66 * reveal, { blur: 8 });
}

function upsurge(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const expansion = easeOutCubic(smoothstep(0.16, 0.72, t));
  const cx = 640;
  const cy = 290;
  fieldNodes(ctx, t, env, { count: 120, alpha: 0.1 + expansion * 0.28 });
  for (let index = 0; index < 20; index += 1) {
    const angle = (index / 20) * TAU;
    const inner = polar(cx, cy, 24 + 20 * expansion, angle);
    const outer = polar(cx, cy, 58 + 320 * expansion, angle + 0.04 * wave(t, 0.5, index / 20));
    drawPartialPath(
      ctx,
      [inner, outer],
      expansion,
      index % 3 === 0 ? accent : (index % 2 ? secondary : gold),
      index % 3 === 0 ? 2 : 0.9,
      reveal * (0.25 + 0.35 * expansion),
      { blur: 7 },
    );
  }
  drawGlowOrb(ctx, cx, cy, 48 + 28 * expansion, gold, 0.84 * reveal);
  drawRing(ctx, cx, cy, 85 + 170 * expansion, accent, 0.42 * reveal, 1.5);
  drawLotus(ctx, cx, cy, 62 + 95 * expansion, {
    petals: 12,
    rotation: t * 0.08,
    stroke: secondary,
    fill: "rgba(52,66,107,0.025)",
    alpha: 0.74 * reveal,
  });
  drawLabel(ctx, scene.params?.centerText ?? "उद्यमः", cx, cy + 5, {
    devanagari: true,
    size: 30,
    color: secondary,
    alpha: reveal,
  });
}

function waveOcean(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const baseline = 345;
  const points = [];
  for (let index = 0; index <= 240; index += 1) {
    const x = 120 + index * (1040 / 240);
    const envelope = Math.sin((index / 240) * Math.PI);
    const y = baseline - Math.sin(index * 0.075 - t * TAU * 0.42) * 98 * envelope;
    points.push({ x, y });
  }
  ctx.save();
  ctx.globalAlpha = 0.07 * reveal;
  ctx.fillStyle = secondary;
  ctx.beginPath();
  ctx.moveTo(points[0].x, baseline);
  for (const point of points) ctx.lineTo(point.x, point.y);
  ctx.lineTo(points.at(-1).x, 465);
  ctx.lineTo(points[0].x, 465);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
  drawGlowingPath(ctx, points, secondary, 2.4, 0.72 * reveal, { blur: 8 });
  drawPartialPath(ctx, [{ x: 120, y: baseline }, { x: 1160, y: baseline }], 1, gold, 1.1, 0.35 * reveal, { blur: 4 });
  const amount = (t * 0.28 + 0.4) % 1;
  const crest = pointAlong(points, amount);
  drawGlowOrb(ctx, crest.x, crest.y, 13, accent, 0.72 * reveal);
  drawLabel(ctx, scene.params?.waveText ?? "form", crest.x, crest.y - 36, {
    color: accent,
    size: 14,
    alpha: 0.8 * reveal,
  });
  drawLabel(ctx, scene.params?.oceanText ?? "one water", 640, 485, {
    color: secondary,
    size: 16,
    alpha: 0.82 * reveal,
  });
}

function texturesDisplay(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const labels = scene.params?.labels ?? ["color", "sound", "memory", "thought", "grief", "delight"];
  const localColors = [accent, secondary, gold, theme.structure, "#61845f", "#bf6e84"];
  for (let index = 0; index < labels.length; index += 1) {
    const angle = -Math.PI / 2 + (index / labels.length) * TAU + t * 0.06;
    const radius = 205 + 18 * wave(t, 0.45, index / labels.length);
    const point = polar(640, 290, radius, angle);
    drawGlowOrb(ctx, point.x, point.y, 24 + index * 2, localColors[index % localColors.length], 0.62 * reveal);
    drawRing(ctx, point.x, point.y, 42, localColors[index % localColors.length], 0.42 * reveal, 1.1);
    drawLabel(ctx, labels[index], point.x, point.y + 62, {
      color: localColors[index % localColors.length],
      size: 13,
      alpha: 0.76 * reveal,
    });
    drawGlowingPath(ctx, [{ x: 640, y: 290 }, point], localColors[index % localColors.length], 0.9, 0.2 * reveal, { blur: 4 });
  }
  fieldCore(ctx, t, theme, gold, reveal, 40);
}

function limitationReversal(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const reversed = easeInOutCubic(smoothstep(0.35, 0.8, t));
  const labels = scene.params?.labels ?? ["cannot", "unknown", "want", "passing"];
  const positions = [
    { x: 390, y: 220 },
    { x: 890, y: 220 },
    { x: 390, y: 390 },
    { x: 890, y: 390 },
  ];
  for (let index = 0; index < positions.length; index += 1) {
    const point = positions[index];
    drawRing(ctx, point.x, point.y, 56 + 8 * wave(t, 0.5, index * 0.17), index % 2 ? secondary : accent, 0.62 * reveal, 1.4);
    drawGlowOrb(ctx, point.x, point.y, 13 + 9 * reversed, gold, (0.4 + 0.35 * reversed) * reveal);
    drawLabel(ctx, labels[index], point.x, point.y + 82, {
      color: index % 2 ? secondary : accent,
      size: 14,
      alpha: 0.82 * reveal,
    });
    drawPartialPath(
      ctx,
      [point, { x: 640, y: 300 }],
      reversed,
      gold,
      1.4,
      0.5 * reveal,
      { blur: 6 },
    );
  }
  drawGlowOrb(ctx, 640, 300, 30 + 35 * reversed, gold, 0.84 * reveal);
  drawRing(ctx, 640, 300, 84 + 82 * reversed, secondary, 0.4 * reveal, 1.2);
  drawLabel(ctx, scene.params?.centerText ?? "known", 640, 304, {
    color: theme.ink,
    size: 16,
    alpha: reveal,
  });
}

function openingFist(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const opening = easeInOutCubic(smoothstep(0.18, 0.82, t));
  const cx = 640;
  const cy = 292;
  for (let index = 0; index < 5; index += 1) {
    const baseAngle = -Math.PI * 0.9 + index * (Math.PI * 0.45);
    const spread = opening * (index - 2) * 0.18;
    const radius = 70 + index * 18 + opening * 78;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(baseAngle + spread);
    ctx.globalAlpha = 0.74 * reveal;
    ctx.strokeStyle = index % 2 ? secondary : accent;
    ctx.lineWidth = 6 - index * 0.45;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.arc(0, 0, radius, -0.48, 0.48);
    ctx.stroke();
    ctx.restore();
  }
  drawGlowOrb(ctx, cx, cy, 34 + 78 * opening, gold, 0.9 * reveal);
  drawRing(ctx, cx, cy, 70 + 165 * opening, gold, 0.36 * reveal, 1.2);
  drawLabel(ctx, scene.params?.centerText ?? "I", cx, cy + 3, {
    color: secondary,
    size: 28,
    alpha: reveal,
  });
  if (opening > 0.45) {
    const arrow = polar(cx, cy, 230 * opening, -Math.PI / 2);
    drawArrowHead(ctx, arrow.x, arrow.y, -Math.PI / 2, 11, gold, 0.4 * reveal * opening);
  }
}

const staticRenderers = Object.freeze({
  "constraint-field": constraintField,
  "point-of-view": pointOfView,
  "five-lenses": fiveLenses,
  "local-power": localPower,
  "melody-time": melodyTime,
  "attention-beam": attentionBeam,
  "desire-orbit": desireOrbit,
  "smallness-cage": smallnessCage,
  "powered-prison": poweredPrison,
  "practice-folds": practiceFolds,
  upsurge,
  "wave-ocean": waveOcean,
  "textures-display": texturesDisplay,
  "limitation-reversal": limitationReversal,
  "opening-fist": openingFist,
});

const dynamicRenderers = new Map();
const dynamicRendererMetadata = new Map();

export function registerDynamicRenderer(nameOrDefinition, rendererArg, descriptionArg) {
  const definition = typeof nameOrDefinition === "object"
    ? nameOrDefinition
    : { name: nameOrDefinition, renderer: rendererArg, description: descriptionArg };
  const { name, renderer, description = "Dynamically registered semantic mechanism." } = definition;
  if (!name || typeof renderer !== "function") {
    throw new Error("registerDynamicRenderer requires a name and renderer function");
  }
  const existing = dynamicRenderers.get(name);
  if (staticRenderers[name]) throw new Error(`Renderer "${name}" is already built in`);
  if (existing) {
    if (existing === renderer) return;
    throw new Error(`Renderer "${name}" is already registered`);
  }
  dynamicRenderers.set(name, renderer);
  dynamicRendererMetadata.set(name, Object.freeze({ name, description }));
}

export function hasSemanticVisual(name) {
  return Boolean(staticRenderers[name] || dynamicRenderers.has(name) || systemVisualNames.includes(name));
}

export function listSemanticVisualNames() {
  return Object.freeze([...new Set([...semanticVisualNames, ...dynamicRenderers.keys()])]);
}

export function listDynamicSemanticVisuals() {
  return Object.freeze([...dynamicRendererMetadata.values()]);
}

export function getDynamicRenderer(name) {
  return dynamicRenderers.get(name) ?? null;
}

function findRenderer(name) {
  return staticRenderers[name] || dynamicRenderers.get(name) || null;
}

export function renderSemanticEssay(ctx, t, scene, env) {
  const name = scene.params?.visual;
  const renderer = findRenderer(name);
  if (!renderer && renderSystemVisual(ctx, t, scene, env)) return;
  if (!renderer) {
    throw new Error(
      `Unknown semantic visual "${name}" in scene "${scene.id}". ` +
      `Choose one of: ${listSemanticVisualNames().join(", ")}`,
    );
  }
  renderer(ctx, clamp(t), scene, env);
  if (Array.isArray(scene.overlays)) {
    renderAssetLayers(ctx, clamp(t), scene.overlays, env);
  }
}
