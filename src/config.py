from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_MUNICIPALITIES_PATH = BASE_DIR / "data" / "raw" / "al_municipios_base.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SAMPLE_PATH = PROCESSED_DIR / "cadunico_sample.csv"
MUNICIPAL_PROFILE_PATH = PROCESSED_DIR / "municipal_profile.csv"
SUMMARY_PATH = PROCESSED_DIR / "summary.json"
YEAR_REFERENCE = 2018
