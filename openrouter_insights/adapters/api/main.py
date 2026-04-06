from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from openrouter_insights import LLMIndex, LLMModel


# Enum Definitions for better Swagger UI
class Provider(str, Enum):
    OPENAI = "OpenAI"
    ANTHROPIC = "Anthropic"
    GOOGLE = "Google"
    META = "Meta"
    MISTRAL = "Mistral"
    XAI = "xAI"
    DEEPSEEK = "DeepSeek"
    MICROSOFT = "Microsoft"
    COHERE = "Cohere"

class BestFor(str, Enum):
    CODING = "coding"
    REASONING = "reasoning"
    REAL_TIME = "real-time"
    MULTIMODAL_HIGH_FIDELITY = "multimodal-high-fidelity"
    MULTIMODAL = "multimodal"
    RAG = "rag"

class SortBy(str, Enum):
    PRICE = "price"
    INTELLIGENCE = "intelligence"
    SPEED = "speed"
    ELO = "elo"

class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PaginatedModelsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[LLMModel]

app = FastAPI(
    title="LLMIndex API",
    description="The Unified Open-Source LLM Registry API.",
    version="0.1.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency Injection Setup
def get_index():
    return LLMIndex(mode="sqlite")

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "LLMIndex API is live."}

@app.get("/api/v1/models", response_model=PaginatedModelsResponse, tags=["Models"])
async def get_models(
    provider: Provider = Query(None, description="Filter by provider (e.g., OpenAI, Anthropic)"),
    best_for: BestFor = Query(None, description="Filter by strength (coding, rag, real-time, multimodal)"),
    is_free: bool = Query(False, description="Show only free models"),
    min_intelligence: float = Query(None, description="Minimum benchmark score"),
    sort_by: SortBy = Query(None, description="Sort order (price, intelligence, speed)"),
    order: Order = Query(Order.DESC, description="Sorting direction (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    index: LLMIndex = Depends(get_index)
):
    """
    Query the unified LLM registry with high-fidelity filters.
    """
    p_val = provider.value if provider else None
    b_val = best_for.value if best_for else None
    s_val = sort_by.value if sort_by else None
    o_val = order.value

    total = await index.get_count(
        provider=p_val,
        best_for=b_val,
        is_free=is_free,
        min_intelligence=min_intelligence
    )

    models = await index.get_models(
        provider=p_val,
        best_for=b_val,
        is_free=is_free,
        min_intelligence=min_intelligence,
        sort_by=s_val,
        sort_order=o_val,
        page=page,
        page_size=page_size
    )

    return PaginatedModelsResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=models
    )


@app.get("/api/v1/models/{model_id:path}", response_model=LLMModel, tags=["Models"])
async def get_model_detail(
    model_id: str,
    index: LLMIndex = Depends(get_index)
):
    """Get a detailed view of a specific model in the registry."""
    model = await index.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found in registry.")
    return model

@app.get("/api/v1/search", response_model=List[LLMModel], tags=["Models"])
async def search_models(
    q: str = Query(..., min_length=2, description="Search term for model name or provider"),
    limit: int = Query(10, ge=1, le=50),
    index: LLMIndex = Depends(get_index)
):
    """Fuzzy search models by name or provider."""
    return await index.search(q, limit=limit)

@app.post("/api/v1/sync", tags=["Admin"])
async def trigger_sync(index: LLMIndex = Depends(get_index)):
    """
    Trigger a manual synchronization of the registry.
    """
    models = await index.sync()
    return {"status": "success", "synced_models": len(models)}


def run_server():
    import uvicorn
    uvicorn.run("openrouter_insights.adapters.api.main:app", host="0.0.0.0", port=8000, reload=True)
