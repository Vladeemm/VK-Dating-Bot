"""Главный модуль запуска бота."""

from bot.core.handlers import handle_events


def run_bot() -> None:
    """Запускает основной цикл обработки событий."""
    handle_events()
