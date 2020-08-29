#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from urllib.parse import unquote
from googleapiclient.discovery import build
from typing import Union

from config import PEOPLE, API_GOOGLE, CX_ID_GOOGLE_SEARCH


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"google_credit.json"


async def get_custom_search_result(query: str) -> str:
    """Returns search results"""
    answer = await _search_in_google(query)

    if answer != None:
        return answer

    return PEOPLE['nothing_in_google']


async def _search_in_google(query: str) -> Union[str, None]:
    """Returns search results or None"""  
    try:
        resourse = build("customsearch", 'v1', developerKey=API_GOOGLE).cse()

        result = resourse.list(q=query, cx=CX_ID_GOOGLE_SEARCH).execute()

        to_send = f'Друг, я спросила у гугла <{query}>, передаю ответ:\n======================\n'

        for item in result['items']:
            to_send = to_send + '🌐' + item['title'] + '🌐\n'
            to_send = to_send + '🔎' + unquote(item['link']) + '\n'
            to_send = to_send + '======================\n'

        return to_send

    except:
        return None
    