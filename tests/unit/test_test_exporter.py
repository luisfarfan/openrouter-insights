import os
import json
import tempfile
import time
import pytest
from ai_provider_tracker.adapters.persistence.json_exporter import JSONExporter
from ai_provider_tracker.domain.entities import LLMModel, Pricing

@pytest.fixture
def temp_json():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    # Remove it so the first test sees a "new" file
    if os.path.exists(path):
        os.remove(path)
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_exporter_new_file(temp_json):
    exporter = JSONExporter(output_path=temp_json)
    models = [
        LLMModel(
            id="openai/gpt-4o",
            name="GPT-4o",
            provider="OpenAI",
            context_length=128000,
            pricing=Pricing(input=1.0, output=3.0),
            modalities=["text"]
        )
    ]
    
    # Export for the first time
    exporter.export(models)
    assert os.path.exists(temp_json)
    
    with open(temp_json, "r") as f:
        data = json.load(f)
        assert "metadata" in data
        assert len(data["models"]) == 1

def test_exporter_skip_if_no_changes(temp_json):
    exporter = JSONExporter(output_path=temp_json)
    models = [
        LLMModel(id="m1", name="M1", provider="P1", context_length=1, pricing=Pricing(input=1, output=1), modalities=["text"])
    ]
    
    # First export
    exporter.export(models)
    first_mtime = os.path.getmtime(temp_json)
    
    # Wait a bit to ensure mtime would change if written
    time.sleep(0.1)
    
    # Second export (identical models)
    exporter.export(models)
    second_mtime = os.path.getmtime(temp_json)
    
    # The file should not have been overwritten
    assert first_mtime == second_mtime

def test_exporter_update_on_changes(temp_json):
    exporter = JSONExporter(output_path=temp_json)
    models = [
        LLMModel(id="m1", name="M1", provider="P1", context_length=1, pricing=Pricing(input=1, output=1), modalities=["text"])
    ]
    exporter.export(models)
    first_mtime = os.path.getmtime(temp_json)
    
    time.sleep(0.1)
    
    # Change a price
    models[0].pricing.input = 2.0
    
    exporter.export(models)
    second_mtime = os.path.getmtime(temp_json)
    
    assert second_mtime > first_mtime
