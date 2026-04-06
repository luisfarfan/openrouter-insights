import asyncio
import os
from openrouter_insights import LLMIndex, LLMIndexSync

def test_sync_mode():
    print("\n--- Testing Sync Mode (No await) ---")
    client = LLMIndexSync(mode="json", path="openrouter_insights.json")
    
    # Smart Methods
    smartest = client.get_smartest(limit=3)
    print(f"Top 3 Smartest: {[m.name for m in smartest]}")
    
    cheapest = client.get_cheapest(best_for="coding", limit=3)
    print(f"Top 3 Cheapest for Coding: {[m.name for m in cheapest]}")
    
    fastest = client.get_fastest(limit=1)
    print(f"Fastest Model: {fastest[0].name if fastest else 'None'}")
    
    frontier = client.get_top_frontier(limit=2)
    print(f"Frontier Models: {[m.name for m in frontier]}")

    results = client.search("gpt-4o", limit=1)
    print(f"Search 'gpt-4o': {results[0].id if results else 'None'}")

async def test_async_mode():
    print("\n--- Testing Async Mode (With await) ---")
    client = LLMIndex(mode="json", path="openrouter_insights.json")
    
    # Smart Methods
    smartest = await client.get_smartest(limit=3)
    print(f"Top 3 Smartest (Async): {[m.name for m in smartest]}")
    
    results = await client.search("claude 3.5", limit=1)
    print(f"Search 'claude 3.5': {results[0].id if results else 'None'}")

async def main():
    test_sync_mode()
    await test_async_mode()

if __name__ == "__main__":
    if os.path.exists("openrouter_insights.json"):
        asyncio.run(main())
    else:
        print("openrouter_insights.json not found. Run a sync first or provide the file.")
