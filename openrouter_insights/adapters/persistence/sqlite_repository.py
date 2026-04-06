import json
from typing import List, Optional
from sqlalchemy import desc, asc
from sqlmodel import SQLModel, Field, Session, create_engine
from rapidfuzz import process, fuzz
from openrouter_insights.domain.entities import LLMModel, Pricing, Benchmarks
from openrouter_insights.domain.interfaces import IModelRepository
from openrouter_insights.infrastructure.config import get_settings

class LLMModelORM(SQLModel, table=True):
    """SQLModel representation for SQLite persistence."""
    __tablename__ = "models"

    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    provider: str = Field(index=True)
    context_length: int = Field(default=0)
    pricing_input: float = Field(default=0.0)
    pricing_output: float = Field(default=0.0)
    modalities: str = Field(default="[]") # JSON string
    
    # Benchmarks (flattened for easy filtering)
    intelligence_score: Optional[float] = Field(default=None, index=True)
    speed_score: Optional[float] = Field(default=None)
    reasoning_score: Optional[float] = Field(default=None)
    coding_score: Optional[float] = Field(default=None)
    elo_score: Optional[float] = Field(default=None, index=True) # Multimodal ELO
    
    is_virtual: bool = Field(default=False, index=True)
    
    # Pre-calculated tags for faster API queries
    best_for: str = Field(default="[]") # JSON string of tags

class SQLiteModelRepository(IModelRepository):
    """Synchronous implementation of IModelRepository using SQLModel and SQLite."""

    def __init__(self, database_url: str = None):
        if not database_url:
            settings = get_settings()
            database_url = settings.DATABASE_URL
        
        if "://" not in database_url:
            database_url = f"sqlite:///{database_url}"
        
        self.engine = create_engine(database_url)
        SQLModel.metadata.create_all(self.engine)

    def _to_orm(self, m: LLMModel) -> LLMModelORM:
        return LLMModelORM(
            id=m.id,
            name=m.name,
            provider=m.provider,
            context_length=m.context_length,
            pricing_input=m.pricing.input,
            pricing_output=m.pricing.output,
            modalities=json.dumps(m.modalities),
            intelligence_score=m.benchmarks.intelligence_score if m.benchmarks else None,
            speed_score=m.benchmarks.speed_score if m.benchmarks else None,
            reasoning_score=m.benchmarks.reasoning_score if m.benchmarks else None,
            coding_score=m.benchmarks.coding_score if m.benchmarks else None,
            elo_score=m.benchmarks.elo_score if m.benchmarks else None,
            is_virtual=m.is_virtual,
            best_for=json.dumps(m.best_for)
        )

    def save(self, model: LLMModel) -> None:
        with Session(self.engine) as session:
            session.merge(self._to_orm(model))
            session.commit()

    def save_batch(self, models: List[LLMModel]) -> None:
        with Session(self.engine) as session:
            for m in models:
                session.merge(self._to_orm(m))
            session.commit()

    def get_all(
        self, 
        provider: Optional[str] = None,
        best_for: Optional[str] = None,
        is_free: bool = False,
        min_intelligence: Optional[float] = None,
        filter_virtual: bool = True,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> List[LLMModel]:
        with Session(self.engine) as session:
            query = session.query(LLMModelORM)
            query = self._apply_filters(query, provider, best_for, is_free, min_intelligence, filter_virtual)

            direction = desc if sort_order == "desc" else asc
            if sort_by == "price":
                query = query.order_by(direction(LLMModelORM.pricing_input + LLMModelORM.pricing_output))
            elif sort_by == "intelligence":
                query = query.order_by(direction(LLMModelORM.intelligence_score))
            elif sort_by == "speed":
                query = query.order_by(direction(LLMModelORM.speed_score))
            elif sort_by == "elo":
                query = query.order_by(direction(LLMModelORM.elo_score))

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            return [self._to_entity(r) for r in query.all()]

    def get_count(
        self,
        provider: Optional[str] = None,
        best_for: Optional[str] = None,
        is_free: bool = False,
        min_intelligence: Optional[float] = None,
        filter_virtual: bool = True
    ) -> int:
        with Session(self.engine) as session:
            query = session.query(LLMModelORM)
            query = self._apply_filters(query, provider, best_for, is_free, min_intelligence, filter_virtual)
            return query.count()

    def get_by_id(self, model_id: str) -> Optional[LLMModel]:
        with Session(self.engine) as session:
            orm = session.get(LLMModelORM, model_id)
            return self._to_entity(orm) if orm else None

    def get_best_alternative(self, model_id: str, max_price: Optional[float] = None) -> Optional[LLMModel]:
        source = self.get_by_id(model_id)
        if not source:
            return None
        
        with Session(self.engine) as session:
            query = session.query(LLMModelORM).filter(LLMModelORM.id != model_id)
            query = query.filter(~LLMModelORM.is_virtual)
            
            # Try same tier (highly recommended)
            tier = source.performance_tier
            query = query.filter(LLMModelORM.best_for.like(f'%"{tier}"%'))
            
            if max_price is not None:
                query = query.filter((LLMModelORM.pricing_input + LLMModelORM.pricing_output) <= max_price)
            
            # Sort by intelligence
            query = query.order_by(desc(LLMModelORM.intelligence_score))
            
            best = query.first()
            return self._to_entity(best) if best else None

    def search(self, query: str, limit: int = 10) -> List[LLMModel]:
        """Hybrid search: SQL filter + Fuzzy ranking."""
        with Session(self.engine) as session:
            # Fetch candidates using SQL LIKE for efficiency
            candidates = session.query(LLMModelORM).filter(
                (LLMModelORM.name.like(f"%{query}%")) | 
                (LLMModelORM.provider.like(f"%{query}%")) |
                (LLMModelORM.id.like(f"%{query}%"))
            ).limit(100).all()
            
            if not candidates:
                return []

            models = [self._to_entity(c) for c in candidates]
            model_names = [f"{m.provider} {m.name} {m.id}" for m in models]
            results = process.extract(query, model_names, scorer=fuzz.WRatio, limit=limit)
            return [models[res[2]] for res in results]

    def _apply_filters(self, query, provider, best_for, is_free, min_intelligence, filter_virtual):
        if provider:
            query = query.filter(LLMModelORM.provider == provider)
        if is_free:
            query = query.filter(LLMModelORM.pricing_input == 0)
        if min_intelligence:
            query = query.filter(LLMModelORM.intelligence_score >= min_intelligence)
        if best_for:
            query = query.filter(LLMModelORM.best_for.like(f'%"{best_for}"%'))
        if filter_virtual:
            query = query.filter(~LLMModelORM.is_virtual)
            query = query.filter(LLMModelORM.pricing_input >= 0)
        return query

    def _to_entity(self, orm: LLMModelORM) -> LLMModel:
        benchmarks = Benchmarks(
            intelligence_score=orm.intelligence_score,
            speed_score=orm.speed_score,
            reasoning_score=orm.reasoning_score,
            coding_score=orm.coding_score,
            elo_score=orm.elo_score
        )
        return LLMModel(
            id=orm.id,
            name=orm.name,
            provider=orm.provider,
            context_length=orm.context_length,
            pricing=Pricing(input=orm.pricing_input, output=orm.pricing_output),
            modalities=json.loads(orm.modalities),
            benchmarks=benchmarks
        )
