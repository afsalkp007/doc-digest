"""Unit tests for LLM execution providers and mock fallbacks."""

import json
import pytest
from doc_digest.providers import MockProvider, GeminiProvider, get_llm_provider


def test_mock_provider_map_phase():
    provider = MockProvider()
    prompt = "MAP PHASE: intermediate section extraction for outage report"
    res = provider.generate(prompt, json_mode=True)
    data = json.loads(res)

    assert "key_takeaways" in data
    assert "quantitative_metrics" in data
    assert "identified_risks" in data
    assert "action_items" in data
    assert len(data["key_takeaways"]) > 0


def test_mock_provider_reduce_phase():
    provider = MockProvider()
    prompt = "REDUCE PHASE: synthesize executive briefing for outage incident"
    res = provider.generate(prompt, json_mode=True)
    data = json.loads(res)

    assert "bluf_summary" in data
    assert "health_verdict" in data
    assert "key_metrics" in data
    assert "risk_register" in data
    assert "action_matrix" in data
    assert len(data["risk_register"]) > 0


def test_gemini_provider_missing_key_raises():
    with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
        GeminiProvider(api_key="")


def test_get_llm_provider_default():
    provider = get_llm_provider()
    # In test environment without valid real key, it falls back to MockProvider
    assert isinstance(provider, MockProvider)
