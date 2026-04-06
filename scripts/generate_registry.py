import asyncio
import json
import logging
from pathlib import Path
from openrouter_insights.domain.interfaces import IFetcherGateway
from openrouter_insights.domain.services.matching_engine import MatchingEngine
from openrouter_insights.adapters.persistence.sqlite_repository import SQLiteModelRepository
from openrouter_insights.adapters.persistence.json_exporter import JSONExporter
from openrouter_insights.use_cases.sync_registry import SyncRegistryUseCase

# Dependency Mock for the demo
class LocalFileGateway(IFetcherGateway):
    """Fetcher that reads from local raw JSON files for union demonstration."""
    async def fetch_catalog(self):
        with open("data/raw/raw_openrouter.json", "r") as f:
            return json.load(f)
            
    async def fetch_benchmarks(self):
        with open("data/raw/raw_benchmarks.json", "r") as f:
            return json.load(f)

async def main():
    """Script to demonstrate the UNION of OpenRouter and ArtificialAnalysis."""
    logging.basicConfig(level=logging.INFO)
    
    # Initialization
    # (Note: We use a Mock Session for SQLite for this demo, or just null it 
    # since we care about the JSON export union)
    class MockRepo:
        async def save_batch(self, models): pass
        
    engine = MatchingEngine()
    exporter = JSONExporter("openrouter_insights.json") # The SINGLE UNIFIED FILE in root
    gateway = LocalFileGateway()
    
    use_case = SyncRegistryUseCase(
        repository=MockRepo(), # type: ignore
        gateways=[gateway],
        matching_engine=engine,
        exporter=exporter
    )
    
    print("--- Running Unified Registry Generation ---")
    models = await use_case.execute()
    print(f"Created {len(models)} unified models.")
    print("Check 'openrouter_insights.json' in the root directory.")

if __name__ == "__main__":
    asyncio.run(main())
