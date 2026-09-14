"""Project constants kept in one place for reproducibility."""

from pathlib import Path


YEARS = (1965, 1985, 2005, 2025)

CHART_DATES = {
    1965: "1965-08-28",
    1985: "1985-08-24",
    2005: "2005-08-27",
    2025: "2025-05-03",
}


def find_project_root(start: Path | None = None) -> Path:
    """Find the repository root from either the root or notebooks directory."""
    candidate = (start or Path.cwd()).resolve()
    for path in (candidate, *candidate.parents):
        if (path / "src" / "offthechart").exists() and (path / "data").exists():
            return path
    raise FileNotFoundError("Could not locate the off-the-chart project root.")

