# LLMIndex

A unified, open-source LLM registry merging **OpenRouter** (catalog) and **ArtificialAnalysis** (benchmarks).

## Vision
LLMIndex provides a "Single Source of Truth" for LLM metadata and performance tiers. It uses a **Git-Ops** approach, where the data is updated daily via GitHub Actions and stored in portable **JSON** and **SQLite** formats.

## Key Features
- **Library-First**: Consume as a Python dependency in your own projects.
- **Dual Persistence**: Choose between **SQLite** (for sync/write) and **JSON** (for read-only low-infra apps).
- **Normalized Registry**: Standardized model IDs across providers.
- **Computed Metrics**: Intelligence/Cost efficiency scores and performance tiers.
- **Ready for Agents**: Designed with "AI-Friendly" documentation.

## Installation

```bash
# Basic installation (Library only)
pip install openrouter_insights

# With API support (FastAPI + Uvicorn)
pip install "openrouter_insights[api]"
```

## Library Usage

The `LLMIndex` class is the main entry point for consuming the registry.

### Consume from JSON (No database required)
If you just want to query the pre-generated registry file:

```python
import asyncio
from openrouter_insights import LLMIndex

async def main():
    # 'openrouter_insights.json' should be in your project root or provide the full path
    client = LLMIndex(mode="json", path="openrouter_insights.json")
    
    models = await client.get_models(best_for="coding", sort_by="price")
    for m in models:
        print(f"{m.name}: ${m.pricing.input}/1M tokens")

asyncio.run(main())
```

### Consume from SQLite
Use SQLite if you need to run synchronization or prefer a database-backed store:

```python
from openrouter_insights import LLMIndex

client = LLMIndex(mode="sqlite", path="data/openrouter_insights.sqlite")

# Get counts
total = await client.get_count(provider="OpenAI")

# Sync registry (Requires OPENROUTER_API_KEY in ENV)
await client.sync()
```

## Running the API Server

If you installed with `[api]`, you can run the unified registry server:

```bash
openrouter_insights  # or uvicorn openrouter_insights.adapters.api.main:app --reload
```

## Documentation
See the [docs/](docs/) folder for detailed specifications:
- [Architecture](docs/01-architecture.md)
- [Data Schema](docs/02-data-schema.md)
- [Matching Engine](docs/03-matching-engine.md)
- [Classification Logic](docs/05-classification-logic.md)

---
*Open Source for the AI Community.*
