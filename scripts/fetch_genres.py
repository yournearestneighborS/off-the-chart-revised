"""Add artist genres from Spotify, retaining match metadata for review."""

from __future__ import annotations

import argparse
import os
import time
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left.casefold().strip(), right.casefold().strip()).ratio()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET before running.")

    client = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    )
    chart = pd.read_csv(args.input)
    records: list[dict[str, object]] = []
    for row in chart.itertuples(index=False):
        result = client.search(q=f'artist:"{row.artist}"', type="artist", limit=5)
        candidates = result.get("artists", {}).get("items", [])
        best = max(candidates, key=lambda item: similarity(row.artist, item["name"]), default=None)
        score = similarity(row.artist, best["name"]) if best else 0.0
        genres = ", ".join(best.get("genres", [])) if best and score >= 0.60 else None
        records.append(
            {
                "rank": row.rank,
                "title": row.title,
                "artist": row.artist,
                "genre": genres,
                "genre_source": "Spotify" if genres else None,
                "matched_artist": best["name"] if best else None,
                "artist_match_score": score,
                "match_needs_review": score < 0.85 or not genres,
            }
        )
        time.sleep(args.delay)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(args.output, index=False)
    print(f"Saved {len(records)} genre records to {args.output}")


if __name__ == "__main__":
    main()
