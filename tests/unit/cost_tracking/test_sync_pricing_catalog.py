import json

import pytest
from aioresponses import aioresponses

from scripts.sync_pricing_catalog import (
    FAL_MODELS_URL,
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
            f"{FAL_MODELS_URL}?limit=100",
            payload={
                "models": [
                    {
                        "endpoint_id": "fal-ai/flux/dev",
                        "metadata": {"status": "active"},
                    }
                ],
                "next_cursor": None,
                "has_more": False,
            },
        )
        mock.get(
            f"{FAL_PRICING_URL}?endpoint_id=fal-ai%2Fflux%2Fdev",
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
                f"{FAL_MODELS_URL}?limit=100",
                payload={
                    "models": [{"endpoint_id": "fal-ai/model"}],
                    "next_cursor": None,
                    "has_more": False,
                },
            )
            mock.get(
                f"{FAL_PRICING_URL}?endpoint_id=fal-ai%2Fmodel",
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


@pytest.mark.asyncio
async def test_sync_pricing_catalog_splits_fal_batch_when_endpoint_has_no_pricing(tmp_path, monkeypatch):
    monkeypatch.delenv("FAL_KEY", raising=False)
    monkeypatch.delenv("FAL_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    output = tmp_path / "pricing_catalog.json"
    endpoint_ids = ["fal-ai/model-a", "fal-ai/model-b", "fal-ai/model-c"]
    invalid_endpoint = "fal-ai/model-b"

    with aioresponses() as mock:
        mock.get(
            f"{FAL_MODELS_URL}?limit=100",
            payload={
                "models": [{"endpoint_id": endpoint_id} for endpoint_id in endpoint_ids],
                "next_cursor": None,
                "has_more": False,
            },
        )
        mock.get(
            f"{FAL_PRICING_URL}?endpoint_id=fal-ai%2Fmodel-a%2Cfal-ai%2Fmodel-b",
            status=404,
        )
        mock.get(
            f"{FAL_PRICING_URL}?endpoint_id=fal-ai%2Fmodel-a",
            payload={
                "prices": [
                    {
                        "endpoint_id": "fal-ai/model-a",
                        "unit": "request",
                        "unit_price": "0.01",
                        "currency": "USD",
                    }
                ]
            },
        )
        mock.get(f"{FAL_PRICING_URL}?endpoint_id=fal-ai%2Fmodel-b", status=404)
        mock.get(
            f"{FAL_PRICING_URL}?endpoint_id=fal-ai%2Fmodel-c",
            payload={
                "prices": [
                    {
                        "endpoint_id": "fal-ai/model-c",
                        "unit": "request",
                        "unit_price": "0.02",
                        "currency": "USD",
                    }
                ]
            },
        )
        mock.get(OPENROUTER_MODELS_URL, payload={"data": []})

        changed = await sync_pricing_catalog(str(output), fal_batch_size=2)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert changed is True
    assert len(data["prices"]) == 2
    assert invalid_endpoint not in {item["model"] for item in data["prices"]}
