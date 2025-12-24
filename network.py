# network.py
import asyncio
import httpx
from loguru import logger
from config import NSE_HOME, BASE_HEADERS

class NetworkManager:
    def __init__(self):
        self.client = None
        self.cookies = {}

    async def initialize(self):
        """Creates a persistent HTTP/2 session."""
        # HTTP/2 is often less blocked than HTTP/1.1 for scripts
        self.client = httpx.AsyncClient(http2=True, headers=BASE_HEADERS, follow_redirects=True, timeout=10.0)
        
        try:
            logger.info(f"Handshaking with {NSE_HOME} (HTTP/2)...")
            resp = await self.client.get(NSE_HOME)
            
            if resp.status_code == 200:
                self.cookies = resp.cookies
                logger.info("NSE Cookies obtained successfully.")
            else:
                logger.error(f"Failed to handshake NSE: {resp.status_code} - {resp.text[:100]}...")
        except Exception as e:
            logger.error(f"Network init error: {e}")

    async def fetch(self, url):
        """High-speed fetch."""
        if not self.client:
            await self.initialize()
            
        try:
            # Manually pass cookies if needed, though httpx client holds cookie jar
            # merging init cookies with client cookies
            resp = await self.client.get(url)
            
            if resp.status_code == 200:
                return resp.content # bytes
            elif resp.status_code in (401, 403):
                logger.warning("Session expired or blocked. Refreshing...")
                await self.initialize()
                return None
        except Exception as e:
            logger.error(f"Fetch error: {url} -> {e}")
            return None

    async def close(self):
        if self.client:
            await self.client.aclose()
