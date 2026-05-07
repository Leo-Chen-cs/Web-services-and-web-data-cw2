# COMP3011 Coursework 2 Search Engine Tool

This project implements a small command-line search engine for
<https://quotes.toscrape.com/>. It politely crawls the website, builds an
inverted index, stores the index as JSON, and supports `print` and `find`
queries over the saved data.

## Features

- Polite BFS crawler using `requests` and `BeautifulSoup`
- Six-second politeness window between HTTP requests
- Duplicate URL detection and same-site crawling only
- Graceful handling for timeouts, non-200 responses, and unsupported content
- Case-insensitive inverted index with frequencies and token positions
- JSON persistence through `build` and `load`
- AND search for multi-word queries
- Exact phrase search using token positions, for example `find "good friends"`
- TF-IDF ranking for `find` results
- Query suggestions for close missing terms
- Focused `pytest` test suite covering crawler, indexing, search, and CLI logic
- Reproducible benchmark script and complexity analysis notes

## Project Structure

```text
.
├── src/
│   ├── crawler.py
│   ├── indexer.py
│   ├── search.py
│   └── main.py
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   ├── test_main.py
│   └── test_search.py
├── data/
│   └── index.json
├── docs/
│   ├── complexity_analysis.md
│   ├── genai_reflection.md
│   ├── submission_report.tex
│   └── video_script.md
├── scripts/
│   └── benchmark.py
├── requirements.txt
└── README.md
```

## Installation

Use Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Start the interactive CLI:

```bash
python -m src.main
```

Available commands:

```text
build [max_pages]       Crawl the site, build an index, and save it
load [index_path]       Load an existing JSON index
print <word>            Show the inverted index entry for one word
find <word1> [word2...] Find pages containing all words, ranked by TF-IDF
exit                    Quit the program
```

Example session:

```text
> build
Built index for 213 pages and saved it to data/index.json. Failed URLs: 1.
> load
Loaded index from data/index.json (213 documents).
> print miracle
Term: miracle
Document frequency: 2
IDF: 4.6109
- https://quotes.toscrape.com/: frequency=2; positions=[...]
> find life love
1. Quotes to Scrape
   URL: https://quotes.toscrape.com/
   Score: 8.5132; frequencies: life=2, love=1
> find "good friends"
1. Quotes to Scrape
   URL: https://quotes.toscrape.com/tag/friends/
   Score: ...
```

You can also run one command non-interactively, which is useful for video demos:

```bash
python -m src.main --command "load"
python -m src.main --command "find life love"
```

For `print` and `find`, the CLI automatically loads `data/index.json` when it
exists, so one-shot commands work in a fresh terminal.

For faster development-only checks, limit the number of crawled pages:

```bash
python -m src.main --command "build 3"
```

The submitted index should be generated with the normal `build` command so the
six-second politeness rule is respected for the full crawl.

## Testing

Run the full suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

The tests mock HTTP responses so they are fast, deterministic, and do not make
network requests.

For reproducibility, the tests avoid live network access and use mocked crawler
responses where appropriate.

## Design Decisions

The crawler uses breadth-first search because it gives predictable coverage of
the site and naturally works with a queue of discovered links. Each URL is
normalised by removing fragments, and the crawler only follows links on the
same host as the base URL.

The index uses a dictionary-based inverted index:

```text
term -> postings -> url -> frequency + positions
```

This structure makes `print <word>` direct and efficient, while multi-word
search is implemented by intersecting URL sets for each query term. The index
also stores document metadata and IDF values so `find` can rank results by
simple TF-IDF:

```text
score(document, query) = sum(term_frequency * inverse_document_frequency)
```

The JSON format is intentionally readable so the marker can inspect the index
file without needing a custom viewer.

Phrase queries reuse the stored positions. A quoted query such as
`find "good friends"` first finds pages containing both words, then checks that
the positions are consecutive. This keeps the index structure simple while
adding advanced query processing beyond the base requirements.

## Complexity And Benchmarking

Detailed complexity notes are in `docs/complexity_analysis.md`.

Run a local benchmark:

```bash
python scripts/benchmark.py --repeats 100
```

The benchmark reports indexing time for deterministic synthetic pages and
average query latency for single-term, multi-term, phrase, and missing-term
queries. Real crawl time is not benchmarked because the coursework requires a
six-second politeness delay between successive requests.

## Video Demo Checklist

Keep the final video under five minutes:

1. Live demo: `build`, `load`, `print`, `find`, missing word, and empty query.
2. Code walkthrough: crawler politeness, inverted index, phrase queries, and
   TF-IDF ranking.
3. Testing: run `pytest --cov=src --cov-report=term-missing` and mention the
   benchmark script.
4. Git: show meaningful commits and explain the development order.
5. GenAI reflection: state the tools used, how they helped, where they were
   wrong or incomplete, and what you learned by checking the generated code.

## GenAI Use Statement

Generative AI was used as a programming assistant to help plan the project,
draft implementation ideas, create tests, and improve documentation. All AI
output was reviewed, run locally, and corrected where needed. The most important
learning was understanding why the generated code worked: especially the URL
normalisation, the politeness window, and the inverted-index structure.

The final implementation also includes manual improvements beyond generated
drafts, including testable politeness-window injection, exact phrase matching
using token positions, and benchmark documentation.

## References

- Requests documentation: <https://requests.readthedocs.io/>
- Beautiful Soup documentation: <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>
- Pytest documentation: <https://docs.pytest.org/>
- Quotes to Scrape test website: <https://quotes.toscrape.com/>
