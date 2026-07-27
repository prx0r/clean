import { readdir, readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import {
  baseSemanticVisualNames,
  registerSemanticVisual,
} from "./semantic-visuals.mjs";
import { registerTheme } from "./theme.mjs";
import { registerMechanismRelations } from "./visual-semantics.mjs";
import { registerVisualAsset } from "./visual-assets.mjs";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
export const CAPABILITY_PACK_ROOT = join(ROOT, "capability-packs");
const PACK_ID = /^[a-z][a-z0-9-]{2,63}$/u;

const manifestCache = new Map();
const profileCache = new Map();
const activatedPacks = new Set();

function packIds(ids = ["base"]) {
  const values = ids?.length ? ids : ["base"];
  if (!Array.isArray(values)) throw new Error("capabilityPacks must be an array of pack ids");
  const normalized = [...new Set(values)];
  for (const id of normalized) {
    if (!PACK_ID.test(id)) throw new Error(`Invalid capability pack id "${id}"`);
  }
  return normalized;
}

function manifestPath(id) {
  return join(CAPABILITY_PACK_ROOT, id, "pack.json");
}

function assertText(value, path, minimum = 3, maximum = 1000) {
  if (typeof value !== "string" || value.length < minimum || value.length > maximum) {
    throw new Error(`${path} must be a string between ${minimum} and ${maximum} characters`);
  }
}

export function assertCapabilityManifest(manifest) {
  if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) {
    throw new Error("Capability pack manifest must be an object");
  }
  if (manifest.version !== "1.0") throw new Error('capability manifest version must equal "1.0"');
  assertText(manifest.id, "manifest.id", 3, 64);
  if (!PACK_ID.test(manifest.id)) throw new Error("manifest.id must use lowercase kebab-case");
  assertText(manifest.title, "manifest.title", 3, 120);
  assertText(manifest.description, "manifest.description", 20, 1000);
  if (!Array.isArray(manifest.extends)) throw new Error("manifest.extends must be an array");
  packIds(manifest.extends);
  if (!Array.isArray(manifest.mechanisms)) throw new Error("manifest.mechanisms must be an array");
  const mechanismIds = new Set();
  for (const [index, mechanism] of manifest.mechanisms.entries()) {
    const path = `manifest.mechanisms[${index}]`;
    assertText(mechanism?.id, `${path}.id`, 3, 64);
    if (!PACK_ID.test(mechanism.id)) throw new Error(`${path}.id must use lowercase kebab-case`);
    if (mechanismIds.has(mechanism.id)) throw new Error(`Duplicate mechanism "${mechanism.id}"`);
    mechanismIds.add(mechanism.id);
    assertText(mechanism.description, `${path}.description`, 20, 600);
    assertText(mechanism.motionProof, `${path}.motionProof`, 20, 600);
    if (!Array.isArray(mechanism.relations) || mechanism.relations.length < 1) {
      throw new Error(`${path}.relations must contain at least one relation`);
    }
    if (!Array.isArray(mechanism.operators) || mechanism.operators.length < 1) {
      throw new Error(`${path}.operators must contain at least one visual operator`);
    }
    if (!Array.isArray(mechanism.semanticTags) || mechanism.semanticTags.length < 2) {
      throw new Error(`${path}.semanticTags must contain at least two search tags`);
    }
  }
  if (manifest.assets !== undefined && !Array.isArray(manifest.assets)) {
    throw new Error("manifest.assets must be an array");
  }
  const assetIds = new Set();
  for (const [index, asset] of (manifest.assets ?? []).entries()) {
    const path = `manifest.assets[${index}]`;
    assertText(asset?.id, `${path}.id`, 3, 64);
    if (!PACK_ID.test(asset.id)) throw new Error(`${path}.id must use lowercase kebab-case`);
    if (assetIds.has(asset.id)) throw new Error(`Duplicate asset "${asset.id}"`);
    assetIds.add(asset.id);
    assertText(asset.description, `${path}.description`, 20, 600);
    assertText(asset.category, `${path}.category`, 3, 80);
    assertText(asset.epistemicMode, `${path}.epistemicMode`, 3, 80);
    if (!Array.isArray(asset.semanticTags) || asset.semanticTags.length < 2) {
      throw new Error(`${path}.semanticTags must contain at least two search tags`);
    }
  }
  if (manifest.themes !== undefined && !Array.isArray(manifest.themes)) {
    throw new Error("manifest.themes must be an array");
  }
  for (const [index, theme] of (manifest.themes ?? []).entries()) {
    assertText(theme?.name, `manifest.themes[${index}].name`, 3, 64);
    if (!theme.tokens || typeof theme.tokens !== "object") {
      throw new Error(`manifest.themes[${index}].tokens must be an object`);
    }
  }
  if (manifest.runtimeModule !== undefined) {
    assertText(manifest.runtimeModule, "manifest.runtimeModule", 3, 300);
  }
  if (!manifest.defaultTheme) throw new Error("manifest.defaultTheme is required");
  return manifest;
}

export async function loadCapabilityManifest(id) {
  if (manifestCache.has(id)) return manifestCache.get(id);
  const path = manifestPath(id);
  let manifest;
  try {
    manifest = JSON.parse(await readFile(path, "utf8"));
  } catch (error) {
    throw new Error(`Cannot load capability pack "${id}" at ${path}: ${error.message}`);
  }
  assertCapabilityManifest(manifest);
  if (manifest.id !== id) {
    throw new Error(`Capability directory "${id}" contains manifest id "${manifest.id}"`);
  }
  const record = Object.freeze({ manifest, path, directory: dirname(path) });
  manifestCache.set(id, record);
  return record;
}

async function inheritanceOrder(ids) {
  const ordered = [];
  const permanent = new Set();
  const visiting = [];

  async function visit(id) {
    if (permanent.has(id)) return;
    const cycleAt = visiting.indexOf(id);
    if (cycleAt >= 0) {
      throw new Error(`Capability inheritance cycle: ${[...visiting.slice(cycleAt), id].join(" -> ")}`);
    }
    visiting.push(id);
    const record = await loadCapabilityManifest(id);
    for (const parent of record.manifest.extends) await visit(parent);
    visiting.pop();
    permanent.add(id);
    ordered.push(record);
  }

  for (const id of packIds(ids)) await visit(id);
  return ordered;
}

function publicProfile(profile) {
  return {
    requestedPacks: [...profile.requestedPacks],
    inheritanceOrder: [...profile.inheritanceOrder],
    defaultTheme: profile.defaultTheme,
    themes: [...profile.themes],
    mechanisms: [...profile.mechanisms],
    mechanismOwners: Object.fromEntries(profile.mechanismOwners),
    assets: [...profile.assets],
    assetOwners: Object.fromEntries(profile.assetOwners),
    selectionPolicy: profile.selectionPolicy,
  };
}

function profileKey(ids) {
  return [...packIds(ids)].sort().join("|");
}

export async function activateCapabilityPacks(ids = ["base"]) {
  const requested = packIds(ids);
  const key = profileKey(requested);
  if (profileCache.has(key)) return publicProfile(profileCache.get(key));
  const records = await inheritanceOrder(requested);
  const mechanisms = new Set();
  const mechanismOwners = new Map();
  const assets = new Set();
  const assetOwners = new Map();
  const themes = new Set();
  let defaultTheme = "ivoryManuscript";
  let selectionPolicy = {};

  for (const record of records) {
    const { manifest } = record;
    if (manifest.includeBuiltins) {
      for (const name of baseSemanticVisualNames) {
        mechanisms.add(name);
        mechanismOwners.set(name, manifest.id);
      }
    }
    for (const theme of manifest.themes ?? []) {
      registerTheme(theme.name, theme.tokens);
      themes.add(theme.name);
    }
    if (manifest.defaultTheme) defaultTheme = manifest.defaultTheme;
    selectionPolicy = {
      ...selectionPolicy,
      ...(manifest.selectionPolicy ?? {}),
    };

    let implementations = {};
    let assetImplementations = {};
    if (manifest.runtimeModule) {
      const modulePath = resolve(record.directory, manifest.runtimeModule);
      const runtime = await import(pathToFileURL(modulePath).href);
      implementations = runtime.mechanismImplementations ?? {};
      assetImplementations = runtime.assetImplementations ?? {};
    }
    for (const mechanism of manifest.mechanisms) {
      const previousOwner = mechanismOwners.get(mechanism.id);
      if (previousOwner && previousOwner !== manifest.id) {
        throw new Error(
          `Mechanism "${mechanism.id}" is declared by both "${previousOwner}" and "${manifest.id}"`,
        );
      }
      const renderer = implementations[mechanism.id];
      if (typeof renderer !== "function") {
        throw new Error(
          `Capability pack "${manifest.id}" declares "${mechanism.id}" but its runtime module does not export an implementation`,
        );
      }
      registerSemanticVisual({
        name: mechanism.id,
        renderer,
        description: mechanism.description,
      });
      registerMechanismRelations(mechanism.id, mechanism.relations);
      mechanisms.add(mechanism.id);
      mechanismOwners.set(mechanism.id, manifest.id);
    }
    for (const asset of manifest.assets ?? []) {
      const previousOwner = assetOwners.get(asset.id);
      if (previousOwner && previousOwner !== manifest.id) {
        throw new Error(
          `Visual asset "${asset.id}" is declared by both "${previousOwner}" and "${manifest.id}"`,
        );
      }
      const renderer = assetImplementations[asset.id];
      if (typeof renderer !== "function") {
        throw new Error(
          `Capability pack "${manifest.id}" declares asset "${asset.id}" but its runtime module does not export an implementation`,
        );
      }
      registerVisualAsset({
        name: asset.id,
        renderer,
        description: asset.description,
        category: asset.category,
        epistemicMode: asset.epistemicMode,
        semanticTags: asset.semanticTags,
      });
      assets.add(asset.id);
      assetOwners.set(asset.id, manifest.id);
    }
    activatedPacks.add(manifest.id);
  }

  const profile = Object.freeze({
    requestedPacks: Object.freeze(requested),
    inheritanceOrder: Object.freeze(records.map((record) => record.manifest.id)),
    defaultTheme,
    themes: Object.freeze([...themes]),
    mechanisms: Object.freeze([...mechanisms]),
    mechanismSet: new Set(mechanisms),
    mechanismOwners,
    assets: Object.freeze([...assets]),
    assetSet: new Set(assets),
    assetOwners,
    selectionPolicy: Object.freeze(selectionPolicy),
  });
  profileCache.set(key, profile);
  return publicProfile(profile);
}

export async function resolveCapabilityProfile(ids = ["base"]) {
  return activateCapabilityPacks(ids);
}

export function isVisualAllowedByPacks(ids, visual) {
  const key = profileKey(ids);
  const profile = profileCache.get(key);
  if (!profile) {
    throw new Error(
      `Capability profile "${key}" is not active. Load the pack or program through the framework loader first.`,
    );
  }
  return profile.mechanismSet.has(visual);
}

export function isAssetAllowedByPacks(ids, asset) {
  const key = profileKey(ids);
  const profile = profileCache.get(key);
  if (!profile) {
    throw new Error(
      `Capability profile "${key}" is not active. Load the pack or program through the framework loader first.`,
    );
  }
  return profile.assetSet.has(asset);
}

export function activeCapabilityPackIds() {
  return [...activatedPacks].sort();
}

export async function installedCapabilityPackIds() {
  const entries = await readdir(CAPABILITY_PACK_ROOT, { withFileTypes: true });
  return entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort();
}
