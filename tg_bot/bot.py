import datetime
import os
import logging
import zipfile

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from pars_logic.parser import Parser
from tg_bot import bot_, loop, dp, MAGASINE_DATA

greet_kb = ReplyKeyboardMarkup()
for i in MAGASINE_DATA:
    greet_kb.add(KeyboardButton(i))
greet_kb.add(KeyboardButton('ALL'))


@dp.message_handler(commands=['start'])
async def send_welcome(message):
    await bot_.send_message(message.from_user.id, "Выберите бренд для парсинга", reply_markup=greet_kb)


@dp.message_handler()
async def send_file(message):
    if message.text in MAGASINE_DATA:
        await bot_.send_message(message.from_user.id, "Начали парсить, подождите", reply_markup=greet_kb)
        async with open(await Parser(MAGASINE_DATA[message.text]).main(), 'rb') as t:
            await bot_.send_file(message.from_user.id, t, reply_markup=greet_kb)
    else:
        await bot_.send_message(message.from_user.id, "Неправильное имя бренда", reply_markup=greet_kb)
