# AI Provider Tracker

[![PyPI version](https://img.shields.io/pypi/v/ai-provider-tracker.svg)](https://pypi.org/project/ai-provider-tracker/)
[![Python versions](https://img.shields.io/pypi/pyversions/ai-provider-tracker.svg)](https://pypi.org/project/ai-provider-tracker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI Provider Tracker** is a Python library for tracking AI provider usage and estimating per-generation costs across heterogeneous providers.

It is designed for apps that already call providers such as **FAL.AI** and **OpenRouter**, but need a centralized way to:

- normalize usage metadata
- calculate request/generation costs
- store raw request/response payloads for auditability
- persist optional local analytics in SQLite
- use bundled pricing snapshots without calling pricing APIs at runtime

## Installation

```bash
pip install ai-provider-tracker
```

Optional FastAPI dependencies for the legacy model registry API:

```bash
pip install "ai-provider-tracker[api]"
```

## Cost Tracking

Use your provider SDK as usual, then pass the request and response to the tracker.

```python
from ai_provider_tracker import CostTracker

tracker = CostTracker()

event = tracker.track_generation(
    provider="fal",
    model="fal-ai/flux/dev",
    request={"prompt": "A cyberpunk city", "num_images": 2},
    response={"images": [{"url": "a"}, {"url": "b"}]},
)

print(event.cost.total)       # 0.050
print(event.cost.source)      # public_snapshot
print(event.cost.confidence)  # high
print(event.cost.breakdown)
```

Enable local SQLite persistence:

```python
tracker = CostTracker(sqlite_path="ai_usage.sqlite")
```

This stores generation events with normalized usage, cost breakdown, raw request, raw response, and metadata.

## OpenRouter

For OpenRouter, provider-reported usage cost is preferred when present:

```python
event = tracker.track_generation(
    provider="openrouter",
    model="anthropic/claude-sonnet-4.5",
    request={"messages": [{"role": "user", "content": "Hello"}]},
    response={
        "usage": {
            "prompt_tokens": 1200,
            "completion_tokens": 800,
            "cost": "0.015",
        }
    },
)

print(event.cost.total)   # provider-reported cost
print(event.cost.source)  # provider_reported
```

If `usage.cost` is not present, the tracker falls back to token-based calculation using the bundled pricing catalog when possible.

## Pricing Catalog

The package ships with a bundled JSON pricing catalog:

```text
ai_provider_tracker/data/pricing_catalog.json
```

Runtime requests do not call pricing APIs. Pricing sync is handled by:

```bash
python scripts/sync_pricing_catalog.py
```

The GitHub Actions workflow `.github/workflows/pricing_sync.yml` runs daily and commits the catalog only when prices actually change.

## Legacy Model Registry

This package still includes the original OpenRouter model registry APIs:

```python
from ai_provider_tracker import LLMIndexSync

client = LLMIndexSync(mode="json")
models = client.get_cheapest(limit=5)
```

The old import path remains available temporarily:

```python
from openrouter_insights import CostTracker
```

New code should use:

```python
from ai_provider_tracker import CostTracker
```

## Accuracy Contract

Cost values are intended for product analytics, internal attribution, and budget monitoring.

- FAL.AI costs are locally estimated from pricing snapshots and normalized request/response metadata.
- OpenRouter costs use provider-reported cost when available.
- Public bundled pricing is a reference snapshot, not a guarantee of account-specific billing.

For invoice-grade accounting, reconcile against provider billing/usage APIs.

## License

MIT
