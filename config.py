"""
config.py — single source of truth for this project.

Every script under src/ imports from here instead of hardcoding NOC codes,
place names, or file paths. If it is required to add a NOC code, change a folder
location, or add a new month's URL, this is the only file you should need
to touch.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

# Make sure these exist even on a fresh clone (data/ folders are gitignored).
for d in (RAW_DIR, INTERIM_DIR, PROCESSED_DIR, MODELS_DIR, FIGURES_DIR):
    d.mkdir(parents=True, exist_ok=True)

RAW_COMBINED_PATH = RAW_DIR / "combined_raw.csv"
PROCESSED_POSTINGS_PATH = PROCESSED_DIR / "vancouver_tech_postings.csv"

# ---------------------------------------------------------------------------
# Job Bank open data
# ---------------------------------------------------------------------------

# Dataset landing page (for reference):
# https://open.canada.ca/data/en/dataset/ea639e28-c0fc-48bf-b5dd-b8899bd43072
#
# By default, URLs are auto-discovered from the CKAN API (see
# src/data/download.py: discover_monthly_urls). MONTHS_TO_FETCH controls
# how many of the most recent months to pull.
MONTHS_TO_FETCH: int = 24

# Leave this empty to use auto-discovery. If it is required to pin specific
# files (e.g. a manually-verified list, or months auto-discovery misses),
# populate this list instead. It takes priority over MONTHS_TO_FETCH.
DIRECT_URLS: list[str] = [
    # "https://open.canada.ca/data/dataset/.../download/job-bank-open-data-all-job-postings-en-apr2026.csv",
]

# ---------------------------------------------------------------------------
# Filtering criteria
# ---------------------------------------------------------------------------

# Tech-related NOC 2021 codes.
TECH_NOC_CODES: set[str] = {
    "21211",  # Data scientists
    "21230",  # Computer systems developers and programmers
    "21231",  # Software engineers and designers
    "21232",  # Software developers and programmers
    "21233",  # Web designers
    "21234",  # Web developers and programmers
    "21220",  # Cybersecurity specialists
    "21221",  # Business systems specialists
    "21222",  # Information systems specialists
    "21223",  # Database analysts and data administrators
    "21311",  # Computer engineers (except software engineers and designers)
    "22220",  # Computer network and web technicians
    "20012",  # Computer and information systems managers
}

# Human-readable labels, useful for chart legends later.
NOC_LABELS: dict[str, str] = {
    "21211": "Data scientists",
    "21230": "Computer systems developers/programmers",
    "21231": "Software engineers and designers",
    "21232": "Software developers and programmers",
    "21233": "Web designers",
    "21234": "Web developers and programmers",
    "21220": "Cybersecurity specialists",
    "21221": "Business systems specialists",
    "21222": "Information systems specialists",
    "21223": "Database analysts and data administrators",
    "21311": "Computer engineers (except software engineers and designers)",
    "22220": "Computer network and web technicians",
    "20012": "Computer and information systems managers",
}

# Metro Vancouver municipalities — matched as substrings against the
# (free-text) location field, case-insensitive.
METRO_VANCOUVER_PLACES: list[str] = [
    "vancouver", "burnaby", "richmond", "surrey", "coquitlam",
    "north vancouver", "west vancouver", "new westminster", "delta",
    "langley", "port coquitlam", "port moody", "maple ridge",
    "white rock", "pitt meadows",
]
