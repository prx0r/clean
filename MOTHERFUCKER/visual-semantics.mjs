export const relationTypes = Object.freeze([
  "identity-across-change",
  "dependency",
  "interface",
  "emergence",
  "containment",
  "selection",
  "sequence",
  "feedback",
  "translation",
  "comparison",
  "recursion",
  "propagation",
  "transformation",
  "cessation",
  "inquiry",
  "divergence",
  "convergence",
  "self-modification",
  "coordination",
  "differentiation",
]);

export const semanticRolesV2 = Object.freeze([
  "hook",
  "question",
  "thesis",
  "definition",
  "mechanism",
  "analogy",
  "example",
  "consequence",
  "objection",
  "reversal",
  "comparison",
  "practice",
  "recognition",
  "synthesis",
  "open-question",
  "coda",
]);

export const visualOperatorsV2 = Object.freeze([
  "reveal",
  "contract",
  "frame",
  "filter",
  "sequence",
  "select",
  "reach",
  "enclose",
  "construct",
  "unfold",
  "invert",
  "differentiate",
  "recontextualize",
  "open",
  "coordinate",
  "propagate",
  "translate",
  "loop",
  "compare",
  "recurse",
  "cool",
  "tune",
  "emerge",
  "transform",
]);

export const continuityActions = Object.freeze([
  "introduce",
  "develop",
  "contrast",
  "invert",
  "return",
  "resolve",
]);

export const encodingChannels = Object.freeze([
  "position",
  "containment",
  "connection",
  "direction",
  "sequence",
  "repetition",
  "shape",
  "scale",
  "color",
  "opacity",
  "rhythm",
  "motion",
  "text",
]);

const dynamicMechanismRelations = new Map();

export const mechanismRelations = Object.freeze({
  "constraint-field": ["containment", "transformation", "emergence"],
  "point-of-view": ["interface", "selection", "containment"],
  "five-lenses": ["interface", "selection", "differentiation"],
  "local-power": ["selection", "emergence", "differentiation"],
  "melody-time": ["sequence", "identity-across-change", "transformation"],
  "attention-beam": ["selection", "interface", "containment"],
  "desire-orbit": ["feedback", "selection", "transformation"],
  "smallness-cage": ["containment", "selection", "transformation"],
  "powered-prison": ["feedback", "containment", "self-modification"],
  "practice-folds": ["recursion", "inquiry", "transformation"],
  upsurge: ["transformation", "emergence", "containment"],
  "wave-ocean": ["identity-across-change", "containment", "transformation"],
  "textures-display": ["differentiation", "emergence", "comparison"],
  "limitation-reversal": ["comparison", "transformation", "containment"],
  "opening-fist": ["cessation", "transformation", "containment"],
  "pattern-ensemble": ["identity-across-change", "comparison", "transformation"],
  "dependency-network": ["dependency", "coordination", "propagation"],
  "umwelt-windows": ["interface", "selection", "comparison"],
  "multiscale-agent": ["emergence", "coordination", "containment"],
  "boundary-gates": ["interface", "selection", "containment"],
  "memory-relay": ["translation", "sequence", "transformation"],
  "morphing-invariant": ["identity-across-change", "transformation", "comparison"],
  "reciprocal-reeds": ["dependency", "feedback", "coordination"],
  "causal-vortex": ["feedback", "sequence", "self-modification"],
  "cooling-chain": ["cessation", "sequence", "transformation"],
  "dialectic-bridge": ["divergence", "comparison", "convergence"],
  "tuning-network": ["coordination", "propagation", "dependency"],
  "source-compile-runtime": ["translation", "sequence", "self-modification"],
  "recursive-observer": ["recursion", "inquiry", "containment"],
  "open-question": ["divergence", "inquiry", "comparison"],
  "relational-birth": ["emergence", "dependency", "propagation"],
});

export const roleOperators = Object.freeze({
  hook: ["reveal", "frame", "contrast", "emerge"],
  question: ["reveal", "frame", "compare", "recurse"],
  thesis: ["reveal", "construct", "recontextualize", "emerge"],
  definition: ["filter", "frame", "differentiate", "reveal"],
  mechanism: ["sequence", "construct", "coordinate", "translate", "loop", "emerge"],
  analogy: ["compare", "transform", "recontextualize", "sequence"],
  example: ["reveal", "select", "compare", "differentiate"],
  consequence: ["sequence", "propagate", "construct", "transform"],
  objection: ["enclose", "construct", "compare", "frame"],
  reversal: ["invert", "recontextualize", "open", "cool", "transform"],
  comparison: ["compare", "contrast", "differentiate", "converge"],
  practice: ["unfold", "recurse", "select", "cool", "translate"],
  recognition: ["invert", "recontextualize", "open", "recurse"],
  synthesis: ["coordinate", "converge", "recontextualize", "propagate"],
  "open-question": ["compare", "diverge", "reveal", "recurse"],
  coda: ["return", "resolve", "open", "recontextualize"],
});

const aliases = Object.freeze({
  contrast: "compare",
  converge: "coordinate",
  diverge: "differentiate",
  return: "recontextualize",
  resolve: "recontextualize",
});

export function registerMechanismRelations(mechanismId, relations) {
  if (!mechanismId || !Array.isArray(relations) || relations.length === 0) {
    throw new Error("registerMechanismRelations requires mechanism id and relations");
  }
  const invalid = relations.filter((relation) => !relationTypes.includes(relation));
  if (invalid.length) throw new Error(`Unknown relation types: ${invalid.join(", ")}`);
  const existing = dynamicMechanismRelations.get(mechanismId);
  if (existing) {
    if (JSON.stringify(existing) === JSON.stringify(relations)) return;
    throw new Error(`Relations for "${mechanismId}" are already registered`);
  }
  dynamicMechanismRelations.set(mechanismId, Object.freeze([...relations]));
}

export function getMechanismRelations(visual) {
  return mechanismRelations[visual] ?? dynamicMechanismRelations.get(visual) ?? [];
}

export function isMechanismCompatible(visual, relationType) {
  return getMechanismRelations(visual).includes(relationType);
}

export function isRoleOperatorCompatible(role, operator) {
  const normalized = aliases[operator] ?? operator;
  return (roleOperators[role] ?? []).some((candidate) => (
    (aliases[candidate] ?? candidate) === normalized
  ));
}

export function compatibilityExplanation(visual, relationType) {
  const supported = getMechanismRelations(visual);
  return `"${visual}" encodes ${supported.join(", ") || "no registered relations"}; ` +
    `it cannot be used for "${relationType}" without an explicit custom composition.`;
}
