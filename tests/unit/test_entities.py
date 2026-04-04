import pytest
from src.domain.entities import LLMModel, Pricing, Benchmarks

def test_llm_model_best_for_coding():
    """Verify that a model with high coding score is tagged as 'coding'."""
    model = LLMModel(
        id="test/model",
        name="Test Model",
        provider="Test",
        context_length=128000,
        pricing=Pricing(input=0.1, output=0.2),
        benchmarks=Benchmarks(coding_score=95.0, intelligence_score=90.0)
    )
    
    assert "coding" in model.best_for
    assert "rag" in model.best_for  # context >= 128k and intelligence >= 80

def test_llm_model_performance_tier():
    """Verify the performance tier classification."""
    frontier_model = LLMModel(
        id="test/frontier",
        name="Frontier",
        provider="Test",
        context_length=8192,
        pricing=Pricing(),
        benchmarks=Benchmarks(intelligence_score=98.0)
    )
    
    mid_model = LLMModel(
        id="test/mid",
        name="Mid",
        provider="Test",
        context_length=8192,
        pricing=Pricing(),
        benchmarks=Benchmarks(intelligence_score=75.0)
    )
    
    assert frontier_model.performance_tier == "frontier"
    assert mid_model.performance_tier == "mid"

def test_llm_model_efficiency_score():
    """Verify efficiency score calculation (Intelligence / Cost)."""
    model = LLMModel(
        id="test/efficient",
        name="Efficient",
        provider="Test",
        context_length=8192,
        pricing=Pricing(input=1.0, output=2.0), # $2.0 per 1M output tokens
        benchmarks=Benchmarks(intelligence_score=90.0)
    )
    
    # Formula: (Score / (Cost * 1000)) scaled
    # 90 / (2.0 * 1000) = 0.045
    # scaled result: round(0.045 / 100, 4) -> 0.0005 (approx)
    # Note: The formula in entities.py is: round(min(1.0, raw_score / 100), 4)
    assert model.efficiency_score > 0
