"""Lyric extraction cleanup that preserves sentiment-bearing punctuation and case."""

from __future__ import annotations

import re


SECTION_HEADER = re.compile(r"^\s*\[[^\]]{1,80}\]\s*$", re.MULTILINE)
TRAILING_EMBED = re.compile(r"\s*\d*\s*Embed\s*$", re.IGNORECASE)
PREAMBLE_CUES = re.compile(
    r"\b(track|song|single|album|billboard|chart|grammy|released|written|produced|soundtrack|peaked)\b",
    re.IGNORECASE,
)
CONTAMINATION_PATTERNS = {
    "contains_read_more": re.compile(r"read more", re.IGNORECASE),
    "contains_embed": re.compile(r"\bembed\b", re.IGNORECASE),
    "contains_contributors": re.compile(r"\bcontributors?\b", re.IGNORECASE),
    "contains_genius_metadata": re.compile(
        r"more on genius|you might also like|translations?", re.IGNORECASE
    ),
}


def clean_lyrics(text: object) -> str:
    """Remove Genius page material while retaining lyric wording and punctuation.

    The former pipeline lowercased text and removed punctuation before VADER scoring.
    This version keeps both because capitalization and punctuation carry sentiment.
    """
    if not isinstance(text, str):
        return ""

    cleaned = text.replace("\xa0", " ").replace("\r\n", "\n").strip()

    # Genius descriptions commonly end with an ellipsis followed by “Read More”.
    if re.search(r"read more\s*\n", cleaned, flags=re.IGNORECASE):
        cleaned = re.split(r"read more\s*\n", cleaned, maxsplit=1, flags=re.IGNORECASE)[1]

    # Remove a metadata-like first paragraph when it precedes a blank line.
    blocks = re.split(r"\n\s*\n", cleaned, maxsplit=1)
    if len(blocks) == 2 and PREAMBLE_CUES.search(blocks[0]) and len(blocks[0]) < 600:
        cleaned = blocks[1]

    for marker in (
        "You might also like",
        "More on Genius",
        "Translations",
        "Contributors",
    ):
        cleaned = re.split(re.escape(marker), cleaned, maxsplit=1, flags=re.IGNORECASE)[0]

    cleaned = SECTION_HEADER.sub("", cleaned)
    cleaned = TRAILING_EMBED.sub("", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def lyric_quality_flags(text: object) -> dict[str, bool | int]:
    """Return transparent checks used before a lyric is included in analysis."""
    raw = text if isinstance(text, str) else ""
    cleaned = clean_lyrics(raw)
    result: dict[str, bool | int] = {
        name: bool(pattern.search(raw)) for name, pattern in CONTAMINATION_PATTERNS.items()
    }
    result.update(
        {
            "raw_character_count": len(raw),
            "clean_character_count": len(cleaned),
            "clean_word_count": len(re.findall(r"\b[\w’']+\b", cleaned)),
            "clean_line_count": len([line for line in cleaned.splitlines() if line.strip()]),
            "usable_lyrics": len(cleaned) >= 100,
        }
    )
    return result


def lexical_features(text: object) -> dict[str, float | int]:
    """Calculate non-copyrighted summary features from cleaned lyrics."""
    cleaned = clean_lyrics(text)
    tokens = re.findall(r"\b[a-zA-Z’']+\b", cleaned.lower())
    lines = [line.strip().lower() for line in cleaned.splitlines() if line.strip()]
    unique_token_ratio = len(set(tokens)) / len(tokens) if tokens else 0.0
    repeated_line_share = 1 - (len(set(lines)) / len(lines)) if lines else 0.0
    return {
        "word_count": len(tokens),
        "line_count": len(lines),
        "unique_word_ratio": unique_token_ratio,
        "repeated_line_share": repeated_line_share,
    }

