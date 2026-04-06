# 04 - LLMIndex: API Service

## API Strategy
The **LLMIndex API** is a high-performance, lightweight **FastAPI** wrapper that serves as the query layer for the unified registry.

### Endpoints Specification

#### 1. `GET /models`
Retrieves the full registry or a filtered subset.
- **Query Params**:
  - `provider`: (e.g., `openai`) Filter by company.
  - `modality`: (e.g., `image`) Filter by types supported.
  - `max_price`: (float) Max input/output pricing.
  - `min_intelligence`: (int 0-100) Min score required.
  - `sort`: (e.g., `pricing`, `intelligence_score`, `speed_score`).
  - `order`: (`asc`, `desc`).

#### 2. `GET /models/{id}`
Returns the full JSON detail for a single model ID.

#### 3. `GET /models/best`
Shortcut for top performers in key categories.
- **Query Params**:
  - `for`: (`coding`, `reasoning`, `rag`, `chat`).
  - `limit`: (default: 5) Number of results.

#### 4. `GET /stats`
Aggregated statistics for the registry (average price per provider, context length distribution).

### Consumption Patterns

- **Direct JSON**: For frontend/client-side apps, they can skip the API and `fetch` the `openrouter_insights.json` directly from the repo.
- **REST API**: For server-to-server integrations requiring dynamic filtering and sorting at the engine level.
- **Local SQLite**: For power users or local scripts that want to run complex SQL queries from the derived database.

### API Documentation
The API includes an interactive **Swagger UI** (available at `/docs`) and a **ReDoc** documentation page (at `/redoc`) generated automatically from the Pydantic models.

## Deployment & Hosting
- **Backend**: Containerized with **Docker** for easy deployment as a standalone service.
- **Serverless**: Fully compatible with **Vercel** or **AWS Lambda** (FastAPI with Mangum) for low-cost, on-demand hosting.
- **Static Assets**: The `openrouter_insights.json` is synced to a public URL (GitHub Raw or Vercel Edge Cache) for lightning-fast delivery.
