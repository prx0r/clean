import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { semanticVisualNames } from "./semantic-visuals.mjs";
import { assertPack } from "./schema.mjs";
import { assertVisualProgram, auditVisualProgram } from "./visual-auditor.mjs";

const PROGRAM_ID = /^[a-z][a-z0-9-]{2,63}$/;
const SHOT_ID = /^[a-z][a-z0-9-]{2,31}$/;
const VISUALS = new Set(semanticVisualNames);

function words(text) {
  return text.match(/[\p{L}\p{N}]+(?:[’'-][\p{L}\p{N}]+)*/gu) ?? [];
}

function cleanNarration(markdown) {
  return markdown
    .replace(/^>\s?/gm, "")
    .replace(/[*_`]/g, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

export function extractEssayParagraphs(markdown) {
  return extractEssayUnits(markdown).map((unit) => (
    unit.narrationText || unit.visualText
  ));
}

export function extractEssayUnits(markdown) {
  const units = markdown
    .split(/\n\s*\n/u)
    .map((paragraph) => paragraph.trim())
    .filter((paragraph) => (
      paragraph &&
      paragraph !== "---" &&
      !/^#{1,6}\s/u.test(paragraph)
    ))
    .map((sourceText, index) => {
      const code = /^```/u.test(sourceText);
      const quote = /^>/u.test(sourceText);
      const list = /^(?:[-*+]\s)/mu.test(sourceText);
      const visualText = code
        ? sourceText.replace(/^```[^\n]*\n?/u, "").replace(/\n?```$/u, "").trim()
        : cleanNarration(sourceText);
      return {
        index: index + 1,
        type: code ? "visual-only" : (quote ? "quotation" : (list ? "list" : "prose")),
        sourceText,
        visualText,
        narrationText: code ? "" : cleanNarration(sourceText),
        wordCount: code ? 0 : words(cleanNarration(sourceText)).length,
      };
    });
  if (units.length === 0) throw new Error("The source essay contains no content units");
  return units;
}

function requiredString(value, path, minimum = 1, maximum = 500) {
  if (typeof value !== "string" || value.length < minimum || value.length > maximum) {
    throw new Error(`${path} must be a string between ${minimum} and ${maximum} characters`);
  }
}

function requiredNumber(value, path, minimum, maximum, integer = false) {
  if (typeof value !== "number" || !Number.isFinite(value) || value < minimum || value > maximum) {
    throw new Error(`${path} must be a number between ${minimum} and ${maximum}`);
  }
  if (integer && !Number.isInteger(value)) throw new Error(`${path} must be an integer`);
}

export function assertEssayProgram(program) {
  if (!program || typeof program !== "object" || Array.isArray(program)) {
    throw new Error("Essay visual program must be a JSON object");
  }
  if (program.version !== "1.0" && program.version !== "2.0") {
    throw new Error('program.version must equal "1.0" or "2.0"');
  }
  requiredString(program.id, "program.id", 3, 64);
  if (!PROGRAM_ID.test(program.id)) throw new Error("program.id must use lowercase kebab-case");
  requiredString(program.title, "program.title", 3, 120);
  requiredString(program.sourceEssay, "program.sourceEssay", 3, 300);
  requiredString(program.visualThesis, "program.visualThesis", 20, 1000);
  if (!program.timing || typeof program.timing !== "object") throw new Error("program.timing is required");
  requiredNumber(program.timing.wordsPerMinute, "program.timing.wordsPerMinute", 80, 220);
  requiredNumber(program.timing.tailPadding, "program.timing.tailPadding", 0, 4);
  if (!program.render || typeof program.render !== "object") throw new Error("program.render is required");
  requiredNumber(program.render.width, "program.render.width", 640, 7680, true);
  requiredNumber(program.render.height, "program.render.height", 360, 4320, true);
  requiredNumber(program.render.fps, "program.render.fps", 1, 60, true);
  if (!Array.isArray(program.shots) || program.shots.length < 1 || program.shots.length > 100) {
    throw new Error("program.shots must contain between 1 and 100 shots");
  }
  const ids = new Set();
  for (const [index, shot] of program.shots.entries()) {
    const path = `program.shots[${index}]`;
    requiredString(shot.id, `${path}.id`, 3, 32);
    if (!SHOT_ID.test(shot.id)) throw new Error(`${path}.id must use lowercase kebab-case`);
    if (ids.has(shot.id)) throw new Error(`Duplicate shot id "${shot.id}"`);
    ids.add(shot.id);
    requiredString(shot.chapter, `${path}.chapter`, 2, 100);
    requiredString(shot.title, `${path}.title`, 2, 80);
    requiredString(shot.subtitle, `${path}.subtitle`, 2, 140);
    requiredString(shot.term, `${path}.term`, 1, 50);
    requiredString(shot.devanagari, `${path}.devanagari`, 1, 50);
    if (!/[\u0900-\u097f]/u.test(shot.devanagari)) {
      throw new Error(`${path}.devanagari must contain Devanāgarī text`);
    }
    if (!Array.isArray(shot.paragraphs) || shot.paragraphs.length !== 2) {
      throw new Error(`${path}.paragraphs must be [first, last] using 1-based inclusive indexes`);
    }
    requiredNumber(shot.paragraphs[0], `${path}.paragraphs[0]`, 1, 10000, true);
    requiredNumber(shot.paragraphs[1], `${path}.paragraphs[1]`, shot.paragraphs[0], 10000, true);
    requiredString(shot.semanticRole, `${path}.semanticRole`, 2, 80);
    requiredString(shot.visualOperator, `${path}.visualOperator`, 2, 80);
    requiredString(shot.continuityObject, `${path}.continuityObject`, 2, 100);
    requiredString(shot.visualRationale, `${path}.visualRationale`, 12, 500);
    if (!VISUALS.has(shot.visual)) {
      throw new Error(`${path}.visual must be one of: ${semanticVisualNames.join(", ")}`);
    }
    if (shot.duration !== undefined) requiredNumber(shot.duration, `${path}.duration`, 1, 30);
  }
  if (program.version === "2.0") assertVisualProgram(program);
  return program;
}

function durationFor(shot, passage, program, timingManifest) {
  const exact = timingManifest?.shots?.find((candidate) => candidate.id === shot.id)?.duration;
  const unquantized = exact ?? shot.duration ?? (
    (words(passage).length * 60) / program.timing.wordsPerMinute +
    program.timing.tailPadding
  );
  const frameDuration = 1 / program.render.fps;
  const duration = Math.ceil(unquantized / frameDuration) * frameDuration;
  if (duration > 30) {
    throw new Error(
      `Shot "${shot.id}" is ${duration.toFixed(3)}s. Split its paragraph range so every shot is at most 30s.`,
    );
  }
  return duration;
}

function assertTimingManifest(program, timingManifest) {
  if (!timingManifest) return;
  if (!Array.isArray(timingManifest.shots)) {
    throw new Error("Exact timing manifest must contain a shots array");
  }
  const expected = new Set(program.shots.map((shot) => shot.id));
  const seen = new Set();
  for (const [index, timing] of timingManifest.shots.entries()) {
    if (!timing || typeof timing !== "object") {
      throw new Error(`timingManifest.shots[${index}] must be an object`);
    }
    requiredString(timing.id, `timingManifest.shots[${index}].id`, 3, 32);
    if (!expected.has(timing.id)) throw new Error(`Exact timing contains unknown shot "${timing.id}"`);
    if (seen.has(timing.id)) throw new Error(`Exact timing duplicates shot "${timing.id}"`);
    seen.add(timing.id);
    requiredNumber(timing.duration, `Exact duration for "${timing.id}"`, 1, 30);
  }
  const missing = [...expected].filter((id) => !seen.has(id));
  if (missing.length > 0) {
    throw new Error(`Exact timing manifest is missing ${missing.length} shot(s): ${missing.join(", ")}`);
  }
}

export function compileEssayProgram(program, markdown, timingManifest = undefined) {
  assertEssayProgram(program);
  assertTimingManifest(program, timingManifest);
  const units = extractEssayUnits(markdown);
  let expectedParagraph = 1;
  let frameCursor = 0;
  const scenes = [];
  const storyboardShots = [];
  const narration = [];

  for (const shot of program.shots) {
    const [first, last] = shot.paragraphs;
    if (first !== expectedParagraph) {
      throw new Error(
        `Shot "${shot.id}" begins at paragraph ${first}; expected ${expectedParagraph}. ` +
        "Paragraph ranges must cover the essay exactly once and in order.",
      );
    }
    if (last > units.length) {
      throw new Error(`Shot "${shot.id}" ends at source unit ${last}, but the essay has ${units.length}`);
    }
    const sourceUnits = units.slice(first - 1, last);
    const passage = shot.spokenOverride ?? sourceUnits
      .map((unit) => unit.narrationText)
      .filter(Boolean)
      .join(" ");
    if (!passage) {
      throw new Error(
        `Shot "${shot.id}" contains only visual-only source units; group it with spoken prose or provide spokenOverride.`,
      );
    }
    const duration = durationFor(shot, passage, program, timingManifest);
    const frameCount = Math.round(duration * program.render.fps);
    const start = frameCursor / program.render.fps;
    frameCursor += frameCount;
    const end = frameCursor / program.render.fps;
    expectedParagraph = last + 1;
    narration.push(passage);
    scenes.push({
      id: shot.id,
      title: shot.title,
      subtitle: shot.subtitle,
      term: shot.term,
      devanagari: shot.devanagari,
      motif: "semantic-essay",
      duration: frameCount / program.render.fps,
      theme: shot.theme,
      seed: shot.seed,
      palette: shot.palette,
      params: {
        ...(shot.params ?? {}),
        visual: shot.visual,
      },
    });
    storyboardShots.push({
      id: shot.id,
      start,
      end,
      duration: end - start,
      frameStart: Math.round(start * program.render.fps),
      frameEnd: frameCursor,
      paragraphRange: [first, last],
      sourceUnitTypes: sourceUnits.map((unit) => unit.type),
      visualOnlySource: sourceUnits
        .filter((unit) => unit.type === "visual-only")
        .map((unit) => unit.visualText),
      spokenPassage: passage,
      chapter: shot.chapter,
      semanticRole: shot.semanticRole,
      claim: shot.claim,
      relationType: shot.relationType,
      sourceState: shot.sourceState,
      targetState: shot.targetState,
      preserves: shot.preserves,
      visualOperator: shot.visualOperator,
      visualMechanism: shot.visual,
      continuityObject: shot.continuityObject,
      continuityAction: shot.continuityAction,
      visualEncoding: shot.visualEncoding,
      motionProof: shot.motionProof,
      misreadRisk: shot.misreadRisk,
      antiLiteral: shot.antiLiteral,
      candidateAudit: shot.candidateAudit,
      visualRationale: shot.visualRationale,
      transition: shot.transition ?? "motif-preserving cut or short dissolve",
    });
  }

  if (expectedParagraph !== units.length + 1) {
    throw new Error(
      `Visual program ends at source unit ${expectedParagraph - 1}, but the essay has ${units.length}`,
    );
  }

  const pack = assertPack({
    version: "1.0",
    id: program.id,
    title: program.title,
    description: program.visualThesis.slice(0, 500),
    theme: program.theme ?? "ivoryManuscript",
    seed: program.seed ?? 1,
    render: {
      ...program.render,
      sceneDuration: program.render.sceneDuration ?? 8,
    },
    scenes,
  });

  return {
    pack,
    storyboard: {
      version: "1.0",
      filmId: program.id,
      title: program.title,
      sourceEssay: program.sourceEssay,
      timingMethod: timingManifest
        ? "Exact per-shot durations supplied by a narration timing manifest and quantized to video frames."
        : `Draft narration estimate at ${program.timing.wordsPerMinute} words per minute plus ` +
          `${program.timing.tailPadding}s per shot, quantized to ${program.render.fps} fps.`,
      visualThesis: program.visualThesis,
      continuitySystems: program.continuitySystems ?? [],
      captionPolicy: program.captionPolicy ?? "Narration carries prose; visuals carry relations and transformation.",
      correspondenceAudit: auditVisualProgram(program),
      shotCount: storyboardShots.length,
      sourceUnitCount: units.length,
      paragraphCount: units.length,
      runtimeSeconds: frameCursor / program.render.fps,
      shots: storyboardShots,
    },
    narration: `${narration.join("\n\n")}\n`,
  };
}

export async function loadEssayProgram(programPath, timingPath = undefined) {
  const absoluteProgram = programPath instanceof URL
    ? fileURLToPath(programPath)
    : resolve(programPath);
  const program = JSON.parse(await readFile(absoluteProgram, "utf8"));
  assertEssayProgram(program);
  const markdown = await readFile(resolve(dirname(absoluteProgram), program.sourceEssay), "utf8");
  const timingManifest = timingPath
    ? JSON.parse(await readFile(timingPath instanceof URL ? fileURLToPath(timingPath) : resolve(timingPath), "utf8"))
    : undefined;
  return compileEssayProgram(program, markdown, timingManifest);
}
