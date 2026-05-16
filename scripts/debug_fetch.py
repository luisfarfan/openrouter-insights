import asyncio
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from ai_provider_tracker.adapters.gateways.openrouter_fetcher import OpenRouterFetcher
from ai_provider_tracker.adapters.gateways.artificial_analysis_fetcher import ArtificialAnalysisFetcher

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Debug script to fetch raw data and save it for analysis."""
    # Load .env (Poetry might handle this, but let's be explicit)
    load_dotenv()
    
    # Create data directory if not exists
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize Fetchers
    or_fetcher = OpenRouterFetcher()
    aa_fetcher = ArtificialAnalysisFetcher()
    
    logger.info("--- Starting Debug Fetch ---")
    
    # 1. OpenRouter Catalog
    logger.info("Fetching OpenRouter catalog...")
    try:
        or_data = await or_fetcher.fetch_catalog()
        if or_data:
            path = output_dir / "raw_openrouter.json"
            with open(path, "w") as f:
                json.dump(or_data, f, indent=2)
            logger.info(f"Saved {len(or_data)} models from OpenRouter to {path}")
        else:
            logger.warning("No data retrieved from OpenRouter. Check your API key.")
    except Exception as e:
        logger.error(f"Error fetching OpenRouter: {str(e)}")

    # 2. ArtificialAnalysis Benchmarks
    # (Note: This will likely fail or be empty if the key is not in .env)
    logger.info("Fetching ArtificialAnalysis benchmarks...")
    try:
        aa_data = await aa_fetcher.fetch_benchmarks()
        if aa_data:
            path = output_dir / "raw_benchmarks.json"
            with open(path, "w") as f:
                json.dump(aa_data, f, indent=2)
            logger.info(f"Saved {len(aa_data)} benchmark items to {path}")
        else:
            logger.warning("No data retrieved from ArtificialAnalysis. Check your API key.")
    except Exception as e:
        logger.error(f"Error fetching ArtificialAnalysis: {str(e)}")

    logger.info("--- Debug Fetch Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
