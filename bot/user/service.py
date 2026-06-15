"""Общий сервис бизнес-логики для бота."""

from bot.database.repositories.user_repo import ensure_user
from bot.database.repositories.status_repo import get_status_by_user_id, create_status
from bot.ui.messages import WELCOME_TEXT
from bot.bot_service import write_message
from bot.vk_api.users import get_user_info_from_vk


def add_user_to_db(user_vk: int) -> None:
    user_info = get_user_info_from_vk(user_vk)
    user_name = user_info[1] if len(user_info) > 1 else str(user_vk)
    ensure_user(user_vk, user_name)
    status = get_status_by_user_id(user_vk)
    if not status:
        create_status(user_vk, 'start')


def send_welcome(user_vk: int) -> None:
    write_message(user_vk, WELCOME_TEXT)
