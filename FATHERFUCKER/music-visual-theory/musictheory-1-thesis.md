# Music Theory 1: Harmonic Surprise & Neural Phase Dynamics

## Core Finding
Information-theoretic harmonic surprise triggers measurable disruptions in frontal neural oscillations. Coherence restoration rate correlates with subjective emotional valence.

## Methodology
- **Dataset**: DEAM corpus (1,802 excerpts, 32-channel EEG, 128Hz)
- **Surprise**: Markov chain order-3 on Lakh MIDI corpus. S_t = -log₂(P(chord_t | context))
- **Phase**: Hilbert transform → PLV (phase locking value) between frontal channels

## Three Hypotheses
| H | Prediction | Method |
|---|-----------|--------|
| H1 | High surprise → phase reset in frontal theta | Rayleigh test on 500ms post-event epochs |
| H2 | Alpha coherence ↔ positive valence correlation | Mixed-effects regression |
| H3 | Coherence restoration rate predicts emotional intensity | dPLV/dt regression |

## Relevance to Our System
- SignatureTiming.transform → H1: phase reset from harmonic surprise
- SignatureTiming.resolve → H3: coherence restoration rate
- Rasa valence → H2: alpha coherence correlation
- M₂ (geometric alignment → chord quality) → directly testable via EEG
