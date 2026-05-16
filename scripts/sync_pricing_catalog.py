import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import aiohttp


DEFAULT_OUTPUT = "ai_provider_tracker/data/pricing_catalog.json"
FAL_PRICING_URL = "https://api.fal.ai/v1/models/pricing"
FAL_MODELS_URL = "https://api.fal.ai/v1/models"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


def decimal_string(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    try:
        return str(Decimal(str(value)))
    except (InvalidOperation, ValueError, TypeError):
        return None


async def fetch_json(session: aiohttp.ClientSession, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
    async with session.get(url, headers=headers or {}) as response:
        response.raise_for_status()
        return await response.json()


async def fetch_fal_prices(session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
    key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
    headers = {"Authorization": f"Key {key}"} if key else {}
    endpoint_ids = await fetch_fal_endpoint_ids(session, headers)
    prices: List[Dict[str, Any]] = []

    for batch in chunked(endpoint_ids, 50):
        url = f"{FAL_PRICING_URL}?{urlencode({'endpoint_id': ','.join(batch)})}"
        data = await fetch_json(session, url, headers=headers)
        raw_prices = data.get("prices", data if isinstance(data, list) else [])

        for item in raw_prices:
            unit_price = decimal_string(item.get("unit_price"))
            model = item.get("endpoint_id")
            metric_type = item.get("unit")
            if not model or not metric_type or unit_price is None:
                continue
            prices.append(
                {
                    "provider": "fal",
                    "model": model,
                    "metric_type": str(metric_type),
                    "unit_price": unit_price,
                    "currency": item.get("currency") or "USD",
                    "raw": item,
                }
            )

    return prices


async def fetch_fal_endpoint_ids(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
) -> List[str]:
    endpoint_ids: List[str] = []
    cursor: Optional[str] = None

    while True:
        params = {"limit": "100"}
        if cursor:
            params["cursor"] = cursor
        url = f"{FAL_MODELS_URL}?{urlencode(params)}"
        data = await fetch_json(session, url, headers=headers)
        models = data.get("models", data if isinstance(data, list) else [])

        for item in models:
            endpoint_id = item.get("endpoint_id")
            if endpoint_id:
                endpoint_ids.append(endpoint_id)

        cursor = data.get("next_cursor") if isinstance(data, dict) else None
        if not cursor:
            break

    return endpoint_ids


def chunked(items: List[str], size: int) -> List[List[str]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


async def fetch_openrouter_prices(session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
    key = os.getenv("OPENROUTER_API_KEY")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    data = await fetch_json(session, OPENROUTER_MODELS_URL, headers=headers)
    models = data.get("data", data if isinstance(data, list) else [])
    prices: List[Dict[str, Any]] = []

    metric_map = {
        "prompt": "input_token",
        "completion": "output_token",
        "request": "request",
        "image": "image",
    }

    for model in models:
        model_id = model.get("id")
        raw_pricing = model.get("pricing") or {}
        if not model_id:
            continue
        for source_metric, metric_type in metric_map.items():
            unit_price = decimal_string(raw_pricing.get(source_metric))
            if unit_price is None:
                continue
            prices.append(
                {
                    "provider": "openrouter",
                    "model": model_id,
                    "metric_type": metric_type,
                    "unit_price": unit_price,
                    "currency": "USD",
                    "raw": {"source_metric": source_metric, "pricing": raw_pricing},
                }
            )

    return prices


def build_catalog(prices: List[Dict[str, Any]]) -> Dict[str, Any]:
    sorted_prices = sorted(
        prices,
        key=lambda item: (item["provider"], item["model"], item["metric_type"]),
    )
    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "format_version": "1.0",
        },
        "prices": sorted_prices,
    }


def write_if_changed(output_path: Path, catalog: Dict[str, Any]) -> bool:
    new_payload = json.dumps(catalog, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output_path.exists():
        try:
            current = json.loads(output_path.read_text(encoding="utf-8"))
            if current.get("prices") == catalog["prices"]:
                return False
        except json.JSONDecodeError:
            pass

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(new_payload, encoding="utf-8")
    return True


async def sync_pricing_catalog(output: str = DEFAULT_OUTPUT) -> bool:
    async with aiohttp.ClientSession() as session:
        fal_prices, openrouter_prices = await asyncio.gather(
            fetch_fal_prices(session),
            fetch_openrouter_prices(session),
        )

    catalog = build_catalog([*fal_prices, *openrouter_prices])
    return write_if_changed(Path(output), catalog)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync bundled AI pricing catalog.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    changed = asyncio.run(sync_pricing_catalog(args.output))
    print("pricing catalog updated" if changed else "pricing catalog unchanged")


if __name__ == "__main__":
    main()
