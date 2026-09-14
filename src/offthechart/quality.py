"""Coverage and integrity checks for each stage of the project pipeline."""

from __future__ import annotations

import pandas as pd


def audit_chart_pipeline(
    chart: pd.DataFrame,
    genres: pd.DataFrame,
    lyrics: pd.DataFrame,
    year: int,
) -> dict[str, int | float]:
    """Measure chart completeness, metadata coverage, and lyric retrieval coverage."""
    chart_keys = set(zip(chart["title"], chart["artist"]))
    genre_keys = set(zip(genres["title"], genres["artist"]))
    lyric_keys = set(zip(lyrics["song_title"], lyrics["artist"]))
    chart_rows = len(chart)
    return {
        "year": year,
        "chart_rows": chart_rows,
        "unique_ranks": int(chart["rank"].nunique()),
        "missing_chart_positions": max(0, 100 - chart_rows),
        "duplicate_chart_keys": int(chart.duplicated(["title", "artist"]).sum()),
        "genre_rows_matched": len(chart_keys & genre_keys),
        "genres_missing": int(genres["genre"].isna().sum()),
        "lyrics_retrieved": len(chart_keys & lyric_keys),
        "lyrics_missing": len(chart_keys - lyric_keys),
        "lyric_coverage_pct": len(chart_keys & lyric_keys) / chart_rows * 100 if chart_rows else 0.0,
    }

