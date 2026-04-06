# 📊 OpenRouter Insights

[![PyPI version](https://img.shields.io/pypi/v/openrouter-insights.svg)](https://pypi.org/project/openrouter-insights/)
[![Python versions](https://img.shields.io/pypi/pyversions/openrouter-insights.svg)](https://pypi.org/project/openrouter-insights/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/luisfarfan/openrouter-insights/actions/workflows/tests.yml/badge.svg)](https://github.com/luisfarfan/openrouter-insights/actions/workflows/tests.yml)

**OpenRouter Insights** is a professional, unified LLM registry that supercharges the official **OpenRouter** catalog with high-fidelity intelligence and benchmarks.

It provides a "Single Source of Truth" for model capabilities, pricing, and performance, designed for production-grade AI agents and high-performance applications.

---

## 📖 Table of Contents
- [🔥 OpenRouter with Superpowers](#-openrouter-with-superpowers)
- [🛠️ Installation](#️-installation)
- [💡 Quick Start](#-quick-start)
- [🧠 Data Intelligence (Providers)](#-data-intelligence-providers)
- [🕒 Data Freshness & Automation](#-data-freshness--automation-git-ops)
- [✨ Smart Query Methods](#-smart-query-methods)
- [🧪 Verified Reliability](#-verified-reliability)
- [🔮 Future Roadmap](#-future-roadmap)
- [🤝 Contributing](#-contributing)

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

```python
from openrouter_insights import LLMIndexSync

client = LLMIndexSync(mode="json")

# Get the absolute cheapest frontier model
cheap_pro = client.get_cheapest(tier="frontier", limit=3)
for m in cheap_pro:
    print(f"{m.name}: ${m.pricing.input}/1M tokens")
```

---

## 🧠 Data Intelligence (Providers)

OpenRouter Insights aggregates data from world-class sources to provide high-fidelity metrics:

*   **[ArtificialAnalysis.ai](https://artificialanalysis.ai/)**: Our primary source for model performance. We integrate their independent benchmarks for **Intelligence, Quality (V2 ELO), and Speed (TPS)** to power our ranking logic.
*   **[OpenRouter.ai](https://openrouter.ai/)**: Our core model catalog. We sync directly with their API to provide real-time pricing and availability for hundreds of models.

---

## 🕒 Data Freshness & Automation (Git-Ops)

OpenRouter Insights is not a static file. We run an **automated 24-hour synchronization job** via GitHub Actions (CRON) that:
1.  **Fetches** the latest models and pricing from OpenRouter.
2.  **Unifies** benchmark data from ArtificialAnalysis.
3.  **Processes** the results via our Matching Engine.
4.  **Commits** the fresh `openrouter_insights.sqlite` and `.json` back to the repository.

*This ensures you always have access to the latest frontier models as they are released.*

---

## ✨ Smart Query Methods

OpenRouter Insights comes with pre-built logic to discover models based on real-world capabilities:

*   `.get_smartest()`: Highest intelligence scores first.
*   `.get_cheapest()`: Lowest cost-to-output first.
*   `.get_best_for_coding()`: Top-tier coding performers.
*   `.get_top_frontier()`: Only the best models in the world.
*   `.get_fastest()`: Highest Tokens Per Second (TPS).

---

## 🧪 Verified Reliability

We take production stability seriously. Every release is validated against a comprehensive test suite (Unit, Integration, Persistence, and Facade tests).

**Current Status**: 19 tests passed (100% success rate).

---

## 🔮 Future Roadmap

We are committed to making this the most comprehensive LLM index in the industry. Future data sources planned for integration include:
- **Hugging Face**: Open LLM Leaderboard scores.
- **Vercel AI**: Comprehensive provider metrics.
- **LMSYS Chatbot Arena**: Live ELO ratings.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---
**Luis Eduardo Farfan Melgar** - [lucho.farfan9@gmail.com](mailto:lucho.farfan9@gmail.com)  
Project Link: [https://github.com/luisfarfan/openrouter-insights](https://github.com/luisfarfan/openrouter-insights)
