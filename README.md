# 🚀 OpenRouter Insights

[![PyPI version](https://img.shields.io/pypi/v/openrouter-insights.svg)](https://pypi.org/project/openrouter-insights/)
[![Python versions](https://img.shields.io/pypi/pyversions/openrouter-insights.svg)](https://pypi.org/project/openrouter-insights/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-19%20passed-brightgreen.svg)](#-verified-reliability)

**OpenRouter Insights** is a professional, unified LLM registry that supercharges the official **OpenRouter** catalog with high-fidelity intelligence from **ArtificialAnalysis**. 

It provides a "Single Source of Truth" for model capabilities, pricing, and performance, designed for production-grade AI agents and high-performance applications.

---

## 🔥 OpenRouter with "Superpowers"

Why use this instead of the raw OpenRouter API?

| Feature | Raw OpenRouter API | **OpenRouter Insights** |
|---------|-------------------|-------------------------|
| **Model Catalog** | ✅ Yes | ✅ Yes (Auto-synced) |
| **Pricing** | ✅ Yes | ✅ Yes (Normalized) |
| **Intelligence Scores** | ❌ No | ✅ Yes (ArtificialAnalysis) |
| **Performance Tiers** | ❌ No | ✅ Yes (Frontier/Pro/Lite) |
| **Smart Discovery** | ❌ No | ✅ Yes (`get_smartest`, `get_cheapest`) |
| **Fuzzy Search** | ❌ Limited | ✅ Yes (RapidFuzz integrated) |
| **Sync/Async Facades** | ❌ No | ✅ Yes (Plug & Play) |

---

## 🛠️ Installation

```bash
# Basic installation (Library only)
pip install openrouter-insights

# With API support (FastAPI + Uvicorn)
pip install "openrouter-insights[api]"
```

---

## 💡 Quick Start

### ⚡ Async Facade (For FastAPI / High Performance)
Ideal for modern asynchronous applications.

```python
import asyncio
from openrouter_insights import LLMIndex

async def main():
    # Uses local JSON registry (no DB setup required)
    client = LLMIndex(mode="json")
    
    # Smart Discovery: Get the smartest model for coding
    models = await client.get_best_for_coding(limit=1)
    if models:
        print(f"Best model: {models[0].name} (Tier: {models[0].performance_tier})")
        
    # Full Fuzzy Search
    results = await client.search("gpt4-o reasoning")
    for r in results:
        print(f"Matched: {r.id}")

asyncio.run(main())
```

### 🕒 Sync Facade (For Scripts / Notebooks)
No `async/await` boilerplate. Pure simplicity.

```python
from openrouter_insights import LLMIndexSync

client = LLMIndexSync(mode="json")

# Get the absolute cheapest frontier model
cheap_pro = client.get_cheapest(tier="frontier", limit=3)
for m in cheap_pro:
    print(f"{m.name}: ${m.pricing.input}/1M tokens")
```

---

## 🕒 Data Freshness & Automation (Git-Ops)

OpenRouter Insights is not a static file. We run an **automated 24-hour synchronization job** via GitHub Actions (CRON) that:
1.  **Fetches** the latest models and pricing from OpenRouter.
2.  **Unifies** benchmark data from ArtificialAnalysis.
3.  **Processes** the results via our Matching Engine.
4.  **Commits** the fresh `openrouter_insights.sqlite` and `.json` back to the repository.

This ensures you always have access to the latest frontier models as they are released.

---

## 🧠 Smart Query Methods

OpenRouter Insights comes with pre-built logic to discover models based on real-world capabilities:

*   `.get_smartest()`: Highest intelligence scores first.
*   `.get_cheapest()`: Lowest cost-to-output first.
*   `.get_best_for_coding()`: Top-tier coding performers.
*   `.get_top_frontier()`: Only the best models in the world.
*   `.get_fastest()`: Highest Tokens Per Second (TPS).

---

## ✅ Verified Reliability

We take production stability seriously. Every release is validated against a comprehensive test suite:

*   **Unit Tests**: Logic for classification, tiers, and matching engine.
*   **Integration Tests**: Mocked gateway verification for OpenRouter and ArtificialAnalysis.
*   **Persistence Tests**: Integrity checks for both SQLite and JSON engines.
*   **Facade Tests**: Sync/Async interface consistency.

**Current Status**: 19 tests passed (100% success rate).

---

## 📖 Documentation
Detailed architectural and domain documentation can be found in the `docs/` folder:
- [Architecture & Design](docs/01-architecture.md)
- [Data Schema](docs/02-data-schema.md)
- [Matching & Unification Engine](docs/03-matching-engine.md)

---
*Developed with ❤️ for the AI Engineering community.*
