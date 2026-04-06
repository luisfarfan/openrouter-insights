import logging
from typing import List, Dict, Any, Optional
from openrouter_insights.domain.interfaces import IFetcherGateway
from openrouter_insights.adapters.gateways.http_fetcher import BaseHTTPFetcher
from openrouter_insights.infrastructure.config import get_settings
from rapidfuzz import process, fuzz

logger = logging.getLogger(__name__)

class ArtificialAnalysisFetcher(BaseHTTPFetcher, IFetcherGateway):
    """
    Gateway Adapter for ArtificialAnalysis API v2.
    Fetches both LLM models and specialized Multimodal Media ratings.
    """

    def __init__(self):
        super().__init__()
        settings = get_settings()
        self.api_key = settings.ARTIFICIAL_ANALYSIS_API_KEY
        self.base_url = "https://artificialanalysis.ai/api/v2/data"
        self.endpoints = {
            "models": f"{self.base_url}/llms/models",
            "image": f"{self.base_url}/media/text-to-image",
            "video": f"{self.base_url}/media/text-to-video",
            "speech": f"{self.base_url}/media/text-to-speech",
            "editing": f"{self.base_url}/media/image-editing"
        }

    async def fetch_catalog(self) -> List[Dict[str, Any]]:
        return []

    async def fetch_benchmarks(self) -> List[Dict[str, Any]]:
        """ Aggregate and INTERNALLY unify specialized benchmarks with local fallback."""
        all_raw: Dict[str, List[Dict[str, Any]]] = {}
        
        # --- Attempt API Fetch ---
        if self.api_key and self.api_key != "not-set":
            headers = {"x-api-key": self.api_key}
            if "aa_" in self.api_key: # Likely AA v2 format
                 headers = {"Authorization": f"Bearer {self.api_key}"}
                 
            for name, url in self.endpoints.items():
                data = await self.get(url, headers=headers)
                if data:
                    all_raw[name] = data
        
        # --- Local Fallback ---
        if not all_raw.get("models"):
            import json, os
            local_path = "data/raw/raw_benchmarks.json"
            if os.path.exists(local_path):
                logger.info(f"Using local benchmark data from {local_path}")
                with open(local_path, "r") as f:
                    all_raw["models"] = json.load(f)
                    for cat in ["image", "video", "speech", "editing"]:
                        all_raw[cat] = []
            else:
                return []

        # 1. Start with the Master LLM list
        unified: Dict[str, Dict[str, Any]] = {}
        names_index: List[str] = []
        
        for item in all_raw["models"]:
            name = item.get("name") or item.get("id") or item.get("slug")
            if name:
                unified[name] = item
                names_index.append(name)

        # 2. Fuzzy Merge Media Data
        for category in ["image", "video", "speech", "editing"]:
            for m_item in all_raw.get(category, []):
                m_name = m_item.get("name") or m_item.get("id") or m_item.get("slug")
                if not m_name: continue
                
                match = process.extractOne(m_name, names_index, scorer=fuzz.WRatio)
                if match and match[1] > 90:
                    target_name = match[0]
                    unified[target_name].update(m_item)
                else:
                    unified[m_name] = m_item
                    names_index.append(m_name)
        
        return list(unified.values())
