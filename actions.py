import os
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
