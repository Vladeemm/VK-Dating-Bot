"""Обработчики событий бота."""

from vk_api.longpoll import VkLongPoll, VkEventType
from bot.vk_api.client import vk_group_session
from bot.core.states import (
    START,
    START_MESSAGING,
    VIEWING_FAVORITE_QUESTIONNAIRE,
    CHOOSING_CITY,
    CHOOSING_GENDER,
    CHOOSING_AGE_FROM,
    CHOOSING_AGE_TO,
    VIEWING_QUESTIONNAIRES,
)
from bot.user.service import add_user_to_db, send_welcome
from bot.user.preferences import (
    start_preference_flow,
    handle_city_input,
    handle_gender_input,
    handle_age_from_input,
    handle_age_to_input,
)
from bot.user.favorites import (
    start_favorite_flow,
    show_next_favorite,
    show_previous_favorite,
    delete_current_favorite,
    add_to_favorites,
)
from bot.user.search_flow import (
    get_current_questionnaire_id,
    send_questionnaire,
)
from bot.database.repositories.status_repo import (
    get_status_by_user_id,
    update_status_step,
)
from bot.ui.keyboard import build_menu_keyboard
from bot.ui.messages import HELP_LINES
from bot.bot_service import write_message
from bot.vk_api.photos import three_best_photos


def initial_launch(user_vk: int) -> None:
    user_status = get_status_by_user_id(user_vk)
    if user_status and user_status.step == START:
        send_welcome(user_vk)
        keyboard = build_menu_keyboard(['🎬 Начать', '🆘 Помощь', '🆒 Избранное'], one_time=True)
        write_message(
            user_vk,
            "Жмите на кнопку чтобы составить твои предпочтения для поиска!\n"
            "     👇👇👇",
            keyboard=keyboard,
        )


def send_help(user_vk: int) -> None:
    for line in HELP_LINES:
        write_message(user_vk, line)

    keyboard = build_menu_keyboard(['🟢 Главное меню', '🆒 Избранное'], one_time=True)
    write_message(user_vk, 'Выберите действие:', keyboard=keyboard)


class MessageHandler:
    def __init__(self):
        self.handlers = {
            '🆘 Помощь': self.handle_help,
            '🆒 Избранное': self.handle_favorites,
            '🟢 Главное меню': self.handle_main_menu,
            '🔎 Новый поиск': self.handle_new_search,
            '🎬 Начать': self.handle_start,
        }

    def handle(self, user_vk: int, message: str, user_status):
        handler = self.handlers.get(message)
        if handler:
            handler(user_vk, user_status)
            return True
        return False

    def handle_help(self, user_vk: int, user_status) -> None:
        write_message(user_vk, 'Всегда рад помочь!')
        send_help(user_vk)

    def handle_favorites(self, user_vk, user_status) -> None:
        start_favorite_flow(user_vk)

    def handle_main_menu(self, user_vk, user_status) -> None:
        btn = (
            '👀 Продолжить просмотр'
            if user_status.step == VIEWING_FAVORITE_QUESTIONNAIRE
            else '🔎 Новый поиск'
        )
        keyboard = build_menu_keyboard([btn, '🆘 Помощь', '🆒 Избранное'], one_time=True)
        write_message(user_vk, 'Что вы хотите?', keyboard=keyboard)
        update_status_step(user_status, START)

    def handle_new_search(self, user_vk, user_status) -> None:
        update_status_step(user_status, START_MESSAGING)
        start_preference_flow(user_vk)

    def handle_start(self, user_vk, user_status) -> None:
        update_status_step(user_status, START_MESSAGING)
        start_preference_flow(user_vk)



def handle_events() -> None:
    longpoll = VkLongPoll(vk_group_session, wait=2)
    message_handler = MessageHandler()

    for event in longpoll.listen():
        if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
            continue

        if event.peer_id != event.user_id:
            continue

        user_vk = event.user_id
        message = event.text

        add_user_to_db(user_vk)
        user_status = get_status_by_user_id(user_vk)
        if not user_status:
            continue

        if message_handler.handle(user_vk, message, user_status):
            continue

        if user_status.step == START:
            initial_launch(user_vk)
            continue

        if user_status.step == CHOOSING_CITY:
            handle_city_input(user_vk, message)
            continue

        if user_status.step == CHOOSING_GENDER:
            handle_gender_input(user_vk, message)
            continue

        if user_status.step == CHOOSING_AGE_FROM:
            handle_age_from_input(user_vk, message)
            continue

        if user_status.step == CHOOSING_AGE_TO:
            handle_age_to_input(user_vk, message)
            continue

        if user_status.step == VIEWING_QUESTIONNAIRES:
            if message == '⏩ Далее':
                if not send_questionnaire(user_vk, user_status):
                    write_message(
                        user_vk,
                        'Больше анкет не найдено. Пожалуйста, измените критерии поиска или вернитесь в главное меню',
                    )
                continue
            if message == '❤ В избранное':
                current_questionnaire_id = get_current_questionnaire_id(user_status)
                if current_questionnaire_id is None:
                    write_message(user_vk, 'Сначала откройте анкету, которую хотите добавить в избранное.')
                    continue

                questionnaire_info = three_best_photos(current_questionnaire_id)
                if not questionnaire_info:
                    write_message(user_vk, 'Не удалось загрузить данные анкеты. Попробуйте позже.')
                    continue

                questionnaire = questionnaire_info[current_questionnaire_id]
                add_to_favorites(
                    user_vk,
                    current_questionnaire_id,
                    questionnaire['name'],
                    questionnaire.get('surname', ''),
                    str(questionnaire.get('gender', '0')),
                    questionnaire.get('photos'),
                )
                continue

            write_message(user_vk, 'Пожалуйста, выберите одну из кнопок: '
                                   '⏩ Далее, '
                                   '❤ В избранное, '
                                   '🟢 Главное меню или '
                                   '🆒 Избранное.')
            continue

        if user_status.step == VIEWING_FAVORITE_QUESTIONNAIRE:
            if message == '👀 Продолжить просмотр':
                start_favorite_flow(user_vk)
                continue
            if message == '⏪ Назад':
                show_previous_favorite(user_vk)
                continue
            if message == '⏩ Вперед':
                show_next_favorite(user_vk)
                continue
            if message == '🗑 Удалить из Избранного':
                delete_current_favorite(user_vk)
                continue


