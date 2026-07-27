"""Render the Spanda film. One-command wrapper using the shared renderer."""
import sys, json
from pathlib import Path
from renderer import Film
from spanda_scenes import SCENES

OUT = Path(__file__).parent / "spanda_output_pack"

film = Film("spanda", "The Engine of Consciousness — Spanda and the Hidden Pulse", SCENES)

# Save manifest
manifest = film.manifest()
(OUT / "scene_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

print(f"Rendering: {film.title}")
print(f"Scenes: {len(SCENES)}")
print(f"Duration: {sum(s.duration for s in SCENES):.1f}s")

film.render(OUT / "spanda_animation.mp4")
print(f"Saved: {OUT / 'spanda_animation.mp4'}")
