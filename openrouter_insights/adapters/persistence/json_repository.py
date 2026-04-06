import json
from typing import List, Optional
from rapidfuzz import process, fuzz
from openrouter_insights.domain.entities import LLMModel
from openrouter_insights.domain.interfaces import IModelRepository

class JSONModelRepository(IModelRepository):
    """
    Synchronous implementation of IModelRepository using a static JSON file.
    Ideal for 'low-infra' consumption as a dependency.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._models = self._load()

    def _load(self) -> List[LLMModel]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Support for new structured format (v2.0)
                if isinstance(data, dict) and "models" in data:
                    data = data["models"]
                
                # Check for valid list structure
                if not isinstance(data, list):
                    return []
                    
                return [LLMModel.model_validate(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return []

    def get_all(
        self, 
        provider: Optional[str] = None,
        best_for: Optional[str] = None,
        is_free: bool = False,
        min_intelligence: Optional[float] = None,
        filter_virtual: bool = True,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> List[LLMModel]:
        # Filtering
        filtered = self._models
        if filter_virtual:
            filtered = [m for m in filtered if not m.is_virtual]
        if provider:
            filtered = [m for m in filtered if m.provider.lower() == provider.lower()]
        if is_free:
            filtered = [m for m in filtered if m.pricing.input == 0]
        if min_intelligence:
            filtered = [m for m in filtered if m.benchmarks and (m.benchmarks.intelligence_score or 0) >= min_intelligence]
        if best_for:
            filtered = [m for m in filtered if best_for.lower() in [t.lower() for t in m.best_for]]

        # Sorting
        reverse = sort_order == "desc"
        if sort_by == "price":
            filtered.sort(key=lambda m: m.pricing.input + m.pricing.output, reverse=False if sort_order == "asc" else True)
        elif sort_by == "intelligence":
            filtered.sort(key=lambda m: m.benchmarks.intelligence_score if m.benchmarks and m.benchmarks.intelligence_score else 0, reverse=reverse)
        elif sort_by == "speed":
            filtered.sort(key=lambda m: m.benchmarks.speed_score if m.benchmarks and m.benchmarks.speed_score else 0, reverse=reverse)
        elif sort_by == "elo":
            filtered.sort(key=lambda m: m.benchmarks.elo_score if m.benchmarks and m.benchmarks.elo_score else 0, reverse=reverse)

        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        return filtered[start:end]

    def get_by_id(self, model_id: str) -> Optional[LLMModel]:
        for model in self._models:
            if model.id == model_id:
                return model
        return None

    def get_best_alternative(self, model_id: str, max_price: Optional[float] = None) -> Optional[LLMModel]:
        source = self.get_by_id(model_id)
        if not source:
            return None
        
        candidates = [
            m for m in self._models 
            if m.id != model_id and not m.is_virtual and source.performance_tier in m.best_for
        ]
        
        if max_price is not None:
            candidates = [m for m in candidates if (m.pricing.input + m.pricing.output) <= max_price]
            
        if not candidates:
            return None
        
        # Sort by intelligence
        candidates.sort(key=lambda m: m.intelligence_score, reverse=True)
        return candidates[0]

    def get_count(
        self,
        provider: Optional[str] = None,
        best_for: Optional[str] = None,
        is_free: bool = False,
        min_intelligence: Optional[float] = None,
        filter_virtual: bool = True
    ) -> int:
        return len(self.get_all(provider, best_for, is_free, min_intelligence, filter_virtual, page_size=1000000))

    def search(self, query: str, limit: int = 10) -> List[LLMModel]:
        """Fuzzy search models by name or provider."""
        model_names = [f"{m.provider} {m.name} {m.id}" for m in self._models]
        results = process.extract(query, model_names, scorer=fuzz.WRatio, limit=limit)
        
        found_models = []
        for res in results:
            # res: (string, score, index)
            found_models.append(self._models[res[2]])
        return found_models

    def save(self, model: LLMModel) -> None:
        pass

    def save_batch(self, models: List[LLMModel]) -> None:
        pass
