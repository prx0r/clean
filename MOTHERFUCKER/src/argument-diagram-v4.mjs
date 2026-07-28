import { smoothstep, wave } from "../math.mjs";
import { drawGlowOrb, drawRing } from "../primitives.mjs";

const CX = 640, CY = 316;

function drawSubtleField(ctx, t, theme) {
  const a = 0.04 + 0.02 * wave(t, 0.15);
  for (let i = 0; i < 3; i++) {
    const r = 200 + i * 160 + 30 * wave(t + i * 0.3, 0.1);
    ctx.save();
    ctx.globalAlpha = a * (0.5 + 0.5 * smoothstep(0, 0.3, t));
    ctx.strokeStyle = `rgba(90,98,106,${a * 0.25})`;
    ctx.lineWidth = 0.3;
    ctx.beginPath();
    ctx.arc(CX, CY, r, 0, 6.283 * smoothstep(0, 0.8, t));
    ctx.stroke();
    ctx.restore();
  }
}

const FONT = '"Source Serif 4", "EB Garamond", serif';
const MONO = "#1a1a1a";
const MUTED = "#5c626a";
const REFUTE = "#a43e46";
const RESOLVE = "#3e7857";

function resolveColor(move) {
  if (move.status === "refuted") return REFUTE;
  if (move.status === "resolved") return RESOLVE;
  if (move.status === "neutral") return MUTED;
  if (move.status === "highlight") return MONO;
  return move.color || MONO;
}

function styledText(ctx, text, x, y, baseSize, color, alpha, align) {
  const parts = text.split(/(\*[^*]+\*|\*\*[^*]+\*\*)/g);
  ctx.textBaseline = "middle";
  const segments = [];
  for (const part of parts) {
    if (!part) continue;
    if (part.startsWith("**") && part.endsWith("**")) {
      segments.push({ t: part.slice(2, -2), font: "700 " + baseSize + 'px ' + FONT });
    } else if (part.startsWith("*") && part.endsWith("*")) {
      segments.push({ t: part.slice(1, -1), font: baseSize + 'px "KaTeX Math", "Source Serif 4", serif' });
    } else {
      segments.push({ t: part, font: baseSize + 'px ' + FONT });
    }
  }
  let totalW = 0;
  for (const s of segments) { ctx.font = s.font; totalW += ctx.measureText(s.t).width; }
  const gap = 4 * Math.max(0, segments.length - 1);
  let cx = align === "center" ? x - (totalW + gap) / 2 : x;
  ctx.textAlign = "left";
  for (const s of segments) {
    ctx.font = s.font;
    ctx.fillStyle = `rgba(${hexToRgb(color)},${alpha})`;
    ctx.fillText(s.t, cx, y);
    cx += ctx.measureText(s.t).width + 4;
  }
}

function hexToRgb(hex) {
  const v = hex.replace("#", "");
  const h = v.length === 3 ? v.split("").map(c => c.repeat(2)).join("") : v;
  return `${parseInt(h.slice(0,2),16)},${parseInt(h.slice(2,4),16)},${parseInt(h.slice(4,6),16)}`;
}

function alpha(t) { return smoothstep(0, 0.1, t); }

// Re-implement v1 renderers with local timing
function renderClaim(ctx, t, move) {
  const a = alpha(t);
  const color = resolveColor(move);
  const size = move.size || 34;
  const scale = 0.94 + 0.06 * (1 - (1 - smoothstep(0, 0.2, t)) ** 3);
  const lines = move.text.split("\n");
  const lineH = size * 1.3;
  const startY = -(lines.length - 1) * lineH / 2;
  ctx.save();
  ctx.globalAlpha = a;
  ctx.translate(CX, CY);
  ctx.scale(scale, scale);
  for (let i = 0; i < lines.length; i++) {
    const la = smoothstep(0.03 + i * 0.06, 0.1 + i * 0.06, t);
    styledText(ctx, lines[i], 0, startY + i * lineH, size, color, a * la * 0.95, "center");
  }
  ctx.restore();
  if (move.status === "refuted" && t > 0.25) {
    const strikeT = smoothstep(0.25, 0.4, t);
    ctx.save();
    ctx.globalAlpha = a * strikeT * 0.5;
    ctx.strokeStyle = `rgba(${hexToRgb(REFUTE)},${a * strikeT * 0.4})`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(180, CY);
    ctx.lineTo(1100, CY);
    ctx.stroke();
    ctx.restore();
  }
}

function renderSubclaim(ctx, t, move) {
  const a = alpha(t);
  const size = move.size || 20;
  const color = resolveColor(move);
  const y = typeof move.y === "number" ? move.y : 440;
  ctx.save();
  ctx.globalAlpha = a;
  styledText(ctx, move.text, CX, y, size, color, a * 0.85, "center");
  ctx.restore();
}

function renderSideBySide(ctx, t, move) {
  const a = alpha(t);
  const size = move.size || 20;
  const colW = 380;
  const leftReveal = smoothstep(0, 0.25, t);
  const rightReveal = smoothstep(0.15, 0.4, t);
  ctx.save();
  if (leftReveal > 0) {
    ctx.globalAlpha = a * leftReveal;
    const lLines = move.left.split("\n");
    for (let i = 0; i < lLines.length; i++) {
      styledText(ctx, lLines[i], CX - colW / 2 - 20, CY - (lLines.length - 1) * size * 0.65 + i * size * 1.3,
        size, MUTED, a * leftReveal * 0.9, "center");
    }
    drawRing(ctx, CX - colW / 2 - 20, CY, 160 + 8 * wave(t, 0.2), MUTED, a * leftReveal * 0.06, 0.8);
  }
  if (rightReveal > 0) {
    ctx.globalAlpha = a * rightReveal;
    const rLines = move.right.split("\n");
    for (let i = 0; i < rLines.length; i++) {
      styledText(ctx, rLines[i], CX + colW / 2 + 20, CY - (rLines.length - 1) * size * 0.65 + i * size * 1.3,
        size, MONO, a * rightReveal * 0.9, "center");
    }
    drawRing(ctx, CX + colW / 2 + 20, CY, 160 + 8 * wave(t, 0.2), MONO, a * rightReveal * 0.06, 0.8);
  }
  if (leftReveal > 0.3 && rightReveal > 0.3) {
    ctx.globalAlpha = a * 0.12;
    ctx.strokeStyle = `rgba(90,98,106,${a * 0.12})`;
    ctx.lineWidth = 0.4;
    ctx.beginPath();
    ctx.moveTo(CX, 140);
    ctx.lineTo(CX, 500);
    ctx.stroke();
  }
  ctx.restore();
}

function renderBranch(ctx, t, move) {
  const a = alpha(t);
  const branches = move.branches || [];
  const spread = Math.min(420, 840 / Math.max(branches.length, 2));
  const topY = 280;
  const botY = 390;
  ctx.save();
  for (let i = 0; i < branches.length; i++) {
    const ba = smoothstep(0.05 + i * 0.12, 0.18 + i * 0.12, t);
    const x = CX + (i - (branches.length - 1) / 2) * spread;
    const c = branches[i].color || MUTED;
    if (ba > 0) {
      ctx.globalAlpha = a * ba;
      ctx.strokeStyle = `rgba(90,98,106,${a * ba * 0.3})`;
      ctx.lineWidth = 0.7;
      ctx.beginPath();
      ctx.moveTo(CX, topY + 10);
      ctx.quadraticCurveTo((CX + x) / 2, botY - 60, x, botY);
      ctx.stroke();
      ctx.font = '400 15px ' + FONT;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = `rgba(${hexToRgb(MONO)},${a * ba * 0.88})`;
      const lines = branches[i].label.split("\n");
      for (let li = 0; li < lines.length; li++) {
        ctx.fillText(lines[li], x, botY + 28 + li * 20);
      }
    }
  }
  ctx.restore();
}

function renderConverge(ctx, t, move) {
  const a = alpha(t);
  const size = move.size || 28;
  const color = resolveColor(move);
  const slideUp = 50 * (1 - (1 - smoothstep(0, 0.3, t)) ** 3);
  const lines = move.text.split("\n");
  const lineH = size * 1.3;
  ctx.save();
  ctx.globalAlpha = a;
  for (let i = 0; i < lines.length; i++) {
    const la = smoothstep(0.05 + i * 0.08, 0.12 + i * 0.08, t);
    ctx.globalAlpha = a * la;
    ctx.font = '400 ' + size + 'px ' + FONT;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = `rgba(${hexToRgb(color)},${a * la * 0.92})`;
    ctx.fillText(lines[i], CX, CY - slideUp + i * lineH - (lines.length - 1) * lineH / 2);
  }
  if (t > 0.25) {
    ctx.globalAlpha = a * 0.08;
    ctx.strokeStyle = `rgba(52,66,107,${a * 0.08})`;
    ctx.lineWidth = 0.4;
    ctx.beginPath();
    ctx.arc(CX, CY - slideUp, 240 + 10 * wave(t, 0.2), 0, 6.283 * smoothstep(0.25, 0.6, t));
    ctx.stroke();
  }
  ctx.restore();
}

function renderPremiseList(ctx, t, move) {
  const a = alpha(t);
  const ps = move.premises || [];
  const size = move.size || 18;
  const lineH = 36;
  const totalH = (ps.length + 1) * lineH + 24;
  const startY = CY - totalH / 2;
  ctx.save();
  for (let i = 0; i < ps.length; i++) {
    const pa = smoothstep(0.05 + i * 0.1, 0.15 + i * 0.1, t);
    if (pa > 0) {
      ctx.globalAlpha = a * pa;
      ctx.font = '400 ' + size + 'px ' + FONT;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = `rgba(${hexToRgb(MONO)},${a * pa * 0.8})`;
      ctx.fillText(ps[i], CX, startY + i * lineH);
    }
  }
  if (move.conclusion && smoothstep(0.55, 0.75, t) > 0) {
    const ca = smoothstep(0.55, 0.75, t);
    const lineY = startY + ps.length * lineH + 6;
    ctx.globalAlpha = a * ca;
    ctx.strokeStyle = `rgba(43,102,133,${a * ca * 0.4})`;
    ctx.lineWidth = 0.6;
    ctx.beginPath();
    ctx.moveTo(240, lineY);
    ctx.lineTo(1040, lineY);
    ctx.stroke();
    ctx.font = '500 ' + (size + 2) + 'px ' + FONT;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = `rgba(43,102,133,${a * ca * 0.92})`;
    ctx.fillText(move.conclusion, CX, lineY + 32);
  }
  ctx.restore();
}

function renderConceptMap(ctx, t, move) {
  const a = alpha(t);
  const nodes = move.nodes || [];
  const size = move.size || 16;
  ctx.save();
  const centralReveal = smoothstep(0, 0.2, t);
  if (centralReveal > 0 && move.central) {
    ctx.globalAlpha = a * centralReveal;
    drawGlowOrb(ctx, CX, CY, 10, MONO, a * centralReveal * 0.1);
    drawRing(ctx, CX, CY, 48 + 6 * wave(t, 0.3), MONO, a * centralReveal * 0.08, 0.6);
    styledText(ctx, "**" + move.central + "**", CX, CY, size + 4, MONO, a * centralReveal * 0.92, "center");
  }
  for (let i = 0; i < nodes.length; i++) {
    const n = nodes[i];
    const nx = CX + (n.x || 0);
    const ny = CY + (n.y || 0);
    const nodeT = smoothstep(0.15 + i * 0.08, 0.25 + i * 0.08, t);
    if (nodeT <= 0 || !move.central) continue;
    ctx.globalAlpha = a * nodeT;
    ctx.strokeStyle = `rgba(90,98,106,${a * nodeT * 0.2})`;
    ctx.lineWidth = 0.4;
    ctx.beginPath();
    ctx.moveTo(CX, CY);
    ctx.quadraticCurveTo((CX + nx) / 2 + (i % 3 - 1) * 30, (CY + ny) / 2 - 20 + (i % 2) * 20, nx, ny);
    ctx.stroke();
    drawGlowOrb(ctx, nx, ny, 3.5, MONO, a * nodeT * 0.15);
    styledText(ctx, n.label, nx, ny + 24, size, MONO, a * nodeT * 0.88, "center");
    if (n.relation && nodeT > 0.3) {
      styledText(ctx, n.relation, nx, ny - 28, size - 4, MUTED, a * nodeT * 0.4, "center");
    }
  }
  ctx.restore();
}

function renderDivider(ctx, t) {
  const a = alpha(t) * 0.2;
  ctx.save();
  ctx.globalAlpha = a;
  ctx.strokeStyle = `rgba(90,98,106,${a})`;
  ctx.lineWidth = 0.35;
  ctx.beginPath();
  ctx.moveTo(CX - 160, CY);
  ctx.lineTo(CX + 160, CY);
  ctx.stroke();
  ctx.restore();
}

const RENDERERS = {
  claim: renderClaim, subclaim: renderSubclaim,
  "side-by-side": renderSideBySide, branch: renderBranch,
  converge: renderConverge, premises: renderPremiseList,
  "concept-map": renderConceptMap, divider: renderDivider,
};

export function renderArgumentDiagramV4(ctx, t, scene, env) {
  const seconds = env.sceneSeconds ?? (t * (scene.duration ?? 12));
  const sceneDur = scene.duration ?? 12;
  const moves = scene.params?.moves ?? [];
  if (!moves.length) return;

  ctx.fillStyle = "#fafaf8";
  ctx.fillRect(0, 0, 1280, 720);
  drawSubtleField(ctx, t, env.theme);

  for (const move of moves) {
    const startNorm = (move.at ?? 0) / sceneDur;
    const endNorm = ((move.at ?? 0) + (move.duration ?? 4)) / sceneDur;
    if (t < startNorm || t > endNorm) continue;
    const localT = smoothstep(startNorm, endNorm, t);
    const fadeOutAt = endNorm - 0.06;
    const globalFade = t > fadeOutAt ? smoothstep(endNorm, fadeOutAt, t) : 1;
    ctx.save();
    ctx.globalAlpha *= globalFade;
    const fn = RENDERERS[move.type];
    if (fn) fn(ctx, localT, move);
    ctx.restore();
  }
}
