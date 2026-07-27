import test from "node:test";
import assert from "node:assert/strict";
import { ParticleSystem } from "../src/particles/particle-system.mjs";
import { pointEmitter } from "../src/particles/emitters.mjs";
import { radialField } from "../src/particles/fields.mjs";
test("particle system emits deterministically",()=>{
  const make=()=>new ParticleSystem({seed:42,maxParticles:20,emitter:pointEmitter({x:0,y:0,rate:10,spread:5}),field:radialField({cx:0,cy:0,strength:1}),renderer:{draw(){}}});
  const a=make(),b=make();a.update(1);b.update(1);assert.deepEqual(a.particles,b.particles);assert.equal(a.particles.length,10);
});
