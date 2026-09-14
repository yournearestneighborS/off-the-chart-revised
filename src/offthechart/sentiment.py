"""Line-level VADER aggregation for longer text such as song lyrics."""

from __future__ import annotations

from statistics import mean, median


def sentiment_label(score: float, threshold: float = 0.05) -> str:
    if score >= threshold:
        return "positive"
    if score <= -threshold:
        return "negative"
    return "neutral"


def score_lyrics_by_line(text: object, analyzer) -> dict[str, float | int | str]:
    """Score non-empty lyric lines and aggregate them at the song level.

    `analyzer` follows the NLTK VADER interface and is injected so this function
    can be tested without downloading a model during import.
    """
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    if not lines:
        return {
            "sentiment_score": 0.0,
            "sentiment_median": 0.0,
            "positive_line_share": 0.0,
            "neutral_line_share": 0.0,
            "negative_line_share": 0.0,
            "lines_scored": 0,
            "sentiment_label": "neutral",
        }

    scores = [float(analyzer.polarity_scores(line)["compound"]) for line in lines]
    labels = [sentiment_label(score) for score in scores]
    average = mean(scores)
    total = len(scores)
    return {
        "sentiment_score": average,
        "sentiment_median": median(scores),
        "positive_line_share": labels.count("positive") / total,
        "neutral_line_share": labels.count("neutral") / total,
        "negative_line_share": labels.count("negative") / total,
        "lines_scored": total,
        "sentiment_label": sentiment_label(average),
    }

