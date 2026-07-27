import { TAU, clamp, easeOutCubic, rgba, smoothstep } from "../math.mjs";
import { drawLabel } from "../primitives.mjs";

const MARGIN_X = 100;
const MARGIN_Y = 100;
const CONTENT_WIDTH = 1080;
const LINE_HEIGHT = 32;
const BOX_PAD = 24;
const SECTION_SPACING = 48;

function alpha(t) {
  return smoothstep(0, 0.08, t);
}

function themeColor(theme, key, fallback) {
  return theme[key] || fallback;
}

function renderSectionHeader(ctx, block, x, y, theme, alphaVal) {
  const color = themeColor(theme, "accent", theme.structure);
  const numSize = 22;
  const titleSize = 20;
  ctx.save();
  ctx.globalAlpha = alphaVal;
  ctx.fillStyle = rgba(color, alphaVal);
  ctx.font = "700 " + numSize + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.textBaseline = "alphabetic";
  ctx.fillText(block.number, x, y + numSize);
  ctx.font = "400 " + titleSize + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.fillStyle = rgba(theme.ink, alphaVal * 0.9);
  ctx.fillText(block.title, x + numSize + 16, y + titleSize);
  ctx.strokeStyle = rgba(color, alphaVal * 0.3);
  ctx.lineWidth = 0.5;
  ctx.beginPath();
  ctx.moveTo(x, y + numSize + 12);
  ctx.lineTo(x + CONTENT_WIDTH, y + numSize + 12);
  ctx.stroke();
  ctx.restore();
  return y + numSize + 24;
}

function renderBody(ctx, block, x, y, theme, alphaVal, maxWidth) {
  const size = block.size || 17;
  const color = rgba(theme.ink, alphaVal * 0.88);
  ctx.save();
  ctx.globalAlpha = alphaVal;
  ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.textBaseline = "alphabetic";
  ctx.fillStyle = color;
  const words = block.text.split(" ");
  let line = "";
  let ly = y;
  for (const word of words) {
    const test = line ? line + " " + word : word;
    const tw = ctx.measureText(test).width;
    if (tw > maxWidth && line) {
      ctx.fillText(line, x, ly + size);
      line = word;
      ly += LINE_HEIGHT;
    } else {
      line = test;
    }
  }
  if (line) {
    ctx.fillText(line, x, ly + size);
    ly += LINE_HEIGHT;
  }
  ctx.restore();
  return ly + 8;
}

function renderBoxedEquation(ctx, block, x, y, theme, alphaVal, maxWidth) {
  const size = block.size || 22;
  const font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.save();
  ctx.globalAlpha = alphaVal;
  ctx.font = font;
  ctx.textBaseline = "alphabetic";
  const text = block.content;
  const tw = ctx.measureText(text).width;
  const bw = Math.min(tw + BOX_PAD * 2, maxWidth);
  const bh = size + BOX_PAD * 2;
  const bx = x + (maxWidth - bw) / 2;
  const by = y;
  const color = block.color || themeColor(theme, "secondary", theme.structure);
  ctx.save();
  ctx.globalAlpha = alphaVal;
  ctx.strokeStyle = rgba(color, alphaVal * 0.6);
  ctx.lineWidth = 1.2;
  ctx.strokeRect(bx, by, bw, bh);
  ctx.restore();
  ctx.fillStyle = rgba(color, alphaVal * 0.92);
  ctx.fillText(text, bx + BOX_PAD, by + BOX_PAD + size * 0.72);
  if (block.caption) {
    ctx.font = "400 13px \"EB Garamond\", \"Tantra Garamond\", serif";
    ctx.fillStyle = rgba(theme.structure, alphaVal * 0.55);
    ctx.textBaseline = "alphabetic";
    ctx.fillText(block.caption, x, by + bh + 26);
  }
  ctx.restore();
  return by + bh + (block.caption ? 38 : 22);
}

function renderProof(ctx, block, x, y, theme, alphaVal, maxWidth, progress) {
  const size = 17;
  ctx.save();
  ctx.globalAlpha = alphaVal;
  ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.textBaseline = "alphabetic";
  const premCount = block.premises.length;
  const premReveal = smoothstep(0, 0.5, progress);
  const concReveal = smoothstep(0.45, 0.8, progress);
  let py = y;
  for (let i = 0; i < premCount; i++) {
    const reveal = smoothstep((i + 1) * 0.15, (i + 1) * 0.15 + 0.2, premReveal);
    if (reveal > 0) {
      ctx.save();
      ctx.globalAlpha = alphaVal * reveal;
      ctx.fillStyle = rgba(theme.structure, alphaVal * 0.7 * reveal);
      ctx.fillText(String(i + 1) + ". " + block.premises[i], x + 16, py + size);
      ctx.restore();
    }
    py += LINE_HEIGHT;
  }
  py += 12;
  if (concReveal > 0) {
    ctx.save();
    ctx.globalAlpha = alphaVal * concReveal;
    ctx.strokeStyle = rgba(theme.accent, alphaVal * 0.5 * concReveal);
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(x + 16, py);
    ctx.lineTo(x + 200, py);
    ctx.stroke();
    py += 20;
    ctx.font = "600 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
    ctx.fillStyle = rgba(themeColor(theme, "accent", theme.structure), alphaVal * concReveal);
    ctx.fillText("therefore " + block.conclusion, x + 16, py + size);
    ctx.restore();
  }
  ctx.restore();
  return py + LINE_HEIGHT + 8;
}

function renderComparisonTable(ctx, block, x, y, theme, alphaVal, maxWidth, progress) {
  const size = 15;
  ctx.save();
  ctx.globalAlpha = alphaVal;
  ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.textBaseline = "alphabetic";
  const cols = block.columns || [];
  const rows = block.rows || [];
  const colW = maxWidth / cols.length;
  const headerH = size + 16;
  const tableReveal = smoothstep(0, 0.4, progress);
  ctx.save();
  ctx.globalAlpha = alphaVal * tableReveal;
  for (let ci = 0; ci < cols.length; ci++) {
    ctx.font = "600 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
    ctx.fillStyle = rgba(themeColor(theme, "secondary", theme.structure), alphaVal * tableReveal);
    ctx.fillText(cols[ci], x + ci * colW + 8, y + headerH - 6);
    ctx.strokeStyle = rgba(theme.structure, alphaVal * 0.2 * tableReveal);
    ctx.lineWidth = 0.5;
    ctx.strokeRect(x + ci * colW, y, colW, headerH);
  }
  ctx.restore();
  let ry = y + headerH;
  for (let ri = 0; ri < rows.length; ri++) {
    const rowReveal = smoothstep(0.2 + ri * 0.08, 0.3 + ri * 0.08, tableReveal);
    ctx.save();
    ctx.globalAlpha = alphaVal * rowReveal;
    ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
    for (let ci = 0; ci < cols.length; ci++) {
      const cell = (rows[ri][ci] !== undefined) ? rows[ri][ci] : "";
      ctx.fillStyle = rgba(theme.ink, alphaVal * 0.8 * rowReveal);
      ctx.fillText(cell, x + ci * colW + 8, ry + size + 4);
      ctx.strokeStyle = rgba(theme.structure, alphaVal * 0.12 * rowReveal);
      ctx.lineWidth = 0.3;
      ctx.strokeRect(x + ci * colW, ry, colW, LINE_HEIGHT + 8);
    }
    ctx.restore();
    ry += LINE_HEIGHT + 8;
  }
  return ry + 12;
}

function renderCitation(ctx, block, x, y, theme, alphaVal, maxWidth) {
  const size = 12;
  ctx.save();
  ctx.globalAlpha = alphaVal * 0.6;
  ctx.font = "400 " + size + 'px "EB Garamond", "Tantra Garamond", serif';
  ctx.textBaseline = "alphabetic";
  ctx.fillStyle = rgba(theme.structure, alphaVal * 0.5);
  const words = block.text.split(" ");
  let line = "";
  let ly = y;
  for (const word of words) {
    const test = line ? line + " " + word : word;
    if (ctx.measureText(test).width > maxWidth - 40 && line) {
      ctx.fillText(line, x + 20, ly + size);
      line = word;
      ly += 18;
    } else {
      line = test;
    }
  }
  if (line) {
    ctx.fillText(line, x + 20, ly + size);
  }
  ctx.restore();
  return ly + 8;
}

function renderDivider(ctx, block, x, y, theme, alphaVal, maxWidth) {
  ctx.save();
  ctx.globalAlpha = alphaVal * 0.25;
  ctx.strokeStyle = rgba(theme.structure, alphaVal * 0.25);
  ctx.lineWidth = 0.5;
  const cx = x + maxWidth / 2;
  ctx.beginPath();
  ctx.moveTo(cx - 120, y + 10);
  ctx.lineTo(cx + 120, y + 10);
  ctx.stroke();
  ctx.restore();
  return y + 32;
}

export function renderArgumentDisplay(ctx, t, scene, env) {
  const theme = env.theme;
  const blocks = (scene.params && scene.params.blocks) || [];
  const style = (scene.params && scene.params.style) || "academic";
  const revealType = (scene.params && scene.params.revealType) || "progressive";
  const a = alpha(t);
  if (!blocks.length) return;
  const x = MARGIN_X;
  let y = MARGIN_Y;
  const maxWidth = CONTENT_WIDTH;
  const totalBlocks = blocks.length;
  for (let i = 0; i < totalBlocks; i++) {
    const block = blocks[i];
    let blockProgress = 1;
    if (revealType === "progressive") {
      const blockStart = i / totalBlocks;
      const blockEnd = (i + 1) / totalBlocks;
      blockProgress = smoothstep(blockStart, blockEnd, t);
    }
    const ba = a * blockProgress;
    if (ba < 0.01) {
      y += 20;
      continue;
    }
    switch (block.type) {
      case "section-header":
        y = renderSectionHeader(ctx, block, x, y, theme, ba);
        break;
      case "body":
        y = renderBody(ctx, block, x, y, theme, ba, maxWidth);
        break;
      case "boxed-equation":
        y = renderBoxedEquation(ctx, block, x, y, theme, ba, maxWidth);
        break;
      case "proof":
        y = renderProof(ctx, block, x, y, theme, ba, maxWidth, blockProgress);
        break;
      case "table":
        y = renderComparisonTable(ctx, block, x, y, theme, ba, maxWidth, blockProgress);
        break;
      case "citation":
        y = renderCitation(ctx, block, x, y, theme, ba, maxWidth);
        break;
      case "divider":
        y = renderDivider(ctx, block, x, y, theme, ba, maxWidth);
        break;
      default:
        y += 20;
    }
  }
}
