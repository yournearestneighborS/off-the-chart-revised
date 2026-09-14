"""Build public, analysis-ready features from local source files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import CHART_DATES, YEARS
from .genres import apply_genre_overrides
from .quality import audit_chart_pipeline
from .sentiment import score_lyrics_by_line
from .sentiment import sentiment_label
from .text import clean_lyrics, lexical_features, lyric_quality_flags


def build_song_features(project_root: Path, analyzer=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return a song-level feature table and a year-level audit table.

    Full lyrics are read from `data/private` but deliberately excluded from the
    returned table so the public repository contains derived features only.
    """
    overrides = pd.read_csv(project_root / "data" / "reference" / "genre_overrides.csv")
    feature_frames: list[pd.DataFrame] = []
    audits: list[dict[str, int | float]] = []

    for year in YEARS:
        chart = pd.read_csv(project_root / "data" / "raw" / "charts" / f"hot100_{year}.csv")
        genres = pd.read_csv(
            project_root / "data" / "interim" / "genres" / f"hot100_{year}_with_genres.csv"
        )
        lyrics_path = project_root / "data" / "private" / f"lyrics_{year}_data.csv"
        if not lyrics_path.exists():
            raise FileNotFoundError(
                f"Missing private lyric input: {lyrics_path}. See data/private/README.md."
            )
        lyrics = pd.read_csv(lyrics_path)
        audits.append(audit_chart_pipeline(chart, genres, lyrics, year))

        frame = chart.merge(
            genres[["title", "artist", "genre"]],
            on=["title", "artist"],
            how="left",
            validate="one_to_one",
        ).rename(columns={"genre": "raw_genre"})
        frame = frame.merge(
            lyrics[["song_title", "artist", "lyrics"]].rename(columns={"song_title": "title"}),
            on=["title", "artist"],
            how="left",
            validate="one_to_one",
        )

        legacy_path = project_root / "data" / "private" / f"lyrics_with_sentiment_{year}.csv"
        if legacy_path.exists():
            legacy = pd.read_csv(legacy_path).rename(
                columns={
                    "simplified_genre": "legacy_simplified_genre",
                    "vader_sentiment": "vader_fulltext_score",
                    "textblob_sentiment": "textblob_fulltext_score",
                    "sentiment_label": "vader_fulltext_label",
                }
            )
            frame = frame.merge(
                legacy[[
                    "song_title", "artist", "legacy_simplified_genre",
                    "vader_fulltext_score", "textblob_fulltext_score", "vader_fulltext_label",
                ]].rename(columns={"song_title": "title"}),
                on=["title", "artist"],
                how="left",
                validate="one_to_one",
            )
            frame["textblob_fulltext_label"] = frame["textblob_fulltext_score"].map(
                lambda value: sentiment_label(float(value)) if pd.notna(value) else "not_scored"
            )
            frame["model_agreement"] = (
                frame["vader_fulltext_label"] == frame["textblob_fulltext_label"]
            ) & frame["vader_fulltext_label"].notna()
        frame.insert(0, "year", year)
        frame.insert(1, "chart_date", CHART_DATES[year])
        frame = apply_genre_overrides(frame, overrides)

        quality_rows = [lyric_quality_flags(value) for value in frame["lyrics"]]
        lexical_rows = [lexical_features(value) for value in frame["lyrics"]]
        quality = pd.DataFrame(quality_rows, index=frame.index)
        lexical = pd.DataFrame(lexical_rows, index=frame.index)
        frame = pd.concat([frame, quality, lexical], axis=1)
        frame["lyrics_available"] = frame["lyrics"].notna()
        frame["rank_weight"] = 101 - frame["rank"]

        if analyzer is not None:
            cleaned = frame["lyrics"].map(clean_lyrics)
            sentiment = pd.DataFrame(
                [score_lyrics_by_line(value, analyzer) for value in cleaned],
                index=frame.index,
            )
            frame = pd.concat([frame, sentiment], axis=1)

        # Do not publish raw or cleaned lyrics in the derived feature table.
        frame = frame.drop(columns=["lyrics"])
        feature_frames.append(frame)

    features = pd.concat(feature_frames, ignore_index=True)
    audit = pd.DataFrame(audits)
    return features, audit


def build_quality_issues(features: pd.DataFrame) -> pd.DataFrame:
    """Create a human-readable exception table for the README and notebook."""
    issues: list[dict[str, object]] = []
    for _, row in features.iterrows():
        if not row["lyrics_available"]:
            issues.append({
                "year": row["year"], "rank": row["rank"], "title": row["title"],
                "artist": row["artist"], "issue": "lyrics_not_retrieved"
            })
        if row["genre_review_status"] in {"manual_override", "missing"}:
            issues.append({
                "year": row["year"], "rank": row["rank"], "title": row["title"],
                "artist": row["artist"], "issue": f"genre_{row['genre_review_status']}"
            })
    return pd.DataFrame(issues).sort_values(["year", "rank", "issue"]).reset_index(drop=True)
