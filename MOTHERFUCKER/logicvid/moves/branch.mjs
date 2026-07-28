import { drawRichText, wrapLines } from "../typography/rich-text.mjs";
import { COLORS, rgba } from "../statuses.mjs";
import { resolveSize, LAYOUT } from "../typography/scale.mjs";

export function branch(frame, move, ctx, W, H) {
  const CX = W / 2, CY = H / 2;
  const branches = move.branches || [];
  const spread = Math.min(420, 840 / Math.max(branches.length, 2));
  const size = move.size || 15;
  ctx.save();
  for (let i = 0; i < branches.length; i++) {
    const x = CX + (i - (branches.length - 1) / 2) * spread;
    const color = branches[i].color || COLORS.ink;
    ctx.strokeStyle = rgba(COLORS.faint, 0.4);
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(CX, H * 0.4);
    ctx.quadraticCurveTo((CX + x) / 2, H * 0.48, x, H * 0.56);
    ctx.stroke();
    const lines = branches[i].label.split("\n");
    for (let li = 0; li < lines.length; li++)
      drawRichText(ctx, [{t: lines[li], w: 400, i: false}], x, H * 0.56 + 28 + li * 20, size, color, 0.85, "center");
  }
  ctx.restore();
}
