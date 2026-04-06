from typing import List, Optional
from pydantic import BaseModel, Field, computed_field
from datetime import datetime

class Pricing(BaseModel):
    """Pricing in USD per 1M tokens."""
    input: float = 0.0
    output: float = 0.0

class Benchmarks(BaseModel):
    """Evaluation metrics from ArtificialAnalysis."""
    intelligence_score: Optional[float] = None
    speed_score: Optional[float] = None # TPS
    reasoning_score: Optional[float] = None
    coding_score: Optional[float] = None
    cost_efficiency: Optional[float] = None
    elo_score: Optional[float] = None # Multimodal Quality Rating (v2)

class LLMModel(BaseModel):
    """
    Unified LLM Model Entity.
    The single source of truth for a model's capabilities and costs.
    """
    id: str
    name: str
    provider: str
    context_length: int = 0
    pricing: Pricing
    modalities: List[str] = ["text"]
    benchmarks: Optional[Benchmarks] = None
    last_synced: datetime = Field(default_factory=datetime.now, exclude=True)

    @computed_field
    @property
    def best_for(self) -> List[str]:
        """Dynamically Tag models based on unified data."""
        tags = []
        if self.benchmarks:
            if (self.benchmarks.coding_score or 0) > 80:
                tags.append("coding")
            if (self.benchmarks.intelligence_score or 0) > 85:
                tags.append("reasoning")
            if (self.benchmarks.speed_score or 0) > 100:
                tags.append("real-time")
            if self.benchmarks.elo_score:
                tags.append("multimodal-high-fidelity")
        
        if "image" in self.modalities or "audio" in self.modalities:
            if "multimodal" not in tags:
                tags.append("multimodal")
        
        # Context-based tags
        if self.context_length >= 128000:
            tags.append("rag")
            
        return tags

    @computed_field
    @property
    def performance_tier(self) -> str:
        """Categorize models into tiers."""
        base_score = 0
        if self.benchmarks and self.benchmarks.intelligence_score:
            base_score = self.benchmarks.intelligence_score
            
        if base_score > 90:
            return "frontier"
        if base_score > 70:
            return "pro"
        return "lite"


    @computed_field
    @property
    def efficiency_score(self) -> float:
        """Calculate bang-for-buck score."""
        if not self.benchmarks or not self.benchmarks.intelligence_score:
            return 0.0
        total_cost = self.pricing.input + self.pricing.output
        if total_cost == 0:
            return 1.0 # Free is max efficiency
        return round(self.benchmarks.intelligence_score / (total_cost + 0.01), 4)
