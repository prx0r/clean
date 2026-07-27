import test from "node:test";
import assert from "node:assert/strict";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { activateCapabilityPacks } from "../extensionpacks/capability-packs.mjs";
import { getTheme } from "../theme.mjs";
import { hasSemanticVisual } from "../semantic-visuals.mjs";
import { getMechanismRelations } from "../visual-semantics.mjs";
import { listVisualAssetNames } from "../visual-assets.mjs";
import { loadCapabilityScenePack } from "../src/load-capability-scene-pack.mjs";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));

test("invariant composition pack activates end-to-end", async () => {
  const profile = await activateCapabilityPacks(["invariant-composition"]);
  assert.equal(profile.defaultTheme, "kineticIvory");
  assert.equal(getTheme("kineticIvory").name, "kineticIvory");
  assert.ok(hasSemanticVisual("transformation-invariance"));
  assert.ok(getMechanismRelations("causal-memory").includes("feedback"));
  assert.ok(listVisualAssetNames().includes("continuity-seed"));
});

test("demo scene pack validates after capability activation", async () => {
  const pack = await loadCapabilityScenePack(join(ROOT, "packs/invariant-composition-demo.json"));
  assert.equal(pack.scenes.length, 12);
});
