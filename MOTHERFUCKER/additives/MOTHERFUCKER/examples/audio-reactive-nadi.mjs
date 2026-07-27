import { ParticleSystem } from "../src/particles/particle-system.mjs";
import { pathEmitter } from "../src/particles/emitters.mjs";
import { pathFollowField, noiseField, combineFields } from "../src/particles/fields.mjs";
import { pathAttractorConstraint } from "../src/particles/constraints.mjs";
import { orbRenderer, trailRenderer, compositeParticleRenderer } from "../src/particles/renderers.mjs";
import { AudioRouter } from "../src/audio/audio-router.mjs";

export function createAudioReactiveNadi(points) {
  const router=new AudioRouter([
    {source:"onset",target:"emission",minimum:4,maximum:70,curve:"ease-out",attack:0.01,release:0.18},
    {source:"harmonicEnergy",target:"trailLength",minimum:8,maximum:36,attack:0.08,release:0.6},
    {source:"spectralCentroid",target:"speed",minimum:18,maximum:95,attack:0.05,release:0.3},
  ]);
  const system=new ParticleSystem({
    seed:108,maxParticles:700,
    emitter:pathEmitter({points,rate:15,jitter:4,options:{life:3.2,trail:true,color:"#f4d77c"}}),
    field:combineFields(pathFollowField({points,strength:55,attraction:1.4}),noiseField({strength:4,frequency:0.018})),
    constraint:pathAttractorConstraint({points,maximumDistance:32,correction:0.35}),
    renderer:compositeParticleRenderer(trailRenderer({color:"#65d5e7",width:1.2}),orbRenderer({color:"#f4d77c",glow:10})),
  });
  return {
    update(features,dt){
      const values=router.update(features,dt);
      system.emitter.rate=values.emission;
      for(const particle of system.particles) particle.trailLength=Math.round(values.trailLength);
      system.update(dt,values);
    },
    draw(ctx){system.draw(ctx);}
  };
}
