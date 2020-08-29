#!/usr/bin/env python
# -*- coding: utf-8 -*-

#|------------------------ IMPORTS -------------------|
import requests
import pyowm
import json
from typing import Union
from aiogram import types

#|------------------- LOCAL MODULES ------------------|
from config import WEATHER_ID, TIME, \
    DATE, WETHA, YEAR, CITIES, OWM_URL, PEOPLE, GEOCODE_URL

#|---------------------- CODE ------------------------|

async def get_my_forecast(message: types.Message) -> str:
    """Return users city forecast"""
    city = await _get_users_city(message.chat.id)
    if city == None:
        return PEOPLE['need_city']
    else:
        result = await _get_long_weather(city)

    if result == None:
        result = PEOPLE['city_from_file_error']
    
    return result


async def get_my_weather(message: types.Message) -> str:
    """Return users city weather"""
    city = await _get_users_city(message.chat.id)
    if city == None:
        return PEOPLE['need_city']
    else:
        result = await _get_short_weather(city)

    if result == None:
        result = PEOPLE['city_from_file_error']
    
    return result


async def get_weather(city: str, need_long_weather: bool) -> str:
    """Return weather info"""
    try:
        if need_long_weather:
            result = await _get_long_weather(city)
        else:
            result = await _get_short_weather(city)

        if result == None:
            result = PEOPLE['nothing_in_weather']
    except:
        result = PEOPLE['nothing_in_weather']
    
    return result


async def _make_correct_time(date: str) -> str:
    """Returns time info in a right format"""
    return TIME[f'{date}']


async def _make_correct_date(date: str) -> str:
    """Returns date info in a right format"""
    return DATE[f'{date}']


async def _make_correct_weather_emoji(wethe: str) -> Union[str, None]: 
    """Returns weather info in a right format"""
    for key in WETHA.keys():
        if key in wethe:
            return WETHA[key]
    return None


async def _make_correct_city(city: str) -> Union[str, None]:
    """Returns city info in a right format"""
    city = city.lower()
    for key, value in CITIES.items():
        for key_city in key:
            if city in key_city:
                return value
    return None


async def _get_short_weather(city: str) -> Union[str, None]:
    """Returns short weather info of None"""
    try:
        from_dic_city = await _make_correct_city(city)
        if from_dic_city != None:
            city = from_dic_city
        else:
            city = city.title()

        owm = pyowm.OWM(WEATHER_ID, language='ru')
        observation = owm.weather_at_place(city)
        weather_main = observation.get_weather()
        weather_info = weather_main.get_detailed_status()
        weather_emoji = await _make_correct_weather_emoji(weather_info)
        temperature = weather_main.get_temperature('celsius')['temp']
        result = f'В городе {city} сейчас {weather_emoji}{weather_info}{weather_emoji}.\nПримерно {temperature} ℃'
        return result
    except:
        return None


async def _get_long_weather(city: str) -> Union[str, None]:
    """Returns long weather info of None"""
    try:
        correct_city = await _make_correct_city(city)
        if correct_city != None:
            city = correct_city
        else:
            city = city.title()
    
        result = city + '\n'
        response = requests.get(OWM_URL,
                           params={'q': city, 'units': 'metric', 'lang': 'ru', 'APPID': WEATHER_ID})
        data = response.json()
        day = '00-00'
        for i in data['list']:
            date = str(i['dt_txt'])
            current_day = str(date[5:10])
            current_time = str(date[11:16])
            desc = str(i['weather'][0]['description'])
            desc_cor = await _make_correct_weather_emoji(desc)
            time_cor = await _make_correct_time(current_time)

            if current_day != day:
                month = await _make_correct_date(str(current_day[:2]))
                month_emo = YEAR[month]
                day_day = str(current_day[3:5])
                result += '\n'
                result = result + f'{month_emo} {month} {day_day} {month_emo}\n'
                day = current_day

            result = result + current_time + " " + (" " * current_time.count("1"))
  
            if ((time_cor == 'ночь') or (time_cor == 'полночь')) and (desc == 'ясно'):
                result = result + WETHA['ночь_ясно'] + ' '
            elif ((time_cor == 'вечер') or (time_cor == 'сумерки')) and ( desc == 'ясно'):
                result = result + WETHA['вечер'] + ' '

            elif desc_cor != None:
                result = result + desc_cor + ' '

            else:
                result = result + desc + ' '

            temp = str('{0:+3.0f}'.format(i['main']['temp']))
            result = result + temp + '℃ ' + (" " * temp.count("1"))

            result = result + WETHA['ветер'] + str('{0:3.0f}'.format(i['wind']['speed'])) + 'м/c' + '\n'
        result = result + '\n' + city
        return result
    except:
        return None


async def _add_users_city(chat_id: str, city: str) -> None:
    """Adds users city to file"""
    with open('id_city.json', 'r+', encoding='utf-8') as file:
        data = json.load(file)
        data[f"{chat_id}"] = city
        file.seek(0)
        file.write(json.dumps(data, ensure_ascii=False, indent=4))
        file.truncate()


async def _get_users_city(chat_id: str) -> Union[str, None]:
    """Returns users city from file"""
    with open('id_city.json', 'r+', encoding='utf-8') as file:
        data = json.load(file)
        try:
            city = data[f"{chat_id}"]
        except:
            city = None
    
    return city


async def _understand_city(latitude: str, longitude: str) -> Union[str, None]:
    """Return city by coordinates"""
    json_adress_info = \
        requests.get(GEOCODE_URL + f'{longitude},{latitude}').json(encoding='utf-8')

    country = json_adress_info["response"]\
        ["GeoObjectCollection"]["featureMember"][0]\
            ["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]\
                ["AddressDetails"]["Country"]
    
    try:
        try:
            city = country["AdministrativeArea"]\
                ["SubAdministrativeArea"]["Locality"]["LocalityName"]
        except:
            try:
                city = country["AdministrativeArea"]["Locality"]["LocalityName"]
            except:
                city = country["Locality"]["LocalityName"]
    except:
        return None

    return city.lower()