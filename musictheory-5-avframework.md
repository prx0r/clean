# Music Theory 5: Audio-Visual Framework (JavaScript Implementation)

## Architecture
Working p5.js + Web Audio implementation with 7-mapper pipeline.

## Mapper Implementations
| Mapper | Maps | Details |
|--------|------|---------|
| SpectralEngine | Frequency → spectrum | Harmonic series with inharmonicity + brightness. Spectrum morphing. |
| HarmonicField | Spectrum → spatial field | Frequency centers in 2D space with interference waves. |
| ColorMapper | Frequency/note → HSL color | 12 notes → 12 hues via circle of fifths. Octave = brightness mod. |
| TimbreMapper | Instrument → visual texture | Strings=flowing curves (warm), brass=metallic cones (gold), woodwinds=organic tubes (earth), percussion=impact bursts (bright). |
| RhythmMapper | Hit type → spatial interference | Kick=radial pulse, snare=directional burst, hihat=high-freq scatter. |
| DynamicsMapper | Dynamics → field energy | ppp=0.1, mf=0.6, ff=0.9 field energy with opacity/size/glow. |
| GeometryMapper | Interval → shape | Unison=point, octave=circle, fifth=pentagon, third=triangle. Chords → polygons with stability weights. |

## What to Steal
- Note → color mapping table (12 notes)
- Timbre → visual texture mapping (4 instruments)
- Interval → geometry mapping (7 intervals)
- Rhythm → interference pattern mapping (3 hit types)
