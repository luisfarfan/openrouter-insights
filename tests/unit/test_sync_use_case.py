import pytest
from aioresponses import aioresponses
from ai_provider_tracker.use_cases.sync_registry import SyncRegistryUseCase
from ai_provider_tracker.adapters.gateways.openrouter_fetcher import OpenRouterFetcher
from ai_provider_tracker.adapters.gateways.artificial_analysis_fetcher import ArtificialAnalysisFetcher
from ai_provider_tracker.domain.services.matching_engine import MatchingEngine
from unittest.mock import MagicMock

@pytest.fixture
def sync_use_case(monkeypatch):
    # Ensure AA API key is set for tests
    monkeypatch.setenv("ARTIFICIAL_ANALYSIS_API_KEY", "test-key")
    
    # Mocking repositories and exporters
    repository = MagicMock()
    exporter = MagicMock()
    
    # We use real fetchers but mock their HTTP responses via aioresponses
    return SyncRegistryUseCase(
        repository=repository,
        gateways=[OpenRouterFetcher(), ArtificialAnalysisFetcher()],
        matching_engine=MatchingEngine(),
        exporter=exporter
    )

@pytest.mark.asyncio
async def test_sync_registry_success(sync_use_case):
    with aioresponses() as m:
        # Mock OpenRouter Models
        m.get(
            "https://openrouter.ai/api/v1/models",
            payload={"data": [{"id": "openai/gpt-4o", "name": "GPT-4o", "context_length": 128000, "pricing": {"prompt": "0.000001", "completion": "0.000003"}}]}
        )
        
        # Mock all AA endpoints to avoid connection errors
        base_aa = "https://artificialanalysis.ai/api/v2/data"
        m.get(f"{base_aa}/llms/models", payload=[{"id": "gpt-4o", "name": "GPT-4o", "quality_score": 90.0}])
        m.get(f"{base_aa}/media/text-to-image", payload=[])
        m.get(f"{base_aa}/media/text-to-video", payload=[])
        m.get(f"{base_aa}/media/text-to-speech", payload=[])
        m.get(f"{base_aa}/media/image-editing", payload=[])

        # Execute Sync
        result = await sync_use_case.execute()
        
        assert len(result) > 0
        assert result[0].id == "openai/gpt-4o"
        assert sync_use_case.repository.save_batch.called
        assert sync_use_case.exporter.export.called

@pytest.mark.asyncio
async def test_sync_registry_provider_splitting(sync_use_case):
    with aioresponses() as m:
        # Mocking a model WITHOUT a slash in the ID, but a colon in the name
        m.get(
            "https://openrouter.ai/api/v1/models",
            payload={"data": [{"id": "llama-3-8b", "name": "Meta: Llama 3", "context_length": 8000, "pricing": {"prompt": "0", "completion": "0"}}]}
        )
        # Mock AA (it might be skipped if no match, but let's be safe)
        base_aa = "https://artificialanalysis.ai/api/v2/data"
        m.get(f"{base_aa}/llms/models", payload=[])
        m.get(f"{base_aa}/media/text-to-image", payload=[])
        m.get(f"{base_aa}/media/text-to-video", payload=[])
        m.get(f"{base_aa}/media/text-to-speech", payload=[])
        m.get(f"{base_aa}/media/image-editing", payload=[])

        result = await sync_use_case.execute()
        assert result[0].provider == "Meta"

@pytest.mark.asyncio
async def test_sync_registry_invalid_benchmark_float(sync_use_case):
    with aioresponses() as m:
        m.get(
            "https://openrouter.ai/api/v1/models",
            payload={"data": [{"id": "m1", "name": "M1", "context_length": 1000, "pricing": {"prompt": "0.1", "completion": "0.1"}}]}
        )
        # Mock AA with N/A string
        base_aa = "https://artificialanalysis.ai/api/v2/data"
        m.get(f"{base_aa}/llms/models", payload=[{"slug": "m1", "name": "M1", "quality_score": "N/A"}])
        m.get(f"{base_aa}/media/text-to-image", payload=[])
        m.get(f"{base_aa}/media/text-to-video", payload=[])
        m.get(f"{base_aa}/media/text-to-speech", payload=[])
        m.get(f"{base_aa}/media/image-editing", payload=[])

        result = await sync_use_case.execute()
        assert result[0].id == "m1"
        assert result[0].benchmarks is None # Fully failed to parse invalid scores

@pytest.mark.asyncio
async def test_sync_registry_fetch_failure(sync_use_case):
    with aioresponses() as m:
        # Simulate OpenRouter failure
        m.get("https://openrouter.ai/api/v1/models", status=500)
        # AA mock
        base_aa = "https://artificialanalysis.ai/api/v2/data"
        m.get(f"{base_aa}/llms/models", payload=[])
        m.get(f"{base_aa}/media/text-to-image", payload=[])
        m.get(f"{base_aa}/media/text-to-video", payload=[])
        m.get(f"{base_aa}/media/text-to-speech", payload=[])
        m.get(f"{base_aa}/media/image-editing", payload=[])
        
        result = await sync_use_case.execute()
        assert len(result) == 0
