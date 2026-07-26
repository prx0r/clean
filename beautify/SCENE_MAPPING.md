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

## Pack 03 · Voice Inside the Chest

Art direction: abyssal bioluminescent anatomy — peristaltic ribbons, neural
plankton, vagal signal tides and serotonin amber in a black-teal body ocean.

| Visual key | GLSL shader | PIL semantic reference |
|---|---|---|
| `architecture` | `03_voice_inside_chest/vis_gut_architecture.glsl` | `vis_gut_architecture` |
| `neural_crest` | `03_voice_inside_chest/vis_neural_crest_migration.glsl` | `vis_neural_crest_migration` |
| `reflex` | `03_voice_inside_chest/vis_independent_reflex.glsl` | `vis_independent_reflex` |
| `serotonin` | `03_voice_inside_chest/vis_serotonin_factory.glsl` | `vis_serotonin_factory` |
| `vagus` | `03_voice_inside_chest/vis_vagus_highway.glsl` | `vis_vagus_highway` |
| `microbiome` | `03_voice_inside_chest/vis_microbiome_dialogue.glsl` | `vis_microbiome_dialogue` |
| `gut_feeling` | `03_voice_inside_chest/vis_gut_feeling.glsl` | `vis_gut_feeling` |
| `glia` | `03_voice_inside_chest/vis_enteric_glia.glsl` | `vis_enteric_glia` |
| `stress` | `03_voice_inside_chest/vis_stress_response.glsl` | `vis_stress_response` |
| `neurogenesis` | `03_voice_inside_chest/vis_neurogenesis.glsl` | `vis_neurogenesis` |
| `heart` | `03_voice_inside_chest/vis_heart_center.glsl` | `vis_heart_center` |
| `dual_brain` | `03_voice_inside_chest/vis_dual_brain.glsl` | `vis_dual_brain` |
| `synthesis` | `03_voice_inside_chest/vis_synthesis.glsl` | `vis_synthesis` |
| `intelligence` | `03_voice_inside_chest/vis_bodily_intelligence.glsl` | `vis_bodily_intelligence` |
| `resilience` | `03_voice_inside_chest/vis_resilience.glsl` | `vis_resilience` |
| `evidence` | `03_voice_inside_chest/vis_human_implication.glsl` | `vis_human_implication` |
| `final` | `03_voice_inside_chest/vis_final.glsl` | `vis_final` |

## Pack 04 · Dreams Create Worlds

Art direction: wet dream-watercolor — luminous pigment blooms, capillary
edges, soft paper currents and half-remembered forms that merge as they move.

| Visual key | GLSL shader | PIL semantic reference |
|---|---|---|
| `sleep_cycle` | `04_dreams_create_worlds/vis_sleep_cycle.glsl` | `vis_sleep_cycle` |
| `brain_active` | `04_dreams_create_worlds/vis_brain_active.glsl` | `vis_brain_active` |
| `not_random` | `04_dreams_create_worlds/vis_dreams_not_random.glsl` | `vis_dreams_not_random` |
| `two_worlds` | `04_dreams_create_worlds/vis_seth_dream_reality.glsl` | `vis_seth_dream_reality` |
| `frameworks` | `04_dreams_create_worlds/vis_conventional_versus.glsl` | `vis_conventional_versus` |
| `wave` | `04_dreams_create_worlds/vis_dream_wave.glsl` | `vis_dream_wave` |
| `seeding` | `04_dreams_create_worlds/vis_dream_seeding.glsl` | `vis_dream_seeding` |
| `source` | `04_dreams_create_worlds/vis_dream_source.glsl` | `vis_dream_source` |
| `primitive` | `04_dreams_create_worlds/vis_primitive_dream.glsl` | `vis_primitive_dream` |
| `cooperative` | `04_dreams_create_worlds/vis_cooperative_dream.glsl` | `vis_cooperative_dream` |
| `invention` | `04_dreams_create_worlds/vis_dream_invention.glsl` | `vis_dream_invention` |
| `extension` | `04_dreams_create_worlds/vis_waking_extension.glsl` | `vis_waking_extension` |
| `lucid` | `04_dreams_create_worlds/vis_lucid_dream.glsl` | `vis_lucid_dream` |
| `consciousness_units` | `04_dreams_create_worlds/vis_consciousness_all_species.glsl` | `vis_consciousness_all_species` |
| `spacious` | `04_dreams_create_worlds/vis_space_present.glsl` | `vis_space_present` |
| `dialog` | `04_dreams_create_worlds/vis_dialog.glsl` | `vis_dialog` |
| `inner_senses` | `04_dreams_create_worlds/vis_inner_senses.glsl` | `vis_inner_senses` |
| `dual_focus` | `04_dreams_create_worlds/vis_dual_focus.glsl` | `vis_dual_focus` |
| `merge` | `04_dreams_create_worlds/vis_dream_merge.glsl` | `vis_dream_merge` |
| `universe_dreamed` | `04_dreams_create_worlds/vis_universe_dreamed.glsl` | `vis_universe_dreamed` |
| `transition` | `04_dreams_create_worlds/vis_waking_to_dream.glsl` | `vis_waking_to_dream` |
| `final` | `04_dreams_create_worlds/vis_final.glsl` | `vis_final` |

## Pack 05 · Time Is Produced by Forgetting

Art direction: abstract temporal geometry — obsidian depth, gold and cyan
chronostructures, recursive clocks, discontinuous planes and dissolving ink
at the limits of sequence.

| Visual key | GLSL shader | PIL semantic reference |
|---|---|---|
| `all` | `05_time_is_produced_by_forgetting/vis_all_at_once.glsl` | `vis_all_at_once` |
| `exclude` | `05_time_is_produced_by_forgetting/vis_exclusion.glsl` | `vis_exclusion` |
| `sequence` | `05_time_is_produced_by_forgetting/vis_sequence_birth.glsl` | `vis_sequence_birth` |
| `now` | `05_time_is_produced_by_forgetting/vis_now_slice.glsl` | `vis_now_slice` |
| `past` | `05_time_is_produced_by_forgetting/vis_past_trace.glsl` | `vis_past_trace` |
| `future` | `05_time_is_produced_by_forgetting/vis_future_open.glsl` | `vis_future_open` |
| `desire` | `05_time_is_produced_by_forgetting/vis_desire_clock.glsl` | `vis_desire_clock` |
| `fear` | `05_time_is_produced_by_forgetting/vis_fear_future.glsl` | `vis_fear_future` |
| `boredom` | `05_time_is_produced_by_forgetting/vis_boredom.glsl` | `vis_boredom` |
| `flow` | `05_time_is_produced_by_forgetting/vis_flow_time.glsl` | `vis_flow_time` |
| `identity` | `05_time_is_produced_by_forgetting/vis_memory_identity.glsl` | `vis_memory_identity` |
| `tense` | `05_time_is_produced_by_forgetting/vis_language_tense.glsl` | `vis_language_tense` |
| `clock` | `05_time_is_produced_by_forgetting/vis_clock_vs_lived.glsl` | `vis_clock_vs_lived` |
| `kala` | `05_time_is_produced_by_forgetting/vis_kanchuka_kala.glsl` | `vis_kanchuka_kala` |
| `krama` | `05_time_is_produced_by_forgetting/vis_krama.glsl` | `vis_krama` |
| `akrama` | `05_time_is_produced_by_forgetting/vis_akrama.glsl` | `vis_akrama` |
| `flash` | `05_time_is_produced_by_forgetting/vis_flash.glsl` | `vis_flash` |
| `music` | `05_time_is_produced_by_forgetting/vis_music.glsl` | `vis_music` |
| `death` | `05_time_is_produced_by_forgetting/vis_death_boundary.glsl` | `vis_death_boundary` |
| `meditation` | `05_time_is_produced_by_forgetting/vis_meditation_gap.glsl` | `vis_meditation_gap` |
| `recognition` | `05_time_is_produced_by_forgetting/vis_recognition.glsl` | `vis_recognition` |
| `bridge` | `05_time_is_produced_by_forgetting/vis_science_bridge.glsl` | `vis_science_bridge` |
| `caution` | `05_time_is_produced_by_forgetting/vis_caution.glsl` | `vis_caution` |
| `final` | `05_time_is_produced_by_forgetting/vis_final.glsl` | `vis_final` |
