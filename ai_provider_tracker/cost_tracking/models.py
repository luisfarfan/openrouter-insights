from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class UsageUnit(BaseModel):
    metric_type: str
    quantity: Decimal


class NormalizedUsage(BaseModel):
    provider: str
    model: str
    usage_type: str
    units: List[UsageUnit] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CostBreakdownLine(BaseModel):
    metric_type: str
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal
    currency: str = "USD"


class CostResult(BaseModel):
    total: Decimal
    currency: str = "USD"
    source: str
    confidence: str
    breakdown: List[CostBreakdownLine] = Field(default_factory=list)
    provider_reported_total: Optional[Decimal] = None
    estimated_total: Optional[Decimal] = None


class GenerationUsageEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    provider: str
    model: str
    request_type: str
    normalized_usage: NormalizedUsage
    cost: CostResult
    raw_request: Dict[str, Any] = Field(default_factory=dict)
    raw_response: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PricingEntry(BaseModel):
    provider: str
    model: str
    metric_type: str
    unit_price: Decimal
    currency: str = "USD"
    raw: Dict[str, Any] = Field(default_factory=dict)
