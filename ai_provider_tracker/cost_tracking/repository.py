import json
import sqlite3
from pathlib import Path

from ai_provider_tracker.cost_tracking.models import GenerationUsageEvent


class SQLiteUsageRepository:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = Path(sqlite_path)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_generation_usage (
                    id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    request_type TEXT NOT NULL,
                    normalized_usage TEXT NOT NULL,
                    total_cost TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    cost_source TEXT NOT NULL,
                    cost_confidence TEXT NOT NULL,
                    cost_breakdown TEXT NOT NULL,
                    raw_request TEXT NOT NULL,
                    raw_response TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save(self, event: GenerationUsageEvent) -> None:
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO ai_generation_usage (
                    id, provider, model, request_type, normalized_usage, total_cost,
                    currency, cost_source, cost_confidence, cost_breakdown,
                    raw_request, raw_response, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.provider,
                    event.model,
                    event.request_type,
                    event.normalized_usage.model_dump_json(),
                    str(event.cost.total),
                    event.cost.currency,
                    event.cost.source,
                    event.cost.confidence,
                    event.cost.model_dump_json(),
                    json.dumps(event.raw_request, default=str),
                    json.dumps(event.raw_response, default=str),
                    json.dumps(event.metadata, default=str),
                    event.created_at.isoformat(),
                ),
            )
            conn.commit()
