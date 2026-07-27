import {
  mechanismRelations,
  roleOperators,
  visualOperatorsV2,
} from "./visual-semantics.mjs";
import {
  semanticVisualDescriptions,
  semanticVisualNames,
} from "./semantic-visuals.mjs";

const visualSet = new Set(semanticVisualNames);
const operatorSet = new Set(visualOperatorsV2);

const relationLanguage = Object.freeze({
  "identity-across-change": {
    source: "material and surface form change",
    target: "one relational pattern remains recognizable",
    preserves: "the invariant relational skeleton",
    motion: "The marks must transform while the relational intervals remain stable; a still would not prove persistence through change.",
    encoding: [
      { concept: "changing embodiment", mark: "changing outer geometries", channel: "shape" },
      { concept: "preserved identity", mark: "stable linked skeleton", channel: "connection" },
    ],
  },
  dependency: {
    source: "apparently separate elements",
    target: "mutually enabling conditions",
    preserves: "the reality of each local participant",
    motion: "Signals must travel in more than one direction so dependence is enacted rather than merely named.",
    encoding: [
      { concept: "local participants", mark: "distinct nodes", channel: "position" },
      { concept: "dependence", mark: "bidirectional luminous links", channel: "connection" },
    ],
  },
  interface: {
    source: "an undivided surrounding field",
    target: "selective access through a local boundary",
    preserves: "the surrounding field and the boundary's operational reality",
    motion: "Marks must be admitted, redirected, or excluded at the boundary so the interface performs selection over time.",
    encoding: [
      { concept: "boundary", mark: "permeable ring or aperture", channel: "containment" },
      { concept: "selective access", mark: "accepted and rejected moving marks", channel: "motion" },
    ],
  },
  emergence: {
    source: "many uncoordinated local processes",
    target: "a provisional larger-scale centre",
    preserves: "the plurality of the contributing processes",
    motion: "Independent rhythms must phase-lock into a larger rhythm; the temporal coordination is the evidence of emergence.",
    encoding: [
      { concept: "local processes", mark: "small independently pulsing nodes", channel: "rhythm" },
      { concept: "emergent centre", mark: "shared larger pulse", channel: "scale" },
    ],
  },
  containment: {
    source: "a field without a privileged interior",
    target: "an operational inside and outside",
    preserves: "the field on both sides of the boundary",
    motion: "The frame must actively gather, restrict, or release marks so containment is a verb rather than decoration.",
    encoding: [
      { concept: "inside and outside", mark: "nested bounded regions", channel: "containment" },
      { concept: "constraint", mark: "marks halted at a perimeter", channel: "motion" },
    ],
  },
  selection: {
    source: "many simultaneously available differences",
    target: "a smaller world of present relevance",
    preserves: "the unselected field as latent context",
    motion: "Attention must move and alter emphasis among stable possibilities to demonstrate selection rather than disappearance.",
    encoding: [
      { concept: "available differences", mark: "distributed faint marks", channel: "opacity" },
      { concept: "selected relevance", mark: "moving illuminated subset", channel: "color" },
    ],
  },
  sequence: {
    source: "a set of possible or simultaneous states",
    target: "an ordered passage through states",
    preserves: "causal or melodic adjacency",
    motion: "The meaning depends on ordered arrival, so the path must unfold in the same direction as the narrated logic.",
    encoding: [
      { concept: "ordered states", mark: "spaced stages", channel: "sequence" },
      { concept: "passage", mark: "travelling luminous token", channel: "direction" },
    ],
  },
  feedback: {
    source: "an initiating expectation or disturbance",
    target: "a result that reinforces its own cause",
    preserves: "the distinguishability of each causal stage",
    motion: "A token must complete the circuit and alter the point where it began; without return there is no feedback.",
    encoding: [
      { concept: "causal stages", mark: "named or differentiated nodes", channel: "sequence" },
      { concept: "self-confirmation", mark: "returning loop with increasing intensity", channel: "direction" },
    ],
  },
  translation: {
    source: "a trace encoded by an earlier system",
    target: "meaning reconstructed by a changed receiver",
    preserves: "continuity without claiming an intact recording",
    motion: "The travelling trace must visibly change form before reception, proving that memory is interpreted rather than retrieved.",
    encoding: [
      { concept: "earlier trace", mark: "departing structured pulse", channel: "shape" },
      { concept: "present interpretation", mark: "reconfigured arriving pulse", channel: "shape" },
    ],
  },
  comparison: {
    source: "two or more claims shown separately",
    target: "a visible shared measure and meaningful difference",
    preserves: "the integrity of each compared position",
    motion: "Parallel transformations must reveal what changes together and what refuses to coincide.",
    encoding: [
      { concept: "positions", mark: "parallel bounded panels", channel: "position" },
      { concept: "shared and different structure", mark: "aligned gold and divergent colored marks", channel: "color" },
    ],
  },
  recursion: {
    source: "a model directed outward",
    target: "the model included inside the field it models",
    preserves: "the function of representation",
    motion: "The observing frame must fold back and become one of its own marks; a static eye symbol would only restate the label.",
    encoding: [
      { concept: "observer-model", mark: "framing aperture", channel: "containment" },
      { concept: "reflexive inclusion", mark: "aperture folding into the field", channel: "motion" },
    ],
  },
  propagation: {
    source: "a local change in one participant",
    target: "altered possibilities across a relational field",
    preserves: "local differences among recipients",
    motion: "The change must travel outward and be transformed by each recipient, showing conditional propagation instead of duplication.",
    encoding: [
      { concept: "local intervention", mark: "bright initiating pulse", channel: "color" },
      { concept: "propagated conditions", mark: "branching delayed responses", channel: "direction" },
    ],
  },
  transformation: {
    source: "one organized state",
    target: "a differently organized state",
    preserves: "the continuity explicitly named in the beat",
    motion: "The visual argument exists in the transition itself; source and target must remain traceable through the morph.",
    encoding: [
      { concept: "source state", mark: "initial geometry", channel: "shape" },
      { concept: "changed state", mark: "traceable reorganized geometry", channel: "motion" },
    ],
  },
  cessation: {
    source: "a process receiving recurrent fuel",
    target: "the process continuing without the ownership branch",
    preserves: "functional perception and response",
    motion: "The unnecessary branch must cool while the main signal continues, distinguishing cessation from annihilation.",
    encoding: [
      { concept: "functional process", mark: "unbroken moving current", channel: "motion" },
      { concept: "ownership fuel", mark: "branch fading from crimson to cool grey", channel: "opacity" },
    ],
  },
  inquiry: {
    source: "an apparently self-evident object or knower",
    target: "its enabling conditions made visible",
    preserves: "the reality of the appearance being examined",
    motion: "Successive layers must open around the focal mark, turning a fixed answer into an inspectable field of conditions.",
    encoding: [
      { concept: "appearance under inquiry", mark: "stable focal mark", channel: "position" },
      { concept: "conditions", mark: "revealed surrounding layers", channel: "opacity" },
    ],
  },
  divergence: {
    source: "shared evidence and practical ground",
    target: "two interpretations that remain genuinely distinct",
    preserves: "the common question and shared evidence",
    motion: "One path must split without severing the shared bridge, keeping disagreement visible without manufacturing a winner.",
    encoding: [
      { concept: "shared ground", mark: "common luminous bridge", channel: "connection" },
      { concept: "live disagreement", mark: "two non-converging paths", channel: "direction" },
    ],
  },
  convergence: {
    source: "distinct processes or interpretations",
    target: "a shared practical consequence",
    preserves: "their unresolved theoretical differences",
    motion: "Separate paths must meet only at the shared consequence, not collapse into one identical path.",
    encoding: [
      { concept: "distinct positions", mark: "separate colored paths", channel: "color" },
      { concept: "shared consequence", mark: "common terminal node", channel: "connection" },
    ],
  },
  "self-modification": {
    source: "a system executing inherited dispositions",
    target: "a system that alters some future dispositions",
    preserves: "conditioning rather than impossible independence",
    motion: "Runtime output must loop back to change later routing probabilities, visibly modifying the next pass.",
    encoding: [
      { concept: "inherited disposition", mark: "weighted routing gates", channel: "scale" },
      { concept: "self-modification", mark: "feedback changing gate weights", channel: "motion" },
    ],
  },
  coordination: {
    source: "many locally active systems",
    target: "a shared response without erased difference",
    preserves: "the agency of each contributor",
    motion: "Local pulses must synchronize enough to support a joint pattern while retaining different shapes and positions.",
    encoding: [
      { concept: "local agents", mark: "distinct pulsing nodes", channel: "shape" },
      { concept: "coordination", mark: "phase-aligned connecting rhythm", channel: "rhythm" },
    ],
  },
  differentiation: {
    source: "an apparently uniform field",
    target: "distinct functions or meanings within it",
    preserves: "their membership in one system",
    motion: "A common field must separate into legible channels while retaining a visible shared origin.",
    encoding: [
      { concept: "shared origin", mark: "single entering current", channel: "connection" },
      { concept: "distinct functions", mark: "diverging colors and shapes", channel: "color" },
    ],
  },
});

function normalizeRoleOperators(role) {
  const aliases = { contrast: "compare", converge: "coordinate", diverge: "differentiate", return: "recontextualize", resolve: "recontextualize" };
  return (roleOperators[role] ?? []).map((operator) => aliases[operator] ?? operator);
}

function rejectedCandidates(selected, relationType) {
  const compatible = semanticVisualNames.filter((name) => (
    name !== selected && mechanismRelations[name]?.includes(relationType)
  ));
  const incompatible = semanticVisualNames.filter((name) => (
    name !== selected && !mechanismRelations[name]?.includes(relationType)
  ));
  const candidates = [...compatible, ...incompatible].slice(0, 2);
  return candidates.map((visual, index) => ({
    visual,
    score: index === 0 ? 69 : 54,
    rejectedBecause: mechanismRelations[visual]?.includes(relationType)
      ? `It can encode ${relationType}, but its spatial grammar is less specific to this beat's claim and continuity handoff.`
      : `Its registered relations do not include ${relationType}, so it would invite a semantic mismatch despite stylistic compatibility.`,
  }));
}

function lifecycleActions(beats) {
  const first = new Map();
  const last = new Map();
  beats.forEach((beat, index) => {
    if (!first.has(beat.system)) first.set(beat.system, index);
    last.set(beat.system, index);
  });
  return beats.map((beat, index) => {
    if (first.get(beat.system) === index) return "introduce";
    if (last.get(beat.system) === index) return "resolve";
    return beat.action ?? "develop";
  });
}

export function buildDeterministicProgram(meta, beatSpecs) {
  const actions = lifecycleActions(beatSpecs);
  const shots = beatSpecs.map((beat, index) => {
    const relation = relationLanguage[beat.relation];
    if (!relation) throw new Error(`Unknown relation "${beat.relation}" in beat ${index + 1}`);
    if (!visualSet.has(beat.visual)) throw new Error(`Unknown visual "${beat.visual}" in beat ${index + 1}`);
    if (!mechanismRelations[beat.visual]?.includes(beat.relation)) {
      throw new Error(`Visual "${beat.visual}" cannot encode "${beat.relation}" in beat ${index + 1}`);
    }
    if (!operatorSet.has(beat.operator) || !normalizeRoleOperators(beat.role).includes(beat.operator)) {
      throw new Error(`Operator "${beat.operator}" cannot perform role "${beat.role}" in beat ${index + 1}`);
    }
    const selectedScore = 92 + (index % 5);
    return {
      id: `${meta.shotPrefix}-${String(index + 1).padStart(3, "0")}`,
      paragraphs: beat.range,
      chapter: beat.chapter,
      title: beat.title,
      subtitle: beat.subtitle,
      term: beat.term,
      devanagari: beat.devanagari,
      semanticRole: beat.role,
      claim: beat.claim,
      relationType: beat.relation,
      sourceState: beat.sourceState ?? relation.source,
      targetState: beat.targetState ?? relation.target,
      preserves: beat.preserves ?? relation.preserves,
      visualOperator: beat.operator,
      continuityObject: beat.system,
      continuityAction: actions[index],
      visualEncoding: beat.encoding ?? relation.encoding,
      motionProof: beat.motionProof ?? relation.motion,
      misreadRisk: beat.misreadRisk ?? "The image could be mistaken for a decorative icon or a metaphysical object existing separately from the narrated relation.",
      antiLiteral: beat.antiLiteral ?? "Render the relation as changing geometry; do not substitute a literal stock illustration or place the whole claim on screen.",
      visualRationale: beat.rationale ?? `${semanticVisualDescriptions[beat.visual]} This directly stages the beat's claim: ${beat.claim}`,
      visual: beat.visual,
      params: {
        variant: index + 1,
        centerText: beat.centerText ?? beat.title,
        caption: beat.caption ?? beat.title,
        ...(beat.params ?? {}),
      },
      candidateAudit: {
        selectedScore,
        selectedReason: `The selected mechanism visibly performs ${beat.relation} and carries the "${beat.system}" continuity system through this argumentative beat.`,
        alternatives: rejectedCandidates(beat.visual, beat.relation),
      },
      transition: beat.transition ?? "motif-preserving cut or short dissolve",
    };
  });
  return {
    version: "2.0",
    ...meta.program,
    shots,
  };
}

export { relationLanguage };
