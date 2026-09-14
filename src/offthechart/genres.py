"""Broad, auditable genre grouping for cross-era comparison."""

from __future__ import annotations

import re

import pandas as pd


GENRE_RULES = (
    ("Christian", r"christian|gospel|worship"),
    ("Latin", r"latin|reggaeton|urbano|corrido|m[úu]sica mexicana|sierre[nñ]o|banda"),
    ("Hip-Hop", r"hip[ -]?hop|\brap\b|trap|crunk|drill|g-funk"),
    ("R&B/Soul", r"r&b|rnb|soul|motown|quiet storm|new jack swing|funk"),
    ("Metal", r"metal|metalcore"),
    ("Alternative", r"alternative|indie|grunge|emo|punk"),
    ("Rock", r"rock|rockabilly|new wave|synthpop|hi-nrg"),
    ("Country", r"country"),
    ("Dance/Electronic", r"dance|electronic|edm|house|trance|disco|freestyle"),
    ("Jazz", r"jazz|bossa nova|big band|swing"),
    ("Folk", r"folk|singer.songwriter"),
    ("Pop", r"pop|adult standards|doo-wop"),
)


def simplify_genre(raw_genre: object) -> str:
    """Map a source genre string into a stable cross-era category."""
    if not isinstance(raw_genre, str) or not raw_genre.strip():
        return "Unknown"
    normalized = raw_genre.casefold()
    for label, pattern in GENRE_RULES:
        if re.search(pattern, normalized):
            return label
    return "Other"


def apply_genre_overrides(
    data: pd.DataFrame, overrides: pd.DataFrame
) -> pd.DataFrame:
    """Apply documented song-level corrections without hiding source values."""
    required = {"year", "title", "artist", "corrected_genre", "reason"}
    missing = required.difference(overrides.columns)
    if missing:
        raise ValueError(f"Genre override file is missing columns: {sorted(missing)}")

    result = data.copy()
    result["simplified_genre"] = result["raw_genre"].map(simplify_genre)
    result["genre_review_status"] = "rule_based"
    result["genre_review_note"] = ""

    lookup = overrides.set_index(["year", "title", "artist"])
    for idx, row in result.iterrows():
        key = (int(row["year"]), row["title"], row["artist"])
        if key in lookup.index:
            correction = lookup.loc[key]
            result.at[idx, "simplified_genre"] = correction["corrected_genre"]
            result.at[idx, "genre_review_status"] = "manual_override"
            result.at[idx, "genre_review_note"] = correction["reason"]
        elif not isinstance(row["raw_genre"], str) or not row["raw_genre"].strip():
            result.at[idx, "genre_review_status"] = "missing"
            result.at[idx, "genre_review_note"] = "No genre returned by source APIs."
    return result

