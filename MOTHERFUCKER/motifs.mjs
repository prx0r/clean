import {
  TAU,
  clamp,
  easeInOutCubic,
  easeOutCubic,
  hashString,
  mixColor,
  polar,
  pulse,
  regularPolygon,
  sampleCubic,
  seededRandom,
  smoothstep,
  stagger,
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
  drawRadialWords,
  drawRing,
  drawSilhouette,
  pointAlong,
} from "./primitives.mjs";
import { palette, typography } from "./theme.mjs";
import { renderComposition } from "./composition.mjs";
import {
  renderSemanticEssay,
  semanticVisualDescriptions,
} from "./semantic-visuals.mjs";
import { renderArgumentDisplay } from "./src/argument-display.mjs";
import { renderArgumentDiagram } from "./src/argument-diagram.mjs";
import { renderArgumentDiagramV2 } from "./src/argument-diagram-v2.mjs";
import { renderArgumentDiagramV3 } from "./src/argument-diagram-v3.mjs";
import { renderArgumentDiagramV4 } from "./src/argument-diagram-v4.mjs";
import { renderArgumentDiagramV5 } from "./src/argument-diagram-v5.mjs";

function sceneColor(scene, key, fallback) {
  return scene.palette?.[key] ?? scene.params?.[key] ?? fallback;
}

function heartLattice(ctx, t, scene, env) {
  const { theme } = env;
  const accent = sceneColor(scene, "accent", theme.accent);
  const secondary = sceneColor(scene, "secondary", theme.secondary);
  const gold = sceneColor(scene, "luminous", theme.luminous);
  const reveal = easeOutCubic(smoothstep(0.01, 0.25, t));
  const cx = 640;
  const cy = 294;
  const phase = t * TAU;
  const density = clamp(scene.params?.density ?? 0.72, 0.3, 1);
  const columns = Math.round(5 + density * 4);
  const rows = Math.round(4 + density * 4);

  const nodes = [];
  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      const nx = columns === 1 ? 0 : column / (columns - 1);
      const ny = rows === 1 ? 0 : row / (rows - 1);
      const baseX = 330 + nx * 620;
      const baseY = 150 + ny * 295;
      const distance = Math.hypot(baseX - cx, baseY - cy);
      const displacement = Math.sin(distance * 0.036 - phase * 2.2) * 7.5;
      const angle = Math.atan2(baseY - cy, baseX - cx);
      nodes.push({
        x: baseX + Math.cos(angle) * displacement,
        y: baseY + Math.sin(angle) * displacement * 0.55,
        distance,
      });
    }
  }

  ctx.save();
  ctx.globalAlpha = reveal;
  for (let index = 0; index < nodes.length; index += 1) {
    const node = nodes[index];
    const shimmer = 0.42 + 0.38 * pulse(t, 1.25, index * 0.071);
    const radius = 1.3 + 1.5 * (1 - clamp(node.distance / 390));
    drawNode(ctx, node.x, node.y, radius, {
      fill: theme.backgroundLight,
      stroke: mixColor(secondary, gold, 1 - clamp(node.distance / 390)),
      alpha: shimmer,
      width: 0.8,
    });
  }

  const spokeCount = 12;
  for (let index = 0; index < spokeCount; index += 1) {
    const angle = -Math.PI / 2 + (index / spokeCount) * TAU + phase * 0.025;
    const endpoint = polar(cx, cy, 188 + 8 * wave(t, 0.8, index * 0.08), angle);
    drawPartialPath(
      ctx,
      [{ x: cx, y: cy }, endpoint],
      smoothstep(index * 0.015, 0.46 + index * 0.015, t),
      index % 2 === 0 ? gold : secondary,
      1.2,
      0.34,
      { blur: 4 },
    );
  }

  const breath = 1 + 0.045 * wave(t, 0.72);
  drawGlowOrb(ctx, cx, cy, 42 * breath, gold, 0.78 * reveal);
  drawRing(ctx, cx, cy, 73 * breath, gold, 0.58 * reveal, 1.25);
  drawRing(ctx, cx, cy, 104 / breath, secondary, 0.36 * reveal, 1);
  drawLotus(ctx, cx, cy + 6, 90 * breath, {
    petals: 12,
    rotation: phase * 0.018,
    stroke: accent,
    fill: `rgba(191,110,132,${0.055 + 0.025 * pulse(t, 1)})`,
    alpha: 0.9 * reveal,
    lineWidth: 1.2,
  });
  drawLabel(ctx, scene.params?.centerText ?? "हृ", cx, cy + 4, {
    devanagari: true,
    size: 37,
    color: secondary,
    alpha: reveal,
  });
  drawLabel(ctx, "the field is gathered without becoming smaller", cx, 495, {
    style: typography.small,
    color: theme.structure,
    alpha: 0.8 * reveal,
  });
  ctx.restore();
}

function attentionLens(ctx, t, scene, env) {
  const { theme } = env;
  const accent = sceneColor(scene, "accent", theme.accent);
  const secondary = sceneColor(scene, "secondary", theme.secondary);
  const gold = sceneColor(scene, "luminous", theme.luminous);
  const reveal = smoothstep(0.02, 0.22, t);
  const cx = 640;
  const cy = 300;
  const phase = t * TAU;

  const horizon = sampleCubic(
    { x: 175, y: 326 },
    { x: 410, y: 286 + 16 * wave(t, 0.6) },
    { x: 870, y: 316 - 14 * wave(t, 0.6) },
    { x: 1105, y: 326 },
    180,
  );
  drawPartialPath(ctx, horizon, easeOutCubic(smoothstep(0.02, 0.5, t)), theme.structure, 1.4, 0.52);

  for (let index = 0; index < 7; index += 1) {
    const spread = 42 + index * 25;
    const lensBreath = 1 + 0.035 * wave(t, 0.8, index * 0.11);
    drawEllipseRing(
      ctx,
      cx,
      cy,
      spread * 0.66 * lensBreath,
      spread * 1.24,
      index % 2 ? secondary : accent,
      (0.12 + index * 0.032) * reveal,
      index === 0 ? 2 : 1,
      phase * 0.008 * (index % 2 ? -1 : 1),
    );
  }

  const leftPath = sampleCubic(
    { x: 155, y: 215 },
    { x: 345, y: 165 },
    { x: 480, y: 420 },
    { x: cx, y: cy },
    140,
  );
  const rightPath = sampleCubic(
    { x: 1125, y: 405 },
    { x: 940, y: 470 },
    { x: 795, y: 175 },
    { x: cx, y: cy },
    140,
  );
  drawGlowingPath(ctx, leftPath, secondary, 1.2, 0.24 * reveal, { blur: 5 });
  drawGlowingPath(ctx, rightPath, accent, 1.2, 0.24 * reveal, { blur: 5 });

  const speed = scene.params?.speed ?? 0.23;
  for (let index = 0; index < 14; index += 1) {
    const amount = (t * speed * 4 + index / 14) % 1;
    const path = index % 2 ? leftPath : rightPath;
    const point = pointAlong(path, amount);
    const alpha = Math.sin(amount * Math.PI) * reveal;
    drawGlowOrb(ctx, point.x, point.y, 5 + 2 * pulse(t, 1.8, index * 0.07), index % 2 ? secondary : accent, 0.58 * alpha);
  }

  drawGlowOrb(ctx, cx, cy, 34 + 4 * wave(t, 0.75), gold, 0.82 * reveal);
  drawRing(ctx, cx, cy, 20 + 3 * wave(t, 0.75, 0.25), accent, 0.8 * reveal, 1.5);
  drawLabel(ctx, scene.params?.centerText ?? "अवधानम्", cx, cy + 78, {
    devanagari: true,
    size: 27,
    color: secondary,
    alpha: reveal,
  });
  drawLabel(ctx, "a horizon appears wherever awareness selects a relation", cx, 500, {
    style: typography.small,
    color: theme.structure,
    alpha: 0.8 * reveal,
  });
}

function phonemeForge(ctx, t, scene, env) {
  const { theme } = env;
  const accent = sceneColor(scene, "accent", theme.accent);
  const secondary = sceneColor(scene, "secondary", theme.secondary);
  const gold = sceneColor(scene, "luminous", theme.luminous);
  const reveal = smoothstep(0.01, 0.2, t);
  const phase = t * TAU;
  const phonemes = scene.params?.phonemes ?? ["अ", "इ", "उ", "ऋ", "क", "च", "ट", "त", "प", "य", "श", "ह"];
  const ribbon = sampleCubic(
    { x: 155, y: 355 },
    { x: 325, y: 115 + 20 * wave(t, 0.7) },
    { x: 565, y: 505 - 16 * wave(t, 0.7) },
    { x: 690, y: 292 },
    180,
  );
  drawPartialPath(ctx, ribbon, smoothstep(0.01, 0.58, t), secondary, 2.2, 0.64, { blur: 7 });

  for (let index = 0; index < phonemes.length; index += 1) {
    const base = index / Math.max(1, phonemes.length - 1);
    const amount = clamp(base + 0.016 * wave(t, 0.9, index * 0.13));
    const point = pointAlong(ribbon, amount);
    const alpha = stagger(index, phonemes.length, t, 0.35);
    drawGlowOrb(ctx, point.x, point.y, 10, index % 3 === 0 ? gold : secondary, 0.34 * alpha);
    drawLabel(ctx, phonemes[index], point.x, point.y + 1, {
      devanagari: true,
      size: 20,
      color: index % 3 === 0 ? accent : secondary,
      alpha,
    });
  }

  const forgeX = 890;
  const forgeY = 300;
  drawGlowOrb(ctx, forgeX, forgeY, 46 + 5 * wave(t, 0.72), gold, 0.78 * reveal);
  const shapes = [
    { points: regularPolygon(forgeX, forgeY, 116, 3, -Math.PI / 2), color: accent },
    { points: regularPolygon(forgeX, forgeY, 88, 4, Math.PI / 4 + phase * 0.014), color: secondary },
    { points: regularPolygon(forgeX, forgeY, 60, 6, phase * -0.02), color: gold },
  ];
  for (let index = 0; index < shapes.length; index += 1) {
    const closed = [...shapes[index].points, shapes[index].points[0]];
    drawPartialPath(
      ctx,
      closed,
      smoothstep(0.24 + index * 0.08, 0.72 + index * 0.06, t),
      shapes[index].color,
      1.6,
      0.7,
      { blur: 5 },
    );
  }

  for (let index = 0; index < 8; index += 1) {
    const angle = (index / 8) * TAU + phase * 0.12;
    const point = polar(forgeX, forgeY, 148, angle);
    drawNode(ctx, point.x, point.y, 3.4, {
      fill: theme.backgroundLight,
      stroke: index % 2 ? accent : secondary,
      alpha: 0.75 * reveal,
      glow: index % 2 ? accent : gold,
    });
  }
  drawLabel(ctx, "वाक्", forgeX, forgeY + 4, {
    devanagari: true,
    size: 34,
    color: accent,
    alpha: reveal,
  });
  drawLabel(ctx, "sound does not decorate form — it specifies a path into form", 640, 500, {
    style: typography.small,
    color: theme.structure,
    alpha: 0.8 * reveal,
  });
}

function reflexiveMirror(ctx, t, scene, env) {
  const { theme } = env;
  const accent = sceneColor(scene, "accent", theme.accent);
  const secondary = sceneColor(scene, "secondary", theme.secondary);
  const gold = sceneColor(scene, "luminous", theme.luminous);
  const reveal = smoothstep(0.01, 0.2, t);
  const phase = t * TAU;
  const left = { x: 390, y: 295 };
  const right = { x: 890, y: 295 };

  for (let index = 0; index < 4; index += 1) {
    const breath = 1 + 0.035 * wave(t, 0.7, index * 0.15);
    drawRing(ctx, left.x, left.y, (94 + index * 22) * breath, secondary, (0.32 - index * 0.045) * reveal, 1.2);
    drawRing(ctx, right.x, right.y, (94 + index * 22) / breath, accent, (0.32 - index * 0.045) * reveal, 1.2);
  }
  drawSilhouette(ctx, left.x, left.y + 22, 0.78, secondary, 0.9 * reveal);
  drawLotus(ctx, right.x, right.y + 20, 77, {
    petals: 10,
    rotation: phase * 0.015,
    stroke: accent,
    fill: "rgba(191,110,132,0.06)",
    alpha: reveal,
  });
  drawGlowOrb(ctx, right.x, right.y - 8, 23 + 3 * wave(t, 0.8), gold, 0.7 * reveal);

  const upper = sampleCubic(
    { x: left.x + 118, y: left.y - 22 },
    { x: 585, y: 128 + 14 * wave(t, 0.72) },
    { x: 700, y: 128 - 14 * wave(t, 0.72) },
    { x: right.x - 118, y: right.y - 22 },
    150,
  );
  const lower = sampleCubic(
    { x: right.x - 118, y: right.y + 34 },
    { x: 705, y: 465 + 10 * wave(t, 0.72, 0.5) },
    { x: 575, y: 465 - 10 * wave(t, 0.72, 0.5) },
    { x: left.x + 118, y: left.y + 34 },
    150,
  );
  drawPartialPath(ctx, upper, smoothstep(0.02, 0.55, t), gold, 2.2, 0.62, { blur: 8 });
  drawPartialPath(ctx, lower, smoothstep(0.16, 0.72, t), accent, 2.2, 0.52, { blur: 8 });

  for (let index = 0; index < 12; index += 1) {
    const amount = (t * 0.92 + index / 12) % 1;
    const path = index % 2 ? upper : lower;
    const point = pointAlong(path, amount);
    drawGlowOrb(ctx, point.x, point.y, 4.5, index % 2 ? gold : accent, 0.5 * Math.sin(amount * Math.PI) * reveal);
  }
  drawLabel(ctx, "aham", left.x, 475, { color: secondary, size: 17, alpha: 0.85 * reveal });
  drawLabel(ctx, "idam", right.x, 475, { color: accent, size: 17, alpha: 0.85 * reveal });
  drawLabel(ctx, "विमर्शः", 640, 291, {
    devanagari: true,
    size: 27,
    color: theme.structure,
    alpha: reveal,
  });
  drawLabel(ctx, "the world is disclosed through a circuit in which awareness meets itself", 640, 510, {
    style: typography.small,
    color: theme.structure,
    alpha: 0.8 * reveal,
  });
}

function returnCurrent(ctx, t, scene, env) {
  const { theme } = env;
  const accent = sceneColor(scene, "accent", theme.accent);
  const secondary = sceneColor(scene, "secondary", theme.secondary);
  const gold = sceneColor(scene, "luminous", theme.luminous);
  const reveal = smoothstep(0.01, 0.2, t);
  const nodeCount = scene.params?.nodes ?? 10;
  const nodes = Array.from({ length: nodeCount }, (_, index) => ({
    x: 640 + Math.sin(index * 1.27) * (165 - index * 8),
    y: 115 + index * 38,
  }));
  const descent = [];
  for (let index = 0; index < nodes.length - 1; index += 1) {
    descent.push(nodes[index], {
      x: (nodes[index].x + nodes[index + 1].x) / 2,
      y: (nodes[index].y + nodes[index + 1].y) / 2,
    });
  }
  descent.push(nodes.at(-1));
  const returnPath = [...descent].reverse().map((point, index) => ({
    x: point.x + Math.sin(index * 0.9 + t * TAU) * 10,
    y: point.y,
  }));

  drawPartialPath(ctx, descent, smoothstep(0.01, 0.54, t), secondary, 1.6, 0.44, { blur: 5 });
  drawPartialPath(ctx, returnPath, smoothstep(0.22, 0.86, t), accent, 2.8, 0.68, { blur: 9 });
  for (let index = 0; index < nodes.length; index += 1) {
    const alpha = stagger(index, nodes.length, t, 0.42);
    const radius = index === 0 ? 11 : 7.5;
    drawNode(ctx, nodes[index].x, nodes[index].y, radius, {
      fill: theme.backgroundLight,
      stroke: mixColor(secondary, gold, index / nodes.length),
      alpha,
      glow: index === 0 ? gold : undefined,
    });
    if (index > 0 && index < nodes.length - 1) {
      drawLabel(ctx, String(index + 1).padStart(2, "0"), nodes[index].x, nodes[index].y + 1, {
        style: typography.tiny,
        size: 9,
        color: theme.structure,
        alpha: 0.72 * alpha,
      });
    }
  }

  for (let index = 0; index < 9; index += 1) {
    const amount = (t * 0.78 + index / 9) % 1;
    const point = pointAlong(returnPath, amount);
    drawGlowOrb(ctx, point.x, point.y, 6, index % 3 === 0 ? gold : accent, 0.62 * Math.sin(amount * Math.PI) * reveal);
  }
  const top = returnPath.at(-1);
  const before = returnPath.at(-2);
  drawArrowHead(ctx, top.x, top.y, Math.atan2(top.y - before.y, top.x - before.x), 13, accent, reveal);
  drawGlowOrb(ctx, nodes[0].x, nodes[0].y, 35 + 4 * wave(t, 0.7), gold, 0.64 * reveal);
  drawLabel(ctx, "प्रत्यभिज्ञा", 930, 235, {
    devanagari: true,
    size: 31,
    color: accent,
    alpha: reveal,
  });
  drawLabel(ctx, "recognition does not leave the world; it reverses the direction of explanation", 640, 516, {
    style: typography.small,
    color: theme.structure,
    alpha: 0.8 * reveal,
  });
}

function closingHeartSeal(ctx, t, scene, env) {
  const { theme } = env;
  const accent = sceneColor(scene, "accent", theme.accent);
  const secondary = sceneColor(scene, "secondary", theme.secondary);
  const gold = sceneColor(scene, "luminous", theme.luminous);
  const reveal = smoothstep(0.01, 0.19, t);
  const cx = 640;
  const cy = 292;
  const phase = t * TAU;
  const radii = [222, 186, 146, 106];

  for (let index = 0; index < radii.length; index += 1) {
    const scale = 1 + 0.018 * wave(t, 0.56, index * 0.13);
    drawRing(
      ctx,
      cx,
      cy,
      radii[index] * scale,
      [theme.structure, gold, secondary, accent][index],
      (0.54 - index * 0.035) * stagger(index, radii.length, t, 0.24),
      index === 0 ? 2 : 1.35,
    );
  }

  const outerCount = scene.params?.outerNodes ?? 24;
  for (let index = 0; index < outerCount; index += 1) {
    const angle = -Math.PI / 2 + (index / outerCount) * TAU + phase * 0.018;
    const point = polar(cx, cy, 222, angle);
    const alpha = stagger(index, outerCount, t, 0.45);
    drawNode(ctx, point.x, point.y, index % 6 === 0 ? 6 : 3.6, {
      fill: theme.backgroundLight,
      stroke: index % 3 === 0 ? accent : secondary,
      alpha: 0.78 * alpha,
      glow: index % 6 === 0 ? gold : undefined,
    });
  }

  const spokes = 12;
  for (let index = 0; index < spokes; index += 1) {
    const angle = (index / spokes) * TAU + phase * -0.012;
    const inner = polar(cx, cy, 82, angle);
    const outer = polar(cx, cy, 205, angle + 0.08 * wave(t, 0.45, index / spokes));
    drawPartialPath(
      ctx,
      [inner, outer],
      smoothstep(0.12 + index * 0.012, 0.58 + index * 0.012, t),
      index % 2 ? secondary : gold,
      1,
      0.31,
      { blur: 4 },
    );
  }

  drawOrbitingNodes(ctx, cx, cy, 8, 151, 68, phase * 0.085, {
    color: accent,
    fill: theme.backgroundLight,
    radius: 4,
    alpha: 0.72 * reveal,
  });
  drawGlowOrb(ctx, cx, cy, 52 + 5 * wave(t, 0.62), gold, 0.82 * reveal);
  drawLotus(ctx, cx, cy + 4, 92, {
    petals: 12,
    rotation: phase * 0.022,
    stroke: accent,
    fill: "rgba(191,110,132,0.06)",
    alpha: reveal,
    lineWidth: 1.25,
  });
  drawLotus(ctx, cx, cy + 4, 55, {
    petals: 8,
    rotation: -phase * 0.03,
    stroke: secondary,
    fill: "rgba(52,66,107,0.035)",
    alpha: reveal,
    lineWidth: 1,
  });
  drawRadialWords(
    ctx,
    scene.params?.ringWords ?? ["cit", "spanda", "śakti", "vāc", "kāla", "deha", "jagat", "ānanda"],
    cx,
    cy,
    252,
    -Math.PI / 2 + phase * 0.004,
    {
      size: 12,
      color: theme.structure,
      alpha: 0.72 * reveal,
    },
  );
  drawLabel(ctx, scene.params?.centerText ?? "हृदयम्", cx, cy + 7, {
    devanagari: true,
    size: 34,
    color: secondary,
    alpha: reveal,
  });
  drawLabel(ctx, "the centre is not inside the whole — it is the whole appearing from here", cx, 535, {
    style: typography.small,
    color: theme.structure,
    alpha: 0.82 * reveal,
  });
}

export const motifRegistry = Object.freeze({
  composition: renderComposition,
  "semantic-essay": renderSemanticEssay,
  "logical-argument": renderArgumentDisplay,
  "argument-diagram": renderArgumentDiagram,
  "argument-diagram-v2": renderArgumentDiagramV2,
  "argument-diagram-v3": renderArgumentDiagramV3,
  "argument-diagram-v4": renderArgumentDiagramV4,
  "argument-diagram-v5": renderArgumentDiagramV5,
  "heart-lattice": heartLattice,
  "attention-lens": attentionLens,
  "phoneme-forge": phonemeForge,
  "reflexive-mirror": reflexiveMirror,
  "return-current": returnCurrent,
  "closing-heart-seal": closingHeartSeal,
});

export const motifDescriptions = Object.freeze({
  composition: "A declarative stack of style-locked Skia layers for original AI-authored scenes.",
  "semantic-essay": {
    description: "A controlled visual grammar for narration-locked philosophical essay films.",
    mechanisms: semanticVisualDescriptions,
  },
  "heart-lattice": "A breathing bindu-lotus gathers a responsive field without collapsing it.",
  "attention-lens": "Two particle currents and nested lenses enact selection and horizon formation.",
  "phoneme-forge": "A shaped Sanskrit phoneme current crystallizes into geometric form.",
  "reflexive-mirror": "Subject and world complete a circulating loop of self-disclosure.",
  "return-current": "A descending architecture is traversed in reverse by a luminous recognition current.",
  "closing-heart-seal": "A multi-ring contemplative seal integrates nodes, petals, words, and the heart-centre.",
});

export function renderMotif(ctx, t, scene, env) {
  const motif = motifRegistry[scene.motif];
  if (!motif) {
    throw new Error(`Unknown motif "${scene.motif}" in scene "${scene.id}"`);
  }
  ctx.save();
  motif(ctx, clamp(t), scene, {
    ...env,
    random: seededRandom((scene.seed ?? env.seed) ^ hashString(scene.id)),
  });
  ctx.restore();
}
