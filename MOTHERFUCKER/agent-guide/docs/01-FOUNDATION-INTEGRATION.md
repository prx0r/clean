# Foundation Integration

## 1. Copy the PathKit overlay

Copy the contents of the PathKit package over the existing framework:

```bash
cp -R pathkit-visionary-engine/MOTHERFUCKER/* \
  /path/to/clean/MOTHERFUCKER/
```

The overlay is additive.

## 2. Confirm capability-aware loading

Dynamic packs must be activated before scene validation.

Use:

```js
import { loadCapabilityScenePack } from "./src/load-capability-scene-pack.mjs";

const pack = await loadCapabilityScenePack("./packs/example.json");
```

Do not call the old `renderer.loadPack()` directly for a pack containing custom
dynamic mechanisms unless it has already been updated to activate declared
capabilities first.

## 3. Add shared runtime context

The renderer should expose a stable environment object to every asset and
mechanism:

```js
const environment = {
  theme,
  seed,
  width,
  height,
  fps,
  frame,
  seconds,
  sceneSeconds,
  sceneProgress,
  audio: sampledAudioFeatures,
  narration: sampledNarrationFeatures,
  score: sampledScoreFeatures,
  style: resolvedStyleProfile,
  material: resolvedMaterialProfile,
  composition: compositionState,
};
```

Existing mechanisms may ignore these fields. New mechanisms can consume them
without changing their function signature.

## 4. Recommended scene contract

```json
{
  "id": "nadi-entrainment-01",
  "motif": "semantic-essay",
  "params": {
    "visual": "central-channel-entrainment"
  },
  "assets": [
    {
      "id": "subtle-body-frame",
      "layer": "structure"
    },
    {
      "id": "sushumna-channel",
      "layer": "channel"
    }
  ],
  "styleProfile": "luminous-subtle-body",
  "materialProfile": "luminous-subtle-body",
  "motionProfile": "breath-current",
  "signalRouting": "nadi-harmonic-prana",
  "duration": 12
}
```

## 5. Registry additions

The framework should eventually expose registries for:

```text
capabilities
assets
mechanisms
geometry profiles
material profiles
motion profiles
style profiles
audio routes
narration routes
composition profiles
```

Until those registries exist, the guide uses JSON profile files loaded by the
scene compiler.
