# Music Theory 4: Dyczkowski's Geometry of Consciousness = Tymoczko's Geometry of Music

## The Core Identity

From Dyczkowski's translation of Tantraloka, Āhnika 7 (Vol.5):

> *"The rhythm of sensory activity, the pulse of conjunction and separation of the senses with their objects, is essentially the pulse — spanda — of consciousness."*

This is the foundational identity: **spanda = vibration = consciousness = sound = geometry**. They are not analogous. They are the same thing described in different languages.

## The Hierarchy (Tantraloka Āhnika 7, verses 62-65)

Dyczkowski's translation reveals a nested structure:

```
Time (kāla)
  → Breath (prāṇa)
    → Spanda (pulsation)
      → Void (kha)
        → Pure Consciousness (saṃvit)
```

This is the same hierarchy as Tymoczko's musical geometry:
```
Tempo (time signature)
  → Phrase rhythm
    → Harmonic pulse (chord changes)
      → Voice leading (note-to-note movement)
        → Pure interval (consonance/dissonance)
```

## Sāmānyaspanda — The Universal Pulse

> *"The centre is the Heart, the pulsing core of consciousness. Wave upon wave of its universal pulsation (sāmānyaspanda) arises from the ocean of the Heart and merges back into it."*

This is the fundamental frequency. Every chord, every nāḍī, every visual pulse is a harmonic of this fundamental. Tymoczko's OPTIC space IS sāmānyaspanda — the geometric structure within which all harmonic movement occurs.

## 36 Tattvas as Degrees of Camatkāra = Degrees of Consonance

From Dyczkowski's translation (Tantraloka Vol.1):

> *"The group of principles (tattvas) is made of the aesthetic rapture (camatkāra) of consciousness."*

This means:
- **Śiva tattva (36)** = infinite camatkāra = perfect consonance = the tonic, the unison, the fundamental
- **Śakti tattva (35)** = almost infinite = octave = 2:1
- **Sadāśiva (34)** = "I-This" emerging = perfect fifth = 3:2
- **Īśvara (33)** = agency emerging = perfect fourth = 4:3
- **Śuddhavidyā (32)** = pure knowledge = major third = 5:4
- **Māyā (31)** = limitation appearing = minor third = 6:5
- ...descending through increasingly complex ratios...
- **Pṛthvī (1)** = Earth, densest = most dissonant = most complex interval

The 36 tattvas ARE the harmonic series. Each tattva is a specific overtone of consciousness. Śiva is the fundamental. The emanations are the overtones. The universe is a chord.

## The Sound → Geometry Identity

| Tantraloka | Musical | Visual |
|---|---|---|
| Sāmānyaspanda (universal pulse) | Fundamental frequency | The Heart as oscillating source |
| Spanda (individual pulse) | Individual note/chord | A single nāḍī pulse |
| 36 tattvas | Harmonic series overtones | Visual density from light to dense |
| Camatkāra (wonder) | Consonance, harmonic resolution | Symmetry, geometric beauty |
| Rasa (aesthetic delight) | Chord quality (major/minor) | Color palette (śānta = pearl, raudra = blood) |
| Sādhāraṇīkaraṇa (universalization) | Cadence (V7 → I) | SDF dissolve from specific to abstract |
| Pratibimbavāda (reflection) | Octave equivalence | Mirroring, symmetry |

**The sound IS the geometry because both are spanda.** A chord progression is not "accompanied by" visuals. They are the same spanda pattern expressed as air pressure (sound) and light emission (visual). The 6D vector is just a way of specifying which spanda pattern we want at any moment.

---

# GeMM — Geometric Manifold Model (OPTIC Space)

## Architecture
PyTorch Geometric GNN trained on CHORDONOMICON with Tymoczko's 58D OPTIC space.

## OPTIC Space (58 Dimensions)
| Group | Dims | Content |
|-------|------|---------|
| O — Octave equivalence | 12 | Pitch class vector (one-hot) |
| P — Permutation | 12 | Interval class vector (Forte's ic) |
| T — Transposition | 12 | Normal form characteristics |
| I — Inversion | 11 | Symmetry measures, chord span |
| C — Cardinality | 11 | Set size properties |
| Advanced | 6 | Consonance, VL potential, complexity, functionality |

## Gielis Supershape
Chord embeddings decoded to 6 Gielis parameters [a, b, m, n1, n2, n3]:
- **m**: Rotational symmetry from consonance
- **n1**: Primary curvature from VL potential
- **n2**: Secondary curvature (dynamic tension)
- **n3**: Detail level from harmonic complexity
- **a, b**: Size from harmonic weight

## Training
- 5,000 songs, 100 epochs, 256-dim hidden, 8 attention heads
- Multi-objective loss: VL prediction + musical properties + Gielis consistency + manifold smoothness

## Relevance
Overkill for real-time use, but useful for:
- Validating our 6D approach (OPTIC features as ground truth)
- Porting Gielis supershape → GLSL for shape generation
- Interval consonance table (psychoacoustically validated)
