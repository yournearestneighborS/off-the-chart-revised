# Processed data dictionary

`data/processed/song_features.csv` contains one row per chart position. It does not contain full lyrics.

| Field | Meaning |
|---|---|
| `year`, `chart_date` | Snapshot year and exact Billboard chart date |
| `rank`, `title`, `artist` | Chart position and song identifiers |
| `raw_genre` | Genre text returned by the source lookup |
| `legacy_simplified_genre` | Broad genre used in the original notebook |
| `simplified_genre` | Revised broad genre after rules and overrides |
| `genre_review_status` | `rule_based`, `manual_override`, or `missing` |
| `genre_review_note` | Reason for a documented manual correction |
| `vader_fulltext_score` | Original whole-lyric VADER compound score |
| `textblob_fulltext_score` | Original whole-lyric TextBlob polarity |
| `vader_fulltext_label`, `textblob_fulltext_label` | Score mapped to positive, neutral, or negative using ±0.05 |
| `model_agreement` | Whether the two broad sentiment labels match |
| `contains_*` | Flags for possible Genius page contamination in the source text |
| `raw_character_count`, `clean_character_count` | Text length before and after revised cleanup |
| `clean_word_count`, `clean_line_count`, `usable_lyrics` | Quality checks on revised cleaned text |
| `word_count`, `line_count` | Derived lyric length features |
| `unique_word_ratio` | Unique lowercase tokens divided by all tokens |
| `repeated_line_share` | Share of lines that repeat another normalized line |
| `lyrics_available` | Whether a lyric record was retrieved |
| `rank_weight` | `101 - rank`, used for sensitivity analysis |

The `legacy_` and `fulltext_` names make it clear which fields came from the original analysis. The refactored line-level scoring code is available in `src/offthechart/sentiment.py` but is not presented as an executed result without a fresh run.
