import asyncio
import logging
import aiohttp

from aiohttp_proxy import ProxyConnector
from typing import Generator
from settings import SESSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def connect() -> Generator:
    #connect_ = ProxyConnector.from_url(f'http://{PROXY_LIST.pop()}')
    async with aiohttp.ClientSession() as session:
        yield session
