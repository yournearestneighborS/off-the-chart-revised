import unittest

from offthechart.text import clean_lyrics, lexical_features, lyric_quality_flags


class LyricCleaningTests(unittest.TestCase):
    def test_read_more_preamble_is_removed(self) -> None:
        raw = "The track reached number one… Read More\nFirst lyric line\nSecond line"
        self.assertEqual(clean_lyrics(raw), "First lyric line\nSecond line")

    def test_metadata_first_paragraph_is_removed(self) -> None:
        raw = "It won a Grammy for the song.\n\nReal lyric\nAnother lyric"
        self.assertEqual(clean_lyrics(raw), "Real lyric\nAnother lyric")

    def test_section_headers_are_removed_but_punctuation_is_preserved(self) -> None:
        raw = "[Chorus]\nI LOVE this song!!!\n[Verse 2]\nDon't stop."
        self.assertEqual(clean_lyrics(raw), "I LOVE this song!!!\n\nDon't stop.")

    def test_quality_and_lexical_features(self) -> None:
        raw = "Good day\nGood day\nNew line"
        flags = lyric_quality_flags(raw)
        features = lexical_features(raw)
        self.assertEqual(flags["clean_line_count"], 3)
        self.assertEqual(features["word_count"], 6)
        self.assertAlmostEqual(features["repeated_line_share"], 1 / 3)


if __name__ == "__main__":
    unittest.main()

