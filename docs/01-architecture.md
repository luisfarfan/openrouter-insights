# 01 - Architecture

## Package Shape

```text
ai_provider_tracker/
  cost_tracking/
    models.py         # Public Pydantic models
    pricing.py        # Bundled/custom pricing catalog loader
    normalizers.py    # Provider-specific usage extraction
    calculator.py     # Decimal-based cost engine
    repository.py     # Optional SQLite event persistence
    tracker.py        # Public CostTracker facade
  data/
    pricing_catalog.json
  adapters/           # Legacy OpenRouter registry API/adapters
  domain/             # Legacy LLM model entities and matching
  use_cases/          # Legacy registry sync pipeline
```

## Runtime Flow

```text
Provider SDK call happens in user app
        |
        v
CostTracker.track_generation(provider, model, request, response)
        |
        v
Provider normalizer extracts NormalizedUsage
        |
        v
PricingCatalog selects local pricing entries
        |
        v
CostCalculator creates CostResult
        |
        v
Optional SQLiteUsageRepository saves GenerationUsageEvent
```

## Pricing Sync Flow

```text
GitHub Actions daily schedule
        |
        v
scripts/sync_pricing_catalog.py
        |
        +--> FAL Pricing API
        +--> OpenRouter Models API
        |
        v
ai_provider_tracker/data/pricing_catalog.json
        |
        v
Commit only if prices changed
```

Runtime requests never call provider pricing APIs.

## Key Design Rules

- Keep provider-specific extraction inside normalizers.
- Keep cost math inside `CostCalculator`.
- Use `Decimal` for money and quantities.
- Store raw request/response only when SQLite persistence is enabled.
- Treat bundled public pricing as an estimate, not invoice-grade truth.
- Prefer provider-reported cost where available, especially for OpenRouter.

## Compatibility

`openrouter_insights` remains as a temporary import shim:

```python
from openrouter_insights import CostTracker
```

New code must import:

```python
from ai_provider_tracker import CostTracker
```
