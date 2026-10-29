"""Unit tests for Map-Reduce synthesizer pipeline."""

import pytest
from doc_digest.synthesizer import MapReduceSynthesizer
from doc_digest.providers import MockProvider
from doc_digest.models import DocumentSection, MappedSectionSummary


def test_synthesizer_map_single_section():
    synth = MapReduceSynthesizer(provider=MockProvider())
    section = DocumentSection(
        section_index=0,
        title="Database Incident",
        content="Database failover incident caused 18 minutes of downtime.",
        word_count=8,
        token_estimate=10,
    )
    mapped = synth.map_section(section)

    assert isinstance(mapped, MappedSectionSummary)
    assert mapped.section_index == 0
    assert mapped.title == "Database Incident"
    assert len(mapped.key_takeaways) > 0
    assert len(mapped.quantitative_metrics) > 0


def test_synthesizer_reduce_summaries():
    synth = MapReduceSynthesizer(provider=MockProvider())
    summaries = [
        MappedSectionSummary(
            section_index=0,
            title="Outage Summary",
            key_takeaways=["18 min downtime"],
            quantitative_metrics=["$64,000 lost"],
            identified_risks=["Single point of failure"],
            action_items=["Automate failover"],
            raw_summary="Outage due to unindexed table migration.",
        )
    ]
    brief = synth.reduce_summaries(summaries, title="Outage Postmortem")

    assert brief.document_title == "Outage Postmortem"
    assert len(brief.bluf_summary) > 0
    assert len(brief.key_metrics) > 0
    assert len(brief.risk_register) > 0
    assert len(brief.action_matrix) > 0
    assert "# Executive Intelligence Brief" in brief.full_synthesis_markdown


def test_synthesizer_reduce_empty_summaries():
    synth = MapReduceSynthesizer(provider=MockProvider())
    brief = synth.reduce_summaries([], title="Empty Document")

    assert brief.document_title == "Empty Document"
    assert "No document content" in brief.bluf_summary
    assert brief.health_verdict == "Empty"


def test_synthesizer_full_process_with_progress():
    synth = MapReduceSynthesizer(provider=MockProvider())
    sample_text = """# Section 1: Growth
Financial review showed strong ARR growth of 38% reaching $52.4M.

# Section 2: Headwinds
Inference compute costs expanded to $1.15M per month, squeezing gross margins.
"""
    progress_stages = []

    def on_progress(stage, current, total):
        progress_stages.append((stage, current, total))

    report = synth.process(sample_text, title="Quarterly Review", on_progress=on_progress)

    assert report.total_sections == 2
    assert report.total_words > 0
    assert report.total_latency_ms >= 0
    assert len(report.mapped_sections) == 2
    assert report.executive_brief.document_title == "Quarterly Review"
    assert len(progress_stages) >= 3  # 2 map steps + 1 reduce step
    assert ("reduce", 1, 1) in progress_stages
