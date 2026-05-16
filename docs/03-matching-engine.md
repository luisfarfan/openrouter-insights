# 03 - Provider Normalization and Cost Rules

## FAL.AI

FAL pricing entries define the billing unit for each model/endpoint. The tracker infers quantity from request/response payloads.

Supported v1 units:

- `image`
  - Quantity priority: `request.num_images`, then `len(response.images)`, then fallback `1`.

- `request`
  - Quantity is `1`.

- `video_second`
  - Quantity from response/request duration fields.

- `megapixel`
  - Quantity is `width * height / 1_000_000`.
  - Width/height may come from explicit request fields or `image_size` / `resolution`.

Unsupported or ambiguous units:

- Example: `gpu_second`
  - Cost is marked `unknown` unless a future normalizer can reliably infer execution seconds.

## OpenRouter

OpenRouter normalization extracts:

- `usage.cost`
- `usage.prompt_tokens` / `usage.input_tokens`
- `usage.completion_tokens` / `usage.output_tokens`

Rules:

1. If provider-reported cost exists, it becomes `CostResult.total`.
2. If token counts and local pricing exist, `estimated_total` is also calculated.
3. If provider cost is missing, token-based estimate becomes the final total.
4. If usage is missing, cost source is `unknown`.

## Adding a Provider

To add a provider:

1. Add pricing sync support if public pricing exists.
2. Add a provider normalizer that returns `NormalizedUsage`.
3. Ensure `CostTracker.track_generation()` routes to it.
4. Add tests for quantities, missing prices, and persistence.
