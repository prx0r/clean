import {
  relationTypes,
  semanticRolesV2,
  visualOperatorsV2,
  continuityActions,
  encodingChannels,
  mechanismRelations,
  roleOperators,
  isMechanismCompatible,
  isRoleOperatorCompatible,
  compatibilityExplanation,
} from "../visual-semantics.mjs";

const dynamicRelations = new Map();

export {
  relationTypes,
  semanticRolesV2,
  visualOperatorsV2,
  continuityActions,
  encodingChannels,
  mechanismRelations,
  roleOperators,
  isMechanismCompatible,
  isRoleOperatorCompatible,
  compatibilityExplanation,
};

export function registerMechanismRelations(mechanismId, relations) {
  if (!mechanismId || !Array.isArray(relations) || relations.length === 0) {
    throw new Error(`registerMechanismRelations requires mechanismId and non-empty relations array`);
  }
  if (dynamicRelations.has(mechanismId)) {
    throw new Error(`Relations for mechanism "${mechanismId}" are already registered`);
  }
  for (const rel of relations) {
    if (!relationTypes.includes(rel)) {
      console.warn(`registerMechanismRelations: "${rel}" is not a standard relation type`);
    }
  }
  dynamicRelations.set(mechanismId, Object.freeze([...relations]));
}

export function getMechanismRelations(mechanismId) {
  return dynamicRelations.get(mechanismId);
}

export function getAllDynamicRelations() {
  return Object.freeze([...dynamicRelations.entries()]);
}
