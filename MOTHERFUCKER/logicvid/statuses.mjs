// Color system based on Albers' Interaction of Color principles:
// 1. Color intervals matter more than absolute colors (relational, not absolute)
// 2. Equal light intensity = vanishing boundaries (use sparingly)
// 3. Weber-Fechner: perceptual response is logarithmic, use gamma-aware interpolation
//
// Color intervals (CIELAB perceptual distance):
// - ink → muted: maximum contrast (text hierarchy)
// - ink → blue/red/green/gold: equal perceptual distance from neutral
// - Each status color is spaced for distinct semantic meaning

const hexRgb = (hex) => {
  const h = hex.replace("#", "");
  return [parseInt(h.slice(0,2),16), parseInt(h.slice(2,4),16), parseInt(h.slice(4,6),16)];
};

export const COLORS = {
  // Base neutrals (grayscale, no hue)
  ink:   hexRgb("#1a1a1a"),   // near-black — main text
  muted: hexRgb("#8c8c8c"),   // mid-gray — secondary text, subclaims
  faint: hexRgb("#c1c1c1"),   // light-gray — dividers, borders
  paper: hexRgb("#fafaf8"),   // off-white — background

  // Status colors (equal perceptual weight)
  blue:  hexRgb("#2d6685"),   // scientific/descriptive — hue 200°
  red:   hexRgb("#a43e46"),   // objection/refuted — hue 357°
  green: hexRgb("#3e7857"),   // resolved/supported — hue 145°
  gold:  hexRgb("#a9782f"),   // frontier/question — hue 38°
};

// Albers-Weber-Fechner interpolation: logarithmic mixing for perceptual evenness
export function mixColor(a, b, t) {
  // Apply Weber-Fechner: perceptual response ∝ log(stimulus)
  // Transform linear t to perceptual t using log curve
  const pt = 1 - Math.exp(-t * 5);
  const clamped = Math.max(0, Math.min(1, pt));
  return a.map((c, i) => Math.round(c + (b[i] - c) * clamped));
}

export function rgba(color, alpha = 1) {
  return `rgba(${color[0]},${color[1]},${color[2]},${alpha})`;
}

export function statusColor(status) {
  switch (status) {
    case "refuted":   return COLORS.red;
    case "resolved":  return COLORS.green;
    case "highlight":
    case "frontier":  return COLORS.gold;
    case "scientific": return COLORS.blue;
    case "neutral":   return COLORS.muted;
    default:          return COLORS.ink;
  }
}
