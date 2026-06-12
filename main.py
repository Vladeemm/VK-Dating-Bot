"""Модуль с ботом который находит во "ВКонтакте" людей по интересам.
Этот модуль содержит обработчики команд и сообщений для VK бота DatingBot.
"""
import os
import vk_api
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from DatingBotBase import session
from vk_api.longpoll import VkLongPoll, VkEventType
from actions import write_message, check_city, view_help_button, add_user_to_db, menu_buttons, favorite_questionnaire
from models import Status


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


def initial_launch (user_vk):
    """Первый запуск бота пользователем"""
    # Статус пользователя из БД
    user_status = session.query(Status).filter(Status.user_vk_id == user_vk).first()
    if user_status.step == START:
        write_message(user_vk, "Здравствуйте, я Бот который знакомит красивых людей и находит друзей по интересам 🥰")

        keyboard = VkKeyboard(one_time=True)  # чтобы скрыть после нажатия
        keyboard.add_button('Приступим', color=VkKeyboardColor.PRIMARY)
        write_message(user_vk, "Жмите на кнопку чтобы составить твои предпочтения для поиска!"
                               "👇👇👇", keyboard=keyboard.get_keyboard())


def preference_formation(user_vk, message):
    """Формирование анкеты предпочтений пользователя"""
    if not message:
        return
    # Статус пользователя из БД
    user_status = session.query(Status).filter(Status.user_vk_id == user_vk).first()

    if message == '🆘 Помощь':
        menu_buttons(user_vk, "Всегда рад помочь!",
                     '⏪ Назад', one_time=False)
        view_help_button(user_vk)

    if message == '🆒 Избранное':
        menu_buttons(user_vk, "Смотрим ваш список...",
                     '⏪ Назад', '🆘 Помощь', one_time=False)
        favorite_questionnaire(user_vk)
        user_status.step = VIEWING_QUESTIONNAIRES
        session.commit()

    if message == '⏪ Назад':
        menu_buttons(user_vk, "Вернемся к предыдущему действию.",
                     '🆘 Помощь', '🆒 Избранное', one_time=False)
        favorite_questionnaire(user_vk)
        user_status.step = VIEWING_QUESTIONNAIRES
        session.commit()








    # Сбор данных для приоритета поиска
    if user_status.step == START_MESSAGING:
        # Если user обновляет предпочтения, поле search_criteria надо почистить.
        user_status.search_criteria = {}
        session.commit()
        menu_buttons(user_vk, "В каком городе искать?",
                     '🆘 Помощь', '🆒 Избранное', one_time=False)

        user_status.step = CHOOSING_CITY
        session.commit()
        return

    elif user_status.step == CHOOSING_CITY:
        city = message
        if not check_city(city):
            write_message(user_vk, "Возможна ошибка, такой город не найден.\n"
                                   "Попробуйте еще раз.")
            return

        # К словарю просто добавляем новый ключ значение
        user_status.search_criteria = {**user_status.search_criteria, 'city': city}
        session.commit()

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('♂️ Муж.', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('♀️ Жен.', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Не имеет значение', color=VkKeyboardColor.POSITIVE)
        write_message(user_vk, "Какой пол вас интересует? (М/Ж)",
                      keyboard=keyboard.get_keyboard())
        user_status.step = CHOOSING_GENDER
        session.commit()
        return

    elif user_status.step == CHOOSING_GENDER:
        sex = "2" if message == "♂️ Муж." else "1" if message == "♀️ Жен." else "0"
        user_status.search_criteria = {**user_status.search_criteria, 'sex': sex}
        session.commit()

        write_message(user_vk, "Выберите возраст (от 18 до 99 лет)")
        menu_buttons(user_vk, "Какой минимальный возраст вас интересует?",
                     '🆘 Помощь', '🆒 Избранное', one_time=False)

        write_message(user_vk, )
        user_status.step = CHOOSING_AGE_FROM
        session.commit()
        return

    elif user_status.step == CHOOSING_AGE_FROM:
        age = message
        if not any(char.isdigit() for char in age):
            write_message(user_vk, "Пожалуйста, ввести корректное значение.")
            return

        if int(age) < 18 or int(age) > 90:
            write_message(user_vk, "Пожалуйста, выберите возраст (от 18 до 99 лет)")
            return

        user_status.search_criteria = {**user_status.search_criteria, 'age_from': age}
        session.commit()

        write_message(user_vk, "Какой максимальный возраст вам интересен?")
        user_status.step = CHOOSING_AGE_TO
        session.commit()
        return

    elif user_status.step == CHOOSING_AGE_TO:
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




# def search_candidates(user_vk):
#     """Поиск кандидатов по предпочтениям"""
#
#    pass


def main():
    """Основной цикл работы бота"""
    print("Бот начал работу")

    session.query(Status).update({Status.step: START})#Удалить из готового кода
    session.commit()#Удалить из готового кода

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_vk = event.user_id
            message = event.text

            if event.peer_id != event.user_id:
                continue

            add_user_to_db(user_vk)

            user_status = session.query(Status).filter(Status.user_vk_id == user_vk).first()

            # Обработка команды 'Приступим'
            if message == 'Приступим' and user_status.step == START:
                user_status.step = START_MESSAGING
                session.commit()
                preference_formation(user_vk, message)
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
