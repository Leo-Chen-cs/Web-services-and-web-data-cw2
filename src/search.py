"""Search and display helpers for an inverted index."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from typing import Any, Mapping

from .indexer import tokenize


@dataclass(frozen=True)
class SearchResult:
    """A ranked search hit."""

    url: str
    title: str
    score: float
    frequencies: dict[str, int]


@dataclass(frozen=True)
class QueryGroup:
    """A token group from a query; multi-token groups are phrase queries."""

    raw: str
    tokens: tuple[str, ...]

    @property
    def is_phrase(self) -> bool:
        """Return whether this group should match consecutive positions."""
        return len(self.tokens) > 1


class SearchEngine:
    """Run AND queries over an inverted index with TF-IDF ranking."""

    def __init__(self, index: Mapping[str, Any] | None = None) -> None:
        self.index: Mapping[str, Any] | None = index

    @property
    def loaded(self) -> bool:
        """Return whether an index is currently available."""
        return self.index is not None

    def set_index(self, index: Mapping[str, Any]) -> None:
        """Replace the active index."""
        self.index = index

    def find(self, raw_terms: list[str] | tuple[str, ...]) -> list[SearchResult]:
        """Find documents containing all query terms, ranked by TF-IDF score."""
        index = self._require_index()
        groups = self._normalise_query(raw_terms)
        if not groups:
            return []

        terms = self._flatten_groups(groups)
        term_data = index.get("terms", {})
        if any(term not in term_data for term in terms):
            return []

        matching_urls: set[str] | None = None
        for term in terms:
            urls = set(term_data[term].get("postings", {}))
            matching_urls = urls if matching_urls is None else matching_urls & urls

        if not matching_urls:
            return []

        documents = index.get("documents", {})
        results: list[SearchResult] = []
        for url in matching_urls:
            phrase_counts = self._phrase_counts_for_url(groups, url, term_data)
            if phrase_counts is None:
                continue

            score = 0.0
            frequencies: dict[str, int] = {}
            for term in terms:
                stats = term_data[term]
                posting = stats["postings"][url]
                frequency = int(posting["frequency"])
                frequencies[term] = frequency
                score += frequency * float(stats.get("idf", 1.0))
            frequencies.update(phrase_counts)

            document = documents.get(url, {})
            results.append(
                SearchResult(
                    url=url,
                    title=document.get("title", url),
                    score=round(score, 6),
                    frequencies=frequencies,
                )
            )

        return sorted(results, key=lambda result: (-result.score, result.url))

    def print_term(self, raw_term: str) -> str:
        """Return a human-readable posting list for one term."""
        index = self._require_index()
        tokens = tokenize(raw_term)
        if len(tokens) != 1:
            return "Please provide exactly one searchable word."

        term = tokens[0]
        stats = index.get("terms", {}).get(term)
        if not stats:
            suggestions = self.suggest(term)
            hint = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
            return f"No index entries found for '{term}'.{hint}"

        lines = [
            f"Term: {term}",
            f"Document frequency: {stats['document_frequency']}",
            f"IDF: {float(stats.get('idf', 0.0)):.4f}",
        ]
        for url, posting in stats.get("postings", {}).items():
            positions = ", ".join(str(position) for position in posting["positions"])
            lines.append(
                f"- {url}: frequency={posting['frequency']}; positions=[{positions}]"
            )
        return "\n".join(lines)

    def suggest(self, raw_term: str, limit: int = 3) -> list[str]:
        """Suggest close vocabulary matches for a missing term."""
        index = self._require_index()
        tokens = tokenize(raw_term)
        if not tokens:
            return []
        vocabulary = list(index.get("terms", {}).keys())
        return get_close_matches(tokens[0], vocabulary, n=limit, cutoff=0.75)

    def _normalise_query(
        self,
        raw_terms: list[str] | tuple[str, ...],
    ) -> list[QueryGroup]:
        groups: list[QueryGroup] = []
        seen: set[tuple[str, ...]] = set()
        for raw_term in raw_terms:
            tokens = tuple(tokenize(raw_term))
            if tokens and tokens not in seen:
                groups.append(QueryGroup(raw=raw_term, tokens=tokens))
                seen.add(tokens)
        return groups

    def _flatten_groups(self, groups: list[QueryGroup]) -> list[str]:
        terms: list[str] = []
        seen: set[str] = set()
        for group in groups:
            for token in group.tokens:
                if token not in seen:
                    terms.append(token)
                    seen.add(token)
        return terms

    def _phrase_counts_for_url(
        self,
        groups: list[QueryGroup],
        url: str,
        term_data: Mapping[str, Any],
    ) -> dict[str, int] | None:
        phrase_counts: dict[str, int] = {}
        for group in groups:
            if not group.is_phrase:
                continue

            count = self._count_phrase_matches(group.tokens, url, term_data)
            if count == 0:
                return None
            phrase_counts[" ".join(group.tokens)] = count
        return phrase_counts

    def _count_phrase_matches(
        self,
        phrase_tokens: tuple[str, ...],
        url: str,
        term_data: Mapping[str, Any],
    ) -> int:
        first_token, *remaining_tokens = phrase_tokens
        first_positions = term_data[first_token]["postings"][url]["positions"]
        remaining_position_sets = [
            set(term_data[token]["postings"][url]["positions"])
            for token in remaining_tokens
        ]

        matches = 0
        for start_position in first_positions:
            if all(
                start_position + offset + 1 in positions
                for offset, positions in enumerate(remaining_position_sets)
            ):
                matches += 1
        return matches

    def _require_index(self) -> Mapping[str, Any]:
        if self.index is None:
            raise RuntimeError("No index loaded. Run 'build' or 'load' first.")
        return self.index


def format_results(results: list[SearchResult]) -> str:
    """Format ranked search results for the command line."""
    if not results:
        return "No matching pages found."

    lines = []
    for rank, result in enumerate(results, start=1):
        frequencies = ", ".join(
            f"{term}={frequency}"
            for term, frequency in sorted(result.frequencies.items())
        )
        lines.append(
            f"{rank}. {result.title}\n"
            f"   URL: {result.url}\n"
            f"   Score: {result.score:.4f}; frequencies: {frequencies}"
        )
    return "\n".join(lines)
