# 05 - Pricing Catalog and Automation

## Bundled Catalog

The package ships:

```text
ai_provider_tracker/data/pricing_catalog.json
```

Shape:

```json
{
  "metadata": {
    "generated_at": "2026-05-16T00:00:00Z",
    "format_version": "1.0"
  },
  "prices": [
    {
      "provider": "fal",
      "model": "fal-ai/flux/dev",
      "metric_type": "image",
      "unit_price": "0.025",
      "currency": "USD",
      "raw": {}
    }
  ]
}
```

## Sync Script

```bash
python scripts/sync_pricing_catalog.py
```

The script fetches:

- FAL pricing from `https://api.fal.ai/v1/models/pricing`
- OpenRouter model pricing from `https://openrouter.ai/api/v1/models`

Environment variables:

- `FAL_KEY` or `FAL_API_KEY`
- `OPENROUTER_API_KEY`

## GitHub Actions

`.github/workflows/pricing_sync.yml` runs daily.

It commits only when `prices` changed. Metadata-only timestamp changes do not trigger commits.

## Accuracy

The public bundled catalog is a reference snapshot. Users with account-specific pricing should generate and pass their own catalog:

```python
tracker = CostTracker(pricing_catalog_path="my_pricing_catalog.json")
```

For invoice-grade accounting, reconcile against provider billing exports or usage APIs.
