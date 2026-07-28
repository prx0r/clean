import { claim } from "./moves/claim.mjs";
import { comparison } from "./moves/comparison.mjs";
import { premises } from "./moves/premises.mjs";
import { branch } from "./moves/branch.mjs";
import { conceptMap } from "./moves/concept-map.mjs";
import { drawRichText, parseInline } from "./typography/rich-text.mjs";
import { COLORS, statusColor } from "./statuses.mjs";

const MOVE_RENDERERS = {
  claim,
  "side-by-side": comparison,
  premises,
  branch,
  "concept-map": conceptMap,
  converge: (frame, move, ctx, W, H) => {
    const CX = W / 2, CY = H / 2;
    const size = move.size || 28;
    const color = statusColor(move.status);
    const lines = (move.text || "").split("\n");
    const lh = size * 1.3;
    ctx.save();
    for (let i = 0; i < lines.length; i++)
      drawRichText(ctx, parseInline(lines[i]), CX, CY - (lines.length - 1) * lh / 2 + i * lh, size, color, 1, "center");
    ctx.restore();
  },
  subclaim: (frame, move, ctx, W, H) => {
    const y = typeof move.y === "number" ? move.y : H * 0.61;
    const size = move.size || 20;
    const color = move.color || COLORS.muted;
    drawRichText(ctx, parseInline(move.text || ""), W / 2, y, size, color, 0.85, "center");
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

  // Track occupied slots per replacement group
  const active = new Map(); // "group:slot" → move index

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

    // Check if a newer move has claimed this slot
    const slotKey = `${m.replacementGroup || "default"}:${m.slot || "center"}`;
    const occupant = active.get(slotKey);
    if (occupant != null && occupant > i) continue;

    active.set(slotKey, i);

    // Compute the settle progress — once settled, it stays fully visible
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
