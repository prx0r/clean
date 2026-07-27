#!/usr/bin/env node
import { access, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");

async function exists(path) {
  try { await access(path); return true; } catch { return false; }
}

async function patchFile(relative, transforms) {
  const path = join(ROOT, relative);
  let source = await readFile(path, "utf8");
  const original = source;
  for (const transform of transforms) source = transform(source);
  if (source !== original) {
    await writeFile(path, source);
    console.log(`patched ${relative}`);
  } else {
    console.log(`unchanged ${relative}`);
  }
}

function replaceOnce(search, replacement) {
  return (source) => {
    if (source.includes(replacement)) return source;
    if (!source.includes(search)) {
      throw new Error(`Patch anchor not found:\n${search.slice(0, 160)}`);
    }
    return source.replace(search, replacement);
  };
}

await patchFile("theme.mjs", [
  replaceOnce(
    'export function getTheme(name = "ivoryManuscript") {\n  const theme = themes[name];',
    'const dynamicThemes = new Map();\n\nexport function registerTheme(name, tokens) {\n' +
    '  if (!name || !tokens || typeof tokens !== "object") throw new Error("registerTheme requires name and token object");\n' +
    '  const existing = themes[name] ?? dynamicThemes.get(name);\n' +
    '  if (existing) {\n' +
    '    if (JSON.stringify(existing) === JSON.stringify({ name, ...tokens })) return existing;\n' +
    '    throw new Error(`Theme "${name}" is already registered with different tokens`);\n' +
    '  }\n' +
    '  const theme = Object.freeze({ name, ...tokens });\n' +
    '  dynamicThemes.set(name, theme);\n' +
    '  return theme;\n' +
    '}\n\nexport function listThemeNames() {\n' +
    '  return Object.freeze([...Object.keys(themes), ...dynamicThemes.keys()]);\n' +
    '}\n\nexport function getTheme(name = "ivoryManuscript") {\n  const theme = themes[name] ?? dynamicThemes.get(name);'
  ),
  (source) => source.replace(
    'Available themes: ${Object.keys(themes).join(", ")}',
    'Available themes: ${listThemeNames().join(", ")}'
  ),
]);

await patchFile("semantic-visuals.mjs", [
  replaceOnce(
    'const dynamicRenderers = new Map();',
    'const dynamicRenderers = new Map();\nconst dynamicRendererMetadata = new Map();'
  ),
  (source) => {
    const old = `export function registerDynamicRenderer(name, renderer) {
  if (!name || typeof renderer !== "function") {
    throw new Error(\`registerDynamicRenderer requires name and function renderer\`);
  }
  if (staticRenderers[name] || dynamicRenderers.has(name)) {
    throw new Error(\`Renderer "\${name}" is already registered\`);
  }
  dynamicRenderers.set(name, renderer);
}`;
    const replacement = `export function registerDynamicRenderer(nameOrDefinition, rendererArg, descriptionArg) {
  const definition = typeof nameOrDefinition === "object"
    ? nameOrDefinition
    : { name: nameOrDefinition, renderer: rendererArg, description: descriptionArg };
  const { name, renderer, description = "Dynamically registered semantic mechanism." } = definition;
  if (!name || typeof renderer !== "function") {
    throw new Error("registerDynamicRenderer requires a name and renderer function");
  }
  const existing = dynamicRenderers.get(name);
  if (staticRenderers[name]) throw new Error(\`Renderer "\${name}" is already built in\`);
  if (existing) {
    if (existing === renderer) return;
    throw new Error(\`Renderer "\${name}" is already registered\`);
  }
  dynamicRenderers.set(name, renderer);
  dynamicRendererMetadata.set(name, Object.freeze({ name, description }));
}

export function hasSemanticVisual(name) {
  return Boolean(staticRenderers[name] || dynamicRenderers.has(name) || systemVisualNames.includes(name));
}

export function listSemanticVisualNames() {
  return Object.freeze([...new Set([...semanticVisualNames, ...dynamicRenderers.keys()])]);
}

export function listDynamicSemanticVisuals() {
  return Object.freeze([...dynamicRendererMetadata.values()]);
}`;
    if (source.includes(replacement)) return source;
    if (!source.includes(old)) throw new Error("semantic dynamic registry anchor not found");
    return source.replace(old, replacement);
  },
  (source) => source.replace(
    '`Choose one of: ${semanticVisualNames.join(", ")}`',
    '`Choose one of: ${listSemanticVisualNames().join(", ")}`'
  ),
]);

await patchFile("visual-semantics.mjs", [
  replaceOnce(
    'export const mechanismRelations = Object.freeze({',
    'const dynamicMechanismRelations = new Map();\n\nexport const mechanismRelations = Object.freeze({'
  ),
  replaceOnce(
    'export function isMechanismCompatible(visual, relationType) {\n  return mechanismRelations[visual]?.includes(relationType) ?? false;\n}',
    `export function registerMechanismRelations(mechanismId, relations) {
  if (!mechanismId || !Array.isArray(relations) || relations.length === 0) {
    throw new Error("registerMechanismRelations requires mechanism id and relations");
  }
  const invalid = relations.filter((relation) => !relationTypes.includes(relation));
  if (invalid.length) throw new Error(\`Unknown relation types: \${invalid.join(", ")}\`);
  const existing = dynamicMechanismRelations.get(mechanismId);
  if (existing) {
    if (JSON.stringify(existing) === JSON.stringify(relations)) return;
    throw new Error(\`Relations for "\${mechanismId}" are already registered\`);
  }
  dynamicMechanismRelations.set(mechanismId, Object.freeze([...relations]));
}

export function getMechanismRelations(visual) {
  return mechanismRelations[visual] ?? dynamicMechanismRelations.get(visual) ?? [];
}

export function isMechanismCompatible(visual, relationType) {
  return getMechanismRelations(visual).includes(relationType);
}`
  ),
  (source) => source.replace(
    'const supported = mechanismRelations[visual] ?? [];',
    'const supported = getMechanismRelations(visual);'
  ),
]);

await patchFile("schema.mjs", [
  (source) => source.replace(
    'import { semanticVisualNames } from "./semantic-visuals.mjs";',
    'import { hasSemanticVisual, listSemanticVisualNames } from "./semantic-visuals.mjs";'
  ),
  (source) => source.replace(
    '!semanticVisualNames.includes(scene.params.visual)',
    '!hasSemanticVisual(scene.params.visual)'
  ),
  (source) => source.replace(
    '${semanticVisualNames.join(", ")}',
    '${listSemanticVisualNames().join(", ")}'
  ),
  (source) => source.replace(
    'if (!themes[pack.theme]) throw new Error(`Unknown pack theme "${pack.theme}"`);',
    'getTheme(pack.theme);'
  ).replace(
    'import { themes } from "./theme.mjs";',
    'import { getTheme } from "./theme.mjs";'
  ).replace(
    'if (scene.theme !== undefined && !themes[scene.theme]) {\n      throw new Error(`${path}.theme has unknown value "${scene.theme}"`);\n    }',
    'if (scene.theme !== undefined) getTheme(scene.theme);'
  ),
]);

const extensionTheme = `export {
  themes,
  palette,
  getTheme,
  registerTheme,
  listThemeNames as getAllThemeNames,
  typography,
  LOGICAL_WIDTH,
  LOGICAL_HEIGHT,
} from "../theme.mjs";
`;
await writeFile(join(ROOT, "extensionpacks/theme.mjs"), extensionTheme);

const extensionSemantics = `export {
  relationTypes,
  semanticRolesV2,
  visualOperatorsV2,
  continuityActions,
  encodingChannels,
  mechanismRelations,
  roleOperators,
  registerMechanismRelations,
  getMechanismRelations,
  isMechanismCompatible,
  isRoleOperatorCompatible,
  compatibilityExplanation,
} from "../visual-semantics.mjs";
`;
await writeFile(join(ROOT, "extensionpacks/visual-semantics.mjs"), extensionSemantics);

const extensionVisuals = `import {
  semanticVisualNames,
  registerDynamicRenderer,
  listDynamicSemanticVisuals,
  listSemanticVisualNames,
} from "../semantic-visuals.mjs";

export const baseSemanticVisualNames = semanticVisualNames;

export function registerSemanticVisual(definition) {
  registerDynamicRenderer(definition);
}

export function getAllDynamicMechanisms() {
  return listDynamicSemanticVisuals();
}

export { listSemanticVisualNames };
`;
await writeFile(join(ROOT, "extensionpacks/semantic-visuals.mjs"), extensionVisuals);

for (const filename of ["anatomy-visuals.mjs", "neuro-visuals.mjs", "science-visuals.mjs"]) {
  const path = join(ROOT, "src", filename);
  if (!(await exists(path))) continue;
  let source = await readFile(path, "utf8");
  source = source
    .replaceAll('from "./math.mjs"', 'from "../math.mjs"')
    .replaceAll('from "./primitives.mjs"', 'from "../primitives.mjs"')
    .replaceAll('from "./theme.mjs"', 'from "../theme.mjs"')
    .replaceAll('from "./visual-assets.mjs"', 'from "../visual-assets.mjs"')
    .replaceAll('from "./anatomy-geometry.mjs"', 'from "../anatomy-geometry.mjs"');
  if (filename === "neuro-visuals.mjs") {
    if (!source.includes('import { Path2D } from "@napi-rs/canvas";')) {
      source = 'import { Path2D } from "@napi-rs/canvas";\n\n' + source;
    }
    source = source.replace(/,\s*drawGrid,\s*\n} from "\.\.\/primitives\.mjs";/, '\n} from "../primitives.mjs";');
  }
  await writeFile(path, source);
  console.log(`repaired src/${filename}`);
}

const index = `export {
  FrameRenderer,
  loadPack,
  renderVideo,
  renderPoster,
  renderContactSheet,
  validateVideo,
  probeVideo,
} from "./renderer.mjs";

export {
  getTheme,
  registerTheme,
  listThemeNames,
  themes,
  palette,
  typography,
  LOGICAL_WIDTH,
  LOGICAL_HEIGHT,
} from "./theme.mjs";

export {
  relationTypes,
  semanticRolesV2,
  visualOperatorsV2,
  continuityActions,
  encodingChannels,
  registerMechanismRelations,
  getMechanismRelations,
  isMechanismCompatible,
  isRoleOperatorCompatible,
} from "./visual-semantics.mjs";

export {
  registerVisualAsset,
  hasVisualAsset,
  listVisualAssets,
  listVisualAssetNames,
  renderVisualAsset,
  renderAssetLayers,
} from "./visual-assets.mjs";

export {
  registerDynamicRenderer,
  hasSemanticVisual,
  listSemanticVisualNames,
  listDynamicSemanticVisuals,
} from "./semantic-visuals.mjs";

export {
  activateCapabilityPacks,
  resolveCapabilityProfile,
  installedCapabilityPackIds,
  activeCapabilityPackIds,
  isVisualAllowedByPacks,
  isAssetAllowedByPacks,
} from "./extensionpacks/capability-packs.mjs";
`;
await writeFile(join(ROOT, "index.mjs"), index);

console.log("formal framework patch applied");
