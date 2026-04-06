from abc import ABC, abstractmethod
from typing import List, Optional
from openrouter_insights.domain.entities import LLMModel

class IModelRepository(ABC):
    """Port: Interface for LLMModel persistence."""

    @abstractmethod
    def get_by_id(self, model_id: str) -> Optional[LLMModel]: ...

    @abstractmethod
    def get_all(
        self, 
        provider: Optional[str] = None,
        best_for: Optional[str] = None,
        is_free: bool = False,
        min_intelligence: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> List[LLMModel]: ...

    @abstractmethod
    def get_count(
        self,
        provider: Optional[str] = None,
        best_for: Optional[str] = None,
        is_free: bool = False,
        min_intelligence: Optional[float] = None
    ) -> int: ...

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[LLMModel]: ...

    @abstractmethod
    def save(self, model: LLMModel) -> None: ...

    @abstractmethod
    def save_batch(self, models: List[LLMModel]) -> None: ...

class IFetcherGateway(ABC):
    """Port: Interface for fetching data from external APIs."""

    @abstractmethod
    async def fetch_catalog(self) -> List[dict]: ...

    @abstractmethod
    async def fetch_benchmarks(self) -> List[dict]: ...

class IStaticExporter(ABC):
    """Port: Interface for exporting to a static file format."""
    
    @abstractmethod
    async def export(self, models: List[LLMModel]) -> None: ...
