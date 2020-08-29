#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wikipediaapi
from urllib.parse import unquote
from typing import Union

from config import PEOPLE


WIKI_WIKI = wikipediaapi.Wikipedia('ru')


async def search_in_wiki(query: str) -> str:
    """Returns wiki info for given query"""
    result = await _get_wiki_results(query)
    if result != None:
        return result
    else:
        return PEOPLE['nothing_in_wiki']


async def _get_wiki_results(query: str) -> Union[str, None]:   
    """Returns wiki info for given query or None"""     
    try:
        is_exist = await _is_page_exist(query)
        if is_exist:
            page_url = await _get_page_url(query)
            page_summary = await _get_page_summary(query)
            result = f'🔮Друг, я спросила {query}, выдаю результаты:🔮\n'
            result = result + '📜' + page_summary + '📜' + '\n'
            result = result + '🔎' + unquote(page_url)
            return result
        else:
            return None
    except:
        return None


async def _get_page(page_name: str) -> str:
    """Returns wiki page"""
    return WIKI_WIKI.page(page_name)


async def _is_page_exist(page_name: str) -> bool:
    """Returns if wiki page exists"""
    page = await _get_page(page_name)
    return page.exists()


async def _get_page_summary(page_name: str) -> str:
    """Returns wiki page summary"""
    page = await _get_page(page_name)
    return WIKI_WIKI.extracts(page, exsentences=5)


async def _get_page_url(page_name: str) -> str:
    """Returns wiki page url"""
    page = await _get_page(page_name)
    return page.canonicalurl