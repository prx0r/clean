import { motifRegistry } from "./motifs.mjs";
import { layerTypes } from "./composition.mjs";
import { semanticVisualNames } from "./semantic-visuals.mjs";
import { themes } from "./theme.mjs";

const ID_PATTERN = /^[a-z][a-z0-9-]{2,63}$/;
const SCENE_ID_PATTERN = /^[a-z][a-z0-9-]{2,31}$/;

function assertString(value, path, minimum, maximum) {
  if (typeof value !== "string" || value.length < minimum || value.length > maximum) {
    throw new Error(`${path} must be a string between ${minimum} and ${maximum} characters`);
  }
}

function assertNumber(value, path, minimum, maximum, integer = false) {
  if (typeof value !== "number" || !Number.isFinite(value) || value < minimum || value > maximum) {
    throw new Error(`${path} must be a number between ${minimum} and ${maximum}`);
  }
  if (integer && !Number.isInteger(value)) {
    throw new Error(`${path} must be an integer`);
  }
}

export function assertPack(pack) {
  if (!pack || typeof pack !== "object" || Array.isArray(pack)) {
    throw new Error("Pack must be a JSON object");
  }
  if (pack.version !== "1.0") throw new Error('pack.version must equal "1.0"');
  assertString(pack.id, "pack.id", 3, 64);
  if (!ID_PATTERN.test(pack.id)) throw new Error("pack.id must use lowercase kebab-case");
  assertString(pack.title, "pack.title", 3, 120);
  if (!themes[pack.theme]) throw new Error(`Unknown pack theme "${pack.theme}"`);
  assertNumber(pack.seed, "pack.seed", 0, 4294967295, true);

  if (!pack.render || typeof pack.render !== "object") throw new Error("pack.render is required");
  assertNumber(pack.render.width, "pack.render.width", 640, 7680, true);
  assertNumber(pack.render.height, "pack.render.height", 360, 4320, true);
  if (pack.render.width % 2 || pack.render.height % 2) {
    throw new Error("Render dimensions must be even for yuv420p encoding");
  }
  assertNumber(pack.render.fps, "pack.render.fps", 1, 60, true);
  assertNumber(pack.render.sceneDuration, "pack.render.sceneDuration", 1, 30);
  if (pack.render.crf !== undefined) assertNumber(pack.render.crf, "pack.render.crf", 0, 35, true);
  if (pack.render.transitionDuration !== undefined) {
    assertNumber(pack.render.transitionDuration, "pack.render.transitionDuration", 0, 2);
  }

  if (!Array.isArray(pack.scenes) || pack.scenes.length < 1 || pack.scenes.length > 100) {
    throw new Error("pack.scenes must contain between 1 and 100 scenes");
  }

  const ids = new Set();
  for (const [index, scene] of pack.scenes.entries()) {
    const path = `pack.scenes[${index}]`;
    if (!scene || typeof scene !== "object" || Array.isArray(scene)) {
      throw new Error(`${path} must be an object`);
    }
    assertString(scene.id, `${path}.id`, 3, 32);
    if (!SCENE_ID_PATTERN.test(scene.id)) throw new Error(`${path}.id must use lowercase kebab-case`);
    if (ids.has(scene.id)) throw new Error(`Duplicate scene id "${scene.id}"`);
    ids.add(scene.id);
    assertString(scene.title, `${path}.title`, 2, 80);
    assertString(scene.subtitle, `${path}.subtitle`, 2, 140);
    assertString(scene.term, `${path}.term`, 1, 50);
    assertString(scene.devanagari, `${path}.devanagari`, 1, 50);
    if (!/[\u0900-\u097f]/u.test(scene.devanagari)) {
      throw new Error(`${path}.devanagari must contain Devanāgarī text, not IAST transliteration`);
    }
    if (!motifRegistry[scene.motif]) {
      throw new Error(`${path}.motif has unknown value "${scene.motif}"`);
    }
    if (scene.motif === "composition") {
      if (!Array.isArray(scene.layers) || scene.layers.length < 1 || scene.layers.length > 40) {
        throw new Error(`${path}.layers must contain between 1 and 40 layers for the composition motif`);
      }
      for (const [layerIndex, layer] of scene.layers.entries()) {
        if (!layer || typeof layer !== "object" || !layerTypes.includes(layer.type)) {
          throw new Error(`${path}.layers[${layerIndex}] has an unknown layer type`);
        }
      }
    }
    if (scene.motif === "semantic-essay") {
      if (!scene.params || !semanticVisualNames.includes(scene.params.visual)) {
        throw new Error(
          `${path}.params.visual must be one of: ${semanticVisualNames.join(", ")}`,
        );
      }
    }
    if (scene.theme !== undefined && !themes[scene.theme]) {
      throw new Error(`${path}.theme has unknown value "${scene.theme}"`);
    }
    if (scene.duration !== undefined) assertNumber(scene.duration, `${path}.duration`, 1, 30);
    if (scene.seed !== undefined) assertNumber(scene.seed, `${path}.seed`, 0, 4294967295, true);
  }
  return pack;
}

export function packDuration(pack) {
  return pack.scenes.reduce(
    (sum, scene) => sum + (scene.duration ?? pack.render.sceneDuration),
    0,
  );
}
