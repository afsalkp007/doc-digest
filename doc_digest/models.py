"""Pydantic data models for Map-Reduce document sectioning, intermediate mapping, and executive briefs."""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentSection(BaseModel):
    """An individual chunk or section of a long document."""
    section_index: int = Field(..., ge=0)
    title: str = Field(default="Section", description="Section header or generated label")
    content: str = Field(..., description="Raw text of the section")
    word_count: int = Field(default=0, ge=0)
    token_estimate: int = Field(default=0, ge=0)


class MappedSectionSummary(BaseModel):
    """Intermediate extraction from the Map phase for a single section."""
    section_index: int
    title: str
    key_takeaways: List[str] = Field(default_factory=list)
    quantitative_metrics: List[str] = Field(default_factory=list)
    identified_risks: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    raw_summary: str = Field(default="", description="Dense narrative distillation of the section")


class MetricItem(BaseModel):
    metric: str
    description: str
    impact: str = "Neutral"


class RiskItem(BaseModel):
    risk: str
    severity: str = "Medium"
    mitigation: str


class ActionItem(BaseModel):
    action: str
    owner: str = "Unassigned"
    priority: str = "P1"


class ExecutiveBrief(BaseModel):
    """Synthesized executive briefing produced in the Reduce phase."""
    document_title: str
    bluf_summary: str = Field(..., description="Bottom Line Up Front / 2-sentence executive summary")
    health_verdict: str = Field(default="Normal", description="Overall health, status, or urgency level")
    synthesized_takeaways: List[str] = Field(default_factory=list)
    key_metrics: List[MetricItem] = Field(default_factory=list)
    risk_register: List[RiskItem] = Field(default_factory=list)
    action_matrix: List[ActionItem] = Field(default_factory=list)
    full_synthesis_markdown: str = ""


class MapReduceReport(BaseModel):
    """Complete end-to-end report of the Map-Reduce pipeline."""
    document_title: str
    total_words: int
    total_sections: int
    mapped_sections: List[MappedSectionSummary]
    executive_brief: ExecutiveBrief
    map_phase_latency_ms: float = 0.0
    reduce_phase_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    compression_ratio_percent: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
