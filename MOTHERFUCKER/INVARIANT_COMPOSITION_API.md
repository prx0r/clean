# Invariant Composition API

## Assets

| Asset | Purpose |
|---|---|
| `continuity-seed` | General lobed continuity object |
| `relational-signature` | Identity encoded as relations |
| `transformation-orbit` | Group-action family |
| `carrier-shell` | Material embodiment |
| `causal-trace` | History-dependent field |
| `trajectory-ribbon` | Value, velocity and acceleration |
| `lead-lag-lanes` | Cross-modal offsets |
| `invariant-gauge` | Preservation score |
| `topology-thread` | Connectivity continuity |
| `semantic-verb-mark` | Causal transition grammar |
| `attention-budget` | Density allocation |
| `recognition-field` | Carrier-to-relation emphasis shift |

## Mechanisms

| Mechanism | Visual theorem |
|---|---|
| `transformation-invariance` | Appearance may change while relation persists |
| `carrier-transfer` | Identity can migrate without a permanent carrier |
| `causal-memory` | Present state depends on its history |
| `derivative-trajectory` | Equal values can imply different futures |
| `lead-lag-counterpoint` | Coordination does not require simultaneity |
| `conservation-filter` | Continuity is constrained, not arbitrary |
| `semantic-transition` | A transition is a causal operation |
| `polyphonic-identity` | Multiplicity can preserve one subject |
| `recognition-transaction` | Attention can shift from carrier to invariant |
| `climax-assimilation` | Peak and endpoint are distinct |
| `structural-homology` | Different media can perform one causal law |
| `constraint-tournament` | Quality emerges through principled rejection |

## Rendering

The current core `renderer.loadPack()` validates before it knows which
capability packs to activate. Use the included capability-aware loader:

```js
import { loadCapabilityScenePack } from "./src/load-capability-scene-pack.mjs";

const pack = await loadCapabilityScenePack(
  "./packs/invariant-composition-demo.json",
);
```

Or run:

```bash
node tools/render-invariant-demo.mjs
```

## Child-pack strategy

This pack should usually be combined with a domain pack:

```json
{
  "capabilityPacks": [
    "invariant-composition",
    "neurocognition"
  ]
}
```

Examples:

- memory essay: `causal-memory` + `memory-trace`;
- predictive processing: `lead-lag-counterpoint` + `predictive-loop`;
- subtle-body/science comparison: `structural-homology` +
  `physical-subtle-compare`;
- Tantrāloka manifestation: `transformation-invariance` +
  a future tattva/adhvan pack;
- textual transmission: `carrier-transfer` + a manuscript asset pack.
