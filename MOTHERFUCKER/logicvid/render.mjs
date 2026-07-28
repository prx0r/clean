import { claim } from "./moves/claim.mjs";
import { comparison } from "./moves/comparison.mjs";
import { premises } from "./moves/premises.mjs";
import { branch } from "./moves/branch.mjs";
import { conceptMap } from "./moves/concept-map.mjs";
import { drawRichText, parseInline, wrapLines } from "./typography/rich-text.mjs";
import { COLORS, statusColor } from "./statuses.mjs";

const MOVE_RENDERERS = {
  claim,
  "side-by-side": comparison,
  premises,
  branch,
  "concept-map": conceptMap,
  verdict: (frame, move, ctx, W, H) => {
    // ChatGPT-style bold verdict statement, left-aligned with optional horizontal rule above
    const LM = 80, CY = H / 2;
    const size = move.size || 26;
    const color = statusColor(move.status);
    const maxW = Math.min(W - LM * 2, 900);
    ctx.save();
    if (move.showRule !== false) {
      ctx.strokeStyle = `rgba(193,193,193,0.4)`;
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(LM, CY - 60);
      ctx.lineTo(W - LM, CY - 60);
      ctx.stroke();
    }
    const lines = wrapLines(move.text, size, maxW, ctx);
    const lh = size * 1.4;
    const totalH = lines.reduce((s, ln) => s + lh, 0) - lh;
    const sy = CY - totalH / 2 + (move.showRule !== false ? 10 : 0);
    for (let i = 0; i < lines.length; i++)
      drawRichText(ctx, lines[i], LM, sy + i * lh, size, color, 1, "left");
    ctx.restore();
  },
  subclaim: (frame, move, ctx, W, H) => {
    // ChatGPT-style body text, left-aligned
    const LM = 80, CY = H * 0.55;
    const size = move.size || 19;
    const color = move.color ? (COLORS[move.color] || move.color) : COLORS.muted;
    const maxW = Math.min(W - LM * 2, 900);
    ctx.save();
    const lines = wrapLines(move.text, size, maxW, ctx);
    const lh = size * 1.4;
    const totalH = lines.reduce((s, ln) => s + lh, 0) - lh;
    const sy = CY - totalH / 2;
    for (let i = 0; i < lines.length; i++)
      drawRichText(ctx, lines[i], LM, sy + i * lh, size, color, 0.85, "left");
    ctx.restore();
  },
  divider: (frame, move, ctx, W, H) => {
    const y = move.y != null ? move.y : H / 2;
    ctx.strokeStyle = `rgba(193,193,193,0.35)`;
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(80, y);
    ctx.lineTo(W - 80, y);
    ctx.stroke();
  },
};

export function renderLogicvid(ctx, t, scene, env) {
  const W = env.width || 1280;
  const H = env.height || 720;
  const frameCount = scene.frameCount || Math.round((scene.duration || 12) * (env.fps || 24));
  const frame = Math.round(t * frameCount);
  ctx.fillStyle = "#fafaf8";
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
