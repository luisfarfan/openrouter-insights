import pytest
from unittest.mock import AsyncMock, patch
from openrouter_insights.adapters.gateways.openrouter_fetcher import OpenRouterFetcher
from openrouter_insights.adapters.gateways.artificial_analysis_fetcher import ArtificialAnalysisFetcher

@pytest.mark.asyncio
async def test_openrouter_fetcher_success():
    """Verify that OpenRouter fetcher parses the 'data' field."""
    fetcher = OpenRouterFetcher()
    mock_response = {"data": [{"id": "meta-llama/llama-3-70b", "name": "Llama 3 70B"}]}
    
    with patch("openrouter_insights.adapters.gateways.http_fetcher.BaseHTTPFetcher.get", new_callable=AsyncMock) as mocked_get:
        mocked_get.return_value = mock_response
        result = await fetcher.fetch_catalog()
        
        assert len(result) == 1
        assert result[0]["id"] == "meta-llama/llama-3-70b"

@pytest.mark.asyncio
async def test_artificial_analysis_fetcher_success():
    """Verify that ArtificialAnalysis fetcher handles JSON arrays."""
    with patch("openrouter_insights.adapters.gateways.artificial_analysis_fetcher.get_settings") as mocked_settings:
        mocked_settings.return_value.ARTIFICIAL_ANALYSIS_API_KEY = "test-key"
        fetcher = ArtificialAnalysisFetcher()
        # MUST include id or slug or name
        mock_response = [{"id": "llama-3-70b-instruct", "intelligence_score": 90.0}]
        
        with patch("openrouter_insights.adapters.gateways.http_fetcher.BaseHTTPFetcher.get", new_callable=AsyncMock) as mocked_get:
            mocked_get.return_value = mock_response
            result = await fetcher.fetch_benchmarks()
            
            assert len(result) == 1
            assert result[0]["id"] == "llama-3-70b-instruct"

@pytest.mark.asyncio
async def test_artificial_analysis_fetcher_handles_error():
    """Verify that fetcher returns an empty list on error (Partial Sync behavior)."""
    with patch("openrouter_insights.adapters.gateways.artificial_analysis_fetcher.get_settings") as mocked_settings:
        mocked_settings.return_value.ARTIFICIAL_ANALYSIS_API_KEY = "test-key"
        fetcher = ArtificialAnalysisFetcher()
        
        with patch("openrouter_insights.adapters.gateways.http_fetcher.BaseHTTPFetcher.get", new_callable=AsyncMock) as mocked_get, \
             patch("os.path.exists", return_value=False):
            mocked_get.return_value = None
            result = await fetcher.fetch_benchmarks()
            
            assert result == []
