import { Path2D } from "@napi-rs/canvas";

export const anatomyLandmarks = Object.freeze({
  crown: Object.freeze({ x: 0, y: 16 }),
  brow: Object.freeze({ x: 0, y: 55 }),
  mouth: Object.freeze({ x: 0, y: 72 }),
  throat: Object.freeze({ x: 0, y: 104 }),
  leftShoulder: Object.freeze({ x: -72, y: 118 }),
  rightShoulder: Object.freeze({ x: 72, y: 118 }),
  heart: Object.freeze({ x: -8, y: 169 }),
  lungLeft: Object.freeze({ x: -27, y: 174 }),
  lungRight: Object.freeze({ x: 27, y: 174 }),
  diaphragm: Object.freeze({ x: 0, y: 213 }),
  solarPlexus: Object.freeze({ x: 0, y: 211 }),
  navel: Object.freeze({ x: 0, y: 243 }),
  sacrum: Object.freeze({ x: 0, y: 286 }),
  root: Object.freeze({ x: 0, y: 304 }),
  leftElbow: Object.freeze({ x: -101, y: 219 }),
  rightElbow: Object.freeze({ x: 101, y: 219 }),
  leftWrist: Object.freeze({ x: -112, y: 309 }),
  rightWrist: Object.freeze({ x: 112, y: 309 }),
  leftHip: Object.freeze({ x: -42, y: 293 }),
  rightHip: Object.freeze({ x: 42, y: 293 }),
  leftKnee: Object.freeze({ x: -44, y: 395 }),
  rightKnee: Object.freeze({ x: 44, y: 395 }),
  leftAnkle: Object.freeze({ x: -40, y: 478 }),
  rightAnkle: Object.freeze({ x: 40, y: 478 }),
});

export const chakraLandmarks = Object.freeze([
  Object.freeze({ id: "muladhara", term: "Mūlādhāra", devanagari: "मूलाधार", x: 0, y: 298, petals: 4, color: "#a8444e" }),
  Object.freeze({ id: "svadhisthana", term: "Svādhiṣṭhāna", devanagari: "स्वाधिष्ठान", x: 0, y: 267, petals: 6, color: "#c56f34" }),
  Object.freeze({ id: "manipura", term: "Maṇipūra", devanagari: "मणिपूर", x: 0, y: 222, petals: 10, color: "#d6a338" }),
  Object.freeze({ id: "anahata", term: "Anāhata", devanagari: "अनाहत", x: 0, y: 174, petals: 12, color: "#5c9274" }),
  Object.freeze({ id: "vishuddha", term: "Viśuddha", devanagari: "विशुद्ध", x: 0, y: 107, petals: 16, color: "#4389a6" }),
  Object.freeze({ id: "ajna", term: "Ājñā", devanagari: "आज्ञा", x: 0, y: 55, petals: 2, color: "#5c6ca4" }),
  Object.freeze({ id: "sahasrara", term: "Sahasrāra", devanagari: "सहस्रार", x: 0, y: 15, petals: 24, color: "#8767a3" }),
]);

export const dvadasantaStations = Object.freeze([
  Object.freeze({ id: "hrdaya", label: "hṛdaya", x: 0, y: 174 }),
  Object.freeze({ id: "kantha", label: "kaṇṭha", x: 0, y: 107 }),
  Object.freeze({ id: "talu", label: "tālu", x: 0, y: 78 }),
  Object.freeze({ id: "bhrumadhya", label: "bhrūmadhya", x: 0, y: 55 }),
  Object.freeze({ id: "lalata", label: "lalāṭa", x: 0, y: 39 }),
  Object.freeze({ id: "brahmarandhra", label: "brahmarandhra", x: 0, y: 15 }),
  Object.freeze({ id: "sikha", label: "śikhā", x: 0, y: -10 }),
  Object.freeze({ id: "pascima", label: "paścima", x: -10, y: -34 }),
  Object.freeze({ id: "shakti", label: "śakti", x: 0, y: -58 }),
  Object.freeze({ id: "vyapini", label: "vyāpinī", x: 0, y: -86 }),
  Object.freeze({ id: "samana", label: "samanā", x: 0, y: -116 }),
  Object.freeze({ id: "unmana", label: "unmanā", x: 0, y: -150 }),
]);

export function bodyFrame(params = {}) {
  return {
    cx: params.x ?? 640,
    top: params.y ?? 82,
    scale: params.scale ?? 0.91,
  };
}

export function bodyPoint(nameOrPoint, params = {}) {
  const frame = bodyFrame(params);
  const point = typeof nameOrPoint === "string"
    ? anatomyLandmarks[nameOrPoint]
    : nameOrPoint;
  if (!point) throw new Error(`Unknown anatomy landmark "${nameOrPoint}"`);
  return {
    x: frame.cx + point.x * frame.scale,
    y: frame.top + point.y * frame.scale,
  };
}

export function standingBodyPath() {
  const path = new Path2D();
  path.moveTo(-18, 87);
  path.bezierCurveTo(-31, 91, -51, 103, -74, 112);
  path.bezierCurveTo(-93, 122, -100, 151, -104, 183);
  path.bezierCurveTo(-110, 224, -116, 268, -119, 310);
  path.bezierCurveTo(-120, 324, -108, 329, -102, 316);
  path.bezierCurveTo(-88, 271, -79, 226, -70, 184);
  path.bezierCurveTo(-64, 160, -58, 150, -52, 148);
  path.bezierCurveTo(-55, 192, -58, 238, -49, 278);
  path.bezierCurveTo(-45, 296, -47, 317, -51, 345);
  path.bezierCurveTo(-57, 387, -51, 437, -47, 476);
  path.bezierCurveTo(-45, 493, -34, 499, -27, 484);
  path.bezierCurveTo(-16, 441, -12, 391, -9, 345);
  path.lineTo(0, 314);
  path.lineTo(9, 345);
  path.bezierCurveTo(12, 391, 16, 441, 27, 484);
  path.bezierCurveTo(34, 499, 45, 493, 47, 476);
  path.bezierCurveTo(51, 437, 57, 387, 51, 345);
  path.bezierCurveTo(47, 317, 45, 296, 49, 278);
  path.bezierCurveTo(58, 238, 55, 192, 52, 148);
  path.bezierCurveTo(58, 150, 64, 160, 70, 184);
  path.bezierCurveTo(79, 226, 88, 271, 102, 316);
  path.bezierCurveTo(108, 329, 120, 324, 119, 310);
  path.bezierCurveTo(116, 268, 110, 224, 104, 183);
  path.bezierCurveTo(100, 151, 93, 122, 74, 112);
  path.bezierCurveTo(51, 103, 31, 91, 18, 87);
  path.bezierCurveTo(14, 80, 13, 76, 13, 73);
  path.lineTo(-13, 73);
  path.bezierCurveTo(-13, 76, -14, 80, -18, 87);
  path.closePath();
  return path;
}

export function withBodyTransform(ctx, params, draw) {
  const frame = bodyFrame(params);
  ctx.save();
  ctx.translate(frame.cx, frame.top);
  ctx.scale(frame.scale, frame.scale);
  draw(frame);
  ctx.restore();
}

