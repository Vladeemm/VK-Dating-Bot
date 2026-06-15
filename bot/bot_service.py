"""Сервисные функции бота общего назначения."""

from random import randrange
from bot.vk_api.client import vk_group_api


def write_message(user_id: int, message: str, attachments=None, keyboard=None) -> None:
    params = {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7),
    }
    if attachments:
        params['attachment'] = attachments
    if keyboard:
        params['keyboard'] = keyboard

    vk_group_api.messages.send(**params)
