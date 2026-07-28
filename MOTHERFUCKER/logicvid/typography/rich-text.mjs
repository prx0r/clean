export const FONT_SERIF = '"Source Serif 4", "EB Garamond", serif';
export const FONT_SERIF_ITALIC = '"Source Serif 4", "EB Garamond", serif';
export const FONT_MATH = '"KaTeX Math", "Source Serif 4", serif';

export function parseInline(text) {
  const parts = text.split(/(\$\$[^$]+\$\$|\$[^$]+\$|\*\*[^*]+\*\*|\*[^*]+\*)/g);
  const segs = [];
  for (const p of parts) {
    if (!p) continue;
    if (p.startsWith("$$") && p.endsWith("$$"))
      segs.push({ t: p.slice(2, -2), w: 400, i: true, isMath: true });
    else if (p.startsWith("$") && p.endsWith("$"))
      segs.push({ t: p.slice(1, -1), w: 400, i: true, isMath: true });
    else if (p.startsWith("**") && p.endsWith("**"))
      segs.push({ t: p.slice(2, -2), w: 700, i: false });
    else if (p.startsWith("*") && p.endsWith("*"))
      segs.push({ t: p.slice(1, -1), w: 400, i: true, isMath: false });
    else segs.push({ t: p, w: 400, i: false });
  }
  return segs;
}

export function measureRichText(ctx, segments, size) {
  let total = 0;
  for (const s of segments) {
    ctx.font = s.isMath
      ? `${s.w} ${size}px ${FONT_MATH}`
      : `${s.i ? "italic " : ""}${s.w} ${size}px ${FONT_SERIF}`;
    total += ctx.measureText(s.t).width;
  }
  return total;
}

export function drawRichText(ctx, segments, x, y, size, color, alpha, align) {
  if (!segments.length) return;
  const gap = 4;
  ctx.textBaseline = "middle";
  ctx.textAlign = "left";
  let tw = 0;
  for (const s of segments) {
    ctx.font = s.isMath
      ? `${s.w} ${size}px ${FONT_MATH}`
      : `${s.i ? "italic " : ""}${s.w} ${size}px ${FONT_SERIF}`;
    tw += ctx.measureText(s.t).width;
  }
  tw += gap * (segments.length - 1);
  let cx = align === "center" ? x - tw / 2 : x;
  for (const s of segments) {
    ctx.font = s.isMath
      ? `${s.w} ${size}px ${FONT_MATH}`
      : `${s.i ? "italic " : ""}${s.w} ${size}px ${FONT_SERIF}`;
    ctx.fillStyle = `rgba(${color},${alpha})`;
    ctx.fillText(s.t, cx, y);
    cx += ctx.measureText(s.t).width + gap;
  }
}

export function wrapLines(text, size, maxWidth, ctx) {
  const lines = [];
  for (const para of String(text).split("\n")) {
    const words = para.split(/\s+/).filter(Boolean);
    let line = "";
    for (const w of words) {
      const segs = parseInline(line ? `${line} ${w}` : w);
      const wdt = measureRichText(ctx, segs, size);
      if (line && wdt > maxWidth) {
        lines.push(parseInline(line));
        line = w;
      } else {
        line = line ? `${line} ${w}` : w;
      }
    }
    if (line) lines.push(parseInline(line));
    if (!para) lines.push([]);
  }
  return lines;
}
