"""Reusable summaries for the portfolio analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    """Return a weighted mean after removing incomplete pairs."""
    mask = values.notna() & weights.notna()
    if not mask.any():
        return float("nan")
    return float(np.average(values[mask], weights=weights[mask]))


def bootstrap_mean_ci(
    values: pd.Series,
    *,
    confidence: float = 0.95,
    iterations: int = 5_000,
    seed: int = 510,
) -> tuple[float, float]:
    """Return a non-parametric confidence interval for a sample mean."""
    sample = values.dropna().to_numpy(dtype=float)
    if sample.size < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    draws = rng.choice(sample, size=(iterations, sample.size), replace=True).mean(axis=1)
    alpha = (1 - confidence) / 2
    return tuple(np.quantile(draws, [alpha, 1 - alpha]).astype(float))


def summarize_years(features: pd.DataFrame) -> pd.DataFrame:
    """Create a concise year-level table for the notebook and README."""
    rows: list[dict[str, object]] = []
    for year, group in features.groupby("year", sort=True):
        scored = group.dropna(subset=["vader_fulltext_score", "textblob_fulltext_score"])
        vader_low, vader_high = bootstrap_mean_ci(scored["vader_fulltext_score"], seed=int(year))
        blob_low, blob_high = bootstrap_mean_ci(
            scored["textblob_fulltext_score"], seed=int(year) + 1
        )
        rows.append(
            {
                "year": int(year),
                "chart_date": group["chart_date"].iloc[0],
                "chart_songs": len(group),
                "lyrics_scored": len(scored),
                "lyric_coverage_pct": 100 * len(scored) / len(group),
                "vader_mean": scored["vader_fulltext_score"].mean(),
                "vader_ci_low": vader_low,
                "vader_ci_high": vader_high,
                "vader_positive_pct": 100
                * scored["vader_fulltext_label"].eq("positive").mean(),
                "vader_saturated_pct": 100
                * scored["vader_fulltext_score"].abs().ge(0.9).mean(),
                "textblob_mean": scored["textblob_fulltext_score"].mean(),
                "textblob_ci_low": blob_low,
                "textblob_ci_high": blob_high,
                "model_agreement_pct": 100 * scored["model_agreement"].mean(),
                "rank_weighted_vader_mean": weighted_mean(
                    scored["vader_fulltext_score"], scored["rank_weight"]
                ),
                "rank_weighted_textblob_mean": weighted_mean(
                    scored["textblob_fulltext_score"], scored["rank_weight"]
                ),
            }
        )
    return pd.DataFrame(rows)


def summarize_genres(features: pd.DataFrame, minimum_songs: int = 5) -> pd.DataFrame:
    """Summarize genre results while marking groups too small to interpret."""
    scored = features.dropna(subset=["vader_fulltext_score", "textblob_fulltext_score"])
    result = (
        scored.groupby(["year", "simplified_genre"], as_index=False)
        .agg(
            songs=("title", "size"),
            vader_mean=("vader_fulltext_score", "mean"),
            textblob_mean=("textblob_fulltext_score", "mean"),
        )
        .rename(columns={"simplified_genre": "genre"})
    )
    result["meets_minimum"] = result["songs"].ge(minimum_songs)
    return result.sort_values(["year", "songs", "genre"], ascending=[True, False, True])


def bootstrap_difference(
    first: pd.Series,
    second: pd.Series,
    *,
    iterations: int = 10_000,
    seed: int = 510,
) -> tuple[float, float, float]:
    """Return mean(first)-mean(second) and its 95% bootstrap interval."""
    a = first.dropna().to_numpy(dtype=float)
    b = second.dropna().to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    differences = (
        rng.choice(a, size=(iterations, a.size), replace=True).mean(axis=1)
        - rng.choice(b, size=(iterations, b.size), replace=True).mean(axis=1)
    )
    low, high = np.quantile(differences, [0.025, 0.975])
    return float(a.mean() - b.mean()), float(low), float(high)
