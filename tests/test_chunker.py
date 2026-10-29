"""Unit tests for hierarchical DocumentChunker."""

import pytest
from doc_digest.chunker import DocumentChunker


def test_chunker_empty_input():
    chunker = DocumentChunker()
    assert chunker.chunk("") == []
    assert chunker.chunk("   \n\n  ") == []


def test_chunker_markdown_headings():
    chunker = DocumentChunker(max_words=200, overlap_words=20)
    doc = """# Introduction
This is the executive summary introduction.

# Financial Performance
Revenue increased by 30% this quarter across all product lines.

## Operational Risks
Supply chain delays impacted delivery times in Europe.
"""
    sections = chunker.chunk(doc)
    assert len(sections) == 3
    assert sections[0].title == "Introduction"
    assert "executive summary" in sections[0].content
    assert sections[1].title == "Financial Performance"
    assert "Revenue increased" in sections[1].content
    assert sections[2].title == "Operational Risks"
    assert "Supply chain delays" in sections[2].content


def test_chunker_paragraph_splitting_without_headers():
    chunker = DocumentChunker(max_words=25, overlap_words=5)
    p1 = "Paragraph one with several words designed to consume token budget and test splitting behavior cleanly."
    p2 = "Paragraph two containing more content to push the word count past the twenty-five word threshold."
    p3 = "Paragraph three concluding the sequence of text segments for testing."

    doc = f"{p1}\n\n{p2}\n\n{p3}"
    sections = chunker.chunk(doc, default_title="Document")

    assert len(sections) >= 2
    for s in sections:
        assert s.word_count > 0
        assert s.token_estimate > 0


def test_chunker_subsplit_oversized_markdown_section():
    chunker = DocumentChunker(max_words=30, overlap_words=5)
    long_content = " ".join([f"word{i}" for i in range(100)])
    doc = f"# Large Section\n\n{long_content}"

    sections = chunker.chunk(doc)
    # The oversized section should be partitioned into parts
    assert len(sections) > 1
    assert "Large Section (Part" in sections[0].title or "Large Section" in sections[0].title


def test_chunk_document_alias():
    chunker = DocumentChunker()
    doc = "# Heading\nContent here."
    s1 = chunker.chunk(doc)
    s2 = chunker.chunk_document(doc)
    assert len(s1) == len(s2) == 1
    assert s1[0].title == s2[0].title
