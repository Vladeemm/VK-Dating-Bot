"""Модуль с ботом который находит во "ВКонтакте" людей по интересам.
Этот модуль содержит обработчики команд и сообщений для VK бота DatingBot.
"""
import datetime
import random
import time
import os
import vk_api
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from DatingBotBase import session
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from actions import write_message, text_message
from models import Users, Status
from datetime import datetime

try:
    load_file = load_dotenv()
    if not load_file:
        print("Файл не найден")
    token = os.getenv('BOT_TOKEN')

except Exception as e:
    raise Exception(f"Ошибка подключения к VK API: {e}")

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk, wait=1)


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
            step='start', #надо поменять при согласовании статусов
            search_criteria={},
            list_applicants={},
            step_datetime=datetime.now()
        )
        session.add(new_status)
        session.commit()


def initial_launch (user_vk):
    """Первый запуск бота пользователем"""
    # Статус пользователя из БД
    user_status = session.query(Status).filter(Status.user_vk_id == user_vk).first()
    if user_status.step == 'start':
        write_message(user_vk, "Я знакомлю красивых людей и нахожу друзей по интересам 🥰")
        write_message(user_vk, "Жмите на кнопку чтобы составить твои предпочтения для поиска!")

        keyboard = VkKeyboard(one_time=True)  # чтобы скрыть после нажатия
        keyboard.add_button('Приступим', color=VkKeyboardColor.PRIMARY)

        write_message(user_vk, "Нажмите 'Приступим'", keyboard=keyboard.get_keyboard())


def preference_formation(user_vk, message):
    """Формирование анкеты предпочтений пользователя"""
    # Статус пользователя из БД
    user_status = session.query(Status).filter(Status.user_vk_id == user_vk).first()

    if user_status.step == 'start_messaging':
        # Сбор данных для приоритета поиска
        write_message(user_vk, "В каком городе искать?")
        user_status.step = 'choosing_city'
        session.commit()
        return

    elif user_status.step == 'choosing_city':
        city = message # текст который введет пользователь
        user_status.search_criteria['choosing_city'] = city
        session.commit()

        write_message(user_vk, "Какой пол тебя интересует? (М/Ж)")
        user_status.step = 'choosing_gender'
        session.commit()
        return

    elif user_status.step == 'choosing_gender':
        gender = "men" if message.lower() == "м" else "woman"
        user_status.search_criteria['choosing_gender'] = gender
        session.commit()

        write_message(user_vk, "Какой возраст тебя интересует? (например: 20-30)") #такой запрос сокращает код
        user_status.step = 'choosing_age'
        session.commit()
        return

    elif user_status.step == 'choosing_age':
        try:
            age_range = message.split('-') # так как написали 20-30, значение надо разделить
            user_status.search_criteria['age_from'] = int(age_range[0])
            user_status.search_criteria['age_to'] = int(age_range[1])

            write_message(user_vk, "Супер!🎉 Предпочтения сохранены! ")
            user_status.step = 'search'
            session.commit()
            return
        except (ValueError, IndexError):
            write_message(user_vk, "Неверный формат. Пример необходимой записи: 20-30")
            return


def search_candidates(user_vk):
    """Поиск кандидатов по предпочтениям"""

    """Что мы имеем в параметрах для поиска
    params = {
        'city': criteria.get('choosing_city'),
        'sex': 1 if criteria.get('choosing_gender') == 'woman' else 2,  # тут использую запись как  1 или 2 -- 1-жен,2-муж
        'age_from': criteria.get('age_from'),
        'age_to': criteria.get('age_to'),
        'has_photo': 1,
        'count': 10,
        'fields': 'photo_max,domain'
    }"""

    pass


def main():
    """Основной цикл работы бота"""
    print("Бот начал работу")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_vk = event.user_id
            message = event.text.lower()

            add_user_to_db(user_vk)

            user_status = session.query(Status).filter(Status.user_vk_id == user_vk).first()

            # Обработка команды 'Приступим'
            if event.text.lower() == 'приступим' and user_status.step == 'start':
                user_status.step = 'start_messaging'
                session.commit()
                preference_formation(user_vk, '')
                continue

            if user_status.step == 'start':
                initial_launch(user_vk)
                continue

            if user_status.step in ['start_messaging', 'choosing_city', 'choosing_gender', 'choosing_age']:
                preference_formation(user_vk, event.text)
                continue
            # elif user_status.step == 'listing_favorites':
            #    candidates = search_candidates(user_vk)
                # Тут пока так, поменяем когда опишем функции показа кандидатов
                if candidates:
                    write_message(user_vk, f"Найдено {len(candidates)} кандидатов")

            print(user_status.search_criteria)
            write_message(user_vk, f"Данные для поиска сохранены")
            session.commit()



if __name__ == '__main__':
    main()

