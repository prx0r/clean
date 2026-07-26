# Neurodatasets — Research Directive

## Mission

Find, document and access raw experimental datasets relevant to the Trika–Consciousness-Science research programme. Focus on frontier, pre-paper, unorganized data — things that haven't been fully analyzed yet and could produce visually compelling video content.

Priority: meditation fMRI/EEG > psychedelic > default mode > consciousness > nondual > cessation > attention > self-processing.

## Database Inventory

### OpenNeuro (openneuro.org)
- **Access:** REST API + direct download (NIfTI/TSV/BIDS)
- **Rate limit:** Unknown — website requires JS but raw files downloadable via S3
- **Query method:** GraphQL endpoint at openneuro.org/graphql (may need auth)
- **S3 access:** Files hosted on GIN or AWS — direct URLs pattern: `https://openneuro.org/crn/datasets/{DS}/versions/{VERSION}/`
- **Known relevant datasets:**
  - `ds000171` — Brewer DMN meditation (Yale, 12 experts/12 novices)
  - `ds003554` — Hasenkamp mind wandering (attention cycle)
  - `ds002815` — Loving-kindness meditation fMRI
  - `ds004215` — Psychedelic fMRI (psilocybin, Carhart-Harris lab)
  - `ds003151` — Default mode / task engagement
  - Cogitate Consortium adversarial test (IIT vs GNWT, Nature 2025) — 210 subjects, fMRI+MEG
- **Status:** TO EXPLORE — need to test download endpoints

### Neurosynth (neurosynth.org)
- **Access:** REST API
- **Rate limit:** Unknown, seems generous
- **Endpoints:**
  - `neurosynth.org/api/analyses/terms/?term={term}` — meta-analysis maps
  - `neurosynth.org/api/v2/data/{study_id}` — individual study data
  - Also has NeuroVault integration for statistical maps
- **Features:** 14,000+ fMRI studies, coordinate-based meta-analysis, topic modeling
- **Status:** NOT YET QUERIED — should try term searches for "meditation", "default mode", "self", "awareness"
- **Video potential:** Can generate 3D brain heat maps showing literature convergence

### NeuroVault (neurovault.org)
- **Access:** REST API
- **Rate limit:** Unknown
- **Endpoints:**
  - `neurovault.org/api/collections/?search={term}` — collections
  - `neurovault.org/api/images/?search={term}` — individual statistical maps
- **Status:** QUERIED ONCE — search for "meditation" returned 17,627 results (too broad)
- **Note:** Most collections have DOIs linking to papers, not raw data

### Zenodo (zenodo.org)
- **Access:** REST API
- **Rate limit:** Generous
- **Endpoints:**
  - `zenodo.org/api/records?q={query}&file_type=dataset`
- **Status:** QUERIED — search results mostly low quality for meditation/consciousness
- **Good for:** Specific known datasets by DOI

### OSF (Open Science Framework)
- **Access:** REST API at api.osf.io/v2/
- **Rate limit:** Unknown
- **Endpoints:**
  - `api.osf.io/v2/nodes/?filter[description]={term}`
- **Status:** NOT YET PROPERLY EXPLORED
- **Potential:** Pre-registrations with uploaded data but no paper yet

### GIN (G-Node Infrastructure, gin.g-node.org)
- **Access:** REST API
- **Status:** QUERIED ONCE — no useful results for "meditation"

### Other Sources
- **Kaggle:** Search "brain" / "EEG" / "fMRI" — some datasets
- **PhysioNet:** Clinical physiological data, some EEG
- **EBRAINS:** EU brain research platform
- **CONP:** Canadian Open Neuroscience Platform
- **DANDI:** DANDI Archive for neurophysiology (NWB format)
- **HCP:** Human Connectome Project (1,200+ subjects)

## Papers with Associated Data We Already Have

| Paper | Likely Data Location | Status |
|-------|---------------------|--------|
| Josipovic 2011 — Neural correlates of nondual awareness | NeuroVault / personal site | PDF owned |
| Josipovic 2014 — Neural correlates of nondual awareness (NYAS) | Unknown | PDF owned |
| Brewer 2011 — Meditation and DMN | OpenNeuro ds000171 | PDF owned |
| Farb 2007 — Attending to the present | OpenNeuro ds001787 | PDF owned |
| Hasenkamp 2012 — Mind wandering cycle | OpenNeuro ds003554 | PDF owned |
| Nath & Laukkonen 2026 — Meditation SNR | OSF? | PDF owned |
| Laukkonen 2023 — Cessations (nirodha) | OSF / Zenodo? | PDF owned |
| Millière 2018 — Psychedelics & self | OSF / Zenodo | PDF owned |
| Cogitate Consortium 2025 — IIT vs GNWT | OpenNeuro | Own Nature paper |

## Data Types by Video Potential

| Type | Format | Video Potential | Notes |
|------|--------|----------------|-------|
| fMRI BOLD | NIfTI (.nii) | HIGH — can render 3D brain volumes | Standard for meditation studies |
| EEG | .set / .edf / .fif | HIGH — can show waveforms + topographies | Good for cessation/alpha/theta |
| MEG | .fif | HIGH — better temporal resolution | Used in Cogitate test |
| Behavioral | .tsv / .csv | MEDIUM — reaction times, ratings | Needs good visualization |
| Meta-analysis maps | .nii (z-stats) | HIGH — show convergence across studies | Neurosynth exportable |
| Structural MRI | .nii | MEDIUM — VBM, cortical thickness | For long-term meditator studies |

## Next Steps

1. Query Neurosynth API for "meditation" meta-analysis map → download z-map → visualize
2. Test OpenNeuro direct download for ds000171 (Brewer DMN)
3. Search OSF for "nirodha" / "cessation" / "nondual" pre-registrations with data
4. Look at NeuroVault for Josipovic's specific statistical maps
5. Check if Cogitate Consortium data is downloadable from OpenNeuro
6. Document any rate limits encountered

## Notes

- OpenNeuro requires JS for the web UI but raw files may be directly accessible
- Neurosynth seems to have no strict rate limit
- Zenodo and OSF are generally very accessible
- Many labs post data to their own institutional repos — may need manual searching
