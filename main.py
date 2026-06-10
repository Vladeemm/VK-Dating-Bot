"""Модуль с ботом который находит во "ВКонтакте" людей по интересам.
Этот модуль содержит обработчики команд и сообщений для VK бота DatingBot.
"""
import os
import vk_api
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from DatingBotBase import session
from vk_api.longpoll import VkLongPoll, VkEventType
from actions import write_message, check_city, text_message
from models import Users, Status
from datetime import datetime


""" Статусы Пользователя в VK Bot """
START = 'start'
START_MESSAGING = 'start_messaging'
VIEW_HELP = 'view_help'
IN_MAIN_MENU = 'in_main_menu'
VIEWING_FAVORITES = 'listing_favorites'
CHOOSING_CITY = 'choosing_city'
CHOOSING_GENDER = 'choosing_gender'
CHOOSING_AGE_FROM = 'choosing_age_from'
CHOOSING_AGE_TO = 'choosing_age_to'
VIEWING_QUESTIONNAIRES = 'viewing_questionnaires'
ADD_TO_FAVORITE = 'add_to_favorite'
VIEWING_FAVORITE_QUESTIONNAIRE = 'viewing_favorite_questionnaire'

try:
    load_file = load_dotenv()
    if not load_file:
        print("Файл не найден")
    token = os.getenv('BOT_TOKEN')

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
            step=START, #надо поменять при согласовании статусов
            search_criteria={},
            list_applicants=[],
            step_datetime=datetime.now()
        )
        session.add(new_status)
        session.commit()


def initial_launch (user_vk):
    """Первый запуск бота пользователем"""
    # Статус пользователя из БД
    user_status = session.query(Status).filter(Status.user_vk_id == user_vk).first()
    if user_status.step == START:
        write_message(user_vk, "Я знакомлю красивых людей и нахожу друзей по интересам 🥰")
        write_message(user_vk, "Жмите на кнопку чтобы составить твои предпочтения для поиска!")

        keyboard = VkKeyboard(one_time=True)  # чтобы скрыть после нажатия
        keyboard.add_button('Приступим', color=VkKeyboardColor.PRIMARY)

        write_message(user_vk, "Нажмите 'Приступим'", keyboard=keyboard.get_keyboard())


def preference_formation(user_vk, message):
    """Формирование анкеты предпочтений пользователя"""
    if not message:
        return
    # Статус пользователя из БД
    user_status = session.query(Status).filter(Status.user_vk_id == user_vk).first()
    # Сбор данных для приоритета поиска
    if user_status.step == START_MESSAGING:
        # Если user обновляет предпочтения, поле search_criteria надо почистить.
        user_status.search_criteria = {}
        session.commit()

        write_message(user_vk, "В каком городе искать?")
        keyboard = VkKeyboard(one_time=True)  # чтобы скрыть после нажатия
        keyboard.add_button('Помощь', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Избранное', color=VkKeyboardColor.PRIMARY)
        if message == 'Помощь':
            user_status.step = VIEW_HELP
            session.commit()

            keyboard = VkKeyboard(one_time=True)  # чтобы скрыть после нажатия
            keyboard.add_button('Новый поиск', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Просмотр пользователей', color=VkKeyboardColor.PRIMARY)

            write_message(user_vk, "Я бот сообщества VK Dating Bot."
                                   "Я создан, чтобы знакомить красивых людей и находить друзей по интересам!")
            write_message(user_vk, "Навигация по чату простая, и имеет всего несколько кнопок.")
            write_message(user_vk, "---Помощь --- Здесь я вас жду, чтобы помочь сориентироваться в навигации по чату.")
            write_message(user_vk, "---Новый поиск --- Позволяет вам обновить свои предпочтения для поиска.")
            write_message(user_vk, "---Избранное --- Позволяет вам просмотреть все понравившиеся аккаунты.")
            write_message(user_vk, "---Назад --- Позволит вам вернуться к предыдущему пользователю.")
            write_message(user_vk, "---Вперед --- Позволит вам перейти к следующему пользователю.")
            if message == 'Новый поиск':
                user_status.step = START_MESSAGING
                session.commit()
            elif message == 'Просмотр пользователей':
                user_status.step = VIEWING_QUESTIONNAIRES
                session.commit()

        elif message == 'Избранное':
            user_status.step = VIEWING_FAVORITE_QUESTIONNAIRE
            session.commit()
            # Просмотр списка избранных

        user_status.step = CHOOSING_CITY
        session.commit()
        return

    elif user_status.step == CHOOSING_CITY:
        city = message  # текст который введет пользователь
        if not check_city(city):
            write_message(user_vk, "Возможна ошибка, такой город не найден.\n"
                                   "Попробуйте еще раз.")
            return

        # К словарю просто добавляем новый ключ значение
        user_status.search_criteria = {**user_status.search_criteria, 'city': city}
        session.commit()

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Муж.', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Жен.', color=VkKeyboardColor.PRIMARY)
        write_message(user_vk, "Какой пол тебя интересует? (М/Ж)",
                      keyboard=keyboard.get_keyboard())
        user_status.step = CHOOSING_GENDER
        session.commit()
        return

    elif user_status.step == CHOOSING_GENDER:
        gender = "male" if message == "Муж." else "female"
        user_status.search_criteria = {**user_status.search_criteria, 'gender': gender}
        session.commit()

        write_message(user_vk, "Выберите возраст ОТ (18-99 лет)")
        write_message(user_vk, "Какой минимальный возраст тебя интересует?")
        user_status.step = CHOOSING_AGE_FROM
        session.commit()
        return

    elif user_status.step == CHOOSING_AGE_FROM:
        age = message
        #надо проверить на веденное значение, что там не буквы

        while int(age) < 18 or int(age) > 90:
            write_message(user_vk, "Пожалуйста, ввести корректное число.\n"
                                   "Попробуйте еще раз.")
            age = text_message(user_vk)

        user_status.search_criteria = {**user_status.search_criteria, 'age_from': age}
        session.commit()

        write_message(user_vk, "Какой максимальный возраст тебе интересен?")
        user_status.step = CHOOSING_AGE_TO
        session.commit()
        return

    elif user_status.step == CHOOSING_AGE_TO:
        age = message
        while int(age) < 18 or int(age) > 90:
            write_message(user_vk, "Пожалуйста, ввести корректное число.\n"
                                   "Попробуйте еще раз.")
            age = text_message(user_vk)

        user_status.search_criteria = {**user_status.search_criteria, 'age_to': age}
        session.commit()

        write_message(user_vk, "Супер!🎉 Предпочтения сохранены! ")
        user_status.step = VIEWING_QUESTIONNAIRES
        session.commit()
        return


# def search_candidates(user_vk):
#     """Поиск кандидатов по предпочтениям"""
#
#     """Что мы имеем в параметрах для поиска
#    {"city": "\u041a\u0430\u0437\u0430\u043d\u044c", "gender": "female", "age_from": "35", "age_to": "37"}
#     params = {
#         'city': criteria.get('city'),
#         'sex': 1 if criteria.get('gender') == 'female' else 2,
#         'age_from': criteria.get('age_from'),
#         'age_to': criteria.get('age_to'),
#         'has_photo': 1,
#         'count': 10,
#         'fields': 'photo_max,domain'
#     }"""
#
#     pass


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
            if message == 'приступим' and user_status.step == START:
                user_status.step = START_MESSAGING
                session.commit()
                preference_formation(user_vk, '')
                continue

            if user_status.step == START:
                initial_launch(user_vk)
                continue

            if user_status.step in [START_MESSAGING, CHOOSING_CITY, CHOOSING_GENDER, CHOOSING_AGE_FROM, CHOOSING_AGE_TO]:
                preference_formation(user_vk, event.text)

             # elif user_status.step == VIEWING_FAVORITES:
             #    candidates = search_candidates(user_vk)
             #    # Тут пока так, поменяем когда опишем функции показа кандидатов
             #    if candidates:
             #        write_message(user_vk, f"Найдено {len(candidates)} кандидатов")






if __name__ == '__main__':
    main()
