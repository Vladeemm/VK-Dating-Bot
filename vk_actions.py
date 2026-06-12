import os
import time
import vk_api

from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

my_token = os.getenv('MY_VK_TOKEN')

# ----- для тестов
# user_vk_id = 2846903
# city = 'Москва'
# age_from = 31
# age_to = 32
# gender = 1
# ---------------

vk_session = vk_api.VkApi(token=my_token)
vk = vk_session.get_api()

def get_user_info_from_vk(user_vk_id: int) -> list[Any]:
    """Получает информацию о пользователе ВКонтакте для занесения в БД.

    Args:
        user_vk_id (int): VK ID пользователя.

    Returns:
        list[Any]: Список, содержащий VK ID пользователя и его имя.
    """

    user_info = vk.users.get(
        user_ids=user_vk_id
    )
    user_name: str = user_info[0]['first_name']
    return [user_vk_id, user_name]

def get_city_id(city: str) -> Optional[int]:
    """Получает идентификатор города ВКонтакте.

    Args:
        city (str): Название города для поиска.

    Returns:
        Optional[int]: ID города, если найден, иначе None.
    """
    try:
        response = vk.database.getCities(q=city)
        
        items = response.get('items', [])

        if items:
            return items[0]['id']
            
        # Если список пустой, значит VK не нашел такой город
        return None
        
    except vk_api.exceptions.ApiError:
        # print(f"Ошибка VK API при поиске города '{city}': {e}")
        return None
    except Exception:
        # print(f"Непредвиденная ошибка при поиске города '{city}': {e}")
        return None

def get_questionnaires_by_criteria(city_id: int, gender: int, age_from: int, age_to: int) -> list[int]:
    """Получает список пользователей ВКонтакте по критериям поиска.

    Args:
        city_id (int): ID города для поиска.
        gender (int): Пол пользователей (1 — женщина, 2 — мужчина).
        age_from (int): Минимальный возраст.
        age_to (int): Максимальный возраст.

    Returns:
        list[int]: Список идентификаторов пользователей, подходящих по критериям.
    """
    
    params = {
        'city': city_id,
        'sex': gender,
        'age_from': age_from,
        'age_to': age_to,
        'fields': 'is_closed, has_photo',
        'count': 1000
    }

    response = vk.users.search(**params)
    questionnaires = response.get('items', [])
    ids_list = []

    if len(questionnaires) > 0:
        for questionnaire in questionnaires:
            has_photo: int = questionnaire.get('has_photo', 0)
            is_closed: bool = questionnaire.get('is_closed', True)
            if not is_closed and has_photo == 1:
                ids_list.append(questionnaire['id'])

    return ids_list

def three_best_photos(user_vk_id) -> dict | None:
    """Получает три лучшие фотографии пользователя ВКонтакте.

    Args:
        user_vk_id: VK ID пользователя.

    Returns:
        dict: Словарь с информацией о пользователе и списком трёх лучших фото.
    """
    
    basic_response = vk.users.get(
        user_ids=user_vk_id,
        fields='sex'
        )
    
    time.sleep(0.35)
    
    response = vk.photos.get(
        owner_id=user_vk_id,
        album_id='profile',
        extended=1
        )
    
    time.sleep(0.35)

    questionnaire_info = {}
    all_photo = []

    if response['count'] >= 3:
        all_sizes_photos = response.get('items')
        for photo in all_sizes_photos:
            likes_count = photo.get('likes', {}).get('count', 0)
            sizes = photo.get('sizes', [])
            if sizes:
                photo_x_url = sizes[-1]['url']
                all_photo.append((photo_x_url, likes_count))
            sorted_all_photos = sorted(all_photo, key=lambda x: x[1], reverse=True)[:3]

            questionnaire_info[user_vk_id] = {
                'user_vk_id': user_vk_id,
                'name':  basic_response[0]['first_name'],
                'surname':  basic_response[0]['last_name'],
                'gender':  basic_response[0]['sex'],
                'photos': sorted_all_photos
            }
    else:
        return None

    return questionnaire_info