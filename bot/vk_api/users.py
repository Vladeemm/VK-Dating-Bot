"""Модуль для работы с пользователями и городами через VK API.

Предоставляет функции для получения информации о пользователях
ВКонтакте и определения ID городов по названию.
"""

import time
from typing import Any, Dict, Optional
from .client import vk
from .decorators import vk_api_call


@vk_api_call
def get_user_info_from_vk(user_vk_id: int) -> Optional[list[int | str]]:
    """Получить базовую информацию о пользователе ВКонтакте.

    Запрашивает имя пользователя через VK API по его ID.

    Args:
        user_vk_id: ID пользователя ВКонтакте.

    Returns:
        list[int | str]: Список с ID пользователя и его именем:
            - [0]: ID пользователя
            - [1]: Имя пользователя
        None: Если запрос к API завершился неудачей или требуется капча.
    """
    response: list[Dict[str, Any]] = vk.users.get(user_ids=user_vk_id)
    time.sleep(0.35)

    if not response:
        return None

    first_name: str = response[0].get('first_name', '')
    
    if not first_name:
        return None
    
    return [user_vk_id, first_name]


@vk_api_call
def get_city_id(city: str) -> Optional[int]:
    """Получить ID города ВКонтакте по названию.

    Выполняет поиск города в базе данных VK API и возвращает ID
    первого найденного совпадения.

    Args:
        city: Название города для поиска.

    Returns:
        int: ID города в базе VK API.
        None: Если город не найден, запрос завершился неудачей
            или требуется капча.
    """
    response: Dict[str, Any] = vk.database.getCities(q=city)
    time.sleep(0.35)

    items: list[Dict[str, Any]] = response.get('items', [])
    if items:
        return items[0].get('id')
    return None
