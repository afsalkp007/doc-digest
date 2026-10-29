"""LLM execution providers with structured JSON support and zero-crash mock fallback."""

import os
import json
import logging
import warnings
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()
logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Abstract interface for LLM completions."""

    @abstractmethod
    def generate(self, prompt: str, json_mode: bool = False) -> str:
        pass


class GeminiProvider(BaseLLM):
    """Google Gemini 2.5 Flash completion provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

    def generate(self, prompt: str, json_mode: bool = False) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        config: Dict[str, Any] = {"temperature": 0.2}
        if json_mode:
            config["responseMimeType"] = "application/json"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": config,
        }

        resp = requests.post(url, json=payload, timeout=45)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API request failed ({resp.status_code}): {resp.text}")

        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        if json_mode:
            # Clean markdown codeblocks if model returned them
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

        return raw_text.strip()


class MockProvider(BaseLLM):
    """High-fidelity mock provider reflecting realistic Map-Reduce extraction and executive synthesis."""

    def generate(self, prompt: str, json_mode: bool = False) -> str:
        p_lower = prompt.lower()

        # 1. MAP PHASE: Section Extraction
        if "map phase" in p_lower or "extract section" in p_lower or "intermediate section extraction" in p_lower:
            if "outage" in p_lower or "failover" in p_lower or "database" in p_lower:
                return json.dumps({
                    "key_takeaways": [
                        "Database failover incident caused 18 minutes of unmitigated production downtime.",
                        "Primary PostgreSQL replica locked due to an unindexed schema migration script.",
                        "Automated circuit breaker failed to divert traffic to read-only backup replica."
                    ],
                    "quantitative_metrics": [
                        "Downtime: 18 minutes",
                        "Transaction loss: 4,200 checkout sessions",
                        "Estimated revenue impact: $64,000"
                    ],
                    "identified_risks": [
                        "Single point of failure on primary database cluster",
                        "Lack of automated query indexing verification in CI/CD"
                    ],
                    "action_items": [
                        "Deploy automated index validation check to migration pipeline",
                        "Reconfigure circuit breaker timeout from 15m to 45s"
                    ],
                    "raw_summary": "Major database deadlock during deployment triggered failover latency, dropping 4.2k active user sessions."
                })
            elif "revenue" in p_lower or "financial" in p_lower or "q3" in p_lower or "growth" in p_lower:
                return json.dumps({
                    "key_takeaways": [
                        "Q3 Annual Recurring Revenue (ARR) accelerated to $52.4M, representing 38% YoY growth.",
                        "Enterprise tier net expansion reached 124%, driven by AI-assisted add-on module adoption.",
                        "Gross margins contracted slightly by 180 bps due to frontier cloud inference infrastructure."
                    ],
                    "quantitative_metrics": [
                        "Ending ARR: $52.4M (+38% YoY)",
                        "Net Dollar Retention (NDR): 124%",
                        "Gross Margin: 74.2% (-180 bps)"
                    ],
                    "identified_risks": [
                        "Model inference compute costs growing faster than seat additions",
                        "Sales cycle length in EMEA extended from 42 to 68 days"
                    ],
                    "action_items": [
                        "Implement GPU semantic caching proxy to compress inference spend",
                        "Introduce tiered enterprise pricing for high-token workflows"
                    ],
                    "raw_summary": "Strong top-line acceleration with record expansion, tempered by infrastructure gross margin compression."
                })
            else:
                # General section
                return json.dumps({
                    "key_takeaways": [
                        "Core operational objectives were achieved within scheduled timeline milestones.",
                        "Team dependencies and cross-functional coordination remain on critical path."
                    ],
                    "quantitative_metrics": [
                        "Completion rate: 92%",
                        "Open action items: 4"
                    ],
                    "identified_risks": [
                        "Resource bottleneck on senior infrastructure engineering"
                    ],
                    "action_items": [
                        "Conduct weekly milestone sync with technical leads"
                    ],
                    "raw_summary": "Progress is pacing in line with expectations with minor resourcing adjustments needed."
                })

        # 2. REDUCE PHASE: Executive Briefing Synthesis
        if "reduce phase" in p_lower or "executive briefing" in p_lower or "synthesize" in p_lower:
            if "outage" in p_lower or "incident" in p_lower or "failover" in p_lower:
                return json.dumps({
                    "bluf_summary": "A 18-minute primary database deadlock halted checkout operations, resulting in 4,200 aborted transactions and $64,000 in lost revenue. Full recovery was achieved via read-replica promotion, with immediate architectural remediations underway.",
                    "health_verdict": "Critical Incident (Resolved)",
                    "synthesized_takeaways": [
                        "Root cause: Unindexed foreign key migration locked active rows under peak checkout load.",
                        "Failover delay: Manual operator verification added 12 minutes to automated failover threshold.",
                        "Data integrity: Zero customer records or ledger states were corrupted."
                    ],
                    "key_metrics": [
                        {"metric": "18 minutes", "description": "Total checkout downtime", "impact": "Negative"},
                        {"metric": "$64,000", "description": "Dropped cart revenue impact", "impact": "Negative"},
                        {"metric": "4,200", "description": "Aborted checkout sessions", "impact": "Negative"},
                        {"metric": "0", "description": "Permanent data loss records", "impact": "Positive"}
                    ],
                    "risk_register": [
                        {"risk": "Database single-point-of-failure", "severity": "High", "mitigation": "Migrate to multi-region active-active Aurora cluster"},
                        {"risk": "Unvetted migration scripts", "severity": "High", "mitigation": "Enforce mandatory CI lint rule blocking unindexed table alters"},
                        {"risk": "Manual failover delays", "severity": "Medium", "mitigation": "Automate health-check promotion trigger under 60 seconds"}
                    ],
                    "action_matrix": [
                        {"action": "Deploy CI migration index linter", "owner": "DBA / DevOps Lead", "priority": "P0"},
                        {"action": "Reconfigure Aurora failover timeout to 45s", "owner": "Infrastructure Team", "priority": "P0"},
                        {"action": "Issue formal customer postmortem & SLA credit notice", "owner": "Customer Success VP", "priority": "P1"}
                    ]
                })
            else:
                return json.dumps({
                    "bluf_summary": "The organization demonstrated strong operational execution across key quarterly priorities, achieving 92% milestone delivery while identifying critical compute cost bottlenecks that require immediate architectural optimization.",
                    "health_verdict": "Healthy / Targeted Attention",
                    "synthesized_takeaways": [
                        "Top-line expansion remains robust with high customer adoption of new features.",
                        "Infrastructure and inference unit costs require proactive caching and governance.",
                        "Cross-functional delivery velocity met primary delivery commitments."
                    ],
                    "key_metrics": [
                        {"metric": "92%", "description": "Milestone delivery rate", "impact": "Positive"},
                        {"metric": "38%", "description": "Year-over-year revenue expansion", "impact": "Positive"},
                        {"metric": "180 bps", "description": "Cloud gross margin compression", "impact": "Negative"}
                    ],
                    "risk_register": [
                        {"risk": "Infrastructure spend acceleration", "severity": "High", "mitigation": "Implement semantic caching and token budget quotas"},
                        {"risk": "Key person resource dependency", "severity": "Medium", "mitigation": "Cross-train platform engineering team on failover runbooks"}
                    ],
                    "action_matrix": [
                        {"action": "Deploy semantic caching proxy gateway", "owner": "Platform Engineering", "priority": "P0"},
                        {"action": "Revise enterprise tier pricing structure", "owner": "Product Lead", "priority": "P1"},
                        {"action": "Finalize Q4 operational capacity plan", "owner": "Operations Director", "priority": "P2"}
                    ]
                })

        return "Synthesized analysis complete."


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLM:
    """Factory function for LLM provider."""
    active = (provider_name or os.getenv("LLM_PROVIDER", "gemini")).lower()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    if active == "gemini" and gemini_key and not gemini_key.startswith("your_"):
        try:
            return GeminiProvider(api_key=gemini_key)
        except Exception as e:
            logger.warning("Failed to initialize GeminiProvider: %s. Using MockProvider.", e)
            return MockProvider()

    return MockProvider()
