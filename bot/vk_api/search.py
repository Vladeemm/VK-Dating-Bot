"""VK API поиск анкет по критериям."""

from typing import List
from bot.vk_api.client import vk


def get_questionnaires_by_criteria(city_id: int, gender: int, age_from: int, age_to: int) -> List[int]:
    """Получает список открытых анкет ВКонтакте по критериям."""
    params = {
        'city': city_id,
        'sex': gender,
        'age_from': age_from,
        'age_to': age_to,
        'fields': 'is_closed,has_photo',
        'count': 100,
    }

    try:
        response = vk.users.search(**params)
    except Exception as exc:
        print(f'VK API search error: {exc}')
        return []

    questionnaires = response.get('items', [])
    ids_list: List[int] = []

    for questionnaire in questionnaires:
        has_photo = questionnaire.get('has_photo', 0)
        is_closed = questionnaire.get('is_closed', True)
        if not is_closed and has_photo == 1:
            ids_list.append(questionnaire['id'])

    return ids_list
