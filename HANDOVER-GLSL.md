# GLSL Pipeline — Handover for Next Agent

## Current State

17 GLSL shaders exist in `/root/projects/tantraloka/moderngl/shaders/` — they are **syntactically correct but never tested on GPU**. The render harness at `moderngl/render_harness.py` exists. The studio at `studio.tantrafiles.xyz` serves videos from R2 but doesn't yet pull from the anakhra-renders bucket.

## What's Needed to Get GLSL Rendering Working

### 1. Rent a GPU Box (Vast AI, ~$0.20-0.40/hr)

```bash
# On the GPU box:
pip install moderngl numpy pillow
python -c "import moderngl; ctx = moderngl.create_context(standalone=True, backend='egl'); print(ctx.info['GL_RENDERER'])"
```

Must output a GPU name (e.g., "NVIDIA RTX 4090"), not "llvmpipe". If llvmpipe → EGL ICD is broken, fix with:

```bash
apt install libegl1-mesa libegl1-mesa-dev
apt install nvidia-egl-icd  # or nvidia-driver-*-server on Vast
```

### 2. Test All 17 Shaders

```bash
cd /root/projects/tantraloka/moderngl
python render_harness.py --pack life_crosses_barriers --preview
```

The `--preview` flag renders 4 stills per scene instead of the full video. Then compare side-by-side with the existing PIL output at `/mnt/HC_Volume_106427611/goldrender/rendered_platinum/`.

Common issues:
- Domain-warped noise in `fieldBackground()` may differ from PIL version
- Glow intensities may need tuning (additive glow in GLSL looks different from alpha-blend in PIL)
- All text rendering is commented out (no SDF font atlas yet)

### 3. Wire Audio Uniforms

Only `classical_wall.glsl` has audio reactivity wired. The other 16 shaders accept `u_audioVolume` and `u_audioBeat` uniforms but don't use them yet.

### 4. Connect to Studio

Once shaders render correctly, upload output to R2 bucket `anakhra-renders` and the studio will serve them. The studio API at `tantrafiles-hub/functions/api/[[path]].js` already handles R2 serving for any video key.

## Deploying Studio Changes (Blocked on Token)

The timestamp capture code is saved at `tantrafiles-hub/public/index.html` and `tantrafiles-hub/functions/api/[[path]].js`. Needs:

```bash
# Fix: the wrangler config was missing an auth token
npx wrangler login  # or set CLOUDFLARE_API_TOKEN
npx wrangler pages deploy public --project-name tantrafiles
```

If the Cloudflare token has expired, generate a new one at `dash.cloudflare.com/profile/api-tokens` with permissions for Workers R2 and Pages.

## Reference: Key File Locations

| File | Purpose |
|------|---------|
| `tantraloka/moderngl/shaders/` | 17 GLSL fragment shaders |
| `tantraloka/moderngl/render_harness.py` | Headless GPU render pipeline |
| `tantraloka/moderngl/renderer/engine.py` | ModernGL context, framebuffer, render loop |
| `tantraloka/moderngl/renderer/audio_analysis.py` | Librosa audio feature extraction |
| `tantraloka/moderngl/SCENE_MAPPING.md` | Which shader maps to which PIL visual mode |
| `tantraloka/moderngl/HANDOVER.md` | Full GLSL port handover notes |
| `tantraloka/goldrender/` | 99 existing PIL packs (reference output) |
| `tantraloka/goldrender/batch_render.py` | Batch render orchestrator |
| `tantraloka/goldrender/HANDOVER.md` | Goldrender pipeline handover |
| `tantrafiles-hub/functions/api/[[path]].js` | Studio API — D1 comments, R2 video serving |
| `tantrafiles-hub/public/index.html` | Studio UI — video player, timestamp capture, comments |
