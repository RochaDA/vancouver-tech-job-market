# Vancouver Tech Job Market

A three-stage portfolio project analyzing the tech job market in Metro
Vancouver, using Job Bank Canada's open postings data.

- **Stage 1 — Data Analysis:** clean the data, explore trends, build a dashboard.
- **Stage 2 — Data Science:** wage prediction, time-series forecasting of postings volume.
- **Stage 3 — AI/ML:** NLP on job descriptions — skill extraction, role clustering, resume matching.

## Data source

[Job Bank Canada — Job Postings open data](https://open.canada.ca/data/en/dataset/ea639e28-c0fc-48bf-b5dd-b8899bd43072)
(monthly CSVs, updated by Employment and Social Development Canada).

## Setup

```bash
conda env create -f environment.yml
conda activate tech-jobs
```

To update the environment later after adding a dependency to `environment.yml`:

```bash
conda env update -f environment.yml --prune
```


## Building the dataset

1. Open the [dataset page](https://open.canada.ca/data/en/dataset/ea639e28-c0fc-48bf-b5dd-b8899bd43072)
   and copy the CSV link for each month you want.
2. Paste those URLs into `DIRECT_URLS` in `config.py`.
3. Run the pipeline:

```bash
python -m src.data.build_dataset
```

This downloads each month, caches the raw combined file in `data/raw/`,
filters to tech-related NOC codes + Metro Vancouver locations, and saves
the result to `data/processed/vancouver_tech_postings.csv`.

## Project structure

```
config.py               # single source of truth: NOC codes, place names, paths
src/
├── data/                # download + filter/clean pipeline
├── analysis/            # Stage 1: EDA
├── models/              # Stage 2: wage prediction, forecasting
└── nlp/                 # Stage 3: skill extraction, clustering, matching
notebooks/               # exploratory work, numbered by stage
data/{raw,interim,processed}/
reports/{figures,dashboard}/
```

## Status

- [x] Data pipeline (download + filter)
- [ ] Stage 1: EDA + dashboard
- [ ] Stage 2: wage model + forecasting
- [ ] Stage 3: NLP skill extraction + matching
