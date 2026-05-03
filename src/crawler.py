"""Polite web crawler for building a small search index."""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
import time
from typing import Callable, Iterable
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class Page:
    """Text content extracted from a crawled page."""

    url: str
    title: str
    text: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serialisable representation of the page."""
        return asdict(self)


class Crawler:
    """Breadth-first crawler constrained to one website."""

    def __init__(
        self,
        base_url: str,
        politeness_window: float = 6.0,
        timeout: float = 10.0,
        session: requests.Session | None = None,
        sleep_func: Callable[[float], None] = time.sleep,
        time_func: Callable[[], float] = time.monotonic,
    ) -> None:
        if politeness_window < 0:
            raise ValueError("politeness_window must be non-negative")

        self.base_url = self._normalise_url(base_url)
        self.politeness_window = politeness_window
        self.timeout = timeout
        self.session = session or requests.Session()
        self.sleep_func = sleep_func
        self.time_func = time_func
        self.visited_urls: set[str] = set()
        self.failed_urls: dict[str, str] = {}
        self._last_request_started_at: float | None = None
        self._base_netloc = urlparse(self.base_url).netloc

    def crawl(self, start_url: str | None = None, max_pages: int | None = None) -> list[Page]:
        """Crawl pages from ``start_url`` using BFS and return extracted pages."""
        if max_pages is not None and max_pages <= 0:
            return []

        first_url = self._normalise_url(start_url or self.base_url)
        queue: deque[str] = deque([first_url])
        queued: set[str] = {first_url}
        pages: list[Page] = []

        while queue:
            if max_pages is not None and len(pages) >= max_pages:
                break

            url = queue.popleft()
            queued.discard(url)
            if url in self.visited_urls or not self._is_allowed_url(url):
                continue

            html = self.fetch(url)
            self.visited_urls.add(url)
            if html is None:
                continue

            page, links = self.parse(url, html)
            pages.append(page)

            for link in links:
                if link not in self.visited_urls and link not in queued:
                    queue.append(link)
                    queued.add(link)

        return pages

    def fetch(self, url: str) -> str | None:
        """Download one URL, returning HTML or ``None`` if retrieval fails."""
        self._respect_politeness_window()
        self._last_request_started_at = self.time_func()

        try:
            response = self.session.get(url, timeout=self.timeout)
        except requests.RequestException as exc:
            self.failed_urls[url] = exc.__class__.__name__
            return None

        if response.status_code != 200:
            self.failed_urls[url] = f"HTTP {response.status_code}"
            return None

        content_type = response.headers.get("Content-Type", "")
        if "html" not in content_type.lower() and content_type:
            self.failed_urls[url] = f"Unsupported content type: {content_type}"
            return None

        return response.text

    def parse(self, page_url: str, html: str) -> tuple[Page, list[str]]:
        """Extract readable text and same-site links from an HTML document."""
        soup = BeautifulSoup(html, "html.parser")

        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        title = soup.title.get_text(" ", strip=True) if soup.title else page_url
        text = soup.get_text(" ", strip=True)
        links = sorted(self._extract_links(page_url, soup))
        return Page(url=page_url, title=title, text=text), links

    def _extract_links(self, page_url: str, soup: BeautifulSoup) -> set[str]:
        links: set[str] = set()
        for anchor in soup.find_all("a", href=True):
            candidate = self._normalise_url(urljoin(page_url, anchor["href"]))
            if self._is_allowed_url(candidate):
                links.add(candidate)
        return links

    def _respect_politeness_window(self) -> None:
        if self._last_request_started_at is None:
            return

        elapsed = self.time_func() - self._last_request_started_at
        remaining = self.politeness_window - elapsed
        if remaining > 0:
            self.sleep_func(remaining)

    def _is_allowed_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and parsed.netloc == self._base_netloc

    @staticmethod
    def _normalise_url(url: str) -> str:
        url_without_fragment, _fragment = urldefrag(url.strip())
        parsed = urlparse(url_without_fragment)
        path = parsed.path or "/"
        normalised = parsed._replace(path=path, fragment="")
        return normalised.geturl()


def pages_to_dicts(pages: Iterable[Page]) -> list[dict[str, str]]:
    """Convert Page objects to dictionaries for persistence or tests."""
    return [page.to_dict() for page in pages]

