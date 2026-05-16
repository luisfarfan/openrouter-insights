from typing import Any, Dict, Optional

from ai_provider_tracker.cost_tracking.calculator import CostCalculator
from ai_provider_tracker.cost_tracking.models import GenerationUsageEvent
from ai_provider_tracker.cost_tracking.normalizers import FalUsageNormalizer, OpenRouterUsageNormalizer
from ai_provider_tracker.cost_tracking.pricing import PricingCatalog
from ai_provider_tracker.cost_tracking.repository import SQLiteUsageRepository
from ai_provider_tracker.cost_tracking.utils import to_plain_data


class CostTracker:
    def __init__(
        self,
        pricing_catalog_path: Optional[str] = None,
        sqlite_path: Optional[str] = None,
    ):
        self.catalog = PricingCatalog(pricing_catalog_path)
        self.calculator = CostCalculator()
        self.repository = SQLiteUsageRepository(sqlite_path) if sqlite_path else None
        self.fal_normalizer = FalUsageNormalizer()
        self.openrouter_normalizer = OpenRouterUsageNormalizer()

    def track_generation(
        self,
        provider: str,
        model: str,
        request: Any,
        response: Any,
        metadata: Optional[Dict[str, Any]] = None,
        request_type: Optional[str] = None,
    ) -> GenerationUsageEvent:
        provider_key = provider.lower()
        prices = self.catalog.find_prices(provider_key, model)
        provider_reported_total = None

        if provider_key == "fal":
            normalized_usage = self.fal_normalizer.normalize(model, request, response, prices)
        elif provider_key == "openrouter":
            normalized_usage, provider_reported_total = self.openrouter_normalizer.normalize(
                model,
                request,
                response,
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        cost = self.calculator.calculate(
            normalized_usage,
            prices,
            provider_reported_total=provider_reported_total,
        )

        event = GenerationUsageEvent(
            provider=provider_key,
            model=model,
            request_type=request_type or normalized_usage.usage_type,
            normalized_usage=normalized_usage,
            cost=cost,
            raw_request=to_plain_data(request),
            raw_response=to_plain_data(response),
            metadata=metadata or {},
        )

        if self.repository:
            self.repository.save(event)

        return event
