import { clamp, smoothstep } from "./math.mjs";

const assets = new Map();
const metadata = new Map();
const ASSET_ID = /^[a-z][a-z0-9-]{2,63}$/u;

export function registerVisualAsset(definition) {
  const {
    name,
    renderer,
    description,
    category = "overlay",
    epistemicMode = "structural",
    semanticTags = [],
  } = definition ?? {};
  if (!ASSET_ID.test(name ?? "")) {
    throw new Error("Visual asset name must use lowercase kebab-case");
  }
  if (typeof renderer !== "function") {
    throw new Error(`Visual asset "${name}" must provide a renderer function`);
  }
  if (typeof description !== "string" || description.length < 20) {
    throw new Error(`Visual asset "${name}" must provide a useful description`);
  }
  const existing = assets.get(name);
  if (existing) {
    if (existing === renderer && metadata.get(name)?.description === description) return;
    throw new Error(`Visual asset "${name}" is already registered`);
  }
  assets.set(name, renderer);
  metadata.set(name, Object.freeze({
    name,
    description,
    category,
    epistemicMode,
    semanticTags: Object.freeze([...semanticTags]),
  }));
}

export function hasVisualAsset(name) {
  return assets.has(name);
}

export function listVisualAssetNames() {
  return [...assets.keys()].sort();
}

export function listVisualAssets() {
  return listVisualAssetNames().map((name) => metadata.get(name));
}

export function renderVisualAsset(ctx, t, name, params, env) {
  const renderer = assets.get(name);
  if (!renderer) {
    throw new Error(
      `Unknown visual asset "${name}". Available assets: ${listVisualAssetNames().join(", ")}`,
    );
  }
  renderer(ctx, clamp(t), params ?? {}, env);
}

export function renderAssetLayers(ctx, t, layers, env) {
  for (const layer of layers ?? []) {
    const start = layer.start ?? 0;
    const revealEnd = layer.revealEnd ?? Math.min(1, start + 0.18);
    const exitStart = layer.exitStart ?? 1;
    const alpha = (layer.opacity ?? 1)
      * smoothstep(start, revealEnd, t)
      * (1 - smoothstep(exitStart, 1, t));
    if (alpha <= 0.0001) continue;
    const localT = clamp((t - start) / Math.max(0.0001, 1 - start));
    ctx.save();
    ctx.globalAlpha *= alpha;
    if (layer.blendMode) ctx.globalCompositeOperation = layer.blendMode;
    renderVisualAsset(ctx, localT, layer.asset, layer.params, {
      ...env,
      alpha,
      layer,
    });
    ctx.restore();
  }
}

