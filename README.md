# 📊 OpenRouter Insights

[![PyPI version](https://img.shields.io/pypi/v/openrouter-insights.svg)](https://pypi.org/project/openrouter-insights/)
[![Python versions](https://img.shields.io/pypi/pyversions/openrouter-insights.svg)](https://pypi.org/project/openrouter-insights/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/luisfarfan/openrouter-insights/actions/workflows/tests.yml/badge.svg)](https://github.com/luisfarfan/openrouter-insights/actions/workflows/tests.yml)

**OpenRouter Insights** is a professional, production-ready Python library that provides a unified, high-fidelity index of Large Language Models. 

---

## 🚀 Quick Start

### Installation

```bash
pip install openrouter-insights
```

### Usage

```python
from openrouter_insights import LLMIndexSync

# Initialize (Uses local registry by default)
index = LLMIndexSync()

# 1. Find the best model for a specific task
best_coder = index.get_best_models(tag="coding", limit=1)[0]
print(f"Recommended for code: {best_coder.name} (${best_coder.pricing.input}/1M tokens)")

# 2. Advanced Filtering
frontier_models = index.filter_models(
    tier="frontier",
    min_intelligence=80,
    modalities=["image"]
)
```

## 🛠️ Data Freshness (Git-Ops)

This library uses a **Git-Ops automation workflow**. Every 24 hours, a GitHub Action:
1. Fetches the latest data from **OpenRouter** and **ArtificialAnalysis**.
2. Performs fuzzy matching and data unification.
3. Updates the local SQLite and JSON registries.
4. **Idempotent Sync**: Only commits changes if the model intelligence or pricing has actually evolved.

---

## 📈 Key Advantages

| Feature | OpenRouter Insights | Standard API List |
| :--- | :--- | :--- |
| **Intelligence Scores** | ✅ Included (from ArtificialAnalysis) | ❌ Missing |
| **Performance Tiers** | ✅ Categorized (Frontier/Pro/Lite) | ❌ Raw list |
| **Efficiency Metrics** | ✅ Bang-for-buck calculation | ❌ Manual calc |
| **Fuzzy Discovery** | ✅ Advanced Search & Ranking | ❌ Exact match only |

---

## 🧪 Testing & Reliability

The library is backed by a comprehensive test suite (Unit, Integration, and Facade tests) to ensure data integrity and interface stability.

```bash
# Run tests
pytest
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Luis Eduardo Farfan Melgar** - [lucho.farfan9@gmail.com](mailto:lucho.farfan9@gmail.com)  
Project Link: [https://github.com/luisfarfan/openrouter-insights](https://github.com/luisfarfan/openrouter-insights)
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
