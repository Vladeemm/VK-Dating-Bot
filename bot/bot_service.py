"""Модуль сервисных функций бота общего назначения.

Предоставляет функции для отправки сообщений пользователям
ВКонтакте через API сообщества.
"""

from random import randrange
from typing import Any, Dict, Optional

from bot.vk_api.client import vk_group_api


def write_message(
    user_id: int,
    message: str,
    attachments: Optional[str] = None,
    keyboard: Optional[str] = None,
) -> None:
    """Отправить сообщение пользователю ВКонтакте.

    Формирует параметры запроса и отправляет сообщение через
    API сообщества с опциональными вложениями и клавиатурой.

    Args:
        user_id: ID пользователя ВКонтакте.
        message: Текст сообщения.
        attachments: Строка с вложениями в формате VK API или None.
        keyboard: JSON-представление клавиатуры или None.
    """
    params: Dict[str, Any] = {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7),
    }
    if attachments:
        params['attachment'] = attachments
    if keyboard:
        params['keyboard'] = keyboard

    vk_group_api.messages.send(**params)
