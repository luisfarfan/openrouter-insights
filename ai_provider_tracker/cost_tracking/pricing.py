import json
from importlib import resources
from pathlib import Path
from typing import Iterable, List, Optional

from ai_provider_tracker.cost_tracking.models import PricingEntry


class PricingCatalog:
    """Loads provider pricing from the bundled JSON catalog or a custom path."""

    def __init__(self, path: Optional[str] = None):
        self.path = path
        self.entries = self._load_entries()

    def _load_entries(self) -> List[PricingEntry]:
        if self.path:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            catalog = resources.files("ai_provider_tracker.data").joinpath("pricing_catalog.json")
            data = json.loads(catalog.read_text(encoding="utf-8"))

        prices = data.get("prices", data if isinstance(data, list) else [])
        return [PricingEntry.model_validate(item) for item in prices]

    def find_prices(self, provider: str, model: str) -> List[PricingEntry]:
        provider_key = provider.lower()
        model_key = model.lower()
        return [
            entry
            for entry in self.entries
            if entry.provider.lower() == provider_key and entry.model.lower() == model_key
        ]

    def find_price(self, provider: str, model: str, metric_type: str) -> Optional[PricingEntry]:
        metric_key = metric_type.lower()
        for entry in self.find_prices(provider, model):
            if entry.metric_type.lower() == metric_key:
                return entry
        return None

    def providers(self) -> Iterable[str]:
        return sorted({entry.provider for entry in self.entries})
