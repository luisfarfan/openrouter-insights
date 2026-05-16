# AGENT.md: AI Provider Tracker Operating Guide

## Project Context

**AI Provider Tracker** is a Python library for provider-neutral AI usage and cost tracking.

The main product is `CostTracker`: users call providers such as FAL.AI and OpenRouter themselves, then pass request/response payloads to the tracker to normalize usage, calculate cost, and optionally persist an auditable local event.

The former OpenRouter registry functionality remains in the package as legacy compatibility (`LLMIndex`, `LLMIndexSync`). Do not treat it as the primary product surface for new work.

## Core Architecture

- `ai_provider_tracker/cost_tracking/models.py`
  - Public Pydantic models: `UsageUnit`, `NormalizedUsage`, `CostResult`, `GenerationUsageEvent`.

- `ai_provider_tracker/cost_tracking/pricing.py`
  - Loads bundled or custom pricing catalogs.

- `ai_provider_tracker/cost_tracking/normalizers.py`
  - Provider-specific usage extraction for FAL.AI and OpenRouter.

- `ai_provider_tracker/cost_tracking/calculator.py`
  - Decimal-based cost calculations.

- `ai_provider_tracker/cost_tracking/repository.py`
  - Optional SQLite persistence.

- `ai_provider_tracker/cost_tracking/tracker.py`
  - Public `CostTracker` facade.

- `ai_provider_tracker/data/pricing_catalog.json`
  - Bundled public pricing snapshot.

- `scripts/sync_pricing_catalog.py`
  - Pricing sync script used by GitHub Actions.

## Development Rules

1. Runtime cost tracking must not call provider pricing APIs.
2. Provider-specific parsing belongs in normalizers, not application-facing APIs.
3. Cost math must use `Decimal`, not `float`.
4. Keep raw request/response persistence optional.
5. Preserve `openrouter_insights` as a temporary shim unless explicitly removing backward compatibility.
6. Update README and docs when changing public APIs or pricing behavior.
7. Add tests for every new metric type or provider.

## Common Commands

```bash
poetry install
poetry run pytest -q
poetry build
poetry run python scripts/sync_pricing_catalog.py
```

## Public Import

New code:

```python
from ai_provider_tracker import CostTracker
```

Temporary compatibility:

```python
from openrouter_insights import CostTracker
```

## Release Notes

The PyPI package name is `ai-provider-tracker`. The import package is `ai_provider_tracker`.
