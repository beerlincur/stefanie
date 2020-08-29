import requests
from aiogram import types
from typing import Union, Tuple

from config import HEADERS, URL, TOKEN, PROXIE_URL_W_AUTH, PEOPLE
from weather import get_weather, _understand_city, _add_users_city, _make_correct_city


async def get_file(file_id: str) -> Union[str, None]:
    """Returns URL for given file id or None"""    
    return await _get_file_path(file_id)


async def get_location(message: types.Message) -> str:
    """Return weather results for location in given message"""
    try:
        latitude = message['location']['latitude']
        longitude = message['location']['longitude']
        chat_id = message.chat.id

        result = await _check_location(latitude, longitude, chat_id)

        if result == None:
            result = PEOPLE['wrong_city_location']
        else:
            result += '\n\n{}'.format(PEOPLE['city_remember'])
    except:
        result = PEOPLE['wrong_city_location']

    return result


async def get_city_info(city: str, chat_id: str) -> str:
    """Return weather info about given city"""
    try:
        result = await _check_city_by_name(city, chat_id)

        if result == None:
            result = PEOPLE['wrong_city']
        else:
            result += '\n\n{}'.format(PEOPLE['city_remember'])

    except:
        result = PEOPLE['wrong_city']

    return result


async def _check_city_by_name(city: str, chat_id: str) -> Union[str, None]:
    """Return weather info about given city or None"""
    try:
        result = await get_weather(city, False)

        if result != None:
            await _add_users_city(chat_id, city)
            return result

    except:
        return None

    return None


async def _check_location(latitude: str, longitude: str, chat_id: str) -> Union[str, None]:
    """Return weather info about given location or None"""
    try:
        city = await _understand_city(latitude, longitude)
        result = await get_weather(city, False)

        if result != None:
            await _add_users_city(chat_id, city)
            return result
    except:
        return None

    return None


async def _get_file_path(file_id: str) -> Union[str, None]:
    """Return URL (telegram servers) for given file id or None"""
    try:
        url = URL + 'getFile?file_id=' + file_id
        session = requests.Session()
        
        session.proxies = {
            "http": PROXIE_URL_W_AUTH,
            "https": PROXIE_URL_W_AUTH
        }

        request_result = session.get(url, headers=HEADERS)
        json_result = request_result.json()
        local_path = json_result['result']['file_path']
        file_url = 'https://api.telegram.org/file/bot' + TOKEN + '/' + local_path

        return file_url
    except:
        return None