import os
import requests
import vk_api
from random import randrange
from dotenv import load_dotenv
from vk_api.longpoll import VkEventType, VkLongPoll

try:
    load_file = load_dotenv()
    if not load_file:
        print("Файл не найден")
    token = os.getenv('BOT_TOKEN')
    my_token = os.getenv('MY_VK_TOKEN')

except Exception as e:
    raise Exception(f"Ошибка подключения к VK API: {e}")

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk, wait=2)

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

def text_message(user_id):
    """Функция для определения поступивших сообщений из конкретного чата"""
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
            message = event.text
            return message
    return None


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

    if 'response' in data and data['response']['count'] == 0:
        return False
    cities = data['response']['items']
    for city in cities:
        if city['title'].lower() == city_name.lower():
            return True
    return False
