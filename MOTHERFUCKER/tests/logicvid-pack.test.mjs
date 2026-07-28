import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const path=new URL("../packs/logicvid-reality-appears.template.json",import.meta.url);
const pack=JSON.parse(await readFile(path,"utf8"));

test("logicvid contains a complete nine-scene argument",()=>{
  assert.equal(pack.scenes.length,9);
  assert.deepEqual(pack.scenes.map((s)=>s.id),["lv01","lv02","lv03","lv04","lv05","lv06","lv07","lv08","lv09"]);
});

test("every scene uses authored move windows",()=>{
  for(const scene of pack.scenes){
    assert.equal(scene.motif,"argument-diagram-v2");
    for(const move of scene.params.moves){
      assert.ok(Number.isFinite(move.start));
      assert.ok(Number.isFinite(move.end));
      assert.ok(move.start>=0&&move.end<=1&&move.end>move.start);
    }
  }
});

test("film preserves epistemic distinction",()=>{
  const text=JSON.stringify(pack);
  assert.match(text,/structural comparison|Comparable as/);
  assert.match(text,/not an empirical result|established scientific result/);
  assert.match(text,/Non-claim|physics verified spanda/);
});
