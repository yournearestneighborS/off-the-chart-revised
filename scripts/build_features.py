"""Build public song features and pipeline-quality summaries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from offthechart.pipeline import build_quality_issues, build_song_features


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-sentiment",
        action="store_true",
        help="Calculate line-level VADER metrics. Requires NLTK and its vader_lexicon.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analyzer = None
    if args.with_sentiment:
        from nltk.sentiment import SentimentIntensityAnalyzer

        analyzer = SentimentIntensityAnalyzer()

    features, audit = build_song_features(PROJECT_ROOT, analyzer=analyzer)
    output_dir = PROJECT_ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_dir / "song_features.csv", index=False)
    audit.to_csv(output_dir / "pipeline_audit.csv", index=False)
    build_quality_issues(features).to_csv(output_dir / "quality_issues.csv", index=False)
    print(f"Built {len(features):,} song records across {len(audit)} chart snapshots.")


if __name__ == "__main__":
    main()

