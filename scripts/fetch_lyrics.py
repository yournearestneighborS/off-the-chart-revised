"""Retrieve lyrics from Genius while recording the match used for each song."""

from __future__ import annotations

import argparse
import os
import time
from difflib import SequenceMatcher
from pathlib import Path

import lyricsgenius
import pandas as pd


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left.casefold().strip(), right.casefold().strip()).ratio()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    token = os.getenv("GENIUS_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Set GENIUS_ACCESS_TOKEN in your environment before running this script.")
    genius = lyricsgenius.Genius(
        token, skip_non_songs=True, remove_section_headers=False, retries=3, timeout=20
    )
    chart = pd.read_csv(args.input)
    records: list[dict[str, object]] = []

    for row in chart.itertuples(index=False):
        song = genius.search_song(row.title, row.artist)
        title_score = similarity(row.title, song.title) if song else 0.0
        artist_score = similarity(row.artist, song.artist) if song else 0.0
        accepted = bool(song and song.lyrics and title_score >= 0.65 and artist_score >= 0.45)
        records.append(
            {
                "song_title": row.title,
                "artist": row.artist,
                "lyrics": song.lyrics if accepted else None,
                "matched_title": song.title if song else None,
                "matched_artist": song.artist if song else None,
                "title_match_score": title_score,
                "artist_match_score": artist_score,
                "match_accepted": accepted,
                "source": "Genius",
            }
        )
        time.sleep(args.delay)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(args.output, index=False)
    print(f"Saved {len(records)} retrieval records to {args.output}")


if __name__ == "__main__":
    main()
