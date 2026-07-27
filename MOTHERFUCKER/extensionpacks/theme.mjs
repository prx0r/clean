import { themes, palette, getTheme, typography, LOGICAL_WIDTH, LOGICAL_HEIGHT } from "../theme.mjs";

const dynamicTokens = new Map();

export { themes, palette, getTheme, typography, LOGICAL_WIDTH, LOGICAL_HEIGHT };

export function registerTheme(name, tokens) {
  if (!name || !tokens || typeof tokens !== "object") {
    throw new Error(`registerTheme requires a name and tokens object`);
  }
  if (themes[name] || dynamicTokens.has(name)) {
    throw new Error(`Theme "${name}" is already registered`);
  }
  dynamicTokens.set(name, tokens);
}

export function getDynamicTheme(name) {
  return dynamicTokens.get(name);
}

export function getAllThemeNames() {
  return Object.freeze([...Object.keys(themes), ...dynamicTokens.keys()]);
}
