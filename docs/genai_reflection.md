# GenAI Critical Reflection Notes

This document provides concise points for the required GenAI section of the
coursework video.

## Tools Used

I used generative AI as a coding assistant for project planning, implementation
ideas, test-case design, and README drafting.

## Where AI Helped

AI helped turn the coursework requirements into a modular design:

- `crawler.py` for crawling and HTML parsing
- `indexer.py` for tokenisation and inverted-index construction
- `search.py` for query handling and ranking
- `main.py` for the CLI

This made the project easier to test because each module has one main
responsibility.

## Where AI Needed Correction

Some AI suggestions were too simplistic. For example, a crawler can easily pass
basic tests while still being impolite if it sends requests too quickly. I
checked this against the brief and implemented a six-second politeness window.
I also avoided real sleeps in tests by injecting fake sleep and time functions.

Another issue was ranking. A basic answer might only return pages in arbitrary
dictionary order. I added TF-IDF scoring so `find` returns more relevant pages
first.

## Quality And Correctness Checks

I reviewed the generated ideas manually and verified them with `pytest`. The
tests mock network responses to check duplicate URL handling, network errors,
token positions, case-insensitive indexing, AND queries, and CLI edge cases.

## Learning Impact

Using AI saved time on scaffolding, but it did not replace understanding. The
most useful learning came from debugging and explaining the final design:
normalising URLs, respecting the politeness rule, storing positions in posting
lists, and calculating TF-IDF scores.

## Development Process Impact

AI improved time management by producing an initial structure quickly. The main
risk was over-trusting generated code, so the workflow used tests and manual
review to catch missing requirements before submission.

