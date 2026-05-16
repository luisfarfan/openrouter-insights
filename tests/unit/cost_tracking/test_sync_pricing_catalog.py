import json

import pytest
from aioresponses import aioresponses

from scripts.sync_pricing_catalog import (
    FAL_PRICING_URL,
    OPENROUTER_MODELS_URL,
    sync_pricing_catalog,
)


@pytest.mark.asyncio
async def test_sync_pricing_catalog_generates_deterministic_json(tmp_path, monkeypatch):
    monkeypatch.delenv("FAL_KEY", raising=False)
    monkeypatch.delenv("FAL_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    output = tmp_path / "pricing_catalog.json"

    with aioresponses() as mock:
        mock.get(
            FAL_PRICING_URL,
            payload={
                "prices": [
                    {
                        "endpoint_id": "fal-ai/flux/dev",
                        "unit": "image",
                        "unit_price": 0.025,
                        "currency": "USD",
                    }
                ]
            },
        )
        mock.get(
            OPENROUTER_MODELS_URL,
            payload={
                "data": [
                    {
                        "id": "openai/gpt",
                        "pricing": {
                            "prompt": "0.000001",
                            "completion": "0.000002",
                        },
                    }
                ]
            },
        )

        changed = await sync_pricing_catalog(str(output))

    data = json.loads(output.read_text(encoding="utf-8"))
    assert changed is True
    assert data["metadata"]["format_version"] == "1.0"
    assert [item["provider"] for item in data["prices"]] == [
        "fal",
        "openrouter",
        "openrouter",
    ]
    assert data["prices"][0]["model"] == "fal-ai/flux/dev"
    assert data["prices"][1]["metric_type"] == "input_token"
    assert data["prices"][2]["metric_type"] == "output_token"


@pytest.mark.asyncio
async def test_sync_pricing_catalog_does_not_rewrite_when_prices_unchanged(tmp_path, monkeypatch):
    monkeypatch.delenv("FAL_KEY", raising=False)
    monkeypatch.delenv("FAL_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    output = tmp_path / "pricing_catalog.json"

    async def run_once():
        with aioresponses() as mock:
            mock.get(
                FAL_PRICING_URL,
                payload={
                    "prices": [
                        {
                            "endpoint_id": "fal-ai/model",
                            "unit": "request",
                            "unit_price": "0.01",
                            "currency": "USD",
                        }
                    ]
                },
            )
            mock.get(OPENROUTER_MODELS_URL, payload={"data": []})
            return await sync_pricing_catalog(str(output))

    assert await run_once() is True
    first_payload = output.read_text(encoding="utf-8")
    assert await run_once() is False
    assert output.read_text(encoding="utf-8") == first_payload
