# GLSL ↔ PIL Visual Mode Mapping
## Pack: life_crosses_barriers_platinum.py

Each GLSL shader corresponds to one visual mode function used by multiple scenes.
The shader receives `u` (scene progress) and `t` (elapsed time) to animate
through the scene's progression. Audio uniforms (`u_audioVolume`, `u_audioBeat`)
add per-frame reactivity.

| GLSL Shader | PIL Function | Scene Titles (narration topics) |
|---|---|---|
| `classical_wall.glsl` | `visual_classical_wall` | "A proton reaches a wall" · "Climb" · "Stop" · "Return to wall" |
| `tunnelling.glsl` | `visual_tunnelling` | "Third option" · "No crack" · "Wave penetrates" · "Wavefunction" · "Decay" · "Detection" · "Quantum layer" |
| `width.glsl` | `visual_exponential_width` | "Width" · "Geometry becomes destiny" |
| `mass.glsl` | `visual_mass_comparison` | "Mass" · "Hydrogen transfer" |
| `landscape.glsl` | `visual_energy_landscape` | "Catalysis before enzyme" · "Catalysis inside enzyme" |
| `enzyme.glsl` | `visual_enzyme_pocket` | "Prepared situation" · "Donor and acceptor apart" · "Protein samples geometry" · "Breathing barrier" · "Motion and probability" · "Reliable flux" |
| `isotope.glsl` | `visual_isotope` | "Replace H with D" |
| `evidence.glsl` | `visual_evidence_caution` | "Open a case" · "Mechanism remains plural" |
| `evolution.glsl` | `visual_evolution` | "Evolution selects geometry" · "The molecule inherits mathematics" |
| `form.glsl` | `visual_triangle_doublewell` | "Triangle" · "Double well" · "Pointer into possibility" |
| `rates.glsl` | `visual_structure_rates` | "Structure selects" |
| `gate.glsl` | `visual_proton_gate` | "Water relay" · "Electric gate" · "Constraint gives direction" · "Life sculpts barriers" |
| `noise.glsl` | `visual_noise_control` | "Warm, wet, noisy" · "Noise samples geometry" · "Control without purity" |
| `architecture.glsl` | `visual_architecture_truth` | "No concept required" · "Architecture knows" · "Truths the body cannot state" |
| `warning.glsl` | `visual_metaphor_warning` | "No quantum magic" · "Do not overreach" · "Exact mechanism" · "Disciplined metaphor" |
| `psychology.glsl` | `visual_psychological_geometry` | "Same wall, more force" · "Change geometry" · "Preparation" · "Sudden from one level" |
| `final.glsl` | `visual_final_synthesis` | "No violation" · "Biological layer" · "Closing" · "Thin wall" |

## Notes

- Each shader is reused across multiple scenes with different narration text.
- The `u` uniform (0→1) drives per-scene animation independently.
- Audio uniforms make each scene's response unique per narration take.
- Shaders with mode branching (`classical_wall` has climb/stop, `psychology` has force/geometry) use `u` progression to switch states.

## Pack 02 · Beliefs Create Biology

Art direction: living stained-glass psychobiology — wine-dark cytoplasm,
breathing membranes, refracted cognition and gold intention.

| Visual key | GLSL shader | PIL semantic reference |
|---|---|---|
| `conventional` | `02_beliefs_create_biology/vis_conventional_view.glsl` | `vis_conventional_view` |
| `placebo` | `02_beliefs_create_biology/vis_placebo_phenomenon.glsl` | `vis_placebo_phenomenon` |
| `placebo_growing` | `02_beliefs_create_biology/vis_placebo_growing.glsl` | `vis_placebo_growing` |
| `seth_claim` | `02_beliefs_create_biology/vis_seth_claim.glsl` | `vis_seth_claim` |
| `belief_cell` | `02_beliefs_create_biology/vis_belief_shapes_cell.glsl` | `vis_belief_shapes_cell` |
| `cellular_faith` | `02_beliefs_create_biology/vis_cells_have_beliefs.glsl` | `vis_cells_have_beliefs` |
| `value_fulfillment` | `02_beliefs_create_biology/val_fulfillment.glsl` | `val_fulfillment` |
| `cooperation` | `02_beliefs_create_biology/vis_molecular_cooperation.glsl` | `vis_molecular_cooperation` |
| `dna_antenna` | `02_beliefs_create_biology/vis_dna_antenna.glsl` | `vis_dna_antenna` |
| `field` | `02_beliefs_create_biology/vis_consciousness_field.glsl` | `vis_consciousness_field` |
| `illness` | `02_beliefs_create_biology/vis_illness_as_communication.glsl` | `vis_illness_as_communication` |
| `dreams` | `02_beliefs_create_biology/vis_dreams_source.glsl` | `vis_dreams_source` |
| `psyche` | `02_beliefs_create_biology/vis_psyche_gestalt.glsl` | `vis_psyche_gestalt` |
| `free_will` | `02_beliefs_create_biology/vis_free_will_primitive.glsl` | `vis_free_will_primitive` |
| `vikalpa` | `02_beliefs_create_biology/vis_vikalpa_samskara.glsl` | `vis_vikalpa_samskara` |
| `healing` | `02_beliefs_create_biology/vis_healing_parity.glsl` | `vis_healing_parity` |
| `primacy` | `02_beliefs_create_biology/vis_consciousness_before_matter.glsl` | `vis_consciousness_before_matter` |
| `final` | `02_beliefs_create_biology/vis_final_synthesis.glsl` | `vis_final_synthesis` |
