import pytest
from openrouter_insights.domain.entities import LLMModel, Pricing, Benchmarks

def test_llm_model_tier_frontier():
    # Test high-end frontier model
    model = LLMModel(
        id="openai/gpt-4o",
        name="GPT-4o",
        provider="OpenAI",
        context_length=128000,
        pricing=Pricing(input=1, output=3),
        modalities=["text", "vision"],
        benchmarks=Benchmarks(intelligence_score=91.0, speed_score=100.0)
    )
    assert model.performance_tier == "frontier"

def test_llm_model_tier_lite():
    # Test low-end lite model
    model = LLMModel(
        id="anthropic/claude-3-haiku",
        name="Claude Haiku",
        provider="Anthropic",
        context_length=200000,
        pricing=Pricing(input=0.1, output=0.3),
        modalities=["text"],
        benchmarks=Benchmarks(intelligence_score=40.0, speed_score=200.0)
    )
    assert model.performance_tier == "lite"


def test_llm_model_is_free():
    model = LLMModel(
        id="free-model",
        name="Free",
        provider="Other",
        context_length=4096,
        pricing=Pricing(input=0, output=0),
        modalities=["text"]
    )
    assert model.pricing.input == 0
    assert model.pricing.output == 0
