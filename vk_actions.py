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
        'count': 25
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

def get_three_photos_from_questionnaires(questionnaires_ids: list) -> dict[int, list[tuple[str, int]]]:
    """Получает три лучших фотографии для каждой найденной анкеты.

    Args:
        questionnaires_ids (list): Список идентификаторов ВК-пользователей.

    Returns:
        dict[int, list[tuple[str, int]]]: Словарь, где ключ — идентификатор анкеты,
            а значение — список до трёх кортежей с URL фото и числом лайков.
    """

    three_photos_by_questionnaire = {}

    for questionnaire_id in questionnaires_ids:
        all_photos = []
        response = vk.photos.get(
            owner_id=questionnaire_id,
            album_id='profile',
            extended=1
        )

        photo_count = response.get('count', 0)
        if photo_count >= 3:
            all_sizes = response.get('items')
            for photo in all_sizes:
                likes = photo.get('likes', {}).get('count', 0)
                sizes = photo.get('sizes', [])
                photo_url = sizes[-1]['url']
                all_photos.append((photo_url, likes))
        
            sorted_photos = sorted(all_photos, key=lambda x: x[1], reverse=True)
            top_3_photos = sorted_photos[:3]
            three_photos_by_questionnaire[questionnaire_id] = top_3_photos
        
        time.sleep(0.35)

    return three_photos_by_questionnaire