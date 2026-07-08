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
conda activate vancouver-tech-jobs
```

To update the environment later after adding a dependency to `environment.yml`:

```bash
conda env update -f environment.yml --prune
```


## Building the dataset

URLs are auto-discovered from the dataset's CKAN API — no manual copy-pasting
needed. Just set how many recent months you want in `config.py`:

```python
MONTHS_TO_FETCH: int = 24
```

Then run the pipeline:

```bash
python -m src.data.build_dataset
```

This calls the [CKAN API](https://open.canada.ca/data/api/action/package_show?id=ea639e28-c0fc-48bf-b5dd-b8899bd43072)
to find the most recent English-language CSV files, downloads each month,
caches the raw combined file in `data/raw/`, filters to tech-related NOC
codes + Metro Vancouver locations, and saves the result to
`data/processed/vancouver_tech_postings.csv`.

If you ever need to pin specific files instead (e.g. auto-discovery misses
a month), populate `DIRECT_URLS` in `config.py` — it takes priority over
`MONTHS_TO_FETCH` when non-empty.

### Known data limitation

A small share of Job Bank postings have no `City`, `Economic Region`, or
postal code at all — only a coarse `Province/Territory`. There's no way to
confirm whether these are in Metro Vancouver specifically (vs. Victoria,
Kelowna, etc. within BC), so they're excluded from the filtered dataset
rather than guessed at. The pipeline prints how many tech-NOC postings this
affects each run, so the gap is visible rather than silent.

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
