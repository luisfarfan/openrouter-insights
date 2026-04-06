# 01 - LLMIndex: Architecture

## High-Level Architecture (Pure Backend)
**LLMIndex** is built as a **Multi-Stage Data Pipeline** using **FastAPI (Python)** for its logic and **SQLite/JSON** for data delivery.

### 1. Data Processing Pipeline (Stages)
The core logic resides in a set of **Services** and **Pipelines** that execute in sequence:

1.  **Fetchers**: 
    - `OpenRouterFetcher`: Retrieves the latest model catalog via HTTP.
    - `ArtificialAnalysisFetcher`: Retrieves the latest benchmarking dataset.
2.  **Normalizers**: Standardizes the naming conventions and modalities from both sources.
3.  **Matching Engine**: A fuzzy and deterministic engine that identifies that `openai/gpt-4.5-preview` (OpenRouter) is the same as `gpt45-preview` (ArtificialAnalysis).
4.  **Classification Engine**: Calculates derived fields (`efficiency_score`, `best_for`, `performance_tier`).
5.  **Exporters**:
    - `SQLiteExporter`: Stores the unified data into a single-file `openrouter_insights.sqlite` for local queries.
    - `JSONExporter`: Generates a static `openrouter_insights.json` for global consumption and Git versioning.

### 2. Tech Stack
- **Language**: Python 3.11+.
- **Engine**: FastAPI (API layer + Dependency Injection).
- **Persistence**: 
    - **Primary**: `SQLite` (one file).
    - **Distribution**: `JSON` (version-controlled).
- **Automation**: GitHub Actions (to trigger the periodic "Sync" command).

### 3. Automated Sync (GitHub Actions & Git-Ops)
The project uses **GitHub Actions** to maintain a "Living Registry" without manual intervention:

1.  **Schedule**: A cron job defined in `.github/workflows/sync.yml` triggers once every 24 hours (or as configured).
2.  **Environment**: GitHub spins up an Ubuntu runner, installs Python dependencies, and injects **API Keys** via **GitHub Secrets**.
3.  **Command**: The action runs `python main.py sync`, which pulls from OpenRouter and ArtificialAnalysis.
4.  **Auto-Commit**: If the script modifies `data/openrouter_insights.json` or `data/openrouter_insights.sqlite`, the action automatically commits and pushes the changes back to the `main` branch.
5.  **Distribution**: The updated data is immediately served via "GitHub Raw" URLs, making it a globally available, zero-cost API.

### 4. API Keys & Security
- **Production**: Keys are stored as **GitHub Secrets** (`OPENROUTER_API_KEY`, etc.).
- **Local**: Developers use an `.env` file (ignored by Git) for local testing.

### 4. Error Handling & Fallbacks
- **API Failure**: If one data source is down, the system uses the last cached/committed version and alerts in the logs.
- **Matching Miss**: Models that cannot be matched are stored in a "Pending Review" log and excluded from calculations until added to the `fallback_mapping.json`.

## Performance Considerations
- **No Heavy Loads**: Since the data is small (hundreds of models), all indexing and classification are done in-memory before exporting.
- **FastAPI Metadata**: The API layer uses Pydantic to serve requests from the local SQLite/JSON with negligible latency.
