import os
import pytest
import tempfile
import shutil
from ai_provider_tracker.adapters.persistence.sqlite_repository import SQLiteModelRepository
from ai_provider_tracker.domain.entities import LLMModel, Pricing, Benchmarks

@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)

@pytest.fixture
def sqlite_repo():
    # Use memory for high speed and clean state
    db_url = "sqlite://"
    repo = SQLiteModelRepository(database_url=db_url)
    
    # Pre-seed with diverse data
    models = [
        # intelligence 90 -> "reasoning" tag
        LLMModel(id="o1", name="Model 1", provider="OpenAI", context_length=1, pricing=Pricing(input=10, output=20), benchmarks=Benchmarks(intelligence_score=90, elo_score=1200, speed_score=50), modalities=["text"]),
        LLMModel(id="o2", name="Model 2", provider="OpenAI", context_length=1, pricing=Pricing(input=1, output=1), benchmarks=Benchmarks(intelligence_score=50, elo_score=1000, speed_score=100), modalities=["text"]),
        LLMModel(id="a1", name="Model 3", provider="Anthropic", context_length=1, pricing=Pricing(input=0, output=0), benchmarks=Benchmarks(intelligence_score=80, elo_score=1100, speed_score=20), modalities=["text"]),
    ]
    repo.save_batch(models)
    return repo

def test_sqlite_repo_init_defaults(temp_dir):
    # Test initialization with relative path and defaults
    db_path = os.path.join(temp_dir, "test.db")
    repo = SQLiteModelRepository(database_url=db_path)
    assert repo.engine is not None

def test_sqlite_filter_provider(sqlite_repo):
    results = sqlite_repo.get_all(provider="OpenAI")
    assert len(results) == 2
    assert all(m.provider == "OpenAI" for m in results)

def test_sqlite_filter_free(sqlite_repo):
    results = sqlite_repo.get_all(is_free=True)
    assert len(results) == 1
    assert results[0].id == "a1"

def test_sqlite_filter_intelligence(sqlite_repo):
    results = sqlite_repo.get_all(min_intelligence=85)
    assert len(results) == 1
    assert results[0].id == "o1"

def test_sqlite_sorting_price_asc(sqlite_repo):
    results = sqlite_repo.get_all(sort_by="price", sort_order="asc")
    assert results[0].id == "a1" # Free
    assert results[-1].id == "o1" # Expensive

def test_sqlite_sorting_intelligence_desc(sqlite_repo):
    results = sqlite_repo.get_all(sort_by="intelligence", sort_order="desc")
    assert results[0].benchmarks.intelligence_score == 90

def test_sqlite_sorting_elo_desc(sqlite_repo):
    results = sqlite_repo.get_all(sort_by="elo", sort_order="desc")
    assert results[0].benchmarks.elo_score == 1200

def test_sqlite_pagination(sqlite_repo):
    # Page size 1, get second page
    results = sqlite_repo.get_all(page=2, page_size=1)
    assert len(results) == 1
    
    count = sqlite_repo.get_count()
    assert count == 3

def test_sqlite_empty_results(sqlite_repo):
    results = sqlite_repo.get_all(provider="NonExistent")
    assert len(results) == 0
    
    count = sqlite_repo.get_count(provider="NonExistent")
    assert count == 0

def test_sqlite_get_by_id(sqlite_repo):
    model = sqlite_repo.get_by_id("o1")
    assert model is not None
    assert model.name == "Model 1"
    
    none_model = sqlite_repo.get_by_id("invalid")
    assert none_model is None

def test_sqlite_filter_best_for(sqlite_repo):
    # Model 1 (intel 90) -> tag "reasoning"
    results = sqlite_repo.get_all(best_for="reasoning")
    assert len(results) > 0
    assert any(m.id == "o1" for m in results)

def test_sqlite_search(sqlite_repo):
    results = sqlite_repo.search("OpenAI")
    assert len(results) >= 2
    assert results[0].provider == "OpenAI"

def test_sqlite_no_benchmarks(sqlite_repo):
    # Add a model with NO benchmarks
    m = LLMModel(id="nb1", name="No Bench", provider="P1", context_length=1, pricing=Pricing(input=0, output=0), modalities=["text"], benchmarks=None)
    sqlite_repo.save_batch([m])
    
    # Sorting by intelligence should handle this gracefully (nulls)
    results = sqlite_repo.get_all(sort_by="intelligence", sort_order="desc")
    assert len(results) == 4
    # nb1 should be at the end as its score is None
    assert results[-1].id == "nb1"
