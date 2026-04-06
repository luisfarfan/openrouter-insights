from typing import Optional, List
from sqlmodel import SQLModel, Field, JSON, Column
from datetime import datetime

class LLMModelORM(SQLModel, table=True):
    """
    Persistence Model for SQLite using SQLModel.
    Maps to the Domain Entity LLMModel.
    """
    __tablename__ = "llm_models"

    id: str = Field(primary_key=True)
    name: str
    provider: str
    context_length: int
    
    # Store nested fields as JSON columns in SQLite
    pricing: dict = Field(default_factory=dict, sa_column=Column(JSON))
    benchmarks: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    modalities: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    last_synced: datetime = Field(default_factory=datetime.utcnow)
