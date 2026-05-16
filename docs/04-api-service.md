# 04 - Public APIs and Usage

## Primary API: `CostTracker`

```python
from ai_provider_tracker import CostTracker

tracker = CostTracker()

event = tracker.track_generation(
    provider="fal",
    model="fal-ai/flux/dev",
    request={"prompt": "city", "num_images": 2},
    response={"images": [{"url": "a"}, {"url": "b"}]},
)
```

## Constructor

```python
CostTracker(
    pricing_catalog_path: str | None = None,
    sqlite_path: str | None = None,
)
```

- `pricing_catalog_path`: optional custom pricing JSON path.
- `sqlite_path`: optional local SQLite analytics database.

If no pricing path is passed, the bundled catalog is used.

## FAL Example

```python
event = tracker.track_generation(
    provider="fal",
    model="fal-ai/flux/dev",
    request={"prompt": "A cyberpunk city", "num_images": 1},
    response={"images": [{"url": "https://example.com/image.png"}]},
    metadata={"project_id": "demo"},
)

print(event.cost.total)
print(event.cost.breakdown)
```

## OpenRouter Example

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
```

## Legacy Registry APIs

The legacy model discovery APIs remain available:

```python
from ai_provider_tracker import LLMIndexSync

client = LLMIndexSync(mode="json")
models = client.get_smartest(limit=5)
```

These APIs are secondary to the cost tracking surface.
