"""Поисковый поток для показа анкет и навигации по результатам."""

from random import shuffle
from typing import Any, Dict, List, Optional

from ..bot_service import write_message
from ..database.models import Status
from ..database.repositories.status_repo import (
    update_list_applicants,
    update_search_criteria,
    update_status_step,
)
from ..ui.formatter import format_questionnaire_message
from ..ui.keyboard import build_menu_keyboard
from ..vk_api.photos import three_best_photos
from ..vk_api.search import get_questionnaires_by_criteria

SEARCH_NAVIGATION_BUTTONS = [
    '🟢 Главное меню',
    '⏩ Далее',
    '🆒 Избранное',
    '❤ В избранное',
]


def get_current_questionnaire_id(status: Status) -> Optional[int]:
    """Возвращает идентификатор текущей анкеты из критериев поиска.

    Args:
        status: Текущий статус пользователя.

    Returns:
        Идентификатор анкеты или None, если он не установлен.
    """
    return (status.search_criteria or {}).get('current_questionnaire_id')


def set_current_questionnaire_id(status: Status, questionnaire_vk_id: Optional[int]) -> None:
    """Записывает текущую анкету в критерии поиска пользователя.

    Args:
        status: Текущий статус пользователя.
        questionnaire_vk_id: Идентификатор анкеты для отображения.
    """
    criteria: Dict[str, Optional[int]] = {**(status.search_criteria or {})}
    if questionnaire_vk_id is None:
        criteria.pop('current_questionnaire_id', None)
    else:
        criteria['current_questionnaire_id'] = questionnaire_vk_id
    update_search_criteria(status, criteria)


def _send_questionnaire_by_id(user_vk: int, status: Status, questionnaire_vk_id: int) -> bool:
    """Отправляет анкету пользователю по её идентификатору.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
        status: Текущий статус пользователя.
        questionnaire_vk_id: Идентификатор анкеты для отправки.

    Returns:
        True, если анкета отправлена, иначе False.
    """
    questionnaire_info = three_best_photos(questionnaire_vk_id)
    if not questionnaire_info:
        return False

    questionnaire = questionnaire_info[questionnaire_vk_id]
    attachments = ",".join(
        f"photo{owner_id}_{photo_id}"
        for owner_id, photo_id, likes in questionnaire['photos']
    )
    message_text = format_questionnaire_message(questionnaire)
    write_message(user_vk, message_text, attachments=attachments)
    keyboard = build_menu_keyboard(SEARCH_NAVIGATION_BUTTONS, one_time=False)
    write_message(user_vk, 'Анкета из поиска:', keyboard=keyboard)
    set_current_questionnaire_id(status, questionnaire_vk_id)
    return True


def send_questionnaire(user_vk: int, status: Status) -> bool:
    """Отправляет следующую доступную анкету из списка найденных результатов."""
    ids_list = list(status.list_applicants or [])

    while ids_list:
        questionnaire_vk_id = ids_list.pop()
        if _send_questionnaire_by_id(user_vk, status, questionnaire_vk_id):
            update_list_applicants(status, ids_list)
            return True

    update_list_applicants(status, None)
    set_current_questionnaire_id(status, None)
    return False


def search_and_send_first_questionnaire(user_vk: int, status: Status) -> bool:
    """Инициирует поиск по критериям и отправляет первую найденную анкету.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
        status: Текущий статус пользователя.

    Returns:
        True, если анкету удалось отправить, иначе False.
    """
    criteria = status.search_criteria or {}
    city_id = criteria.get('city')
    sex = criteria.get('sex')
    age_from = criteria.get('age_from')
    age_to = criteria.get('age_to')

    if city_id is None or sex is None or age_from is None or age_to is None:
        write_message(user_vk, 'Сначала задайте критерии поиска')
        keyboard = build_menu_keyboard(['🟢 Главное меню'], one_time=True)
        write_message(user_vk, 'Главное меню', keyboard=keyboard)
        return False

    ids_list: List[int] = get_questionnaires_by_criteria(
        int(city_id), int(sex), int(age_from), int(age_to)
    )
    if not ids_list:
        write_message(
            user_vk,
            'К сожалению, по вашим параметрам не нашлось анкет. Пожалуйста, измените критерии поиска',
        )
        keyboard = build_menu_keyboard(['🟢 Главное меню'], one_time=True)
        write_message(user_vk, 'Возвращаемся в главное меню', keyboard=keyboard)
        update_status_step(status, START)
        return False

    shuffle(ids_list)
    update_list_applicants(status, ids_list)
    if not send_questionnaire(user_vk, status):
        write_message(
            user_vk,
            'К сожалению, среди найденных анкет нет ни одной с 3 фотографиями. Пожалуйста, измените критерии поиска',
        )
        return False

    return True
