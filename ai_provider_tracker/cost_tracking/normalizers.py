from decimal import Decimal
from typing import Any, Dict, List, Optional

from ai_provider_tracker.cost_tracking.models import NormalizedUsage, PricingEntry, UsageUnit
from ai_provider_tracker.cost_tracking.utils import get_nested, to_decimal, to_plain_data


class FalUsageNormalizer:
    def normalize(
        self,
        model: str,
        request: Any,
        response: Any,
        prices: List[PricingEntry],
    ) -> NormalizedUsage:
        request_data = to_plain_data(request)
        response_data = to_plain_data(response)
        units: List[UsageUnit] = []
        metadata: Dict[str, Any] = {}

        for price in prices:
            quantity = self._quantity_for(price.metric_type, request_data, response_data)
            if quantity is not None:
                units.append(UsageUnit(metric_type=price.metric_type, quantity=quantity))

        if not units and prices:
            metadata["unresolved_metric_types"] = [price.metric_type for price in prices]

        return NormalizedUsage(
            provider="fal",
            model=model,
            usage_type=self._usage_type(prices),
            units=units,
            metadata=metadata,
        )

    def _quantity_for(
        self,
        metric_type: str,
        request: Dict[str, Any],
        response: Dict[str, Any],
    ) -> Optional[Decimal]:
        metric = metric_type.lower()
        if metric == "image":
            return self._image_quantity(request, response)
        if metric == "request":
            return Decimal("1")
        if metric == "video_second":
            return self._duration_seconds(request, response)
        if metric == "megapixel":
            return self._megapixels(request, response)
        return None

    def _image_quantity(self, request: Dict[str, Any], response: Dict[str, Any]) -> Decimal:
        explicit = to_decimal(
            get_nested(
                request,
                [
                    "num_images",
                    "num_inference_steps.images",
                    "arguments.num_images",
                    "image_count",
                    "count",
                ],
            )
        )
        if explicit is not None and explicit > 0:
            return explicit

        images = get_nested(response, ["images", "data.images", "output.images"])
        if isinstance(images, list) and images:
            return Decimal(len(images))

        return Decimal("1")

    def _duration_seconds(
        self,
        request: Dict[str, Any],
        response: Dict[str, Any],
    ) -> Optional[Decimal]:
        value = get_nested(
            response,
            [
                "duration",
                "duration_seconds",
                "video.duration",
                "video.duration_seconds",
                "metadata.duration",
                "metadata.duration_seconds",
            ],
        )
        if value is None:
            value = get_nested(
                request,
                [
                    "duration",
                    "duration_seconds",
                    "video_duration",
                    "arguments.duration",
                    "arguments.duration_seconds",
                ],
            )
        duration = to_decimal(value)
        return duration if duration is not None and duration > 0 else None

    def _megapixels(
        self,
        request: Dict[str, Any],
        response: Dict[str, Any],
    ) -> Optional[Decimal]:
        width = to_decimal(get_nested(response, ["width", "image.width", "metadata.width"]))
        height = to_decimal(get_nested(response, ["height", "image.height", "metadata.height"]))

        if width is None or height is None:
            width, height = self._size_from_request(request)

        if width is None or height is None or width <= 0 or height <= 0:
            return None
        return (width * height) / Decimal("1000000")

    def _size_from_request(self, request: Dict[str, Any]) -> tuple[Optional[Decimal], Optional[Decimal]]:
        width = to_decimal(get_nested(request, ["width", "image_width", "arguments.width"]))
        height = to_decimal(get_nested(request, ["height", "image_height", "arguments.height"]))
        if width is not None and height is not None:
            return width, height

        size = get_nested(request, ["image_size", "resolution", "arguments.image_size", "arguments.resolution"])
        if isinstance(size, str) and "x" in size.lower():
            raw_width, raw_height = size.lower().split("x", 1)
            return to_decimal(raw_width.strip()), to_decimal(raw_height.strip())
        if isinstance(size, dict):
            return to_decimal(size.get("width")), to_decimal(size.get("height"))
        return None, None

    def _usage_type(self, prices: List[PricingEntry]) -> str:
        metrics = {price.metric_type for price in prices}
        if "video_second" in metrics:
            return "video"
        if "image" in metrics or "megapixel" in metrics:
            return "image"
        return "generation"


class OpenRouterUsageNormalizer:
    def normalize(self, model: str, request: Any, response: Any) -> tuple[NormalizedUsage, Optional[Decimal]]:
        response_data = to_plain_data(response)
        usage = response_data.get("usage") or {}

        input_tokens = to_decimal(
            usage.get("prompt_tokens")
            or usage.get("input_tokens")
            or usage.get("prompt")
        )
        output_tokens = to_decimal(
            usage.get("completion_tokens")
            or usage.get("output_tokens")
            or usage.get("completion")
        )
        provider_cost = to_decimal(usage.get("cost") or usage.get("total_cost"))

        units: List[UsageUnit] = []
        if input_tokens is not None:
            units.append(UsageUnit(metric_type="input_token", quantity=input_tokens))
        if output_tokens is not None:
            units.append(UsageUnit(metric_type="output_token", quantity=output_tokens))

        normalized = NormalizedUsage(
            provider="openrouter",
            model=model,
            usage_type="llm",
            units=units,
            metadata={"raw_usage": usage},
        )
        return normalized, provider_cost
