import { drawRichText, wrapLines, parseInline } from "../typography/rich-text.mjs";
import { statusColor } from "../statuses.mjs";

export function claim(frame, move, ctx, W, H) {
  const CX = W / 2, CY = H / 2;
  const color = statusColor(move.status);
  const size = move.size || 34;
  const lh = size * 1.35;
  const align = move.layout === "left" ? "left" : "center";
  const leftMargin = 80;
  const maxW = Math.min(W - leftMargin * 2, 900);
  ctx.save();
  const lines = wrapLines(move.text, size, maxW, ctx);
  const totalH = lines.reduce((s, ln) => s + lh, 0) - lh;
  const sy = CY - totalH / 2;
  for (let i = 0; i < lines.length; i++) {
    const y = sy + i * lh;
    const x = align === "left" ? leftMargin : CX;
    drawRichText(ctx, lines[i], x, y, size, color, 1, align);
  }
  ctx.restore();
  if (move.status === "refuted" && move.layout !== "left") {
    ctx.strokeStyle = `rgba(164,62,70,0.4)`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(160, CY);
    ctx.lineTo(W - 160, CY);
    ctx.stroke();
  }
}
