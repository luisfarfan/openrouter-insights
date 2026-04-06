import pytest
import os
import json
import tempfile
import shutil
from openrouter_insights import LLMIndexSync, LLMIndex

@pytest.fixture
def temp_json():
    dirpath = tempfile.mkdtemp()
    json_path = os.path.join(dirpath, "openrouter_insights.json")
    
    # Mock some data
    data = [
        {"id": "o/smart", "name": "S", "provider": "O", "context_length": 1, "pricing": {"input": 10, "output": 10}, "modalities": ["text"], "benchmarks": {"intelligence_score": 100.0, "speed_score": 10}},
        {"id": "o/cheap", "name": "C", "provider": "O", "context_length": 1, "pricing": {"input": 0, "output": 0}, "modalities": ["text"], "benchmarks": {"intelligence_score": 10.0, "speed_score": 100}},
        {"id": "o/fast", "name": "F", "provider": "O", "context_length": 1, "pricing": {"input": 5, "output": 5}, "modalities": ["text"], "benchmarks": {"intelligence_score": 50.0, "speed_score": 1000}}
    ]
    with open(json_path, "w") as f:
        json.dump(data, f)
        
    yield json_path
    shutil.rmtree(dirpath)

def test_facade_sync_smart_methods(temp_json):
    client = LLMIndexSync(mode="json", path=temp_json)
    
    # Smartest
    smartest = client.get_smartest(limit=1)
    assert smartest[0].id == "o/smart"
    
    # Cheapest
    cheapest = client.get_cheapest(limit=1)
    assert cheapest[0].id == "o/cheap"
    
    # Fastest
    fastest = client.get_fastest(limit=1)
    assert fastest[0].id == "o/fast"

@pytest.mark.asyncio
async def test_facade_async_search(temp_json):
    client = LLMIndex(mode="json", path=temp_json)
    results = await client.search("smart")
    assert len(results) >= 1
    assert results[0].id == "o/smart"
