"""Generate analysis tables and portfolio-ready figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from offthechart.analysis import bootstrap_difference, summarize_genres, summarize_years


PALETTE = {
    1965: "#375A7F",
    1985: "#4C956C",
    2005: "#F2A65A",
    2025: "#C8553D",
}


def save_figure(fig: plt.Figure, name: str) -> None:
    output = PROJECT_ROOT / "reports" / "figures" / name
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    data = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "song_features.csv")
    summary = summarize_years(data)
    genres = summarize_genres(data, minimum_songs=5)
    output_dir = PROJECT_ROOT / "data" / "processed"
    summary.to_csv(output_dir / "year_summary.csv", index=False)
    genres.to_csv(output_dir / "genre_summary.csv", index=False)

    prior = data[data["year"].lt(2025)]
    current = data[data["year"].eq(2025)]
    comparisons = []
    for metric in ("vader_fulltext_score", "textblob_fulltext_score"):
        difference, low, high = bootstrap_difference(
            current[metric], prior[metric], seed=510 if metric.startswith("vader") else 511
        )
        comparisons.append(
            {"comparison": "2025 minus 1965–2005 pooled", "metric": metric,
             "mean_difference": difference, "ci_low": low, "ci_high": high}
        )
    pd.DataFrame(comparisons).to_csv(output_dir / "sentiment_comparisons.csv", index=False)

    sns.set_theme(style="whitegrid", context="notebook")
    years = summary["year"].astype(int).tolist()
    colors = [PALETTE[year] for year in years]

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    coverage = summary["lyric_coverage_pct"]
    bars = ax.bar([str(y) for y in years], coverage, color=colors, width=0.64)
    ax.set(title="Lyric coverage is high but not identical", xlabel="Chart snapshot", ylabel="Songs with retrieved lyrics (%)", ylim=(0, 105))
    ax.bar_label(bars, labels=[f"{value:.0f}%" for value in coverage], padding=3)
    ax.text(0.01, -0.2, "Note: the 2025 source chart contains 99 ranks; the other snapshots contain 100.", transform=ax.transAxes, fontsize=9, color="#555555")
    sns.despine(fig)
    save_figure(fig, "01_lyric_coverage.png")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharex=True)
    for ax, metric, low_col, high_col, title, ylabel in (
        (axes[0], "vader_mean", "vader_ci_low", "vader_ci_high", "VADER full-text score", "Mean compound score"),
        (axes[1], "textblob_mean", "textblob_ci_low", "textblob_ci_high", "TextBlob full-text score", "Mean polarity"),
    ):
        means = summary[metric].to_numpy()
        lower = means - summary[low_col].to_numpy()
        upper = summary[high_col].to_numpy() - means
        ax.errorbar(years, means, yerr=np.vstack([lower, upper]), fmt="o-", color="#243B53", ecolor="#829AB1", capsize=4, lw=2, ms=7)
        ax.axhline(0, color="#9FB3C8", lw=1)
        ax.set(title=title, xlabel="Chart snapshot", ylabel=ylabel, xticks=years)
    fig.suptitle("Both models score the 2025 snapshot lower", y=1.03, fontsize=15, fontweight="bold")
    fig.text(0.01, -0.02, "Points are sample means; bars are 95% bootstrap intervals. These are four weekly snapshots, not annual samples.", fontsize=9, color="#555555")
    sns.despine(fig)
    save_figure(fig, "02_sentiment_by_year.png")

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    bars = ax.bar([str(y) for y in years], summary["model_agreement_pct"], color=colors, width=0.64)
    ax.set(title="The two sentiment models agree less often in 2025", xlabel="Chart snapshot", ylabel="Same positive/neutral/negative label (%)", ylim=(0, 80))
    ax.bar_label(bars, labels=[f"{value:.0f}%" for value in summary["model_agreement_pct"]], padding=3)
    ax.text(0.01, -0.2, "Lower agreement makes strong claims about the exact sentiment label less defensible.", transform=ax.transAxes, fontsize=9, color="#555555")
    sns.despine(fig)
    save_figure(fig, "03_model_agreement.png")

    composition = pd.crosstab(data["simplified_genre"], data["year"], normalize="columns") * 100
    top = data["simplified_genre"].value_counts().head(8).index
    composition = composition.loc[top]
    fig, ax = plt.subplots(figsize=(9.4, 5.7))
    sns.heatmap(composition, annot=True, fmt=".0f", cmap="Blues", cbar_kws={"label": "% of chart snapshot"}, ax=ax)
    ax.set(title="Genre mix differs sharply across the four chart weeks", xlabel="Chart snapshot", ylabel="Broad genre")
    fig.text(0.01, -0.01, "Broad genres use rule-based mappings plus documented manual corrections. Values are shares of each chart snapshot.", fontsize=9, color="#555555")
    save_figure(fig, "04_genre_mix.png")

    print(f"Wrote {len(summary)} year summaries, {len(genres)} genre summaries, and 4 figures.")


if __name__ == "__main__":
    main()
