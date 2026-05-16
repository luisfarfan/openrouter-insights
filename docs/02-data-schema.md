# 02 - Cost Tracking Data Schema

## `UsageUnit`

Represents one measurable billing unit.

```json
{
  "metric_type": "image",
  "quantity": "2"
}
```

Common metric types:

- `image`
- `request`
- `megapixel`
- `video_second`
- `input_token`
- `output_token`
- `gpu_second`

## `NormalizedUsage`

Provider-specific request/response payloads are normalized into this structure.

```json
{
  "provider": "fal",
  "model": "fal-ai/flux/dev",
  "usage_type": "image",
  "units": [
    {"metric_type": "image", "quantity": "2"}
  ],
  "metadata": {}
}
```

## `CostBreakdownLine`

One priced line item.

```json
{
  "metric_type": "image",
  "quantity": "2",
  "unit_price": "0.025",
  "subtotal": "0.050",
  "currency": "USD"
}
```

## `CostResult`

Final cost object returned to users.

```json
{
  "total": "0.050",
  "currency": "USD",
  "source": "public_snapshot",
  "confidence": "high",
  "provider_reported_total": null,
  "estimated_total": "0.050",
  "breakdown": []
}
```

`source` values:

- `provider_reported`: Provider returned cost directly.
- `public_snapshot`: Cost calculated from bundled/local pricing catalog.
- `unknown`: Missing usage quantity, missing price, or unsupported unit.

`confidence` values:

- `high`: Quantity and price are known, or provider reported total.
- `low`: Missing price/quantity or unsupported metric.

## `GenerationUsageEvent`

Persistable event created by `CostTracker`.

```json
{
  "provider": "fal",
  "model": "fal-ai/flux/dev",
  "request_type": "image",
  "normalized_usage": {},
  "cost": {},
  "raw_request": {},
  "raw_response": {},
  "metadata": {},
  "created_at": "2026-05-16T00:00:00Z"
}
```

When `sqlite_path` is configured, this event is stored in `ai_generation_usage`.
