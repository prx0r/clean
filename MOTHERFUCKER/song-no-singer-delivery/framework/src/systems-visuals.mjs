import {
  TAU,
  clamp,
  easeInOutCubic,
  easeOutCubic,
  polar,
  pulse,
  regularPolygon,
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
  drawNode,
  drawPartialPath,
  drawRing,
  drawSilhouette,
  pointAlong,
} from "./primitives.mjs";
import { typography } from "./theme.mjs";

export const systemVisualNames = Object.freeze([
  "pattern-ensemble",
  "dependency-network",
  "umwelt-windows",
  "multiscale-agent",
  "boundary-gates",
  "memory-relay",
  "morphing-invariant",
  "reciprocal-reeds",
  "causal-vortex",
  "cooling-chain",
  "dialectic-bridge",
  "tuning-network",
  "source-compile-runtime",
  "recursive-observer",
  "open-question",
  "relational-birth",
]);

export const systemVisualDescriptions = Object.freeze({
  "pattern-ensemble": "One relational pattern remains recognizable across differently constrained performances.",
  "dependency-network": "Identity and activity arise from a pulsing network with no isolated root node.",
  "umwelt-windows": "Different interfaces select different worlds of relevance from a shared field.",
  "multiscale-agent": "Many local regulators coordinate into a temporary agent at a larger scale.",
  "boundary-gates": "A boundary creates selective access through distinct incoming and outgoing channels.",
  "memory-relay": "An earlier encounter alters a trace that a changed later system must interpret.",
  "morphing-invariant": "A stable relational skeleton persists while its material and geometry transform.",
  "reciprocal-reeds": "Self-model and world-model lean upon and continuously regenerate one another.",
  "causal-vortex": "Memory, prediction, attention, action, and changed world form a self-confirming loop.",
  "cooling-chain": "The same appearance and feeling continue after the ownership branch loses fuel.",
  "dialectic-bridge": "Two interpretations share evidence, diverge at a live question, and remain in contact.",
  "tuning-network": "Local systems alter one another’s conditions until new coordinated possibilities emerge.",
  "source-compile-runtime": "Reproducible pattern, inherited disposition, and living process exchange causal influence.",
  "recursive-observer": "The observer-model becomes another appearance inside the field it attempts to own.",
  "open-question": "Several explanations illuminate one unresolved centre without premature convergence.",
  "relational-birth": "Many inherited conditions coordinate into a new boundary and world of concern.",
});

function colors(scene, theme) {
  return {
    accent: scene.palette?.accent ?? theme.accent,
    secondary: scene.palette?.secondary ?? theme.secondary,
    gold: scene.palette?.luminous ?? theme.luminous,
  };
}

function revealIn(t) {
  return smoothstep(0, 0.06, t);
}

function line(ctx, a, b, color, alpha = 1, width = 1, blur = 4) {
  drawGlowingPath(ctx, [a, b], color, width, alpha, { blur });
}

function directedLine(ctx, a, b, color, alpha = 1, width = 1.4) {
  line(ctx, a, b, color, alpha, width, width * 4);
  const angle = Math.atan2(b.y - a.y, b.x - a.x);
  drawArrowHead(ctx, b.x, b.y, angle, 8, color, alpha);
}

function travellingOrb(ctx, path, t, color, alpha = 1, phase = 0, speed = 0.22) {
  const amount = (t * speed + phase) % 1;
  const point = pointAlong(path, amount);
  drawGlowOrb(ctx, point.x, point.y, 4.5, color, alpha * Math.sin(amount * Math.PI));
}

function patternEnsemble(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const base = scene.params?.pattern ?? [0, 2, 1, 3, 2, 0, 1];
  const labels = scene.params?.labels ?? ["piano", "cello", "voice", "toy keys"];
  const rowColors = [secondary, accent, gold, theme.structure];
  const left = 245;
  const right = 1035;
  for (let row = 0; row < 4; row += 1) {
    const cy = 150 + row * 96;
    const scale = [1, 0.72, 1.18, 0.5][row];
    const offset = [0, 12, -8, 5][row];
    const points = base.map((value, index) => ({
      x: left + index * ((right - left) / Math.max(1, base.length - 1)),
      y: cy - (value - 1.5) * 17 * scale + offset,
    }));
    drawPartialPath(
      ctx,
      points,
      smoothstep(0.02 + row * 0.04, 0.56 + row * 0.05, t),
      rowColors[row],
      row === 2 ? 2.1 : 1.35,
      reveal * (0.52 + row * 0.08),
      { blur: 6 },
    );
    for (const [index, point] of points.entries()) {
      drawNode(ctx, point.x, point.y, 3.5 + row * 0.35, {
        fill: theme.backgroundLight,
        stroke: rowColors[row],
        alpha: reveal * (0.52 + 0.42 * pulse(t, 0.45, index / points.length)),
        glow: index === Math.floor((t * 0.18 * points.length) % points.length) ? gold : undefined,
      });
    }
    drawLabel(ctx, labels[row], 160, cy, {
      color: rowColors[row],
      size: 14,
      alpha: 0.82 * reveal,
      align: "left",
    });
  }
  for (let index = 0; index < base.length; index += 1) {
    const x = left + index * ((right - left) / Math.max(1, base.length - 1));
    line(ctx, { x, y: 118 }, { x, y: 468 }, gold, 0.08 * reveal, 0.7, 2);
  }
  drawLabel(ctx, scene.params?.caption ?? "one relation · many performances", 640, 510, {
    color: theme.structure,
    style: typography.small,
    alpha: 0.78 * reveal,
  });
}

function dependencyNetwork(ctx, t, scene, env) {
  const { theme, random } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const count = scene.params?.count ?? 24;
  const points = Array.from({ length: count }, (_, index) => {
    const angle = random() * TAU;
    const radius = Math.sqrt(random());
    return {
      x: 640 + Math.cos(angle) * 430 * radius,
      y: 290 + Math.sin(angle) * 190 * radius,
      color: index % 5 === 0 ? accent : (index % 2 ? secondary : gold),
    };
  });
  for (let index = 0; index < points.length; index += 1) {
    for (const offset of [1, 4]) {
      const target = points[(index + offset) % points.length];
      line(ctx, points[index], target, index % 3 === 0 ? gold : secondary, 0.11 * reveal, 0.7, 2);
    }
  }
  for (const [index, point] of points.entries()) {
    drawNode(ctx, point.x, point.y, 3 + (index % 4), {
      fill: theme.backgroundLight,
      stroke: point.color,
      alpha: reveal * (0.55 + 0.35 * pulse(t, 0.55, index / count)),
      glow: index % 9 === 0 ? gold : undefined,
    });
  }
  for (let index = 0; index < 10; index += 1) {
    const a = points[index];
    const b = points[(index + 4) % points.length];
    travellingOrb(ctx, [a, b], t, index % 2 ? gold : accent, 0.55 * reveal, index / 10, 0.28);
  }
  drawRing(ctx, 640, 290, 235 + 8 * wave(t, 0.36), gold, 0.16 * reveal, 1);
  drawLabel(ctx, scene.params?.centerText ?? "no node stands alone", 640, 505, {
    color: theme.structure,
    size: 15,
    alpha: 0.8 * reveal,
  });
}

function umweltWindows(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const labels = scene.params?.labels ?? ["bacterium", "plant", "tick", "bat", "human"];
  const localColors = [gold, "#61845f", accent, secondary, theme.structure];
  for (let index = 0; index < labels.length; index += 1) {
    const x = 250 + index * 195;
    const focus = scene.params?.focus;
    const active = focus === undefined || focus === index;
    const alpha = reveal * (active ? 0.86 : 0.18);
    drawEllipseRing(ctx, x, 285, 72, 132, localColors[index], alpha, active ? 1.6 : 0.8);
    if (index === 0) {
      for (let dot = 0; dot < 8; dot += 1) {
        const point = polar(x, 285, 22 + dot * 6, dot * 1.9 + t);
        drawGlowOrb(ctx, point.x, point.y, 3, gold, 0.4 * alpha);
      }
    } else if (index === 1) {
      for (let ray = 0; ray < 7; ray += 1) {
        line(ctx, { x: x - 44 + ray * 14, y: 210 }, { x, y: 310 }, gold, 0.18 * alpha, 1, 3);
      }
    } else if (index === 2) {
      drawGlowOrb(ctx, x, 250, 20, accent, 0.62 * alpha);
      drawGlowOrb(ctx, x, 330, 11, secondary, 0.42 * alpha);
    } else if (index === 3) {
      for (let arc = 0; arc < 4; arc += 1) {
        drawEllipseRing(ctx, x, 285, 16 + arc * 14, 35 + arc * 12, secondary, (0.55 - arc * 0.09) * alpha, 1);
      }
    } else {
      for (let node = 0; node < 6; node += 1) {
        const point = polar(x, 285, 48, (node / 6) * TAU);
        drawNode(ctx, point.x, point.y, 4, {
          fill: theme.backgroundLight,
          stroke: node % 2 ? accent : secondary,
          alpha,
        });
      }
      drawGlowOrb(ctx, x, 285, 16, gold, 0.68 * alpha);
    }
    drawLabel(ctx, labels[index], x, 455, {
      color: localColors[index],
      size: active ? 15 : 12,
      alpha,
    });
  }
  line(ctx, { x: 150, y: 500 }, { x: 1130, y: 500 }, gold, 0.22 * reveal, 1, 3);
}

function multiscaleAgent(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const levels = scene.params?.levels ?? ["cell", "tissue", "animal", "person"];
  const radii = [58, 115, 180, 245];
  for (let level = 0; level < levels.length; level += 1) {
    const radius = radii[level] + 5 * wave(t, 0.42, level * 0.17);
    drawEllipseRing(ctx, 640, 288, radius, radius * 0.58, level % 2 ? secondary : accent, (0.62 - level * 0.08) * reveal, 1.2);
    const count = 6 + level * 4;
    for (let index = 0; index < count; index += 1) {
      const angle = (index / count) * TAU + t * 0.08 * (level % 2 ? -1 : 1);
      const point = { x: 640 + Math.cos(angle) * radius, y: 288 + Math.sin(angle) * radius * 0.58 };
      drawNode(ctx, point.x, point.y, 2.4 + level * 0.35, {
        fill: theme.backgroundLight,
        stroke: level % 2 ? secondary : accent,
        alpha: 0.62 * reveal,
      });
    }
    drawLabel(ctx, levels[level], 640 + radius + 38, 288 - radius * 0.32, {
      color: level % 2 ? secondary : accent,
      size: 13,
      alpha: 0.78 * reveal,
    });
  }
  drawGlowOrb(ctx, 640, 288, 36 + 6 * wave(t, 0.55), gold, 0.82 * reveal);
  const current = sampleCubic(
    { x: 640, y: 470 },
    { x: 500, y: 390 },
    { x: 780, y: 230 },
    { x: 640, y: 125 },
    160,
  );
  drawPartialPath(ctx, current, smoothstep(0.02, 0.72, t), gold, 2, 0.58 * reveal, { blur: 8 });
  travellingOrb(ctx, current, t, gold, 0.75 * reveal, 0, 0.35);
}

function boundaryGates(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const cx = 640;
  const cy = 290;
  const radius = 178;
  const gates = 10;
  for (let index = 0; index < gates; index += 1) {
    const angle = (index / gates) * TAU - Math.PI / 2;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(angle);
    ctx.globalAlpha = 0.72 * reveal;
    ctx.strokeStyle = index % 3 === 0 ? gold : (index % 2 ? accent : secondary);
    ctx.lineWidth = index % 3 === 0 ? 5 : 2;
    ctx.beginPath();
    ctx.arc(0, 0, radius, -0.2, 0.2);
    ctx.stroke();
    ctx.restore();
  }
  drawRing(ctx, cx, cy, radius - 10, secondary, 0.25 * reveal, 1);
  drawGlowOrb(ctx, cx, cy, 34, gold, 0.62 * reveal);
  for (let index = 0; index < 14; index += 1) {
    const angle = (index / 14) * TAU;
    const open = index % 3 === 0;
    const progress = (t * 0.26 + index / 14) % 1;
    const distance = open
      ? 255 - progress * 150
      : 250 - Math.sin(progress * Math.PI) * 52;
    const point = polar(cx, cy, distance, angle);
    drawGlowOrb(ctx, point.x, point.y, open ? 5 : 3.5, open ? gold : accent, 0.55 * reveal);
  }
  drawLabel(ctx, "what enters", 350, 470, { color: gold, size: 14, alpha: 0.72 * reveal });
  drawLabel(ctx, "what is excluded", 930, 470, { color: accent, size: 14, alpha: 0.72 * reveal });
}

function memoryRelay(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const earlier = { x: 300, y: 300 };
  const later = { x: 980, y: 300 };
  drawSilhouette(ctx, earlier.x, earlier.y + 25, 0.68, secondary, 0.8 * reveal);
  drawSilhouette(ctx, later.x, later.y + 25, 0.82, accent, 0.86 * reveal);
  drawGlowOrb(ctx, earlier.x, earlier.y - 10, 18, gold, 0.58 * reveal);
  drawGlowOrb(ctx, later.x, later.y - 10, 24, gold, 0.7 * reveal);
  const path = sampleCubic(
    { x: earlier.x + 58, y: earlier.y },
    { x: 470, y: 120 + 18 * wave(t, 0.35) },
    { x: 790, y: 455 - 18 * wave(t, 0.35) },
    { x: later.x - 62, y: later.y },
    180,
  );
  drawPartialPath(ctx, path, smoothstep(0.03, 0.65, t), gold, 2, 0.7 * reveal, { blur: 8 });
  for (let index = 0; index < 9; index += 1) {
    travellingOrb(ctx, path, t, index % 2 ? accent : secondary, 0.48 * reveal, index / 9, 0.18);
  }
  const knot = pointAlong(path, 0.5);
  drawEllipseRing(ctx, knot.x, knot.y, 58, 35, accent, 0.58 * reveal, 1.4, t * 0.08);
  drawLabel(ctx, scene.params?.leftText ?? "earlier system", earlier.x, 465, {
    color: secondary,
    size: 14,
    alpha: 0.78 * reveal,
  });
  drawLabel(ctx, scene.params?.rightText ?? "changed receiver", later.x, 465, {
    color: accent,
    size: 14,
    alpha: 0.78 * reveal,
  });
  drawLabel(ctx, scene.params?.centerText ?? "trace interpreted now", 640, 500, {
    color: theme.structure,
    size: 14,
    alpha: 0.78 * reveal,
  });
}

function morphingInvariant(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const labels = scene.params?.labels ?? ["flame", "melody", "river", "person"];
  const centers = [260, 510, 770, 1020];
  for (let panel = 0; panel < centers.length; panel += 1) {
    const cx = centers[panel];
    const cy = 290;
    const sides = 3 + panel;
    const outer = regularPolygon(cx, cy, 105, sides, -Math.PI / 2 + t * 0.08 * (panel % 2 ? -1 : 1));
    drawPartialPath(
      ctx,
      [...outer, outer[0]],
      smoothstep(0.02 + panel * 0.04, 0.62 + panel * 0.04, t),
      panel % 2 ? accent : secondary,
      1.2,
      0.5 * reveal,
      { blur: 4 },
    );
    const skeleton = [
      { x: cx - 48, y: cy + 24 },
      { x: cx - 16, y: cy - 35 },
      { x: cx + 22, y: cy + 18 },
      { x: cx + 52, y: cy - 25 },
    ];
    drawGlowingPath(ctx, skeleton, gold, 2, 0.72 * reveal, { blur: 7 });
    for (const point of skeleton) {
      drawNode(ctx, point.x, point.y, 4, {
        fill: theme.backgroundLight,
        stroke: gold,
        alpha: 0.84 * reveal,
      });
    }
    drawLabel(ctx, labels[panel], cx, 455, {
      color: panel % 2 ? accent : secondary,
      size: 14,
      alpha: 0.8 * reveal,
    });
  }
  line(ctx, { x: 165, y: 505 }, { x: 1115, y: 505 }, gold, 0.28 * reveal, 1.1, 4);
}

function reciprocalReeds(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const sway = 8 * wave(t, 0.38);
  for (let index = 0; index < 7; index += 1) {
    const leftBase = { x: 300 + index * 25, y: 445 };
    const leftTop = { x: 560 + index * 8 + sway, y: 135 };
    const rightBase = { x: 980 - index * 25, y: 445 };
    const rightTop = { x: 720 - index * 8 - sway, y: 135 };
    line(ctx, leftBase, leftTop, secondary, 0.38 * reveal, 1.4, 4);
    line(ctx, rightBase, rightTop, accent, 0.38 * reveal, 1.4, 4);
  }
  const junction = { x: 640, y: 255 };
  drawGlowOrb(ctx, junction.x, junction.y, 28 + 5 * wave(t, 0.5), gold, 0.78 * reveal);
  const upper = sampleCubic(
    { x: 390, y: 330 },
    { x: 505, y: 150 },
    { x: 775, y: 150 },
    { x: 890, y: 330 },
    150,
  );
  const lower = sampleCubic(
    { x: 890, y: 360 },
    { x: 770, y: 505 },
    { x: 510, y: 505 },
    { x: 390, y: 360 },
    150,
  );
  drawGlowingPath(ctx, upper, gold, 1.5, 0.48 * reveal, { blur: 6 });
  drawGlowingPath(ctx, lower, secondary, 1.3, 0.4 * reveal, { blur: 5 });
  for (let index = 0; index < 10; index += 1) {
    travellingOrb(ctx, index % 2 ? upper : lower, t, index % 2 ? gold : accent, 0.5 * reveal, index / 10, 0.3);
  }
  drawLabel(ctx, scene.params?.leftText ?? "self-model", 340, 490, {
    color: secondary,
    size: 15,
    alpha: 0.82 * reveal,
  });
  drawLabel(ctx, scene.params?.rightText ?? "world-model", 940, 490, {
    color: accent,
    size: 15,
    alpha: 0.82 * reveal,
  });
}

function causalVortex(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const labels = scene.params?.labels ?? [
    "memory",
    "expectation",
    "attention",
    "interpretation",
    "action",
    "changed world",
    "new memory",
  ];
  const points = labels.map((label, index) => ({
    ...polar(640, 290, 220, -Math.PI / 2 + (index / labels.length) * TAU),
    label,
  }));
  for (let index = 0; index < points.length; index += 1) {
    const a = points[index];
    const b = points[(index + 1) % points.length];
    directedLine(ctx, a, b, index % 2 ? secondary : accent, 0.42 * reveal, 1.2);
    drawNode(ctx, a.x, a.y, 8, {
      fill: theme.backgroundLight,
      stroke: index % 2 ? secondary : accent,
      alpha: 0.82 * reveal,
      glow: index === Math.floor((t * 0.35 * labels.length) % labels.length) ? gold : undefined,
    });
    const align = a.x < 640 ? "right" : "left";
    const dx = a.x < 640 ? -20 : 20;
    drawLabel(ctx, a.label, a.x + dx, a.y, {
      color: theme.structure,
      size: 13,
      alpha: 0.78 * reveal,
      align,
    });
  }
  for (let index = 0; index < 9; index += 1) {
    const amount = (t * 0.2 + index / 9) % 1;
    const angle = -Math.PI / 2 + amount * TAU;
    const point = polar(640, 290, 220, angle);
    drawGlowOrb(ctx, point.x, point.y, 4.5, gold, 0.55 * reveal);
  }
  drawGlowOrb(ctx, 640, 290, 38 + 6 * wave(t, 0.48), gold, 0.66 * reveal);
  drawLabel(ctx, scene.params?.centerText ?? "model confirms model", 640, 294, {
    color: theme.ink,
    size: 15,
    alpha: reveal,
  });
}

function coolingChain(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const cooling = easeInOutCubic(smoothstep(0.26, 0.82, t));
  const top = scene.params?.before ?? ["appearance", "feeling", "mine", "grasping", "becoming"];
  const lower = scene.params?.after ?? ["appearance", "feeling", "clear response"];
  const drawChain = (labels, y, coolBranch) => {
    const left = 235;
    const right = 1045;
    const spacing = (right - left) / Math.max(1, labels.length - 1);
    for (let index = 0; index < labels.length; index += 1) {
      const x = left + index * spacing;
      const owned = coolBranch && index >= 2;
      const alpha = reveal * (owned ? 1 - cooling * 0.82 : 0.82);
      drawNode(ctx, x, y, 12, {
        fill: theme.backgroundLight,
        stroke: owned ? accent : secondary,
        alpha,
        glow: index === Math.floor((t * 0.18 * labels.length) % labels.length) ? gold : undefined,
      });
      drawLabel(ctx, labels[index], x, y + 45, {
        color: owned ? accent : secondary,
        size: 13,
        alpha,
      });
      if (index < labels.length - 1) {
        directedLine(
          ctx,
          { x: x + 18, y },
          { x: x + spacing - 18, y },
          owned ? accent : gold,
          alpha * 0.55,
          1.1,
        );
      }
    }
  };
  drawChain(top, 225, true);
  drawChain(lower, 405, false);
  const x = 640;
  drawPartialPath(ctx, [{ x, y: 265 }, { x, y: 360 }], cooling, gold, 2, 0.65 * reveal, { blur: 7 });
  drawLabel(ctx, "ownership cools", 640, 330, {
    color: accent,
    size: 15,
    alpha: cooling * reveal,
  });
}

function dialecticBridge(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const left = { x: 390, y: 280 };
  const right = { x: 890, y: 280 };
  for (let ring = 0; ring < 4; ring += 1) {
    drawRing(ctx, left.x, left.y, 70 + ring * 25, secondary, (0.42 - ring * 0.07) * reveal, 1.1);
    drawRing(ctx, right.x, right.y, 70 + ring * 25, accent, (0.42 - ring * 0.07) * reveal, 1.1);
  }
  drawGlowOrb(ctx, left.x, left.y, 28, secondary, 0.62 * reveal);
  drawGlowOrb(ctx, right.x, right.y, 28, accent, 0.62 * reveal);
  const common = sampleCubic(
    { x: left.x, y: 405 },
    { x: 520, y: 470 },
    { x: 760, y: 470 },
    { x: right.x, y: 405 },
    150,
  );
  drawGlowingPath(ctx, common, gold, 2, 0.58 * reveal, { blur: 7 });
  const bridge = sampleCubic(
    { x: left.x + 92, y: 250 },
    { x: 560, y: 130 + 15 * wave(t, 0.42) },
    { x: 720, y: 130 - 15 * wave(t, 0.42) },
    { x: right.x - 92, y: 250 },
    150,
  );
  drawPartialPath(ctx, bridge, smoothstep(0.06, 0.68, t), gold, 1.4, 0.46 * reveal, { blur: 6 });
  for (let index = 0; index < 10; index += 1) {
    travellingOrb(ctx, index % 2 ? bridge : common, t, index % 2 ? gold : secondary, 0.48 * reveal, index / 10, 0.24);
  }
  drawLabel(ctx, scene.params?.leftText ?? "Madhyamaka", left.x, 490, {
    color: secondary,
    size: 16,
    alpha: 0.84 * reveal,
  });
  drawLabel(ctx, scene.params?.rightText ?? "Pratyabhijñā", right.x, 490, {
    color: accent,
    size: 16,
    alpha: 0.84 * reveal,
  });
  drawLabel(ctx, scene.params?.centerText ?? "what is the status of appearing?", 640, 300, {
    color: theme.structure,
    size: 14,
    alpha: 0.82 * reveal,
  });
}

function tuningNetwork(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const nodes = [
    { x: 640, y: 175 },
    { x: 420, y: 225 },
    { x: 860, y: 225 },
    { x: 325, y: 390 },
    { x: 545, y: 430 },
    { x: 735, y: 430 },
    { x: 955, y: 390 },
  ];
  const edges = [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6], [4, 5], [3, 4], [5, 6]];
  for (const [index, edge] of edges.entries()) {
    const [a, b] = edge.map((nodeIndex) => nodes[nodeIndex]);
    line(ctx, a, b, index % 2 ? secondary : gold, 0.2 * reveal, 1, 4);
    travellingOrb(ctx, [a, b], t, index % 3 === 0 ? accent : gold, 0.5 * reveal, index / edges.length, 0.24);
  }
  for (const [index, node] of nodes.entries()) {
    const damaged = index === (scene.params?.damaged ?? 3);
    drawRing(ctx, node.x, node.y, damaged ? 29 : 36, damaged ? accent : secondary, 0.62 * reveal, damaged ? 2.4 : 1.2);
    const waveform = Array.from({ length: 18 }, (_, pointIndex) => ({
      x: node.x - 24 + pointIndex * (48 / 17),
      y: node.y + Math.sin(pointIndex * 0.9 + t * TAU * 0.55 + index) * (damaged ? 11 : 6),
    }));
    drawGlowingPath(ctx, waveform, damaged ? accent : gold, damaged ? 2 : 1.1, 0.66 * reveal, { blur: 5 });
  }
  drawLabel(ctx, scene.params?.centerText ?? "conditions tune conditions", 640, 505, {
    color: theme.structure,
    size: 15,
    alpha: 0.8 * reveal,
  });
}

function sourceCompileRuntime(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const columns = [
    { x: 300, label: "source pattern", color: gold },
    { x: 640, label: "compiled disposition", color: secondary },
    { x: 980, label: "runtime", color: accent },
  ];
  for (const [index, column] of columns.entries()) {
    ctx.save();
    ctx.globalAlpha = 0.12 * reveal;
    ctx.fillStyle = column.color;
    ctx.beginPath();
    ctx.roundRect(column.x - 115, 155, 230, 275, 18);
    ctx.fill();
    ctx.restore();
    drawRing(ctx, column.x, 285, 72 + 4 * wave(t, 0.42, index * 0.17), column.color, 0.62 * reveal, 1.4);
    const count = 5 + index * 2;
    for (let node = 0; node < count; node += 1) {
      const point = polar(column.x, 285, 45, (node / count) * TAU + t * 0.08 * (index % 2 ? -1 : 1));
      drawNode(ctx, point.x, point.y, 3.5, {
        fill: theme.backgroundLight,
        stroke: column.color,
        alpha: 0.72 * reveal,
      });
    }
    drawLabel(ctx, column.label, column.x, 475, {
      color: column.color,
      size: 15,
      alpha: 0.84 * reveal,
    });
  }
  directedLine(ctx, { x: 390, y: 285 }, { x: 535, y: 285 }, gold, 0.58 * reveal, 1.5);
  directedLine(ctx, { x: 745, y: 285 }, { x: 875, y: 285 }, secondary, 0.58 * reveal, 1.5);
  const feedback = sampleCubic(
    { x: 980, y: 385 },
    { x: 900, y: 535 },
    { x: 700, y: 535 },
    { x: 640, y: 385 },
    120,
  );
  drawPartialPath(ctx, feedback, smoothstep(0.22, 0.82, t), accent, 1.8, 0.62 * reveal, { blur: 7 });
  const end = feedback.at(-1);
  const beforeEnd = feedback.at(-2);
  drawArrowHead(ctx, end.x, end.y, Math.atan2(end.y - beforeEnd.y, end.x - beforeEnd.x), 9, accent, 0.62 * reveal);
  travellingOrb(ctx, feedback, t, gold, 0.6 * reveal, 0, 0.25);
}

function recursiveObserver(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const inclusion = easeInOutCubic(smoothstep(0.3, 0.82, t));
  drawSilhouette(ctx, 640, 340, 0.82, secondary, 0.82 * reveal);
  drawGlowOrb(ctx, 640, 250, 23, gold, 0.72 * reveal);
  const models = [
    { x: 480, y: 190, label: "world" },
    { x: 640, y: 145, label: "body" },
    { x: 800, y: 190, label: "uncertainty" },
    { x: 760, y: 355, label: "ownership" },
  ];
  for (const [index, model] of models.entries()) {
    drawRing(ctx, model.x, model.y, 42, index === 3 ? accent : secondary, 0.52 * reveal, 1.2);
    drawLabel(ctx, model.label, model.x, model.y + 62, {
      color: index === 3 ? accent : secondary,
      size: 12,
      alpha: 0.76 * reveal,
    });
    line(ctx, { x: 640, y: 260 }, model, index === 3 ? accent : gold, 0.26 * reveal, 1, 4);
  }
  const observerX = 420 + inclusion * 220;
  const observerY = 390 - inclusion * 120;
  drawRing(ctx, observerX, observerY, 48 - inclusion * 18, accent, 0.72 * reveal, 1.8);
  drawLabel(ctx, "observer-model", observerX, observerY, {
    color: accent,
    size: 13,
    alpha: 0.84 * reveal,
  });
  drawRing(ctx, 640, 290, 250 + 12 * wave(t, 0.38), gold, 0.18 * reveal, 1);
  drawLabel(ctx, scene.params?.centerText ?? "the knower is also in the field", 640, 510, {
    color: theme.structure,
    size: 15,
    alpha: 0.8 * reveal,
  });
}

function openQuestion(ctx, t, scene, env) {
  const { theme } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const labels = scene.params?.labels ?? ["science", "Madhyamaka", "Pratyabhijñā", "illusionism"];
  const localColors = [theme.structure, secondary, accent, gold];
  const centre = { x: 640, y: 290 };
  for (let index = 0; index < labels.length; index += 1) {
    const angle = -Math.PI / 2 + (index / labels.length) * TAU;
    const point = polar(centre.x, centre.y, 225, angle);
    drawRing(ctx, point.x, point.y, 58 + 5 * wave(t, 0.42, index * 0.19), localColors[index], 0.62 * reveal, 1.3);
    drawGlowOrb(ctx, point.x, point.y, 13, localColors[index], 0.48 * reveal);
    drawLabel(ctx, labels[index], point.x, point.y + (index === 0 ? -82 : 82), {
      color: localColors[index],
      size: 14,
      alpha: 0.8 * reveal,
    });
    const path = sampleCubic(
      point,
      polar(centre.x, centre.y, 145, angle + 0.35),
      polar(centre.x, centre.y, 90, angle - 0.25),
      centre,
      90,
    );
    drawPartialPath(ctx, path, 0.72 + 0.16 * wave(t, 0.35, index * 0.2), localColors[index], 1.2, 0.34 * reveal, { blur: 5 });
  }
  drawGlowOrb(ctx, centre.x, centre.y, 42 + 8 * wave(t, 0.5), gold, 0.72 * reveal);
  drawRing(ctx, centre.x, centre.y, 96, accent, 0.42 * reveal, 1.3);
  drawLabel(ctx, scene.params?.centerText ?? "?", centre.x, centre.y + 3, {
    color: theme.ink,
    size: 32,
    alpha: reveal,
  });
}

function relationalBirth(ctx, t, scene, env) {
  const { theme, random } = env;
  const { accent, secondary, gold } = colors(scene, theme);
  const reveal = revealIn(t);
  const forming = easeOutCubic(smoothstep(0.12, 0.62, t));
  const centre = { x: 640, y: 290 };
  const conditions = Array.from({ length: 18 }, (_, index) => {
    const angle = (index / 18) * TAU + random() * 0.14;
    return {
      ...polar(centre.x, centre.y, 250 + random() * 90, angle),
      color: index % 3 === 0 ? accent : (index % 2 ? secondary : gold),
    };
  });
  for (const [index, condition] of conditions.entries()) {
    const target = polar(centre.x, centre.y, 105, (index / conditions.length) * TAU);
    const current = {
      x: condition.x + (target.x - condition.x) * forming,
      y: condition.y + (target.y - condition.y) * forming,
    };
    line(ctx, condition, current, condition.color, 0.25 * reveal, 1, 4);
    drawNode(ctx, current.x, current.y, 3.5, {
      fill: theme.backgroundLight,
      stroke: condition.color,
      alpha: 0.68 * reveal,
    });
  }
  drawRing(ctx, centre.x, centre.y, 108 + 5 * wave(t, 0.45), accent, 0.72 * reveal * forming, 2);
  drawRing(ctx, centre.x, centre.y, 72, secondary, 0.48 * reveal * forming, 1.2);
  drawGlowOrb(ctx, centre.x, centre.y, 30 + 12 * forming, gold, 0.82 * reveal);
  for (let index = 0; index < 8; index += 1) {
    const angle = (index / 8) * TAU + t * 0.08;
    const inner = polar(centre.x, centre.y, 115, angle);
    const outer = polar(centre.x, centre.y, 190 + 18 * wave(t, 0.42, index / 8), angle);
    drawPartialPath(ctx, [inner, outer], forming, index % 2 ? secondary : gold, 1.1, 0.32 * reveal, { blur: 4 });
  }
  drawLabel(ctx, scene.params?.centerText ?? "a new centre of concern", 640, 500, {
    color: theme.structure,
    size: 15,
    alpha: 0.82 * reveal,
  });
}

export const systemVisualRenderers = Object.freeze({
  "pattern-ensemble": patternEnsemble,
  "dependency-network": dependencyNetwork,
  "umwelt-windows": umweltWindows,
  "multiscale-agent": multiscaleAgent,
  "boundary-gates": boundaryGates,
  "memory-relay": memoryRelay,
  "morphing-invariant": morphingInvariant,
  "reciprocal-reeds": reciprocalReeds,
  "causal-vortex": causalVortex,
  "cooling-chain": coolingChain,
  "dialectic-bridge": dialecticBridge,
  "tuning-network": tuningNetwork,
  "source-compile-runtime": sourceCompileRuntime,
  "recursive-observer": recursiveObserver,
  "open-question": openQuestion,
  "relational-birth": relationalBirth,
});

export function renderSystemVisual(ctx, t, scene, env) {
  const renderer = systemVisualRenderers[scene.params?.visual];
  if (!renderer) return false;
  renderer(ctx, clamp(t), scene, env);
  return true;
}
