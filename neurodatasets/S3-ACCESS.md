# OpenNeuro S3 Access — Working!

All OpenNeuro datasets are publicly accessible via AWS S3 with **no authentication required**.

## Base Pattern

```
s3://openneuro.org/{DS_ID}/
```

## Commands

### List dataset contents
```bash
aws s3 ls s3://openneuro.org/ds000171/ --no-sign-request --region us-east-1
```

### Download entire dataset
```bash
aws s3 sync s3://openneuro.org/ds000171/ ./ds000171/ --no-sign-request --region us-east-1
```

### Download single subject
```bash
aws s3 sync s3://openneuro.org/ds000171/sub-control01/ ./sub-control01/ --no-sign-request --region us-east-1
```

### Read dataset metadata
```bash
aws s3 cp s3://openneuro.org/ds000171/dataset_description.json - --no-sign-request --region us-east-1
```

## Confirmed Accessible Datasets

| ID | Name | Size |
|----|------|------|
| ds000171 | Brewer DMN — Neural Processing of Emotional Stimuli in Depression | 6.9 GiB |
| ds003554 | Visser et al. 2015 Psychoneuroendocrinology | — |
| ds004215 | Psilocybin fMRI (Carhart-Harris) | — |
| ds003151 | Stress-associated brain activation | — |
| ds003768 | Simultaneous EEG+fMRI during sleep | — |

## How Hermes Found This

Hermes used its browser automation to navigate OpenNeuro's JS-heavy web UI, identified that datasets are hosted on AWS S3 as Open Data, and extracted the access pattern. The result: `s3://openneuro.org/{DS_ID}/` with `--no-sign-request`.

## Next Steps

1. Find the right dataset IDs for: Brewer DMN meditation, Hasenkamp mind wandering, Farb self-reference, Josipovic nondual, Laukkonen cessation
2. Write a Hermes skill to automate: given a paper DOI → find associated OpenNeuro dataset → download via S3
3. Cogitate Consortium adversarial test data — find where it's hosted
