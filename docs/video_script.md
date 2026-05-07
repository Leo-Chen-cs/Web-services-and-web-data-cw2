# Five-Minute Video Script

## 0:00-2:00 Live Demo

Show the terminal and run:

```bash
python -m src.main
```

Demonstrate:

```text
> build
> load
> print life
> find life love
> find "good friends"
> find missingword
> find
```

Explain briefly that `build` crawls the website politely, constructs the index,
and saves `data/index.json`; `load` reuses the saved index; `print` shows the
posting list; `find` uses AND logic and TF-IDF ranking.

## 2:00-3:30 Code And Design

Open `src/crawler.py`, `src/indexer.py`, and `src/search.py`.

Key points:

- `Crawler.crawl` uses BFS, keeps visited URLs, and stays on the same host.
- `_respect_politeness_window` enforces at least six seconds between requests.
- `build_index` maps each token to URLs, frequencies, and positions.
- `SearchEngine.find` intersects posting lists for AND queries, verifies quoted
  phrase queries using token positions, and ranks with TF-IDF.
- JSON was chosen because it is readable and easy to submit.

## 3:30-4:00 Tests

Run:

```bash
pytest --cov=src --cov-report=term-missing
```

Explain that tests cover normal crawl behaviour, duplicate links, error
recovery, politeness, indexing, positions, single-word search, multi-word search,
phrase search, missing terms, and CLI edge cases. Mention the benchmark script
for reproducible performance checks.

## 4:00-4:30 Git

Run:

```bash
git log --oneline
```

Mention the implementation was developed in clear stages: crawler, index/search,
tests, documentation, and high-scoring extras such as phrase search and
benchmarking notes.

## 4:30-5:00 GenAI Reflection

State that AI was used to help plan, implement, and test. Give concrete examples:

- Helpful: suggested separating crawler, indexer, and search modules, which made
  testing easier.
- Needed correction: AI-style crawler drafts often forget the six-second
  politeness window or make tests wait in real time, so the final code injects
  `sleep_func` and `time_func` for fast tests.
- Learning impact: checking the code improved understanding of BFS crawling,
  inverted indexes, JSON persistence, phrase matching, and TF-IDF.
