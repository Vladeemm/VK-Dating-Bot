"""Управление избранными анкетами пользователя."""

from typing import Optional, List

from ..database.models import Status
from ..database.repositories.favorite_repo import (
    add_favorite,
    get_favorites_by_user,
    get_favorite,
    remove_favorite,
)
from ..database.repositories.status_repo import (
    get_status_by_user_id,
    update_list_applicants,
    update_search_criteria,
    update_status_step,
)
from ..bot_service import write_message
from ..ui.formatter import format_favorite_item, format_questionnaire_message
from ..ui.keyboard import build_menu_keyboard
from ..vk_api.photos import get_user_profile, three_best_photos
from ..core.states import (
    START,
    VIEWING_FAVORITE_QUESTIONNAIRE,
)

FAVORITE_NAVIGATION_BUTTONS = [
    '⏪ Назад',
    '⏩ Вперед',
    '🟢 Главное меню',
    '🗑 Удалить из Избранного',
]


def get_favorite_index(status: Status) -> int:
    """Возвращает индекс текущей анкеты в избранном."""
    return int((status.search_criteria or {}).get('favorite_index', 0))


def set_favorite_index(status: Status, index: int) -> None:
    """Сохраняет индекс текущей анкеты в избранном."""
    criteria = {**(status.search_criteria or {}), 'favorite_index': index}
    update_search_criteria(status, criteria)


def send_favorite_questionnaire(user_vk: int, status: Status) -> bool:
    """Отправляет текущую анкету из избранного пользователю."""
    favorite_ids = list(status.list_applicants or [])
    if not favorite_ids:
        write_message(user_vk, 'У вас пока нет анкет в избранном.')
        return False

    index = get_favorite_index(status)
    if index < 0:
        index = 0
        set_favorite_index(status, index)
    if index >= len(favorite_ids):
        index = len(favorite_ids) - 1
        set_favorite_index(status, index)

    favorite_vk_id = favorite_ids[index]
    favorite = get_favorite(user_vk, favorite_vk_id)
    if not favorite:
        write_message(user_vk, 'Не удалось загрузить анкету из избранного.')
        return False

    questionnaire_info = three_best_photos(favorite_vk_id)
    if questionnaire_info:
        questionnaire = questionnaire_info[favorite_vk_id]
        attachments = ",".join(
            f"photo{owner_id}_{photo_id}" for owner_id, photo_id, likes in questionnaire['photos']
        )
        message_text = format_questionnaire_message(questionnaire)
        write_message(user_vk, message_text, attachments=attachments)
    else:
        profile = get_user_profile(favorite_vk_id)
        age = profile.get('age') if profile else None
        message_text = format_favorite_item(
            favorite.name,
            favorite.surname,
            favorite_vk_id,
            age=age,
        )
        write_message(user_vk, message_text)
        write_message(user_vk, 'Для этой анкеты нет 3 доступных фото.')

    keyboard = build_menu_keyboard(FAVORITE_NAVIGATION_BUTTONS, one_time=False)
    write_message(user_vk, f'Анкета {index + 1} из {len(favorite_ids)}', keyboard=keyboard)
    return True


def start_favorite_flow(user_vk: int) -> None:
    """Запускает просмотр списка избранных анкет пользователя."""
    status = get_status_by_user_id(user_vk)
    favorites = get_favorites_by_user(user_vk)
    if not status:
        return

    if not favorites:
        write_message(user_vk, 'У вас пока нет анкет в избранном.')
        return

    favorite_ids = [favorite.favorite_user_vk_id for favorite in favorites]
    update_list_applicants(status, favorite_ids)
    set_favorite_index(status, 0)
    update_status_step(status, VIEWING_FAVORITE_QUESTIONNAIRE)
    send_favorite_questionnaire(user_vk, status)


def show_next_favorite(user_vk: int) -> None:
    """Показывает следующую анкету из списка избранного."""
    status = get_status_by_user_id(user_vk)
    if not status:
        return

    favorite_ids = list(status.list_applicants or [])
    index = get_favorite_index(status)
    if index >= len(favorite_ids) - 1:
        write_message(user_vk, 'Это последняя анкета. Больше анкет нет.')
        return

    set_favorite_index(status, index + 1)
    send_favorite_questionnaire(user_vk, status)


def show_previous_favorite(user_vk: int) -> None:
    """Показывает предыдущую анкету из списка избранного."""
    status = get_status_by_user_id(user_vk)
    if not status:
        return

    index = get_favorite_index(status)
    if index <= 0:
        write_message(user_vk, 'Это первая анкета в избранном.')
        return

    set_favorite_index(status, index - 1)
    send_favorite_questionnaire(user_vk, status)


def delete_current_favorite(user_vk: int) -> None:
    """Удаляет текущую выбранную анкету из избранного."""
    status = get_status_by_user_id(user_vk)
    if not status:
        return

    favorite_ids = list(status.list_applicants or [])
    if not favorite_ids:
        write_message(user_vk, 'У вас пока нет анкет в избранном.')
        return

    index = get_favorite_index(status)
    favorite_vk_id = favorite_ids.pop(index)
    remove_favorite(user_vk, favorite_vk_id)
    write_message(user_vk, 'Анкета удалена из избранного.')

    if not favorite_ids:
        update_list_applicants(status, None)
        update_status_step(status, START)
        keyboard = build_menu_keyboard(['🎬 Начать', '🆘 Помощь', '🆒 Избранное'], one_time=True)
        write_message(user_vk, 'Избранное пустое. Возвращаемся в главное меню.', keyboard=keyboard)
        return

    update_list_applicants(status, favorite_ids)
    if index >= len(favorite_ids):
        index = len(favorite_ids) - 1
    set_favorite_index(status, index)
    send_favorite_questionnaire(user_vk, status)


def add_to_favorites(user_vk: int, favorite_vk_id: int, name: str, surname: str, gender: str, photos: Optional[dict]) -> None:
    """Добавляет анкету в избранное, если она ещё не была сохранена."""
    existing = get_favorite(user_vk, favorite_vk_id)
    if existing:
        write_message(user_vk, 'Эта анкета уже есть в избранном.')
        return

    try:
        add_favorite(user_vk, favorite_vk_id, name, surname, gender, photos)
        write_message(user_vk, 'Анкета добавлена в избранное')
    except Exception:
        write_message(user_vk, 'Не удалось добавить анкету в избранное. Попробуйте позже.')


def remove_from_favorites(user_vk: int, favorite_vk_id: int) -> None:
    """Удаляет указанную анкету из избранного пользователя."""
    if remove_favorite(user_vk, favorite_vk_id):
        write_message(user_vk, 'Анкета удалена из избранного')
    else:
        write_message(user_vk, 'Анкета не найдена в избранном')
