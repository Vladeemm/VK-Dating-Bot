import os
import random
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
from vk_actions import get_city_id


""" Статус Пользователя в VK Bot """
START = 'start'
START_MESSAGING = 'start_messaging'
VIEW_HELP = 'view_help'
VIEWING_FAVORITES = 'listing_favorites'
CHOOSING_CITY = 'choosing_city'
CHOOSING_GENDER = 'choosing_gender'
CHOOSING_AGE_FROM = 'choosing_age_from'
CHOOSING_AGE_TO = 'choosing_age_to'
VIEWING_QUESTIONNAIRES = 'viewing_questionnaires'
VIEWING_FAVORITE_QUESTIONNAIRE = 'viewing_favorite_questionnaire'

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
    time.sleep(0.5)
    write_message(user_vk, "Навигация по чату простая, и имеет всего несколько кнопок.")
    time.sleep(1)
    write_message(user_vk, "--- 🟢 Главное меню --- С помощью главного меню вы активируете три кнопки. "
                           "--- 🔎 Новый поиск --- или --- Продолжить просмотр ---, --- 🆘 Помощь ---, --- 🆒 Избранное ---")
    write_message(user_vk, "--- ▶️ Продолжить --- Мы продолжим действие, на котором остановились")
    write_message(user_vk, "--- 🆘 Помощь --- Здесь я вас жду, чтобы помочь сориентироваться в навигации по чату.")
    write_message(user_vk, "--- 🔎 Поиск --- Позволяет вам обновить свои предпочтения для поиска.")
    write_message(user_vk, "--- 🆒 Избранное --- Позволяет вам просмотреть все понравившиеся аккаунты.")
    write_message(user_vk, "--- ⏪ Назад --- Позволит вам вернуться к предыдущему пользователю.")
    write_message(user_vk, "--- ⏩ Далее --- Позволит вам перейти к следующему пользователю.")

def menu_buttons(user_vk, text, btn_text1, btn_text2=None, btn_text3=None, one_time=False):
    """Создает до трех кнопок в один ряд синего цвета"""
    keyboard = VkKeyboard(one_time=one_time)
    keyboard.add_button(btn_text1, color=VkKeyboardColor.PRIMARY)
    if btn_text2:
        keyboard.add_button(btn_text2, color=VkKeyboardColor.PRIMARY)
    if btn_text3:
        keyboard.add_button(btn_text3, color=VkKeyboardColor.PRIMARY)
    write_message(user_vk, f'{text}', keyboard=keyboard.get_keyboard())


def preference_formation(user_vk, message):
    """Формирование анкеты предпочтений пользователя"""
    if not message:
        return
    # Статус пользователя из БД
    user_status = session.query(Status).filter(Status.user_vk_id == user_vk).first()

    # Сбор данных для приоритета поиска
    if (user_status.step == START_MESSAGING) or (message == '🔎 Новый поиск'):
        # Если user обновляет предпочтения, поле search_criteria надо почистить.
        user_status.search_criteria = {}
        session.commit()
        menu_buttons(user_vk, "Пожалуйста, напишите  название города на русском языке.",
                     '🟢 Главное меню', '🆒 Избранное', one_time=False)

        user_status.step = CHOOSING_CITY
        session.commit()
        return

    elif user_status.step == CHOOSING_CITY:
        if message == '▶️ Продолжить':
            menu_buttons(user_vk, "Пожалуйста напишите в каком городе искать новых знакомых?",
                         '🟢 Главное меню', '🆒 Избранное', one_time=False)
            return

        city = message
        if not check_city(city):
            write_message(user_vk, "Возможна ошибка, такой город не найден.\n"
                                   "Попробуйте еще раз.")
            menu_buttons(user_vk, "Пожалуйста напишите в каком городе искать знакомства",
                         '🟢 Главное меню', '🆒 Избранное', one_time=False)
            return

        city_id = get_city_id(city)
        # К словарю просто добавляем новый ключ значение
        user_status.search_criteria = {**user_status.search_criteria, 'city': city_id}
        session.commit()

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('♂️ Муж.', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('♀️ Жен.', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Не имеет значение', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('🟢 Главное меню', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('🆒 Избранное', color=VkKeyboardColor.PRIMARY)
        write_message(user_vk, "Какой пол вас интересует?",
                      keyboard=keyboard.get_keyboard())
        user_status.step = CHOOSING_GENDER
        session.commit()
        return

    elif user_status.step == CHOOSING_GENDER:
        if message == '▶️ Продолжить':
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('♂️ Муж.', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('♀️ Жен.', color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()
            keyboard.add_button('Не имеет значение', color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()
            keyboard.add_button('🟢 Главное меню', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('🆒 Избранное', color=VkKeyboardColor.PRIMARY)
            write_message(user_vk, "Пожалуйста укажите какой пол вас интересует.",
                          keyboard=keyboard.get_keyboard())
            return
        sex = "2" if message == "♂️ Муж." else "1" if message == "♀️ Жен." else "0"
        user_status.search_criteria = {**user_status.search_criteria, 'sex': sex}
        session.commit()

        write_message(user_vk, "Определите возрастной диапазон (от 18 до 99 лет)")
        menu_buttons(user_vk, "Какой минимальный возраст вас интересует?",
                     '🟢 Главное меню', '🆒 Избранное', one_time=False)

        user_status.step = CHOOSING_AGE_FROM
        session.commit()
        return

    elif user_status.step == CHOOSING_AGE_FROM:
        if message == '▶️ Продолжить':
            menu_buttons(user_vk, "Пожалуйста напишите какой минимальный возраст вас интересует.",
                         '🟢 Главное меню', '🆒 Избранное', one_time=False)
            return

        age = message
        if not any(char.isdigit() for char in age):
            write_message(user_vk, "Пожалуйста, ввести корректное значение.")
            return

        if int(age) < 18 or int(age) > 90:
            write_message(user_vk, "Пожалуйста, выберите возраст (от 18 до 99 лет)")
            return

        user_status.search_criteria = {**user_status.search_criteria, 'age_from': age}
        session.commit()

        write_message(user_vk, "Напишите предельный возраст который вам интересен.")
        user_status.step = CHOOSING_AGE_TO
        session.commit()
        return

    elif user_status.step == CHOOSING_AGE_TO:
        if message == '▶️ Продолжить':
            menu_buttons(user_vk, "Пожалуйста напишите какой предельный возраст который вам интересен.",
                         '🟢 Главное меню', '🆒 Избранное', one_time=False)
            return

        age = message
        min_age = user_status.search_criteria['age_from']
        if not any(char.isdigit() for char in age):
            write_message(user_vk, "Пожалуйста, ввести корректное значение.")
            return
        elif  int(age) < 18 or int(age) > 90:
            write_message(user_vk, "Пожалуйста, выберите возраст (от 18 до 99 лет)")
            return
        elif int(age) < int(min_age):
            write_message(user_vk, f"Пожалуйста, выберите возраст (от {min_age} до 99 лет)")
            return

        user_status.search_criteria = {**user_status.search_criteria, 'age_to': age}
        session.commit()

        write_message(user_vk, "Супер!🎉 Твои предпочтения сохранены, я готов к поиску! ")
        user_status.step = VIEWING_QUESTIONNAIRES
        session.commit()
        return


def get_random_id() -> int:
    """ Возвращает случайное число из диапазона """
    return random.randint(-2**30, 2**30)