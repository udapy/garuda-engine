import asyncio
from network import NetworkManager
from loguru import logger

async def test():
    nm = NetworkManager()
    await nm.initialize()
    if nm.cookies:
        logger.success("✅ Handshake Successful! Cookies obtained.")
    else:
        logger.error("❌ Handshake Failed.")
    await nm.close()

if __name__ == "__main__":
    asyncio.run(test())
