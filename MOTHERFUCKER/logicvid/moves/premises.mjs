import { drawRichText, wrapLines } from "../typography/rich-text.mjs";
import { COLORS, rgba } from "../statuses.mjs";
import { resolveSize, resolveLineHeight, LAYOUT, SPACING } from "../typography/scale.mjs";

export function premises(frame, move, ctx, W, H) {
  const CY = H / 2, LM = LAYOUT.marginX;
  const size = resolveSize(move);
  const lh = resolveLineHeight(move);
  const ps = move.premises || [];
  const maxW = Math.min(W - LM * 2, 900);
  ctx.save();
  const totalH = (ps.length + 1) * lh + SPACING.lg;
  const sy = CY - totalH / 2;
  for (let i = 0; i < ps.length; i++) {
    const lines = wrapLines(ps[i], size, maxW, ctx);
    let ly = sy + i * lh;
    for (let li = 0; li < lines.length; li++)
      drawRichText(ctx, lines[li], LM, ly + li * resolveLineHeight({size}), size, COLORS.ink, 0.85, "left");
  }
  if (move.conclusion) {
    const ly = sy + ps.length * lh + SPACING.sm;
    ctx.strokeStyle = rgba(COLORS.blue, 0.35);
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(LM, ly);
    ctx.lineTo(W - LM, ly);
    ctx.stroke();
    const lines = wrapLines(move.conclusion, size + 2, maxW, ctx);
    drawRichText(ctx, lines[0] || [{t: move.conclusion, w:500, i:false}], LM, ly + SPACING.lg, size + 2, COLORS.blue, 0.92, "left");
  }
  ctx.restore();
}
