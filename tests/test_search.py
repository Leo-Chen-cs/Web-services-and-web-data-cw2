"""Tests for search and command formatting."""

from __future__ import annotations

import pytest

from src.crawler import Page
from src.indexer import build_index
from src.main import SearchCli
from src.search import SearchEngine, format_results


@pytest.fixture()
def engine() -> SearchEngine:
    index = build_index(
        [
            Page(
                url="https://quotes.toscrape.com/",
                title="Home",
                text="Love life life",
            ),
            Page(
                url="https://quotes.toscrape.com/page/2/",
                title="Page 2",
                text="Love books",
            ),
        ]
    )
    return SearchEngine(index)


def test_single_word_query_returns_ranked_pages(engine: SearchEngine) -> None:
    results = engine.find(["life"])

    assert [result.url for result in results] == ["https://quotes.toscrape.com/"]
    assert results[0].frequencies == {"life": 2}


def test_multi_word_query_uses_and_logic(engine: SearchEngine) -> None:
    results = engine.find(["love", "books"])

    assert [result.url for result in results] == [
        "https://quotes.toscrape.com/page/2/"
    ]


def test_quoted_phrase_query_requires_consecutive_positions() -> None:
    index = build_index(
        [
            Page(
                url="https://quotes.toscrape.com/phrase/",
                title="Phrase",
                text="Good friends are rare",
            ),
            Page(
                url="https://quotes.toscrape.com/apart/",
                title="Apart",
                text="Good ideas and loyal friends are rare",
            ),
        ]
    )
    engine = SearchEngine(index)

    phrase_results = engine.find(["good friends"])
    and_results = engine.find(["good", "friends"])

    assert [result.url for result in phrase_results] == [
        "https://quotes.toscrape.com/phrase/"
    ]
    assert phrase_results[0].frequencies["good friends"] == 1
    assert {result.url for result in and_results} == {
        "https://quotes.toscrape.com/phrase/",
        "https://quotes.toscrape.com/apart/",
    }


def test_phrase_query_can_combine_with_single_terms() -> None:
    index = build_index(
        [
            Page(
                url="https://quotes.toscrape.com/match/",
                title="Match",
                text="Good friends read books",
            ),
            Page(
                url="https://quotes.toscrape.com/no-extra-term/",
                title="No Extra Term",
                text="Good friends travel",
            ),
        ]
    )
    engine = SearchEngine(index)

    results = engine.find(["good friends", "books"])

    assert [result.url for result in results] == [
        "https://quotes.toscrape.com/match/"
    ]


def test_missing_and_empty_queries(engine: SearchEngine) -> None:
    assert engine.find(["missing"]) == []
    assert engine.find([]) == []


def test_print_term_output_includes_posting_details(engine: SearchEngine) -> None:
    output = engine.print_term("LOVE!")

    assert "Term: love" in output
    assert "Document frequency: 2" in output
    assert "frequency=1" in output


def test_print_term_validates_single_word_and_suggests_matches(
    engine: SearchEngine,
) -> None:
    assert engine.print_term("two words") == "Please provide exactly one searchable word."

    output = engine.print_term("lve")

    assert "No index entries found for 'lve'." in output
    assert "Did you mean: love?" in output


def test_search_engine_requires_loaded_index() -> None:
    engine = SearchEngine()

    with pytest.raises(RuntimeError):
        engine.find(["life"])


def test_suggest_handles_empty_input(engine: SearchEngine) -> None:
    assert engine.suggest("!!!") == []


def test_format_results_handles_empty_result_set() -> None:
    assert format_results([]) == "No matching pages found."


def test_cli_handles_edge_cases(engine: SearchEngine, tmp_path) -> None:
    cli = SearchCli(index_path=tmp_path / "index.json")
    cli.engine = engine

    assert cli.execute("") == (
        "Enter a command: build, load, print <word>, find <word...>, help, exit"
    )
    assert cli.execute("print two words") == "Usage: print <word>"
    assert cli.execute("find") == "Usage: find <word1> [word2 ...]"


def test_cli_auto_loads_default_index_for_one_shot_commands(tmp_path) -> None:
    from src.indexer import save_index

    index_path = tmp_path / "index.json"
    save_index(
        build_index(
            [
                Page(
                    url="https://quotes.toscrape.com/",
                    title="Home",
                    text="Life is lovely",
                )
            ]
        ),
        index_path,
    )
    cli = SearchCli(index_path=index_path)

    output = cli.execute("find life")

    assert "https://quotes.toscrape.com/" in output
