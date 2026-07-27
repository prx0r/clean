import { semanticVisualNames, registerDynamicRenderer } from "../semantic-visuals.mjs";

export const baseSemanticVisualNames = semanticVisualNames;

export function registerSemanticVisual({ name, renderer, description }) {
  registerDynamicRenderer(name, renderer);
}

export function getAllDynamicMechanisms() {
  return [];
}
