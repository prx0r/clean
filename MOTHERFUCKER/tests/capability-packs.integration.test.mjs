import test from "node:test";
import assert from "node:assert/strict";

import {
  activateCapabilityPacks,
  isVisualAllowedByPacks,
} from "../extensionpacks/capability-packs.mjs";
import { getTheme } from "../theme.mjs";
import { hasSemanticVisual } from "../semantic-visuals.mjs";
import { getMechanismRelations } from "../visual-semantics.mjs";

test("base pack activates", async () => {
  const profile = await activateCapabilityPacks(["base"]);
  assert.equal(profile.inheritanceOrder[0], "base");
  assert.ok(isVisualAllowedByPacks(["base"], "constraint-field"));
});

test("dynamic pack integrates theme, mechanism, and relations", async () => {
  const profile = await activateCapabilityPacks(["neurocognition"]);
  assert.equal(profile.defaultTheme, "neuralIvory");
  assert.equal(getTheme("neuralIvory").name, "neuralIvory");
  assert.ok(hasSemanticVisual("predictive-loop"));
  assert.ok(getMechanismRelations("predictive-loop").includes("feedback"));
});
