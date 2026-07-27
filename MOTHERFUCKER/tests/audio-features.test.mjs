import test from "node:test";
import assert from "node:assert/strict";
import { sampleAudioFeatures, EnvelopeFollower } from "../src/audio/audio-features.mjs";
import { AudioRouter } from "../src/audio/audio-router.mjs";
const manifest={version:"1.0",frames:[{time:0,rms:0,onset:0,chroma:[0,1]},{time:1,rms:1,onset:0.5,chroma:[1,0]}]};
test("feature interpolation",()=>{const r=sampleAudioFeatures(manifest,0.5);assert.equal(r.rms,0.5);assert.deepEqual(r.chroma,[0.5,0.5]);});
test("envelope finite",()=>{const f=new EnvelopeFollower();const v=f.update(1,1/60);assert.ok(v>0&&v<1);});
test("router range",()=>{const r=new AudioRouter([{source:"rms",target:"size",minimum:2,maximum:10,attack:0.01,release:0.2}]);assert.ok(r.update({rms:1},1).size>9);});
