import aiohttp
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BaseHTTPFetcher:
    """Async HTTP Client for external API requests."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Any]:
        """Perform an async GET request and return JSON response."""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"HTTP Error {response.status} for URL: {url}")
                        text = await response.text()
                        logger.debug(f"Response content: {text[:200]}")
                        return None
                    return await response.json()
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {str(e)}")
            return None
