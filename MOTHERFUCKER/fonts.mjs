import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { GlobalFonts } from "@napi-rs/canvas";

import { typography } from "./theme.mjs";

const FRAMEWORK_ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
let initialized = false;

function registerFont(path, family) {
  const result = GlobalFonts.registerFromPath(path, family);
  if (!result) {
    throw new Error(`Skia failed to register font ${path}`);
  }
}

export function initializeFonts() {
  if (initialized) return;

  registerFont(
    join(FRAMEWORK_ROOT, "assets/fonts/eb-garamond/EBGaramond-Variable.ttf"),
    typography.title.family,
  );
  registerFont(
    join(FRAMEWORK_ROOT, "assets/fonts/eb-garamond/EBGaramond-Italic-Variable.ttf"),
    typography.title.family,
  );
  registerFont(
    join(FRAMEWORK_ROOT, "assets/fonts/noto-serif-devanagari/NotoSerifDevanagari-Variable.ttf"),
    typography.devanagari.family,
  );

  try {
    const HERE = dirname(fileURLToPath(import.meta.url));
    const srcSerifDir = join(HERE, "node_modules/source-serif/VAR");
    registerFont(
      join(srcSerifDir, "SourceSerif4Variable-Roman.ttf"),
      "Source Serif 4",
    );
    registerFont(
      join(srcSerifDir, "SourceSerif4Variable-Italic.ttf"),
      "Source Serif 4",
    );
  } catch (e) {
    console.warn("Source Serif 4 not available:", e.message);
  }

  initialized = true;
}

export function fontString(style) {
  const weight = style.weight ?? 400;
  const fontStyle = style.italic ? "italic " : "";
  return `${fontStyle}${weight} ${style.size}px "${style.family}"`;
}

export function applyTextStyle(ctx, style, options = {}) {
  ctx.font = fontString({ ...style, ...options });
  ctx.textRendering = "optimizeLegibility";
  ctx.fontKerning = "normal";
  ctx.letterSpacing = options.letterSpacing ?? "0px";
  ctx.wordSpacing = options.wordSpacing ?? "0px";
  ctx.lang = options.lang ?? "en";
  ctx.direction = options.direction ?? "ltr";
  ctx.textBaseline = options.baseline ?? "alphabetic";
  ctx.textAlign = options.align ?? "left";
}

export function fitText(ctx, text, style, maxWidth, minimumSize = 10) {
  let size = style.size;
  while (size > minimumSize) {
    applyTextStyle(ctx, { ...style, size });
    if (ctx.measureText(text).width <= maxWidth) return size;
    size -= 0.5;
  }
  return minimumSize;
}

export function fontStatus() {
  initializeFonts();
  return {
    latinFamily: typography.title.family,
    devanagariFamily: typography.devanagari.family,
    latinRegistered: GlobalFonts.has(typography.title.family),
    devanagariRegistered: GlobalFonts.has(typography.devanagari.family),
  };
}
