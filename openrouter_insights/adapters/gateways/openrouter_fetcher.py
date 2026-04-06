import logging
from typing import List, Optional
from openrouter_insights.domain.interfaces import IFetcherGateway
from openrouter_insights.adapters.gateways.http_fetcher import BaseHTTPFetcher
from openrouter_insights.infrastructure.config import get_settings

logger = logging.getLogger(__name__)

class OpenRouterFetcher(BaseHTTPFetcher, IFetcherGateway):
    """Fetcher for the OpenRouter Models API."""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.project_name = "OpenRouter Insights"

    async def fetch_catalog(self) -> List[dict]:
        """Fetch models catalog from OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://openrouter_insights.ai", # Required by OpenRouter for ranking
            "X-Title": self.project_name
        }
        
        logger.info(f"Fetching OpenRouter catalog from {self.settings.OPENROUTER_MODELS_URL}")
        data = await self.get(self.settings.OPENROUTER_MODELS_URL, headers=headers)
        
        if data and "data" in data:
            return data["data"]
        
        logger.warning("Empty or invalid response from OpenRouter catalog.")
        return []

    async def fetch_benchmarks(self) -> List[dict]:
        """OpenRouter doesn't provide ArtificialAnalysis-style benchmarks directly."""
        return []
