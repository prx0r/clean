import { clamp, lerp } from "../../math.mjs";

export function hexToRgb(hex) {
  const normalized = hex.replace("#", "");
  const full = normalized.length === 3 ? normalized.split("").map((c) => c + c).join("") : normalized;
  const value = Number.parseInt(full, 16);
  return { r: ((value >> 16) & 255) / 255, g: ((value >> 8) & 255) / 255, b: (value & 255) / 255 };
}
export function rgbToHex({ r, g, b }) {
  const byte = (v) => Math.round(clamp(v) * 255).toString(16).padStart(2, "0");
  return `#${byte(r)}${byte(g)}${byte(b)}`;
}
const lin = (v) => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
const delinear = (v) => v <= 0.0031308 ? v * 12.92 : 1.055 * v ** (1 / 2.4) - 0.055;

export function rgbToOklab(rgb) {
  const r = lin(rgb.r), g = lin(rgb.g), b = lin(rgb.b);
  const l = Math.cbrt(0.4122214708*r + 0.5363325363*g + 0.0514459929*b);
  const m = Math.cbrt(0.2119034982*r + 0.6806995451*g + 0.1073969566*b);
  const s = Math.cbrt(0.0883024619*r + 0.2817188376*g + 0.6299787005*b);
  return { L:0.2104542553*l+0.793617785*m-0.0040720468*s, a:1.9779984951*l-2.428592205*m+0.4505937099*s, b:0.0259040371*l+0.7827717662*m-0.808675766*s };
}
export function oklabToRgb({ L, a, b }) {
  const l=(L+0.3963377774*a+0.2158037573*b)**3;
  const m=(L-0.1055613458*a-0.0638541728*b)**3;
  const s=(L-0.0894841775*a-1.291485548*b)**3;
  return { r:delinear(4.0767416621*l-3.3077115913*m+0.2309699292*s), g:delinear(-1.2684380046*l+2.6097574011*m-0.3413193965*s), b:delinear(-0.0041960863*l-0.7034186147*m+1.707614701*s) };
}
export function interpolateOklab(leftHex, rightHex, amount) {
  const l=rgbToOklab(hexToRgb(leftHex)), r=rgbToOklab(hexToRgb(rightHex));
  return rgbToHex(oklabToRgb({ L:lerp(l.L,r.L,amount), a:lerp(l.a,r.a,amount), b:lerp(l.b,r.b,amount) }));
}
