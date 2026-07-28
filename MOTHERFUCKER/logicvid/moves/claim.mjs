import { drawRichText, wrapLines } from "../typography/rich-text.mjs";
import { statusColor, rgba, COLORS } from "../statuses.mjs";
import { resolveSize, resolveLineHeight, LAYOUT } from "../typography/scale.mjs";

export function claim(frame, move, ctx, W, H) {
  const CX = W / 2, CY = H / 2;
  const color = statusColor(move.status);
  const size = resolveSize(move);
  const lh = resolveLineHeight(move);
  const align = move.layout === "left" ? "left" : "center";
  const margin = LAYOUT.marginX;
  const maxW = Math.min(W - margin * 2, 1120);
  ctx.save();
  const lines = wrapLines(move.text, size, maxW, ctx);
  const totalH = lines.reduce((s) => s + lh, 0) - lh;
  const sy = CY - totalH / 2;
  for (let i = 0; i < lines.length; i++) {
    const y = sy + i * lh;
    const x = align === "left" ? margin : CX;
    drawRichText(ctx, lines[i], x, y, size, color, 1, align);
  }
  ctx.restore();
  if (move.status === "refuted" && move.layout !== "left") {
    ctx.strokeStyle = rgba(COLORS.red, 0.4);
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(LAYOUT.marginX, CY);
    ctx.lineTo(W - LAYOUT.marginX, CY);
    ctx.stroke();
  }
}
