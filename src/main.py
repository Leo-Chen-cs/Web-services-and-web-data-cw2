"""Command line interface for the coursework search engine."""

from __future__ import annotations

import argparse
import shlex
from pathlib import Path

from .crawler import Crawler
from .indexer import build_index, load_index, save_index
from .search import SearchEngine, format_results


DEFAULT_BASE_URL = "https://quotes.toscrape.com/"
DEFAULT_INDEX_PATH = Path("data/index.json")


class SearchCli:
    """Interactive command processor for build/load/print/find commands."""

    def __init__(
        self,
        index_path: Path = DEFAULT_INDEX_PATH,
        base_url: str = DEFAULT_BASE_URL,
        politeness_window: float = 6.0,
    ) -> None:
        self.index_path = index_path
        self.base_url = base_url
        self.politeness_window = politeness_window
        self.engine = SearchEngine()

    def execute(self, command_line: str) -> str:
        """Execute one CLI command and return the output text."""
        try:
            parts = shlex.split(command_line)
        except ValueError as exc:
            return f"Could not parse command: {exc}"

        if not parts:
            return "Enter a command: build, load, print <word>, find <word...>, help, exit"

        command, *args = parts
        command = command.lower()

        if command == "build":
            return self._build(args)
        if command == "load":
            return self._load(args)
        if command == "print":
            return self._print(args)
        if command == "find":
            return self._find(args)
        if command in {"help", "?"}:
            return HELP_TEXT
        if command in {"exit", "quit"}:
            raise EOFError

        return f"Unknown command '{command}'. Type 'help' for available commands."

    def run(self) -> None:
        """Run the interactive prompt until the user exits."""
        print("COMP3011 Search Engine Tool")
        print("Type 'help' for commands. Type 'exit' to quit.")
        while True:
            try:
                command_line = input("> ")
                output = self.execute(command_line)
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break
            except Exception as exc:
                output = f"Error: {exc}"

            if output:
                print(output)

    def _build(self, args: list[str]) -> str:
        max_pages = None
        if args:
            try:
                max_pages = int(args[0])
            except ValueError:
                return "Usage: build [max_pages]"

        crawler = Crawler(
            base_url=self.base_url,
            politeness_window=self.politeness_window,
        )
        pages = crawler.crawl(max_pages=max_pages)
        if not pages:
            return "No pages were crawled; index was not updated."

        index = build_index(
            pages,
            extra_metadata={
                "base_url": crawler.base_url,
                "crawler_strategy": "breadth-first search",
                "politeness_window_seconds": crawler.politeness_window,
                "visited_urls": sorted(getattr(crawler, "visited_urls", set())),
                "failed_urls": dict(
                    sorted(getattr(crawler, "failed_urls", {}).items())
                ),
            },
        )
        save_index(index, self.index_path)
        self.engine.set_index(index)
        failed_count = len(crawler.failed_urls)
        return (
            f"Built index for {len(pages)} pages and saved it to {self.index_path}. "
            f"Failed URLs: {failed_count}."
        )

    def _load(self, args: list[str]) -> str:
        path = Path(args[0]) if args else self.index_path
        index = load_index(path)
        self.engine.set_index(index)
        document_count = index.get("metadata", {}).get("document_count", "unknown")
        return f"Loaded index from {path} ({document_count} documents)."

    def _print(self, args: list[str]) -> str:
        if len(args) != 1:
            return "Usage: print <word>"
        load_message = self._ensure_index_loaded()
        if load_message:
            return load_message
        return self.engine.print_term(args[0])

    def _find(self, args: list[str]) -> str:
        if not args:
            return "Usage: find <word1> [word2 ...]"
        load_message = self._ensure_index_loaded()
        if load_message:
            return load_message
        return format_results(self.engine.find(args))

    def _ensure_index_loaded(self) -> str | None:
        if self.engine.loaded:
            return None
        if not self.index_path.exists():
            return "No index loaded. Run 'build' or 'load' first."
        index = load_index(self.index_path)
        self.engine.set_index(index)
        return None


HELP_TEXT = """Available commands:
  build [max_pages]       Crawl the site, build an index, and save it
  load [index_path]       Load an existing JSON index
  print <word>            Show the inverted index entry for one word
  find <word1> [word2...] Find pages containing all words, ranked by TF-IDF
  exit                    Quit the program"""


def parse_args() -> argparse.Namespace:
    """Parse process-level options for the CLI."""
    parser = argparse.ArgumentParser(description="COMP3011 search engine tool")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--politeness-window", type=float, default=6.0)
    parser.add_argument(
        "--command",
        help="Run one command non-interactively, for example: --command 'load'",
    )
    return parser.parse_args()


def main() -> None:
    """Run the command line interface."""
    args = parse_args()
    cli = SearchCli(
        index_path=args.index,
        base_url=args.base_url,
        politeness_window=args.politeness_window,
    )
    if args.command:
        print(cli.execute(args.command))
    else:
        cli.run()


if __name__ == "__main__":
    main()
