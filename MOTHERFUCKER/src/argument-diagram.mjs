import { TAU, clamp, easeInOutCubic, easeOutCubic, rgba, smoothstep, wave } from "../math.mjs";
import { drawArrowHead, drawLabel, drawGlowOrb } from "../primitives.mjs";

const CX = 640;
const CY = 320;
const WHITE = "#fafaf8";

function themeColor(theme, key, fallback) {
  return theme[key] || fallback;
}

const STATUS_COLORS = {
  "active": null,
  "refuted": "#c4445a",
  "resolved": "#3b8c5a",
  "neutral": "#59646d",
  "highlight": "#d2a744",
};

function resolveColor(move, theme) {
  const status = move.status || "active";
  const override = STATUS_COLORS[status];
  if (override) return override;
  return move.color || theme.ink;
}

function renderClaim(ctx, t, move, theme, env) {
  const a = smoothstep(0, 0.15, t);
  const scale = 0.92 + 0.08 * (1 - easeOutCubic(smoothstep(0, 0.3, t)));
  const size = move.size || 36;
  const color = resolveColor(move, theme);
  const prevColor = move.prevStatus ? (STATUS_COLORS[move.prevStatus] || theme.structure) : color;
  const tColor = move.statusTransition ? smoothstep(0.3, 0.7, t) : 1;
  const finalColor = tColor < 1 ? prevColor : color;
  ctx.save();
  ctx.globalAlpha = a;
  ctx.translate(CX, CY);
  ctx.scale(scale, scale);
  ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  if (move.status === "refuted" && t > 0.3) {
    ctx.fillStyle = rgba(STATUS_COLORS["refuted"], a * 0.15);
    ctx.fillRect(-320, -size * 0.7, 640, size * 1.7);
  }
  if (move.status === "resolved" && t > 0.3) {
    ctx.fillStyle = rgba(STATUS_COLORS["resolved"], a * 0.08);
    ctx.fillRect(-320, -size * 0.7, 640, size * 1.7);
  }
  ctx.fillStyle = rgba(finalColor, a * 0.92);
  const lines = move.text.split("\n");
  const lineHeight = size * 1.3;
  const startY = -(lines.length - 1) * lineHeight / 2;
  for (let i = 0; i < lines.length; i++) {
    const la = smoothstep(0.05 + i * 0.08, 0.15 + i * 0.08, t);
    ctx.globalAlpha = a * la;
    ctx.fillText(lines[i], 0, startY + i * lineHeight);
  }
  ctx.restore();
}

function renderSubclaim(ctx, t, move, theme, env) {
  const a = smoothstep(0, 0.2, t);
  const size = move.size || 24;
  const y = move.y || 260;
  const color = move.color || themeColor(theme, "secondary", theme.structure);
  ctx.save();
  ctx.globalAlpha = a;
  ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = rgba(color, a * 0.85);
  ctx.fillText(move.text, CX, y);
  ctx.restore();
}

function renderRefutation(ctx, t, move, theme, env) {
  const a = smoothstep(0, 0.2, t);
  const size = move.size || 28;
  const slideIn = 120 * (1 - easeOutCubic(smoothstep(0, 0.35, t)));
  const color = move.color || themeColor(theme, "accent", "#c4445a");
  ctx.save();
  ctx.globalAlpha = a;
  ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = rgba(color, a * 0.9);
  ctx.fillText(move.text, CX + slideIn, CY);
  if (slideIn > 20) {
    ctx.strokeStyle = rgba(color, a * 0.4);
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 8]);
    ctx.beginPath();
    ctx.moveTo(CX - 320, CY + size + 16);
    ctx.lineTo(CX + 280, CY + size + 16);
    ctx.stroke();
    ctx.setLineDash([]);
    drawArrowHead(ctx, CX + 280, CY + size + 16, 0, 10, color, a * 0.5);
  }
  ctx.restore();
}

function renderBranch(ctx, t, move, theme, env) {
  const a = smoothstep(0, 0.15, t);
  const branches = move.branches || [];
  const gap = 380;
  const startX = CX;
  const endY = CY + 60;
  ctx.save();
  for (let i = 0; i < branches.length; i++) {
    const ba = smoothstep(0.1 + i * 0.15, 0.25 + i * 0.15, t);
    const x = startX + (i - (branches.length - 1) / 2) * gap;
    const color = branches[i].color || (i === 0 ? themeColor(theme, "accent", theme.structure) : themeColor(theme, "secondary", theme.structure));
    if (ba > 0) {
      ctx.globalAlpha = a * ba;
      ctx.strokeStyle = rgba(color, a * ba * 0.5);
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(startX, CY + 40);
      const cpY = CY + 100;
      ctx.quadraticCurveTo(startX + (x - startX) * 0.5, cpY, x, endY);
      ctx.stroke();
      drawArrowHead(ctx, x, endY, Math.atan2(endY - cpY, x - (startX + (x - startX) * 0.5)), 8, color, a * ba * 0.6);
      ctx.font = "400 18px \"EB Garamond\", \"Tantra Garamond\", serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = rgba(color, a * ba * 0.88);
      ctx.fillText(branches[i].label, x, endY + 36);
    }
  }
  ctx.restore();
}

function renderConverge(ctx, t, move, theme, env) {
  const a = smoothstep(0, 0.2, t);
  const size = move.size || 30;
  const slideUp = 60 * (1 - easeOutCubic(smoothstep(0, 0.35, t)));
  const color = move.color || theme.ink;
  ctx.save();
  ctx.globalAlpha = a;
  const lines = move.text.split("\n");
  ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (let i = 0; i < lines.length; i++) {
    const la = smoothstep(0.05 + i * 0.1, 0.15 + i * 0.1, t);
    ctx.globalAlpha = a * la;
    ctx.fillStyle = rgba(color, a * la * 0.92);
    ctx.fillText(lines[i], CX, CY - slideUp + i * size * 1.3 - (lines.length - 1) * size * 0.65);
  }
  ctx.restore();
}

function renderDivider(ctx, t, move, theme, env) {
  const a = smoothstep(0, 0.2, t);
  ctx.save();
  ctx.globalAlpha = a * 0.3;
  ctx.strokeStyle = rgba(theme.structure, a * 0.3);
  ctx.lineWidth = 0.5;
  ctx.beginPath();
  ctx.moveTo(CX - 200, CY);
  ctx.lineTo(CX + 200, CY);
  ctx.stroke();
  ctx.restore();
}

function renderPremiseList(ctx, t, move, theme, env) {
  const a = smoothstep(0, 0.15, t);
  const premises = move.premises || [];
  const size = move.size || 20;
  const startY = CY - ((premises.length - 1) * 38) / 2;
  ctx.save();
  for (let i = 0; i < premises.length; i++) {
    const pa = smoothstep(0.1 + i * 0.12, 0.22 + i * 0.12, t);
    if (pa > 0) {
      ctx.globalAlpha = a * pa;
      ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = rgba(theme.structure, a * pa * 0.8);
      ctx.fillText(premises[i], CX, startY + i * 38);
    }
  }
  if (move.conclusion && smoothstep(0.5, 0.7, t) > 0) {
    const ca = smoothstep(0.55, 0.75, t);
    ctx.globalAlpha = a * ca;
    ctx.strokeStyle = rgba(themeColor(theme, "accent", theme.structure), a * ca * 0.5);
    ctx.lineWidth = 0.8;
    const lineY = startY + premises.length * 38 + 8;
    ctx.beginPath();
    ctx.moveTo(CX - 160, lineY);
    ctx.lineTo(CX + 160, lineY);
    ctx.stroke();
    ctx.font = "500 22px \"EB Garamond\", \"Tantra Garamond\", serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = rgba(themeColor(theme, "accent", theme.structure), a * ca * 0.92);
    ctx.fillText(move.conclusion, CX, lineY + 36);
  }
  ctx.restore();
}

function renderSideBySide(ctx, t, move, theme, env) {
  const a = smoothstep(0, 0.15, t);
  const left = move.left || "";
  const right = move.right || "";
  const size = move.size || 22;
  const colW = 380;
  ctx.save();
  const leftReveal = smoothstep(0, 0.3, t);
  const rightReveal = smoothstep(0.2, 0.5, t);
  if (leftReveal > 0) {
    ctx.globalAlpha = a * leftReveal;
    ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const lColor = move.leftColor || themeColor(theme, "accent", theme.structure);
    ctx.fillStyle = rgba(lColor, a * leftReveal * 0.9);
    const lLines = left.split("\n");
    for (let i = 0; i < lLines.length; i++) {
      ctx.fillText(lLines[i], CX - colW / 2 - 20, CY - (lLines.length - 1) * size * 0.65 + i * size * 1.3);
    }
  }
  if (rightReveal > 0) {
    ctx.globalAlpha = a * rightReveal;
    ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const rColor = move.rightColor || themeColor(theme, "secondary", theme.structure);
    ctx.fillStyle = rgba(rColor, a * rightReveal * 0.9);
    const rLines = right.split("\n");
    for (let i = 0; i < rLines.length; i++) {
      ctx.fillText(rLines[i], CX + colW / 2 + 20, CY - (rLines.length - 1) * size * 0.65 + i * size * 1.3);
    }
  }
  if (leftReveal > 0.3 && rightReveal > 0.3) {
    ctx.globalAlpha = a * 0.2;
    ctx.strokeStyle = rgba(theme.structure, a * 0.2);
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(CX, CY - 160);
    ctx.lineTo(CX, CY + 160);
    ctx.stroke();
  }
  ctx.restore();
}

const RENDERERS = {
  "claim": renderClaim,
  "subclaim": renderSubclaim,
  "refutation": renderRefutation,
  "branch": renderBranch,
  "converge": renderConverge,
  "divider": renderDivider,
  "premises": renderPremiseList,
  "side-by-side": renderSideBySide,
};

export function renderArgumentDiagram(ctx, t, scene, env) {
  const theme = env.theme;
  const moves = (scene.params && scene.params.moves) || [];
  if (!moves.length) return;

  ctx.save();
  ctx.fillStyle = WHITE;
  ctx.fillRect(0, 0, 1280, 720);
  ctx.restore();

  const totalMoves = moves.length;
  for (let i = 0; i < totalMoves; i++) {
    const move = moves[i];
    const moveStart = i / totalMoves;
    const moveEnd = (i + 1) / totalMoves;
    const moveT = smoothstep(moveStart, moveEnd, t);
    if (moveT <= 0) continue;
    const renderer = RENDERERS[move.type];
    if (renderer) {
      renderer(ctx, moveT, move, theme, env);
    }
  }
}
