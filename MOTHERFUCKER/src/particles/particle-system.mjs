import { seededRandom } from "../../math.mjs";

export class ParticleSystem {
  constructor({ seed = 1, maxParticles = 1000, emitter, field, constraint = null, renderer }) {
    if (!emitter || !field || !renderer) throw new Error("ParticleSystem requires emitter, field and renderer");
    this.rng = seededRandom(seed >>> 0);
    this.maxParticles = maxParticles;
    this.emitter = emitter;
    this.field = field;
    this.constraint = constraint;
    this.renderer = renderer;
    this.particles = [];
    this.accumulator = 0;
    this.time = 0;
  }
  random() { return this.rng(); }
  emit(count, context = {}) {
    const amount = Math.min(this.maxParticles - this.particles.length, Math.max(0, Math.floor(count)));
    for (let i = 0; i < amount; i += 1) {
      this.particles.push(this.emitter.create({
        rng: () => this.random(),
        time: this.time,
        index: this.particles.length,
        context,
      }));
    }
  }
  update(dt, context = {}) {
    this.time += dt;
    const rate = Math.max(0, typeof this.emitter.rate === "function" ? this.emitter.rate(context) : this.emitter.rate ?? 0);
    this.accumulator += rate * dt;
    const count = Math.floor(this.accumulator);
    if (count > 0) { this.emit(count, context); this.accumulator -= count; }
    for (const particle of this.particles) {
      particle.age += dt;
      const a = this.field.sample(particle, { ...context, time:this.time, dt });
      particle.vx += (a.x ?? 0) * dt;
      particle.vy += (a.y ?? 0) * dt;
      particle.x += particle.vx * dt;
      particle.y += particle.vy * dt;
      if (this.constraint) this.constraint.apply(particle, context);
      if (particle.trail) {
        particle.trail.push({ x:particle.x, y:particle.y, age:particle.age });
        if (particle.trail.length > (particle.trailLength ?? 16)) particle.trail.shift();
      }
    }
    this.particles = this.particles.filter((particle) => particle.age < particle.life);
  }
  draw(ctx, context = {}) { this.renderer.draw(ctx, this.particles, { ...context, time:this.time }); }
}
