"""
src/data/build_dataset.py

Filters the raw Job Bank data down to tech-related NOC codes in Metro
Vancouver, cleans it, and saves the analysis-ready CSV. Run this file
directly to execute the full pipeline (download -> filter -> save).
"""

import pandas as pd

from config import (
    DIRECT_URLS,
    METRO_VANCOUVER_PLACES,
    PROCESSED_POSTINGS_PATH,
    RAW_COMBINED_PATH,
    TECH_NOC_CODES,
)
from src.data.download import load_all


def filter_tech_vancouver(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows that are both a tech NOC code and a Metro Vancouver location."""
    print("Columns found in raw data:", list(df.columns))

    # Column names are best guesses based on the published schema — if these
    # don't match, print(df.columns) above will show you the real names.
    noc_col = next((c for c in df.columns if "noc" in c.lower()), None)
    location_col = next(
        (c for c in df.columns if "location" in c.lower() or "city" in c.lower()), None
    )

    if noc_col is None or location_col is None:
        raise KeyError(
            "Could not auto-detect NOC / location columns — inspect df.columns "
            "and set noc_col / location_col manually."
        )

    df = df.copy()
    df[noc_col] = df[noc_col].astype(str).str.strip()
    is_tech = df[noc_col].isin(TECH_NOC_CODES)

    location_lower = df[location_col].astype(str).str.lower()
    is_van = location_lower.apply(
        lambda loc: any(place in loc for place in METRO_VANCOUVER_PLACES)
    )

    return df[is_tech & is_van].copy()


if __name__ == "__main__":
    if not DIRECT_URLS:
        raise SystemExit(
            "Add at least one monthly CSV URL to DIRECT_URLS in config.py before running.\n"
            "Grab them from: https://open.canada.ca/data/en/dataset/"
            "ea639e28-c0fc-48bf-b5dd-b8899bd43072"
        )

    raw = load_all(DIRECT_URLS)
    print(f"Raw rows loaded: {len(raw):,}")
    raw.to_csv(RAW_COMBINED_PATH, index=False)  # cache raw before filtering

    tech_van = filter_tech_vancouver(raw)
    print(f"Vancouver tech postings after filtering: {len(tech_van):,}")

    tech_van.to_csv(PROCESSED_POSTINGS_PATH, index=False)
    print(f"Saved to {PROCESSED_POSTINGS_PATH}")
