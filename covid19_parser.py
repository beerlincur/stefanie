import json # модуль для работы с json
import requests # модуль для получения страницы
from bs4 import BeautifulSoup as bs # модуль для парсинга страницы
from lxml import html # для парсинга html
import datetime
from covid.api import CovId19Data
from typing import Union

from config import HEADERS # заголовки браузера для корректной работы


async def get_world_corona_stats() -> str:
    """Returns corona virus world info"""
    world_corona_stats = await _world_corona_stats_parser()

    if world_corona_stats != None:
        return world_corona_stats

    return "При получении мировой статистики произошла ошибка :("


async def get_russia_corona_stats() -> str:
    """Returns corona virus russia info"""
    russia_corona_stats = await _russia_corona_stats_parser()

    if russia_corona_stats != None:
        return russia_corona_stats

    return "При получении статистики по России произошла ошибка :("


async def _world_corona_stats_parser() -> Union[str, None]:
    """Returns corona virus world info or None"""
    try:
        api = CovId19Data(force=False)

        latest = api.get_stats()

        result = "🌎 Мир 🌎\n🤖Зараженных в мире: " + str(latest['confirmed']) + "\n☠️Смертей в мире: " + str(latest['deaths']) + "\n🍀Выздоровевших в мире: " + str(latest['recovered'])

        return result
    except:
        return None

    
async def _russia_corona_stats_parser() -> Union[str, None]:
    """Returns corona virus russia info or None"""
    try:
        api = CovId19Data(force=False)
        
        russia = api.filter_by_country("russia") # {'confirmed': 1534, 'label': 'Russia', 'last_updated': '2020-03-29 00:00:00', 'lat': '60.0', 'long': '90.0', 'recovered': 64, 'deaths': 8}
        
        result = "🇷🇺 Россия 🇷🇺\n🤖Заражений за все время: " + str(russia['confirmed']) + "\n☠️Смертей за все время: " + str(russia['deaths']) + "\n🍀Выздоровлений: " + str(russia['recovered'])
        
        return result
    except:
        return None
