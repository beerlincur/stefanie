#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests 
import re
from typing import Union

from config import HEADERS, PEOPLE


async def get_hh_results(area_code: int, job_name: str) -> str:
    """Returns head hunter search results"""
    hh_result = await _hh_api(area_code, job_name)
    if hh_result != None:
        return hh_result

    return PEOPLE['nothing_in_hh']


async def _hh_api(area_code: int, job_name: str) -> Union[str, None]:
    """Returns head hunter search results or None"""
    try:
        job_url = f"https://api.hh.ru/vacancies?area={area_code}&text={job_name}&per_page=7&page=1"
        session = requests.Session()
        request = session.get(job_url, headers=HEADERS)

        result = '======================\n'
        if len(request.json()["items"]) == 0:
            return None

        for job in request.json()["items"]:

            result += ('📈' + job["name"] + '📉' + '\n')
            result += ('🌎' + '"' + job["employer"]["name"] + '"' + '🌎' + '\n')
            result += '💸'


            if job["salary"] == None:
                result += "Бесценно💸\n"

            elif job["salary"]["from"] == None and job["salary"]["to"] == None:
                result += "Бесценно💸\n"

            elif job["salary"]["to"] == None:
                result += ("от " + str(job["salary"]["from"]) + '💸\n')

            elif job["salary"]["from"] == None:
                result += ("до " + str(job["salary"]["to"]) + '💸\n')

            else:
                result = result + str(job["salary"]["from"]) + "-" + str(job["salary"]["to"]) + '💸\n'

            if job["snippet"]["requirement"] != None:
                result += ('📄' + re.sub(r'\<[^>]*\>', '', job["snippet"]["requirement"]) + '.\n')

            if job["snippet"]["responsibility"] != None:
                result += (re.sub(r'\<[^>]*\>', '', job["snippet"]["responsibility"]) + '.📄\n')
                
            result += ('🔎' + job['alternate_url'] + '\n')
            result += ('='*22 + '\n')
            
        return result
    except:
        return None