# Complexity Analysis and Benchmarking

This note documents the main algorithmic trade-offs in the search engine and
provides a reproducible benchmark command for the video or README.

## Symbols

- `P`: number of crawled pages
- `L`: number of discovered links
- `T`: total number of tokens across all pages
- `V`: vocabulary size
- `k`: number of unique query terms
- `p_i`: posting-list size for query term `i`
- `R`: number of matching result pages

## Crawling

The crawler uses breadth-first search with a queue, a visited set, and a queued
set. Each crawled URL is fetched at most once and each discovered link is
normalised and checked.

- Time complexity: `O(P + L)`, ignoring network latency.
- Space complexity: `O(P + L)` for visited URLs, queued URLs, and extracted
  pages.
- Politeness: runtime is intentionally dominated by the six-second delay
  between requests during the real `build` command.

## Indexing

The indexer tokenises each page once and records every token position in a
dictionary-based inverted index:

```text
term -> postings -> url -> frequency + positions
```

- Time complexity: `O(T)`.
- Space complexity: `O(T + V)` because every token position is stored once and
  each unique term has metadata.

This structure makes `print <word>` efficient because it performs one
dictionary lookup for the normalised term.

## Search

Single-word search performs one term lookup and ranks the posting list.

- Lookup time: `O(1)` average dictionary access.
- Ranking time: `O(R log R)`.

Multi-word search intersects posting-list URL sets for all query terms.

- Candidate selection: `O(sum(p_i))`.
- Ranking: `O(R log R)`.

Quoted phrase search, for example `find "good friends"`, reuses the stored
positions. After candidate selection, it checks whether the phrase terms appear
at consecutive positions.

- Phrase verification: `O(R * m * a)` in the simple implementation, where `m`
  is phrase length and `a` is the number of occurrences of the first phrase
  token in a candidate page.

## Benchmarking

Run:

```bash
python scripts/benchmark.py --repeats 100
```

The script reports:

- indexing time for 100 deterministic synthetic pages,
- average query time for representative single-term, multi-term, phrase, and
  missing-term queries.

These figures are intentionally local and reproducible. Real crawl time is not
benchmarked because the coursework politeness window must delay successive
requests by at least six seconds.

