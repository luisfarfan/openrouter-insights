import json
import sqlite3
from decimal import Decimal

from ai_provider_tracker import CostTracker
from ai_provider_tracker.cost_tracking.pricing import PricingCatalog


def write_catalog(path, prices):
    path.write_text(
        json.dumps(
            {
                "metadata": {"format_version": "1.0", "generated_at": "test"},
                "prices": prices,
            }
        ),
        encoding="utf-8",
    )


def price(provider, model, metric_type, unit_price):
    return {
        "provider": provider,
        "model": model,
        "metric_type": metric_type,
        "unit_price": unit_price,
        "currency": "USD",
        "raw": {},
    }


def test_pricing_catalog_loads_bundled():
    catalog = PricingCatalog()
    assert "fal" in catalog.providers()
    assert catalog.find_price("fal", "fal-ai/flux/dev", "image") is not None


def test_pricing_catalog_loads_custom(tmp_path):
    path = tmp_path / "pricing.json"
    write_catalog(path, [price("fal", "model/a", "request", "0.10")])

    catalog = PricingCatalog(str(path))

    entry = catalog.find_price("fal", "model/a", "request")
    assert entry is not None
    assert entry.unit_price == Decimal("0.10")


def test_fal_image_cost_from_num_images(tmp_path):
    path = tmp_path / "pricing.json"
    write_catalog(path, [price("fal", "fal-ai/flux/dev", "image", "0.025")])

    tracker = CostTracker(pricing_catalog_path=str(path))
    event = tracker.track_generation(
        provider="fal",
        model="fal-ai/flux/dev",
        request={"prompt": "city", "num_images": 2},
        response={"images": [{"url": "a"}, {"url": "b"}]},
    )

    assert event.cost.total == Decimal("0.050")
    assert event.cost.breakdown[0].quantity == Decimal("2")
    assert event.cost.source == "public_snapshot"


def test_fal_image_cost_from_response_images(tmp_path):
    path = tmp_path / "pricing.json"
    write_catalog(path, [price("fal", "fal-ai/flux/dev", "image", "0.025")])

    tracker = CostTracker(pricing_catalog_path=str(path))
    event = tracker.track_generation(
        provider="fal",
        model="fal-ai/flux/dev",
        request={"prompt": "city"},
        response={"images": [{"url": "a"}, {"url": "b"}, {"url": "c"}]},
    )

    assert event.cost.total == Decimal("0.075")
    assert event.cost.breakdown[0].quantity == Decimal("3")


def test_fal_request_cost(tmp_path):
    path = tmp_path / "pricing.json"
    write_catalog(path, [price("fal", "fal-ai/model", "request", "0.01")])

    tracker = CostTracker(pricing_catalog_path=str(path))
    event = tracker.track_generation("fal", "fal-ai/model", {}, {"ok": True})

    assert event.cost.total == Decimal("0.01")
    assert event.normalized_usage.units[0].metric_type == "request"


def test_fal_megapixel_cost(tmp_path):
    path = tmp_path / "pricing.json"
    write_catalog(path, [price("fal", "fal-ai/model", "megapixel", "0.02")])

    tracker = CostTracker(pricing_catalog_path=str(path))
    event = tracker.track_generation(
        "fal",
        "fal-ai/model",
        {"image_size": "1000x500"},
        {"ok": True},
    )

    assert event.cost.total == Decimal("0.010")
    assert event.cost.breakdown[0].quantity == Decimal("0.5")


def test_fal_video_second_cost(tmp_path):
    path = tmp_path / "pricing.json"
    write_catalog(path, [price("fal", "fal-ai/video", "video_second", "0.05")])

    tracker = CostTracker(pricing_catalog_path=str(path))
    event = tracker.track_generation("fal", "fal-ai/video", {"duration": 6}, {"video": {"url": "v"}})

    assert event.cost.total == Decimal("0.30")
    assert event.normalized_usage.usage_type == "video"


def test_fal_unknown_unit_is_low_confidence_unknown(tmp_path):
    path = tmp_path / "pricing.json"
    write_catalog(path, [price("fal", "fal-ai/model", "gpu_second", "0.001")])

    tracker = CostTracker(pricing_catalog_path=str(path))
    event = tracker.track_generation("fal", "fal-ai/model", {}, {"ok": True})

    assert event.cost.total == Decimal("0")
    assert event.cost.source == "unknown"
    assert event.cost.confidence == "low"


def test_openrouter_uses_provider_reported_cost(tmp_path):
    path = tmp_path / "pricing.json"
    write_catalog(
        path,
        [
            price("openrouter", "openai/gpt", "input_token", "0.001"),
            price("openrouter", "openai/gpt", "output_token", "0.002"),
        ],
    )

    tracker = CostTracker(pricing_catalog_path=str(path))
    event = tracker.track_generation(
        "openrouter",
        "openai/gpt",
        {"messages": []},
        {"usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": "0.123"}},
    )

    assert event.cost.total == Decimal("0.123")
    assert event.cost.provider_reported_total == Decimal("0.123")
    assert event.cost.estimated_total == Decimal("0.020")
    assert event.cost.source == "provider_reported"


def test_openrouter_fallback_cost_by_tokens(tmp_path):
    path = tmp_path / "pricing.json"
    write_catalog(
        path,
        [
            price("openrouter", "openai/gpt", "input_token", "0.001"),
            price("openrouter", "openai/gpt", "output_token", "0.002"),
        ],
    )

    tracker = CostTracker(pricing_catalog_path=str(path))
    event = tracker.track_generation(
        "openrouter",
        "openai/gpt",
        {},
        {"usage": {"prompt_tokens": 10, "completion_tokens": 5}},
    )

    assert event.cost.total == Decimal("0.020")
    assert event.cost.source == "public_snapshot"


def test_openrouter_without_usage_is_unknown(tmp_path):
    path = tmp_path / "pricing.json"
    write_catalog(path, [])

    tracker = CostTracker(pricing_catalog_path=str(path))
    event = tracker.track_generation("openrouter", "openai/gpt", {}, {"choices": []})

    assert event.cost.total == Decimal("0")
    assert event.cost.source == "unknown"


def test_sqlite_repository_persists_event(tmp_path):
    pricing_path = tmp_path / "pricing.json"
    sqlite_path = tmp_path / "usage.sqlite"
    write_catalog(pricing_path, [price("fal", "fal-ai/flux/dev", "image", "0.025")])

    tracker = CostTracker(pricing_catalog_path=str(pricing_path), sqlite_path=str(sqlite_path))
    event = tracker.track_generation(
        "fal",
        "fal-ai/flux/dev",
        {"prompt": "city"},
        {"images": [{"url": "a"}]},
        metadata={"project_id": "demo"},
    )

    with sqlite3.connect(sqlite_path) as conn:
        row = conn.execute(
            "SELECT id, provider, model, total_cost, raw_request, raw_response FROM ai_generation_usage"
        ).fetchone()

    assert row[0] == event.id
    assert row[1] == "fal"
    assert row[2] == "fal-ai/flux/dev"
    assert row[3] == "0.025"
    assert json.loads(row[4])["prompt"] == "city"
    assert json.loads(row[5])["images"][0]["url"] == "a"
