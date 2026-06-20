"""Модуль для поиска анкет через VK API.

Предоставляет функции для поиска открытых анкет пользователей
ВКонтакте по городу, полу и возрасту с фильтрацией по наличию фото.
"""

from typing import Any, Dict, Optional
from .client import vk
from .decorators import vk_api_call


@vk_api_call
def get_questionnaires_by_criteria(
    city_id: int,
    gender: int,
    age_from: int,
    age_to: int,
) -> Optional[list[int]]:
    """Получить список ID открытых анкет ВКонтакте по критериям поиска.

    Выполняет поиск пользователей через VK API и фильтрует результаты:
    оставляет только открытые профили с фотографией.

    Args:
        city_id: ID города для поиска.
        gender: Пол пользователя (1 — женский, 2 — мужской).
        age_from: Минимальный возраст.
        age_to: Максимальный возраст.

    Returns:
        list[int]: Список ID пользователей, подходящих под критерии.
        None: Если запрос к API завершился неудачей или требуется капча.
    """
    params: Dict[str, Any] = {
        'city': city_id,
        'sex': gender,
        'age_from': age_from,
        'age_to': age_to,
        'fields': 'is_closed,has_photo',
        'count': 100,
    }

    response: Dict[str, Any] = vk.users.search(**params)

    questionnaires: list[Dict[str, Any]] = response.get('items', [])
    ids_list: list[int] = []

    for questionnaire in questionnaires:
        has_photo: int = questionnaire.get('has_photo', 0)
        is_closed: bool = questionnaire.get('is_closed', True)
        if not is_closed and has_photo == 1:
            ids_list.append(questionnaire['id'])

    return ids_list
