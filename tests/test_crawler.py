"""Tests for the polite crawler."""

from __future__ import annotations

import requests

import pytest

from src.crawler import Crawler, pages_to_dicts


class FakeResponse:
    """Minimal response object used by crawler tests."""

    def __init__(
        self,
        text: str,
        status_code: int = 200,
        content_type: str = "text/html",
    ) -> None:
        self.text = text
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}


class FakeSession:
    """Session that returns registered HTML pages."""

    def __init__(self, pages: dict[str, FakeResponse]) -> None:
        self.pages = pages
        self.requested_urls: list[str] = []

    def get(self, url: str, timeout: float) -> FakeResponse:
        self.requested_urls.append(url)
        if url == "https://quotes.toscrape.com/error/":
            raise requests.Timeout("slow test URL")
        return self.pages.get(url, FakeResponse("missing", status_code=404))


def test_crawl_collects_pages_and_deduplicates_links() -> None:
    session = FakeSession(
        {
            "https://quotes.toscrape.com/": FakeResponse(
                """
                <html><head><title>Home</title></head><body>
                <p>Alpha quote</p>
                <a href="/page/2/">next</a>
                <a href="/page/2/#duplicate">duplicate</a>
                <a href="https://example.com/outside">outside</a>
                </body></html>
                """
            ),
            "https://quotes.toscrape.com/page/2/": FakeResponse(
                "<html><title>Page 2</title><body>Beta quote</body></html>"
            ),
        }
    )
    crawler = Crawler(
        "https://quotes.toscrape.com/",
        politeness_window=0,
        session=session,
    )

    pages = crawler.crawl()

    assert [page.url for page in pages] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert session.requested_urls.count("https://quotes.toscrape.com/page/2/") == 1


def test_politeness_window_is_observed_between_requests() -> None:
    sleeps: list[float] = []
    session = FakeSession(
        {
            "https://quotes.toscrape.com/": FakeResponse(
                '<a href="/page/2/">next</a>'
            ),
            "https://quotes.toscrape.com/page/2/": FakeResponse("done"),
        }
    )
    crawler = Crawler(
        "https://quotes.toscrape.com/",
        politeness_window=6,
        session=session,
        sleep_func=sleeps.append,
        time_func=lambda: 10.0,
    )

    crawler.crawl()

    assert sleeps == [6]


def test_network_errors_are_recorded_and_do_not_stop_crawl() -> None:
    session = FakeSession(
        {
            "https://quotes.toscrape.com/": FakeResponse(
                '<a href="/error/">bad</a><a href="/ok/">ok</a>'
            ),
            "https://quotes.toscrape.com/ok/": FakeResponse("Recovered"),
        }
    )
    crawler = Crawler(
        "https://quotes.toscrape.com/",
        politeness_window=0,
        session=session,
    )

    pages = crawler.crawl()

    assert "https://quotes.toscrape.com/error/" in crawler.failed_urls
    assert [page.url for page in pages] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/ok/",
    ]


def test_crawler_rejects_negative_politeness_window() -> None:
    with pytest.raises(ValueError):
        Crawler("https://quotes.toscrape.com/", politeness_window=-1)


def test_crawl_respects_non_positive_max_pages() -> None:
    crawler = Crawler(
        "https://quotes.toscrape.com/",
        politeness_window=0,
        session=FakeSession({}),
    )

    assert crawler.crawl(max_pages=0) == []


def test_fetch_records_bad_status_and_content_type() -> None:
    session = FakeSession(
        {
            "https://quotes.toscrape.com/bad/": FakeResponse("missing", 404),
            "https://quotes.toscrape.com/image/": FakeResponse(
                "png",
                200,
                "image/png",
            ),
        }
    )
    crawler = Crawler(
        "https://quotes.toscrape.com/",
        politeness_window=0,
        session=session,
    )

    assert crawler.fetch("https://quotes.toscrape.com/bad/") is None
    assert crawler.fetch("https://quotes.toscrape.com/image/") is None
    assert crawler.failed_urls["https://quotes.toscrape.com/bad/"] == "HTTP 404"
    assert "Unsupported content type" in crawler.failed_urls[
        "https://quotes.toscrape.com/image/"
    ]


def test_pages_to_dicts_converts_page_objects() -> None:
    pages = crawler_pages = [
        Crawler("https://quotes.toscrape.com/").parse(
            "https://quotes.toscrape.com/",
            "<title>Home</title><p>Text</p>",
        )[0]
    ]

    assert pages_to_dicts(crawler_pages) == [
        {
            "url": "https://quotes.toscrape.com/",
            "title": "Home",
            "text": "Home Text",
        }
    ]
