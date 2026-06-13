"""Модуль с ботом который находит во "ВКонтакте" людей по интересам.
Этот модуль содержит обработчики команд и сообщений для VK бота DatingBot.
"""
import os
import vk_api
from dotenv import load_dotenv
from DatingBotBase import session
from vk_api.longpoll import VkLongPoll, VkEventType
from actions import write_message, view_help_button, add_user_to_db, menu_buttons, preference_formation
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

        menu_buttons(user_vk, "Жмите на кнопку чтобы составить твои предпочтения для поиска!\n"
                              "     👇👇👇",
                     '🎬 Начать', '🆘 Помощь', '🆒 Избранное', one_time=True)


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

            if message == '🆘 Помощь':
                menu_buttons(user_vk, "Всегда рад помочь!",
                             '▶️ Продолжить', '🆒 Избранное', one_time=True)
                view_help_button(user_vk)
                continue

            if message == '🆒 Избранное':
                menu_buttons(user_vk, "Смотрим ваш список...",
                             '⏪ Назад', '⏩ Далее', '🟢 Главное меню', one_time=True)
                get_favorite_questionnaire(user_vk)
                user_status.step = VIEWING_FAVORITE_QUESTIONNAIRE
                session.commit()
                continue

            if message == '🟢 Главное меню':
                btn = "👀 Продолжить просмотр" if user_status.step == VIEWING_FAVORITE_QUESTIONNAIRE else "🔎 Новый поиск"
                menu_buttons(user_vk, "Что вы хотите?",
                             f'{btn}', '🆘 Помощь', '🆒 Избранное', one_time=True)
                continue

            if message == '🔎 Новый поиск':
                write_message(user_vk, "Приступим к обновлению Ваших предпочтений!")
                user_status.step = START_MESSAGING
                session.commit()
                preference_formation(user_vk, message)

                continue

            if message == '🎬 Начать' and user_status.step == START:
                user_status.step = START_MESSAGING
                session.commit()
                preference_formation(user_vk, message)
                continue

            if user_status.step == START:
                initial_launch(user_vk)
                continue

            if user_status.step in [START_MESSAGING, CHOOSING_CITY, CHOOSING_GENDER, CHOOSING_AGE_FROM, CHOOSING_AGE_TO]:
                preference_formation(user_vk, event.text)

            if user_status.step == VIEWING_QUESTIONNAIRES:
                if message == '▶️ Продолжить':
                    menu_buttons(user_vk, "Возвращаемся к просмотру кандидатов",
                                  '🟢 Главное меню', '🆒 Избранное', one_time=False)
                    return

                menu_buttons(user_vk, "--- Тут ожидается логика показа кандидатов ---",
                             '🟢 Главное меню', '🆒 Избранное', one_time=False)

            # def get_search_criteria(user_vk_id) -> dict:
            #     user = session.query(Status).filter(Status.user_vk_id == user_vk_id).first()
            #     return user.search_criteria

             #   def get_questionnaires_by_criteria(city_id: int, gender: int, age_from: int, age_to: int) -> list[int]:

             #    def three_best_photos(user_vk_id) -> dict | None:


            if user_status.step == VIEWING_FAVORITE_QUESTIONNAIRE:
                if message == '▶️ Продолжить':
                    menu_buttons(user_vk, "Возвращаемся к просмотру избранных аккаунтов",
                                  '🟢 Главное меню', '🆒 Избранное', one_time=False)
                    return
                menu_buttons(user_vk, "--- Тут ожидается логика показа избранных ---",
                             '🟢 Главное меню', '🆒 Избранное', one_time=False)
                # favorite = session.query(Favorite).filter(Favorite.id == user_vk).all()






if __name__ == '__main__':
    main()
