import asyncio
import json
import logging
from typing import Generator

from aiogram.utils import executor
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiohttp import web

from pars_logic.signals import connect
from settings import TOKEN_BOT
from settings import PROXY_LIST, SESSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


async def nex(a):
    SESSION.append(await a.__anext__())
    return 1

for i in range(len(PROXY_LIST)):
    a = connect()
    loop.run_until_complete(nex(a))

bot_ = Bot(TOKEN_BOT)
dp = Dispatcher(bot_, loop=loop)

with open('dat.json', 'r') as t:
    MAGASINE_DATA = json.loads(t.read())

from tg_bot import bot

from pars_logic.parser import Parser
import asyncio
asyncio.run(Parser('/catalog/').main())

executor.start_polling(dp, skip_updates=True)
