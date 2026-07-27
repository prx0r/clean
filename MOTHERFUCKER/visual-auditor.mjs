import { semanticVisualNames } from "./semantic-visuals.mjs";
import {
  compatibilityExplanation,
  continuityActions,
  encodingChannels,
  isMechanismCompatible,
  isRoleOperatorCompatible,
  relationTypes,
  semanticRolesV2,
  visualOperatorsV2,
} from "./visual-semantics.mjs";

const VISUALS = new Set(semanticVisualNames);
const RELATIONS = new Set(relationTypes);
const ROLES = new Set(semanticRolesV2);
const OPERATORS = new Set(visualOperatorsV2);
const CONTINUITY_ACTIONS = new Set(continuityActions);
const CHANNELS = new Set(encodingChannels);

function textField(value, path, minimum, maximum, errors) {
  if (typeof value !== "string" || value.length < minimum || value.length > maximum) {
    errors.push(`${path} must be a string between ${minimum} and ${maximum} characters`);
  }
}

function longestRun(values) {
  let longest = 0;
  let current = 0;
  let previous;
  for (const value of values) {
    current = value === previous ? current + 1 : 1;
    previous = value;
    longest = Math.max(longest, current);
  }
  return longest;
}

function visualSignature(shot) {
  return JSON.stringify({
    visual: shot.visual,
    params: shot.params ?? {},
    operator: shot.visualOperator,
  });
}

export function auditVisualProgram(program) {
  const errors = [];
  const warnings = [];
  if (program?.version !== "2.0") {
    return {
      valid: true,
      version: program?.version,
      errors,
      warnings: ["Deterministic semantic audit applies only to essay visual-program version 2.0."],
      metrics: {},
    };
  }

  const systems = new Map();
  if (!Array.isArray(program.continuitySystems) || program.continuitySystems.length < 2) {
    errors.push("program.continuitySystems must contain at least two systems");
  } else {
    for (const [index, system] of program.continuitySystems.entries()) {
      if (!system?.id) {
        errors.push(`program.continuitySystems[${index}].id is required`);
        continue;
      }
      if (systems.has(system.id)) errors.push(`Duplicate continuity system "${system.id}"`);
      systems.set(system.id, system);
    }
  }

  const seenContinuity = new Set();
  const mechanismCounts = new Map();
  const relationCounts = new Map();
  const chapterMechanisms = new Map();
  const signatures = new Map();

  for (const [index, shot] of (program.shots ?? []).entries()) {
    const path = `program.shots[${index}]`;
    textField(shot.claim, `${path}.claim`, 12, 360, errors);
    textField(shot.sourceState, `${path}.sourceState`, 3, 240, errors);
    textField(shot.targetState, `${path}.targetState`, 3, 240, errors);
    textField(shot.preserves, `${path}.preserves`, 3, 240, errors);
    textField(shot.motionProof, `${path}.motionProof`, 20, 600, errors);
    textField(shot.misreadRisk, `${path}.misreadRisk`, 12, 400, errors);
    textField(shot.antiLiteral, `${path}.antiLiteral`, 12, 400, errors);

    if (!ROLES.has(shot.semanticRole)) {
      errors.push(`${path}.semanticRole must be one of: ${semanticRolesV2.join(", ")}`);
    }
    if (!OPERATORS.has(shot.visualOperator)) {
      errors.push(`${path}.visualOperator must be one of: ${visualOperatorsV2.join(", ")}`);
    } else if (ROLES.has(shot.semanticRole) && !isRoleOperatorCompatible(shot.semanticRole, shot.visualOperator)) {
      errors.push(
        `${path} uses operator "${shot.visualOperator}" for semantic role "${shot.semanticRole}", ` +
        "which does not perform that argumentative function.",
      );
    }
    if (!RELATIONS.has(shot.relationType)) {
      errors.push(`${path}.relationType must be one of: ${relationTypes.join(", ")}`);
    }
    if (!VISUALS.has(shot.visual)) {
      errors.push(`${path}.visual is unknown`);
    } else if (RELATIONS.has(shot.relationType) && !isMechanismCompatible(shot.visual, shot.relationType)) {
      errors.push(`${path}: ${compatibilityExplanation(shot.visual, shot.relationType)}`);
    }

    if (!systems.has(shot.continuityObject)) {
      errors.push(`${path}.continuityObject must reference a declared continuity system id`);
    }
    if (!CONTINUITY_ACTIONS.has(shot.continuityAction)) {
      errors.push(`${path}.continuityAction must be one of: ${continuityActions.join(", ")}`);
    } else if (shot.continuityAction === "introduce") {
      if (seenContinuity.has(shot.continuityObject)) {
        errors.push(`${path} re-introduces continuity system "${shot.continuityObject}"`);
      }
      seenContinuity.add(shot.continuityObject);
    } else if (!seenContinuity.has(shot.continuityObject)) {
      errors.push(
        `${path} uses continuity system "${shot.continuityObject}" before an "introduce" action`,
      );
    }

    if (!Array.isArray(shot.visualEncoding) || shot.visualEncoding.length < 2 || shot.visualEncoding.length > 8) {
      errors.push(`${path}.visualEncoding must contain between 2 and 8 concept-to-mark mappings`);
    } else {
      const concepts = new Set();
      for (const [encodingIndex, encoding] of shot.visualEncoding.entries()) {
        const encodingPath = `${path}.visualEncoding[${encodingIndex}]`;
        textField(encoding?.concept, `${encodingPath}.concept`, 2, 100, errors);
        textField(encoding?.mark, `${encodingPath}.mark`, 2, 140, errors);
        if (!CHANNELS.has(encoding?.channel)) {
          errors.push(`${encodingPath}.channel must be one of: ${encodingChannels.join(", ")}`);
        }
        if (concepts.has(encoding?.concept)) {
          warnings.push(`${encodingPath} duplicates concept "${encoding?.concept}"`);
        }
        concepts.add(encoding?.concept);
      }
    }

    const audit = shot.candidateAudit;
    if (!audit || typeof audit !== "object") {
      errors.push(`${path}.candidateAudit is required`);
    } else {
      if (typeof audit.selectedScore !== "number" || audit.selectedScore < 0 || audit.selectedScore > 100) {
        errors.push(`${path}.candidateAudit.selectedScore must be between 0 and 100`);
      }
      textField(audit.selectedReason, `${path}.candidateAudit.selectedReason`, 20, 500, errors);
      if (!Array.isArray(audit.alternatives) || audit.alternatives.length < 2 || audit.alternatives.length > 4) {
        errors.push(`${path}.candidateAudit.alternatives must contain between 2 and 4 rejected candidates`);
      } else {
        const candidates = new Set([shot.visual]);
        for (const [alternativeIndex, alternative] of audit.alternatives.entries()) {
          const alternativePath = `${path}.candidateAudit.alternatives[${alternativeIndex}]`;
          if (!VISUALS.has(alternative?.visual)) {
            errors.push(`${alternativePath}.visual is unknown`);
          }
          if (candidates.has(alternative?.visual)) {
            errors.push(`${alternativePath}.visual duplicates a candidate`);
          }
          candidates.add(alternative?.visual);
          if (typeof alternative?.score !== "number" || alternative.score < 0 || alternative.score > 100) {
            errors.push(`${alternativePath}.score must be between 0 and 100`);
          }
          textField(alternative?.rejectedBecause, `${alternativePath}.rejectedBecause`, 12, 300, errors);
          if (
            typeof audit.selectedScore === "number" &&
            typeof alternative?.score === "number" &&
            alternative.score >= audit.selectedScore
          ) {
            errors.push(`${alternativePath}.score must be lower than selectedScore`);
          }
        }
      }
    }

    mechanismCounts.set(shot.visual, (mechanismCounts.get(shot.visual) ?? 0) + 1);
    relationCounts.set(shot.relationType, (relationCounts.get(shot.relationType) ?? 0) + 1);
    const chapterSet = chapterMechanisms.get(shot.chapter) ?? new Set();
    chapterSet.add(shot.visual);
    chapterMechanisms.set(shot.chapter, chapterSet);
    const signature = visualSignature(shot);
    signatures.set(signature, (signatures.get(signature) ?? 0) + 1);
  }

  for (const [chapter, visuals] of chapterMechanisms.entries()) {
    const shotCount = program.shots.filter((shot) => shot.chapter === chapter).length;
    if (shotCount >= 4 && visuals.size < 2) {
      warnings.push(`Chapter "${chapter}" has ${shotCount} shots but only one visual mechanism`);
    }
  }

  const duplicateSignatures = [...signatures.values()].filter((count) => count > 1);
  if (duplicateSignatures.length > 0) {
    warnings.push(
      `${duplicateSignatures.length} visual signature(s) repeat exactly; verify that repetition carries continuity rather than convenience.`,
    );
  }
  const maxRun = longestRun((program.shots ?? []).map((shot) => shot.visual));
  if (maxRun > 3) {
    warnings.push(`The same visual mechanism runs for ${maxRun} consecutive shots; use parameter development or a visual handoff.`);
  }
  const shotCount = program.shots?.length ?? 0;
  const uniqueMechanisms = mechanismCounts.size;
  const diversityRatio = shotCount ? uniqueMechanisms / shotCount : 0;
  if (shotCount >= 20 && uniqueMechanisms < 8) {
    warnings.push(`Only ${uniqueMechanisms} mechanisms serve ${shotCount} shots; the program may be visually under-specified.`);
  }
  const unresolved = [...seenContinuity].filter((id) => (
    !program.shots.some((shot) => shot.continuityObject === id && shot.continuityAction === "resolve")
  ));
  if (unresolved.length > 0) {
    warnings.push(`Continuity systems without a resolve action: ${unresolved.join(", ")}`);
  }

  return {
    valid: errors.length === 0,
    version: program.version,
    errors,
    warnings,
    metrics: {
      shots: shotCount,
      uniqueMechanisms,
      diversityRatio,
      relationTypesUsed: relationCounts.size,
      continuitySystems: systems.size,
      maxConsecutiveMechanismRun: maxRun,
      exactDuplicateVisualSignatures: duplicateSignatures.length,
    },
  };
}

export function assertVisualProgram(program) {
  const audit = auditVisualProgram(program);
  if (!audit.valid) {
    throw new Error(`Visual correspondence audit failed:\n${audit.errors.join("\n")}`);
  }
  return audit;
}
