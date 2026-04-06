import json
import logging
from datetime import datetime
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
        """Serialize models to a structured JSON registry with metadata."""
        try:
            # Sort models for deterministic output
            sorted_models = sorted(models, key=lambda m: m.id)
            
            # Map to serializable dictionaries (excludes 'last_synced' per LLMModel config)
            model_list = [model.model_dump(mode="json") for model in sorted_models]
            
            # Prepare new unified structure
            new_registry = {
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "total_models": len(models),
                    "format_version": "2.0"
                },
                "models": model_list
            }

            # Check for changes (Comparing only the 'models' payload to avoid noisy updates)
            if self.output_path.exists():
                try:
                    with open(self.output_path, "r", encoding="utf-8") as f:
                        current_registry = json.load(f)
                    
                    if current_registry.get("models") == model_list:
                        logger.info("Registry content unchanged. Skipping export to avoid redundant commits.")
                        return
                except (json.JSONDecodeError, KeyError):
                    logger.warning("Could not parse existing registry. Overwriting with fresh data.")

            # Write to the project root
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(new_registry, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully exported {len(models)} unified models to {self.output_path}")
        except Exception as e:
            logger.error(f"Failed to export Unified Registry: {str(e)}")
            raise e
