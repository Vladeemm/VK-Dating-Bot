"""Модуль для работы с фотографиями из VK API.

Предоставляет функции для получения профилей пользователей и их лучших
фотографий из ВКонтакте с расчетом возраста и сортировкой по популярности.
"""

import datetime
import time
from typing import Any, Dict, Optional
from .client import vk
from .decorators import vk_api_call

def _get_age_from_bdate(bdate: Optional[str]) -> Optional[int]:
    """Вычислить возраст из даты рождения в формате VK API.

    Args:
        bdate: Дата рождения в формате 'день.месяц.год' или None.

    Returns:
        int: Возраст пользователя в годах.
        None: Если дата не предоставлена, имеет неверный формат или
            не содержит год.
    """
    if not bdate:
        return None

    parts = bdate.split('.')
    if len(parts) != 3:
        return None

    try:
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None

    today = datetime.date.today()
    age = today.year - year - ((today.month, today.day) < (month, day))
    return age

@vk_api_call
def get_user_profile(user_vk_id: int) -> Optional[Dict[str, Any]]:
    """Получить профиль пользователя ВКонтакте с информацией о возрасте.

    Запрашивает основную информацию о пользователе через VK API, включая
    пол и дату рождения, затем вычисляет текущий возраст.

    Args:
        user_vk_id: ID пользователя ВКонтакте.

    Returns:
        Dict[str, Any]: Словарь с информацией профиля:
            - user_vk_id: ID пользователя
            - name: Имя пользователя
            - surname: Фамилия пользователя
            - gender: Пол (1 - женский, 2 - мужской)
            - age: Возраст в годах
        None: Если запрос к API завершился неудачей или капча требуется.
    """
    basic_response: Optional[Dict[str, Any]] = vk.users.get(user_ids=user_vk_id, fields='sex,bdate')
    time.sleep(0.35)
    if not basic_response:
        return None

    profile: Dict[str, Any] = basic_response[0] # type: ignore
    return {
        'user_vk_id': user_vk_id,
        'name': profile['first_name'],
        'surname': profile.get('last_name', ''),
        'gender': profile.get('sex'),
        'age': _get_age_from_bdate(profile.get('bdate')),
    }

@vk_api_call
def three_best_photos(user_vk_id: int) -> Optional[Dict[int, Dict[str, Any]]]:
    """Получить три лучшие фотографии пользователя по количеству лайков.

    Запрашивает фотографии профиля пользователя, сортирует их по количеству
    лайков и выбирает три лучших. Возвращает информацию профиля вместе с
    ID лучших фотографий.

    Args:
        user_vk_id: ID пользователя ВКонтакте.

    Returns:
        Dict[int, Dict[str, Any]]: Словарь с информацией пользователя и его
            тремя лучшими фотографиями:
            - user_vk_id: Индекс словаря
                - user_vk_id: ID пользователя
                - name: Имя пользователя
                - surname: Фамилия пользователя
                - gender: Пол пользователя
                - age: Возраст пользователя
                - photos: Список кортежей (owner_id, photo_id, likes_count)
        None: Если профиль не найден, фотографий меньше 3, или при ошибке API.
    """
    user_profile = get_user_profile(user_vk_id)
    if not user_profile:
        return None

    response: Dict[str, Any] = vk.photos.get(owner_id=user_vk_id, album_id='profile', extended=1)
    time.sleep(0.35)

    if response.get('count', 0) < 3:
        return None

    all_photo: list[tuple[int, int, int]] = []
    for photo in response.get('items', []):
        likes_count = photo.get('likes', {}).get('count', 0)
        photo_id = photo.get('id')
        photo_owner_id = photo.get('owner_id')
        if photo_id and photo_owner_id:
            all_photo.append((photo_owner_id, photo_id, likes_count))

    sorted_photos: list[tuple[int, int, int]] = sorted(all_photo, key=lambda x: x[2], reverse=True)[:3]
    questionnaire_info: Dict[int, Dict[str, Any]] = {
        user_vk_id: {
            **user_profile,
            'photos': sorted_photos,
        }
    }

    return questionnaire_info