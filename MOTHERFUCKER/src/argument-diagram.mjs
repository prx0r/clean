import { TAU, clamp, easeInOutCubic, easeOutCubic, rgba, smoothstep, wave } from "../math.mjs";
import { drawGlowOrb, drawRing, drawNode, drawArrowHead, drawPartialPath } from "../primitives.mjs";

const CX = 640, CY = 310;
const FW = 1280, FH = 720;

const MONO = "#1a1a1a";
const MUTED = "#555555";
const REFUTE = "#b33a3a";
const RESOLVE = "#3a7a4a";

function resolveColor(move) {
  if (move.status === "refuted") return REFUTE;
  if (move.status === "resolved") return RESOLVE;
  if (move.status === "neutral") return MUTED;
  if (move.status === "highlight") return MONO;
  return move.color || MONO;
}

function styledText(ctx, text, x, y, baseSize, color, alpha, align) {
  const parts = text.split(/(\*[^*]+\*|\*\*[^*]+\*\*)/g);
  let cx = x;
  ctx.textBaseline = "middle";
  if (align === "center") ctx.textAlign = "center";
  else ctx.textAlign = "left";
  for (const part of parts) {
    if (!part) continue;
    if (part.startsWith("**") && part.endsWith("**")) {
      ctx.font = "700 " + baseSize + 'px "EB Garamond", "Tantra Garamond", serif';
      const t = part.slice(2, -2);
      ctx.fillStyle = rgba(color, alpha);
      if (align === "center") { ctx.fillText(t, x, y); break; }
      ctx.fillText(t, cx, y);
      cx += ctx.measureText(t).width + 4;
    } else if (part.startsWith("*") && part.endsWith("*")) {
      ctx.font = "italic 400 " + baseSize + 'px "EB Garamond", "Tantra Garamond", serif';
      const t = part.slice(1, -1);
      ctx.fillStyle = rgba(color, alpha);
      if (align === "center") { ctx.fillText(t, x, y); break; }
      ctx.fillText(t, cx, y);
      cx += ctx.measureText(t).width + 4;
    } else {
      ctx.font = "400 " + baseSize + 'px "EB Garamond", "Tantra Garamond", serif';
      ctx.fillStyle = rgba(color, alpha);
      if (align === "center") { ctx.fillText(part, x, y); break; }
      ctx.fillText(part, cx, y);
      cx += ctx.measureText(part).width + 4;
    }
  }
}

function drawSubtleField(ctx, t, theme) {
  const a = 0.03 + 0.02 * wave(t, 0.15);
  for (let i = 0; i < 3; i++) {
    const r = 200 + i * 160 + 30 * wave(t + i * 0.3, 0.1);
    ctx.save();
    ctx.globalAlpha = a * (0.5 + 0.5 * smoothstep(0, 0.3, t));
    ctx.strokeStyle = rgba(theme.structure || theme.secondary, a * 0.3);
    ctx.lineWidth = 0.3;
    ctx.beginPath();
    ctx.arc(CX, CY, r, 0, TAU * smoothstep(0, 0.8, t));
    ctx.stroke();
    ctx.restore();
  }
}

function renderClaim(ctx, t, move, theme) {
  const a = smoothstep(0, 0.12, t);
  const color = resolveColor(move);
  const size = move.size || 34;
  const scale = 0.94 + 0.06 * (1 - easeOutCubic(smoothstep(0, 0.2, t)));
  const lines = move.text.split("\n");
  const lineH = size * 1.3;
  const startY = -(lines.length - 1) * lineH / 2;
  ctx.save();
  ctx.globalAlpha = a;
  ctx.translate(CX, CY);
  ctx.scale(scale, scale);
  ctx.textRendering = "geometricPrecision";
  for (let i = 0; i < lines.length; i++) {
    const la = smoothstep(0.03 + i * 0.06, 0.1 + i * 0.06, t);
    ctx.globalAlpha = a * la;
    styledText(ctx, lines[i], 0, startY + i * lineH, size, color, a * la * 0.95, "center");
  }
  ctx.restore();
  if (move.status === "refuted" && t > 0.4) {
    const strikeT = smoothstep(0.4, 0.55, t);
    ctx.save();
    ctx.globalAlpha = a * strikeT * 0.6;
    ctx.strokeStyle = rgba(REFUTE, a * strikeT * 0.5);
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(CX - 280, CY);
    ctx.lineTo(CX + 280, CY);
    ctx.stroke();
    ctx.restore();
  }
}

function renderSubclaim(ctx, t, move, theme) {
  const a = smoothstep(0, 0.15, t);
  const size = move.size || 20;
  const color = resolveColor(move);
  const y = typeof move.y === "number" ? move.y : 410;
  const drift = move.drift ? 40 * (1 - easeOutCubic(smoothstep(0, 0.3, t))) : 0;
  ctx.save();
  ctx.globalAlpha = a;
  ctx.textRendering = "geometricPrecision";
  styledText(ctx, move.text, CX + drift * (move.dir || 1), y, size, color, a * 0.85, "center");
  if (move.arrow && t > 0.3) {
    const arrT = smoothstep(0.3, 0.5, t);
    ctx.strokeStyle = rgba(color, a * 0.3 * arrT);
    ctx.lineWidth = 0.8;
    ctx.setLineDash([4, 6]);
    ctx.beginPath();
    ctx.moveTo(CX - 300, y - 30);
    ctx.lineTo(CX + 280, y - 30);
    ctx.stroke();
    ctx.setLineDash([]);
    drawArrowHead(ctx, CX + 280, y - 30, 0, 8, color, a * 0.3 * arrT);
  }
  ctx.restore();
}

function renderRefutation(ctx, t, move, theme) {
  const a = smoothstep(0, 0.15, t);
  const size = move.size || 26;
  const color = REFUTE;
  const slideIn = 140 * (1 - easeOutCubic(smoothstep(0, 0.3, t)));
  ctx.save();
  ctx.globalAlpha = a;
  ctx.textRendering = "geometricPrecision";
  styledText(ctx, move.text, CX + slideIn, CY, size, color, a * 0.9, "center");
  if (slideIn > 20 && t < 0.6) {
    const lineT = smoothstep(0.1, 0.25, t);
    ctx.strokeStyle = rgba(color, a * 0.25 * (1 - lineT));
    ctx.lineWidth = 1;
    ctx.setLineDash([6, 8]);
    ctx.beginPath();
    ctx.moveTo(200, CY + size + 14);
    ctx.lineTo(1080, CY + size + 14);
    ctx.stroke();
    ctx.setLineDash([]);
  }
  ctx.restore();
}

function renderBranch(ctx, t, move, theme) {
  const a = smoothstep(0, 0.12, t);
  const branches = move.branches || [];
  const spread = Math.min(420, 840 / Math.max(branches.length, 2));
  const startX = CX;
  const topY = 280;
  const botY = 390;
  ctx.save();
  for (let i = 0; i < branches.length; i++) {
    const ba = smoothstep(0.05 + i * 0.12, 0.18 + i * 0.12, t);
    const x = startX + (i - (branches.length - 1) / 2) * spread;
    const color = branches[i].color || MONO;
    if (ba > 0) {
      ctx.globalAlpha = a * ba;
      ctx.strokeStyle = rgba(MUTED, a * ba * 0.35);
      ctx.lineWidth = 0.8;
      ctx.beginPath();
      ctx.moveTo(startX, topY + 10);
      const cp = { x: (startX + x) / 2, y: botY - 60 };
      ctx.quadraticCurveTo(cp.x, cp.y, x, botY);
      ctx.stroke();
      ctx.font = "400 15px \"EB Garamond\", \"Tantra Garamond\", serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = rgba(MONO, a * ba * 0.88);
      const lines = branches[i].label.split("\n");
      for (let li = 0; li < lines.length; li++) {
        ctx.fillText(lines[li], x, botY + 28 + li * 20);
      }
    }
  }
  ctx.restore();
}

function renderConverge(ctx, t, move, theme) {
  const a = smoothstep(0, 0.15, t);
  const size = move.size || 28;
  const color = resolveColor(move, theme);
  const slideUp = 50 * (1 - easeOutCubic(smoothstep(0, 0.3, t)));
  const lines = move.text.split("\n");
  const lineH = size * 1.3;
  ctx.save();
  ctx.globalAlpha = a;
  for (let i = 0; i < lines.length; i++) {
    const la = smoothstep(0.05 + i * 0.08, 0.12 + i * 0.08, t);
    ctx.globalAlpha = a * la;
    ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = rgba(color, a * la * 0.92);
    ctx.fillText(lines[i], CX, CY - slideUp + i * lineH - (lines.length - 1) * lineH / 2);
  }
  if (t > 0.3) {
    ctx.globalAlpha = a * 0.12;
    ctx.strokeStyle = rgba(theme.secondary, a * 0.12);
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.arc(CX, CY - slideUp, 240 + 10 * wave(t, 0.2), 0, TAU * smoothstep(0.3, 0.7, t));
    ctx.stroke();
  }
  ctx.restore();
}

function renderPremiseList(ctx, t, move, theme) {
  const a = smoothstep(0, 0.1, t);
  const premises = move.premises || [];
  const size = move.size || 18;
  const lineH = 36;
  const totalH = (premises.length + 1) * lineH + 24;
  const startY = CY - totalH / 2;
  ctx.save();
  for (let i = 0; i < premises.length; i++) {
    const pa = smoothstep(0.05 + i * 0.1, 0.15 + i * 0.1, t);
    if (pa > 0) {
      ctx.globalAlpha = a * pa;
      drawNode(ctx, 200, startY + i * lineH, 3.5, { fill: theme.secondary, stroke: theme.secondary, alpha: a * pa * 0.5 });
      ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillStyle = rgba(theme.ink, a * pa * 0.8);
      ctx.fillText(premises[i], 220, startY + i * lineH);
      if (i > 0 && pa > 0.3) {
        ctx.strokeStyle = rgba(theme.structure, a * pa * 0.1);
        ctx.lineWidth = 0.3;
        ctx.beginPath();
        ctx.moveTo(205, startY + i * lineH - lineH / 2);
        ctx.lineTo(205, startY + i * lineH - lineH / 2 + 6);
        ctx.stroke();
      }
    }
  }
  if (move.conclusion && smoothstep(0.5, 0.7, t) > 0) {
    const ca = smoothstep(0.55, 0.75, t);
    const lineY = startY + premises.length * lineH + 8;
    ctx.globalAlpha = a * ca;
    ctx.strokeStyle = rgba(theme.accent || "#3b7a9e", a * ca * 0.5);
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(180, lineY);
    ctx.lineTo(1060, lineY);
    ctx.stroke();
    drawGlowOrb(ctx, 180, lineY, 3, theme.accent || "#3b7a9e", a * ca * 0.4);
    ctx.font = "500 " + (size + 2) + 'px "EB Garamond", "Tantra Garamond", serif';
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillStyle = rgba(theme.accent || "#3b7a9e", a * ca * 0.92);
    ctx.fillText(move.conclusion, 200, lineY + 30);
  }
  ctx.restore();
}

function renderSideBySide(ctx, t, move, theme) {
  const a = smoothstep(0, 0.12, t);
  const size = move.size || 20;
  const colW = 380;
  const lColor = MONO;
  const rColor = MONO;
  ctx.save();
  const leftReveal = smoothstep(0, 0.25, t);
  const rightReveal = smoothstep(0.15, 0.4, t);
  if (leftReveal > 0) {
    ctx.globalAlpha = a * leftReveal;
    const lLines = move.left.split("\n");
    for (let i = 0; i < lLines.length; i++) {
      styledText(ctx, lLines[i], CX - colW / 2 - 20, CY - (lLines.length - 1) * size * 0.65 + i * size * 1.3,
        size, lColor, a * leftReveal * 0.9, "center");
    }
    drawRing(ctx, CX - colW / 2 - 20, CY, 160 + 8 * wave(t, 0.2), lColor, a * leftReveal * 0.08, 0.8);
  }
  if (rightReveal > 0) {
    ctx.globalAlpha = a * rightReveal;
    const rLines = move.right.split("\n");
    for (let i = 0; i < rLines.length; i++) {
      styledText(ctx, rLines[i], CX + colW / 2 + 20, CY - (rLines.length - 1) * size * 0.65 + i * size * 1.3,
        size, rColor, a * rightReveal * 0.9, "center");
    }
    drawRing(ctx, CX + colW / 2 + 20, CY, 160 + 8 * wave(t, 0.2), rColor, a * rightReveal * 0.08, 0.8);
  }
  if (leftReveal > 0.3 && rightReveal > 0.3) {
    ctx.globalAlpha = a * 0.15;
    ctx.strokeStyle = rgba(theme.structure, a * 0.15);
    ctx.lineWidth = 0.5;
    ctx.setLineDash([3, 6]);
    ctx.beginPath();
    ctx.moveTo(CX, CY - 180);
    ctx.lineTo(CX, CY + 180);
    ctx.stroke();
    ctx.setLineDash([]);
    drawGlowOrb(ctx, CX, CY, 4, theme.structure, a * 0.2);
  }
  ctx.restore();
}

function renderDivider(ctx, t, move, theme) {
  const a = smoothstep(0, 0.15, t);
  ctx.save();
  ctx.globalAlpha = a * 0.25;
  ctx.strokeStyle = rgba(theme.structure, a * 0.25);
  ctx.lineWidth = 0.4;
  const cx = CX;
  ctx.beginPath();
  ctx.moveTo(cx - 180, CY);
  ctx.lineTo(cx + 180, CY);
  ctx.stroke();
  drawGlowOrb(ctx, cx, CY, 2, theme.structure, a * 0.3);
  ctx.restore();
}

const RENDERERS = {
  claim: renderClaim, subclaim: renderSubclaim, refutation: renderRefutation,
  branch: renderBranch, converge: renderConverge, divider: renderDivider,
  premises: renderPremiseList, "side-by-side": renderSideBySide,
};

export function renderArgumentDiagram(ctx, t, scene, env) {
  const theme = env.theme;
  const moves = (scene.params && scene.params.moves) || [];
  if (!moves.length) return;
  ctx.fillStyle = "#fafaf8";
  ctx.fillRect(0, 0, 1280, 720);
  drawSubtleField(ctx, t, theme);
  const n = moves.length;
  for (let i = 0; i < n; i++) {
    const mt = smoothstep(i / n, (i + 1) / n, t);
    if (mt <= 0) continue;
    const fn = RENDERERS[moves[i].type];
    if (fn) fn(ctx, mt, moves[i], theme);
  }
}
