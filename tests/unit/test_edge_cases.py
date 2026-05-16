import os
import json
import pytest
import tempfile
import shutil
from unittest.mock import patch
from ai_provider_tracker.adapters.persistence.sqlite_repository import SQLiteModelRepository
from ai_provider_tracker.adapters.persistence.json_exporter import JSONExporter
from ai_provider_tracker.adapters.persistence.json_repository import JSONModelRepository
from ai_provider_tracker.domain.entities import LLMModel, Pricing, Benchmarks

@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)

def test_sqlite_defaults(temp_dir):
    # Patch the get_settings in the repository module itself
    with patch("ai_provider_tracker.adapters.persistence.sqlite_repository.get_settings") as mock_get:
        mock_get.return_value.DATABASE_URL = os.path.join(temp_dir, "default.db")
        repo = SQLiteModelRepository()
        assert "default.db" in str(repo.engine.url)

def test_sqlite_sort_speed(temp_dir):
    repo = SQLiteModelRepository(database_url="sqlite://")
    m1 = LLMModel(id="m1", name="M1", provider="P1", pricing=Pricing(), benchmarks=Benchmarks(speed_score=100))
    m2 = LLMModel(id="m2", name="M2", provider="P1", pricing=Pricing(), benchmarks=Benchmarks(speed_score=200))
    repo.save_batch([m1, m2])
    
    results = repo.get_all(sort_by="speed", sort_order="desc")
    assert results[0].id == "m2"

def test_sqlite_search_empty():
    repo = SQLiteModelRepository(database_url="sqlite://")
    results = repo.search("nothing")
    assert results == []

def test_json_exporter_corrupted(temp_dir):
    path = os.path.join(temp_dir, "corrupted.json")
    with open(path, "w") as f:
        f.write("invalid json {")
    
    exporter = JSONExporter(output_path=path)
    # Should not crash, just overwrite/warn
    exporter.export([])
    assert os.path.exists(path)

def test_json_exporter_permission_error():
    exporter = JSONExporter(output_path="/read_only_path.json")
    with pytest.raises(Exception):
        exporter.export([])

def test_json_repository_missing():
    # If path is None or empty
    repo = JSONModelRepository(file_path="")
    assert repo.get_all() == []
    
    repo2 = JSONModelRepository(file_path="nonexistent.json")
    assert repo2.get_all() == []

def test_json_repository_invalid_format(temp_dir):
    path = os.path.join(temp_dir, "invalid.json")
    with open(path, "w") as f:
        json.dump({"not_models": []}, f)
    
    repo = JSONModelRepository(file_path=path)
    # Testing both versions (legacy list and latest metadata struct)
    assert repo.get_all() == []
    
    # Invalid JSON string
    with open(path, "w") as f:
        f.write("!!!")
    assert repo.get_all() == []

def test_json_repository_legacy_list(temp_dir):
    path = os.path.join(temp_dir, "legacy.json")
    legacy_data = [{"id": "m1", "name": "M1", "provider": "P1", "pricing": {"input": 0, "output": 0}}]
    with open(path, "w") as f:
        json.dump(legacy_data, f)
    
    repo = JSONModelRepository(file_path=path)
    results = repo.get_all()
    assert len(results) == 1
    assert results[0].id == "m1"
