# Private lyric inputs

Place the locally collected Genius files and original sentiment outputs here before rebuilding the published baseline:

```text
lyrics_1965_data.csv
lyrics_1985_data.csv
lyrics_2005_data.csv
lyrics_2025_data.csv
lyrics_with_sentiment_1965.csv
lyrics_with_sentiment_1985.csv
lyrics_with_sentiment_2005.csv
lyrics_with_sentiment_2025.csv
```

The four `lyrics_*_data.csv` files are intentionally excluded from version control because they contain complete copyrighted lyrics. The `lyrics_with_sentiment_*` files preserve the original full-text VADER and TextBlob baseline used in the notebook. The public `data/processed/song_features.csv` file contains derived numerical features but no lyric text.

To create a fresh line-level VADER run instead, install the `nlp` dependencies and use:

```bash
python -m nltk.downloader vader_lexicon
python scripts/build_features.py --with-sentiment
```

Fresh line-level columns should be reviewed before replacing the documented full-text baseline in the portfolio notebook.
