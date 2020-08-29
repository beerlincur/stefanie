#!/usr/bin/env python
# -*- coding: utf-8 -*-

#|------------------------ IMPORTS -------------------|
import os, re, io, logging, asyncio
from time import gmtime, strftime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

#|------------------- LOCAL MODULES ------------------|
from config import BOSS_ID, TOKEN, PROXIE_URL, PROXIE_AUTH, PEOPLE, KEYBOARD,\
    KEYBOARD_CORONA, HH_KEYBOARD, WETHA_KEYBOARD, DEAL_KEYBOARD, CANCEL_KEYBOARD, YES_NO_KEYBOARD
from hh import get_hh_results
from speaking import free_talk
from wiki import search_in_wiki
from keyboards import ListOfButtons
from google_vision import get_photo_vision_result
from get import get_location, get_city_info, get_file
from google_custom_search import get_custom_search_result
from weather import get_weather, get_my_forecast, get_my_weather
from covid19_parser import get_world_corona_stats, get_russia_corona_stats
from states import JobForm, GoogleForm, WikiForm, WethaForm, SetCityForm, CooperationForm
from middleware import remember_user_start

#|---------------------- CODE ------------------------|

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()

bot = Bot(token=TOKEN, proxy=PROXIE_URL, proxy_auth=PROXIE_AUTH)

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage, loop=loop)

# ================================================================================================== СТАРТ ХЕЛП
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Отправляет приветственно/вспомогательное сообщение"""
    await remember_user_start(message)
    await message.answer(PEOPLE['start_message'], reply_markup=KEYBOARD)

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    """Отправляет приветственно/вспомогательное сообщение"""
    await message.answer(PEOPLE['start_message'], reply_markup=KEYBOARD)

# ================================================================================================== ПОГОДА
@dp.message_handler(lambda message: message.text == '🌤 Погода 🌤')
async def weather_main_button_handler(message: types.Message):
    """Отправляет краткую сводку о погоде"""
    await message.answer("Как погодка?", reply_markup=WETHA_KEYBOARD)

@dp.callback_query_handler(lambda callback_query: True, state=WethaForm.city)
async def wetha_city_call_handler(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data:

        city_codes = {
            '2': 'Санкт-Петербург', 
            '1': 'Москва',
            '4': 'Новосибирск'
        }

        await callback_query.message.answer(await get_weather(city_codes[callback_query.data[-1]], True))
        await callback_query.message.answer(await get_weather(city_codes[callback_query.data[-1]], False))

        await state.reset_state(with_data=False)
    else:
        await callback_query.message.answer("Что-то ты не то нажал, друг")
        await state.reset_state(with_data=False)

@dp.message_handler(state=WethaForm.city)
async def wetha_city_text_handler(message: types.Message, state: FSMContext):
    await message.answer(await get_weather(message.text, True))
    await message.answer(await get_weather(message.text, False))
    await state.reset_state(with_data=False)

# ================================================================================================== РАБОТА
@dp.message_handler(lambda message: message.text == '💸 Работа 💸')
async def job_handler(message: types.Message):
    """Отправляет до 7 найденных вакансий"""
    await JobForm.job.set()
    await message.answer("Какую работу ищешь?")

@dp.message_handler(state=JobForm.job)
async def job_name_handler(message: types.Message, state: FSMContext):
    job_name = message.text
    await state.update_data(job=job_name)
    await JobForm.area.set()
    await message.answer("Где искать?", reply_markup=HH_KEYBOARD)

@dp.callback_query_handler(lambda callback_query: True, state=JobForm.area)
async def area_job_handler(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data.startswith("city"):
        data = await state.get_data()
        await callback_query.message.answer(await get_hh_results(callback_query.data[-1], data.get("job")))
        await state.reset_state(with_data=False)
    else:
        await callback_query.message.answer("Что-то ты не то нажал")
        await state.reset_state(with_data=False)

# ================================================================================================== СОТРУДНИЧЕСТВО
@dp.message_handler(lambda message: message.text == '💼 Сотрудничество 💼')
async def coop_main_handler(message: types.Message):
    await CooperationForm.name.set()
    await message.answer("Здравствуйте, моё имя Стефани и я электронный секретарь моего создателя.\
\nДля уведомления Григория о желаемом сотрудничестве,\
\nВам предлагается заполнить небольшую форму с информацией о Вашем предложении.\
\nПредоставленные Вами данные будут видны только Вам и (после подтверждения отправки) моему создателю.")

    await message.answer("Представьтесь, пожалуйста, чтобы Григорий мог понять, кто Вы: ", reply_markup=CANCEL_KEYBOARD)

@dp.message_handler(state=CooperationForm.name)
async def coop_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await CooperationForm.connect.set()
    await message.answer("Пожалуйста, укажите удобные для Вас способы связи\
\n(эл. почта, номер телефона, ссылки на соц. сети): ", reply_markup=CANCEL_KEYBOARD)

@dp.message_handler(state=CooperationForm.connect)
async def coop_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(connect=message.text)
    await CooperationForm.deal_text.set()
    await message.answer("Пожалуйста, опишите (как можно подробнее) Ваше предложение, заказ, просьбу или другое (укажите).\
\nЕсли у Вас есть готовое описание, НЕ прикладывайте его к этому сообщению,\
\nВам будет предложено отправить файл следующим сообщением.", reply_markup=CANCEL_KEYBOARD)

@dp.message_handler(state=CooperationForm.deal_text)
async def coop_deal_text_handler(message: types.Message, state: FSMContext):
    await state.update_data(deal_text=message.text)
    await CooperationForm.deal_doc_y_n.set()
    await message.answer("Вы хотите отправить файл с подробным ТЗ или другим описанием предложения?\
\nДля ответа, пожалуйста, используйте кнопки: ", reply_markup=YES_NO_KEYBOARD)

@dp.callback_query_handler(lambda callback_query: True, state=CooperationForm.deal_doc_y_n)
async def coop_deal_doc_y_n_handler(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'yes':
        await state.update_data(deal_doc_y_n='yes')
        await CooperationForm.deal_doc.set()
        await callback_query.message.answer("Пожалуйста, отправьте один файл с описанием предложения\
\n(формата PDF, DOCX и др.): ", reply_markup=CANCEL_KEYBOARD)

    elif callback_query.data == 'no':
        await state.update_data(deal_doc_y_n='no')
        await CooperationForm.money.set()
        await callback_query.message.answer("Пожалуйста, опишите Ваш бюджет, рассчитаный на сотрудничество с Григорием: ", reply_markup=CANCEL_KEYBOARD)
    else:
        await CooperationForm.deal_doc_y_n.set()
        await callback_query.message.answer("Пожалуйста, ответье 'Да' или 'Нет': ", reply_markup=YES_NO_KEYBOARD)

@dp.message_handler(content_types=types.ContentTypes.DOCUMENT, state=CooperationForm.deal_doc)
async def coop_deal_doc_handler(message: types.Message, state: FSMContext):
    await CooperationForm.money.set()
    await state.update_data(deal_doc=message.document.file_id)
    
    await message.answer("Пожалуйста, опишите Ваш бюджет, рассчитаный на сотрудничество с Григорием: ", reply_markup=CANCEL_KEYBOARD)

@dp.message_handler(state=CooperationForm.money)
async def coop_money_handler(message: types.Message, state: FSMContext):
    await state.update_data(money=message.text)
    await CooperationForm.send_y_n.set()
    state_data = await state.get_data()
    ap_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    ap_name = state_data.get('name')
    ap_connect = state_data.get('connect')
    ap_deal_t = state_data.get('deal_text')
    ap_deal_y_n = state_data.get('deal_doc_y_n')
    if ap_deal_y_n == 'yes':
        y_n = 'Да'
    else:
        y_n = 'Нет'
    
    ap_money = state_data.get('money')

    result = f"""
===========================
Обращение от {ap_time}:

Имя: {ap_name}\n
Контакты: {ap_connect}\n
Предложение: {ap_deal_t}\n
Файл описание: {y_n}
Бюджет: {ap_money}
===========================
"""
    await message.answer(result)
    await message.answer("Перед Вами сообщение, которое будет отправлено Григорию,\
\nнажмите кнопку 'Подтвердить', для отправки, 'Отменить отправку', для отмены.", reply_markup=DEAL_KEYBOARD)

@dp.callback_query_handler(lambda callback_query: True, state=CooperationForm.send_y_n)
async def coop_send_y_n_handler(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'confirm_deal_send':
        state_data = await state.get_data()
        ap_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        ap_name = state_data.get('name')
        ap_connect = state_data.get('connect')
        ap_deal_t = state_data.get('deal_text')
        ap_deal_y_n = state_data.get('deal_doc_y_n')
        if ap_deal_y_n == 'yes':
            y_n = 'Да'
        else:
            y_n = 'Нет'
        
        ap_money = state_data.get('money')

        result = f"""
===========================
Обращение от {ap_time}:

Имя: {ap_name}\n
Контакты: {ap_connect}\n
Предложение: {ap_deal_t}\n
Файл описание: {y_n}
Бюджет: {ap_money}
===========================
"""
        await bot.send_message(BOSS_ID, result)

        if ap_deal_y_n == "yes":
            ap_deal_f = state_data.get('deal_doc')
            await bot.send_document(BOSS_ID, ap_deal_f)

        await callback_query.message.answer("Ваше обращение успешно отправлено,\
в скором времени Григорий с Вами свяжется, спасибо за Ваше время!", reply_markup=KEYBOARD)
        await state.reset_state(with_data=False)

    elif callback_query.data == 'cancel_deal_send':
        await state.reset_state(with_data=False)
        await callback_query.message.answer("Вы отменили отправку обращения, может быть, в другой раз, спасибо за Ваше время!", reply_markup=KEYBOARD)
    else:
        await CooperationForm.send_y_n.set()
        await callback_query.message.answer("Пожалуйста, подтвердите или отмените отправку: ", reply_markup=DEAL_KEYBOARD)

# ================================================================================================== ГУГЛ
@dp.message_handler(lambda message: message.text == '🔎 Гугл 🔎')
async def custom_google_handler(message: types.Message):
    """Начало работы с Google"""
    await GoogleForm.query.set()
    await message.answer("Что найти?")

@dp.message_handler(state=GoogleForm.query)
async def google_query_handler(message: types.Message, state: FSMContext):
    """Отправляет первую страницу из результата поиска Google"""
    await state.reset_state(with_data=False)
    await message.answer(await get_custom_search_result(message.text.lower()), reply_markup=KEYBOARD)

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def vision_google_handler(message: types.Message):
    """Отправляет Google Web анализ полученного изображения"""
    await message.answer(await get_photo_vision_result(message), reply_markup=KEYBOARD)

# ================================================================================================== ВИКИ
@dp.message_handler(lambda message: message.text == '🔮 Вики 🔮')
async def wiki_handler(message: types.Message):
    """Начало работы с Wikipedia"""
    await WikiForm.query.set()
    await message.answer("Что найти?")

@dp.message_handler(state=WikiForm.query)
async def wiki_query_handler(message: types.Message, state: FSMContext):
    """Отправляет несколько первых предложений из статьи Wikipedia"""
    await state.reset_state(with_data=False)
    await message.answer(await search_in_wiki(message.text.lower()), reply_markup=KEYBOARD)

# ================================================================================================== МОЯ ПОГОДА
@dp.message_handler(lambda message: message.text == '☂️ Моя погода ☂️') # моя погода
async def my_weather_handler(message: types.Message):
    """Отправляет краткую сводку о погоде сохранённого города"""
    await message.answer(await get_my_forecast(message), reply_markup=KEYBOARD)

# ================================================================================================== МОЙ ПРОГНОЗ
@dp.message_handler(lambda message: message.text == '⛅️ Мой прогноз ⛅️') # мой прогноз 
async def my_forecast_handler(message: types.Message):
    """Отправляет прогноз погоды сохранённого города"""
    await message.answer(await get_my_weather(message), reply_markup=KEYBOARD)

# ================================================================================================== КОРОНАВИРУС
@dp.message_handler(lambda message: message.text == '🐉 Коронавирус 🐉') # коронавирус 
async def my_forecast_handler(message: types.Message):
    """Отправляет информацию о коронавирусе"""
    await message.answer("Где именно?", reply_markup=KEYBOARD_CORONA)

# ================================================================================================== ГЕОЛОКАЦИЯ
@dp.message_handler(content_types=types.ContentType.LOCATION, state=SetCityForm.city)
async def location_handler(message: types.Message, state: FSMContext):
    """Запоминает город по отправленной локации"""
    await message.answer(await get_location(message), reply_markup=KEYBOARD)
    await state.reset_state(with_data=False)
        
# ================================================================================================== МОЙ ГОРОД
@dp.callback_query_handler(lambda callback_query: True, state=SetCityForm.city)
async def city_name_call_handler(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data:

        city_codes = {
            '2': 'Санкт-Петербург', 
            '1': 'Москва',
            '4': 'Новосибирск'
        }

        await callback_query.message.answer(await get_city_info(city_codes[callback_query.data[-1]], callback_query.message.chat.id))
        await state.reset_state(with_data=False)
    else:
        await callback_query.message.answer("Что-то ты не то нажал, друг")
        await state.reset_state(with_data=False)

@dp.message_handler(state=SetCityForm.city)
async def city_name_text_handler(message: types.Message, state: FSMContext):
    await message.answer(await get_city_info(message.text, message.chat.id))
    await state.reset_state(with_data=False)

# ================================================================================================== КОЛЛБЕКИ БЕЗ СТЕЙТОВ
@dp.callback_query_handler(lambda callback_query: True, state="*")
async def call_query_handler(callback_query: types.CallbackQuery, state: FSMContext): # корона хэндлер
    """Отправляет информацию о коронавирусе"""
    if callback_query.data == "corona_russia":
        await callback_query.message.answer(await get_russia_corona_stats(), reply_markup=KEYBOARD)

    elif callback_query.data == "corona_world":
        await callback_query.message.answer(await get_world_corona_stats(), reply_markup=KEYBOARD)

    elif callback_query.data == "my_wetha":
        await callback_query.message.answer(await get_my_weather(callback_query.message), reply_markup=KEYBOARD)

    elif callback_query.data == "my_forecast":
        await callback_query.message.answer(await get_my_forecast(callback_query.message), reply_markup=KEYBOARD)

    elif callback_query.data == "wetha_in":
        await WethaForm.city.set()
        await callback_query.message.answer("В каком городе? Напиши название или вот красивые кнопки :)", reply_markup=HH_KEYBOARD)
    elif callback_query.data == "my_city":
        await SetCityForm.city.set()
        await callback_query.message.answer("Какой город сделать твоим? Напиши название, используй красивые кнопки или отправь свою геолокацию!", reply_markup=HH_KEYBOARD)
    elif callback_query.data == "cancel_movement":
        await state.reset_state(with_data=False)
        await callback_query.message.answer("Вы отменили текущее действие", reply_markup=KEYBOARD)
    else:
        await callback_query.message.answer("Что-то ты не то нажал, дружище")

# ================================================================================================== ВСЕ ОСТАЛЬНОЕ
@dp.message_handler()
async def everything_else_handler(message: types.Message):
    """Обрабатывает прочие сообщения"""
    await message.answer(free_talk(message.text.lower()), reply_markup=KEYBOARD)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
