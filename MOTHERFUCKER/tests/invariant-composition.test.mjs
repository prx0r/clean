import test from "node:test";
import assert from "node:assert/strict";

import {
  normalizedSimilarity,
  pairwiseDistanceSignature,
  transformPoints,
  expApproach,
  hermiteScalar,
} from "../src/invariant-math.mjs";
import { lobedContour } from "../src/invariant-geometry.mjs";

test("distance signature survives similarity transforms and reflection", () => {
  const source = lobedContour({ radius: 60, lobes: 5, harmonic: 0.22, samples: 96 });
  const transformed = transformPoints(source, {
    tx: 280,
    ty: -90,
    scale: 1.74,
    rotation: 1.13,
    reflectX: true,
  });
  const left = pairwiseDistanceSignature(source, 16);
  const right = pairwiseDistanceSignature(transformed, 16);
  assert.ok(normalizedSimilarity(left, right, 0.05) > 0.999);
});

test("exponential memory integration is frame-rate stable", () => {
  let fine = 0;
  for (let index = 0; index < 240; index += 1) fine = expApproach(fine, 1, 1 / 240, 0.5);
  let coarse = 0;
  for (let index = 0; index < 24; index += 1) coarse = expApproach(coarse, 1, 1 / 24, 0.5);
  assert.ok(Math.abs(fine - coarse) < 1e-10);
});

test("trajectory returns value, velocity and acceleration", () => {
  const state = hermiteScalar([0, 1, 0.5, 0.8], 0.5);
  assert.ok(Number.isFinite(state.value));
  assert.ok(Number.isFinite(state.velocity));
  assert.ok(Number.isFinite(state.acceleration));
});
