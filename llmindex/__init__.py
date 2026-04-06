import asyncio
from typing import List, Optional, Literal

__version__ = "0.2.0"
from llmindex.domain.entities import LLMModel, Pricing, Benchmarks
from llmindex.adapters.persistence.sqlite_repository import SQLiteModelRepository
from llmindex.adapters.persistence.json_repository import JSONModelRepository
from llmindex.use_cases.sync_registry import SyncRegistryUseCase
from llmindex.adapters.gateways.openrouter_fetcher import OpenRouterFetcher
from llmindex.adapters.gateways.artificial_analysis_fetcher import ArtificialAnalysisFetcher
from llmindex.domain.services.matching_engine import MatchingEngine
from llmindex.adapters.persistence.json_exporter import JSONExporter

class LLMIndexSync:
    """
    Synchronous entry point for LLMIndex. 
    Perfect for scripts, notebooks, and CLI tools. No 'await' required.
    """
    
    def __init__(self, mode: Literal["sqlite", "json"] = "sqlite", path: Optional[str] = None):
        self.mode = mode
        if mode == "sqlite":
            self.repository = SQLiteModelRepository(database_url=path)
        else:
            self.repository = JSONModelRepository(file_path=path or "llmindex.json")

    def get_models(self, **kwargs) -> List[LLMModel]:
        """Base query method."""
        return self.repository.get_all(**kwargs)

    def get_model(self, model_id: str) -> Optional[LLMModel]:
        return self.repository.get_by_id(model_id)

    # --- Smart Query Methods ---

    def get_smartest(self, limit: int = 10) -> List[LLMModel]:
        """Top models by overall intelligence score."""
        return self.get_models(sort_by="intelligence", page_size=limit)

    def get_cheapest(self, best_for: Optional[str] = None, limit: int = 10) -> List[LLMModel]:
        """Models sorted by price (input + output) ascending."""
        return self.get_models(best_for=best_for, sort_by="price", sort_order="asc", page_size=limit)

    def get_fastest(self, limit: int = 10) -> List[LLMModel]:
        """Top models by Output TPS (Tokens Per Second)."""
        return self.get_models(sort_by="speed", page_size=limit)

    def get_best_for_coding(self, limit: int = 5) -> List[LLMModel]:
        return self.get_models(best_for="coding", sort_by="intelligence", page_size=limit)

    def get_best_for_reasoning(self, limit: int = 5) -> List[LLMModel]:
        return self.get_models(best_for="reasoning", sort_by="intelligence", page_size=limit)

    def get_best_for_rag(self, limit: int = 5) -> List[LLMModel]:
        """Models with high context and solid intelligence."""
        return self.get_models(best_for="rag", sort_by="intelligence", page_size=limit)

    def get_best_for_multimodal(self, limit: int = 5) -> List[LLMModel]:
        """Models with vision/media capabilities and high ELO."""
        return self.get_models(best_for="multimodal", sort_by="elo", page_size=limit)

    def get_free_models(self) -> List[LLMModel]:
        """All models with zero input cost."""
        return self.get_models(is_free=True)

    def get_top_frontier(self, limit: int = 3) -> List[LLMModel]:
        """The absolute SOTA models (Frontier tier)."""
        # Filter by tier in memory for consistency across repos
        all_models = self.get_models(sort_by="intelligence", page_size=50)
        return [m for m in all_models if m.performance_tier == "frontier"][:limit]

    def get_by_tier(self, tier: Literal["frontier", "pro", "lite"], limit: int = 10) -> List[LLMModel]:
        all_models = self.get_models(sort_by="intelligence", page_size=100)
        return [m for m in all_models if m.performance_tier == tier][:limit]

    def get_by_provider(self, provider: str, limit: int = 10) -> List[LLMModel]:
        return self.get_models(provider=provider, page_size=limit)

    def search(self, query: str, limit: int = 10) -> List[LLMModel]:
        """Fuzzy search models by name, provider or ID."""
        return self.repository.search(query, limit=limit)

    def sync(self) -> List[LLMModel]:
        """Synchronize registry (Sync wrapper for the async use case)."""
        if self.mode == "json":
            raise ValueError("Sync is not supported in JSON mode.")
        return asyncio.run(self._async_sync())

    async def _async_sync(self):
        fetchers = [OpenRouterFetcher(), ArtificialAnalysisFetcher()]
        use_case = SyncRegistryUseCase(
            repository=self.repository, 
            gateways=fetchers, 
            matching_engine=MatchingEngine(85.0),
            exporter=JSONExporter("llmindex.json")
        )
        return await use_case.execute()


class LLMIndex:
    """
    Asynchronous entry point for LLMIndex. 
    Ideal for FastAPI, Discord bots, and async apps.
    """
    
    def __init__(self, mode: Literal["sqlite", "json"] = "sqlite", path: Optional[str] = None):
        self.mode = mode
        if mode == "sqlite":
            self.repository = SQLiteModelRepository(database_url=path)
        else:
            self.repository = JSONModelRepository(file_path=path or "llmindex.json")

    async def get_models(self, **kwargs) -> List[LLMModel]:
        return self.repository.get_all(**kwargs)

    async def get_model(self, model_id: str) -> Optional[LLMModel]:
        return self.repository.get_by_id(model_id)

    # --- Smart Query Methods (Async) ---

    async def get_smartest(self, limit: int = 10) -> List[LLMModel]:
        return await self.get_models(sort_by="intelligence", page_size=limit)

    async def get_cheapest(self, best_for: Optional[str] = None, limit: int = 10) -> List[LLMModel]:
        return await self.get_models(best_for=best_for, sort_by="price", sort_order="asc", page_size=limit)

    async def get_fastest(self, limit: int = 10) -> List[LLMModel]:
        return await self.get_models(sort_by="speed", page_size=limit)

    async def get_best_for_coding(self, limit: int = 5) -> List[LLMModel]:
        return await self.get_models(best_for="coding", sort_by="intelligence", page_size=limit)

    async def get_best_for_reasoning(self, limit: int = 5) -> List[LLMModel]:
        return await self.get_models(best_for="reasoning", sort_by="intelligence", page_size=limit)

    async def get_best_for_rag(self, limit: int = 5) -> List[LLMModel]:
        return await self.get_models(best_for="rag", sort_by="intelligence", page_size=limit)

    async def get_best_for_multimodal(self, limit: int = 5) -> List[LLMModel]:
        return await self.get_models(best_for="multimodal", sort_by="elo", page_size=limit)

    async def get_free_models(self) -> List[LLMModel]:
        return await self.get_models(is_free=True)

    async def get_top_frontier(self, limit: int = 3) -> List[LLMModel]:
        all_models = await self.get_models(sort_by="intelligence", page_size=50)
        return [m for m in all_models if m.performance_tier == "frontier"][:limit]

    async def get_by_tier(self, tier: Literal["frontier", "pro", "lite"], limit: int = 10) -> List[LLMModel]:
        all_models = await self.get_models(sort_by="intelligence", page_size=100)
        return [m for m in all_models if m.performance_tier == tier][:limit]

    async def get_by_provider(self, provider: str, limit: int = 10) -> List[LLMModel]:
        return await self.get_models(provider=provider, page_size=limit)

    async def search(self, query: str, limit: int = 10) -> List[LLMModel]:
        return self.repository.search(query, limit=limit)

    async def sync(self) -> List[LLMModel]:
        if self.mode == "json":
            raise ValueError("Sync is not supported in JSON mode.")
        fetchers = [OpenRouterFetcher(), ArtificialAnalysisFetcher()]
        use_case = SyncRegistryUseCase(
            repository=self.repository, 
            gateways=fetchers, 
            matching_engine=MatchingEngine(85.0),
            exporter=JSONExporter("llmindex.json")
        )
        return await use_case.execute()

__all__ = [
    "LLMIndex",
    "LLMIndexSync",
    "LLMModel", 
    "Pricing", 
    "Benchmarks", 
    "SQLiteModelRepository", 
    "JSONModelRepository",
    "SyncRegistryUseCase", 
    "OpenRouterFetcher",
    "ArtificialAnalysisFetcher"
]
