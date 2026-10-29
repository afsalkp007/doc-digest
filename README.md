# 📑 DocDigest

**Hierarchical Map-Reduce Document Summarizer & Executive Intelligence Synthesizer**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![UI](https://img.shields.io/badge/ui-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![LLM Engine](https://img.shields.io/badge/engine-Gemini%202.5%20Flash%20%7C%20Mock-green.svg)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/tests-17%2F17%20passing-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Overview

**DocDigest** is an enterprise-grade document intelligence engine that processes long-form reports, incident postmortems, financial disclosures, and compliance audits using a **Hierarchical Map-Reduce architecture**.

Standard single-pass LLM summarization often suffers from context-window degradation, "lost in the middle" attention decay, and unstructured narrative output. DocDigest resolves these bottlenecks by decomposing lengthy documents into semantic partitions, extracting structured analytical primitives in parallel (**Map Phase**), and synthesizing them into a high-density, board-ready briefing with quantitative metrics, a risk register, and a prioritized action matrix (**Reduce Phase**).

---

## 📐 Architecture & Pipeline

```text
       ┌────────────────────────────────────────────────────────┐
       │                 Source Document (Text)                 │
       │   (Outage Postmortem, 10-K, SOC2 Audit, Architecture)   │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
             ┌───────────────────────────────────────────┐
             │         DocumentChunker (Token Budget)    │
             │   - Markdown Heading Hierarchy (#, ##)    │
             │   - Bounded Token Window + Word Overlap   │
             └───────────────┬───────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   ┌─────────────────┐               ┌─────────────────┐
   │ Section Chunk 1 │      ...      │ Section Chunk N │
   └────────┬────────┘               └────────┬────────┘
            │                                 │
            ▼                                 ▼
   ┌─────────────────┐               ┌─────────────────┐
   │ Map Extractor 1 │               │ Map Extractor N │
   │ (Takeaways,     │               │ (Takeaways,     │
   │  Metrics, Risks)│               │  Metrics, Risks)│
   └────────┬────────┘               └────────┬────────┘
            │                                 │
            └────────────────┬────────────────┘
                             │
                             ▼
             ┌───────────────────────────────────────────┐
             │         Reduce Synthesizer Phase          │
             │   - Deduplication & Conflict Resolution   │
             │   - Board-Ready BLUF Narrative            │
             │   - Health Classification Verdict         │
             └───────────────┬───────────────────────────┘
                             │
                             ▼
       ┌────────────────────────────────────────────────────────┐
       │                Executive Intelligence Brief            │
       │  • Bottom Line Up Front (BLUF)                         │
       │  • Health Verdict (e.g. Critical Incident / Resolved)  │
       │  • Quantitative Metrics Impact Table                   │
       │  • Risk Register & Mitigations                         │
       │  • Priority Action Matrix (P0 / P1 / P2 with DRI)     │
       └────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

- **Hierarchical Map-Reduce Pipeline:** Overcomes context window limits and eliminates attention degradation across long documents.
- **Structured Pydantic Intelligence Schemas:** Extracts typed sections, quantitative figures with impact classification, risk registers, and ownership matrices.
- **Dual Inference Engine:**
  - **Google Gemini 2.5 Flash:** High-speed, structured JSON generation for production workloads.
  - **Zero-Crash Mock Provider:** Built-in deterministic extraction engine for offline development, CI/CD pipelines, and local testing without API keys.
- **Interactive Streamlit Web Dashboard:** Live telemetry, interactive Map section inspector, BLUF banner, metric cards, and instant download of Markdown briefs and raw JSON schemas.
- **Curated Benchmark Presets:** Pre-loaded enterprise benchmarks including SEV-1 Outage Postmortems, Q3 SaaS Financial Reviews, and SOC2 Type II Audits.

---

## 🚀 Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/afsalkp007/doc-digest.git
cd doc-digest
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Configure Environment (Optional for Live Gemini)

```bash
cp .env.example .env
```

Edit `.env` to include your Google AI Studio API key:

```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash
```

*(Note: If `GEMINI_API_KEY` is not provided, DocDigest automatically activates the Offline Mock Engine with zero crashes.)*

### 4. Launch the Web Dashboard

```bash
streamlit run doc_digest/app.py
```

Open your browser at `http://localhost:8501`.

---

## 💻 Programmatic Python API

DocDigest is designed as a standalone Python library that can be integrated directly into automated pipelines:

```python
from doc_digest import DocumentChunker, MapReduceSynthesizer, get_llm_provider

# 1. Initialize Chunker and Provider
chunker = DocumentChunker(max_words=350, overlap_words=30)
provider = get_llm_provider()  # Automatically picks Gemini or Mock
synthesizer = MapReduceSynthesizer(provider=provider, chunker=chunker)

# 2. Source Document Text
document = """
# Database Outage Incident
At 14:02 UTC, unindexed schema migration locked the primary database table.
The incident lasted 18 minutes, dropping 4,200 checkout sessions and $64,000 in revenue.

# Remediation
Deploy automated index validation in CI/CD and adjust Aurora failover timeout to 45 seconds.
"""

# 3. Execute Map-Reduce Pipeline
report = synthesizer.process(document, title="SEV-1 Incident Postmortem")

# 4. Access Executive Intelligence
print("Status Verdict:", report.executive_brief.health_verdict)
print("BLUF:", report.executive_brief.bluf_summary)
print("Key Metrics:", len(report.executive_brief.key_metrics))
print("Identified Risks:", len(report.executive_brief.risk_register))
print("Compression Ratio:", f"{report.compression_ratio_percent}%")

# 5. Export Publication-Ready Markdown
with open("executive_brief.md", "w") as f:
    f.write(report.executive_brief.full_synthesis_markdown)
```

---

## 📊 Core Data Schemas

All pipeline contracts are strictly typed using Pydantic v2:

| Model | Purpose | Key Attributes |
| :--- | :--- | :--- |
| `DocumentSection` | Partitioned chunk from source document | `section_index`, `title`, `content`, `word_count`, `token_estimate` |
| `MappedSectionSummary` | Intermediate extraction from Map phase | `key_takeaways`, `quantitative_metrics`, `identified_risks`, `action_items`, `raw_summary` |
| `ExecutiveBrief` | Synthesized board briefing from Reduce phase | `bluf_summary`, `health_verdict`, `key_metrics`, `risk_register`, `action_matrix` |
| `MapReduceReport` | End-to-end audit artifact and telemetry | `total_words`, `total_sections`, `mapped_sections`, `executive_brief`, `total_latency_ms`, `compression_ratio_percent` |

---

## 🧪 Running Automated Tests

Run the full unit test suite covering chunking logic, Pydantic schemas, providers, and end-to-end synthesis:

```bash
pytest -v
```

All 17 tests run in sub-second time without external network calls.

---

## 📁 Project Structure

```text
doc-digest/
├── doc_digest/
│   ├── __init__.py         # Package exports & runtime warning suppression
│   ├── models.py           # Pydantic data contracts (Section, Brief, Report)
│   ├── chunker.py          # Markdown & token-budgeted hierarchical chunker
│   ├── providers.py        # Gemini 2.5 Flash & Offline Mock providers
│   ├── synthesizer.py      # Map-Reduce pipeline orchestration & prompts
│   ├── presets.py          # Curated enterprise benchmark documents
│   └── app.py              # Streamlit interactive web dashboard
├── tests/
│   ├── test_chunker.py     # Heading splitting & token budget tests
│   ├── test_models.py      # Schema validation & serialization tests
│   ├── test_providers.py   # LLM provider & fallback tests
│   └── test_synthesizer.py # Map-Reduce integration tests
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules (.env, .venv, __pycache__)
├── pyproject.toml          # Project metadata and package setup
├── requirements.txt        # Production & development dependencies
├── LICENSE                 # MIT License (Afsal)
└── README.md               # Technical documentation
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
