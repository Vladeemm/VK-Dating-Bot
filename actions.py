import os
import time
import requests
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from DatingBotBase import session
from models import Users, Status, Favorite
from datetime import datetime
from random import randrange
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll


""" Статус Пользователя в VK Bot """
START = 'start'

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


def add_user_to_db(vk_id):
    """Добавление пользователя в базу данных"""
    user_info = vk.method('users.get', {'user_ids': vk_id})
    if user_info:
        first_name = user_info[0]['first_name']
    else:
        first_name = str(vk_id) #вдруг нет имени
    user = session.query(Users).filter(Users.id == vk_id).first()
    if not user:
        new_user = Users(
            id=vk_id,
            name=first_name
        )
        session.add(new_user)
        session.commit()

        new_status = Status(
            user_vk_id=vk_id,
            step=START,
            search_criteria={},
            list_applicants=[],
            step_datetime=datetime.now()
        )
        session.add(new_status)
        session.commit()

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


def check_city(city_name, country_id=1) -> bool:
    """Проверяет наличие в базе данных ВКонтакте города России"""
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


def view_help_button(user_vk):
    """Бот отправляет сообщения информационного характера"""
    write_message(user_vk, "Вас обслуживает бот сообщества VK Dating Bot. "
                           "Я создан, чтобы знакомить красивых людей и находить друзей по интересам!")
    # time.sleep(0.5)
    # write_message(user_vk, "Навигация по чату простая, и имеет всего несколько кнопок.")
    # time.sleep(1)
    # write_message(user_vk, "--- 🟢 Главное меню --- С помощью главного меню вы активируете три кнопки. "
    #                        "--- 🔎 Новый поиск --- или --- Продолжить просмотр ---, --- 🆘 Помощь ---, --- 🆒 Избранное ---")
    # write_message(user_vk, "--- ▶️ Продолжить --- Мы продолжим действие, на котором остановились")
    # write_message(user_vk, "--- 🆘 Помощь --- Здесь я вас жду, чтобы помочь сориентироваться в навигации по чату.")
    # write_message(user_vk, "--- 🔎 Поиск --- Позволяет вам обновить свои предпочтения для поиска.")
    # write_message(user_vk, "--- 🆒 Избранное --- Позволяет вам просмотреть все понравившиеся аккаунты.")
    # write_message(user_vk, "--- ⏪ Назад --- Позволит вам вернуться к предыдущему пользователю.")
    # write_message(user_vk, "--- ⏩ Далее --- Позволит вам перейти к следующему пользователю.")

def menu_buttons(user_vk, text, btn_text1, btn_text2=None, btn_text3=None, one_time=False):
    keyboard = VkKeyboard(one_time=one_time)
    keyboard.add_button(btn_text1, color=VkKeyboardColor.PRIMARY)
    if btn_text2:
        keyboard.add_button(btn_text2, color=VkKeyboardColor.PRIMARY)
    if btn_text3:
        keyboard.add_button(btn_text3, color=VkKeyboardColor.PRIMARY)
    write_message(user_vk, f'{text}', keyboard=keyboard.get_keyboard())


def favorite_questionnaire(user_vk):
    user_favorite = session.query(Favorite).filter(Favorite.favorite_user_vk_id == user_vk).all()
    if not user_favorite:
        write_message(user_vk, "Извините, вы еще никого не добавили в избранное!")

    write_message(user_vk, "=== Тут будет логика на показ фаворитов ===")
    return
