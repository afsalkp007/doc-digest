"""DocDigest - Hierarchical Map-Reduce Document Summarizer & Executive Intelligence Synthesizer."""

import warnings

warnings.filterwarnings("ignore")

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
from doc_digest.providers import BaseLLM, GeminiProvider, MockProvider, get_llm_provider
from doc_digest.synthesizer import MapReduceSynthesizer

__version__ = "0.1.0"

__all__ = [
    "DocumentSection",
    "MappedSectionSummary",
    "MetricItem",
    "RiskItem",
    "ActionItem",
    "ExecutiveBrief",
    "MapReduceReport",
    "DocumentChunker",
    "BaseLLM",
    "GeminiProvider",
    "MockProvider",
    "get_llm_provider",
    "MapReduceSynthesizer",
]
