"""Логика формирования и валидации предпочтений пользователя."""

from typing import Any, Dict, Optional, cast

from ..database.models import Status
from ..database.repositories.status_repo import update_search_criteria, update_status_step
from ..database.repositories.status_repo import get_status_by_user_id
from ..user.search_flow import search_and_send_first_questionnaire
from ..vk_api.users import get_city_id
from ..ui.keyboard import build_menu_keyboard
from ..ui.messages import (
    PREFERENCE_CITY_PROMPT,
    PREFERENCE_GENDER_PROMPT,
    PREFERENCE_AGE_FROM_PROMPT,
    PREFERENCE_AGE_TO_PROMPT,
)
from ..bot_service import write_message
from ..core.states import (
    CHOOSING_CITY,
    CHOOSING_GENDER,
    CHOOSING_AGE_FROM,
    CHOOSING_AGE_TO,
    VIEWING_QUESTIONNAIRES,
)

class AgeValidationError(Exception):
    """ Класс ошибок при валидации возраста """
    pass

class AgeNotDigitError(AgeValidationError):
    """ Возраст введен не цифрами """
    pass

class AgeOutOfRange(AgeValidationError):
    """ Возраст вне заданного диапазона """
    pass

class AgeLessThanMinError(AgeValidationError):
    """ Возраст меньше минимальной введенной границы """
    pass

def _validate_age_input(message: str, min_age: Optional[int]=None) -> int:
    """Служебная функция валидации возраста.
    
    Raises:
        AgeNotDigitError: Если возраст не является числом.
        AgeOutOfRangeError: Если возраст вне диапазона 18-99.
        AgeLessThanMinError: Если возраст меньше min_age.
    
    Returns:
        int: Валидный возраст.
    """
    age = message.strip()

    if len(age) >= 3:
        raise AgeOutOfRange  # По сути это защита от SQL инъекций

    if not age.isdigit():
        raise AgeNotDigitError()
    
    age = int(age)

    if not 18 <= age <= 99:
        raise AgeOutOfRange()
    
    if min_age is not None and age < min_age:
            raise AgeLessThanMinError()
        
    return age

def _update_criteria(status: Status, key: str, value: Any) -> Status:
    """Обновляет поле search_criteria в статусе пользователя.

    Безопасно объединяет текущие критерии с новым ключом-значением,
    сохраняет изменения в базе данных и возвращает обновлённый объект.

    Args:
        status: Текущий объект статуса пользователя.
        key: Ключ для добавления или обновления в словаре критериев.
        value: Значение, которое нужно записать по указанному ключу.

    Returns:
        Status: Обновлённый объект статуса с применёнными изменениями.
    """

    current_criteria: Dict[str,  Any] = cast(Dict[str, Any], status.search_criteria or {})
    new_criteria = {**current_criteria, key: value}
    return update_search_criteria(status, new_criteria)

def start_preference_flow(user_vk: int) -> None:
    """Запускает поток выбора поисковых критериев для пользователя.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
    """
    user_status = get_status_by_user_id(user_vk)
    if not user_status:
        return

    user_status = update_search_criteria(user_status, {})
    update_status_step(user_status, CHOOSING_CITY)
    keyboard = build_menu_keyboard(['🟢 Главное меню', '🆒 Избранное'], one_time=False)
    write_message(user_vk, PREFERENCE_CITY_PROMPT, keyboard=keyboard)


def handle_city_input(user_vk: int, message: str) -> None:
    """Обрабатывает ввод города и переводит пользователя к выбору пола.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
        message: Текст введенного города.
    """
    user_status = get_status_by_user_id(user_vk)
    if not user_status:
        return

    city_id = get_city_id(message)
    if city_id is None:
        write_message(user_vk, 'Введите другой город, такого нет.')
        keyboard = build_menu_keyboard(['🟢 Главное меню', '🆒 Избранное'], one_time=False)
        write_message(user_vk, PREFERENCE_CITY_PROMPT, keyboard=keyboard)
        return

    user_status: Status = _update_criteria(user_status, 'city', city_id)
    update_status_step(user_status, CHOOSING_GENDER)
    keyboard: str = build_menu_keyboard(['♂️ Муж.', '♀️ Жен.', 'Не имеет значение', '🟢 Главное меню', '🆒 Избранное'], one_time=True)
    write_message(user_vk, PREFERENCE_GENDER_PROMPT, keyboard=keyboard)


def handle_gender_input(user_vk: int, message: str) -> None:
    """Сохраняет выбранный пол и предлагает минимальный возраст.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
        message: Текст выбранной кнопки пола.
    """
    user_status = get_status_by_user_id(user_vk)
    if not user_status:
        return

    if message not in {'♂️ Муж.', '♀️ Жен.', 'Не имеет значение'}:
        write_message(user_vk, 'Пожалуйста, выберите один из предложенных вариантов.')
        return

    sex = 2 if message == '♂️ Муж.' else 1 if message == '♀️ Жен.' else 0
    user_status = _update_criteria(user_status, 'sex', sex)

    update_status_step(user_status, CHOOSING_AGE_FROM)
    keyboard = build_menu_keyboard(['🟢 Главное меню', '🆒 Избранное'], one_time=False)
    write_message(user_vk, 'Определите возрастной диапазон (от 18 до 99 лет)')
    write_message(user_vk, PREFERENCE_AGE_FROM_PROMPT, keyboard=keyboard)


def handle_age_from_input(user_vk: int, message: str) -> None:
    """Сохраняет минимальный возраст и переводит к выбору максимального.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
        message: Текст введенного минимального возраста.
    """
    user_status = get_status_by_user_id(user_vk)
    if not user_status:
        return

    try:
        age_int: int = _validate_age_input(message)
    except AgeNotDigitError:
        write_message(user_vk, "Пожалуйста, введите корректное значение")
        return
    except AgeOutOfRange:
        write_message(user_vk, "Пожалуйста, введите возраст от 18 до 99 лет")
        return
    
    user_status = _update_criteria(user_status, 'age_from', age_int)

    update_status_step(user_status, CHOOSING_AGE_TO)
    keyboard = build_menu_keyboard(['🟢 Главное меню', '🆒 Избранное'], one_time=False)
    write_message(user_vk, PREFERENCE_AGE_TO_PROMPT, keyboard=keyboard)


def handle_age_to_input(user_vk: int, message: str) -> None:
    """Сохраняет максимальный возраст, запускает поиск и показывает первую анкету.

    Args:
        user_vk: Идентификатор ВКонтакте пользователя.
        message: Текст введенного максимального возраста.
    """
    user_status = get_status_by_user_id(user_vk)
    if not user_status:
        return

    min_age = (user_status.search_criteria or {}).get('age_from')

    try:
        age_int: int = _validate_age_input(message, min_age)
    except AgeNotDigitError:
        write_message(user_vk, "Пожалуйста, введите корректное значение")
        return
    except AgeOutOfRange:
        write_message(user_vk, "Пожалуйста, введите возраст от 18 до 99 лет")
        return
    except AgeLessThanMinError:
        write_message(user_vk, f"Пожалуйста введите возраст от {min_age} до 99 лет")
        return
    
    user_status = _update_criteria(user_status, 'age_to', age_int)

    user_status = update_status_step(user_status, VIEWING_QUESTIONNAIRES)
    write_message(user_vk, 'Супер!🎉 Твои предпочтения сохранены, я готов к поиску! ')
    search_and_send_first_questionnaire(user_vk, user_status)
