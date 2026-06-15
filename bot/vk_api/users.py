"""Работа с пользователями и городами через VK API."""

from typing import Any, List, Optional
from bot.vk_api.client import vk


def get_user_info_from_vk(user_vk_id: int) -> List[Any]:
    try:
        response = vk.users.get(user_ids=user_vk_id)
    except Exception as exc:
        print(f'VK API user info error: {exc}')
        return [user_vk_id, '']

    first_name = response[0].get('first_name', '')
    return [user_vk_id, first_name]


def get_city_id(city: str) -> Optional[int]:
    try:
        response = vk.database.getCities(q=city)
    except Exception as exc:
        print(f'VK API get city error: {exc}')
        return None

    items = response.get('items', [])
    if items:
        return items[0].get('id')
    return None
