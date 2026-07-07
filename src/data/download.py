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


def fetch_csv(url: str) -> pd.DataFrame:
    """Download a single Job Bank monthly CSV and return it as a DataFrame."""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return pd.read_csv(io.StringIO(resp.text), low_memory=False)


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
    from config import DIRECT_URLS, RAW_COMBINED_PATH

    raw = load_all(DIRECT_URLS)
    print(f"Raw rows loaded: {len(raw):,}")
    raw.to_csv(RAW_COMBINED_PATH, index=False)
    print(f"Saved raw combined file to {RAW_COMBINED_PATH}")
