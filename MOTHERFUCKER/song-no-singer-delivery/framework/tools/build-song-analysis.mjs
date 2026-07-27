#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { extractEssayUnits } from "../src/essay-program.mjs";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const programPath = resolve(ROOT, "programs/song-no-singer-visual-program.json");
const essayPath = resolve(ROOT, "essays/the-song-with-no-singer.md");
const outputPath = resolve(ROOT, "programs/song-no-singer-analysis.json");

const program = JSON.parse(await readFile(programPath, "utf8"));
const units = extractEssayUnits(await readFile(essayPath, "utf8"));

const occurrences = new Map();
for (const shot of program.shots) {
  const list = occurrences.get(shot.continuityObject) ?? [];
  list.push(shot);
  occurrences.set(shot.continuityObject, list);
}

const analysis = {
  version: "1.0",
  essayId: program.id,
  title: program.title,
  centralClaim: "A person, observer, memory, or song is real as a conditioned and transformable pattern, while suffering intensifies when one local enactment claims independent ownership; recognition loosens that claim and becomes compassionate coordination among partial worlds.",
  sourceUnitCount: units.length,
  continuityCandidates: program.continuitySystems.map((system) => {
    const shots = occurrences.get(system.id);
    return {
      id: system.id,
      meaning: system.meaning,
      firstBeat: shots[0].id,
      development: `Track this conserved meaning through ${shots.length} argumentative beats as its relation, scale, and consequence change.`,
      resolution: `Resolve it in ${shots.at(-1).id}: ${shots.at(-1).claim}`,
    };
  }),
  beats: program.shots.map((shot, index) => {
    const selectedUnits = units.slice(shot.paragraphs[0] - 1, shot.paragraphs[1]);
    const previous = program.shots[index - 1];
    return {
      id: shot.id,
      sourceUnits: shot.paragraphs,
      sourceUnitTypes: [...new Set(selectedUnits.map((unit) => unit.type))],
      spokenWordCount: selectedUnits.reduce((total, unit) => total + unit.wordCount, 0),
      chapter: shot.chapter,
      argumentRole: shot.semanticRole,
      claim: shot.claim,
      relationType: shot.relationType,
      sourceState: shot.sourceState,
      targetState: shot.targetState,
      preserves: shot.preserves,
      whyNow: previous
        ? `This beat follows "${previous.title}" by moving from ${previous.semanticRole} to ${shot.semanticRole} while advancing the essay's next stated relation.`
        : "This opening beat establishes the cross-tradition coordinates required by the essay's first question.",
      misreadRisk: shot.misreadRisk,
      visualExclusions: [shot.antiLiteral],
    };
  }),
};

await writeFile(outputPath, `${JSON.stringify(analysis, null, 2)}\n`);
console.log(outputPath);
