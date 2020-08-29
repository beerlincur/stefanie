#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import requests
from aiogram import types as aiotypes
from google.cloud import vision
from google.cloud.vision import types
from urllib.parse import unquote

from config import PROXIE_URL_W_AUTH, HEADERS
from get import _get_file_path


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"google_credit.json"


def get_photo_vision_result(message: aiotypes.Message) -> str:
    """Returns results of google vision api"""
    file_id = message['photo'][0]['file_id']
    
    file_url = _get_file_path(file_id)

    session = requests.Session()

    session.proxies = {
        "http": PROXIE_URL_W_AUTH,
        "https": PROXIE_URL_W_AUTH
    }
    
    photo = session.get(file_url, headers=HEADERS)

    image_url = "photo.png"

    with open(image_url, 'wb') as file:
        file.write(photo.content)
        
    return _report(_annotate(image_url))


def _annotate(path: str):
    """Returns web annotations given the path to an image."""
    client = vision.ImageAnnotatorClient()

    if path.startswith('http') or path.startswith('gs:'):
        image = types.Image()
        image.source.image_uri = path

    else:
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)

    web_detection = client.web_detection(image=image).web_detection

    return web_detection


def _report(annotations) -> str:
    """Prints detected features in the provided web annotations."""

    result = '📚Я обратилась к интернету - вот результат:📚\n======================\n'

    if annotations.web_entities:
        result = result + '📕{} заголовков страниц:📕 '.format(
              len(annotations.web_entities)) + '\n'

        for entity in annotations.web_entities[:4]:
            result = result + 'Заголовок: {}'.format(entity.description) + '\n'
    
    if annotations.pages_with_matching_images:
        result = result + '======================\n'
        result = result + '\n' + '📗{} страниц с похожими картинками:📗'.format(
            len(annotations.pages_with_matching_images)) + '\n'

        for page in annotations.pages_with_matching_images[:4]:
            result = result + 'Ссылка   : {}'.format(unquote(page.url)) + '\n'

    if annotations.full_matching_images:
        result = result + '======================\n'
        result = result + '\n' + '📘{} полных совпадений: 📘'.format(
              len(annotations.full_matching_images)) + '\n'

        for image in annotations.full_matching_images[:4]:
            result = result + 'Ссылка  : {}'.format(unquote(image.url)) + '\n'

    if annotations.partial_matching_images:
        result = result + '======================\n'
        result = result + '\n' + '📙{} частичных совпадений:📙 '.format(
              len(annotations.partial_matching_images)) + '\n'

        for image in annotations.partial_matching_images[:2]:
            result = result + 'Ссылка  : {}'.format(unquote(image.url)) + '\n'
    
    return result


#'🔮📕📗📘📙🔎📚'
