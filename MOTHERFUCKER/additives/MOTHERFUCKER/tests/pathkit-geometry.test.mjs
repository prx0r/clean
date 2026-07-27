import test from "node:test";
import assert from "node:assert/strict";
import { lotusRing } from "../src/geometry/lotus-generators.mjs";
import { sriYantraApprox } from "../src/geometry/yantra-generators.mjs";
import { resamplePolyline, morphPointSets, signedArea } from "../src/geometry/path-utils.mjs";

test("lotus ring creates requested petals",()=>assert.equal(lotusRing({petals:12}).length,12));
test("resampling returns exact count",()=>assert.equal(resamplePolyline([{x:0,y:0},{x:10,y:0},{x:10,y:10}],32,false).length,32));
test("morph returns stable count",()=>assert.equal(morphPointSets([{x:0,y:0},{x:10,y:0},{x:10,y:10},{x:0,y:10}],[{x:5,y:-5},{x:15,y:5},{x:5,y:15},{x:-5,y:5}],0.5,64,true).length,64));
test("sri yantra approximation creates a path",()=>assert.ok(sriYantraApprox()));
test("signed area distinguishes orientation",()=>assert.ok(signedArea([{x:0,y:0},{x:1,y:0},{x:0,y:1}])>0));
