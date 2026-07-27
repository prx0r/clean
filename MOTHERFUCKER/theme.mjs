export const LOGICAL_WIDTH = 1280;
export const LOGICAL_HEIGHT = 720;

export const palette = Object.freeze({
  parchment: "#f0e6d0",
  parchmentLight: "#f8f2e2",
  paper: "#f7f1e3",
  ivory: "#fcfaf5",
  ink: "#261f1d",
  umber: "#4c3a2d",
  crimson: "#8e2b37",
  saffron: "#cc9439",
  gold: "#b78e44",
  goldLight: "#ebce80",
  indigo: "#34426b",
  blueGrey: "#67789a",
  teal: "#558484",
  slate: "#5c6168",
  white: "#faf6ed",
  night: "#181c28",
  lotusPink: "#bf6e84",
  earth: "#756042",
  green: "#61845f",
});

export const themes = Object.freeze({
  ivoryManuscript: {
    name: "ivoryManuscript",
    background: palette.parchment,
    backgroundLight: palette.parchmentLight,
    backgroundEdge: "#e2d3b7",
    ink: palette.ink,
    structure: palette.umber,
    border: palette.umber,
    accent: palette.crimson,
    secondary: palette.indigo,
    luminous: palette.goldLight,
    panel: "#f7efdb",
    particle: palette.gold,
    textureOpacity: 0.08,
  },
  whiteScientific: {
    name: "whiteScientific",
    background: "#f8f7f2",
    backgroundLight: "#ffffff",
    backgroundEdge: "#ebe7dc",
    ink: "#1f232c",
    structure: "#4d5360",
    border: "#7b6a59",
    accent: palette.crimson,
    secondary: palette.indigo,
    luminous: palette.goldLight,
    panel: "#fbfaf6",
    particle: palette.gold,
    textureOpacity: 0.035,
  },
  midnightVellum: {
    name: "midnightVellum",
    background: "#111725",
    backgroundLight: "#232944",
    backgroundEdge: "#090d16",
    ink: "#f2eee4",
    structure: "#aeb7cc",
    border: "#98885f",
    accent: "#c65a6f",
    secondary: "#7f91d2",
    luminous: "#f2d992",
    panel: "#1b2233",
    particle: "#d9c68f",
    textureOpacity: 0.07,
  },
});

const dynamicThemes = new Map();

export function registerTheme(name, tokens) {
  if (!name || !tokens || typeof tokens !== "object") throw new Error("registerTheme requires name and token object");
  const existing = themes[name] ?? dynamicThemes.get(name);
  if (existing) {
    if (JSON.stringify(existing) === JSON.stringify({ name, ...tokens })) return existing;
    throw new Error(`Theme "${name}" is already registered with different tokens`);
  }
  const theme = Object.freeze({ name, ...tokens });
  dynamicThemes.set(name, theme);
  return theme;
}

export function listThemeNames() {
  return Object.freeze([...Object.keys(themes), ...dynamicThemes.keys()]);
}

export function getTheme(name = "ivoryManuscript") {
  const theme = themes[name] ?? dynamicThemes.get(name);
  if (!theme) {
    throw new Error(`Unknown theme "${name}". Available themes: ${listThemeNames().join(", ")}`);
  }
  return theme;
}

export const typography = Object.freeze({
  title: { family: "Tantra Garamond", size: 31, weight: 600 },
  subtitle: { family: "Tantra Garamond", size: 18, weight: 400 },
  term: { family: "Tantra Garamond", size: 22, weight: 600 },
  label: { family: "Tantra Garamond", size: 16, weight: 500 },
  small: { family: "Tantra Garamond", size: 14, weight: 400 },
  tiny: { family: "Tantra Garamond", size: 11, weight: 400 },
  devanagari: { family: "Tantra Devanagari", size: 23, weight: 500 },
  devanagariLarge: { family: "Tantra Devanagari", size: 42, weight: 600 },
});
