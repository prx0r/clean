import { drawRichText, wrapLines } from "../typography/rich-text.mjs";
import { COLORS } from "../statuses.mjs";

export function comparison(frame, move, ctx, W, H) {
  const CX = W / 2, CY = H / 2;
  const size = move.size || 20;
  const colW = Math.min(W / 2 - 120, 370);
  ctx.save();
  // Left column
  const ll = wrapLines(move.left, size, colW, ctx);
  const lh = size * 1.3;
  const lh2 = ll.reduce((s, ln) => s + lh, 0) - lh;
  const sy = CY - lh2 / 2;
  for (let i = 0; i < ll.length; i++)
    drawRichText(ctx, ll[i], CX - W * 0.19, sy + i * lh, size, COLORS.ink, 0.9, "center");
  // Right column
  const rl = wrapLines(move.right, size, colW, ctx);
  const rh2 = rl.reduce((s, ln) => s + lh, 0) - lh;
  const rsy = CY - rh2 / 2;
  for (let i = 0; i < rl.length; i++)
    drawRichText(ctx, rl[i], CX + W * 0.19, rsy + i * lh, size, COLORS.ink, 0.9, "center");
  // Divider line (thin, like ChatGPT's section separator)
  if (move.showDivider !== false) {
    ctx.strokeStyle = `rgba(193,193,193,0.5)`;
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(CX, H * 0.2);
    ctx.lineTo(CX, H * 0.8);
    ctx.stroke();
  }
  ctx.restore();
}
