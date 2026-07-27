import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

import { activateCapabilityPacks } from "../extensionpacks/capability-packs.mjs";
import { assertPack } from "../schema.mjs";

export async function loadCapabilityScenePack(path) {
  const absolute = resolve(path);
  const data = JSON.parse(await readFile(absolute, "utf8"));
  await activateCapabilityPacks(data.capabilityPacks ?? ["base"]);
  return assertPack(data);
}
