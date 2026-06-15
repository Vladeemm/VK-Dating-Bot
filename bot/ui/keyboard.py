"""Утилиты для создания клавиатур ВКонтакте."""

from typing import Iterable
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def build_menu_keyboard(buttons: Iterable[str], one_time: bool = False) -> str:
    """Создает клавиатуру с кнопками.

    Args:
        buttons: Список текстов кнопок.
        one_time: Показывать клавиатуру один раз.

    Returns:
        JSON-представление клавиатуры.
    """
    keyboard = VkKeyboard(one_time=one_time)
    for button_text in buttons:
        keyboard.add_button(button_text, color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()
