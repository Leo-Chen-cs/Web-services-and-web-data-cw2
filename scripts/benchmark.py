"""Small benchmark utility for indexing and query processing."""

from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean
import sys
from time import perf_counter

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.crawler import Page
from src.indexer import build_index, load_index
from src.search import SearchEngine


DEFAULT_INDEX_PATH = Path("data/index.json")
DEFAULT_QUERIES = [
    ["life"],
    ["love", "life"],
    ["good friends"],
    ["nonexistentword"],
]


def benchmark_queries(index_path: Path, repeats: int) -> list[tuple[str, float, int]]:
    """Return average query timings in milliseconds."""
    index = load_index(index_path)
    engine = SearchEngine(index)
    rows: list[tuple[str, float, int]] = []

    for query in DEFAULT_QUERIES:
        timings: list[float] = []
        result_count = 0
        for _ in range(repeats):
            started_at = perf_counter()
            results = engine.find(query)
            timings.append((perf_counter() - started_at) * 1000)
            result_count = len(results)
        rows.append((" ".join(query), mean(timings), result_count))
    return rows


def benchmark_indexing() -> float:
    """Return indexing time for a small deterministic document set."""
    documents = [
        Page(
            url=f"https://quotes.toscrape.com/example/{index}/",
            title=f"Example {index}",
            text=(
                "Life love friendship books imagination "
                "life courage wisdom truth "
            )
            * 50,
        )
        for index in range(100)
    ]
    started_at = perf_counter()
    build_index(documents)
    return (perf_counter() - started_at) * 1000


def parse_args() -> argparse.Namespace:
    """Parse benchmark command-line arguments."""
    parser = argparse.ArgumentParser(description="Benchmark search engine operations")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--repeats", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    """Run the benchmark and print compact results."""
    args = parse_args()
    if args.repeats <= 0:
        raise SystemExit("--repeats must be positive")

    indexing_ms = benchmark_indexing()
    print(f"Indexing benchmark: 100 synthetic pages in {indexing_ms:.2f} ms")
    print("Query benchmark:")
    print("query, average_ms, result_count")
    for query, average_ms, result_count in benchmark_queries(args.index, args.repeats):
        print(f"{query}, {average_ms:.4f}, {result_count}")


if __name__ == "__main__":
    main()
