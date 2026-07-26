# Signature Film System

This folder is a production system for turning a narrated essay into an
authored GLSL short film. It is intentionally stricter than a style guide:
future agents produce an inspectable `film_spec.json`, validate it, implement
the scenes, render three states, and record review evidence.

The signature is not one palette, emblem, or camera. It is a repeatable relation
between meaning and motion:

> one continuity material is transformed by the argument; every scene gives
> that transformation a new causal topology; the final state preserves visible
> evidence of what the film learned.

## Files

- `SIGNATURE-FILM-SYSTEM.md` — semantic-to-visual design method.
- `PRIOR-OUTPUT-AUDIT.md` — what worked and failed across the previous 326
  shaders and 15 essays.
- `REVIEW-RUBRIC.md` — hard gates, weighted scoring, and render protocol.
- `AGENT-PROMPT.md` — copyable task prompt for future agents.
- `film_spec.schema.json` — machine-readable shape of a film decision record.
- `validate_film_spec.py` — deterministic semantic and repetition checks.
- `../lib/signature.glsl` — reusable semantic rendering operators.

Each new essay keeps its own material include and composition logic. The shared
library supplies relationships, not prefab scenes.

## Minimum command sequence

```bash
python beautify-archive/framework/validate_film_spec.py \
  beautify/<pack>/film_spec.json

python beautify-archive/lib/render_harness.py \
  --pack <pack> --audit --compile --compiler <glslangValidator>
```

Then render `u=0.18`, `u=0.72`, and `u=0.94` with different `t`, volume, and beat
values. A compile pass is necessary; it is not an art review.
