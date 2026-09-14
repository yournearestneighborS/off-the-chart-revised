import unittest

from offthechart.sentiment import score_lyrics_by_line


class FakeAnalyzer:
    def polarity_scores(self, text: str) -> dict[str, float]:
        if "good" in text.lower():
            return {"compound": 0.6}
        if "bad" in text.lower():
            return {"compound": -0.6}
        return {"compound": 0.0}


class SentimentTests(unittest.TestCase):
    def test_line_level_aggregation_preserves_mixed_tone(self) -> None:
        result = score_lyrics_by_line("A good day\nA bad night\nJust here", FakeAnalyzer())
        self.assertEqual(result["lines_scored"], 3)
        self.assertAlmostEqual(result["positive_line_share"], 1 / 3)
        self.assertAlmostEqual(result["negative_line_share"], 1 / 3)
        self.assertAlmostEqual(result["neutral_line_share"], 1 / 3)
        self.assertEqual(result["sentiment_label"], "neutral")

    def test_empty_text_is_neutral(self) -> None:
        result = score_lyrics_by_line("", FakeAnalyzer())
        self.assertEqual(result["lines_scored"], 0)
        self.assertEqual(result["sentiment_label"], "neutral")


if __name__ == "__main__":
    unittest.main()

