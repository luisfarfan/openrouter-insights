import shutil
import tempfile
import json
import os
import pytest
from openrouter_insights.adapters.persistence.json_repository import JSONModelRepository
from openrouter_insights.adapters.persistence.sqlite_repository import SQLiteModelRepository
from openrouter_insights.domain.entities import LLMModel, Pricing

@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)

def test_json_repo_save_and_get(temp_dir):
    json_path = os.path.join(temp_dir, "openrouter_insights.json")
    
    # Pre-seed JSON
    model_data = [
        {
            "id": "openai/gpt-4o",
            "name": "GPT-4o",
            "provider": "OpenAI",
            "context_length": 128000,
            "pricing": {"input": 1, "output": 3},
            "modalities": ["text"],
            "benchmarks": {"intelligence_score": 90.0}
        }
    ]
    with open(json_path, "w") as f:
        json.dump(model_data, f)

    repo = JSONModelRepository(file_path=json_path)
    
    # Get by ID
    model = repo.get_by_id("openai/gpt-4o")
    assert model is not None
    assert model.name == "GPT-4o"

    # Fuzzy Search
    results = repo.search("gpt-4o")
    assert len(results) == 1
    assert results[0].id == "openai/gpt-4o"

def test_sqlite_repo_save_and_get(temp_dir):
    db_path = f"sqlite:///{os.path.join(temp_dir, 'test.db')}"
    repo = SQLiteModelRepository(database_url=db_path)
    
    model = LLMModel(
        id="meta/llama-3-70b",
        name="Llama 3 70B",
        provider="Meta",
        context_length=8192,
        pricing=Pricing(input=0.59, output=0.79),
        modalities=["text"],
        benchmarks=None
    )
    
    repo.save(model)
    
    fetched = repo.get_by_id("meta/llama-3-70b")
    assert fetched is not None
    assert fetched.name == "Llama 3 70B"
    assert fetched.provider == "Meta"
