from openrouter_insights.domain.entities import LLMModel, Pricing, Benchmarks
from openrouter_insights.adapters.persistence.sqlite_repository import SQLiteModelRepository
from openrouter_insights import LLMIndexSync

def test_llm_model_top_level_props():
    model = LLMModel(
        id="test/model",
        name="Test",
        provider="TestProv",
        pricing=Pricing(input=0.1, output=0.2),
        benchmarks=Benchmarks(intelligence_score=95.0)
    )
    
    assert model.intelligence_score == 95.0
    assert not model.is_virtual
    assert "frontier" in model.best_for
    assert "reasoning" in model.best_for

def test_llm_model_virtual_detection():
    # Case 1: Negative Price
    m1 = LLMModel(id="m1", name="M1", provider="P1", pricing=Pricing(input=-1, output=0))
    assert m1.is_virtual
    
    # Case 2: /auto suffix
    m2 = LLMModel(id="openrouter/auto", name="Auto", provider="OpenRouter", pricing=Pricing(input=0.1, output=0.1))
    assert m2.is_virtual

def test_sqlite_virtual_filtering(tmp_path):
    db_path = f"sqlite:///{tmp_path}/test.db"
    repo = SQLiteModelRepository(db_path)
    
    m_real = LLMModel(id="real", name="Real", provider="P1", pricing=Pricing(input=0.1, output=0.1), benchmarks=Benchmarks(intelligence_score=50))
    m_virt = LLMModel(id="openrouter/auto", name="Auto", provider="OR", pricing=Pricing(input=0, output=0))
    
    repo.save_batch([m_real, m_virt])
    
    # Default filter_virtual=True
    all_models = repo.get_all()
    assert len(all_models) == 1
    assert all_models[0].id == "real"
    
    # Explicit False
    all_models_all = repo.get_all(filter_virtual=False)
    assert len(all_models_all) == 2

def test_get_best_alternative(tmp_path):
    db_path = f"sqlite:///{tmp_path}/test_alt.db"
    repo = SQLiteModelRepository(db_path)
    
    # Tier: Frontier (Intelligence > 85)
    gpt4 = LLMModel(id="openai/gpt-4", name="GPT-4", provider="OpenAI", pricing=Pricing(input=30, output=60), benchmarks=Benchmarks(intelligence_score=90))
    claude3 = LLMModel(id="anthropic/claude-3-opus", name="Claude 3", provider="Anthropic", pricing=Pricing(input=15, output=75), benchmarks=Benchmarks(intelligence_score=89))
    cheap_lite = LLMModel(id="meta/llama-3-8b", name="Llama 3 8B", provider="Meta", pricing=Pricing(input=0.1, output=0.1), benchmarks=Benchmarks(intelligence_score=60))
    
    repo.save_batch([gpt4, claude3, cheap_lite])
    
    # Find alternative for GPT-4
    # Claude 3 is in same tier (Frontier)
    alt = repo.get_best_alternative("openai/gpt-4")
    assert alt is not None
    assert alt.id == "anthropic/claude-3-opus"
    
    # Should NOT return Llama 3 (different tier) even if cheaper
    # Should NOT return itself

def test_facade_tier_filtering(tmp_path):
    db_path = str(tmp_path / "facade.db")
    client = LLMIndexSync(mode="sqlite", path=db_path)
    
    m1 = LLMModel(id="m1", name="M1", provider="P1", pricing=Pricing(input=1, output=1), benchmarks=Benchmarks(intelligence_score=95))
    m2 = LLMModel(id="m2", name="M2", provider="P2", pricing=Pricing(input=1, output=1), benchmarks=Benchmarks(intelligence_score=75))
    
    # Sync use case usually saves models. Since we are testing facade, we'll use repository directly to seed
    client.repository.save_batch([m1, m2])
    
    frontier = client.get_by_tier("frontier")
    assert len(frontier) == 1
    assert frontier[0].id == "m1"
    
    pro = client.get_by_tier("pro")
    assert len(pro) == 1
    assert pro[0].id == "m2"
