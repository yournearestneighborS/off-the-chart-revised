"""Download one dated Billboard Hot 100 chart and validate its ranks."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


USER_AGENT = "Mozilla/5.0 (compatible; academic data project; +https://github.com/)"


def fetch_chart(chart_date: str) -> pd.DataFrame:
    """Fetch a Billboard chart page and return explicitly parsed rank/title/artist rows."""
    url = f"https://www.billboard.com/charts/hot-100/{chart_date}/"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    records: list[dict[str, object]] = []

    for item in soup.select("div.o-chart-results-list-row-container"):
        title_node = item.select_one("h3#title-of-a-story")
        rank_node = item.select_one("span.c-label.a-font-primary-bold-l")
        artist_node = item.select_one("li.lrv-u-width-100p ul li span.c-label.a-no-trucate")
        if not (title_node and rank_node and artist_node):
            continue
        rank_text = rank_node.get_text(strip=True)
        if not rank_text.isdigit():
            continue
        records.append(
            {
                "rank": int(rank_text),
                "title": title_node.get_text(" ", strip=True),
                "artist": artist_node.get_text(" ", strip=True),
                "chart_date": chart_date,
                "source_url": url,
            }
        )

    chart = pd.DataFrame(records).drop_duplicates(subset=["rank"]).sort_values("rank")
    expected = set(range(1, 101))
    found = set(chart["rank"]) if not chart.empty else set()
    missing = sorted(expected - found)
    if missing:
        raise ValueError(
            f"Parsed {len(chart)} unique positions; missing ranks: {missing}. "
            "Billboard's page structure may have changed."
        )
    return chart.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="Chart date in YYYY-MM-DD format")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    chart = fetch_chart(args.date)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    chart.to_csv(args.output, index=False)
    print(f"Saved {len(chart)} validated chart positions to {args.output}")


if __name__ == "__main__":
    main()
