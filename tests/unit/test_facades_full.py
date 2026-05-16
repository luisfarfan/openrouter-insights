import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from ai_provider_tracker import LLMIndex, LLMIndexSync
from ai_provider_tracker.domain.interfaces import IModelRepository

@pytest.fixture
def mock_repo():
    repo = MagicMock(spec=IModelRepository)
    repo.get_all.return_value = []
    repo.search.return_value = []
    repo.get_by_id.return_value = None
    return repo

def test_sync_facade_all_methods(mock_repo):
    client = LLMIndexSync(mode="json")
    client.repository = mock_repo
    
    # Basic methods
    client.get_models()
    client.get_model("test")
    client.get_smartest()
    client.get_cheapest()
    client.get_fastest()
    client.get_best_for_coding()
    client.get_best_for_reasoning()
    client.get_best_for_rag()
    client.get_best_for_multimodal()
    client.get_free_models()
    client.get_top_frontier()
    client.get_by_tier("pro")
    client.get_by_provider("OpenAI")
    client.search("test")
    
    assert mock_repo.get_all.called
    assert mock_repo.search.called
    assert mock_repo.get_by_id.called

@pytest.mark.asyncio
async def test_async_facade_all_methods(mock_repo):
    client = LLMIndex(mode="json")
    client.repository = mock_repo
    
    await client.get_models()
    await client.get_model("test")
    await client.get_smartest()
    await client.get_cheapest()
    await client.get_fastest()
    await client.get_best_for_coding()
    await client.get_best_for_reasoning()
    await client.get_best_for_rag()
    await client.get_best_for_multimodal()
    await client.get_free_models()
    await client.get_top_frontier()
    await client.get_by_tier("pro")
    await client.get_by_provider("OpenAI")
    await client.search("test")
    
    assert mock_repo.get_all.called
    assert mock_repo.search.called
    assert mock_repo.get_by_id.called

def test_sync_facade_errors():
    client = LLMIndexSync(mode="json")
    with pytest.raises(ValueError, match="Sync is not supported in JSON mode"):
        client.sync()

@pytest.mark.asyncio
async def test_async_facade_sync_error():
    client = LLMIndex(mode="json")
    with pytest.raises(ValueError, match="Sync is not supported in JSON mode"):
        await client.sync()

def test_sync_facade_call(mock_repo):
    client = LLMIndexSync(mode="sqlite", path=":memory:")
    # We patch the use case execution
    with patch("ai_provider_tracker.use_cases.sync_registry.SyncRegistryUseCase.execute", AsyncMock(return_value=[])):
        client.sync()

@pytest.mark.asyncio
async def test_async_facade_sync_call(mock_repo):
    client = LLMIndex(mode="sqlite", path=":memory:")
    with patch("ai_provider_tracker.use_cases.sync_registry.SyncRegistryUseCase.execute", AsyncMock(return_value=[])):
        await client.sync()
