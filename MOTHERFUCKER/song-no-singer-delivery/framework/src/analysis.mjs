import { readFile } from "node:fs/promises";

import { relationTypes, semanticRolesV2 } from "./visual-semantics.mjs";

const ID = /^[a-z][a-z0-9-]{2,63}$/;
const BEAT_ID = /^[a-z][a-z0-9-]{2,31}$/;
const ROLES = new Set(semanticRolesV2);
const RELATIONS = new Set(relationTypes);
const UNIT_TYPES = new Set(["prose", "quotation", "list", "visual-only"]);
const VISUAL_KEYS = new Set(["visual", "visualMechanism", "visualOperator", "params", "visualEncoding"]);

function string(value, path, min, max) {
  if (typeof value !== "string" || value.length < min || value.length > max) {
    throw new Error(`${path} must be a string between ${min} and ${max} characters`);
  }
}

export function assertEssayAnalysis(analysis) {
  if (!analysis || typeof analysis !== "object" || Array.isArray(analysis)) {
    throw new Error("Essay analysis must be an object");
  }
  if (analysis.version !== "1.0") throw new Error('analysis.version must equal "1.0"');
  string(analysis.essayId, "analysis.essayId", 3, 64);
  if (!ID.test(analysis.essayId)) throw new Error("analysis.essayId must use lowercase kebab-case");
  string(analysis.title, "analysis.title", 3, 120);
  string(analysis.centralClaim, "analysis.centralClaim", 20, 1000);
  if (!Number.isInteger(analysis.sourceUnitCount) || analysis.sourceUnitCount < 1) {
    throw new Error("analysis.sourceUnitCount must be a positive integer");
  }
  if (!Array.isArray(analysis.continuityCandidates) || analysis.continuityCandidates.length < 2 || analysis.continuityCandidates.length > 9) {
    throw new Error("analysis.continuityCandidates must contain between 2 and 9 systems");
  }
  if (!Array.isArray(analysis.beats) || analysis.beats.length < 1 || analysis.beats.length > 100) {
    throw new Error("analysis.beats must contain between 1 and 100 beats");
  }

  const beatIds = new Set();
  let nextSourceUnit = 1;
  for (const [index, beat] of analysis.beats.entries()) {
    const path = `analysis.beats[${index}]`;
    for (const key of Object.keys(beat ?? {})) {
      if (VISUAL_KEYS.has(key)) {
        throw new Error(`${path} contains "${key}"; Pass A must remain visual-free`);
      }
    }
    string(beat?.id, `${path}.id`, 3, 32);
    if (!BEAT_ID.test(beat.id)) throw new Error(`${path}.id must use lowercase kebab-case`);
    if (beatIds.has(beat.id)) throw new Error(`Duplicate beat id "${beat.id}"`);
    beatIds.add(beat.id);
    if (!Array.isArray(beat.sourceUnits) || beat.sourceUnits.length !== 2) {
      throw new Error(`${path}.sourceUnits must be [first, last]`);
    }
    const [first, last] = beat.sourceUnits;
    if (!Number.isInteger(first) || !Number.isInteger(last) || first !== nextSourceUnit || last < first) {
      throw new Error(`${path}.sourceUnits must cover source units contiguously; expected ${nextSourceUnit}`);
    }
    nextSourceUnit = last + 1;
    if (!Array.isArray(beat.sourceUnitTypes) || beat.sourceUnitTypes.length < 1 || beat.sourceUnitTypes.some((type) => !UNIT_TYPES.has(type))) {
      throw new Error(`${path}.sourceUnitTypes contains an unknown or missing type`);
    }
    if (!Number.isInteger(beat.spokenWordCount) || beat.spokenWordCount < 1) {
      throw new Error(`${path}.spokenWordCount must be a positive integer`);
    }
    if (!ROLES.has(beat.argumentRole)) throw new Error(`${path}.argumentRole is unknown`);
    if (!RELATIONS.has(beat.relationType)) throw new Error(`${path}.relationType is unknown`);
    string(beat.chapter, `${path}.chapter`, 2, 100);
    string(beat.claim, `${path}.claim`, 12, 360);
    string(beat.sourceState, `${path}.sourceState`, 3, 240);
    string(beat.targetState, `${path}.targetState`, 3, 240);
    string(beat.preserves, `${path}.preserves`, 3, 240);
    string(beat.whyNow, `${path}.whyNow`, 12, 400);
    string(beat.misreadRisk, `${path}.misreadRisk`, 12, 400);
    if (!Array.isArray(beat.visualExclusions) || beat.visualExclusions.length < 1 || beat.visualExclusions.length > 6) {
      throw new Error(`${path}.visualExclusions must contain between 1 and 6 exclusions`);
    }
    beat.visualExclusions.forEach((exclusion, exclusionIndex) => (
      string(exclusion, `${path}.visualExclusions[${exclusionIndex}]`, 4, 160)
    ));
  }
  if (nextSourceUnit !== analysis.sourceUnitCount + 1) {
    throw new Error(`Analysis covers ${nextSourceUnit - 1} source units, expected ${analysis.sourceUnitCount}`);
  }

  const systemIds = new Set();
  for (const [index, system] of analysis.continuityCandidates.entries()) {
    const path = `analysis.continuityCandidates[${index}]`;
    string(system?.id, `${path}.id`, 3, 64);
    if (!ID.test(system.id)) throw new Error(`${path}.id must use lowercase kebab-case`);
    if (systemIds.has(system.id)) throw new Error(`Duplicate continuity candidate "${system.id}"`);
    systemIds.add(system.id);
    string(system.meaning, `${path}.meaning`, 12, 300);
    string(system.development, `${path}.development`, 12, 400);
    string(system.resolution, `${path}.resolution`, 12, 400);
    if (!beatIds.has(system.firstBeat)) {
      throw new Error(`${path}.firstBeat must reference an existing beat id`);
    }
  }
  return analysis;
}

export async function loadEssayAnalysis(path) {
  return assertEssayAnalysis(JSON.parse(await readFile(path, "utf8")));
}
