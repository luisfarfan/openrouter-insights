# AI Context

## Project Identity

This repository is **AI Provider Tracker**.

The primary product is a Python library for tracking AI provider usage and estimating costs per generation/request.

Do not describe the project primarily as OpenRouter Insights or LLMIndex. Those registry APIs still exist only as legacy compatibility features.

## Main User Flow

```python
from ai_provider_tracker import CostTracker

tracker = CostTracker(sqlite_path="ai_usage.sqlite")

event = tracker.track_generation(
    provider="fal",
    model="fal-ai/flux/dev",
    request={"prompt": "city", "num_images": 1},
    response={"images": [{"url": "image.png"}]},
)
```

## Current Architecture

- `ai_provider_tracker/cost_tracking/`
  - Main cost tracking implementation.

- `ai_provider_tracker/data/pricing_catalog.json`
  - Bundled pricing snapshot used at runtime.

- `scripts/sync_pricing_catalog.py`
  - Fetches FAL/OpenRouter pricing and updates bundled catalog.

- `.github/workflows/pricing_sync.yml`
  - Daily pricing sync workflow.

- `openrouter_insights/`
  - Temporary import shim only.

- `ai_provider_tracker/domain`, `adapters`, `use_cases`
  - Legacy model registry functionality.

## Development Rules

1. Prefer adding new provider support through normalizers and pricing catalog entries.
2. Runtime cost calculation must not call provider pricing APIs.
3. Use `Decimal` for cost and quantity math.
4. Keep raw request/response persistence optional and local.
5. Maintain backward compatibility shim until deliberately removed.
6. Keep tests updated for cost behavior and pricing sync.

## Verification

Run:

```bash
poetry run pytest -q
poetry build
```

Expected package name:

```text
ai-provider-tracker
```
