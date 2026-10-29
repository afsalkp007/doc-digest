"""Unit tests for DocDigest data schemas and validation models."""

import pytest
from pydantic import ValidationError
from doc_digest.models import (
    DocumentSection,
    MappedSectionSummary,
    MetricItem,
    RiskItem,
    ActionItem,
    ExecutiveBrief,
    MapReduceReport,
)


def test_document_section_creation():
    sec = DocumentSection(
        section_index=0,
        title="Infrastructure Overview",
        content="This section details server configurations.",
        word_count=5,
        token_estimate=7,
    )
    assert sec.section_index == 0
    assert sec.title == "Infrastructure Overview"
    assert sec.word_count == 5
    assert sec.token_estimate == 7


def test_document_section_negative_index_fails():
    with pytest.raises(ValidationError):
        DocumentSection(
            section_index=-1,
            title="Invalid",
            content="Error expected",
        )


def test_mapped_section_summary():
    mapped = MappedSectionSummary(
        section_index=1,
        title="Incident Timeline",
        key_takeaways=["Service degraded at 14:00 UTC", "Resolved at 14:18 UTC"],
        quantitative_metrics=["Downtime: 18 minutes", "Error rate: 68%"],
        identified_risks=["Database single point of failure"],
        action_items=["Automate failover to read replica"],
        raw_summary="Primary database locked during migration.",
    )
    assert mapped.section_index == 1
    assert len(mapped.key_takeaways) == 2
    assert len(mapped.quantitative_metrics) == 2
    assert mapped.identified_risks[0] == "Database single point of failure"
    assert mapped.action_items[0] == "Automate failover to read replica"


def test_executive_brief_and_report_serialization():
    brief = ExecutiveBrief(
        document_title="Q3 Review",
        bluf_summary="Q3 revenue grew 38% YoY reaching $52.4M with healthy retention.",
        health_verdict="Healthy",
        synthesized_takeaways=["Strong enterprise adoption"],
        key_metrics=[MetricItem(metric="$52.4M", description="ARR", impact="Positive")],
        risk_register=[RiskItem(risk="Compute costs", severity="High", mitigation="Semantic cache")],
        action_matrix=[ActionItem(action="Deploy cache", owner="Eng Lead", priority="P0")],
        full_synthesis_markdown="# Executive Brief\n\nAll systems nominal.",
    )

    report = MapReduceReport(
        document_title="Q3 Review",
        total_words=1200,
        total_sections=4,
        mapped_sections=[],
        executive_brief=brief,
        map_phase_latency_ms=120.5,
        reduce_phase_latency_ms=85.0,
        total_latency_ms=205.5,
        compression_ratio_percent=78.2,
    )

    assert report.total_words == 1200
    assert report.total_sections == 4
    assert report.compression_ratio_percent == 78.2
    assert report.executive_brief.health_verdict == "Healthy"

    # Verify JSON export
    raw_json = report.model_dump_json() if hasattr(report, "model_dump_json") else report.json()
    assert "Q3 Review" in raw_json
    assert "$52.4M" in raw_json
