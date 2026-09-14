.PHONY: setup build analyze test all

setup:
	python -m pip install -e ".[dev,nlp,acquisition]"

build:
	python scripts/build_features.py

analyze:
	python scripts/analyze_results.py

test:
	python -m pytest -q

all: build analyze test
