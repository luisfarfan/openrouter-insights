import pytest
from openrouter_insights.domain.services.matching_engine import MatchingEngine

@pytest.fixture
def engine():
    return MatchingEngine(threshold=95.0)

def test_normalize_strips_provider(engine):
    assert engine.normalize("openai/gpt-4o") == "gpt-4o"
    assert engine.normalize("anthropic/claude-3.5-sonnet") == "claude-3-5-sonnet"

def test_normalize_replaces_special_chars(engine):
    assert engine.normalize("Gemini 1.5 Pro") == "gemini-1-5-pro"
    assert engine.normalize("GPT_4_turbo") == "gpt-4-turbo"

def test_exact_normalized_match_no_provider(engine):
    # Match 'openai/gpt-4o' with 'gpt-4o'
    candidates = ["gpt-4o", "other-model"]
    match, score = engine.find_match("openai/gpt-4o", candidates)
    assert match == "gpt-4o"
    assert score == 100.0

def test_exact_normalized_match_complex(engine):
    candidates = ["claude-3-5-sonnet"]
    match, score = engine.find_match("anthropic/claude.3.5.sonnet", candidates)
    assert match == "claude-3-5-sonnet"
    assert score == 100.0

def test_fuzzy_match_success(engine):
    candidates = ["llama-3-70b-instruct"]
    match, score = engine.find_match("meta/llama3-70b-instruct", candidates)
    assert match == "llama-3-70b-instruct"
    assert score >= 95.0

def test_fuzzy_match_rejection(engine):
    candidates = ["gpt-4", "claude-3"]
    match, score = engine.find_match("mistral-7b", candidates)
    assert match is None
    assert score < 95.0
