import unittest

import pandas as pd

from offthechart.genres import apply_genre_overrides, simplify_genre


class GenreTests(unittest.TestCase):
    def test_broad_genre_rules(self) -> None:
        self.assertEqual(simplify_genre("west coast hip hop, rap"), "Hip-Hop")
        self.assertEqual(simplify_genre("motown, northern soul"), "R&B/Soul")
        self.assertEqual(simplify_genre("country, acoustic country"), "Country")
        self.assertEqual(simplify_genre(None), "Unknown")

    def test_override_preserves_source_and_adds_audit_note(self) -> None:
        data = pd.DataFrame([{
            "year": 2005,
            "title": "We Belong Together",
            "artist": "Mariah Carey",
            "raw_genre": "christmas",
        }])
        overrides = pd.DataFrame([{
            "year": 2005,
            "title": "We Belong Together",
            "artist": "Mariah Carey",
            "corrected_genre": "R&B/Soul",
            "reason": "Song-level review",
        }])
        result = apply_genre_overrides(data, overrides).iloc[0]
        self.assertEqual(result["raw_genre"], "christmas")
        self.assertEqual(result["simplified_genre"], "R&B/Soul")
        self.assertEqual(result["genre_review_status"], "manual_override")


if __name__ == "__main__":
    unittest.main()

