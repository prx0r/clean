import { createCanvas } from "@napi-rs/canvas";

export class LayerStack {
  constructor(width, height, { colorSpace = "srgb" } = {}) {
    this.width = width;
    this.height = height;
    this.colorSpace = colorSpace;
    this.layers = new Map();
  }
  create(name, options = {}) {
    if (this.layers.has(name)) throw new Error(`Layer "${name}" already exists`);
    const canvas = createCanvas(this.width, this.height);
    const ctx = canvas.getContext("2d", { colorSpace: options.colorSpace ?? this.colorSpace });
    const layer = { name, canvas, ctx, blend: options.blend ?? "source-over", opacity: options.opacity ?? 1, visible: options.visible ?? true };
    this.layers.set(name, layer);
    return layer;
  }
  get(name) {
    const layer = this.layers.get(name);
    if (!layer) throw new Error(`Unknown layer "${name}"`);
    return layer;
  }
  composite(targetCtx, order = [...this.layers.keys()]) {
    targetCtx.save();
    for (const name of order) {
      const layer = this.get(name);
      if (!layer.visible || layer.opacity <= 0) continue;
      targetCtx.globalCompositeOperation = layer.blend;
      targetCtx.globalAlpha = layer.opacity;
      targetCtx.drawImage(layer.canvas, 0, 0);
    }
    targetCtx.restore();
  }
}
