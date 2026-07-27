import { Path2D, PathOp } from "@napi-rs/canvas";
import { pathFromPoints } from "./path-utils.mjs";

function normalizePath(input) {
  if (input instanceof Path2D) return input;
  if (Array.isArray(input)) return pathFromPoints(input, { closed: true });
  throw new TypeError("Expected Path2D or point array");
}

function applyOp(left, right, operation) {
  const a = normalizePath(left);
  const b = normalizePath(right);
  if (typeof a.op !== "function" || operation === undefined) {
    throw new Error("Path boolean operations are unavailable in this @napi-rs/canvas build");
  }
  const result = new Path2D(a);
  result.op(b, operation);
  return result;
}

export const unionPaths = (a, b) => applyOp(a, b, PathOp?.Union);
export const intersectPaths = (a, b) => applyOp(a, b, PathOp?.Intersect);
export const differencePaths = (a, b) => applyOp(a, b, PathOp?.Difference);
export const xorPaths = (a, b) => applyOp(a, b, PathOp?.XOR);

export function trimPath(path, start = 0, end = 1, complement = false) {
  const result = new Path2D(normalizePath(path));
  if (typeof result.trim === "function") result.trim(start, end, complement);
  return result;
}

export function dashPath(path, on = 12, off = 8, phase = 0) {
  const result = new Path2D(normalizePath(path));
  if (typeof result.dash === "function") result.dash(on, off, phase);
  return result;
}

export function strokeToPath(path, options = {}) {
  const result = new Path2D(normalizePath(path));
  if (typeof result.stroke === "function") result.stroke({
    width: options.width ?? 8,
    join: options.join ?? "round",
    cap: options.cap ?? "round",
    miterLimit: options.miterLimit ?? 4,
  });
  return result;
}

export function simplifyPath(path) {
  const result = new Path2D(normalizePath(path));
  if (typeof result.simplify === "function") result.simplify();
  return result;
}
