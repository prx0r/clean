import { drawRichText } from "../typography/rich-text.mjs";
import { COLORS } from "../statuses.mjs";

export function branch(frame, move, ctx, W, H) {
  const CX = W / 2, CY = H / 2;
  const branches = move.branches || [];
  const spread = Math.min(420, 840 / Math.max(branches.length, 2));
  ctx.save();
  for (let i = 0; i < branches.length; i++) {
    const x = CX + (i - (branches.length - 1) / 2) * spread;
    const color = branches[i].color || COLORS.ink;
    ctx.strokeStyle = `rgba(90,98,106,0.18)`;
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(CX, H * 0.4);
    ctx.quadraticCurveTo((CX + x) / 2, H * 0.48, x, H * 0.56);
    ctx.stroke();
    const lines = branches[i].label.split("\n");
    for (let li = 0; li < lines.length; li++)
      drawRichText(ctx, [{ t: lines[li], w: 400, i: false }], x, H * 0.56 + 28 + li * 20, 15, color, 0.85, "center");
  }
  ctx.restore();
}
