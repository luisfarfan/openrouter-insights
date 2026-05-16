import asyncio
import pytest
from aioresponses import aioresponses
from ai_provider_tracker.adapters.gateways.http_fetcher import BaseHTTPFetcher

@pytest.mark.asyncio
async def test_base_http_fetcher_success():
    fetcher = BaseHTTPFetcher()
    url = "https://api.example.com/data"
    
    with aioresponses() as m:
        m.get(url, payload={"status": "ok"})
        data = await fetcher.get(url)
        assert data == {"status": "ok"}

@pytest.mark.asyncio
async def test_base_http_fetcher_error_status():
    fetcher = BaseHTTPFetcher()
    url = "https://api.example.com/error"
    
    with aioresponses() as m:
        m.get(url, status=404, body="Not Found")
        data = await fetcher.get(url)
        assert data is None

@pytest.mark.asyncio
async def test_base_http_fetcher_exception():
    fetcher = BaseHTTPFetcher()
    url = "https://api.example.com/exception"
    
    with aioresponses() as m:
        m.get(url, exception=Exception("Connection Reset"))
        data = await fetcher.get(url)
        assert data is None
