"""Tests for inverted index construction."""

from __future__ import annotations

from src.crawler import Page
import pytest

from src.indexer import (
    build_index,
    load_index,
    save_index,
    term_frequency_summary,
    term_statistics,
    tokenize,
)


def test_tokenize_is_case_insensitive_and_removes_punctuation() -> None:
    assert tokenize("Hello, HELLO! Isn't this working?") == [
        "hello",
        "hello",
        "isn't",
        "this",
        "working",
    ]


def test_build_index_records_frequency_and_positions() -> None:
    index = build_index(
        [
            Page(
                url="https://quotes.toscrape.com/",
                title="Home",
                text="Alpha beta alpha",
            ),
            Page(
                url="https://quotes.toscrape.com/page/2/",
                title="Page 2",
                text="Beta gamma",
            ),
        ]
    )

    alpha_posting = index["terms"]["alpha"]["postings"][
        "https://quotes.toscrape.com/"
    ]
    beta_stats = index["terms"]["beta"]

    assert alpha_posting["frequency"] == 2
    assert alpha_posting["positions"] == [0, 2]
    assert beta_stats["document_frequency"] == 2
    assert index["metadata"]["document_count"] == 2


def test_save_and_load_index_round_trip(tmp_path) -> None:
    index = build_index(
        [Page(url="https://quotes.toscrape.com/", title="Home", text="Alpha")]
    )
    path = tmp_path / "index.json"

    save_index(index, path)
    loaded = load_index(path)

    assert loaded["terms"]["alpha"]["document_frequency"] == 1


def test_build_index_accepts_mapping_documents_and_empty_input() -> None:
    empty_index = build_index([])
    mapping_index = build_index(
        [
            {
                "url": "https://quotes.toscrape.com/",
                "title": "Home",
                "text": "Alpha beta",
            }
        ]
    )

    assert empty_index["metadata"]["document_count"] == 0
    assert mapping_index["documents"]["https://quotes.toscrape.com/"]["length"] == 2


def test_build_index_merges_extra_metadata() -> None:
    index = build_index(
        [Page(url="https://quotes.toscrape.com/", title="Home", text="Alpha")],
        extra_metadata={
            "base_url": "https://quotes.toscrape.com/",
            "politeness_window_seconds": 6,
        },
    )

    assert index["metadata"]["base_url"] == "https://quotes.toscrape.com/"
    assert index["metadata"]["politeness_window_seconds"] == 6


def test_build_index_rejects_missing_document_fields() -> None:
    with pytest.raises(ValueError, match="missing required fields"):
        build_index([{"url": "https://quotes.toscrape.com/", "title": "Home"}])


def test_load_index_rejects_invalid_json_shape(tmp_path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="not a valid index file"):
        load_index(path)


def test_term_statistics_and_frequency_summary() -> None:
    index = build_index(
        [Page(url="https://quotes.toscrape.com/", title="Home", text="Alpha alpha")]
    )

    assert term_statistics(index, "two words") is None
    assert term_frequency_summary(index, "alpha")[
        "https://quotes.toscrape.com/"
    ] == 2
    assert term_frequency_summary(index, "missing") == {}
