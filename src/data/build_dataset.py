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
    MONTHS_TO_FETCH,
    PROCESSED_POSTINGS_PATH,
    RAW_COMBINED_PATH,
    TECH_NOC_CODES,
)
from src.data.download import discover_monthly_urls, load_all


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    """Parse a date column that mixes yyyy-mm-dd and yyyy/mm/dd formats.

    Job Bank's exports aren't consistent about date format across months —
    letting pandas auto-infer the format silently turns some valid dates
    into NaT instead of raising, which quietly shrinks your date range
    without any error. Trying each known format explicitly avoids that.
    """
    parsed = pd.to_datetime(series, format="%Y-%m-%d", errors="coerce")

    still_missing = parsed.isna()
    if still_missing.any():
        parsed.loc[still_missing] = pd.to_datetime(
            series[still_missing], format="%Y/%m/%d", errors="coerce"
        )

    return parsed


def filter_tech_vancouver(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows that are both a tech NOC code and a Metro Vancouver location.

    Known data limitation: a small share of Job Bank postings have no City,
    Economic Region, or postal code at all — only a Province/Territory.
    There's no way to attribute these to Metro Vancouver specifically (vs.
    Victoria, Kelowna, etc. within BC), so they are excluded rather than
    guessed at. This function reports how many tech-NOC rows were dropped
    for this reason so the gap is visible, not silent.

    Note: matching on City name alone isn't safe on its own — some names
    aren't unique to BC (e.g. Richmond, Quebec; Delta, Ontario), so we also
    require Province/Territory == British Columbia as a second condition.
    """
    NOC_COL = "NOC21 Code"
    CITY_COL = "City"
    PROVINCE_COL = "Province/Territory"

    missing = [c for c in (NOC_COL, CITY_COL, PROVINCE_COL) if c not in df.columns]
    if missing:
        raise KeyError(
            f"Expected column(s) not found: {missing}. "
            f"Columns present: {list(df.columns)}"
        )

    df = df.copy()

    # NOC21 Code can come through as a float (e.g. 21231.0) if the column
    # has any missing values, so strip a trailing ".0" after stringifying.
    noc = df[NOC_COL].astype(str).str.strip()
    noc = noc.str.replace(r"\.0$", "", regex=True)
    is_tech = noc.isin(TECH_NOC_CODES)

    # Report (not silently drop) tech postings with no usable location data.
    tech_rows = df[is_tech]
    no_city = tech_rows[CITY_COL].isna()
    if no_city.any():
        print(
            f"Note: {no_city.sum():,} tech-NOC postings have no City "
            f"(and no Economic Region / postal code fallback available) — "
            f"excluded since they can't be confirmed as Metro Vancouver."
        )

    # City is already a clean municipality name (not a full address string),
    # so an exact match against our place list is more precise than a
    # substring search.
    city_lower = df[CITY_COL].astype(str).str.strip().str.lower()
    is_van_city = city_lower.isin(METRO_VANCOUVER_PLACES)

    # Second condition: require the province to actually be BC, to rule out
    # same-named municipalities in other provinces.
    province_lower = df[PROVINCE_COL].astype(str).str.strip().str.lower()
    is_bc = province_lower == "british columbia"

    # Sanity check: flag (don't silently drop) any city-name matches that
    # turned out NOT to be in BC — worth knowing if this ever fires.
    city_match_wrong_province = is_van_city & ~is_bc
    if city_match_wrong_province.any():
        offending = df.loc[city_match_wrong_province, [CITY_COL, PROVINCE_COL]]
        print(
            f"Note: {city_match_wrong_province.sum():,} rows matched a Metro "
            f"Vancouver city name but were NOT in British Columbia — excluded. "
            f"Examples:\n{offending.drop_duplicates().head()}"
        )

    filtered = df[is_tech & is_van_city & is_bc].copy()

    # Parse First Posting Date, handling the mixed yyyy-mm-dd / yyyy/mm/dd
    # formats present in the raw exports.
    DATE_COL = "First Posting Date"
    if DATE_COL in filtered.columns:
        filtered[DATE_COL] = parse_mixed_dates(filtered[DATE_COL])
        unparseable = filtered[DATE_COL].isna().sum()
        if unparseable:
            print(f"Note: {unparseable:,} rows have an unparseable {DATE_COL}.")

    return filtered


if __name__ == "__main__":
    urls = DIRECT_URLS if DIRECT_URLS else discover_monthly_urls(limit=MONTHS_TO_FETCH)

    raw = load_all(urls)
    print(f"Raw rows loaded: {len(raw):,}")
    raw.to_csv(RAW_COMBINED_PATH, index=False)  # cache raw before filtering

    tech_van = filter_tech_vancouver(raw)
    print(f"Vancouver tech postings after filtering: {len(tech_van):,}")

    tech_van.to_csv(PROCESSED_POSTINGS_PATH, index=False)
    print(f"Saved to {PROCESSED_POSTINGS_PATH}")