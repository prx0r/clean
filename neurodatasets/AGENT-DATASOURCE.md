# Neurodatasets — Agent Reference

For use by AI agents writing papers in the Trika–Consciousness-Science programme. This document lists every known data source, its access method, what was tested, and what actually works.

---

## 1. OpenNeuro (openneuro.org)

**Status:** ✅✅✅ **S3 direct access works. No auth required.** This is the primary method.

**What's there:** 1,000+ BIDS-formatted fMRI/EEG/MEG datasets, all publicly accessible.

### S3 Access Pattern (CONFIRMED WORKING)

```bash
# List dataset contents
aws s3 ls s3://openneuro.org/{DS_ID}/ --no-sign-request --region us-east-1

# Download entire dataset
aws s3 sync s3://openneuro.org/{DS_ID}/ ./target/ --no-sign-request --region us-east-1

# Download single subject
aws s3 sync s3://openneuro.org/{DS_ID}/sub-001/ ./sub-001/ --no-sign-request --region us-east-1

# Read dataset metadata
aws s3 cp s3://openneuro.org/{DS_ID}/dataset_description.json - --no-sign-request --region us-east-1
```

**Tested:** Downloaded 1 subject (319 MB) from ds001787 at ~100 MB/s. Real EEG data in BIDS format.

### Key Meditation/Consciousness Datasets Found

| Dataset | Name | Size | Modality |
|---------|------|------|----------|
| ds001787 | EEG meditation study (Delorme/Brandmeyer) | 5.7 GB | EEG |
| ds006644 | DMT + harmine during meditation (fMRI) | 125 GB | fMRI |
| ds007921 | Chakra Meditation fMRI | — | fMRI |
| ds004640 | Brainstem connectivity in human consciousness | — | fMRI |
| ds005365 | Altered states via high ventilation breathwork | — | fMRI |
| ds008064 | Mindfulness + rTMS for depression | — | fMRI |

### Finding More Datasets

Search via GitHub API:
```bash
curl -sL "https://api.github.com/search/repositories?q=meditation+org:OpenNeuroDatasets"
```

Replace `meditation` with: `mindfulness`, `consciousness`, `psychedelic`, `default+mode`, `nondual`, `self`, `attention`, `dmn`, `psilocybin`, `yoga`, `resting+state`.

### Quick Metadata Check

```bash
# Check dataset description
aws s3 cp "s3://openneuro.org/ds001787/dataset_description.json" - --no-sign-request --region us-east-1

# Get total size
aws s3 ls "s3://openneuro.org/ds001787/" --recursive --summarize --no-sign-request --region us-east-1
```

### URL Structure

- S3: `s3://openneuro.org/{DS_ID}/`
- HTTPS: `https://openneuro.org.s3.us-east-1.amazonaws.com/{DS_ID}/{file_path}`
- Web UI: `https://openneuro.org/datasets/{DS_ID}` (JS-heavy, not needed for download)

---

## 2. NeuroVault (neurovault.org)

**Status:** ✅ API works. Data quality varies.

**What's there:** Statistical brain maps (not raw data). Collections of group-level z-maps / t-maps from published studies.

**Agent access method:**
- API: `https://neurovault.org/api/collections/?search={term}` — search by keyword
- API: `https://neurovault.org/api/collections/{ID}/` — get collection details
- Download: `https://neurovault.org/collections/{ID}/download` — bulk download

**Tested results:**
- `search=meditation` → 17,627 results (too broad, includes any study with the word)
- `search=nondual` → 672,178 results (broken, returns everything)
- Collection 496 "meditation" → 1 image, no metadata (useless)
- Collection 2696 "self-regulation" → 124 images, no description (potential — needs exploration)
- Owner search for "Zoran Josipovic" → returns all collections, not filtered

**What works:** Searching by specific Cognitive Atlas terms or known collection IDs. The `/api/collections/` endpoint with exact ID works well. Search by keyword is noisy.

**Recommendation:** Search by known collection IDs from specific papers, not keyword search. If we find a Josipovic collection ID, the API will return the data cleanly.

---

## 3. Zenodo (zenodo.org)

**Status:** ✅ API works. But meditation/consciousness datasets are sparse.

**What's there:** General research data repository. Mostly supplementary materials, not organized datasets.

**Agent access method:**
- API: `https://zenodo.org/api/records?q={query}&file_type=dataset` — search
- Specific record by DOI: `https://zenodo.org/api/records/{doi}`

**Tested:**
- "meditation fMRI dataset" → only 5 results, all low quality
- "nirodha meditation" → 0 results
- "nondual awareness fMRI" → 0 results
- "psychedelic fMRI dataset" → 0 results

**Recommendation:** Use only when we have a known DOI to look up. Not useful for discovery.

---

## 4. OSF (osf.io)

**Status:**
API: `https://api.osf.io/v2/`. Not yet properly explored.

**What's there:** Pre-registrations with optional uploaded data. Many labs post raw data here before publishing.

**Potential:** Laukkonen's cessation (nirodha) data, Josipovic's nondual data, meditation studies with pre-registrations.

**Tested:**
- `filter[title]=nirodha` → 0 results
- `filter[description]=meditation` → no useful results

**Recommendation:** Needs more specific querying. Try searching by author name and known project titles.

---

## 5. Neurosynth (neurosynth.org)

**Status:**
API changed — old v1 endpoint returns 404.

**What it is:** 14,000+ fMRI studies with coordinate data, organized for meta-analysis. Not raw data, but statistical meta-analysis maps.

**Why useful:** Can generate whole-brain maps showing where the literature converges for any term (meditation, default mode, self, awareness). These are 3D statistical maps — excellent for video visualization.

**Agent access method (new):** The project evolved into NeuroQuery (neuroquery.org) and may have a different API now.

**Recommendation:** Worth checking if NeuroQuery has an API. If yes, we can programmatically generate meta-analysis maps for any term in our research programme.

---

## 6. Other Sources (not yet tested)

| Source | URL | What It Has | Access |
|--------|-----|-------------|--------|
| NeuroQuery | neuroquery.org | Text-based meta-analysis of 14k+ fMRI studies | Web UI; API unknown |
| DANDI | dandiarchive.org | Neurophysiology (ECoG, EEG, calcium imaging) | REST API + S3 |
| EBRAINS | ebrains.eu | EU brain data, some meditation/consciousness | Requires registration |
| HCP | humanconnectome.org | 1,200+ subjects, resting-state + task fMRI | Requires registration + data agreement |
| OpenfMRI (legacy) | openfmri.org | Merged into OpenNeuro | — |
| CONP | conp.ca | Canadian Open Neuroscience Platform | Open datasets |
| PhysioNet | physionet.org | Clinical physiological data, some EEG | REST API |

---

## Summary: What an Agent Should Actually Do

### For meta-analysis maps (best for video):
1. Try `neuroquery.org` API if available
2. Fallback: search NeuroVault by specific collection IDs from known papers

### For raw fMRI/EEG data (best for original analysis):
1. OpenNeuro datasets are the gold standard but need programmatic download
2. Use `openneuro-py` Python package or download via web UI
3. Known IDs to try: ds000171 (Brewer DMN), ds003554 (Hasenkamp), ds002815 (Loving-kindness), Cogitate data

### For pre-paper frontier data:
1. OSF — needs better querying by author name
2. Zenodo — useful only with known DOIs

### For brain maps from specific studies:
1. Check the paper's Data Availability Statement
2. Many papers post data on NeuroVault, Zenodo, or lab websites
3. Search by: "{Author} {year} supplementary data" or "{Author} {year} fMRI dataset"

---

## Known Gaps

No easily scriptable API was found that returns meditation/fMRI data directly. The datasets exist but are distributed across multiple platforms, each with different auth requirements. Best approach for an agent tasked with finding evidence for a specific paper:

1. Search OpenNeuro for the dataset ID
2. Check NeuroVault for statistical maps
3. Try OSF/Zenodo for supplementary data
4. If all else fails, the paper's supplementary materials are often on the journal website or the author's institutional page
