import { rgba } from "../../math.mjs";
import { interpolateOklab } from "./color.mjs";

export function conicGradient(ctx, {
  cx, cy, angle = 0,
  stops = [[0,"#fff7db"],[0.33,"#e6b84f"],[0.66,"#a34450"],[1,"#fff7db"]],
} = {}) {
  if (typeof ctx.createConicGradient !== "function") return null;
  const gradient = ctx.createConicGradient(angle, cx, cy);
  for (const [offset, color] of stops) gradient.addColorStop(offset, color);
  return gradient;
}

export function radialGlow(ctx, { cx, cy, innerRadius = 0, outerRadius = 100, color = "#f5d977", alpha = 0.7 } = {}) {
  const gradient = ctx.createRadialGradient(cx, cy, innerRadius, cx, cy, outerRadius);
  gradient.addColorStop(0, rgba(color, alpha));
  gradient.addColorStop(0.38, rgba(color, alpha * 0.42));
  gradient.addColorStop(1, rgba(color, 0));
  return gradient;
}

export function paletteRamp(colors, count = 12) {
  return Array.from({ length: count }, (_, index) => {
    const p = index / Math.max(1, count - 1);
    const scaled = p * (colors.length - 1);
    const left = Math.floor(scaled);
    const right = Math.min(colors.length - 1, left + 1);
    return interpolateOklab(colors[left], colors[right], scaled - left);
  });
}

export const materialProfiles = Object.freeze({
  "mineral-manuscript": { blend:"multiply", glowBlur:3, grainOpacity:0.028, palette:["#f3eddf","#25304a","#8b2f3c","#b88c3e","#61777d"] },
  "ritual-gold": { blend:"screen", glowBlur:10, grainOpacity:0.018, palette:["#16080a","#6d161c","#d79f36","#ffe9a6","#f9f4df"] },
  "luminous-subtle-body": { blend:"screen", glowBlur:14, grainOpacity:0.01, palette:["#070b19","#284b87","#55cce3","#efbb45","#fff8df"] },
  "technical-neural": { blend:"screen", glowBlur:5, grainOpacity:0.006, palette:["#f8fafb","#1b324b","#2b80ad","#5bc6db","#d5535d"] },
  "visionary-midnight": { blend:"lighter", glowBlur:18, grainOpacity:0.015, palette:["#03050d","#16266f","#6c36c8","#e83f8e","#ffd96a"] },
  "ash-and-ember": { blend:"screen", glowBlur:8, grainOpacity:0.035, palette:["#151312","#4c4038","#9d3a20","#ee7a32","#f4d8ad"] },
});
