import { drawRichText } from "../typography/rich-text.mjs";
import { COLORS } from "../statuses.mjs";

export function conceptMap(frame, move, ctx, W, H) {
  const CX = W / 2, CY = H / 2;
  const nodes = move.nodes || [];
  const size = move.size || 16;
  ctx.save();
  for (const n of nodes) {
    const nx = CX + (n.x || 0);
    const ny = CY + (n.y || 0);
    const nc = n.color || COLORS.ink;
    ctx.strokeStyle = `rgba(90,98,106,0.1)`;
    ctx.lineWidth = 0.3;
    ctx.beginPath();
    ctx.moveTo(CX, CY);
    ctx.quadraticCurveTo((CX + nx) / 2, (CY + ny) / 2 - 15, nx, ny);
    ctx.stroke();
    const lines = n.label.split("\n");
    for (let li = 0; li < lines.length; li++)
      drawRichText(ctx, [{ t: lines[li], w: 400, i: false }], nx, ny + 24 + li * 22, size, nc, 0.88, "center");
    if (n.relation)
      drawRichText(ctx, [{ t: n.relation, w: 400, i: true }], nx, ny - 28, size - 4, COLORS.muted, 0.4, "center");
  }
  ctx.restore();
}
