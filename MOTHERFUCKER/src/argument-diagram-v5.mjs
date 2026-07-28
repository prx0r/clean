const CX = 640, CY = 316, W = 1280, H = 720;
const FONT = '"Source Serif 4", "EB Garamond", serif';
const MATH = '"KaTeX Math", "Source Serif 4", serif';
const MONO = "#1a1a1a";
const MUTED = "#5c626a";
const REFUTE = "#a43e46";
const RESOLVE = "#3e7857";
const GOLD = "#a9782f";

function step(t) { return t > 0 ? 1 : 0; }

function clr(c, a) {
  const v = c.replace("#", "");
  const h = v.length === 3 ? v.split("").map(x => x.repeat(2)).join("") : v;
  return `rgba(${parseInt(h.slice(0,2),16)},${parseInt(h.slice(2,4),16)},${parseInt(h.slice(4,6),16)},${a})`;
}

function renderClaim(ctx, t, m) {
  const color = m.status === "refuted" ? REFUTE : m.status === "resolved" ? RESOLVE : m.status === "highlight" ? GOLD : m.color || MONO;
  const size = m.size || 34;
  const lines = m.text.split("\n");
  const lh = size * 1.3;
  const sy = -(lines.length - 1) * lh / 2;
  ctx.save();
  ctx.translate(CX, CY);
  for (let i = 0; i < lines.length; i++)
    drawStyled(ctx, lines[i], 0, sy + i * lh, size, color, 1);
  ctx.restore();
  if (m.status === "refuted" && t > 0) {
    ctx.strokeStyle = clr(REFUTE, 0.4);
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(180, CY);
    ctx.lineTo(1100, CY);
    ctx.stroke();
  }
}

function renderSubclaim(ctx, t, m) {
  const y = typeof m.y === "number" ? m.y : 440;
  const size = m.size || 20;
  const color = m.color || MUTED;
  ctx.save();
  drawStyled(ctx, m.text, CX, y, size, color, 1);
  ctx.restore();
}

function renderSideBySide(ctx, t, m) {
  const size = m.size || 20;
  ctx.save();
  const ll = m.left.split("\n");
  for (let i = 0; i < ll.length; i++)
    drawStyled(ctx, ll[i], CX - 210, CY - (ll.length - 1) * size * 0.65 + i * size * 1.3, size, MUTED, 0.9);
  const rl = m.right.split("\n");
  for (let i = 0; i < rl.length; i++)
    drawStyled(ctx, rl[i], CX + 210, CY - (rl.length - 1) * size * 0.65 + i * size * 1.3, size, MONO, 0.9);
  if (t > 0) {
    ctx.strokeStyle = "rgba(90,98,106,0.1)";
    ctx.lineWidth = 0.35;
    ctx.beginPath();
    ctx.moveTo(CX, 140);
    ctx.lineTo(CX, 500);
    ctx.stroke();
  }
  ctx.restore();
}

function renderBranch(ctx, t, m) {
  const branches = m.branches || [];
  const spread = Math.min(420, 840 / Math.max(branches.length, 2));
  ctx.save();
  for (let i = 0; i < branches.length; i++) {
    const x = CX + (i - (branches.length - 1) / 2) * spread;
    ctx.strokeStyle = "rgba(90,98,106,0.22)";
    ctx.lineWidth = 0.6;
    ctx.beginPath();
    ctx.moveTo(CX, 290);
    ctx.quadraticCurveTo((CX + x) / 2, 320, x, 390);
    ctx.stroke();
    const lines = branches[i].label.split("\n");
    for (let li = 0; li < lines.length; li++)
      drawStyled(ctx, lines[li], x, 420 + li * 20, 15, MONO, 0.85);
  }
  ctx.restore();
}

function renderConverge(ctx, t, m) {
  const size = m.size || 28;
  const color = m.status === "resolved" ? RESOLVE : m.status === "highlight" ? GOLD : m.color || MONO;
  const lines = m.text.split("\n");
  const lh = size * 1.3;
  ctx.save();
  for (let i = 0; i < lines.length; i++)
    drawStyled(ctx, lines[i], CX, CY - (lines.length - 1) * lh / 2 + i * lh, size, color, 1);
  ctx.restore();
}

function renderConceptMap(ctx, t, m) {
  const nodes = m.nodes || [];
  const size = m.size || 16;
  ctx.save();
  for (const n of nodes) {
    const nx = CX + (n.x || 0);
    const ny = CY + (n.y || 0);
    const nodeAt = n.at !== undefined ? n.at : 0;
    if (t <= nodeAt) continue;
    ctx.strokeStyle = "rgba(90,98,106,0.12)";
    ctx.lineWidth = 0.3;
    ctx.beginPath();
    ctx.moveTo(CX, CY);
    ctx.quadraticCurveTo((CX + nx) / 2, (CY + ny) / 2 - 15, nx, ny);
    ctx.stroke();
    const lines = n.label.split("\n");
    for (let li = 0; li < lines.length; li++)
      drawStyled(ctx, lines[li], nx, ny + 24 + li * 22, size, MONO, 0.88);
    if (n.relation && t > nodeAt + 0.02)
      drawStyled(ctx, n.relation, nx, ny - 28, size - 4, MUTED, 0.4);
  }
  ctx.restore();
}

function drawStyled(ctx, text, x, y, size, color, alpha) {
  const parts = text.split(/(\*[^*]+\*|\*\*[^*]+\*\*)/g);
  const segs = [];
  for (const p of parts) {
    if (!p) continue;
    if (p.startsWith("**") && p.endsWith("**")) segs.push({ t: p.slice(2, -2), f: "700 " + size + "px " + FONT });
    else if (p.startsWith("*") && p.endsWith("*")) segs.push({ t: p.slice(1, -1), f: size + "px " + MATH });
    else segs.push({ t: p, f: size + "px " + FONT });
  }
  ctx.textBaseline = "middle";
  let tw = 0;
  for (const s of segs) { ctx.font = s.f; tw += ctx.measureText(s.t).width; }
  let cx = x - (tw + 4 * (segs.length - 1)) / 2;
  ctx.textAlign = "left";
  for (const s of segs) {
    ctx.font = s.f;
    ctx.fillStyle = clr(color, alpha);
    ctx.fillText(s.t, cx, y);
    cx += ctx.measureText(s.t).width + 4;
  }
}

const REND = {
  claim: renderClaim, subclaim: renderSubclaim,
  "side-by-side": renderSideBySide, branch: renderBranch,
  converge: renderConverge, "concept-map": renderConceptMap,
};

export function renderArgumentDiagramV5(ctx, t, scene, env) {
  const dur = scene.duration ?? 12;
  const moves = scene.params?.moves ?? [];
  if (!moves.length) return;
  ctx.fillStyle = "#fafaf8";
  ctx.fillRect(0, 0, W, H);
  for (const m of moves) {
    const st = (m.at ?? 0) / dur;
    const en = ((m.at ?? 0) + (m.duration ?? 4)) / dur;
    if (t < st || t > en) continue;
    const localT = (t - st) / Math.max(0.001, en - st);
    const fn = REND[m.type];
    if (fn) fn(ctx, localT, m);
  }
}
