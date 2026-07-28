import { drawRichText } from "../typography/rich-text.mjs";
import { COLORS, statusColor } from "../statuses.mjs";

export function premises(frame, move, ctx, W, H) {
  const CX = W / 2, CY = H / 2;
  const size = move.size || 18;
  const lh = 36;
  const ps = move.premises || [];
  const totalH = (ps.length + 1) * lh + 24;
  const sy = CY - totalH / 2;
  ctx.save();
  for (let i = 0; i < ps.length; i++) {
    const mf = i; // frame is relative to enterFrame; use simple even spacing for premises
    const v = mf >= 0 ? 1 : 0;
    drawRichText(ctx, [{ t: ps[i], w: 400, i: false }], CX, sy + i * lh, size, COLORS.ink, 0.85 * v, "center");
  }
  if (move.conclusion) {
    const ly = sy + ps.length * lh + 6;
    ctx.strokeStyle = `rgba(45,102,133,0.35)`;
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(240, ly);
    ctx.lineTo(W - 240, ly);
    ctx.stroke();
    drawRichText(ctx, [{ t: move.conclusion, w: 500, i: false }], CX, ly + 32, size + 2, COLORS.blue, 0.92, "center");
  }
  ctx.restore();
}
