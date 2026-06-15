"""Работа с фотографиями из VK API."""

import datetime
import time
from typing import Any, Dict, Optional
from bot.vk_api.client import vk


def _get_age_from_bdate(bdate: Optional[str]) -> Optional[int]:
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


def get_user_profile(user_vk_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает профиль пользователя ВКонтакте с возрастом."""
    try:
        basic_response = vk.users.get(user_ids=user_vk_id, fields='sex,bdate')
        time.sleep(0.35)
    except Exception as exc:
        print(f'VK API profile load error: {exc}')
        return None

    if not basic_response:
        return None

    profile = basic_response[0]
    return {
        'user_vk_id': user_vk_id,
        'name': profile['first_name'],
        'surname': profile.get('last_name', ''),
        'gender': profile.get('sex'),
        'age': _get_age_from_bdate(profile.get('bdate')),
    }


def three_best_photos(user_vk_id: int) -> Optional[Dict[int, Dict[str, Any]]]:
    """Возвращает три лучшие фотографии пользователя."""
    user_profile = get_user_profile(user_vk_id)
    if not user_profile:
        return None

    try:
        response = vk.photos.get(owner_id=user_vk_id, album_id='profile', extended=1)
        time.sleep(0.35)
    except Exception as exc:
        print(f'VK API photo load error: {exc}')
        return None

    if response.get('count', 0) < 3:
        return None

    all_photo = []
    for photo in response.get('items', []):
        likes_count = photo.get('likes', {}).get('count', 0)
        photo_id = photo.get('id')
        photo_owner_id = photo.get('owner_id')
        if photo_id and photo_owner_id:
            all_photo.append((photo_owner_id, photo_id, likes_count))

    sorted_photos = sorted(all_photo, key=lambda x: x[2], reverse=True)[:3]
    questionnaire_info = {
        user_vk_id: {
            **user_profile,
            'photos': sorted_photos,
        }
    }

    return questionnaire_info
