"""
src/data/download.py

Fetches Job Bank's monthly open-data CSV files and concatenates them into
one raw DataFrame. Knows nothing about NOC codes or Vancouver — that logic
lives in build_dataset.py, so this module stays reusable if you ever want
a different city or industry.
"""

import io
import time

import pandas as pd
import requests

CKAN_PACKAGE_URL = (
    "https://open.canada.ca/data/api/action/package_show"
    "?id=ea639e28-c0fc-48bf-b5dd-b8899bd43072"
)


def discover_monthly_urls(language: str = "en", limit: int | None = None) -> list[str]:
    """
    Auto-discover monthly CSV download URLs from the CKAN dataset API,
    instead of copy-pasting them by hand from the webpage.

    language: "en" or "fr" — the dataset publishes both, keep to one to
              avoid double-counting the same postings.
    limit:    if set, only return the first `limit` URLs found (the API
              returns resources newest-first, so this gives you the most
              recent N months).
    """
    resp = requests.get(CKAN_PACKAGE_URL, timeout=30)
    resp.raise_for_status()
    resources = resp.json()["result"]["resources"]

    urls = [
        r["url"]
        for r in resources
        if r.get("format") == "CSV" and language in (r.get("language") or []) and r.get("url")
    ]

    if limit is not None:
        urls = urls[:limit]

    print(f"Discovered {len(urls)} '{language}' CSV file(s) from the CKAN API.")
    return urls


def fetch_csv(url: str) -> pd.DataFrame:
    """Download a single Job Bank monthly CSV and return it as a DataFrame.

    Job Bank's export format isn't consistent across months: recent files
    are UTF-16 + tab-delimited, but older files use a different
    encoding/delimiter. Trying the wrong combination doesn't always raise
    an error — pandas can silently parse it into garbled columns — so we
    try known combinations in order and VALIDATE that the result actually
    has the columns we expect before accepting it.
    """
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    raw = resp.content

    attempts = [
        ("utf-16", "\t"),
        ("utf-8-sig", ","),
        ("utf-8", ","),
        ("cp1252", ","),
        ("latin-1", ","),
    ]

    last_err = None
    for encoding, sep in attempts:
        try:
            df = pd.read_csv(io.BytesIO(raw), encoding=encoding, sep=sep, low_memory=False)
        except Exception as e:
            last_err = e
            continue

        df.columns = df.columns.str.strip().str.replace(r"\s+", " ", regex=True)

        # A correct parse should have many columns including the two we
        # rely on downstream. Anything else is treated as a failed attempt,
        # not silently accepted.
        if df.shape[1] > 5 and "NOC21 Code" in df.columns and "City" in df.columns:
            return df

        last_err = RuntimeError(
            f"Parsed with encoding={encoding!r} sep={sep!r} but got "
            f"{df.shape[1]} column(s) and missing expected headers; "
            f"first columns: {list(df.columns)[:5]}"
        )

    raise RuntimeError(f"Could not parse CSV from {url}: {last_err}")


def load_all(urls: list[str], pause_seconds: float = 1.0) -> pd.DataFrame:
    """Download each URL in turn and concatenate into a single DataFrame."""
    frames = []
    for url in urls:
        print(f"Downloading: {url}")
        try:
            frames.append(fetch_csv(url))
        except Exception as e:
            print(f"  Failed: {e}")
        time.sleep(pause_seconds)  # be polite to the server

    if not frames:
        raise RuntimeError("No files downloaded — check the URL list in config.py.")

    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    # Lets you run `python -m src.data.download` on its own to just refresh
    # the raw cache, without re-running the filtering step.
    from config import DIRECT_URLS, MONTHS_TO_FETCH, RAW_COMBINED_PATH

    urls = DIRECT_URLS if DIRECT_URLS else discover_monthly_urls(limit=MONTHS_TO_FETCH)

    raw = load_all(urls)
    print(f"Raw rows loaded: {len(raw):,}")
    raw.to_csv(RAW_COMBINED_PATH, index=False)
    print(f"Saved raw combined file to {RAW_COMBINED_PATH}")
