// Modular typographic scale based on Fibonacci / golden ratio proportions
// Base: 16px body text
// Ratio: 1.25 (major third) — produces near-Fibonacci sequence: 13, 16, 20, 25, 31, 39, 49
// This aligns with Doczi's principle that neighboring parts share proportional limits.

export const SCALE = Object.freeze({
  micro:  10,   // footnotes, metadata
  small:  13,   // captions, labels
  body:   16,   // body text, subclaims
  lead:   20,   // lead text, emphasized body
  h3:     25,   // sub-headers, subclaim emphasis
  h2:     31,   // section headers, claims
  h1:     39,   // major claims, key propositions
  hero:   49,   // single-word emphasis, verdicts
});

// Vertical rhythm — every line height snaps to an 8px grid
// Line height = size × 1.5, rounded up to nearest 8px
export function lineHeight(size) {
  const raw = Math.round(size * 1.5);
  return Math.ceil(raw / 8) * 8;
}

export const LINE_HEIGHTS = Object.freeze(
  Object.fromEntries(
    Object.entries(SCALE).map(([name, size]) => [name, lineHeight(size)])
  )
);

// Semantic size lookup — move types reference names, not raw px
export function resolveSize(move) {
  const sizeName = move.size;
  if (typeof sizeName === "number") return sizeName;
  if (typeof sizeName === "string" && sizeName in SCALE) return SCALE[sizeName];
  return SCALE.body; // default
}

export function resolveLineHeight(move) {
  return lineHeight(resolveSize(move));
}

// Spacing units based on 8px grid (Doczi: reciprocal sharing of proportions)
export const SPACING = Object.freeze({
  xs:  4,    // tight spacing
  sm:  8,    // default gap
  md:  16,   // paragraph spacing
  lg:  24,   // section spacing
  xl:  40,   // major section spacing
});

// Layout constants (golden ratio proportions of 1280×720 canvas)
export const LAYOUT = Object.freeze({
  marginX: 80,               // left/right margin
  marginY: 60,               // top/bottom margin
  contentWidth: 1280 - 160,  // 1120px content area
  contentHeight: 720 - 120,  // 600px content area
  centerX: 640,
  centerY: 360,
  columnGap: 40,             // gap between columns
  // Golden section divisions of content width
  phiSection: Math.round((1280 - 160) * 0.382),  // smaller section (φ inverse)
  phiSectionLarge: Math.round((1280 - 160) * 0.618), // larger section (φ)
});
