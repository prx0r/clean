# Music Theory 3: CHORDONOMICON 6D Graph Extraction

## Source
CHORDONOMICON dataset: 666,000 songs, avg 6.82 nodes, 13.71 edges per track.
arXiv:2410.22046

## Core Insight
Chord progressions are weighted directed graphs. Graph metrics directly encode musical-emotional structure. No complex harmonic analysis needed.

## The 6D Vector
| D | Feature | Theory | Graph Metric |
|---|---------|--------|--------------|
| 1 | Chord geometry | Tymoczko | Weighted avg edge distance in chord space |
| 2 | Voice leading smoothness | Tymoczko | Inverse of avg semitone movement |
| 3 | Harmonic flow | Tymoczko | PageRank centrality variance |
| 4 | Harmonic consonance | QRI/STV | Degree-weighted chord consonance |
| 5 | Rhythmic regularity | QRI | Edge weight distribution uniformity |
| 6 | Information entropy | QRI | Combined structural + harmonic entropy |

## Performance
- O(n+m) graph algorithms on avg 6.82 nodes/track
- 666k tracks processed in minutes
- Runtime k-NN search: O(k) where k=50

## Rasa → 6D Signatures (Proposed)
| Rasa | D1 geom | D2 VL | D3 flow | D4 cons | D5 rhythm | D6 entropy |
|------|---------|-------|---------|---------|-----------|------------|
| Śānta | low | high | high | high | high | low |
| Raudra | high | low | low | low | low | high |
| Adbhuta | mid | mid | high | mid | mid | mid |
| Śṛṅgāra | low | high | mid | high | mid | low |
| Vīra | mid | mid | mid | mid | mid | mid |
| Bhayānaka | high | low | low | low | low | high |
| Karuṇā | low | mid | mid | mid | low | mid |
| Hāsya | mid | low | mid | mid | high | mid |
| Bībhatsa | high | low | low | low | low | high |
