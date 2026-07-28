import { TAU, clamp, easeOutCubic, rgba, smoothstep, wave } from "../math.mjs";
import { drawArrowHead, drawGlowOrb, drawLabel, drawNode, drawPartialPath, drawRing } from "../primitives.mjs";

const CX = 640, CY = 316, W = 1280, H = 720;

const FONT_SERIF = '"Source Serif 4", "EB Garamond", serif';
const FONT_MATH = '"KaTeX Math", "Source Serif 4", serif';

const C = {
  ink: "#171a1e",
  muted: "#7a7f88",
  blue: "#2d6685",
  red: "#a43e46",
  green: "#3e7857",
  gold: "#a9782f",
  paper: "#fbfaf6",
  dark: "#0d1117",
  warm: "#f5f0e6",
};

function astate(env) {
  return { rms: clamp(env.audio?.rms ?? 0), onset: clamp(env.audio?.onset ?? 0) };
}

function isActive(u, sec) {
  if (!u.at) return true;
  const end = u.end ?? (u.at + (u.duration ?? 1.5));
  return sec >= u.at && sec < end;
}

function localT(u, sec) {
  if (!u.at) return 1;
  const dur = u.duration ?? 1.5;
  return clamp((sec - u.at) / dur);
}

function alpha(t) {
  return smoothstep(0, 0.06, t);
}

function fadeOut(t) {
  return 1 - smoothstep(0.85, 1, t);
}

function typeColor(type) {
  switch (type) {
    case "controversial": return C.red;
    case "resolution": return C.green;
    case "emphasize": case "statement": return C.ink;
    case "term": return C.gold;
    case "aside": return C.muted;
    case "math": return C.blue;
    default: return C.ink;
  }
}

function typeSize(type) {
  switch (type) {
    case "statement": return 36;
    case "emphasize": return 30;
    case "controversial": return 30;
    case "resolution": return 32;
    case "term": return 28;
    case "say": return 24;
    case "math": return 26;
    case "aside": return 19;
    default: return 24;
  }
}

function typeWeight(type) {
  switch (type) {
    case "statement": case "emphasize": case "controversial": case "resolution": return 700;
    default: return 400;
  }
}

function fontString(weight, size, italic) {
  return `${italic ? "italic " : ""}${weight} ${size}px ${italic ? FONT_MATH : FONT_SERIF}`;
}

function renderText(ctx, text, x, y, size, color, a, align, weight) {
  ctx.save();
  ctx.globalAlpha = a;
  ctx.font = fontString(weight ?? 400, size);
  ctx.textAlign = align ?? "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = rgba(color, a);
  ctx.fillText(text, x, y);
  ctx.restore();
}

function renderStyledText(ctx, text, x, y, size, color, a, align) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
  let cx = x;
  let totalW = 0;
  ctx.textBaseline = "middle";
  ctx.textAlign = "left";
  const segments = [];
  for (const p of parts) {
    if (!p) continue;
    if (p.startsWith("**") && p.endsWith("**")) {
      segments.push({ t: p.slice(2, -2), w: 700, i: false });
    } else if (p.startsWith("*") && p.endsWith("*")) {
      segments.push({ t: p.slice(1, -1), w: 400, i: true });
    } else {
      segments.push({ t: p, w: 400, i: false });
    }
  }
  for (const s of segments) {
    ctx.font = fontString(s.w, size, s.i);
    totalW += ctx.measureText(s.t).width;
  }
  ctx.fillStyle = rgba(color, a);
  cx = align === "center" ? x - totalW / 2 : x;
  for (const s of segments) {
    ctx.font = fontString(s.w, size, s.i);
    ctx.fillText(s.t, cx, y);
    cx += ctx.measureText(s.t).width;
  }
}

// Backgrounds
const BG = {
  "dark-field": function (ctx, t, env) {
    const a = astate(env);
    const grad = ctx.createRadialGradient(CX, CY - 40, 30, CX, CY - 40, 700);
    grad.addColorStop(0, "#1a2035");
    grad.addColorStop(0.5, "#0d1117");
    grad.addColorStop(1, "#06080f");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);
    for (let i = 0; i < 80; i++) {
      const x = (i * 137.5 + 50) % W;
      const y = (i * 89.3 + 20) % H;
      const r = 0.3 + 0.7 * Math.sin(i * 1.7 + t * 0.3) ** 2;
      ctx.fillStyle = `rgba(255,255,255,${0.015 * r})`;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, TAU);
      ctx.fill();
    }
    if (a.onset > 0.06) {
      ctx.fillStyle = `rgba(255,200,150,${a.onset * 0.02})`;
      ctx.fillRect(0, 0, W, H);
    }
  },

  "clean-white": function (ctx, t, env) {
    ctx.fillStyle = C.paper;
    ctx.fillRect(0, 0, W, H);
    const grad = ctx.createRadialGradient(CX, CY, 20, CX, CY, 650);
    grad.addColorStop(0, "rgba(255,255,255,0.7)");
    grad.addColorStop(1, "rgba(221,228,226,0.06)");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);
  },

  "warm-glow": function (ctx, t, env) {
    const a = astate(env);
    const grad = ctx.createRadialGradient(CX, CY + 60, 40, CX, CY + 60, 680);
    grad.addColorStop(0, "#f5e6c8");
    grad.addColorStop(0.4, "#f0dbb5");
    grad.addColorStop(1, "#e8d0a0");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);
    const g2 = ctx.createRadialGradient(CX, CY - 80, 10, CX, CY - 80, 400);
    g2.addColorStop(0, `rgba(169,120,47,${0.04 + a.rms * 0.02})`);
    g2.addColorStop(1, "rgba(169,120,47,0)");
    ctx.fillStyle = g2;
    ctx.fillRect(0, 0, W, H);
    for (let i = 0; i < 3; i++) {
      drawRing(ctx, CX, CY, 200 + i * 140 + 5 * wave(t + i * 0.2, 0.1), C.gold, 0.03 + a.rms * 0.01, 0.5);
    }
  },

  "tension-split": function (ctx, t, env) {
    const grad = ctx.createLinearGradient(0, 0, W, 0);
    grad.addColorStop(0, "#1a1a24");
    grad.addColorStop(0.45, "#1a1a24");
    grad.addColorStop(0.5, "#2a2a35");
    grad.addColorStop(0.55, "#f5f0e6");
    grad.addColorStop(1, "#f5f0e6");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(CX, 60);
    ctx.lineTo(CX, H - 60);
    ctx.stroke();
  },

  "resolve": function (ctx, t, env) {
    const a = astate(env);
    const grad = ctx.createRadialGradient(CX, CY, 50, CX, CY, 700);
    grad.addColorStop(0, "#f8f4ec");
    grad.addColorStop(0.5, "#f0e8d8");
    grad.addColorStop(1, "#e8dcc8");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);
    drawRing(ctx, CX, CY, 280 + 8 * wave(t, 0.08), C.gold, 0.04 + a.rms * 0.015, 0.6);
    drawRing(ctx, CX, CY, 140 + 4 * wave(t + 0.3, 0.1), C.gold, 0.025, 0.5);
  },
};

// Utterance renderers
function renderSay(ctx, t, u, env) {
  const a = alpha(t) * fadeOut(t);
  renderStyledText(ctx, u.text, CX, u.y ?? CY, u.size ?? typeSize("say"), typeColor("say"), a, "center");
}

function renderEmphasize(ctx, t, u, env) {
  const a = alpha(t) * fadeOut(t);
  const scale = 1 + 0.03 * easeOutCubic(smoothstep(0, 0.2, t));
  ctx.save();
  ctx.translate(CX, u.y ?? CY);
  ctx.scale(scale, scale);
  renderStyledText(ctx, u.text, 0, 0, u.size ?? typeSize("emphasize"), typeColor("emphasize"), a, "center");
  ctx.restore();
}

function renderStatement(ctx, t, u, env) {
  const a = alpha(t) * fadeOut(t);
  const scale = 1 + 0.02 * easeOutCubic(smoothstep(0, 0.15, t));
  ctx.save();
  ctx.translate(CX, u.y ?? CY);
  ctx.scale(scale, scale);
  renderStyledText(ctx, u.text, 0, 0, u.size ?? typeSize("statement"), typeColor("statement"), a, "center");
  ctx.restore();
  const ringA = a * 0.06 * smoothstep(0.3, 0.5, t);
  drawRing(ctx, CX, u.y ?? CY, 280, C.gold, ringA, 0.7);
}

function renderAside(ctx, t, u, env) {
  const a = alpha(t) * fadeOut(t);
  renderStyledText(ctx, u.text, CX, u.y ?? (CY + 80), u.size ?? typeSize("aside"), typeColor("aside"), a, "center");
}

function renderControversial(ctx, t, u, env) {
  const a = alpha(t) * fadeOut(t);
  const scale = 1 + 0.04 * easeOutCubic(smoothstep(0, 0.25, t));
  ctx.save();
  ctx.translate(CX, u.y ?? CY);
  ctx.scale(scale, scale);
  renderStyledText(ctx, u.text, 0, 0, u.size ?? typeSize("controversial"), C.red, a, "center");
  ctx.restore();
  if (t > 0.2) {
    const strikeT = smoothstep(0.2, 0.35, t);
    ctx.strokeStyle = rgba(C.red, a * strikeT * 0.5);
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(200, (u.y ?? CY));
    ctx.lineTo(1080, (u.y ?? CY));
    ctx.stroke();
  }
}

function renderResolution(ctx, t, u, env) {
  const a = alpha(t) * fadeOut(t);
  const scale = 1 + 0.02 * easeOutCubic(smoothstep(0, 0.15, t));
  ctx.save();
  ctx.translate(CX, u.y ?? CY);
  ctx.scale(scale, scale);
  renderStyledText(ctx, u.text, 0, 0, u.size ?? typeSize("resolution"), C.green, a, "center");
  ctx.restore();
  const ringR = 200 + 8 * wave(t, 0.15);
  drawRing(ctx, CX, u.y ?? CY, ringR, C.gold, a * 0.04 * smoothstep(0.2, 0.4, t), 0.6);
  drawGlowOrb(ctx, CX, (u.y ?? CY) - 50, 6, C.gold, a * 0.08);
}

function renderTerm(ctx, t, u, env) {
  const a = alpha(t) * fadeOut(t);
  const y = u.y ?? CY;
  ctx.save();
  ctx.globalAlpha = a;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  const tx = CX - (u.devanagari ? 100 : 0);
  ctx.font = fontString(700, u.size ?? 30);
  ctx.fillStyle = rgba(C.gold, a);
  ctx.fillText(u.term ?? u.text, tx, y - 20);
  if (u.devanagari) {
    ctx.font = fontString(500, 16, false);
    ctx.fillStyle = rgba(C.muted, a * 0.7);
    ctx.fillText(u.term ?? u.text, tx, y + 30);
    ctx.font = fontString(500, 24, false);
    ctx.fillStyle = rgba(C.ink, a * 0.85);
    ctx.fillText(u.devanagari, CX + 100, y);
  }
  if (u.translation) {
    ctx.font = fontString(400, 18, false);
    ctx.fillStyle = rgba(C.muted, a * 0.6);
    ctx.fillText(u.translation, tx, y + (u.devanagari ? 65 : 45));
  }
  drawRing(ctx, tx, y - 20, 80, C.gold, a * 0.06, 0.5);
  ctx.restore();
}

function renderMath(ctx, t, u, env) {
  const a = alpha(t) * fadeOut(t);
  const y = u.y ?? CY;
  ctx.save();
  ctx.globalAlpha = a;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.font = fontString(400, u.size ?? 22, true);
  ctx.fillStyle = rgba(C.blue, a);
  ctx.fillText(u.text, CX, y);
  if (u.sub) {
    ctx.font = fontString(400, 16, false);
    ctx.fillStyle = rgba(C.muted, a * 0.6);
    ctx.fillText(u.sub, CX, y + 35);
  }
  ctx.restore();
}

function renderPause(ctx, t, u, env) {
  const a = astate(env);
  const dotR = 2 + a.rms * 6;
  ctx.fillStyle = rgba(C.muted, 0.15);
  ctx.beginPath();
  ctx.arc(CX, CY + 120, dotR, 0, TAU);
  ctx.fill();
}

// Diagram renderers
function diagramTriangle(ctx, t, u, env) {
  const nodes = u.nodes ?? [];
  if (nodes.length < 3) return;
  const a = alpha(t);
  ctx.save();
  ctx.globalAlpha = a;
  for (let i = 0; i < 3; i++) {
    const n = nodes[i];
    const nx = CX + (n.x ?? 0);
    const ny = CY + (n.y ?? 0);
    const prev = nodes[(i + 2) % 3];
    const pnx = CX + (prev.x ?? 0);
    const pny = CY + (prev.y ?? 0);
    ctx.strokeStyle = rgba(n.color ?? C.muted, a * 0.25);
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(nx, ny);
    ctx.lineTo(pnx, pny);
    ctx.stroke();
  }
  for (const n of nodes) {
    const nx = CX + (n.x ?? 0);
    const ny = CY + (n.y ?? 0);
    drawGlowOrb(ctx, nx, ny, 4, n.color ?? C.blue, a * 0.3);
    ctx.font = fontString(600, 18, false);
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = rgba(n.color ?? C.ink, a * 0.92);
    ctx.fillText(n.label, nx, ny - 28);
    if (n.relation) {
      ctx.font = fontString(400, 13, true);
      ctx.fillStyle = rgba(C.muted, a * 0.5);
      ctx.fillText(n.relation, nx, ny + 26);
    }
  }
  if (u.caption) {
    ctx.font = fontString(400, 17, false);
    ctx.textAlign = "center";
    ctx.fillStyle = rgba(C.muted, a * 0.5);
    ctx.fillText(u.caption, CX, CY + 210);
  }
  ctx.restore();
}

function diagramSplit(ctx, t, u, env) {
  const a = alpha(t);
  ctx.save();
  ctx.globalAlpha = a;
  ctx.strokeStyle = rgba(C.muted, a * 0.12);
  ctx.lineWidth = 0.4;
  ctx.beginPath();
  ctx.moveTo(CX, 100);
  ctx.lineTo(CX, H - 100);
  ctx.stroke();
  if (u.left) {
    ctx.font = fontString(600, u.leftSize ?? 20, false);
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = rgba(u.leftColor ?? C.blue, a * 0.85);
    ctx.fillText(u.left, CX - 240, CY);
    if (u.leftSub) {
      ctx.font = fontString(400, 15, false);
      ctx.fillStyle = rgba(C.muted, a * 0.55);
      ctx.fillText(u.leftSub, CX - 240, CY + 40);
    }
  }
  if (u.right) {
    ctx.font = fontString(600, u.rightSize ?? 20, false);
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = rgba(u.rightColor ?? C.ink, a * 0.85);
    ctx.fillText(u.right, CX + 240, CY);
    if (u.rightSub) {
      ctx.font = fontString(400, 15, false);
      ctx.fillStyle = rgba(C.muted, a * 0.55);
      ctx.fillText(u.rightSub, CX + 240, CY + 40);
    }
  }
  if (u.caption) {
    ctx.font = fontString(400, 16, false);
    ctx.textAlign = "center";
    ctx.fillStyle = rgba(C.muted, a * 0.45);
    ctx.fillText(u.caption, CX, CY + 180);
  }
  ctx.restore();
}

function diagramStack(ctx, t, u, env) {
  const items = u.items ?? [];
  const a = alpha(t);
  ctx.save();
  ctx.globalAlpha = a;
  const startY = CY - ((items.length - 1) * 36) / 2;
  for (let i = 0; i < items.length; i++) {
    const itemA = smoothstep(0.08 + i * 0.1, 0.15 + i * 0.1, t);
    if (itemA <= 0) continue;
    const y = startY + i * 36;
    ctx.font = fontString(400, 18, false);
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = rgba(u.itemColor ?? C.ink, a * itemA * 0.85);
    ctx.fillText(items[i], CX, y);
    if (i > 0 && itemA > 0.5) {
      ctx.strokeStyle = rgba(C.gold, a * itemA * 0.15);
      ctx.lineWidth = 0.3;
      ctx.beginPath();
      ctx.moveTo(CX - 80, y - 18);
      ctx.lineTo(CX + 80, y - 18);
      ctx.stroke();
    }
  }
  if (u.caption) {
    ctx.font = fontString(400, 15, false);
    ctx.textAlign = "center";
    ctx.fillStyle = rgba(C.muted, a * 0.45);
    ctx.fillText(u.caption, CX, startY + items.length * 36 + 30);
  }
  ctx.restore();
}

function diagramFlow(ctx, t, u, env) {
  const steps = u.steps ?? [];
  const a = alpha(t);
  ctx.save();
  ctx.globalAlpha = a;
  const spacing = Math.min(180, 900 / Math.max(steps.length, 1));
  const startX = CX - ((steps.length - 1) * spacing) / 2;
  for (let i = 0; i < steps.length; i++) {
    const stepA = smoothstep(0.05 + i * 0.1, 0.15 + i * 0.1, t);
    if (stepA <= 0) continue;
    const x = startX + i * spacing;
    drawGlowOrb(ctx, x, CY, 3, u.color ?? C.blue, a * stepA * 0.2);
    ctx.font = fontString(500, 16, false);
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = rgba(u.color ?? C.ink, a * stepA * 0.85);
    ctx.fillText(steps[i], x, CY - 30);
    if (i.stepSub) {
      ctx.font = fontString(400, 13, false);
      ctx.fillStyle = rgba(C.muted, a * stepA * 0.5);
      ctx.fillText(i.stepSub, x, CY);
    }
    if (i > 0 && stepA > 0.4) {
      const ax = startX + (i - 0.5) * spacing;
      ctx.fillStyle = rgba(C.muted, a * 0.2);
      ctx.beginPath();
      ctx.moveTo(startX + (i - 1) * spacing + 50, CY - 30);
      ctx.lineTo(startX + i * spacing - 50, CY - 30);
      ctx.stroke();
    }
  }
  ctx.restore();
}

function diagramScale(ctx, t, u, env) {
  const a = alpha(t);
  ctx.save();
  ctx.globalAlpha = a;
  const y = u.y ?? CY;
  ctx.strokeStyle = rgba(C.muted, a * 0.2);
  ctx.lineWidth = 0.4;
  ctx.beginPath();
  ctx.moveTo(180, y);
  ctx.lineTo(1100, y);
  ctx.stroke();
  if (u.left) {
    ctx.font = fontString(600, u.leftSize ?? 18, false);
    ctx.textAlign = "left";
    ctx.textBaseline = "top";
    ctx.fillStyle = rgba(u.leftColor ?? C.blue, a * 0.85);
    ctx.fillText(u.left, 190, y + 12);
  }
  if (u.right) {
    ctx.font = fontString(600, u.rightSize ?? 18, false);
    ctx.textAlign = "right";
    ctx.textBaseline = "top";
    ctx.fillStyle = rgba(u.rightColor ?? C.red, a * 0.85);
    ctx.fillText(u.right, 1090, y + 12);
  }
  if (u.center) {
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";
    ctx.font = fontString(400, 14, false);
    ctx.fillStyle = rgba(C.muted, a * 0.5);
    ctx.fillText(u.center, CX, y - 8);
  }
  ctx.restore();
}

const DIAGRAMS = {
  triangle: diagramTriangle,
  split: diagramSplit,
  stack: diagramStack,
  flow: diagramFlow,
  scale: diagramScale,
};

function renderDiagram(ctx, t, u, env) {
  const fn = DIAGRAMS[u.diagram];
  if (fn) fn(ctx, t, u, env);
}

const UTTERANCE_RENDERERS = {
  say: renderSay,
  emphasize: renderEmphasize,
  statement: renderStatement,
  aside: renderAside,
  controversial: renderControversial,
  resolution: renderResolution,
  term: renderTerm,
  math: renderMath,
  pause: renderPause,
  diagram: renderDiagram,
};

export function renderArgumentDiagramV3(ctx, t, scene, env) {
  const seconds = env.sceneSeconds ?? (t * (scene.duration ?? 12));
  const bg = scene.params?.background ?? "clean-white";
  const utterances = scene.params?.utterances ?? [];

  const bgFn = BG[bg];
  if (bgFn) bgFn(ctx, t, env);

  for (const u of utterances) {
    if (!isActive(u, seconds)) continue;
    const lt = localT(u, seconds);
    const type = u.type ?? "say";
    const fn = UTTERANCE_RENDERERS[type];
    if (fn) fn(ctx, lt, u, env);
  }
}
