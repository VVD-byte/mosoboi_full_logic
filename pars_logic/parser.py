import asyncio
import random
import logging
import nest_asyncio
import aiohttp
import math

from bs4 import BeautifulSoup

from settings import SESSION
from tg_bot import loop

nest_asyncio.apply()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Parser:
    def __init__(self, url):
        self.start_url = [url]
        self.max_count_tovar_for_page = 124
        self.n = 0
        logger.info('Init Parser')

    async def main(self):
        logger.info(f'Start pars {self.start_url[-1]}')
        if self.start_url[0] == '/catalog/':
            self.start_url = await self.get_catalog()
            logger.info(f'Get all catalog {self.start_url}')
        # courutines = [self.get_tovar_for_brand(i) for i in self.start_url]
        dat = await self.get_tovar_for_brand(self.start_url[0])  # #########
        logger.info(f'Get all tovar for {self.start_url[0]} - {len(dat)} - {dat}')  # ########
        courutines = [self.get_data_for_tovar(i) for i in dat]
        result = loop.run_until_complete(asyncio.gather(*courutines))
        with open('test.json', 'w') as t:
            import json
            t.write(json.dumps(result, ensure_ascii=False))
        # dat = await self.get_data_for_tovar(dat[0])

    async def get_catalog(self) -> list:
        bs = await self.get_soup('http://www.mosoboi.ru/catalog/')
        return ['http://www.mosoboi.ru' + i.find('a').get('href') + f'?list_by={self.max_count_tovar_for_page}'
                for i in bs.find('div', {'class': 'catalog_spis'}).find('ul').find_all('li')]

    async def get_tovar_for_brand(self, url: str) -> list:
        bs = await self.get_soup(url)
        start = await self.get_tovar_for_page_brand(bs)
        for i in range(2, await self.check_tovar_count(bs) + 1):
            start += await self.get_tovar_for_page_brand(await self.get_soup(url + f'&PAGEN_2={i}'))
        return start

    async def get_data_for_tovar(self, url: str):
        try:
            bs = await self.get_soup(url)
            dat = {
                'Наименование': await self.clear_text(bs.find('h1', {'id': 'h1-pages'}).getText()),
                'Изображение': 'https://www.mosoboi.ru'
                               + bs.find('div', {'class': 'detail-element-img'}).find('img').get('src'),
            }
            for i in bs.find('div', {'class': 'properties tab-info js-tab-info active'}).find_all('div', {'class': 'row-item'}):
                name_row = await self.clear_text(i.find("div", {"class": "tab-content-left"}).getText())
                value_row = await self.clear_soup(i.find("span"))
                dat[name_row] = await self.clear_text(value_row.getText())
            self.n += 1
            logger.info(f'{self.n} - {dat}')
            return dat
        except Exception as e:
            logger.error(f'{url} - {e}')

    async def check_exists_file(self):
        pass

    async def check_tovar_count(self, bs: BeautifulSoup) -> int:
        return math.ceil(
            int(bs.find('div', {'class': 'count_products'}).getText().split(' ')[0])/self.max_count_tovar_for_page
        )

    @staticmethod
    async def get_tovar_for_page_brand(bs: BeautifulSoup) -> list:
        return ['http://www.mosoboi.ru' + i.find('div', {'class': 'product-item__hover'}).find('a').get('href')
                for i in bs.find_all('div', {'class': 'col-xs-3'})]

    @staticmethod
    async def clear_text(text: str) -> str:
        return text.replace('\n', '').replace('\t', '').replace('\r', '').replace('  ', '')

    @staticmethod
    async def clear_soup(bs: BeautifulSoup) -> BeautifulSoup:
        for i in bs.select('div'):
            i.extract()
        return bs

    async def get_soup(self, url) -> BeautifulSoup:
        # async with aiohttp.ClientSession() as session:
        async with random.choice(SESSION).get(url) as resp:  # random.choice(SESSION)
            page = await resp.text()
            if resp.status == 200:
                return BeautifulSoup(page, 'lxml')
            else:
                return await self.get_soup(url)
