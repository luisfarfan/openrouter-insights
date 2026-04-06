import json
import logging
from pathlib import Path
from typing import List
from openrouter_insights.domain.entities import LLMModel
from openrouter_insights.domain.interfaces import IStaticExporter

logger = logging.getLogger(__name__)

class JSONExporter(IStaticExporter):
    """Adapter: Export entities to a static JSON file (Git-Ops)."""

    def __init__(self, output_path: str = "openrouter_insights.json"):
        self.output_path = Path(output_path)

    def export(self, models: List[LLMModel]) -> None:
        """Serialize a list of models to a single JSON registry."""
        try:
            # Sort models by name or id for deterministic output
            sorted_models = sorted(models, key=lambda m: m.id)
            
            # Map Pydantic objects to serializable dictionaries (handles datetime -> ISO string)
            data = [model.model_dump(mode="json") for model in sorted_models]
            
            # Write to the project root (or specified path)
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully exported {len(models)} unified models to {self.output_path}")
        except Exception as e:
            logger.error(f"Failed to export Unified Registry: {str(e)}")
            raise e
