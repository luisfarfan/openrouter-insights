from decimal import Decimal
from typing import List, Optional

from ai_provider_tracker.cost_tracking.models import (
    CostBreakdownLine,
    CostResult,
    NormalizedUsage,
    PricingEntry,
)


class CostCalculator:
    def calculate(
        self,
        usage: NormalizedUsage,
        prices: List[PricingEntry],
        provider_reported_total: Optional[Decimal] = None,
    ) -> CostResult:
        price_by_metric = {price.metric_type: price for price in prices}
        breakdown: List[CostBreakdownLine] = []
        missing_price = False

        for unit in usage.units:
            price = price_by_metric.get(unit.metric_type)
            if price is None:
                missing_price = True
                continue

            subtotal = unit.quantity * price.unit_price
            breakdown.append(
                CostBreakdownLine(
                    metric_type=unit.metric_type,
                    quantity=unit.quantity,
                    unit_price=price.unit_price,
                    subtotal=subtotal,
                    currency=price.currency,
                )
            )

        estimated_total = sum((line.subtotal for line in breakdown), Decimal("0"))
        currency = breakdown[0].currency if breakdown else "USD"

        if provider_reported_total is not None:
            return CostResult(
                total=provider_reported_total,
                currency=currency,
                source="provider_reported",
                confidence="high",
                breakdown=breakdown,
                provider_reported_total=provider_reported_total,
                estimated_total=estimated_total if breakdown else None,
            )

        if not usage.units or (missing_price and not breakdown):
            return CostResult(
                total=Decimal("0"),
                currency=currency,
                source="unknown",
                confidence="low",
                breakdown=breakdown,
                estimated_total=estimated_total if breakdown else None,
            )

        confidence = "low" if missing_price else "high"
        return CostResult(
            total=estimated_total,
            currency=currency,
            source="public_snapshot",
            confidence=confidence,
            breakdown=breakdown,
            estimated_total=estimated_total,
        )
