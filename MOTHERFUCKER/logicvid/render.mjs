import { claim } from "./moves/claim.mjs";
import { comparison } from "./moves/comparison.mjs";
import { premises } from "./moves/premises.mjs";
import { branch } from "./moves/branch.mjs";
import { conceptMap } from "./moves/concept-map.mjs";
import { drawRichText, parseInline, wrapLines } from "./typography/rich-text.mjs";
import { COLORS, rgba, statusColor } from "./statuses.mjs";
import { resolveSize, resolveLineHeight, SCALE, LAYOUT, SPACING } from "./typography/scale.mjs";

const MOVE_RENDERERS = {
  claim,
  "side-by-side": comparison,
  premises,
  branch,
  "concept-map": conceptMap,
  verdict: (frame, move, ctx, W, H) => {
    const LM = LAYOUT.marginX, CY = H / 2;
    const size = resolveSize(move);
    const lh = resolveLineHeight(move);
    const color = statusColor(move.status);
    const maxW = Math.min(W - LM * 2, 1120);
    ctx.save();
    if (move.showRule !== false) {
      ctx.strokeStyle = rgba(COLORS.faint, 0.4);
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(LM, CY - SPACING.lg);
      ctx.lineTo(W - LM, CY - SPACING.lg);
      ctx.stroke();
    }
    const lines = wrapLines(move.text, size, maxW, ctx);
    const totalH = lines.reduce((s) => s + lh, 0) - lh;
    const sy = CY - totalH / 2 + (move.showRule !== false ? SPACING.sm : 0);
    for (let i = 0; i < lines.length; i++)
      drawRichText(ctx, lines[i], LM, sy + i * lh, size, color, 1, "left");
    ctx.restore();
  },
  subclaim: (frame, move, ctx, W, H) => {
    const LM = LAYOUT.marginX, CY = H * 0.55;
    const size = resolveSize(move);
    const lh = resolveLineHeight(move);
    const color = move.color ? (COLORS[move.color] || move.color) : COLORS.muted;
    const maxW = Math.min(W - LM * 2, 1120);
    ctx.save();
    const lines = wrapLines(move.text, size, maxW, ctx);
    const totalH = lines.reduce((s) => s + lh, 0) - lh;
    const sy = CY - totalH / 2;
    for (let i = 0; i < lines.length; i++)
      drawRichText(ctx, lines[i], LM, sy + i * lh, size, color, 0.85, "left");
    ctx.restore();
  },
  divider: (frame, move, ctx, W, H) => {
    const y = move.y != null ? move.y : H / 2;
    ctx.strokeStyle = rgba(COLORS.faint, 0.35);
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(LAYOUT.marginX, y);
    ctx.lineTo(W - LAYOUT.marginX, y);
    ctx.stroke();
  },
};

export function renderLogicvid(ctx, t, scene, env) {
  const W = env.width || 1280;
  const H = env.height || 720;
  const frameCount = scene.frameCount || Math.round((scene.duration || 12) * (env.fps || 24));
  const frame = Math.round(t * frameCount);
  ctx.fillStyle = rgba(COLORS.paper, 1);
  ctx.fillRect(0, 0, W, H);
  const moves = scene.params?.moves || [];
  if (!moves.length) return;
  const active = new Map();
  for (let i = 0; i < moves.length; i++) {
    const m = moves[i];
    const enter = m.enterFrame ?? 0;
    const settle = m.settleFrame ?? enter;
    const rawExit = m.exitFrame;
    const exit = rawExit != null ? rawExit : frameCount;
    if (frame < enter || frame >= exit) {
      active.delete(`${m.replacementGroup || "default"}:${m.slot || "center"}`);
      continue;
    }
    const slotKey = `${m.replacementGroup || "default"}:${m.slot || "center"}`;
    const occupant = active.get(slotKey);
    if (occupant != null && occupant > i) continue;
    active.set(slotKey, i);
    const relFrames = frame - enter;
    const settleFrames = settle - enter;
    const settled = settleFrames <= 0 ? 1 : Math.min(1, relFrames / settleFrames);
    if (settled <= 0) continue;
    const fn = MOVE_RENDERERS[m.type];
    if (fn) {
      ctx.save();
      ctx.globalAlpha = settled;
      fn(frame, m, ctx, W, H);
      ctx.restore();
    }
  }
}
