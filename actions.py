import os
import requests
import vk_api
from random import randrange
from dotenv import load_dotenv
from vk_api import longpoll
from vk_api.longpoll import VkEventType

try:
    load_file = load_dotenv()
    if not load_file:
        print("Файл не найден")
    token = os.getenv('BOT_TOKEN')
    my_token = os.getenv('MY_VK_TOKEN')

except Exception as e:
    raise Exception(f"Ошибка подключения к VK API: {e}")

vk = vk_api.VkApi(token=token)

def write_message(user_id, message, keyboard=None):
    """Бот отправляет сообщения в чат"""
    params = {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7),
    }

    if keyboard:
        params['keyboard'] = keyboard

    vk.method('messages.send', params)

def text_message():
    """Функция для определения поступивших сообщений из чата"""
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            message = event.text.lower()
    return message


def check_city(city_name, country_id=1):
    """Функция проверки существующего города в России"""
    params = {
        'country_id': country_id,
        'q': city_name,
        'v': '5.199',
        'access_token': my_token
    }
    response = requests.get('https://api.vk.com/method/database.getCities',
                            params=params
                            )
    data = response.json()

    if 'response' in data and data['response']['count'] > 0:
        return True
    else:
        return False