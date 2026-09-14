import unittest

import pandas as pd

from offthechart.quality import audit_chart_pipeline


class QualityTests(unittest.TestCase):
    def test_pipeline_audit_counts_missing_lyrics(self) -> None:
        chart = pd.DataFrame({"rank": [1, 2], "title": ["A", "B"], "artist": ["X", "Y"]})
        genres = chart.assign(genre=["Pop", None])
        lyrics = pd.DataFrame({"song_title": ["A"], "artist": ["X"], "lyrics": ["words"]})
        audit = audit_chart_pipeline(chart, genres, lyrics, 2025)
        self.assertEqual(audit["lyrics_retrieved"], 1)
        self.assertEqual(audit["lyrics_missing"], 1)
        self.assertEqual(audit["genres_missing"], 1)
        self.assertEqual(audit["missing_chart_positions"], 98)


if __name__ == "__main__":
    unittest.main()

