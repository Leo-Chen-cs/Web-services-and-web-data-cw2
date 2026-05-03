"""Inverted index construction and persistence."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

from .crawler import Page


TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?", re.IGNORECASE)
SCHEMA_VERSION = 1


def tokenize(text: str) -> list[str]:
    """Return lowercase word tokens with punctuation removed."""
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text or "")]


def build_index(documents: Iterable[Page | Mapping[str, str]]) -> dict[str, Any]:
    """Build an inverted index containing term frequency and positions."""
    docs_by_url: dict[str, dict[str, Any]] = {}
    postings: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

    for raw_document in documents:
        document = _coerce_document(raw_document)
        tokens = tokenize(document["text"])
        docs_by_url[document["url"]] = {
            "url": document["url"],
            "title": document["title"],
            "length": len(tokens),
        }

        positions_by_term: dict[str, list[int]] = defaultdict(list)
        for position, token in enumerate(tokens):
            positions_by_term[token].append(position)

        for term, positions in positions_by_term.items():
            postings[term][document["url"]] = {
                "frequency": len(positions),
                "positions": positions,
            }

    document_count = len(docs_by_url)
    terms = {
        term: {
            "document_frequency": len(term_postings),
            "idf": _idf(document_count, len(term_postings)),
            "postings": dict(sorted(term_postings.items())),
        }
        for term, term_postings in sorted(postings.items())
    }

    return {
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "document_count": document_count,
            "term_count": len(terms),
        },
        "documents": dict(sorted(docs_by_url.items())),
        "terms": terms,
    }


def save_index(index: Mapping[str, Any], path: str | Path) -> None:
    """Save an index as readable JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(index, file, indent=2, ensure_ascii=False, sort_keys=True)
        file.write("\n")


def load_index(path: str | Path) -> dict[str, Any]:
    """Load a JSON index from disk and validate its top-level shape."""
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as file:
        index = json.load(file)

    if not isinstance(index, dict) or "terms" not in index or "documents" not in index:
        raise ValueError(f"{input_path} is not a valid index file")
    return index


def term_statistics(index: Mapping[str, Any], term: str) -> dict[str, Any] | None:
    """Return posting data for one normalised term."""
    tokens = tokenize(term)
    if len(tokens) != 1:
        return None
    return index.get("terms", {}).get(tokens[0])


def _coerce_document(document: Page | Mapping[str, str]) -> dict[str, str]:
    if isinstance(document, Page):
        return document.to_dict()

    missing = {"url", "title", "text"} - set(document)
    if missing:
        missing_values = ", ".join(sorted(missing))
        raise ValueError(f"Document is missing required fields: {missing_values}")

    return {
        "url": str(document["url"]),
        "title": str(document["title"]),
        "text": str(document["text"]),
    }


def _idf(document_count: int, document_frequency: int) -> float:
    if document_count == 0 or document_frequency == 0:
        return 0.0
    return math.log((1 + document_count) / (1 + document_frequency)) + 1


def term_frequency_summary(index: Mapping[str, Any], term: str) -> Counter[str]:
    """Return a URL-to-frequency counter for one term."""
    stats = term_statistics(index, term)
    if not stats:
        return Counter()
    return Counter(
        {
            url: posting["frequency"]
            for url, posting in stats.get("postings", {}).items()
        }
    )

