"""Логика формирования и валидации предпочтений пользователя."""

from typing import Dict

from ..database.repositories.status_repo import update_search_criteria, update_status_step
from ..database.repositories.status_repo import get_status_by_user_id
from ..user.search_flow import search_and_send_first_questionnaire
from ..vk_api.users import get_city_id
from ..ui.keyboard import build_menu_keyboard
from ..ui.messages import (
    PREFERENCE_CITY_PROMPT,
    PREFERENCE_GENDER_PROMPT,
    PREFERENCE_AGE_FROM_PROMPT,
    PREFERENCE_AGE_TO_PROMPT,
)
from ..bot_service import write_message
from ..core.states import (
    CHOOSING_CITY,
    CHOOSING_GENDER,
    CHOOSING_AGE_FROM,
    CHOOSING_AGE_TO,
    VIEWING_QUESTIONNAIRES,
)


def start_preference_flow(user_vk: int) -> None:
    """Запускает поток выбора поисковых критериев для пользователя.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
    """
    user_status = get_status_by_user_id(user_vk)
    if not user_status:
        return

    update_search_criteria(user_status, {})
    update_status_step(user_status, CHOOSING_CITY)
    keyboard = build_menu_keyboard(['🟢 Главное меню', '🆒 Избранное'], one_time=False)
    write_message(user_vk, PREFERENCE_CITY_PROMPT, keyboard=keyboard)


def handle_city_input(user_vk: int, message: str) -> None:
    """Обрабатывает ввод города и переводит пользователя к выбору пола.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
        message: Текст введенного города.
    """
    user_status = get_status_by_user_id(user_vk)
    if not user_status:
        return

    city_id = get_city_id(message)
    if city_id is None:
        write_message(user_vk, 'Введите другой город, такого нет.')
        keyboard = build_menu_keyboard(['🟢 Главное меню', '🆒 Избранное'], one_time=False)
        write_message(user_vk, PREFERENCE_CITY_PROMPT, keyboard=keyboard)
        return

    criteria = {**(user_status.search_criteria or {}), 'city': city_id}
    update_search_criteria(user_status, criteria)
    update_status_step(user_status, CHOOSING_GENDER)
    keyboard = build_menu_keyboard(['♂️ Муж.', '♀️ Жен.', 'Не имеет значение', '🟢 Главное меню', '🆒 Избранное'], one_time=True)
    write_message(user_vk, PREFERENCE_GENDER_PROMPT, keyboard=keyboard)


def handle_gender_input(user_vk: int, message: str) -> None:
    """Сохраняет выбранный пол и предлагает минимальный возраст.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
        message: Текст выбранной кнопки пола.
    """
    user_status = get_status_by_user_id(user_vk)
    if not user_status:
        return

    if message not in {'♂️ Муж.', '♀️ Жен.', 'Не имеет значение'}:
        write_message(user_vk, 'Пожалуйста, выберите один из предложенных вариантов.')
        return

    sex = 2 if message == '♂️ Муж.' else 1 if message == '♀️ Жен.' else 0
    criteria = {**(user_status.search_criteria or {}), 'sex': sex}
    update_search_criteria(user_status, criteria)

    update_status_step(user_status, CHOOSING_AGE_FROM)
    keyboard = build_menu_keyboard(['🟢 Главное меню', '🆒 Избранное'], one_time=False)
    write_message(user_vk, 'Определите возрастной диапазон (от 18 до 99 лет)')
    write_message(user_vk, PREFERENCE_AGE_FROM_PROMPT, keyboard=keyboard)


def handle_age_from_input(user_vk: int, message: str) -> None:
    """Сохраняет минимальный возраст и переводит к выбору максимального.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
        message: Текст введенного минимального возраста.
    """
    user_status = get_status_by_user_id(user_vk)
    if not user_status:
        return

    age = message.strip()
    if not age.isdigit():
        write_message(user_vk, 'Пожалуйста, введите корректное значение.')
        return

    age_int = int(age)
    if age_int < 18 or age_int > 99:
        write_message(user_vk, 'Пожалуйста, выберите возраст (от 18 до 99 лет)')
        return

    criteria = {**(user_status.search_criteria or {}), 'age_from': age_int}
    update_search_criteria(user_status, criteria)

    update_status_step(user_status, CHOOSING_AGE_TO)
    keyboard = build_menu_keyboard(['🟢 Главное меню', '🆒 Избранное'], one_time=False)
    write_message(user_vk, PREFERENCE_AGE_TO_PROMPT, keyboard=keyboard)


def handle_age_to_input(user_vk: int, message: str) -> None:
    """Сохраняет максимальный возраст, запускает поиск и показывает первую анкету.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
        message: Текст введенного максимального возраста.
    """
    user_status = get_status_by_user_id(user_vk)
    if not user_status:
        return

    age = message.strip()
    min_age = (user_status.search_criteria or {}).get('age_from')
    if not age.isdigit():
        write_message(user_vk, 'Пожалуйста, введите корректное значение.')
        return

    age_int = int(age)
    if age_int < 18 or age_int > 99:
        write_message(user_vk, 'Пожалуйста, выберите возраст (от 18 до 99 лет)')
        return

    if min_age is not None and age_int < int(min_age):
        write_message(user_vk, f'Пожалуйста, выберите возраст (от {min_age} до 99 лет)')
        return

    criteria = {**(user_status.search_criteria or {}), 'age_to': age_int}
    update_search_criteria(user_status, criteria)

    update_status_step(user_status, VIEWING_QUESTIONNAIRES)
    write_message(user_vk, 'Супер!🎉 Твои предпочтения сохранены, я готов к поиску! ')
    search_and_send_first_questionnaire(user_vk, user_status)
