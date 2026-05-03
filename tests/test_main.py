"""Tests for command-line orchestration."""

from __future__ import annotations

import builtins
import sys

import pytest

from src.crawler import Page
from src.indexer import build_index, save_index
from src.main import HELP_TEXT, SearchCli, main, parse_args


class FakeCrawler:
    """Network-free crawler used for CLI build tests."""

    failed_urls = {"https://quotes.toscrape.com/missing/": "HTTP 404"}

    def __init__(self, base_url: str, politeness_window: float) -> None:
        self.base_url = base_url
        self.politeness_window = politeness_window

    def crawl(self, max_pages: int | None = None) -> list[Page]:
        if max_pages == 0:
            return []
        return [
            Page(
                url="https://quotes.toscrape.com/",
                title="Home",
                text="Simple searchable text",
            )
        ]


def test_build_command_saves_index_without_network(monkeypatch, tmp_path) -> None:
    import src.main as main_module

    monkeypatch.setattr(main_module, "Crawler", FakeCrawler)
    cli = SearchCli(index_path=tmp_path / "index.json")

    output = cli.execute("build 1")

    assert "Built index for 1 pages" in output
    assert "Failed URLs: 1" in output
    assert (tmp_path / "index.json").exists()


def test_build_command_validates_arguments_and_empty_crawl(monkeypatch, tmp_path) -> None:
    import src.main as main_module

    monkeypatch.setattr(main_module, "Crawler", FakeCrawler)
    cli = SearchCli(index_path=tmp_path / "index.json")

    assert cli.execute("build many") == "Usage: build [max_pages]"
    assert cli.execute("build 0") == "No pages were crawled; index was not updated."


def test_load_help_unknown_parse_and_exit_paths(tmp_path) -> None:
    index_path = tmp_path / "index.json"
    save_index(
        build_index(
            [Page(url="https://quotes.toscrape.com/", title="Home", text="Alpha")]
        ),
        index_path,
    )
    cli = SearchCli(index_path=index_path)

    assert cli.execute("load").startswith("Loaded index")
    assert cli.execute("help") == HELP_TEXT
    assert cli.execute("unknown") == (
        "Unknown command 'unknown'. Type 'help' for available commands."
    )
    assert cli.execute('find "unterminated').startswith("Could not parse command:")
    with pytest.raises(EOFError):
        cli.execute("exit")


def test_find_without_index_returns_clear_message(tmp_path) -> None:
    cli = SearchCli(index_path=tmp_path / "missing.json")

    assert cli.execute("find alpha") == "No index loaded. Run 'build' or 'load' first."


def test_interactive_run_handles_help_then_exit(monkeypatch, capsys, tmp_path) -> None:
    commands = iter(["help", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(commands))
    cli = SearchCli(index_path=tmp_path / "index.json")

    cli.run()

    output = capsys.readouterr().out
    assert "COMP3011 Search Engine Tool" in output
    assert "Available commands" in output
    assert "Goodbye." in output


def test_parse_args_and_main_one_shot(monkeypatch, capsys, tmp_path) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--index",
            str(tmp_path / "index.json"),
            "--base-url",
            "https://quotes.toscrape.com/",
            "--politeness-window",
            "0",
            "--command",
            "help",
        ],
    )

    args = parse_args()
    assert args.politeness_window == 0

    main()
    assert "Available commands" in capsys.readouterr().out

