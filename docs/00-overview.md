# 00 - AI Provider Tracker Overview

## Purpose

**AI Provider Tracker** is a Python library for AI usage and cost tracking.

It is not a provider SDK and it is not a microservice. Applications keep calling providers such as FAL.AI and OpenRouter directly, then pass the request/response payloads to this library to normalize usage, calculate costs, and optionally persist analytics.

## Primary Goals

1. **Per-generation cost tracking**
   - Estimate the cost of a single FAL.AI generation from pricing snapshots and request/response metadata.
   - Use OpenRouter provider-reported cost when available.

2. **Provider-neutral usage normalization**
   - Convert heterogeneous usage models into `UsageUnit` records such as `image`, `video_second`, `megapixel`, `input_token`, and `output_token`.

3. **Runtime independence from pricing APIs**
   - Runtime cost calculations use a bundled/local pricing catalog.
   - Pricing APIs are called by sync scripts, not by `CostTracker.track_generation()`.

4. **Auditability**
   - Optional SQLite persistence stores normalized usage, cost breakdown, raw request, raw response, and caller metadata.

5. **Open-source distribution**
   - Bundled public pricing catalog ships with the PyPI package.
   - Users can provide their own catalog path for account-specific or private pricing.

## Supported Providers in v1

- **FAL.AI**
  - Main value case.
  - Costs are locally estimated from pricing unit + inferred quantity.

- **OpenRouter**
  - Uses `usage.cost` as primary cost when present.
  - Falls back to token-based calculation from the pricing catalog.

## Legacy Registry

The package still includes the original OpenRouter model registry functionality (`LLMIndex`, `LLMIndexSync`) for compatibility. New development should treat cost tracking as the primary product surface.
