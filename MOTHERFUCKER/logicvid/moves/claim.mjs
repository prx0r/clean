import { drawRichText, wrapLines, measureRichText, parseInline } from "../typography/rich-text.mjs";
import { statusColor } from "../statuses.mjs";

export function claim(frame, move, ctx, W, H) {
  const CX = W / 2, CY = H / 2;
  const color = statusColor(move.status);
  const size = move.size || 34;
  const lh = size * 1.3;
  ctx.save();
  const lines = wrapLines(move.text, size, Math.min(W - 160, 900), ctx);
  const totalH = lines.reduce((s, ln) => s + lh, 0) - lh;
  const sy = CY - totalH / 2;
  for (let i = 0; i < lines.length; i++) {
    const y = sy + i * lh;
    drawRichText(ctx, lines[i], CX, y, size, color, 1, "center");
  }
  ctx.restore();
  if (move.status === "refuted") {
    ctx.strokeStyle = `rgba(164,62,70,0.4)`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(180, CY);
    ctx.lineTo(W - 180, CY);
    ctx.stroke();
  }
}
