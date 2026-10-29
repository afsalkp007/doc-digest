"""DocDigest - Streamlit Web Dashboard for Hierarchical Map-Reduce Document Summarization."""

import os
import json
import streamlit as st

from doc_digest.models import MapReduceReport
from doc_digest.chunker import DocumentChunker
from doc_digest.providers import GeminiProvider, MockProvider
from doc_digest.synthesizer import MapReduceSynthesizer
from doc_digest.presets import PRESET_DOCUMENTS

# Page Configuration
st.set_page_config(
    page_title="DocDigest | Map-Reduce Document Summarizer",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    .bluf-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #ffffff;
        padding: 20px 24px;
        border-radius: 10px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .bluf-box h3 {
        color: #ffffff !important;
        margin-top: 0;
        font-size: 1.25rem;
    }
    .bluf-box p {
        color: #f1f5f9;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-bottom: 0;
    }
    .badge-p0 {
        background-color: #fee2e2;
        color: #991b1b;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
    }
    .badge-p1 {
        background-color: #fef3c7;
        color: #92400e;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
    }
    .badge-p2 {
        background-color: #e0f2fe;
        color: #075985;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar Configuration
st.sidebar.title("📑 DocDigest")
st.sidebar.caption("Hierarchical Map-Reduce Document Intelligence")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ LLM Configuration")

provider_choice = st.sidebar.radio(
    "Inference Engine",
    ["Mock Engine (Offline / Instant)", "Google Gemini 2.5 Flash"],
    index=0,
    help="Mock engine works instantly without an API key. Gemini uses Google's latest flash model.",
)

api_key = ""
if provider_choice == "Google Gemini 2.5 Flash":
    default_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.sidebar.text_input(
        "Gemini API Key",
        value=default_key,
        type="password",
        help="Enter your Google AI Studio API key.",
    )
    if not api_key:
        st.sidebar.warning("⚠️ Enter an API key or switch to Mock Engine.")

st.sidebar.markdown("---")
st.sidebar.subheader("✂️ Chunker Parameters")
max_words = st.sidebar.slider("Max Words per Chunk", min_value=150, max_value=800, value=350, step=50)
overlap_words = st.sidebar.slider("Chunk Overlap Words", min_value=0, max_value=100, value=30, step=10)

st.sidebar.markdown("---")
st.sidebar.subheader("📚 Curated Presets")
preset_name = st.sidebar.selectbox(
    "Choose a Benchmark Document",
    ["Custom Document"] + list(PRESET_DOCUMENTS.keys()),
    index=1,
)

# Load selected preset or default
if preset_name in PRESET_DOCUMENTS:
    preset_data = PRESET_DOCUMENTS[preset_name]
    default_doc_title = preset_data["title"]
    default_doc_content = preset_data["content"]
else:
    default_doc_title = "Strategic Operations Report"
    default_doc_content = "# Section 1: Overview\n\nEnter your document text here..."

# Main Header
st.title("📑 DocDigest")
st.markdown(
    "**Hierarchical Map-Reduce Document Summarizer & Executive Intelligence Synthesizer.** "
    "Scales across long documents by chunking content, extracting parallel section insights in the **Map** phase, "
    "and synthesizing a cohesive, board-level briefing in the **Reduce** phase."
)

col1, col2 = st.columns([3, 1])
with col1:
    doc_title = st.text_input("Document Title", value=default_doc_title)
with col2:
    st.write("")
    st.write("")
    if st.button("🔄 Reset to Preset", use_container_width=True):
        st.session_state.clear()
        st.rerun()

doc_text = st.text_area(
    "Document Content (Markdown / Plain Text)",
    value=default_doc_content,
    height=280,
    help="Supports Markdown headers (#, ##, ###) for semantic section boundaries.",
)

# Quick stats about input text
input_words = len(doc_text.split())
input_chars = len(doc_text)
input_tokens_est = int(input_words * 1.3)

st.caption(
    f"📊 Document Metrics: **{input_words:,} words** | **{input_chars:,} characters** | "
    f"**~{input_tokens_est:,} estimated tokens**"
)

# Execution Action
run_pipeline = st.button("🚀 Run Map-Reduce Synthesis", type="primary", use_container_width=True)

if run_pipeline:
    if not doc_text.strip():
        st.error("Please provide document text before running synthesis.")
        st.stop()

    # Initialize Provider
    if provider_choice == "Google Gemini 2.5 Flash":
        if not api_key:
            st.error("Gemini API key is required. Please provide it in the sidebar.")
            st.stop()
        provider = GeminiProvider(api_key=api_key)
    else:
        provider = MockProvider()

    chunker = DocumentChunker(max_words=max_words, overlap_words=overlap_words)
    synthesizer = MapReduceSynthesizer(provider=provider, chunker=chunker)

    progress_bar = st.progress(0, text="Initializing Map-Reduce Pipeline...")

    def progress_callback(stage: str, current: int, total: int):
        if stage == "map":
            pct = int((current / max(total, 1)) * 75)
            progress_bar.progress(pct, text=f"🗺️ Map Phase: Extracting section {current} of {total}...")
        elif stage == "reduce":
            progress_bar.progress(85, text="⚡ Reduce Phase: Synthesizing executive briefing...")

    with st.spinner("Processing document through Map-Reduce pipeline..."):
        report = synthesizer.process(
            document_text=doc_text,
            title=doc_title,
            on_progress=progress_callback,
        )
        progress_bar.progress(100, text="✅ Map-Reduce Synthesis Complete!")

    st.session_state["report"] = report

# Render results if available
if "report" in st.session_state:
    report: MapReduceReport = st.session_state["report"]
    brief = report.executive_brief

    st.markdown("---")
    st.subheader("📊 Synthesis Performance Telemetry")

    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        st.metric("Source Words", f"{report.total_words:,}")
    with m_col2:
        st.metric("Map Chunks", f"{report.total_sections}")
    with m_col3:
        st.metric("Map Latency", f"{report.map_phase_latency_ms:.0f} ms")
    with m_col4:
        st.metric("Reduce Latency", f"{report.reduce_phase_latency_ms:.0f} ms")
    with m_col5:
        st.metric("Compression Ratio", f"{report.compression_ratio_percent:.1f}%")

    st.markdown("---")

    # Tabs for structured inspection
    tab_reduce, tab_map, tab_export = st.tabs([
        "📋 Executive Brief (Reduce Output)",
        "🗺️ Map Phase Section Inspector",
        "💾 Export & Raw JSON",
    ])

    # TAB 1: EXECUTIVE BRIEF
    with tab_reduce:
        st.markdown(
            f"""
            <div class="bluf-box">
                <h3>📌 Bottom Line Up Front (BLUF)</h3>
                <p>{brief.bluf_summary}</p>
                <div style="margin-top: 12px; font-size: 0.9rem;">
                    <strong>Executive Verdict:</strong> <code>{brief.health_verdict}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("🎯 Strategic Takeaways")
        for takeaway in brief.synthesized_takeaways:
            st.markdown(f"- {takeaway}")

        # Metrics & Risk columns
        st.markdown("---")
        sec_col1, sec_col2 = st.columns(2)

        with sec_col1:
            st.subheader("📊 Key Quantitative Metrics")
            if brief.key_metrics:
                table_md = "| Metric | Description | Impact |\n| :--- | :--- | :---: |\n"
                for m in brief.key_metrics:
                    impact_badge = "🟢" if m.impact.lower() == "positive" else ("🔴" if m.impact.lower() == "negative" else "⚪")
                    table_md += f"| **{m.metric}** | {m.description} | {impact_badge} {m.impact} |\n"
                st.markdown(table_md)
            else:
                st.info("No quantitative metrics identified.")

        with sec_col2:
            st.subheader("⚠️ Synthesized Risk Register")
            if brief.risk_register:
                risk_md = "| Identified Risk | Severity | Targeted Mitigation |\n| :--- | :---: | :--- |\n"
                for r in brief.risk_register:
                    sev_icon = "🔴" if r.severity.lower() == "high" else ("🟠" if r.severity.lower() == "medium" else "🟡")
                    risk_md += f"| **{r.risk}** | {sev_icon} {r.severity} | {r.mitigation} |\n"
                st.markdown(risk_md)
            else:
                st.info("No risks identified.")

        # Action Matrix
        st.markdown("---")
        st.subheader("⚡ Priority Action Matrix")
        if brief.action_matrix:
            action_md = "| Priority | Action Item | DRI / Owner |\n| :---: | :--- | :--- |\n"
            for a in brief.action_matrix:
                p_class = "badge-p0" if a.priority.upper() == "P0" else ("badge-p1" if a.priority.upper() == "P1" else "badge-p2")
                action_md += f"| <span class='{p_class}'>{a.priority}</span> | {a.action} | **{a.owner}** |\n"
            st.markdown(action_md, unsafe_allow_html=True)
        else:
            st.info("No action items identified.")

    # TAB 2: MAP PHASE INSPECTOR
    with tab_map:
        st.markdown(
            "Inspect the intermediate extractions generated during the **Map Phase** for each semantic section. "
            "These structured cards feed directly into the synthesis prompt of the **Reduce Phase**."
        )

        for s in report.mapped_sections:
            with st.expander(f"📍 Section {s.section_index + 1}: {s.title}", expanded=(s.section_index == 0)):
                st.markdown(f"**Section Summary:** {s.raw_summary}")
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    st.markdown("**Key Takeaways:**")
                    for t in s.key_takeaways:
                        st.markdown(f"- {t}")
                    st.markdown("**Quantitative Metrics:**")
                    for m in s.quantitative_metrics:
                        st.markdown(f"- `{m}`")
                with sub_col2:
                    st.markdown("**Identified Risks:**")
                    for r in s.identified_risks:
                        st.markdown(f"- ⚠️ {r}")
                    st.markdown("**Action Items:**")
                    for a in s.action_items:
                        st.markdown(f"- ⚡ {a}")

    # TAB 3: EXPORT & RAW JSON
    with tab_export:
        st.subheader("💾 Export Artifacts")
        d_col1, d_col2 = st.columns(2)

        with d_col1:
            st.download_button(
                label="📥 Download Executive Brief (Markdown)",
                data=brief.full_synthesis_markdown,
                file_name=f"{report.document_title.lower().replace(' ', '_')}_executive_brief.md",
                mime="text/markdown",
                use_container_width=True,
            )

        report_json_str = report.model_dump_json(indent=2) if hasattr(report, "model_dump_json") else report.json(indent=2)
        with d_col2:
            st.download_button(
                label="📥 Download Full Map-Reduce Audit (JSON)",
                data=report_json_str,
                file_name=f"{report.document_title.lower().replace(' ', '_')}_map_reduce_audit.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("---")
        st.subheader("🔍 Full Pipeline JSON Schema")
        st.json(json.loads(report_json_str))
