"""Map-Reduce document summarization and executive intelligence synthesizer."""

import json
import logging
import re
import time
from typing import List, Optional, Callable, Dict, Any

from doc_digest.models import (
    DocumentSection,
    MappedSectionSummary,
    MetricItem,
    RiskItem,
    ActionItem,
    ExecutiveBrief,
    MapReduceReport,
)
from doc_digest.chunker import DocumentChunker
from doc_digest.providers import BaseLLM, get_llm_provider

logger = logging.getLogger(__name__)


MAP_SECTION_PROMPT = """You are an expert executive document analyst executing the MAP phase of a hierarchical Map-Reduce document summarization pipeline.

Analyze the following document section and extract structured operational intelligence.
Section Index: {section_index}
Section Title: {title}

--- SECTION TEXT ---
{content}
--------------------

Respond with ONLY a valid JSON object matching the following structure:
{{
  "key_takeaways": [
    "Key takeaway 1",
    "Key takeaway 2"
  ],
  "quantitative_metrics": [
    "Metric name: Value and trend (e.g., ARR: $52.4M (+38% YoY))"
  ],
  "identified_risks": [
    "Risk or bottleneck identified in this section"
  ],
  "action_items": [
    "Recommended or planned action item with clear intent"
  ],
  "raw_summary": "A 2-3 sentence dense narrative distillation preserving specific names, numbers, and technical or business facts."
}}
"""

REDUCE_PROMPT = """You are a senior executive intelligence officer executing the REDUCE phase of a hierarchical Map-Reduce document summarization pipeline.

You have received structured intermediate extractions from {total_sections} sections of the document entitled: "{title}".

--- INTERMEDIATE EXTRACTED SUMMARIES ---
{summaries_text}
----------------------------------------

Synthesize these section-level summaries into a unified, non-redundant, board-ready Executive Briefing.

Respond with ONLY a valid JSON object matching the following structure:
{{
  "bluf_summary": "Bottom Line Up Front: 2-3 sentence high-impact summary synthesizing overall outcome, key driver, and primary takeaway.",
  "health_verdict": "Clear classification (e.g., 'Critical Incident (Resolved)', 'Healthy / On Track', 'At Risk - Cost Growth', 'Strong Topline / Margin Pressure')",
  "synthesized_takeaways": [
    "Consolidated strategic takeaway 1",
    "Consolidated strategic takeaway 2",
    "Consolidated strategic takeaway 3"
  ],
  "key_metrics": [
    {{
      "metric": "Key figure (e.g., '$64,000' or '18 min' or '92%')",
      "description": "What this figure represents",
      "impact": "Positive, Negative, or Neutral"
    }}
  ],
  "risk_register": [
    {{
      "risk": "Core risk or failure mode",
      "severity": "High, Medium, or Low",
      "mitigation": "Targeted mitigation or remediation step"
    }}
  ],
  "action_matrix": [
    {{
      "action": "Concrete operational task",
      "owner": "Role, Team, or DRI (e.g., 'Infrastructure Team', 'Product VP')",
      "priority": "P0, P1, or P2"
    }}
  ]
}}
"""


class MapReduceSynthesizer:
    """Orchestrates Map-Reduce hierarchical document summarization."""

    def __init__(
        self,
        provider: Optional[BaseLLM] = None,
        chunker: Optional[DocumentChunker] = None,
    ):
        self.provider = provider or get_llm_provider()
        self.chunker = chunker or DocumentChunker()

    def _clean_json_text(self, text: str) -> str:
        """Strip markdown ticks and whitespace from LLM output."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    def map_section(self, section: DocumentSection) -> MappedSectionSummary:
        """Map phase: extract structured facts, risks, and metrics from a single section."""
        prompt = MAP_SECTION_PROMPT.format(
            section_index=section.section_index,
            title=section.title,
            content=section.content,
        )

        try:
            raw_response = self.provider.generate(prompt, json_mode=True)
            cleaned = self._clean_json_text(raw_response)
            data = json.loads(cleaned)

            return MappedSectionSummary(
                section_index=section.section_index,
                title=section.title,
                key_takeaways=data.get("key_takeaways", []),
                quantitative_metrics=data.get("quantitative_metrics", []),
                identified_risks=data.get("identified_risks", []),
                action_items=data.get("action_items", []),
                raw_summary=data.get("raw_summary", section.content[:200]),
            )
        except Exception as e:
            logger.warning("Error mapping section %d: %s. Using heuristic fallback.", section.section_index, e)
            lines = [l.strip() for l in section.content.split("\n") if l.strip()]
            first_line = lines[0] if lines else section.title
            return MappedSectionSummary(
                section_index=section.section_index,
                title=section.title,
                key_takeaways=[first_line[:120]],
                quantitative_metrics=[],
                identified_risks=[],
                action_items=[],
                raw_summary=section.content[:240],
            )

    def reduce_summaries(
        self,
        summaries: List[MappedSectionSummary],
        title: str = "Document",
    ) -> ExecutiveBrief:
        """Reduce phase: aggregate all intermediate section summaries into an ExecutiveBrief."""
        if not summaries:
            return ExecutiveBrief(
                document_title=title,
                bluf_summary="No document content provided to synthesize.",
                health_verdict="Empty",
                synthesized_takeaways=[],
                key_metrics=[],
                risk_register=[],
                action_matrix=[],
                full_synthesis_markdown="# Executive Brief\n\nNo content available.",
            )

        # Build concatenated summaries representation
        summary_blocks = []
        for s in summaries:
            block = (
                f"### Section {s.section_index + 1}: {s.title}\n"
                f"- Summary: {s.raw_summary}\n"
                f"- Takeaways: {'; '.join(s.key_takeaways) if s.key_takeaways else 'None'}\n"
                f"- Metrics: {'; '.join(s.quantitative_metrics) if s.quantitative_metrics else 'None'}\n"
                f"- Risks: {'; '.join(s.identified_risks) if s.identified_risks else 'None'}\n"
                f"- Actions: {'; '.join(s.action_items) if s.action_items else 'None'}"
            )
            summary_blocks.append(block)

        summaries_text = "\n\n".join(summary_blocks)
        prompt = REDUCE_PROMPT.format(
            total_sections=len(summaries),
            title=title,
            summaries_text=summaries_text,
        )

        try:
            raw_response = self.provider.generate(prompt, json_mode=True)
            cleaned = self._clean_json_text(raw_response)
            data = json.loads(cleaned)

            key_metrics = [
                MetricItem(**m) if isinstance(m, dict) else MetricItem(metric=str(m), description="", impact="Neutral")
                for m in data.get("key_metrics", [])
            ]
            risk_register = [
                RiskItem(**r) if isinstance(r, dict) else RiskItem(risk=str(r), severity="Medium", mitigation="TBD")
                for r in data.get("risk_register", [])
            ]
            action_matrix = [
                ActionItem(**a) if isinstance(a, dict) else ActionItem(action=str(a), owner="Unassigned", priority="P1")
                for a in data.get("action_matrix", [])
            ]

            brief = ExecutiveBrief(
                document_title=title,
                bluf_summary=data.get("bluf_summary", "Synthesis complete."),
                health_verdict=data.get("health_verdict", "Normal"),
                synthesized_takeaways=data.get("synthesized_takeaways", []),
                key_metrics=key_metrics,
                risk_register=risk_register,
                action_matrix=action_matrix,
            )
            brief.full_synthesis_markdown = self._generate_markdown(brief)
            return brief

        except Exception as e:
            logger.warning("Error reducing summaries: %s. Using fallback synthesis.", e)
            fallback_takeaways = [t for s in summaries for t in s.key_takeaways[:2]]
            fallback_metrics = [
                MetricItem(metric=m.split(":")[0], description=m, impact="Neutral")
                for s in summaries
                for m in s.quantitative_metrics[:2]
            ]
            fallback_risks = [
                RiskItem(risk=r, severity="Medium", mitigation="Follow up in sprint planning")
                for s in summaries
                for r in s.identified_risks[:2]
            ]
            fallback_actions = [
                ActionItem(action=a, owner="Team", priority="P1")
                for s in summaries
                for a in s.action_items[:2]
            ]

            brief = ExecutiveBrief(
                document_title=title,
                bluf_summary=f"Analysis of {len(summaries)} sections completed across '{title}'. Review key metrics and risk register for operational execution.",
                health_verdict="Synthesized / Operational Review",
                synthesized_takeaways=fallback_takeaways[:5],
                key_metrics=fallback_metrics[:5],
                risk_register=fallback_risks[:5],
                action_matrix=fallback_actions[:5],
            )
            brief.full_synthesis_markdown = self._generate_markdown(brief)
            return brief

    def _generate_markdown(self, brief: ExecutiveBrief) -> str:
        """Render an ExecutiveBrief as a publication-ready Markdown report."""
        lines = [
            f"# Executive Intelligence Brief: {brief.document_title}",
            f"**Status / Health Verdict:** `{brief.health_verdict}`\n",
            "## 📌 Bottom Line Up Front (BLUF)",
            brief.bluf_summary,
            "\n## 🎯 Strategic Takeaways",
        ]
        for t in brief.synthesized_takeaways:
            lines.append(f"- {t}")

        if brief.key_metrics:
            lines.append("\n## 📊 Quantitative Metrics")
            lines.append("| Metric | Description | Impact |")
            lines.append("| :--- | :--- | :--- |")
            for m in brief.key_metrics:
                lines.append(f"| **{m.metric}** | {m.description} | `{m.impact}` |")

        if brief.risk_register:
            lines.append("\n## ⚠️ Risk Register")
            lines.append("| Identified Risk | Severity | Targeted Mitigation |")
            lines.append("| :--- | :---: | :--- |")
            for r in brief.risk_register:
                lines.append(f"| **{r.risk}** | `{r.severity}` | {r.mitigation} |")

        if brief.action_matrix:
            lines.append("\n## ⚡ Priority Action Matrix")
            lines.append("| Priority | Action Item | Owner |")
            lines.append("| :---: | :--- | :--- |")
            for a in brief.action_matrix:
                lines.append(f"| `{a.priority}` | {a.action} | **{a.owner}** |")

        return "\n".join(lines)

    def process(
        self,
        document_text: str,
        title: str = "Document",
        on_progress: Optional[Callable[[str, int, int], None]] = None,
    ) -> MapReduceReport:
        """Execute end-to-end Map-Reduce summarization pipeline."""
        start_time = time.time()

        # Step 1: Chunking
        sections = self.chunker.chunk_document(document_text, title=title)
        total_sections = len(sections)

        # Step 2: Map Phase
        map_start = time.time()
        mapped_sections: List[MappedSectionSummary] = []
        for i, section in enumerate(sections):
            if on_progress:
                on_progress("map", i + 1, total_sections)
            mapped = self.map_section(section)
            mapped_sections.append(mapped)
        map_latency_ms = (time.time() - map_start) * 1000

        # Step 3: Reduce Phase
        if on_progress:
            on_progress("reduce", 1, 1)
        reduce_start = time.time()
        brief = self.reduce_summaries(mapped_sections, title=title)
        reduce_latency_ms = (time.time() - reduce_start) * 1000

        total_latency_ms = (time.time() - start_time) * 1000

        # Compression calculation
        input_word_count = sum(s.word_count for s in sections)
        output_word_count = len(brief.full_synthesis_markdown.split())
        compression_ratio = 0.0
        if input_word_count > 0:
            compression_ratio = max(
                0.0,
                round((1.0 - (output_word_count / input_word_count)) * 100, 1),
            )

        return MapReduceReport(
            document_title=title,
            total_words=input_word_count,
            total_sections=total_sections,
            mapped_sections=mapped_sections,
            executive_brief=brief,
            map_phase_latency_ms=round(map_latency_ms, 2),
            reduce_phase_latency_ms=round(reduce_latency_ms, 2),
            total_latency_ms=round(total_latency_ms, 2),
            compression_ratio_percent=compression_ratio,
        )
